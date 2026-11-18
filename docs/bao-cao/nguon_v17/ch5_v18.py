# ruff: noqa: E501, F821
# Chapter 5 of report v18 (advisor feedback of 06/11/2026; delivered UI is Next.js + FastAPI).
# Executed by build_v17.py with H2, H3, P, N, T, F, CODE in scope. Numbers come from files.
import json as _json

E = "outputs/demo/chuong_5_20261107/"
DR = "docs/results/chinh_thuc_cloud_20261026/"


def f(x, d=2):
    s = f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s.replace("-", "−")


def load(path):
    return _json.loads(open(path, encoding="utf-8").read())


ev = load(E + "chuong_5.json")
lat = load("outputs/demo/latency_20261107/latency.json")["latency"]
rel = load("docs/results/chuong_5/check_release.json")
example = load(E + "vi_du_phan_hoi.json")
test_stats = {(r["a"], r["b"]): r for r in load(DR + "test/statistics_ndcg_at_10.json")["pairs"]}
files = {x["path"]: x["bytes"] for x in ev["release_files"]}
cons = ev["online_offline_top10"]

P(
    "Chương này trình bày cách tổ chức mã nguồn và đóng gói mô hình, thiết kế dịch vụ API bằng "
    "FastAPI [32], giao diện minh họa bằng Next.js [33], kết quả kiểm thử hệ thống, sau đó tổng kết "
    "mức độ đạt mục tiêu, hạn chế và hướng phát triển của khóa luận. Hệ thống được mô tả là phiên bản "
    f"bàn giao dùng gói mô hình {ev['release']}, tức các mô hình đã khóa ở Chương 4."
)

H2("5.1 Kiến trúc triển khai")
H3("5.1.1 Tổ chức mã nguồn")
P(
    "Mã nguồn được tổ chức theo các lớp chức năng tách biệt để phần thực nghiệm và phần ứng dụng dùng "
    "chung một mã xử lý (Hình 5.1). Gói musicrec gồm mô-đun dữ liệu (làm sạch, chia tập, ánh xạ, biểu "
    "diễn, chia người dùng cho giao thức người dùng mới), mô-đun mô hình chứa các lớp Random, Popularity, "
    "UserCF, ItemCF, SVD có độ lệch, PureSVD, ALS, M1 và M2 dùng chung một giao diện gồm các phương thức "
    "huấn luyện, chấm điểm, gợi ý, lưu và nạp; mô-đun đánh giá chứa bộ tính chỉ số; mô-đun phục vụ "
    "(serving) đọc gói mô hình và định tuyến yêu cầu; mô-đun api chứa dịch vụ FastAPI. Giao diện Next.js "
    "nằm trong thư mục frontend và chỉ giao tiếp với hệ thống qua API. Giao diện Streamlit [34] trong "
    "mô-đun ui được giữ làm phương án dự phòng khi trình diễn."
)
F(
    E + "anh/hinh_5_1_cay.png",
    "Tổ chức mã nguồn của hệ thống",
    "kho mã nguồn, nhánh research/data-preparation-model-survey; hình sinh bằng scripts/ve_hinh_chuong_5.py.",
    width_cm=15.5,
)
H3("5.1.2 Nạp gói mô hình")
grp = [
    (
        "Dữ liệu hiển thị và che lịch sử",
        ["data/artists.json", "data/train.parquet", "data/validation.parquet"],
    ),
    ("PureSVD (k = 16)", [k for k in files if k.startswith("models/pure_svd/")]),
    ("M1 (λ = 0,75; β = 0,5)", [k for k in files if k.startswith("models/m1/")]),
    ("Implicit ALS", [k for k in files if k.startswith("models/implicit_als/")]),
    ("M2 (α = 0,75; n_min = 10)", [k for k in files if k.startswith("models/m2/")]),
    ("Bản kê và mã băm", ["manifest.json"]),
]
P(
    "Các mô hình phục vụ được xuất thành một gói phát hành gồm tham số mô hình, ánh xạ mã người dùng và "
    "nghệ sĩ, lịch sử huấn luyện và xác thực dùng để che các nghệ sĩ đã nghe, bảng tên nghệ sĩ, thông "
    "tin thẻ cho M2, cấu hình M1, mã phiên bản và mã băm SHA-256 của từng tệp (Bảng 5.1). Khi khởi động, "
    "dịch vụ nạp gói một lần vào bộ nhớ và kiểm tra tập tệp cùng mã băm của từng tệp so với bản kê; nếu "
    "thiếu, thừa hoặc lệch tệp nào, dịch vụ từ chối khởi động. Thời gian từ khi khởi động tiến trình Python "
    "đến khi dịch vụ sẵn sàng, đo trong ba tiến trình mới trên máy cá nhân, là "
    + "; ".join(f(s) for s in ev["load_seconds_fresh_process"])
    + f" giây (trung vị {f(ev['load_seconds_median'])} giây), gồm cả thời gian nạp thư viện."
)
T(
    "Các tệp trong gói mô hình phục vụ",
    [3600, 3188, 2000],
    ["Thành phần", "Số tệp", "Dung lượng (MB)"],
    [[name, str(len(paths)), f(sum(files[p] for p in paths) / 1e6)] for name, paths in grp]
    + [["Tổng", str(len(files)), f(ev["release_total_bytes"] / 1e6)]],
    E + "chuong_5.json (danh sách tệp và kích thước). 1 MB = 1.000.000 byte.",
)

