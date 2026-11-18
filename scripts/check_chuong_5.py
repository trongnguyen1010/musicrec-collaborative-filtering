"""Evidence for Chapter 5: release contents, load time, API test cases, online/offline lists.

1. Files of the demo release with sizes, and the time to load it (load_release + DemoService),
   measured in three fresh processes.
2. Test cases T01-T12 run over HTTP (FastAPI TestClient) on the real release; each case
   records its expectation, what happened and Đạt / Không đạt.
3. Online versus offline: for every train user and PureSVD, M1, ALS, the top-10 returned by
   POST /recommend is compared with the top-10 of the original checkpoints in
   outputs/chinh_thuc_cloud_20261026 (not the release copy), masked with train + validation
   as in the official test. Same for M2 on the 189 reserved users with N = 1, 3, 5. Three
   indicators: share of users whose lists are identical in order, mean Jaccard of the item
   sets, and the largest absolute score difference on shared items.

    python scripts/check_chuong_5.py --output-dir outputs/demo/chuong_5_<date>
"""

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from statistics import median
from typing import Any

import pandas as pd
from fastapi.testclient import TestClient

from musicrec.api.main import create_app
from musicrec.data.cold_start import partition_users, profile_order
from musicrec.data.contracts import Interaction
from musicrec.recommenders.implicit_als import ImplicitALSRecommender
from musicrec.recommenders.m1 import M1Recommender
from musicrec.recommenders.m2 import M2Recommender
from musicrec.recommenders.pure_svd import PureSVDRecommender
from musicrec.serving.release import load_release
from musicrec.serving.service import DemoService

RUN = Path("outputs/chinh_thuc_cloud_20261026")
RELEASE = Path("artifacts/releases/demo-chinh-thuc-20261026")
LOAD_SNIPPET = (
    "import time;t=time.perf_counter();"
    "from musicrec.serving.release import load_release;"
    "from musicrec.serving.service import DemoService;"
    f"DemoService(load_release(__import__('pathlib').Path(r'{RELEASE}')));"
    "print(time.perf_counter()-t)"
)


def release_files() -> list[dict[str, Any]]:
    return [
        {"path": p.relative_to(RELEASE).as_posix(), "bytes": p.stat().st_size}
        for p in sorted(RELEASE.rglob("*"))
        if p.is_file()
    ]


def load_times() -> list[float]:
    """Seconds from import to a ready DemoService, each in a fresh interpreter."""
    return [
        float(
            subprocess.run(
                [sys.executable, "-c", LOAD_SNIPPET], capture_output=True, text=True, check=True
            ).stdout.strip()
        )
        for _ in range(3)
    ]


