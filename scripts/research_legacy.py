"""Isolated RecBole 1.1.1 bridge: trusted split conversion and genuine BPR training.

Run using .venv-legacy, never from the serving application. Pickle conversion is
permitted only for files whose SHA256 and Git blob were verified by the downloader.
"""

import argparse
import hashlib
import importlib.metadata
import inspect
import io
import json
import os
import pickle
import platform
import random
import subprocess
import time
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")

import numpy as np
import torch
from recbole.config import Config
from recbole.data import create_dataset, data_preparation
from recbole.model.general_recommender import BPR
from recbole.trainer import Trainer
from recbole.utils import init_seed

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/research"
SPLITS = ROOT / "data/processed/reproduction"
METRICS = ["Recall", "MRR", "NDCG", "Hit", "Precision"]
torch.set_num_threads(4)
torch.set_num_interop_threads(1)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    temporary.replace(path)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pair_array(dataset):
    return np.stack(
        [
            dataset.inter_feat[dataset.uid_field].numpy(),
            dataset.inter_feat[dataset.iid_field].numpy(),
        ],
        axis=1,
    ).astype(np.int64)


def history_array(loader):
    pairs = []
    for user in range(loader.dataset.user_num):
        values = loader.uid2history_item[user]
        if values is not None:
            pairs.extend((user, int(item)) for item in values)
    return np.asarray(pairs, dtype=np.int64).reshape(-1, 2)


def export_split(loaders, destination, metadata):
    train, valid, test = loaders
    dataset = train.dataset
    users = np.asarray(dataset.field2id_token[dataset.uid_field], dtype=str)
    items = np.asarray(dataset.field2id_token[dataset.iid_field], dtype=str)
    np.savez_compressed(
        destination,
        users=users,
        items=items,
        train=pair_array(train.dataset),
        validation=pair_array(valid.dataset),
        test=pair_array(test.dataset),
        valid_history=history_array(valid),
        test_history=history_array(test),
        valid_users=valid.user_df[dataset.uid_field].numpy(),
        test_users=test.user_df[dataset.uid_field].numpy(),
    )
    metadata.update(
        {
            "sha256": sha256(destination),
            "users_with_padding": len(users),
            "items_with_padding": len(items),
            "rows": {
                name: len(pair_array(loader.dataset))
                for name, loader in zip(["train", "validation", "test"], loaders, strict=True)
            },
        }
    )
    write_json(destination.with_suffix(".json"), metadata)


def convert():
    manifest = json.loads((OUT / "download_manifest.json").read_text(encoding="utf-8"))
    records = {row["path"].replace("\\", "/"): row for row in manifest["upstream_files"]}
    target = SPLITS / "aiprobs-original"
    target.mkdir(parents=True, exist_ok=True)
    for index in range(30):
        relative = f"data/interim/aiprobs-source/Data/30 LastFM Realizations/lastfm {index}.pth"
        source = ROOT / relative
        if sha256(source) != records[relative]["sha256"]:
            raise ValueError(f"Unverified pickle: {source}")
        with patch(
            "torch.storage._load_from_bytes",
            lambda content: torch.load(io.BytesIO(content), map_location="cpu", weights_only=False),
        ):
            with source.open("rb") as stream:
                loaders = pickle.load(stream)
        if isinstance(loaders[0], tuple):
            loaders = [entry[0] for entry in loaders]
        # 2022 pickles store ``dataset``; RecBole 1.1.1 exposes it via ``_dataset``.
        # This changes only the attribute location, never interaction contents.
        for loader in loaders:
            if "_dataset" not in loader.__dict__:
                loader.__dict__["_dataset"] = loader.__dict__["dataset"]
        config = loaders[0].config.final_config_dict
        destination = target / f"split_{index:02}.npz"
        export_split(
            loaders,
            destination,
            {
                "protocol": "aiprobs-original",
                "split_id": index,
                "source_sha256": sha256(source),
                "source_commit": manifest["aiprobs_commit"],
                "original_config": config,
                "conversion": "RecBole 1.1.1, CPU map_location",
            },
        )
        print(f"converted {index}: {destination}", flush=True)


