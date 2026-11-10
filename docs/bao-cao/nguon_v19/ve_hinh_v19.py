"""Diagrams for report v19, Chapter 3: use-case diagram and the two-lane processing flow.

Usage: python docs/bao-cao/nguon_v19/ve_hinh_v19.py <output_dir>
Writes so_do_ca_su_dung.png and luong_hai_lan.png (300 dpi). Drawn with matplotlib only;
the content follows Section 3.1 (actors, use cases) and Section 3.3 (offline/online flows).
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

INK, MUTED, BLUE, FILL, LANE = "#1f1f1e", "#6b6a63", "#2a78d6", "#e8f1fc", "#f6f5f1"
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 10})


def actor(ax, x, y, label):
    ax.add_patch(plt.Circle((x, y + 0.42), 0.12, fill=False, color=INK, lw=1.2))
    ax.plot([x, x], [y + 0.30, y - 0.05], color=INK, lw=1.2)
    ax.plot([x - 0.22, x + 0.22], [y + 0.18, y + 0.18], color=INK, lw=1.2)
    ax.plot([x, x - 0.18], [y - 0.05, y - 0.35], color=INK, lw=1.2)
    ax.plot([x, x + 0.18], [y - 0.05, y - 0.35], color=INK, lw=1.2)
    ax.text(x, y - 0.55, label, ha="center", va="top", color=INK, fontsize=9.5)


def use_case(ax, x, y, label, w=3.9, h=0.66):
    ax.add_patch(Ellipse((x, y), w, h, facecolor=FILL, edgecolor=BLUE, lw=1.2))
    ax.text(x, y, label, ha="center", va="center", color=INK, fontsize=9)


def link(ax, a, b, style="-", arrow=False, label=None):
    if arrow:
        ax.add_patch(
            FancyArrowPatch(a, b, arrowstyle="->", mutation_scale=10, color=MUTED, lw=1, ls=style)
        )
    else:
        ax.plot([a[0], b[0]], [a[1], b[1]], color=MUTED, lw=1, ls=style)
    if label:
        ax.text(
            (a[0] + b[0]) / 2,
            (a[1] + b[1]) / 2 + 0.08,
            label,
            ha="center",
            fontsize=8,
            color=MUTED,
            style="italic",
        )


def use_case_diagram(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9.4)
    ax.axis("off")
    ax.add_patch(Rectangle((2.3, 0.3), 7.4, 8.8, fill=False, edgecolor=INK, lw=1.2))
    ax.text(
        6.0,
        8.85,
        "Hệ thống khuyến nghị nghệ sĩ MusicRec",
        ha="center",
        fontsize=10.5,
        color=INK,
        weight="bold",
    )
    cases = {
        "lich_su": (6.0, 8.05, "Xem lịch sử nghe"),
        "goi_y": (6.0, 7.05, "Nhận gợi ý nghệ sĩ"),
        "m1": (6.0, 6.05, "Bật M1 và so sánh với PureSVD"),
        "chon": (6.0, 4.85, "Chọn nghệ sĩ khởi đầu"),
        "du_phong": (6.0, 3.85, "Nhận danh sách dự phòng (M2)"),
        "thuc_nghiem": (6.0, 2.45, "Chạy lại thực nghiệm"),
        "chi_so": (6.0, 1.3, "Xem bảng chỉ số và kiểm định"),
    }
    for x, y, label in cases.values():
        use_case(ax, x, y, label)
    actor(ax, 1.2, 6.9, "Người dùng\ncó sẵn")
    actor(ax, 1.2, 4.0, "Người dùng\nmới")
    actor(ax, 10.8, 1.9, "Người\nđánh giá")
    for key in ["lich_su", "goi_y", "m1"]:
        link(ax, (1.5, 6.95), (cases[key][0] - 1.95, cases[key][1]))
    for key in ["chon", "du_phong"]:
        link(ax, (1.5, 4.05), (cases[key][0] - 1.95, cases[key][1]))
    for key in ["thuc_nghiem", "chi_so"]:
        link(ax, (10.5, 1.95), (cases[key][0] + 1.95, cases[key][1]))
    link(ax, (6.0, 6.36), (6.0, 6.74), style="--", arrow=True)
    ax.text(6.15, 6.52, "«mở rộng»", fontsize=8, color=MUTED, style="italic", va="center")
    link(ax, (6.0, 4.54), (6.0, 4.16), style="--", arrow=True)
    ax.text(6.15, 4.35, "«bao gồm»", fontsize=8, color=MUTED, style="italic", va="center")
    fig.tight_layout()
    fig.savefig(out / "so_do_ca_su_dung.png", dpi=300)
    plt.close(fig)


def box(ax, x, y, label, w=1.85, h=0.95, fill=FILL, edge=BLUE):
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.04",
            facecolor=fill,
            edgecolor=edge,
            lw=1.2,
        )
    )
    ax.text(x, y, label, ha="center", va="center", fontsize=9, color=INK, linespacing=1.15)


def arrow(ax, a, b):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=11, color=INK, lw=1.1))


def two_lane_flow(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 3.9))
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0.2, 6.9)
    ax.axis("off")
    for y0, title in [(3.95, "Luồng ngoại tuyến"), (0.3, "Luồng trực tuyến")]:
        ax.add_patch(Rectangle((0.1, y0), 13.0, 2.85, facecolor=LANE, edgecolor=MUTED, lw=0.8))
        ax.text(0.3, y0 + 2.6, title, fontsize=10, weight="bold", color=INK, va="center")
    top = 5.05
    xs = [1.3, 3.45, 5.6, 7.75, 9.9, 12.0]
    labels = [
        "Dữ liệu gốc\nLast.fm",
        "Kiểm tra,\nchia tập",
        "Biến đổi\n(chỉ học từ\ntập huấn luyện)",
        "Huấn luyện,\ntinh chỉnh",
        "Đánh giá\n(khóa cấu hình\ntrước kiểm thử)",
        "Xuất gói\nmô hình",
    ]
    for i, (x, label) in enumerate(zip(xs, labels, strict=True)):
        box(ax, x, top, label, w=1.7, h=1.15)
        if i:
            arrow(ax, (xs[i - 1] + 0.88, top), (x - 0.88, top))
    bottom = 1.4
    xb = [1.3, 3.75, 6.2, 8.85, 11.6]
    labels_b = [
        "Yêu cầu\n(mã người dùng\nhoặc lịch sử)",
        "Kiểm tra\nđầu vào",
        "Định tuyến\nnhánh",
        "Chấm điểm\nPureSVD / ALS,\nM1 hoặc M2",
        "Phản hồi\n(danh sách, lý do,\nphiên bản)",
    ]
    for i, (x, label) in enumerate(zip(xb, labels_b, strict=True)):
        box(ax, x, bottom, label, w=1.9, h=1.15)
        if i:
            arrow(ax, (xb[i - 1] + 0.98, bottom), (x - 0.98, bottom))
    box(ax, 12.0, 3.85, "Gói mô hình\ncó mã băm", w=1.9, h=0.8, fill="#ffffff", edge=INK)
    arrow(ax, (12.0, top - 0.58), (12.0, 4.25))
    arrow(ax, (11.05, 3.85), (8.85, bottom + 0.58))
    fig.tight_layout()
    fig.savefig(out / "luong_hai_lan.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    target = Path(sys.argv[1])
    target.mkdir(parents=True, exist_ok=True)
    use_case_diagram(target)
    two_lane_flow(target)
    print("ok", target)