H2("5.2 Thiết kế dịch vụ API")
H3("5.2.1 Các chức năng và lược đồ")
P(
    "Dịch vụ API cung cấp năm chức năng ở Bảng 5.2. Đầu vào và đầu ra được định nghĩa bằng lược đồ "
    "Pydantic, nhờ đó FastAPI tự kiểm tra kiểu dữ liệu và sinh tài liệu tương tác tại đường dẫn /docs "
    "(Hình 5.2). Ứng với ba nhánh xử lý đã thiết kế ở Chương 3, POST /recommend định tuyến như sau: "
    "người dùng có trong dữ liệu huấn luyện nhận gợi ý từ PureSVD, M1 hoặc ALS; người dùng mới cung cấp từ "
    "1 đến 5 nghệ sĩ nhận gợi ý từ M2; hồ sơ rỗng nhận danh sách Popularity và được đánh dấu là dự phòng."
)
T(
    "Các chức năng của dịch vụ API",
    [1200, 2700, 4888],
    ["Phương thức", "Đường dẫn", "Chức năng"],
    [
        [
            "GET",
            "/health",
            "Trạng thái dịch vụ, phiên bản gói và cấu hình từng mô hình đang phục vụ.",
        ],
        ["GET", "/users?offset=&limit=", "Danh sách người dùng có sẵn kèm số nghệ sĩ đã nghe."],
        [
            "GET",
            "/users/{user_id}/history",
            "Lịch sử nghe (huấn luyện và xác thực) của một người dùng, xếp theo lượt nghe.",
        ],
        [
            "GET",
            "/artists?q=&limit=",
            "Tìm nghệ sĩ theo tên trong danh mục M2 để người dùng mới chọn.",
        ],
        [
            "POST",
            "/recommend",
            "Nhận user_id hoặc history (0–5 nghệ sĩ), số lượng K (1–100), mô hình (pure_svd, m1, implicit_als) và tùy chọn λ, β của M1; trả danh sách gợi ý.",
        ],
    ],
    "src/musicrec/api/main.py, src/musicrec/api/schemas.py.",
    align=["center", "left", "left"],
)
F(
    E + "anh/hinh_5_2_docs.png",
    "Tài liệu tương tác của API tại đường dẫn /docs",
    "ảnh chụp dịch vụ chạy trên máy cá nhân ngày 07/11/2026.",
    width_cm=15.5,
)
H3("5.2.2 Ví dụ hợp đồng đầu vào đầu ra")
P(
    "Ví dụ sau là một lần gọi thật: người dùng mới chọn ba nghệ sĩ Lady Gaga (mã 89), Britney Spears (mã "
    "289) và Christina Aguilera (mã 292), yêu cầu K = 3. Lượt nghe không bắt buộc; khi thiếu, dịch vụ gán "
    "mức nghe trung bình nằm giữa hai ngưỡng phân vị 40% và 60% của nhóm học."
)
CODE(
    'POST /recommend\n{"history": [{"item_id": "89"}, {"item_id": "289"}, {"item_id": "292"}], "k": 3}'
)
first = example["recommendations"][0]
CODE(
    "{\n"
    f'  "model_version": "{example["model_version"]}",\n'
    f'  "branch": "{example["branch"]}", "model": "{example["model"]}",\n'
    f'  "fallback_used": false, "fallback_reason": null, "ignored_item_ids": [],\n'
    f'  "mean_listeners": {example["mean_listeners"]:.2f},\n'
    '  "recommendations": [\n'
    f'    {{"rank": 1, "item_id": "{first["item_id"]}", "name": "{first["name"]}", "listeners": {first["listeners"]},\n'
    f'     "score": {first["score"]:.4f}, "reason": "{first["reason"]}", "url": "…", "picture_url": "…"}},\n'
    "    …\n  ]\n}"
)
names = ", ".join(r["name"] for r in example["recommendations"])
P(
    f"Ba nghệ sĩ được gợi ý là {names}. Trường score chỉ dùng để so sánh các nghệ sĩ trong cùng một danh "
    "sách, không phải xác suất yêu thích. Trường branch cho biết nhánh xử lý (existing_user, new_user hoặc "
    "popularity), fallback_used và fallback_reason cho biết có dùng phương án dự phòng hay không và vì "
    "sao, ignored_item_ids liệt kê các mã nghệ sĩ không có trong danh mục M2. Trường reason ghi thành phần "
    "nào của M2 có đóng góp (cf là điểm cộng tác, content là điểm nội dung thẻ); mean_listeners là số "
    "người nghe trung bình của danh sách, tức ARP tính riêng cho một người dùng."
)
H3("5.2.3 Xử lý yêu cầu không hợp lệ")
P(
    "Bảng 5.3 liệt kê các trường hợp đầu vào không hợp lệ hoặc đặc biệt và phản hồi của dịch vụ theo mã "
    "đã cài đặt. Lỗi kiểu dữ liệu và miền giá trị được trả dưới dạng JSON có vị trí trường lỗi và nội dung "
    "mô tả, không trả dấu vết ngoại lệ của máy chủ."
)
T(
    "Xử lý các trường hợp đầu vào không hợp lệ hoặc đặc biệt",
    [3900, 1000, 3888],
    ["Trường hợp", "Mã HTTP", "Phản hồi"],
    [
        [
            "K không phải số nguyên, nhỏ hơn 1 hoặc lớn hơn 100",
            "422",
            "Chỉ rõ trường k và miền hợp lệ.",
        ],
        ["Không có cả user_id lẫn history", "422", "Yêu cầu cung cấp một trong hai."],
        [
            "user_id không có trong dữ liệu huấn luyện",
            "404",
            "Thông báo không tìm thấy người dùng.",
        ],
        ["history rỗng", "200", "Danh sách Popularity, fallback_used = true, lý do empty_profile."],
        [
            "history có nghệ sĩ ngoài danh mục M2",
            "200",
            "Bỏ qua mã đó, liệt kê trong ignored_item_ids; nếu mọi nghệ sĩ đều ngoài danh mục thì dự phòng về phổ biến.",
        ],
        ["history có nghệ sĩ trùng hoặc quá 5 nghệ sĩ", "422", "Thông báo hồ sơ không hợp lệ."],
        ["Lượt nghe âm hoặc bằng 0", "422", "Chỉ rõ trường listening_count."],
        ["Mô hình không phục vụ (ví dụ svd)", "422", "Liệt kê ba giá trị hợp lệ."],
        [
            "λ, β của M1 ngoài 12 điểm của lưới xác thực, hoặc chỉ có một trong hai",
            "422",
            "Thông báo tham số phải thuộc lưới đã đánh giá.",
        ],
    ],
    "src/musicrec/api/schemas.py, src/musicrec/serving/service.py; kiểm chứng ở Bảng 5.4.",
    align=["left", "center", "left"],
)

