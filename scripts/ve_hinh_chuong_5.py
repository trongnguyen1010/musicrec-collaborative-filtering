"""Draw Figure 5.1 (source tree of the delivered system) as a PNG for the report.

The tree lists the folders and modules that exist in the repository; the script fails if
any listed path is missing, so the figure cannot drift from the code.

    python scripts/ve_hinh_chuong_5.py --output outputs/demo/chuong_5_<date>/anh/hinh_5_1_cay.png
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TREE = [
    ("configs/", "cấu hình dữ liệu, mô hình, lưới tinh chỉnh"),
    ("data/raw/hetrec2011/", "dữ liệu gốc Last.fm HetRec 2011"),
    ("src/musicrec/", ""),
    ("  data/", "làm sạch, chia tập, ánh xạ, biểu diễn, người dùng mới"),
    ("  recommenders/", "Random, Popularity, UserCF, ItemCF, SVD, PureSVD, ALS, M1, M2"),
    ("  evaluation/", "chỉ số xếp hạng, độ phủ, kiểm định, người dùng mới"),
    ("  serving/", "gói phát hành (release.py), định tuyến yêu cầu (service.py)"),
    ("  api/", "FastAPI: main.py, schemas.py"),
    ("  ui/", "giao diện Streamlit dự phòng (app.py)"),
    ("scripts/", "chạy thực nghiệm, xuất gói, kiểm tra, đo độ trễ"),
    ("artifacts/releases/demo-chinh-thuc-20261026/", "gói mô hình phục vụ"),
    ("frontend/src/app/", "Next.js: trang chủ, nguoi-dung, nguoi-moi, luong, ket-qua"),
    ("frontend/src/lib/api.ts", "lời gọi API từ giao diện"),
    ("tests/unit/, tests/contract/", "kiểm thử đơn vị và hợp đồng API"),
]
PATHS = {
    "  data/": "src/musicrec/data",
    "  recommenders/": "src/musicrec/recommenders",
    "  evaluation/": "src/musicrec/evaluation",
    "  serving/": "src/musicrec/serving",
    "  api/": "src/musicrec/api",
    "  ui/": "src/musicrec/ui",
    "tests/unit/, tests/contract/": "tests/contract",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for name, _ in TREE:
        path = Path(PATHS.get(name, name))
        if not path.exists():
            raise FileNotFoundError(path)
    fig, ax = plt.subplots(figsize=(9.5, 0.36 * len(TREE) + 0.4))
    ax.axis("off")
    for row, (name, note) in enumerate(TREE):
        y = 1 - (row + 0.5) / len(TREE)
        ax.text(0.0, y, name, family="DejaVu Sans Mono", fontsize=10, color="#1f1f1e", va="center")
        if note:
            ax.text(0.47, y, note, fontsize=10, color="#4a4a45", va="center")
    fig.tight_layout()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=300)


if __name__ == "__main__":
    main()