def config_for(data_path, seed, benchmark_filename=None):
    parameters = dict(
        data_path=str(data_path),
        use_gpu=False,
        seed=seed,
        reproducibility=True,
        show_progress=False,
        USER_ID_FIELD="user_id",
        ITEM_ID_FIELD="artist_id",
        load_col={"inter": ["user_id", "artist_id"]},
        user_inter_num_interval="[0,inf)",
        item_inter_num_interval="[0,inf)",
        eval_args={
            "split": {"RS": [0.8, 0.1, 0.1]},
            "group_by": "user",
            "order": "RO",
            "mode": "full",
        },
        embedding_size=64,
        learning_rate=0.0005,
        train_batch_size=4096,
        eval_batch_size=256 * 17633,
        epochs=5000,
        stopping_step=50,
        metrics=METRICS,
        topk=[10],
        valid_metric="NDCG@10",
        checkpoint_dir=str(OUT / "bpr-checkpoints"),
        log_wandb=False,
    )
    if benchmark_filename is not None:
        parameters["benchmark_filename"] = benchmark_filename
    return Config(model="BPR", dataset="lastfm", config_dict=parameters)


def benchmark_splits():
    import pandas as pd

    location = OUT / "benchmark-input"
    folder = location / "lastfm"
    folder.mkdir(parents=True, exist_ok=True)
    original = pd.read_csv(ROOT / "data/raw/hetrec2011/user_artists.dat", sep="\t")
    original[["userID", "artistID"]].to_csv(
        folder / "lastfm.inter", sep="\t", index=False, header=["user_id:token", "artist_id:token"]
    )
    destination = SPLITS / "recbole-bpr-benchmark"
    destination.mkdir(parents=True, exist_ok=True)
    for seed in [2020, 2021, 2022]:
        config = config_for(location, seed)
        init_seed(seed, True)
        loaders = data_preparation(config, create_dataset(config))
        export_split(
            loaders,
            destination / f"split_{seed}.npz",
            {
                "protocol": "recbole-bpr-benchmark",
                "split_id": seed,
                "seed": seed,
                "original_config": config.final_config_dict,
                "split_provenance": "new canonical-input split; published split unavailable",
            },
        )
        print(f"benchmark split {seed}", flush=True)


class ResearchTrainer(Trainer):
    """RecBole training unchanged; save RNG/loader state for deterministic recovery."""

    def _save_checkpoint(self, epoch, verbose=True, **kwargs):
        filename = kwargs.pop("saved_model_file", self.saved_model_file)
        state = {
            "config": self.config,
            "epoch": epoch,
            "cur_step": self.cur_step,
            "best_valid_score": self.best_valid_score,
            "best_valid_result": self.best_valid_result,
            "state_dict": self.model.state_dict(),
            "other_parameter": self.model.other_parameter(),
            "optimizer": self.optimizer.state_dict(),
            "research_rng": {
                "python": random.getstate(),
                "numpy": np.random.get_state(),
                "torch": torch.get_rng_state(),
                "loader": self.research_train.generator.get_state(),
            },
            "research_signature": self.research_signature,
        }
        temporary = str(filename) + ".tmp"
        torch.save(state, temporary, pickle_protocol=4)
        Path(temporary).replace(filename)


