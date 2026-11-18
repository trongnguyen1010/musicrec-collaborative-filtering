# Lộ trình hoàn thiện khóa luận MusicRec (Giai đoạn 1: rà soát)

Ngày lập: 26/10/2026. Phạm vi: chỉ rà soát tài liệu và mã nguồn, **không sửa code, không chạy thực nghiệm mới**. Mốc mã được rà soát: nhánh `research/data-preparation-model-survey`, commit `2615c35`.

Tài liệu này dừng ở trạng thái chờ duyệt. Các chỗ mâu thuẫn hoặc chưa rõ được gom thành câu hỏi ở mục 6; nhóm chưa tự chọn phương án nào.

Quy ước về số liệu trong tài liệu này: mọi con số mô hình được trích từ `docs/data-card.md` và `docs/WEEKLY_IMPLEMENTATION_PLAN.md` tại commit `2615c35`, kèm tên run gốc. **Các thư mục run (`outputs/runs/...`) và dữ liệu HetRec không có trong `C:\Projects\KLTN`** (đã tìm toàn bộ thư mục này), nên chưa đối chiếu lại được số liệu với tệp run. Các con số vì vậy là "số đã ghi trong tài liệu làm việc", chưa phải số đã kiểm tra lại.

---

## 1. Danh mục phiên bản báo cáo, đề cương và tài liệu

### 1.1 Báo cáo khóa luận (Word)

| Tệp | Vị trí | Cấu trúc | Ghi chú |
| --- | --- | --- | --- |
| `BaoCao_KLTN_..._V1.docx` | `docs/reports/` và `File/` | Cấu trúc cũ | Hai tệp trùng mã băm; nội dung văn bản trùng hoàn toàn bản 04-10. |
| `33_..._04-10-2026.docx` | `docs/reports/` | Cấu trúc cũ: Ch2 có 13 mục (2.1–2.13), Ch4–Ch5 viết đầy đủ dạng dự kiến | Bản V1 đổi tên. |
| `33_..._19-10-2026.docx` | `docs/reports/` | Cấu trúc cũ | Thêm kết quả EDA 19/10 vào Ch4. |
| `33_..._20-10-2026.docx` | `docs/reports/` | Cấu trúc cũ | **Bản cuối cùng còn nội dung Ch4–Ch5 dạng "bản viết trước"** (thiết kế E0–E6, lưới siêu tham số, bảng trống, kiểm định, API, kiểm thử T01–T09). |
| `V12/33_..._20-10-2026.docx` | `docs/reports/V12/` | **Cấu trúc mới**: Ch2 còn 2 mục (2.1 lọc cộng tác, 2.2 thước đo); Ch4–Ch5 chỉ còn tiêu đề | Bản thứ hai trong ngày 20/10. |
| `33_..._21-10-2026.docx`, `V13/..._21-10-2026.docx` | `docs/reports/` | Cấu trúc mới | Bổ sung kết quả làm sạch (Bước 3). |
| `33_..._24-10-2026.docx`, `V14/..._24-10-2026.docx` | `docs/reports/` | Cấu trúc mới | Bổ sung chia tập, biểu diễn (Bước 4–5). V14 dài hơn bản gốc cùng ngày. |
| `33_..._25-10-2026.docx` | `docs/reports/` | Cấu trúc mới | **Bản mới nhất.** Ch1–Ch3 có nội dung; Ch3 đã có số liệu thật đến Bước 6; Ch4–Ch5 chỉ có tiêu đề; Phụ lục A–C có nội dung. |

Kết luận về bản mới nhất theo từng phần:

| Phần | Bản nên dùng làm gốc | Lý do |
| --- | --- | --- |
| Ch1, Ch2 | 25-10 | Mới nhất; khác V14 chủ yếu ở mã mục lục và một đoạn về độ tương đồng nghệ sĩ (2.1). |
| Ch3 | 25-10 | Có số liệu thật Bước 1–6 khớp với data card (74.275/9.263/9.263 cặp, 15.398 nghệ sĩ train, bốn ngưỡng phân vị). |
| Ch4, Ch5 (khung nội dung) | Tiêu đề lấy từ 25-10; **nội dung dự kiến lấy từ 20-10 (bản gốc trong ngày)** | Từ V12 trở đi Ch4–Ch5 chỉ còn tiêu đề. Nội dung 20-10 là thiết kế, không phải kết quả. |
| Phụ lục A–C | 25-10 | Phụ lục B có ví dụ tính tay đã khớp kiểm thử. |