H2("5.3 Thiết kế giao diện minh họa")
H3("5.3.1 Luồng sử dụng")
P(
    "Giao diện minh họa được xây dựng bằng Next.js 16 với React 19 và TypeScript, gồm năm trang: giới thiệu, "
    "người dùng có sẵn, người dùng mới, luồng hoạt động và kết quả. Mọi danh sách gợi ý lấy từ API thật; các "
    "số liệu tĩnh trên trang kết quả được sinh tự động từ tệp kết quả của Chương 4."
)
P(
    "Ở trang người dùng có sẵn (Hình 5.3), người dùng nhập hoặc chọn ngẫu nhiên một mã trong 1.877 người "
    "dùng, xem lịch sử nghe và chọn K = 5, 10 hoặc 20. Hai danh sách PureSVD và M1 hiển thị cạnh nhau; mỗi "
    "nghệ sĩ có thanh số người nghe trên tập huấn luyện, đường nối thể hiện nghệ sĩ lên hạng, xuống hạng "
    "hoặc rời khỏi danh sách khi bật M1, và phía trên ghi số người nghe trung bình của hai danh sách. Công "
    "tắc M1 khi tắt tương đương λ = 1, β = 0 nên cho đúng thứ tự PureSVD; người dùng có thể chọn λ, β "
    "trong 12 điểm của lưới xác thực, kèm NDCG@10 và ARP xác thực của điểm đó."
)
F(
    E + "anh/hinh_5_3_nguoi_dung.png",
    "Trang người dùng có sẵn so sánh PureSVD và M1 (người dùng 2, K = 10)",
    "ảnh chụp giao diện Next.js kết nối API, máy cá nhân, ngày 07/11/2026.",
    width_cm=13.5,
)
P(
    "Ở trang người dùng mới (Hình 5.4), người dùng tìm nghệ sĩ theo tên hoặc chọn trong danh sách nghệ sĩ "
    "được nghe nhiều nhất, tối đa năm nghệ sĩ; danh sách gợi ý của M2 cập nhật ngay sau mỗi lần chọn. Khi "
    "chưa chọn nghệ sĩ nào (Hình 5.5), hệ thống trả danh sách Popularity và hiển thị nhãn dự phòng cùng "
    "thông báo. Dưới kết quả, giao diện ghi rõ kết quả thực nghiệm của M2 trên tập kiểm thử để người xem "
    "không hiểu nhầm rằng M2 chính xác hơn Popularity."
)
F(
    E + "anh/hinh_5_4_nguoi_moi.png",
    "Trang người dùng mới với ba nghệ sĩ đã chọn (M2)",
    "ảnh chụp giao diện Next.js kết nối API, máy cá nhân, ngày 07/11/2026.",
    width_cm=13.5,
)
F(
    E + "anh/hinh_5_5_rong.png",
    "Trang người dùng mới khi chưa chọn nghệ sĩ (dự phòng Popularity)",
    "ảnh chụp giao diện Next.js kết nối API, máy cá nhân, ngày 07/11/2026.",
    width_cm=13.5,
)
H3("5.3.2 Thông báo và thời gian chờ")
P(
    "Trong khi chờ phản hồi, giao diện giữ nguyên lựa chọn của người dùng. Thông báo được tách thành ba "
    "loại: lỗi đầu vào do API trả về (ví dụ mã người dùng không tồn tại), trường hợp dự phòng (kết quả vẫn "
    "hợp lệ nhưng dựa trên mức phổ biến) và lỗi kết nối khi dịch vụ chưa chạy. Phiên bản hiện tại không đặt "
    "thời gian chờ riêng cho lời gọi API mà dùng thời gian chờ mặc định của trình duyệt; đây là một điểm "
    "cần bổ sung khi triển khai thật (mục 5.7)."
)

