"""Compare every Chapter 3 / Appendix B number of report v15 (25-10-2026) with a rerun."""

import argparse
import json
import math
from pathlib import Path
from typing import Any

# (section, description, value written in report v15, path in the run, tolerance)
CLAIMS: list[tuple[str, str, float, str, float]] = [
    ("3.4.2", "Người dùng gốc", 1892, "raw_eda:users", 0),
    ("3.4.2", "Nghệ sĩ gốc", 17632, "raw_eda:artists", 0),
    ("3.4.2", "Cặp tương tác phân biệt", 92834, "raw_eda:unique_pairs", 0),
    ("3.4.2", "Số vị trí ma trận", 33359744, "raw_eda:possible_pairs", 0),
    ("3.4.2", "Tỷ lệ quan sát (%)", 0.2783, "raw_eda:density*100", 5e-5),
    ("3.4.2", "Độ thưa (%)", 99.7217, "raw_eda:sparsity*100", 5e-5),
    ("3.4.2", "Lịch sử trung bình", 49.07, "raw_eda:distributions.user_history.mean", 5e-3),
    ("3.4.2", "Người dùng có đúng 50 nghệ sĩ", 1829, "raw_eda:history.exactly_50_artists", 0),
    (
        "3.4.2",
        "Số người nghe TB/nghệ sĩ",
        5.27,
        "raw_eda:distributions.artist_listeners.mean",
        5e-3,
    ),
    ("3.4.2", "Trung vị người nghe/nghệ sĩ", 1, "raw_eda:distributions.artist_listeners.50%", 0),
    ("3.4.3", "Cặp trùng", 0, "raw_eda:interaction_quality.duplicate_pair_extra_rows", 0),
    ("3.4.3", "Liên kết ảnh trống", 444, "raw_eda:@pictureURL_blank", 0),
    ("3.4.3", "Dòng gán thẻ ngoài danh mục", 1538, "raw_eda:tags.outside_catalog_rows", 0),
    ("3.4.3", "Mã nghệ sĩ ngoài danh mục", 390, "raw_eda:tags.outside_catalog_artist_ids", 0),
    ("3.4.3", "Người dùng bị loại (<5)", 15, "raw_eda:history.below_5_users", 0),
    ("3.4.3", "Tương tác bị loại (<5)", 33, "raw_eda:history.pairs_at_below_5_users", 0),
    ("3.4.3", "Người dùng sau lọc", 1877, "cleaning:after.users", 0),
    ("3.4.3", "Nghệ sĩ có tương tác sau lọc", 17617, "cleaning:after.interaction_artists", 0),
    ("3.4.3", "Cặp sau lọc", 92801, "cleaning:after.interactions", 0),
    ("3.4.3", "Nghệ sĩ <5 người nghe", 14804, "raw_eda:long_tail.below_5_listener_artists", 0),
    (
        "3.4.3",
        "Tương tác ở nghệ sĩ <5 người nghe",
        21408,
        "raw_eda:long_tail.pairs_at_below_5_listener_artists",
        0,
    ),
    ("3.4.3", "Danh mục giữ nguyên", 17632, "cleaning:after.catalog_artists", 0),
    ("3.5.1", "Tổng lượt nghe sau lọc", 69138727, "cleaning:after.total_listens", 0),
    ("3.5.1", "Count lớn nhất", 352698, "cleaning:after.max_listening_count", 0),
    (
        "3.5.1",
        "Giá trị thẻ ngoài ASCII/UTF-8",
        8,
        "raw_eda:text_encoding.tags.dat.invalid_utf8_text_rows",
        0,
    ),
    ("3.5.1", "Dòng gán thẻ đầu vào", 186479, "cleaning:tags.input_assignments", 0),
    ("3.5.1", "Dòng gán thẻ giữ lại", 184941, "cleaning:tags.retained_assignments", 0),
    ("3.5.1", "Nghệ sĩ chưa có thẻ", 5499, "cleaning:tags.catalog_artists_without_tags", 0),
    (
        "3.5.1",
        "Nghệ sĩ chưa có thẻ còn tương tác",
        5493,
        "cleaning:tags.active_artists_without_tags",
        0,
    ),
    (
        "3.5.1",
        "Dòng gán thẻ của user bị loại",
        202,
        "cleaning:tags.assignments_by_excluded_users_retained_for_later_protocol_filtering",
        0,
    ),
    ("3.5.2", "Tương tác train", 74275, "split:splits.train.interactions", 0),
    ("3.5.2", "Tương tác validation", 9263, "split:splits.validation.interactions", 0),
    ("3.5.2", "Tương tác test", 9263, "split:splits.test.interactions", 0),
    ("3.5.2", "Người dùng mỗi tập", 1877, "split:splits.test.users", 0),
    ("3.5.2", "Nghệ sĩ trong ánh xạ train", 15398, "split:splits.train.artists", 0),
    (
        "3.5.2",
        "Đích validation ngoài danh mục",
        1121,
        "split:targets.validation.outside_catalog",
        0,
    ),
    (
        "3.5.2",
        "Tỷ lệ ngoài danh mục validation (%)",
        12.10,
        "split:targets.validation.outside_catalog_fraction*100",
        5e-3,
    ),
    ("3.5.2", "Đích validation hợp lệ", 8142, "split:targets.validation.in_catalog", 0),
    (
        "3.5.2",
        "User validation có đích",
        1865,
        "split:targets.validation.users_with_valid_targets",
        0,
    ),
    ("3.5.2", "Đích test ngoài danh mục", 1203, "split:targets.test.outside_catalog", 0),
    (
        "3.5.2",
        "Tỷ lệ ngoài danh mục test (%)",
        12.99,
        "split:targets.test.outside_catalog_fraction*100",
        5e-3,
    ),
    ("3.5.2", "Đích test hợp lệ", 8060, "split:targets.test.in_catalog", 0),
    ("3.5.2", "User test có đích", 1855, "split:targets.test.users_with_valid_targets", 0),
    (
        "3.5.2",
        "User validation không còn đích",
        12,
        "split:targets.validation.users_without_valid_targets",
        0,
    ),
    ("3.5.2", "User test không còn đích", 22, "split:targets.test.users_without_valid_targets", 0),
    ("3.5.3", "Ngưỡng 1", 6.392317, "representations:transform.thresholds.0", 5e-7),
    ("3.5.3", "Ngưỡng 2", 7.562242, "representations:transform.thresholds.1", 5e-7),
    ("3.5.3", "Ngưỡng 3", 8.491853, "representations:transform.thresholds.2", 5e-7),
    ("3.5.3", "Ngưỡng 4", 9.579316, "representations:transform.thresholds.3", 5e-7),
    ("3.5.3", "Train mức 1", 14989, "representations:splits.train.score_counts.1", 0),
    ("3.5.3", "Train mức 2", 14805, "representations:splits.train.score_counts.2", 0),
    ("3.5.3", "Train mức 3", 14819, "representations:splits.train.score_counts.3", 0),
    ("3.5.3", "Train mức 4", 14818, "representations:splits.train.score_counts.4", 0),
    ("3.5.3", "Train mức 5", 14844, "representations:splits.train.score_counts.5", 0),
    ("3.5.3", "Số ô quan sát ma trận train", 74275, "representations:transform.matrix_nnz", 0),
    (
        "3.10.2",
        "Tỷ lệ user gốc có đúng 50 nghệ sĩ (%)",
        96.67,
        "raw_eda:history.exactly_50_artists/users*100",
        5e-3,
    ),
    ("PL B.1", "Precision ví dụ 1", 2 / 3, "evaluator:appendix.appendix_precision", 1e-12),
    ("PL B.1", "Recall ví dụ 1", 1, "evaluator:appendix.appendix_recall", 1e-12),
    ("PL B.1", "NDCG ví dụ 1", 0.6934, "evaluator:appendix.appendix_ndcg", 5e-5),
    ("PL B.1", "Precision@5 danh sách ngắn", 0.4, "evaluator:appendix.short_precision_at_5", 1e-12),
    ("PL B.1", "NDCG khi chỉ trả A (tính độc lập)", 0.61315, "@ndcg_single_hit", 5e-6),
    ("PL B.2", "Gini 4 nghệ sĩ", 0.375, "evaluator:appendix.appendix_gini", 1e-12),
    ("PL B.2", "Precision@3 tổng hợp", 1 / 3, "evaluator:expected_at_3.precision", 1e-12),
    ("PL B.2", "Recall@3 tổng hợp", 2 / 3, "evaluator:expected_at_3.recall", 1e-12),
    ("PL B.2", "NDCG@3 tổng hợp", 0.63991, "evaluator:expected_at_3.ndcg", 5e-6),
    ("PL B.2", "Độ bao phủ", 0.5, "evaluator:expected_at_3.catalog_coverage", 1e-12),
    ("PL B.2", "Gini tổng hợp", 7 / 12, "evaluator:expected_at_3.gini", 1e-12),
    ("PL B.2", "ARP", 1.25, "evaluator:expected_at_3.arp", 1e-12),
    ("PL B.2", "Novelty (bit)", 2.66111, "evaluator:expected_at_3.novelty", 5e-6),
    ("PL B.2", "ILD", 2 / 3, "evaluator:expected_at_3.ild", 1e-12),
]