def run_cases(client: TestClient, service: DemoService) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def case(code: str, content: str, expected: str, passed: bool, note: str) -> None:
        cases.append(
            {
                "ma": code,
                "noi_dung": content,
                "mong_doi": expected,
                "ket_qua": "Đạt" if passed else "Không đạt",
                "ghi_chu": note,
            }
        )

    def post(body: dict[str, Any]) -> Any:
        return client.post("/recommend", json=body)

    r = post({"user_id": "2", "k": 10, "model": "pure_svd"}).json()
    items = [x["item_id"] for x in r["recommendations"]]
    ok = (
        len(items) == 10
        and len(set(items)) == 10
        and not set(items) & service.masked_items("2")
        and [x["rank"] for x in r["recommendations"]] == list(range(1, 11))
    )
    case(
        "T01",
        "Người dùng có sẵn (mã 2), PureSVD, K = 10",
        "10 nghệ sĩ, không trùng, không chứa lịch sử huấn luyện và xác thực",
        ok,
        f"branch={r['branch']}, 10 mục, 0 mục thuộc lịch sử",
    )

    r = post({"history": [], "k": 10}).json()
    ok = (r["branch"], r["fallback_used"], r["fallback_reason"]) == (
        "popularity",
        True,
        "empty_profile",
    ) and len(r["recommendations"]) == 10
    case(
        "T02",
        "Lịch sử rỗng",
        "Danh sách Popularity, fallback_used = true, lý do empty_profile",
        ok,
        f"branch={r['branch']}, fallback_reason={r['fallback_reason']}",
    )

    r = post({"history": [{"item_id": "89"}], "k": 10}).json()
    ok = (r["branch"], r["model"], r["fallback_used"], r["ignored_item_ids"]) == (
        "new_user",
        "m2",
        False,
        [],
    )
    case(
        "T03",
        "Người dùng mới chọn 1 nghệ sĩ có trong danh mục M2 (mã 89)",
        "Nhánh new_user, mô hình M2, không dự phòng",
        ok,
        f"branch={r['branch']}, model={r['model']}",
    )

    r = post({"history": [{"item_id": "99999999"}], "k": 10}).json()
    ok = (
        r["fallback_used"]
        and r["fallback_reason"] == "no_profile_artist_in_m2_catalog"
        and r["ignored_item_ids"] == ["99999999"]
        and len(r["recommendations"]) == 10
    )
    case(
        "T04",
        "Lịch sử chỉ gồm nghệ sĩ ngoài danh mục",
        "Không lỗi, dự phòng về phổ biến, liệt kê mã bị bỏ qua",
        ok,
        f"fallback_reason={r['fallback_reason']}, ignored={r['ignored_item_ids']}",
    )

    r = post({"user_id": "2", "k": 100, "model": "implicit_als"}).json()
    items = [x["item_id"] for x in r["recommendations"]]
    ok = len(items) == 100 and len(set(items)) == 100 and not set(items) & service.masked_items("2")
    case(
        "T05",
        "K = 100 (giới hạn trên của API), ALS",
        "Đúng 100 nghệ sĩ, không trùng, không chứa lịch sử",
        ok,
        f"{len(items)} mục, {len(set(items))} mục khác nhau",
    )

    codes = [post({"user_id": "2", "k": k}).status_code for k in [0, -1, "abc", 101]]
    case(
        "T06",
        "K = 0, K = −1, K không phải số, K = 101",
        "Mã 422 cho cả bốn trường hợp",
        codes == [422] * 4,
        f"mã trả về {codes}",
    )

    base = [x["item_id"] for x in post({"user_id": "2", "k": 10}).json()["recommendations"]]
    m1 = post({"user_id": "2", "k": 10, "model": "m1"}).json()
    off = post({"user_id": "2", "k": 10, "model": "m1", "m1_lambda": 1.0, "m1_beta": 0.0})
    off_items = [x["item_id"] for x in off.json()["recommendations"]]
    ok = len(m1["recommendations"]) == 10 and off.status_code == 200 and off_items == base
    case(
        "T07",
        "Bật M1 và đặt M1 về λ = 1, β = 0 cho cùng người dùng",
        "Hai danh sách hợp lệ; M1 với λ = 1, β = 0 trùng thứ tự PureSVD",
        ok,
        f"M1 khác PureSVD {len(set(base) - {x['item_id'] for x in m1['recommendations']})} mục",
    )

    code = post({"user_id": "2", "model": "svd"}).status_code
    case(
        "T08",
        "Yêu cầu mô hình không phục vụ (svd)",
        "Mã 422, liệt kê giá trị hợp lệ",
        code == 422,
        f"mã trả về {code}",
    )

    body = {"user_id": "7", "k": 20, "model": "m1"}
    first, second = post(body).json(), post(body).json()
    case(
        "T09",
        "Gửi cùng yêu cầu hai lần",
        "Hai kết quả giống hệt (tất định)",
        first == second,
        "so sánh toàn bộ JSON",
    )

    with TestClient(create_app(lambda: DemoService(load_release(RELEASE)))) as fresh:
        again = fresh.post("/recommend", json=body).json()
    case(
        "T10",
        "Nạp lại gói mô hình trong một ứng dụng mới",
        "Kết quả trùng trước khi nạp lại",
        again == first,
        "so sánh toàn bộ JSON",
    )

    codes = [
        post({"user_id": "99999999"}).status_code,
        client.get("/users/99999999/history").status_code,
    ]
    case(
        "T11",
        "Mã người dùng không tồn tại (recommend và history)",
        "Mã 404",
        codes == [404, 404],
        f"mã trả về {codes}",
    )

    bad = [
        {},
        {"history": [{"item_id": "89"}, {"item_id": "89"}]},
        {"history": [{"item_id": str(i)} for i in range(1, 7)]},
        {"history": [{"item_id": "89", "listening_count": -5}]},
        {"user_id": "2", "model": "m1", "m1_lambda": 0.6, "m1_beta": 0.5},
    ]
    codes = [post(b).status_code for b in bad]
    case(
        "T12",
        "Thiếu cả user_id lẫn history; nghệ sĩ trùng; quá 5 nghệ sĩ; lượt nghe âm; λ ngoài lưới",
        "Mã 422 cho cả năm trường hợp",
        codes == [422] * 5,
        f"mã trả về {codes}",
    )
    return cases