H2("5.4 Kiểm thử hệ thống")
H3("5.4.1 Kiểm thử chức năng")
P(
    "Bảng 5.4 trình bày 12 ca kiểm thử chức năng, chạy tự động qua HTTP bằng TestClient của FastAPI trên "
    "gói mô hình thật. Ngoài ra, bộ kiểm thử đơn vị và hợp đồng API của dự án (145 ca, chạy bằng pytest "
    f"trên gói mô hình thu nhỏ) đều đạt. Kết quả: {ev['cases_passed']} trên {len(ev['cases'])} ca đạt."
)
T(
    "Các ca kiểm thử chức năng trên gói mô hình thật",
    [700, 3700, 3388, 1000],
    ["Mã", "Nội dung kiểm thử", "Kết quả mong đợi", "Kết quả"],
    [[c["ma"], c["noi_dung"], c["mong_doi"], c["ket_qua"]] for c in ev["cases"]],
    E
    + "ca_kiem_thu.csv (gồm cột ghi chú chi tiết), chuong_5.json (script scripts/check_chuong_5.py).",
    align=["center", "left", "left", "center"],
)
H3("5.4.2 Đối chiếu trực tuyến và ngoại tuyến")
P(
    "Để trả lời RQ5 về tính nhất quán, nhóm so sánh danh sách 10 nghệ sĩ do API trả về với danh sách tính "
    "trực tiếp từ các tệp mô hình gốc của lần chạy chính thức (không qua gói phát hành), cùng quy tắc che "
    "lịch sử huấn luyện và xác thực. Phép so sánh gồm toàn bộ 1.877 người dùng với PureSVD, M1 và ALS, và "
    "189 người dùng để dành của giao thức người dùng mới với M2 ở N = 1, 3, 5, dùng đúng hồ sơ như khi đánh "
    "giá. Ba chỉ tiêu là tỷ lệ người dùng có danh sách trùng hoàn toàn cả thứ tự, độ tương đồng Jaccard "
    "trung bình giữa hai tập nghệ sĩ và chênh lệch điểm lớn nhất trên các nghệ sĩ chung."
)
T(
    "Đối chiếu danh sách top-10 giữa API và đánh giá ngoại tuyến",
    [2700, 1300, 1700, 1500, 1588],
    [
        "Mô hình",
        "Số người dùng",
        "Trùng cả thứ tự",
        "Jaccard trung bình",
        "Chênh lệch điểm lớn nhất",
    ],
    [
        [
            label,
            str(cons[k]["users"]).replace("1877", "1.877"),
            f"{f(100 * cons[k]['identical_order_rate'])}%",
            f(cons[k]["mean_jaccard"], 4),
            f"{cons[k]['max_abs_score_difference']:g}",
        ]
        for k, label in [
            ("pure_svd", "PureSVD"),
            ("m1", "M1"),
            ("implicit_als", "Implicit ALS"),
            ("m2_n1", "M2, N = 1"),
            ("m2_n3", "M2, N = 3"),
            ("m2_n5", "M2, N = 5"),
        ]
    ],
    E + "chuong_5.json, mục online_offline_top10.",
)
P(
    "Mọi danh sách trùng hoàn toàn cả thứ tự và điểm. Ngoài ra, khi tính lại các chỉ số của Chương 4 từ "
    f"danh sách do dịch vụ tạo ra, {rel['warm']['rows_compared']} dòng chỉ số của người dùng có sẵn "
    f"(Popularity, PureSVD, M1, ALS tại K = 5, 10, 20) và {rel['m2']['rows_compared']} dòng của M2 đều khớp "
    "bảng chính thức với sai số không quá 1e−12. Trả lời RQ5: ứng dụng cho kết quả nhất quán với đánh giá "
    "ngoại tuyến."
)
H3("5.4.3 Đo thời gian phản hồi")
P(
    "Thời gian phản hồi được đo từ phía người gọi qua HTTP, gồm cả thời gian truyền trên máy cục bộ. Dịch vụ "
    "chạy bằng uvicorn, một tiến trình, nhận một yêu cầu tại một thời điểm, trên máy cá nhân (Windows 11, "
    "Intel Core i5-11300H, 8 luồng logic, Python 3.11.9, FastAPI 0.141.1). Mỗi cấu hình chạy 20 lượt khởi "
    "động không tính, sau đó đo 200 lượt với cùng yêu cầu. Nhóm chưa đo riêng thời gian xử lý bên trong dịch "
    "vụ."
)
LAT = [
    ("POST /recommend pure_svd", "Người dùng có sẵn, PureSVD"),
    ("POST /recommend m1", "Người dùng có sẵn, M1"),
    ("POST /recommend implicit_als", "Người dùng có sẵn, ALS"),
    ("POST /recommend m2 (3 artists)", "Người dùng mới, M2 (3 nghệ sĩ)"),
    ("POST /recommend popularity", "Lịch sử rỗng (Popularity)"),
    ("GET /artists?q=", "Tìm nghệ sĩ"),
    ("GET /users/{id}/history", "Lịch sử người dùng"),
]
T(
    "Thời gian phản hồi của dịch vụ (ms)",
    [3388, 1350, 1350, 1350, 1350],
    ["Cấu hình", "Trung bình", "Trung vị", "Độ lệch chuẩn", "P95"],
    [
        [
            lab,
            f(lat[k]["mean_ms"]),
            f(lat[k]["median_ms"]),
            f(lat[k]["stdev_ms"]),
            f(lat[k]["p95_ms"]),
        ]
        for k, lab in LAT
    ],
    "outputs/demo/latency_20261107/latency.json (script scripts/measure_latency.py, người dùng 2, K = 10).",
)
rec = [lat[k]["median_ms"] for k, _ in LAT[:5]]
P(
    f"Trung vị thời gian phản hồi của POST /recommend nằm trong khoảng {f(min(rec))} đến {f(max(rec))} ms. "
    "M1 chậm hơn PureSVD vì phải lấy 100 ứng viên và tính độ tương đồng giữa các ứng viên; M2 tính điểm cộng "
    "tác và điểm nội dung từ hồ sơ mới ở mỗi yêu cầu. Các số này đo trên một máy cá nhân, chưa phải trên máy "
    "chủ triển khai và chưa có tải đồng thời."
)

