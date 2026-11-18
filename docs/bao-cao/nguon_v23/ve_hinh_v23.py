"""Figure 3.3 of report v23 (model and service architecture), redrawn to match Chapter 5.

Usage: python docs/bao-cao/nguon_v23/ve_hinh_v23.py <output_dir>
Writes kien_truc_v23.png. Same layered layout and black-and-white style as the figure it
replaces (v22, which showed Streamlit on top). Layers follow the code as it is:
- Next.js (frontend/) is the main interface and calls FastAPI over HTTP (Chapter 5, Fig. 5.2);
- FastAPI (musicrec.api.main) checks input with Pydantic and hands over to DemoService;
- DemoService (musicrec.serving.service) masks history and routes to the model, M1 or M2;
- Streamlit (musicrec.ui.app) is only a fallback and calls the same REST API;
- the release in artifacts/releases/ is loaded once, every file checked by SHA-256.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

plt.rcParams.update({"font.family": "Times New Roman"})
INK = "black"


def box(ax, x, y, w, h, title, sub, dashed=False, size=15):
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.0,rounding_size=0.06",
            facecolor="white",
            edgecolor=INK,
            lw=1.3,
            ls=(0, (4, 3)) if dashed else "-",
        )
    )
    ax.text(x, y + 0.17, title, ha="center", va="center", fontsize=size, weight="bold")
    ax.text(x, y - 0.2, sub, ha="center", va="center", fontsize=size - 1.5)


def arrow(ax, a, b, dashed=False):
    ax.add_patch(
        FancyArrowPatch(
            a,
            b,
            arrowstyle="-|>",
            mutation_scale=16,
            color=INK,
            lw=1.4,
            ls=(0, (4, 3)) if dashed else "-",
            shrinkA=0,
            shrinkB=0,
        )
    )


def main(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.6)
    ax.axis("off")
    w, h, x = 6.4, 0.75, 3.6
    ys = [5.0, 3.95, 2.9, 1.85, 0.8]
    layers = [
        ("Giao diện Next.js (giao diện chính)", "Nhập hồ sơ, chọn mô hình và hiển thị nghệ sĩ"),
        ("API FastAPI", "Kiểm tra đầu vào và trả JSON qua HTTP"),
        ("Dịch vụ khuyến nghị (DemoService)", "Che lịch sử và chọn mô hình chính, M1 hoặc M2"),
        ("Mô hình nền và tái xếp hạng M1", "Chấm điểm, chọn ứng viên và tạo danh sách"),
        ("Gói mô hình đã xuất", "Tham số, ánh xạ, ngưỡng và thông tin thẻ, có mã băm"),
    ]
    for y, (title, sub) in zip(ys, layers, strict=True):
        box(ax, x, y, w, h, title, sub)
    for y0, y1 in zip(ys, ys[1:], strict=False):
        arrow(ax, (x, y0 - h / 2), (x, y1 + h / 2))
    sx, sw = 8.45, 2.8
    box(ax, sx, ys[0], sw, h, "Giao diện Streamlit", "Phương án dự phòng", dashed=True, size=14)
    arrow(ax, (sx, ys[0] - h / 2), (x + w / 2, ys[1]), dashed=True)
    ax.text(
        sx,
        ys[1] - 0.15,
        "gọi cùng API qua HTTP",
        ha="center",
        va="center",
        fontsize=12,
        style="italic",
    )
    fig.savefig(out / "kien_truc_v23.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    target = Path(sys.argv[1])
    target.mkdir(parents=True, exist_ok=True)
    main(target)