### 1.2 Đề cương

| Tệp | Ngày sửa | Ghi chú |
| --- | --- | --- |
| `File/DeCuongChiTiet_..._LeKhacGiaKhang.docx` | 18/08 | Đề cương gốc. Dùng leave-one-out hoặc time-aware split; RQ4 gắn với E5. |
| `File/..._BanMoi.docx` | 04/10 10:09 | Bản sửa giữa. |
| `File/..._V2.docx` | 04/10 10:11 | **Đề cương mới nhất.** Ba mô hình nền UserCF, ItemCF, SVD + hai mốc Random/Popularity; RQ3: "M1 so với mô hình **SVD** nền". |
| `docs/DeCuongChiTiet_..._ThamKhao.docx` (và bản trong `File/`) | 02/10 | Đề cương tham khảo của đề tài khác cùng chủ đề, không phải của nhóm. |
| `File/MoTaDeTai_KhuyenNghiAmNhac_KLTN.docx` | 18/08 | Mô tả đề tài ban đầu. |

### 1.3 Kế hoạch và tài liệu làm việc trong repo

| Tệp | Vai trò | Tình trạng |
| --- | --- | --- |
| `docs/WEEKLY_IMPLEMENTATION_PLAN.md` | Kế hoạch hiện hành 17 bước, lịch 19/10–30/11 | Cập nhật đến Bước 16 (26/10). Là nguồn mô tả chi tiết nhất các quyết định đã được duyệt trong chat. |
| `docs/data-card.md` | Nhật ký bằng chứng từng bước, bảng số liệu validation | Cập nhật đến Bước 16. Tham chiếu tới run trong `outputs/runs/`. |
| `docs/PROGRESS_TRACKING_GUIDE.md`, `DEVELOPMENT_RULES.md`, `PROJECT_STRUCTURE.md`, `README.md`, `CHANGELOG.md` | Quy tắc, cấu trúc, lệnh chạy lại từng bước | README có lệnh chạy lại Bước 2–16 (đường dẫn Windows `.venv/Scripts/python.exe`). |
| `docs/PROJECT_REVIEW.md` | Đánh giá bộ khung cũ (trước Bước 1) | **Lỗi thời**: mô tả trạng thái scaffold trước khi có pipeline. |
| `docs/TONG_QUAN_TAI_LIEU_THAM_KHAO.md`, `docs/SEMINAR_CHUONG_1_2.md` | Tổng quan tài liệu, ôn tập Ch1–Ch2 | Có mục đối chiếu ALS, M1, M2 (26/10). |
| `docs/Hướng dẫn từng bước hoàn thành khóa luận.docx` | Hướng dẫn của GVHD | Bản trong `File/` khác bản trong `docs/` ở phần cuối; cần xác nhận bản nào là bản cô gửi. |
| `docs/Các công thức độ đo...docx`, `docs/Độ đo RMSE...docx`, `docs/Lý Thuyết...docx`, `docs/Khao sat TQ.docx` | Tài liệu lý thuyết tham khảo | Không ảnh hưởng tới lộ trình. |

### 1.4 Những chỗ các phiên bản mâu thuẫn nhau