H2("5.5 Mức độ đạt mục tiêu")
P("Bảng 5.7 đối chiếu năm mục tiêu cụ thể ở mục 1.3.2 với kết quả đạt được.")
t_m1 = test_stats[("m1", "pure_svd")]
T(
    "Đối chiếu mục tiêu và kết quả",
    [3000, 1300, 4488],
    ["Mục tiêu", "Mức độ", "Minh chứng"],
    [
        [
            "1. Quy trình tiền xử lý Last.fm kiểm tra và chạy lại được",
            "Đạt",
            "Mục 3.4, 3.5; chạy lại từ dữ liệu gốc cho tệp trùng từng byte, khớp 70 con số của Chương 3; Phụ lục A, B.",
        ],
        [
            "2. Bốn mô hình lọc cộng tác và hai mô hình cơ sở dùng chung giao diện",
            "Đạt",
            "Bảng 3.3, 4.3, 4.5; tinh chỉnh 48 cấu hình trên tập xác thực, khóa cấu hình trước khi kiểm thử.",
        ],
        [
            "3. M1 và M2 kèm thử nghiệm loại bỏ thành phần",
            "Đạt một phần",
            "Bảng 4.11, 4.13 đến 4.15. M1 giảm ARP mà không giảm có ý nghĩa NDCG@10; M2 được xây dựng và đánh giá đúng giao thức nhưng chưa vượt Popularity về độ chính xác.",
        ],
        [
            "4. Đánh giá bằng chỉ số xếp hạng và chỉ số bổ sung",
            "Đạt",
            "Bảng 4.5 đến 4.8: tám chỉ số tại K = 5, 10, 20, kiểm định Wilcoxon, hiệu chỉnh Holm, khoảng tin cậy bootstrap.",
        ],
        [
            "5. Dịch vụ API, giao diện minh họa, xử lý đầu vào không hợp lệ",
            "Đạt một phần",
            "Mục 5.2 đến 5.4; Bảng 5.3 đến 5.6: 12/12 ca kiểm thử đạt, danh sách trùng hoàn toàn với đánh giá ngoại tuyến. Giao diện chính là Next.js thay cho Streamlit (Streamlit giữ làm dự phòng); chưa triển khai lên máy chủ công khai.",
        ],
    ],
    "Chương 3 đến 5; docs/results/doi_chieu_muc_tieu.md.",
    align=["left", "center", "left"],
)