def train_bpr(protocol, split_id):
    path = SPLITS / protocol / f"split_{split_id:02}.npz"
    destination = OUT / "bpr" / protocol / f"split_{split_id:02}"
    destination.mkdir(parents=True, exist_ok=True)
    status_path = destination / "result.json"
    source_text = "\n".join(
        inspect.getsource(function) for function in [config_for, ResearchTrainer, train_bpr]
    )
    signature = hashlib.sha256(source_text.encode()).hexdigest()
    if status_path.exists():
        result = json.loads(status_path.read_text(encoding="utf-8"))
        if (
            result.get("status") == "completed"
            and result["split_sha256"] == sha256(path)
            and result.get("training_signature") == signature
        ):
            print(f"resume: already completed {protocol}/{split_id}", flush=True)
            return
    # Cache arrays once: NpzFile indexing decompresses the complete array on every access.
    with np.load(path, allow_pickle=False) as archive:
        split = {name: archive[name] for name in archive.files}
    location = destination / "input"
    folder = location / "lastfm"
    folder.mkdir(parents=True, exist_ok=True)
    for part, key in [("train", "train"), ("valid", "validation"), ("test", "test")]:
        with (folder / f"lastfm.{part}.inter").open("w", encoding="utf-8") as stream:
            stream.write("user_id:token\tartist_id:token\n")
            for user, item in split[key]:
                stream.write(f"{split['users'][user]}\t{split['items'][item]}\n")
    seed = split_id if protocol == "recbole-bpr-benchmark" else 2020
    config = config_for(location, seed, ["train", "valid", "test"])
    config["checkpoint_dir"] = str(destination / "checkpoint")
    init_seed(seed, True)
    dataset = create_dataset(config)
    train, valid, test = data_preparation(config, dataset)
    model = BPR(config, train.dataset).to(config["device"])
    trainer = ResearchTrainer(config, model)
    trainer.research_train = train
    trainer.research_signature = signature
    write_json(destination / "effective_config.json", config.final_config_dict)
    (destination / "training_source.py.txt").write_text(source_text, encoding="utf-8")
    write_json(
        destination / "environment.json",
        {
            "python": platform.python_version(),
            "packages": {
                dist.metadata["Name"]: dist.version for dist in importlib.metadata.distributions()
            },
            "git_sha": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "dataset_sha256": sha256(ROOT / "data/raw/hetrec2011-lastfm-2k.zip"),
            "training_signature": signature,
        },
    )
    started = time.perf_counter()
    write_json(status_path, {"status": "running", "split_sha256": sha256(path)})

    last_epoch = 0

    def progress(epoch, score):
        nonlocal last_epoch
        last_epoch = epoch
        if epoch % 20 == 0:
            record = {
                "epoch": epoch,
                "validation_ndcg": score,
                "best_validation_ndcg": trainer.best_valid_score,
                "elapsed_seconds": time.perf_counter() - started,
            }
            write_json(destination / "progress.json", record)
            print(f"BPR {protocol}/{split_id} {record}", flush=True)

    checkpoint = destination / "checkpoint/latest.pth"
    trainer.saved_model_file = str(checkpoint)
    if checkpoint.exists():
        saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
        if saved.get("research_signature") == signature:
            trainer.resume_checkpoint(str(checkpoint))
            state = saved["research_rng"]
            random.setstate(state["python"])
            np.random.set_state(state["numpy"])
            torch.set_rng_state(state["torch"])
            train.generator.set_state(state["loader"])
            trainer.best_valid_result = trainer.evaluate(
                valid, load_best_model=False, show_progress=False
            )
        del saved
    best_score, valid_result = trainer.fit(
        train, valid, verbose=False, show_progress=False, callback_fn=progress
    )
    test_result = trainer.evaluate(test, load_best_model=True, show_progress=False)
    user_tokens = list(dataset.field2id_token[dataset.uid_field])
    item_tokens = list(dataset.field2id_token[dataset.iid_field])
    user_map = {token: index for index, token in enumerate(user_tokens)}
    item_map = {token: index for index, token in enumerate(item_tokens)}
    u = model.user_embedding.weight.detach().cpu().numpy()
    i = model.item_embedding.weight.detach().cpu().numpy()
    np.savez_compressed(
        destination / "factors.npz",
        users=split["users"],
        items=split["items"],
        user_factors=u[[user_map[x] for x in split["users"]]],
        item_factors=i[[item_map[x] for x in split["items"]]],
    )
    result = {
        "status": "completed",
        "protocol": protocol,
        "split_id": split_id,
        "split_sha256": sha256(path),
        "seed": seed,
        "best_validation": best_score,
        "validation_metrics": valid_result,
        "recbole_test_metrics": test_result,
        "seconds": time.perf_counter() - started,
        "last_epoch": last_epoch,
        "training_signature": signature,
        "factors_sha256": sha256(destination / "factors.npz"),
        "torch": torch.__version__,
        "recbole": importlib.metadata.version("recbole"),
        "python": platform.python_version(),
    }
    write_json(status_path, result)
    print(f"BPR COMPLETE {protocol}/{split_id}: {test_result}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=["convert", "benchmark-splits", "train-bpr", "verify-metrics"]
    )
    parser.add_argument(
        "--protocol",
        choices=["aiprobs-original", "recbole-bpr-benchmark"],
        default="aiprobs-original",
    )
    parser.add_argument("--split-id", type=int)
    args = parser.parse_args()
    if args.action == "convert":
        convert()
    elif args.action == "benchmark-splits":
        benchmark_splits()
    elif args.action == "verify-metrics":
        verify_metrics()
    else:
        indices = (
            [args.split_id]
            if args.split_id is not None
            else (range(30) if args.protocol == "aiprobs-original" else [2020, 2021, 2022])
        )
        for index in indices:
            train_bpr(args.protocol, index)