| Mã | Chỗ mâu thuẫn | Các phiên bản liên quan |
| --- | --- | --- |
| M-1 | **Số mô hình nền.** Đề cương V2: ba mô hình (UserCF, ItemCF, SVD). Báo cáo 25-10 mục 1.3.2: bốn mô hình (thêm PureSVD). Code: sáu mô hình nền + **implicit ALS**. ALS không xuất hiện ở mục tiêu, Ch2 hay Ch3 của bản nào. | Đề cương V2, báo cáo 25-10, code |
| M-2 | **Mô hình nền của M1.** Đề cương V2 và hướng dẫn GVHD: M1 chạy trên SVD. Data card Bước 14: chọn PureSVD nhị phân. Sau đó đổi sang ALS (Bước 15 chạy trên ALS). | Đề cương V2, hướng dẫn GVHD, data card |
| M-3 | **Mục 1.6 "Cấu trúc báo cáo"** (25-10) vẫn mô tả Ch2 gồm dữ liệu thưa, khởi động nguội, thiên lệch phổ biến, nghiên cứu liên quan; Ch2 thực tế (từ V12) chỉ còn 2.1 và 2.2. Mục 1.7 đứng trước 1.6. Ch4 được mô tả có "kết quả khám phá dữ liệu gốc" nhưng EDA đã chuyển sang 3.4.3. | Báo cáo V12–25-10 |
| M-4 | **Biểu diễn đầu vào PureSVD.** Báo cáo 3.6.4: PureSVD dùng cùng ma trận điểm đại diện R. Code Bước 13 so ba biểu diễn; bản nhị phân có NDCG@10 cao nhất và được dùng làm ứng viên M1 ở Bước 14. | Báo cáo 25-10, data card |
| M-5 | **Giao thức M2.** Báo cáo 25-10 (3.8.4, 3.10.2) chỉ nêu "N = 0, 1, 3, 5 trên cùng nhóm có ít nhất 5 tương tác hồ sơ". Báo cáo 20-10 (4.5.4) và kế hoạch hiện hành có thêm chia **người dùng** 80/10/10. Code chia 1.501/187/189 user, catalog M2 có 13.210 nghệ sĩ (khác 15.398 của bảng chính), nên số M2 không so trực tiếp được với bảng warm-start. | Báo cáo 25-10, báo cáo 20-10, kế hoạch, code |
| M-6 | **Thành phần cộng tác trong M2.** Báo cáo 3.8.3 nêu PureSVD/UserCF/ItemCF/SVD có thể cung cấp điểm cộng tác. Kế hoạch và code chỉ dùng ItemCF (L=40). | Báo cáo 25-10, code |
| M-7 | **Fallback khi CF không có láng giềng.** Báo cáo 3.6.3: chuyển sang M2. Code warm-start: UserCF/ItemCF dùng trung bình người dùng hoặc trung bình chung, không gọi M2. | Báo cáo 25-10, code |
| M-8 | **Chi tiết M1.** Báo cáo 3.7: độ tương đồng "nếu dùng thẻ...", phổ biến min–max "có thể log". Code đã chốt côsin nhị phân trên train và p = ln(1+listeners)/ln(1+max). Không mâu thuẫn về ý, nhưng báo cáo chưa ghi lựa chọn cuối. | Báo cáo 25-10, config M1 |
| M-9 | **Ngân sách tinh chỉnh.** Hướng dẫn GVHD: random search 20–30 cấu hình. Báo cáo 20-10 (4.4.1) và kế hoạch: tối đa 12 cấu hình cho UserCF/ItemCF/SVD, 4 số chiều PureSVD, 8 cấu hình ALS. **Thực tế chưa mô hình nào được tinh chỉnh**; mọi kết quả là cấu hình đầu. | Hướng dẫn GVHD, báo cáo 20-10, kế hoạch, data card |
| M-10 | **Phép chia.** Đề cương gốc nêu leave-one-out/time-aware; đề cương V2 và báo cáo 25-10: chia ngẫu nhiên theo người dùng xấp xỉ 80/10/10, ít nhất 5 nghệ sĩ. Code theo báo cáo 25-10. Đây là mâu thuẫn đã được giải quyết, chỉ cần thống nhất lời văn. | Đề cương gốc, V2, báo cáo |
| M-11 | **Mã thực nghiệm.** Đề cương gốc: RQ4 ↔ E5. Báo cáo V1 trở đi: E5 = nhóm lịch sử, E6 = M2. | Đề cương gốc, báo cáo |

---

## 2. Đối chiếu kế hoạch trong báo cáo với code hiện có

Nguồn kế hoạch: báo cáo 25-10 (Ch3, Phụ lục C) và bản viết trước Ch4–Ch5 (20-10). Nguồn trạng thái: code tại `2615c35`, data card và kế hoạch hiện hành.

### 2.1 Kiểm tra chất lượng mã (đã chạy trong lần rà soát này)

Chạy trên môi trường sạch Python 3.11 trong container, cài `.[dev,als]` đúng như CI:

| Lệnh | Kết quả |
| --- | --- |
| `ruff check .` | Đạt. |
| `ruff format --check .` | Đạt (83 tệp). |
| `mypy src` | **Không đạt: 13 lỗi ở 11 tệp**, do thiếu `pandas-stubs`, `scipy-stubs` và `streamlit` trong khai báo phụ thuộc. Khi cài thêm ba gói này thì đạt (31 tệp nguồn). |
| `python -m pytest` | Đạt toàn bộ (91 test, không lỗi). Lưu ý: chạy `pytest` trực tiếp báo lỗi import `scripts`, phải dùng `python -m pytest`. |