H2("5.6 Kết luận")
P(
    "Khóa luận đã xây dựng một hệ thống khuyến nghị nghệ sĩ dựa trên lọc cộng tác với quy trình thực nghiệm "
    "thống nhất trên bộ dữ liệu Last.fm HetRec 2011. Quy trình dữ liệu được kiểm chứng chặt chẽ: ánh xạ và "
    "các ngưỡng biến đổi chỉ học từ tập huấn luyện, đích ngoài danh mục được báo cáo riêng, bộ đánh giá được "
    "kiểm tra bằng ví dụ tính tay và đối chiếu với thư viện chuẩn, và cấu hình được khóa trước khi mở tập "
    "kiểm thử. Trên tập kiểm thử, PureSVD nhị phân đạt NDCG@10 cao nhất trong sáu mô hình đối sánh là "
    "0,182780, cao hơn Popularity 0,114005 và khác biệt có ý nghĩa thống kê; UserCF, ItemCF và SVD có độ "
    "lệch không vượt được Popularity. Mô-đun tái xếp hạng M1 giảm độ phổ biến trung bình của danh sách "
    f"15,69% với mức giảm NDCG@10 0,75% không có ý nghĩa thống kê (p sau Holm {f(t_m1['holm_p'], 3)}). "
    "Mô-đun dự phòng M2 chưa vượt phương án chỉ dựa vào phổ biến về NDCG@10 ở N = 1, 3 và 5, dù tăng độ bao "
    "phủ và giảm ARP. Thực nghiệm mở rộng cho thấy implicit ALS đạt NDCG@10 0,217453, cao hơn PureSVD có ý "
    "nghĩa thống kê. Hệ thống được đóng gói thành dịch vụ FastAPI và giao diện Next.js, cho danh sách trùng "
    f"hoàn toàn với đánh giá ngoại tuyến và thời gian phản hồi trung vị từ {f(min(rec))} đến {f(max(rec))} ms "
    "trên máy cá nhân."
)