def verify_metrics():
    """Compare our per-run metrics to RecBole on exactly the saved top-K lists."""
    from recbole.evaluator import Evaluator
    from recbole.evaluator.collector import DataStruct
    from recbole.evaluator.metrics import MRR, NDCG, Hit, Precision, Recall

    config = config_for(OUT / "benchmark-input", 2020)
    evaluator = Evaluator(config)
    records = []
    for path in sorted((OUT / "runs").rglob("result.json")):
        result = json.loads(path.read_text(encoding="utf-8"))
        if result.get("status") != "completed":
            continue
        with np.load(path.parent / "ranking.npz", allow_pickle=False) as ranking:
            with np.load(
                SPLITS / result["protocol"] / f"split_{result['split_id']:02}.npz",
                allow_pickle=False,
            ) as split:
                positive = split["test"]
                truth = {}
                for user, item in positive:
                    truth.setdefault(int(user), set()).add(int(item))
                hits = np.asarray(
                    [
                        [int(item in truth[int(user)]) for item in ranked]
                        for user, ranked in zip(ranking["users"], ranking["ranking"], strict=True)
                    ]
                )
                counts = ranking["ground_truth_count"][:, None]
                structure = DataStruct()
                structure.set("rec.topk", torch.from_numpy(np.concatenate([hits, counts], axis=1)))
                reference = evaluator.evaluate(structure)
                independent = np.column_stack(
                    [
                        Recall(config).metric_info(hits, counts.ravel())[:, -1],
                        MRR(config).metric_info(hits)[:, -1],
                        NDCG(config).metric_info(hits, counts.ravel())[:, -1],
                        Hit(config).metric_info(hits)[:, -1],
                        Precision(config).metric_info(hits)[:, -1],
                    ]
                )
                np.testing.assert_allclose(
                    independent, ranking["per_user_metrics"], rtol=0, atol=1e-12
                )
                per_user_error = float(np.max(np.abs(independent - ranking["per_user_metrics"])))
        errors = {key: float(result["test"][key] - value) for key, value in reference.items()}
        if any(abs(value) > 0.0000500001 for value in errors.values()):
            raise AssertionError(f"RecBole metric mismatch: {path}: {errors}")
        records.append(
            {
                "protocol": result["protocol"],
                "model": result["model"],
                "split_id": result["split_id"],
                "mlflow_run_id": result["mlflow_run_id"],
                "recbole": dict(reference),
                "raw_minus_rounded_reference": errors,
            }
        )
        records[-1]["max_per_user_metric_error"] = per_user_error
        if result["model"] == "bpr":
            native_path = (
                OUT / "bpr" / result["protocol"] / f"split_{result['split_id']:02}" / "result.json"
            )
            native = json.loads(native_path.read_text(encoding="utf-8"))
            native_errors = {
                key: float(result["test"][key] - value)
                for key, value in native["recbole_test_metrics"].items()
            }
            if any(abs(value) > 0.0000500001 for value in native_errors.values()):
                raise AssertionError(f"BPR adapter differs from native RecBole: {native_errors}")
            records[-1]["adapter_minus_native_bpr_metrics"] = native_errors
    write_json(
        OUT / "metric_verification.json",
        {
            "status": "passed",
            "runs": len(records),
            "rounding_tolerance": 0.0000500001,
            "records": records,
        },
    )
    print(f"RecBole evaluator verified {len(records)} rankings", flush=True)


if __name__ == "__main__":
    main()