CI (`.github/workflows/ci.yml`) chỉ chạy khi có pull request hoặc push vào `main`, nên các lần push lên nhánh research không được kiểm tra.

Thư mục local `C:\Projects\KLTN\SourceCode` có 88 tệp hiện "modified", nhưng `git diff --ignore-cr-at-eol` trống: **chỉ khác ký tự xuống dòng (CRLF/LF)**, không có thay đổi nội dung.

### 2.2 Bảng đối chiếu từng bước

| Hạng mục kế hoạch | Mục báo cáo | Trạng thái | Bằng chứng / ghi chú |
| --- | --- | --- | --- |
| Kiểm tra nguồn, EDA | 3.4 | **Xong** | `scripts/eda.py`; run `raw_eda_20261019_verified`, `source_audit_...`. Số liệu đã vào báo cáo 25-10. |
| Làm sạch | 3.5.1 | **Xong** | `data/cleaning.py`, run `cleaning_20261021`. |
| Chia tập + ánh xạ | 3.5.2 | **Xong** | `data/splitting.py`, run `split_20261024`. |
| Bốn biểu diễn | 3.5.3 | **Xong** | `data/representations.py`, run `representations_20261024`. |
| Bộ đánh giá + ví dụ tính tay | 3.10, Phụ lục B | **Xong** | `evaluation/ranking.py`, `validation.py`; run `evaluator_20261025`. |
| E0 Random, Popularity (validation) | 3.6.1–3.6.2 | **Xong trên validation** | Bước 7–8. |
| E1 UserCF, E2 ItemCF (validation) | 3.6.3 | **Một phần**: chỉ cấu hình đầu L=40, shrinkage=0 | Chưa chạy lưới 12 cấu hình. NDCG@10 (seed 42) UserCF 0,0080787555, ItemCF 0,0074299548, thấp hơn Popularity 0,0623622664 khoảng 8 lần. |
| E3 SVD có độ lệch, PureSVD (validation) | 3.6.4 | **Một phần**: SVD một cấu hình, PureSVD k=32, ba biểu diễn | SVD dừng ở epoch 6, chọn epoch 1; NDCG@10 trung bình 3 seed 0,0576259192, **thấp hơn Popularity**. PureSVD nhị phân 0,1564272628. Chưa thử k = 16/64/128. |
| Implicit ALS | **Không có trong báo cáo** | **Làm ngoài kế hoạch báo cáo** (đã được duyệt trong chat ngày 26/10) | `recommenders/implicit_als.py`; 3 seed, NDCG@10 0,1965852193 ± 0,0014783714. |
| E4 M1 + ablation | 3.7 | **Xong trên validation**, nền ALS | Run `m1_als_validation_20261026`; chọn λ=0,75, β=0,5; NDCG@10 giảm 4,3317%, ARP giảm 24,7101%. |
| E5 nhóm lịch sử | 3.10.2 | **Một phần** | Đã tính trên validation (nhóm <40/=40/>40 có 41/1.822/2 user hợp lệ). Hai nhóm quá nhỏ để kết luận; chưa làm trên test. |
| E6 M2 tại N = 0, 1, 3, 5 | 3.8 | **Xong trên validation**, giao thức chia user riêng | Run `m2_cold_user_validation_20261026`; chọn α=0,75, ngưỡng 10; 189 user để dành chưa dùng. |
| RMSE | 1.3.2, 2.2.4 | **Một phần** | Chỉ có RMSE proxy bổ sung cho UserCF/ItemCF/SVD trong run; chưa có bảng tổng hợp. |
| Tinh chỉnh siêu tham số | 4.4 (bản 20-10) | **Chưa làm** | Mọi mô hình mới chạy cấu hình đầu. |
| Khóa cấu hình, đánh giá test (Bước 17) | 4.7, 4.8 | **Chưa làm** | Test chưa mở lần nào (có guard chặn đọc `test.parquet`). |
| Kiểm định thống kê (bootstrap, Wilcoxon, Holm) | 4.6 | **Chưa làm** | |
| Phân tích lỗi có hệ thống | 4.9 | **Chưa làm** | |
| Xuất gói mô hình, manifest | 5.1.2, Phụ lục A.3 | **Chưa làm** | `artifacts/manifest.py` mới là khung. |
| API FastAPI | 5.2 | **Chưa làm (scaffold)** | `api/main.py` vẫn dùng Popularity trên hai mục giả `seed_item_a/b`; `fallback_used` luôn false. |
| Giao diện Streamlit | 5.3 | **Chưa làm (scaffold)** | Hiển thị JSON. |
| Kiểm thử hệ thống T01–T09, đối chiếu online/offline, đo thời gian | 5.4 | **Chưa làm** | |