H2("5.7 Hạn chế")
P(
    "Thứ nhất, dữ liệu Last.fm HetRec 2011 không có thời điểm của từng lượt nghe, nên phép chia ngẫu nhiên "
    "chỉ kiểm tra khả năng tìm lại một phần nghệ sĩ đã nghe, không mô phỏng việc dự đoán lần nghe tiếp theo. "
    "Thứ hai, mỗi người dùng chỉ được ghi nhận những nghệ sĩ nghe nhiều nhất và phần lớn có đúng 50 nghệ sĩ, "
    "nên ảnh hưởng của độ dài lịch sử chỉ khảo sát được qua thí nghiệm Given-N. Thứ ba, dữ liệu được thu thập "
    "năm 2011 nên không phản ánh thị hiếu âm nhạc hiện nay. Thứ tư, điểm đại diện 1–5 là phép quy đổi của "
    "nhóm từ phân vị lượt nghe, không phải đánh giá do người nghe tự chấm, nên RMSE chỉ có ý nghĩa tham khảo. "
    "Thứ năm, kết quả dựa trên một lần chia dữ liệu với một hạt giống; PureSVD là tất định nên chạy lại với "
    "hạt giống khác không tạo ra kiểm chứng độc lập."
)
P(
    "Thứ sáu, độ đa dạng ILD và phần phạt của M1 cùng dựa trên độ tương đồng đồng nghe; thước đo độc lập theo "
    "thẻ cho thấy mức tăng đa dạng nhỏ hơn. Thứ bảy, thẻ nghệ sĩ do người dùng gán và chỉ khoảng một phần ba "
    "danh mục có thẻ, làm giới hạn M2; giao thức người dùng mới chỉ có chưa tới 200 người mỗi nhóm. Thứ tám, "
    "M1 được tinh chỉnh trên PureSVD trong khi ALS là mô hình chính xác nhất đã đo. Cuối cùng, ứng dụng ở mức "
    "minh họa: chưa triển khai lên máy chủ công khai, giao diện chưa đặt thời gian chờ riêng cho lời gọi API, "
    "chưa kiểm thử tải nhiều người dùng đồng thời và chưa đánh giá với người dùng thật."
)

