"""Design diagrams for Chapter 5 of report v20, drawn from the code as it is.

Usage: python docs/bao-cao/nguon_v20/ve_hinh_v20.py <output_dir>
- trien_khai.png: browser -> Next.js (frontend/) -> FastAPI (musicrec.api.main, uvicorn)
  -> DemoService (musicrec.serving.service) -> hashed release (artifacts/releases/...).
- tuan_tu_recommend.png: POST /recommend with the existing_user, new_user and popularity
  branches of DemoService (recommend_existing, recommend_new, recommend_popular).
- so_do_lop.png: the Recommender interface (fit, predict, recommend) in
  musicrec.recommenders.base, its implementations, M1 and M2.
- dieu_huong.png: the five Next.js pages (/, /nguoi-dung, /nguoi-moi, /luong, /ket-qua).
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

INK, MUTED, BLUE, FILL, LANE = "#1f1f1e", "#6b6a63", "#2a78d6", "#e8f1fc", "#f6f5f1"
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 10})


def box(ax, x, y, w, h, text, fill=FILL, edge=BLUE, size=9, weight="normal", align="center"):
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.03",
            facecolor=fill,
            edgecolor=edge,
            lw=1.2,
        )
    )
    ax.text(
        x if align == "center" else x - w / 2 + 0.12,
        y,
        text,
        ha=align,
        va="center",
        fontsize=size,
        color=INK,
        weight=weight,
        linespacing=1.2,
    )


def arrow(ax, a, b, label=None, style="-", offset=0.12, color=INK):
    ax.add_patch(
        FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=11, color=color, lw=1.1, ls=style)
    )
    if label:
        ax.text(
            (a[0] + b[0]) / 2,
            (a[1] + b[1]) / 2 + offset,
            label,
            ha="center",
            va="bottom",
            fontsize=8.5,
            color=MUTED,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.0},
        )


def deployment(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    ax.add_patch(Rectangle((3.0, 0.3), 11.8, 6.6, facecolor=LANE, edgecolor=MUTED, lw=0.8))
    ax.text(
        3.2,
        6.6,
        "Máy chủ (máy cá nhân trong khóa luận)",
        fontsize=9.5,
        color=INK,
        weight="bold",
        va="center",
    )
    box(ax, 1.3, 4.6, 2.2, 1.3, "Trình duyệt\ncủa người dùng")
    box(ax, 5.0, 4.6, 2.9, 1.6, "Giao diện Next.js\n(frontend/,\nReact, TypeScript)")
    box(ax, 9.0, 4.6, 3.0, 1.6, "Dịch vụ FastAPI\n(musicrec.api.main,\nuvicorn)")
    box(ax, 9.0, 1.9, 3.0, 1.4, "DemoService\n(musicrec.serving)\nđịnh tuyến nhánh")
    box(
        ax,
        12.9,
        1.9,
        3.1,
        1.7,
        "Gói mô hình\nartifacts/releases/\nkèm bản kê SHA-256",
        fill="#ffffff",
        edge=INK,
    )
    box(ax, 5.0, 1.9, 2.9, 1.3, "Streamlit\n(musicrec.ui, dự phòng)", fill="#ffffff", edge=MUTED)
    arrow(ax, (2.4, 4.6), (3.55, 4.6))
    ax.text(2.95, 5.6, "HTTP", ha="center", fontsize=8.5, color=MUTED)
    arrow(ax, (6.45, 4.6), (7.5, 4.6))
    ax.text(6.95, 5.6, "HTTP/JSON", ha="center", fontsize=8.5, color=MUTED)
    arrow(ax, (9.0, 3.8), (9.0, 2.6))
    arrow(ax, (11.35, 1.9), (10.5, 1.9))
    ax.text(
        12.9,
        3.15,
        "nạp một lần khi khởi động,\nkiểm tra mã băm từng tệp",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )
    arrow(ax, (6.45, 1.9), (7.5, 1.9), style="--", color=MUTED)
    fig.tight_layout()
    fig.savefig(out / "trien_khai.png", dpi=300)
    plt.close(fig)


def sequence(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 6.2))
    ax.set_xlim(0, 15)
    ax.set_ylim(-0.7, 13)
    ax.axis("off")
    cols = {"ui": 1.6, "api": 5.2, "svc": 9.0, "model": 12.9}
    names = {
        "ui": "Giao diện",
        "api": "FastAPI\nPOST /recommend",
        "svc": "DemoService",
        "model": "Mô hình trong gói",
    }
    for key, x in cols.items():
        box(ax, x, 12.3, 2.7, 0.9, names[key], size=9)
        ax.plot([x, x], [-0.4, 11.8], color=MUTED, lw=0.8, ls="--")
    y = 11.2
    arrow(ax, (cols["ui"], y), (cols["api"], y), "{user_id, model, k} hoặc {history, k}")
    y -= 0.8
    ax.text(
        cols["api"] + 0.15,
        y,
        "Pydantic kiểm tra kiểu, miền giá trị (lỗi 422)",
        fontsize=8.5,
        color=MUTED,
        va="center",
        bbox={"facecolor": "#fff8e1", "edgecolor": MUTED, "pad": 2},
    )
    frames = [
        (
            "[có user_id] nhánh existing_user",
            9.4,
            [
                ("api", "svc", "recommend_existing(user_id, k, model)"),
                ("svc", "model", "PureSVD / M1 / ALS .recommend(che train + xác thực)"),
                ("svc", "api", "danh sách K nghệ sĩ, fallback_used = false"),
            ],
        ),
        (
            "[history có 1–5 nghệ sĩ] nhánh new_user",
            6.4,
            [
                ("api", "svc", "recommend_new(profile, k)"),
                ("svc", "model", "M2.set_profile(...); M2.recommend(...)"),
                (
                    "svc",
                    "api",
                    "danh sách, ignored_item_ids, fallback nếu không nghệ sĩ nào trong danh mục",
                ),
            ],
        ),
        (
            "[history rỗng] nhánh popularity",
            3.4,
            [
                ("api", "svc", 'recommend_popular(k, "empty_profile")'),
                ("svc", "model", "Popularity.recommend(...)"),
                ("svc", "api", "danh sách, fallback_used = true"),
            ],
        ),
    ]
    for title, top, msgs in frames:
        ax.add_patch(Rectangle((3.6, top - 2.55), 11.1, 2.65, fill=False, edgecolor=BLUE, lw=1))
        ax.text(3.75, top - 0.12, "alt " + title, fontsize=8.5, color=BLUE, va="top", weight="bold")
        yy = top - 0.75
        for a, b, text in msgs:
            arrow(ax, (cols[a], yy), (cols[b], yy), text, style="--" if b == "api" else "-")
            yy -= 0.75
    arrow(
        ax,
        (cols["api"], 0.05),
        (cols["ui"], 0.05),
        "RecommendResponse (JSON); 404 nếu user_id không tồn tại",
        style="--",
    )
    fig.tight_layout()
    fig.savefig(out / "tuan_tu_recommend.png", dpi=300)
    plt.close(fig)


def class_diagram(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9.6)
    ax.axis("off")

    def uml(x, y, w, title, lines, h=None):
        h = h or 0.55 + 0.42 * len(lines)
        ax.add_patch(
            Rectangle((x - w / 2, y - h / 2), w, h, facecolor="#ffffff", edgecolor=INK, lw=1.1)
        )
        ax.add_patch(
            Rectangle((x - w / 2, y + h / 2 - 0.55), w, 0.55, facecolor=FILL, edgecolor=INK, lw=1.1)
        )
        ax.text(x, y + h / 2 - 0.27, title, ha="center", va="center", fontsize=9, weight="bold")
        for k, line in enumerate(lines):
            ax.text(
                x - w / 2 + 0.12,
                y + h / 2 - 0.85 - 0.42 * k,
                line,
                ha="left",
                va="center",
                fontsize=8.5,
                family="DejaVu Sans Mono",
            )
        return h

    uml(
        7.5,
        8.1,
        7.8,
        "«abstract» Recommender",
        [
            "fit(interactions) -> Recommender",
            "predict(user_id, item_id) -> float",
            "recommend(user_id, k, seen) -> list[Recommendation]",
        ],
    )
    names = ["Random", "Popularity", "UserCF", "ItemCF", "SVD", "PureSVD", "ImplicitALS"]
    xs = [1.55 + i * 1.98 for i in range(len(names))]
    for x, name in zip(xs, names, strict=True):
        uml(x, 4.9, 1.85, name, ["save(dir)", "load(dir)"])
        ax.add_patch(
            FancyArrowPatch(
                (x, 5.55),
                (7.5, 7.05),
                arrowstyle="-|>",
                mutation_scale=12,
                color=INK,
                lw=0.9,
                fc="white",
            )
        )
    uml(
        4.2,
        1.6,
        4.8,
        "M1Recommender",
        ["base: Recommender (PureSVD)", "prepare_candidates(user, seen)", "save(dir) / load(dir)"],
    )
    uml(
        10.6,
        1.6,
        4.8,
        "M2Recommender",
        ["item_cf: ItemCFRecommender", "set_profile(user, rows)", "profile_scores(user)"],
    )
    # M1 and M2 also subclass Recommender: route their links around the row of models.
    for x_box, side in [(4.2, -1), (10.6, 1)]:
        x_edge = x_box + side * 2.4
        x_lane = 7.5 + side * 7.25
        ax.plot([x_edge, x_lane, x_lane], [1.6, 1.6, 8.1], color=INK, lw=0.9)
        ax.add_patch(
            FancyArrowPatch(
                (x_lane, 8.1),
                (7.5 + side * 3.9, 8.1),
                arrowstyle="-|>",
                mutation_scale=12,
                color=INK,
                lw=0.9,
            )
        )
    ax.text(
        7.5,
        0.25,
        "Mọi lớp đều kế thừa Recommender; save/load lưu và nạp mô hình không huấn luyện lại.",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )
    fig.tight_layout()
    fig.savefig(out / "so_do_lop.png", dpi=300)
    plt.close(fig)


def navigation(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 6.6)
    ax.axis("off")
    box(ax, 7.5, 5.4, 3.6, 1.1, "Trang giới thiệu  /", weight="bold")
    pages = [
        (1.9, "Người dùng có sẵn\n/nguoi-dung\n(PureSVD, M1, ALS)"),
        (5.6, "Người dùng mới\n/nguoi-moi\n(M2, dự phòng)"),
        (9.4, "Luồng hoạt động\n/luong"),
        (13.1, "Kết quả thực nghiệm\n/ket-qua"),
    ]
    for x, text in pages:
        box(ax, x, 2.4, 3.3, 1.6, text)
        arrow(ax, (7.5, 4.85), (x, 3.2))
    ax.text(
        7.5,
        0.5,
        "Thanh điều hướng chung cho phép chuyển qua lại giữa năm trang; hai trang"
        " gợi ý gọi POST /recommend.",
        ha="center",
        fontsize=8.5,
        color=MUTED,
    )
    fig.tight_layout()
    fig.savefig(out / "dieu_huong.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    target = Path(sys.argv[1])
    target.mkdir(parents=True, exist_ok=True)
    deployment(target)
    sequence(target)
    class_diagram(target)
    navigation(target)
    print("ok", target)