### 2.3 Chỗ code đã đi khác kế hoạch báo cáo

1. **Thêm implicit ALS** (không có trong mục tiêu 1.3.2, Ch2, Ch3) và **đổi nền M1 từ SVD sang ALS**.
2. **M2 đánh giá trên phép chia người dùng riêng** (1.501 học / 187 tinh chỉnh / 189 để dành), catalog 13.210 nghệ sĩ, chỉ dùng ItemCF làm thành phần cộng tác. Bản 25-10 chưa ghi phép chia này.
3. **PureSVD nhị phân** thay cho PureSVD trên điểm đại diện như báo cáo mô tả.
4. **Không có mô hình nào được tinh chỉnh**; ba mô hình UserCF, ItemCF, SVD đều thấp hơn Popularity ở cấu hình đầu. Hướng dẫn GVHD lưu ý trường hợp này thường cần kiểm tra lại tiền xử lý hoặc cấu hình trước khi kết luận.
5. Fallback của CF trong giao thức chính là trung bình người dùng/trung bình chung, không phải M2.

---

## 3. Những việc cần làm trước khi sang Chương 3 (dọn nền)

Các việc này nhỏ, mỗi việc một nhánh và một PR riêng tách từ `research/data-preparation-model-survey`, chỉ làm khi được duyệt.

| Mã | Việc | Lý do | Cần hỏi trước? |
| --- | --- | --- | --- |
| D-1 | Xác định vị trí dữ liệu HetRec và `outputs/runs/` trên máy, hoặc chép vào `C:\Projects\KLTN\SourceCode\data\raw` và `outputs\runs` | Không có dữ liệu thì không đối chiếu hay chạy lại được gì. Máy ảo và container đều bị chặn tải từ grouplens.org. | Có (câu hỏi Q1, Q2) |
| D-2 | Thêm `pandas-stubs`, `scipy-stubs`, `streamlit` vào nhóm `dev`; cho CI chạy cả nhánh research | mypy đang lỗi trên môi trường sạch | Không đổi phương pháp; vẫn sẽ làm PR riêng để duyệt |
| D-3 | Thêm `.gitattributes` chuẩn hóa xuống dòng | 88 tệp hiện "modified" chỉ vì CRLF | Có (đụng nhiều tệp) |
| D-4 | Xử lý ~70 MB tệp Word/PDF trong Git (`docs/reports` 54 MB, `docs/TLTK` 17 MB, `Tai_lieu_...` 17 MB) | Repo nặng | **Có** (xóa/di chuyển tệp) |
| D-5 | Đánh dấu `docs/PROJECT_REVIEW.md` là lỗi thời | Tránh đọc nhầm | Có |

---

## 4. Lộ trình theo chương (Chương 3 trở đi)

Quy ước chung cho mọi chương (theo quy tắc dự án):

- Mỗi việc một nhánh tách từ `research/data-preparation-model-survey`, PR riêng có mô tả.
- Kết quả tái lập lưu theo chương: đề xuất `outputs/chuong_X/<run_id>/` gồm config, seed, Git SHA, hash dữ liệu/split, log, metrics CSV/JSON, hình (cấu trúc thư mục cần duyệt, câu hỏi Q11).
- Viết `docs/results/chuong_X.md`: đã làm gì, bảng số liệu thật kèm nguồn, so sánh với bản viết trước, những điểm cần sửa trong báo cáo.
- Chạy ruff, mypy, pytest trước khi báo xong. Thử trên mẫu nhỏ trước, báo ước tính thời gian trước khi chạy đầy đủ.
- **Dừng sau mỗi chương** chờ duyệt; chỉ viết lại chương trong báo cáo sau khi được duyệt.

Ước tính thời gian dưới đây suy từ thời gian đã ghi trong data card cho các run trên máy của nhóm. Đây là ước tính để lập lịch, không phải kết quả, và sẽ được đo lại trên mẫu nhỏ trước khi chạy.

### Chương 3: Phân tích bài toán và phương pháp đề xuất