def compare_lists(
    online: dict[str, list[tuple[str, float]]], offline: dict[str, list[tuple[str, float]]]
) -> dict[str, Any]:
    same, jaccards, max_diff = 0, [], 0.0
    for user, a in online.items():
        b = offline[user]
        same += [i for i, _ in a] == [i for i, _ in b]
        sa, sb = {i for i, _ in a}, {i for i, _ in b}
        jaccards.append(len(sa & sb) / len(sa | sb) if sa | sb else 1.0)
        scores = dict(b)
        for item, score in a:
            if item in scores:
                max_diff = max(max_diff, abs(score - scores[item]))
    return {
        "users": len(online),
        "identical_order_rate": same / len(online),
        "mean_jaccard": sum(jaccards) / len(jaccards),
        "max_abs_score_difference": max_diff,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=False)

    files = release_files()
    seconds = load_times()
    service = DemoService(load_release(RELEASE))
    with TestClient(create_app(lambda: service)) as client:
        cases = run_cases(client, service)
        for c in cases:
            print(c["ma"], c["ket_qua"], c["ghi_chu"], flush=True)

        source = RUN / "chuong_3/run/representations"
        train = pd.read_parquet(source / "train.parquet")
        pure = PureSVDRecommender.load(RUN / "chuong_4/tuning/pure_svd/pure_svd_lat16/model")
        offline_models = {
            "pure_svd": pure,
            "m1": M1Recommender.load(
                RUN / "chuong_4/m1_pure_svd/seed_42/selected_model", base=pure
            ),
            "implicit_als": ImplicitALSRecommender.load(
                RUN / "chuong_4/tuning/implicit_als/implicit_als_lat32_reg0.1_con1/model"
            ),
        }
        users = sorted({str(u) for u in train.user_id}, key=int)
        consistency: dict[str, Any] = {}
        for model, recommender in offline_models.items():
            online, offline = {}, {}
            for user in users:
                body = {"user_id": user, "k": 10, "model": model}
                recs = client.post("/recommend", json=body).json()["recommendations"]
                online[user] = [(x["item_id"], x["score"]) for x in recs]
                offline[user] = [
                    (r.item_id, r.score)
                    for r in recommender.recommend(user, 10, service.masked_items(user))
                ]
            consistency[model] = compare_lists(online, offline)
            print(model, consistency[model], flush=True)

        split_train = pd.read_parquet(RUN / "chuong_3/run/split/train.parquet")
        split_train["user_id"] = split_train.user_id.astype(str)
        split_train["item_id"] = split_train.item_id.astype(str)
        roles = json.loads((RUN / "chuong_4/m2_tuning/user_roles.json").read_text("utf-8"))
        if roles != partition_users(sorted(split_train.user_id.unique(), key=int), 42):
            raise RuntimeError("Saved user roles differ from the deterministic partition")
        reserved = split_train[split_train.user_id.isin(roles["reserved"])]
        counts = reserved.groupby("user_id").size()
        cold = sorted(counts[counts >= 5].index, key=int)
        m2 = M2Recommender.load(RUN / "chuong_4/m2_tuning/model")
        for n in [1, 3, 5]:
            online, offline = {}, {}
            for user in cold:
                records = reserved[reserved.user_id == user].set_index("item_id")["listening_count"]
                order = profile_order(user, list(records.index), 42)[:n]
                history = [{"item_id": i, "listening_count": float(records[i])} for i in order]
                recs = client.post("/recommend", json={"history": history, "k": 10}).json()
                online[user] = [(x["item_id"], x["score"]) for x in recs["recommendations"]]
                m2.set_profile(user, [Interaction(user, i, float(records[i])) for i in order])
                offline[user] = [(r.item_id, r.score) for r in m2.recommend(user, 10, set())]
            consistency[f"m2_n{n}"] = compare_lists(online, offline)
            print(f"m2 N={n}", consistency[f"m2_n{n}"], flush=True)

    pd.DataFrame(cases).to_csv(out / "ca_kiem_thu.csv", index=False)
    report = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "release": service.release.version,
        "release_files": files,
        "release_total_bytes": sum(f["bytes"] for f in files),
        "load_seconds_fresh_process": seconds,
        "load_seconds_median": median(seconds),
        "cases": cases,
        "cases_passed": sum(c["ket_qua"] == "Đạt" for c in cases),
        "online_offline_top10": consistency,
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            **{
                name: importlib.metadata.version(name)
                for name in ["numpy", "scipy", "pandas", "fastapi", "pydantic", "implicit"]
            },
        },
        "command": sys.argv,
    }
    (out / "chuong_5.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", "utf-8"
    )


if __name__ == "__main__":
    main()