H2("5.8 Hướng phát triển")
P(
    "Từ các hạn chế trên, khóa luận đề xuất một số hướng phát triển. Về dữ liệu, có thể dùng bộ dữ liệu nghe "
    "nhạc có dấu thời gian như LFM-2b [35] để chia tập theo mốc thời gian thay cho chia ngẫu nhiên. Về mô "
    "hình, có thể bổ sung các mô hình tối ưu trực tiếp cho xếp hạng như BPR [36] hoặc EASE [37], các mô hình "
    "dựa trên đồ thị như LightGCN [38], và khai thác quan hệ bạn bè có sẵn trong dữ liệu. Về mô-đun M1, có "
    "thể áp dụng trên mô hình nền ALS và chấm trên một lần chia mới, dùng biểu diễn độc lập với chỉ số đánh "
    "giá cho phần đa dạng (thẻ, thể loại, đặc trưng âm thanh), và cá nhân hóa mức phạt phổ biến theo từng "
    "người dùng như Abdollahpouri và cộng sự [19]. Về M2, có thể bổ sung siêu dữ liệu nghệ sĩ từ nguồn bên "
    "ngoài để tăng độ phủ nội dung, và cho phép người dùng mới chọn thể loại yêu thích ở bước đầu. Về đánh "
    "giá, có thể lặp lại thực nghiệm trên nhiều lần chia để ước lượng bất định và khảo sát người dùng về độ "
    "mới, độ đa dạng. Về hệ thống, có thể triển khai lên môi trường đám mây, bổ sung thời gian chờ, bộ nhớ "
    "đệm và kiểm thử tải."
)

REFS = [
    "[31] Virtanen, P., Gommers, R., Oliphant, T. E., et al. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. Nature Methods, 17(3), 261–272. https://doi.org/10.1038/s41592-019-0686-2",
    "[32] Ramírez, S. FastAPI. Tài liệu chính thức. https://fastapi.tiangolo.com (Truy cập ngày 07/11/2026).",
    "[33] Vercel. Next.js Documentation. https://nextjs.org/docs (Truy cập ngày 07/11/2026).",
    "[34] Snowflake Inc. Streamlit Documentation. https://docs.streamlit.io (Truy cập ngày 07/11/2026).",
    "[35] Schedl, M., Brandl, S., Lesota, O., Parada-Cabaleiro, E., Penz, D., & Rekabsaz, N. (2022). LFM-2b: A dataset of enriched music listening events for recommender systems research and fairness analysis. In Proceedings of CHIIR '22, 337–341. https://doi.org/10.1145/3498366.3505791",
    "[36] Rendle, S., Freudenthaler, C., Gantner, Z., & Schmidt-Thieme, L. (2009). BPR: Bayesian personalized ranking from implicit feedback. In Proceedings of the 25th Conference on Uncertainty in Artificial Intelligence (UAI 2009), 452–461.",
    "[37] Steck, H. (2019). Embarrassingly shallow autoencoders for sparse data. In Proceedings of The World Wide Web Conference (WWW '19), 3251–3257. https://doi.org/10.1145/3308558.3313710",
    "[38] He, X., Deng, K., Wang, X., Li, Y., Zhang, Y., & Wang, M. (2020). LightGCN: Simplifying and powering graph convolution network for recommendation. In Proceedings of SIGIR '20, 639–648. https://doi.org/10.1145/3397271.3401063",
]