Hiện trạng: phần dữ liệu (3.4–3.5) và bộ đánh giá (3.10) đã có số liệu thật trong bản 25-10. Còn thiếu phần mô tả đúng những gì code đã làm ở 3.6–3.8.

| Thứ tự | Việc | Thực nghiệm | Đầu ra |
| --- | --- | --- | --- |
| 3.1 | Chạy lại Bước 1–6 từ dữ liệu gốc vào `outputs/chuong_3/` và so mã băm với run cũ | EDA, làm sạch, chia tập, biểu diễn, kiểm tra evaluator (mỗi bước vài giây đến vài phút) | Bảng: thống kê dữ liệu gốc/sau lọc, kết quả chia tập, đích ngoài catalog, bốn ngưỡng phân vị, phân bố mức 1–5. Hình: phân bố lượt nghe (log), độ tập trung nghệ sĩ, độ phủ thẻ. Báo cáo khớp/không khớp mã băm. |
| 3.2 | Đối chiếu từng con số trong Ch3 bản 25-10 với kết quả chạy lại | Không chạy thêm | Danh sách số đúng/sai kèm nguồn. |
| 3.3 | Tài liệu hóa thiết kế thực tế của 3.6–3.8 (theo quyết định ở câu hỏi Q3–Q7) | Không chạy thêm | Bảng tham số cuối của từng mô hình (gồm ALS nếu giữ), công thức M1 đã chốt, giao thức M2 (chia user, catalog 13.210, TF–IDF min_df=2). |
| 3.4 | Viết `docs/results/chuong_3.md` | | Đề xuất sửa: mục 1.6/1.7, 3.6.3 (fallback), 3.6.4 (biểu diễn PureSVD), 3.7 (similarity/popularity đã chốt), 3.8 (ItemCF, chia user), thêm mô tả ALS nếu giữ. |

### Chương 4: Huấn luyện và thực nghiệm đánh giá

Đây là chương nặng nhất. Thứ tự đề xuất giữ nguyên quy tắc "chọn trên validation, mở test đúng một lần".

| Thứ tự | Việc | Thực nghiệm | Ước tính thời gian | Đầu ra |
| --- | --- | --- | --- | --- |
| 4.1 | Tái lập kết quả validation đã có (Bước 7–16) vào `outputs/chuong_4/` hoặc đối chiếu hash run cũ nếu tìm thấy | E0–E3, ALS 3 seed, M1, M2 trên validation | Dưới 1 giờ nếu chạy lại tất cả: ALS 126–240 giây mỗi seed, SVD khoảng 54 giây mỗi seed, M1 khoảng 156 giây, M2 vài chục giây | Bảng validation đầy đủ K = 5/10/20, đối chiếu với data card. |
| 4.2 | **(Chờ quyết định Q6)** Tinh chỉnh theo ngân sách kế hoạch | UserCF 12, ItemCF 12, SVD 12, PureSVD 4 số chiều, ALS 8 cấu hình; xác nhận seed 43/44 cho cấu hình chọn | UserCF/ItemCF: vài phút mỗi lưới. SVD: khoảng 11 phút nếu dừng sớm như lần đầu, tối đa khoảng 2,5 giờ nếu chạy đủ 100 epoch. ALS: khoảng 17–32 phút. PureSVD: dưới 1 phút | Bảng lưới, cấu hình chọn theo NDCG@10 validation, đường học. |
| 4.3 | Chạy lại M1 nếu nền thay đổi sau tinh chỉnh | 12 tổ hợp λ/β + ablation 3 seed | Khoảng 3 phút | Bảng ablation, hình đường đánh đổi. |
| 4.4 | **Khóa cấu hình** (tệp khóa ghi mô hình, cấu hình, seed, quy tắc tổng hợp, các cặp kiểm định) | Không | | `configs/final_lock.yaml` (tên đề xuất). |
| 4.5 | **Đánh giá test một lần** | E0–E3 (+ALS), E4 M1, E5 nhóm lịch sử trên test; E6 M2 trên 189 user để dành | Dưới 1 giờ (không huấn luyện lại) | Bảng 4.6–4.11 theo khung bản 20-10: P/R/NDCG@5/10/20, Coverage, Gini, ARP, Novelty, ILD, RMSE proxy. |
| 4.6 | Kiểm định thống kê | Bootstrap 1.000 lần theo user, Wilcoxon cặp + Holm cho các cặp định trước | Vài phút | Bảng 4.13: chênh lệch, CI 95%, p sau Holm. |
| 4.7 | Chi phí | Gom thời gian fit/recommend/bộ nhớ/kích thước mô hình | Không chạy thêm | Bảng 4.12. |
| 4.8 | Phân tích lỗi | Chọn ca theo quy tắc: tăng lớn nhất, giảm lớn nhất, gần trung vị | Không chạy thêm | 4–6 ca phân tích, phân loại lỗi theo 4.9.1. |
| 4.9 | Viết `docs/results/chuong_4.md` | | | So sánh với bản viết trước (20-10), trả lời RQ1–RQ4 bằng số, ghi rõ giả thuyết không được ủng hộ (ví dụ ba mô hình thấp hơn Popularity nếu vẫn đúng sau tinh chỉnh). |