def lookup(data: Any, dotted: str) -> Any:
    """Follow a dotted path; keys may themselves contain dots (e.g. tags.dat)."""
    if not dotted:
        return data
    if isinstance(data, list):
        head, _, rest = dotted.partition(".")
        return lookup(data[int(head)], rest)
    for key in sorted(data, key=len, reverse=True):
        if dotted == key or dotted.startswith(key + "."):
            return lookup(data[key], dotted[len(key) + 1 :])
    raise KeyError(dotted)


def actual(run: Path, spec: str) -> float:
    """Resolve a claim path against the saved run outputs."""
    if spec == "@ndcg_single_hit":
        return 1 / (1 + 1 / math.log2(3))
    step, _, expression = spec.partition(":")
    if expression == "@pictureURL_blank":
        lines = (run / step / "tables/quality_by_column.csv").read_text(encoding="utf-8")
        row = next(line for line in lines.splitlines() if line.startswith("artists.dat,pictureURL"))
        return float(row.rsplit(",", 1)[1])
    name = "hand_checks.json" if step == "evaluator" else "metrics.json"
    data = json.loads((run / step / name).read_text(encoding="utf-8"))
    if expression == "history.exactly_50_artists/users*100":
        return (
            100 * float(lookup(data, "history.exactly_50_artists")) / float(lookup(data, "users"))
        )
    path, _, scale = expression.partition("*")
    return float(lookup(data, path)) * (float(scale) if scale else 1)


def main() -> None:
    """Write report_check.json and print the mismatches."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True, help="The run/ folder of run_chuong_3")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for section, label, reported, spec, tolerance in CLAIMS:
        value = actual(args.run, spec)
        rows.append(
            {
                "section": section,
                "claim": label,
                "report_v15": reported,
                "rerun": value,
                "tolerance": tolerance,
                "match": abs(value - reported) <= tolerance,
                "source": spec,
            }
        )
    args.output.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    mismatches = [row for row in rows if not row["match"]]
    print(json.dumps({"claims": len(rows), "mismatches": mismatches}, ensure_ascii=False))


if __name__ == "__main__":
    main()
