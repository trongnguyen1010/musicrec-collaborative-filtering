"""Verify native BPR checkpoint/RNG recovery against an uninterrupted four-epoch run.

This is a training-state regression check, not an additional published-protocol result.
Run only in the isolated legacy environment; the production hyperparameters stay locked.
"""

import random

import numpy as np
import research_legacy as bridge
import torch


def trainer(name, epochs):
    config = bridge.config_for(
        bridge.OUT / "bpr/aiprobs-original/split_00/input", 2020, ["train", "valid", "test"]
    )
    config["epochs"] = epochs
    config["checkpoint_dir"] = str(bridge.OUT / "checkpoint-verification" / name)
    bridge.init_seed(2020, True)
    dataset = bridge.create_dataset(config)
    train, valid, _ = bridge.data_preparation(config, dataset)
    model = bridge.BPR(config, train.dataset).to(config["device"])
    instance = bridge.ResearchTrainer(config, model)
    instance.research_train = train
    instance.research_signature = "checkpoint-regression-v1"
    instance.saved_model_file = str(bridge.OUT / "checkpoint-verification" / name / "state.pth")
    return instance, train, valid


def main():
    whole, train, valid = trainer("whole", 4)
    whole.fit(train, valid, verbose=False, show_progress=False)
    interrupted, train, valid = trainer("interrupted", 2)
    interrupted.fit(train, valid, verbose=False, show_progress=False)
    interrupted._save_checkpoint(1, verbose=False)
    checkpoint = interrupted.saved_model_file
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    resumed, train, valid = trainer("resumed", 4)
    resumed.resume_checkpoint(checkpoint)
    state = saved["research_rng"]
    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.set_rng_state(state["torch"])
    train.generator.set_state(state["loader"])
    resumed.best_valid_result = resumed.evaluate(valid, load_best_model=False, show_progress=False)
    resumed.fit(train, valid, verbose=False, show_progress=False)
    for name, expected in whole.model.state_dict().items():
        torch.testing.assert_close(resumed.model.state_dict()[name], expected, rtol=0, atol=0)
    for key, expected in whole.optimizer.state_dict()["state"].items():
        actual = resumed.optimizer.state_dict()["state"][key]
        for field, value in expected.items():
            torch.testing.assert_close(actual[field], value, rtol=0, atol=0)
    bridge.write_json(
        bridge.OUT / "checkpoint_verification.json",
        {
            "status": "passed",
            "scope": "native RecBole BPR; four epochs; split 0 train/validation",
            "method": "uninterrupted 4 vs 2+checkpoint+2; model and Adam state bit-exact",
            "rng_restored": list(state),
            "selected_experiment_result": False,
        },
    )
    print("Native BPR model/Adam checkpoint recovery is bit-exact")


if __name__ == "__main__":
    main()