Hình dự kiến: NDCG@K theo mô hình, đường học ALS/SVD, đường đánh đổi M1 (NDCG–ARP), đường N của M2, NDCG theo nhóm lịch sử.

### Chương 5: Xây dựng hệ thống và kết luận

Chỉ bắt đầu sau khi Ch4 khóa được mô hình.

| Thứ tự | Việc | Kiểm tra | Đầu ra |
| --- | --- | --- | --- |
| 5.1 | Xuất gói mô hình đã chọn: tham số, ánh xạ, ngưỡng biến đổi, thống kê phổ biến, đặc trưng thẻ M2, manifest có hash | Nạp lại cho cùng danh sách trên tập hồ sơ cố định | Thư mục `artifacts/releases/<version>/`, báo cáo kiểm tra nạp lại. |
| 5.2 | API: `/health` tách trạng thái sẵn sàng, `/recommend` nạp gói thật, cờ `fallback_used` phản ánh M2, xử lý lịch sử rỗng, mã lạ, K sai | Contract test + T01–T09 | Nhật ký kiểm thử từng tình huống. |
| 5.3 | Giao diện Streamlit: nhập user hoặc lịch sử, chọn K, hiển thị tên nghệ sĩ, lý do, cờ dự phòng | Chạy thủ công 3 hồ sơ mẫu | Ảnh chụp giao diện thật. |
| 5.4 | Đối chiếu online/offline và đo thời gian | Cùng hồ sơ qua API và gọi trực tiếp; trung vị và p95 | Bảng đối chiếu, bảng thời gian (ghi rõ máy đo). |
| 5.5 | Kiểm tra môi trường sạch, README chạy lại | Cài mới từ đầu | README đã kiểm tra. |
| 5.6 | Viết `docs/results/chuong_5.md`: mức độ đạt mục tiêu, hạn chế, hướng phát triển | | Bảng mục tiêu ↔ bằng chứng (thay Bảng 5.5 bản 20-10). |

### Thứ tự tổng thể đề xuất

1. Trả lời câu hỏi mục 6, nhất là Q1–Q4 và Q6.
2. Dọn nền D-1, D-2 (và D-3, D-4 nếu được đồng ý).
3. Chương 3 → dừng duyệt.
4. Chương 4 (4.1 → 4.9) → dừng duyệt. Có thể cần một điểm dừng phụ trước 4.5 (mở test) vì bước này không làm lại được.
5. Chương 5 → dừng duyệt.
6. Viết lại báo cáo theo hình thức chọn ở Q9.

Đối chiếu lịch trong kế hoạch hiện hành: mốc chọn mô hình 15/11, demo nội bộ 27/11, nộp demo cuối tháng 11. Hạn nộp toàn bộ báo cáo chưa được xác nhận.

---

## 5. Rủi ro chính

- **Không có dữ liệu và run trên thư mục đã chia sẻ**: chặn mọi việc chạy lại và đối chiếu (Q1).
- **Ba mô hình CF cổ điển thấp hơn Popularity** ở cấu hình đầu. Nếu không tinh chỉnh, Ch4 phải giải thích kết quả này một cách trung thực; nếu tinh chỉnh, cần thêm thời gian ở bước 4.2.
- **ALS và M1 trên nền ALS chưa có trong Ch1–Ch3**: nếu giữ, phải sửa mục tiêu 1.3.2 và thêm lý thuyết vào Ch2, mà Ch2 được coi là đã viết xong.
- Mở test là bước một chiều; mọi thay đổi cấu hình sau đó phải ghi là nghiên cứu bổ sung.

---

## 6. Câu hỏi cần bạn quyết định

Nhóm chưa tự chọn phương án cho các câu hỏi dưới đây. Câu nào có đề xuất thì đề xuất chỉ để tham khảo.

**Dữ liệu và môi trường**

- **Q1.** Dữ liệu HetRec (`data/raw/hetrec2011`) và các run `outputs/runs/...` đang nằm ở đâu trên máy? Trong `C:\Projects\KLTN` không có. Bạn muốn chép vào `SourceCode`, hay cho phép truy cập thư mục khác?
- **Q2.** Chạy thực nghiệm ở đâu: (a) trên Windows của bạn qua phiên điều khiển từ xa, dùng `.venv` sẵn có; (b) trên máy chủ đám mây của Claude, sau khi chép dữ liệu lên (4 CPU, 15 GB RAM; không tự tải được từ grouplens.org); (c) bạn tự chạy theo lệnh mình chuẩn bị? Kết quả thời gian chạy sẽ khác nhau giữa các máy.

**Phương pháp (thay đổi so với báo cáo)**

- **Q3.** Implicit ALS: đưa vào báo cáo như một mô hình chính (phải sửa 1.3.2, thêm lý thuyết vào Ch2, thêm thiết kế vào Ch3), hay chỉ là thực nghiệm mở rộng (một mục riêng ở Ch4 hoặc phụ lục), hay bỏ?
- **Q4.** Mô hình nền của M1: ALS (như code hiện tại), PureSVD, hay SVD (như đề cương V2 và hướng dẫn của cô)?
- **Q5.** Giao thức M2 chia người dùng 1.501/187/189: chấp nhận và viết vào Ch3? Với 189 user để dành, đích đánh giá cuối là tập test hay tập validation của họ?
- **Q6.** Tinh chỉnh siêu tham số trước khi khóa: chạy đủ ngân sách kế hoạch (12/12/12/4/8), chỉ một phần (ví dụ chỉ UserCF/ItemCF/SVD vì đang thấp hơn Popularity), hay khóa cấu hình đầu hiện có?
- **Q7.** PureSVD trong bảng chính dùng biểu diễn nào: điểm đại diện (như báo cáo) hay nhị phân (tốt nhất trên validation)? Hai biểu diễn còn lại đưa vào bảng phụ?
- **Q12.** Các cặp kiểm định định trước: mô hình chọn – Popularity, SVD – PureSVD, M1 – nền, M2 – Popularity tại N=3, và (nếu giữ ALS) ALS – mô hình mạnh nhất trong sáu mô hình. Đồng ý danh sách này?
- **Q13.** RMSE chỉ báo cho UserCF, ItemCF, SVD (mô hình có điểm cùng thang 1–5) như bảng phụ, không dùng để chọn mô hình. Đồng ý?

**Báo cáo**

- **Q8.** Lấy bản 25-10 làm gốc để viết lại? Có sửa Ch1/Ch2 (mục 1.6/1.7, mô tả cấu trúc Ch2, thêm ALS) hay giữ nguyên vì đã nộp/được duyệt?
- **Q9.** Hình thức đầu ra cho mỗi chương: (a) chỉ `docs/results/chuong_X.md` làm tư liệu để bạn tự viết lại báo cáo; (b) thêm bản nháp nội dung chương theo văn phong báo cáo để bạn chỉnh; (c) mình xuất bản Word mới theo quy tắc đặt tên?
- **Q10.** Bản "Hướng dẫn từng bước" trong `File/` và trong `docs/` khác nhau ở phần cuối. Bản nào là bản cô gửi?

**Tổ chức repo**

- **Q11.** Lưu kết quả theo chương ở `outputs/chuong_3/`, `outputs/chuong_4/`, `outputs/chuong_5/` (mỗi thư mục chứa các run), thay cho `outputs/runs/` hiện tại? Run cũ giữ nguyên chỗ cũ.
- **Q14.** Cho phép làm D-2 (stubs cho mypy, CI chạy cả nhánh research), D-3 (`.gitattributes`), D-4 (đưa Word/PDF ra khỏi Git), D-5 (đánh dấu tài liệu lỗi thời)? Mỗi việc là một PR riêng.
- **Q15.** Mô hình nào đưa vào demo (Ch5) và có bật M1/M2 trong API không, hay để quyết định sau khi có kết quả test?
- **Q16.** Đã có hạn nộp toàn bộ báo cáo và ngày bảo vệ chưa? Lịch hiện tại chỉ có mốc demo cuối tháng 11.
