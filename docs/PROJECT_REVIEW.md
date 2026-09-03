# Đánh giá lại bộ khung MusicRec

Ngày đánh giá: 2026-09-03

## Kết luận

**Chấp thuận có điều kiện.** Hướng kiến trúc hiện tại phù hợp với đề tài hệ khuyến nghị
âm nhạc dựa trên Collaborative Filtering và phù hợp với quy mô khóa luận hai thành viên.
Không cần đổi sang microservice hoặc tách nhiều repository.

Tuy nhiên, repository mới đạt mức **bộ khung có định hướng tốt**, chưa đạt mức pipeline nghiên
cứu có thể tái lập. Trước khi phát triển đồng thời các mô hình, nhóm phải hoàn thành các việc P0
ở dưới. Các việc này đã được đưa vào Tuần 1-3 của `WEEKLY_IMPLEMENTATION_PLAN.md`.

Đánh giá tổng quát:

| Hạng mục | Mức hiện tại | Nhận xét |
| --- | ---: | --- |
| Phù hợp đề tài | 7/10 | Đúng bài toán CF, nhưng chưa khóa rõ implicit-feedback protocol và research question. |
| Phân ranh module | 8/10 | Offline/online, model interface, API/UI được tách hợp lý. |
| Tái lập thí nghiệm | 3/10 | Có khung DVC/MLflow nhưng config chưa điều khiển code, DVC chưa hoàn chỉnh, chưa có lock file. |
| Đánh giá mô hình | 3/10 | Mới có hai hàm metric và script placeholder; protocol chưa được hiện thực. |
| Serving/demo | 4/10 | API scaffold chạy theo baseline seed; chưa nạp release artifact và chưa xử lý cold-start thật. |
| Chất lượng/kiểm thử | 5/10 | 4 test pass; lint, format và mypy chưa pass. |
| Làm việc hai người | 6/10 | Có PR rule và CI; chưa có ownership, backlog chuẩn và dashboard tiến độ. |

## Điểm đang làm đúng

1. Modular monorepo là lựa chọn phù hợp. Với hai thành viên, một package `musicrec` giúp dùng
   chung data contract, evaluator và model interface mà không tạo chi phí vận hành phân tán.
2. Ranh giới offline pipeline và online serving đã được ghi rõ. Quy tắc API không train trong
   request và chỉ nạp release artifact là đúng.
3. `Recommender` tạo hợp đồng chung `fit/predict/recommend`; Popularity là baseline bắt buộc;
   API schema được tách khỏi domain object.
4. Đã có nền tảng tốt cho tái lập: config có version, seed, DVC DAG, dự kiến MLflow, release
   manifest và ADR.
5. Có quy tắc PR, Conventional Commits, test layout, pre-commit và GitHub Actions ngay từ đầu.
6. Notebook không được xem là nguồn chân lý; logic dùng lại nằm trong `src/`. Đây là ranh giới
   quan trọng đối với một project nghiên cứu có demo.

Hướng phân tầng này tương đồng với luồng Prepare Data → Model → Evaluate → Model Select →
Operationalize của dự án Recommenders thuộc LF AI & Data, nên không cần thay cấu trúc gốc chỉ để
trông giống một repository công khai khác.

## Vấn đề bắt buộc xử lý trước khi phát triển model

### P0.1 — Khóa bài toán nghiên cứu và protocol đánh giá

`README.md` mới nói “Collaborative Filtering” nhưng chưa nêu:

- đối tượng gợi ý là **artist** hay track;
- dữ liệu `listening_count` là implicit feedback, không phải rating tường minh;
- research question và giả thuyết cần kiểm chứng;
- nhóm baseline/model chính;
- quy tắc split, candidate set và metric chính để chọn model.

Với `user_artists.dat`, đối tượng hiện thực đang là **artist**. Đề xuất khóa phạm vi như sau:

- Bài toán: top-N artist recommendation từ implicit listening feedback.
- Baseline: Popularity.
- Memory-based CF: User-kNN và Item-kNN.
- Model-based CF: implicit ALS hoặc BPR; chỉ giữ tên “SVD” nếu báo cáo định nghĩa chính xác cách
  chuyển implicit signal, loss và negative/unobserved items.
- Metric chọn model: `NDCG@10` chính; `Recall@10`, `Precision@10`, `MAP@10` hỗ trợ.
- Beyond-accuracy: catalog coverage, novelty/average popularity, diversity và inference latency.

Không nên dùng RMSE làm metric chính cho dữ liệu này. Tài liệu RecBole phân tách rõ value-based
metrics như RMSE/MAE khỏi ranking metrics như Recall, Precision, NDCG, MAP và MRR; hai nhóm metric
không được trộn trong cùng một protocol. Repository `implicit` cũng cung cấp ALS, BPR và item-item
KNN chuyên cho implicit dataset, kể cả ví dụ Last.fm.

### P0.2 — Chốt dữ liệu, license và data contract

`configs/dataset.yaml` và `docs/data-card.md` còn `TODO`. GroupLens công bố bộ HetRec Last.fm 2K
gồm khoảng 92.800 bản ghi nghe artist của 1.892 người dùng và yêu cầu đọc README đi kèm để kiểm
tra điều kiện sử dụng.

Trước khi chạy pipeline phải ghi đủ:

- URL chính thức và ngày tải;
- SHA-256 của file zip và từng input dùng thực tế;
- nội dung license/attribution từ README của dataset;
- schema, số dòng, số user, số artist, duplicate/null/outlier;
- quyết định dùng `user_artists.dat`; tags/friend graph nằm ngoài phạm vi hay là phần mở rộng;
- định nghĩa `listening_count`, phép biến đổi log/confidence và ngưỡng lọc.

### P0.3 — Biến DVC/config thành nguồn chân lý thật

Hiện có `dvc.yaml` nhưng không có dấu vết repository DVC đã được khởi tạo (`.dvc/`), không có
`dvc.lock`, remote hoặc file DVC theo dõi raw data. `params.yaml` chỉ trỏ sang các config khác;
các stage không khai báo `params`, và phần lớn script đang hard-code seed, đường dẫn, model.

Do đó thay đổi YAML hiện **không đảm bảo thay đổi kết quả chạy**. Cần:

1. `dvc init`, cấu hình remote dùng chung và commit metadata phù hợp.
2. Tạo download/import stage hoặc quy trình `dvc add` có checksum rõ ràng.
3. Chọn một cơ chế config duy nhất; script nhận config qua CLI và không hard-code.
4. Khai báo đúng `params`/`deps` cho từng stage để DVC invalidation hoạt động.
5. Sinh và commit `dvc.lock`; kiểm tra fresh-clone reproduction.
6. Log Git SHA, data version, config hash, seed, params, metrics và artifact bằng MLflow.

DVC mô tả workflow chuẩn là `dvc init` → track data → khai báo `dvc.yaml` → `dvc repro` → dùng
remote để chia sẻ. MLflow run nên giữ code version, params, metrics và artifacts; với nhóm hai
người, tracking store dùng chung tốt hơn hai database SQLite độc lập.

### P0.4 — Làm CI xanh từ clean environment

Kết quả kiểm tra ngày 2026-09-03:

| Lệnh | Kết quả |
| --- | --- |
| `python -m pytest` | **Pass: 4 tests** |
| `python -m ruff check .` | **Fail: 8 lỗi** |
| `python -m ruff format --check .` | **Fail: 3 file** |
| `python -m mypy src` | **Fail: 2 lỗi ở `ui/app.py`** |

Các lỗi chính là format/line length, import `Iterable` cũ, thứ tự import, thiếu `streamlit` trong
môi trường mà CI cài bằng `.[dev]`, và kiểu `json` truyền cho `requests.post`. README yêu cầu `uv`
nhưng chưa có `uv.lock`; vì vậy môi trường chưa khóa được dependency chính xác.

Definition of Done đang yêu cầu toàn bộ bốn gate này pass, nên `main` hiện chưa thỏa chính quy tắc
của repository.

## Vấn đề ưu tiên tiếp theo

### P1 — Đánh giá và chống leakage

- `scripts/evaluate.py` mới ghi `not_evaluated`; chưa tạo recommendation cho toàn bộ user/candidate.
- `split_data.py` bỏ qua config, hard-code seed và không sinh thống kê user bị loại.
- Dataset không có timestamp cho `user_artists.dat`, nên phải gọi đúng là **random leave-one-out
  per user**, không mô tả nhầm thành temporal split.
- Phải thống nhất full ranking trên toàn bộ unseen catalog hoặc negative sampling cố định. Không
  được so hai model bằng candidate set khác nhau.
- `precision_at_k` hiện chia cho độ dài list trả về. Theo định nghĩa Precision@K phổ biến mà
  Recommenders/Spark dùng, mẫu số là K; nếu trả ít hơn K kết quả thì điểm tối đa có thể nhỏ hơn 1.
- Cần test duplicate recommendation, empty truth, unknown user/item, k lớn hơn catalog, tie order,
  determinism và no-seen-item leakage.

### P1 — API, cold-start và artifact contract

- `docs/api.md` mô tả `/users/{id}/history` và `/metrics` nhưng code chưa có.
- History tạm thời chỉ được dùng để loại item đã nghe; chưa cá nhân hóa recommendation.
- `fallback_used` luôn `False`, kể cả unknown user.
- API đang fit dữ liệu seed khi import module; chưa nạp release artifact.
- `ReleaseManifest` thiếu `config_hash`, metrics, thời điểm tạo và artifact checksums dù
  `PROJECT_STRUCTURE.md` tuyên bố các trường này bắt buộc.
- Cần startup validation: artifact/schema/version không hợp lệ thì service fail-fast; health phải
  phản ánh trạng thái model thật.

### P1 — Test và reproducibility coverage

- Thư mục integration/fixtures có nhưng chưa có test.
- Chưa test các script pipeline bằng tiny fixture end-to-end.
- Chưa có API test bằng `TestClient`, serialization test hoặc release compatibility test.
- Chưa có coverage threshold và chưa xác minh fresh clone trên Windows lẫn CI Linux.

### P2 — Hoàn thiện sản phẩm và tài liệu

- UI cần hiển thị tên artist/metadata, lý do gợi ý, trạng thái fallback và lỗi API thân thiện.
- Cân nhắc Docker chỉ khi cần demo nhất quán; không cần Kubernetes/microservice cho phạm vi này.
- Bổ sung `LICENSE`, model card, experiment report template, demo runbook và sơ đồ kiến trúc.
- Có thể thêm tags/friend relations thành ablation hoặc future work; không đưa vào critical path
  nếu đề tài chỉ yêu cầu Collaborative Filtering từ interaction matrix.

## Đối chiếu với dự án/tài liệu công khai

| Tiêu chí | Tham chiếu công khai | MusicRec hiện tại | Hành động |
| --- | --- | --- | --- |
| Lifecycle | LF AI Recommenders bao phủ prepare/model/evaluate/select/operationalize | Có đúng các lớp chính | Giữ kiến trúc |
| Implicit CF | `implicit` có ALS, BPR, Logistic MF, item-item KNN và ví dụ Last.fm | Dự kiến User/Item-CF và SVD | Thêm ALS/BPR hoặc định nghĩa SVD implicit rõ ràng |
| Evaluation | RecBole chuẩn hóa split, candidate mode và ranking metrics | Split/evaluator còn hard-code/placeholder | Khóa protocol trước model |
| Reproducibility | DVC theo dõi data, pipeline, params; MLflow theo dõi run | Mới là khai báo | Hoàn thiện trong 2 tuần đầu |
| Team workflow | GitHub Projects hỗ trợ iteration, custom fields, board/roadmap/charts | Chỉ có PR template và CI | Dùng Project làm nguồn tiến độ duy nhất |

## Quyết định kiến trúc đề xuất

1. **Giữ modular monorepo hiện tại.**
2. **Không bắt đầu bằng deep learning.** Hoàn thiện baseline, kNN và implicit MF có evaluator chung.
3. **Chọn top-N implicit ranking là protocol chính.** RMSE chỉ tồn tại nếu có một nhánh rating
   prediction được định nghĩa độc lập và có lý do học thuật.
4. **DVC quản lý data/pipeline; MLflow quản lý experiment run; GitHub quản lý công việc/PR.** Ba
   công cụ có trách nhiệm khác nhau, không ghi tiến độ con người vào MLflow.
5. **Mỗi PR nhỏ, một owner code và một reviewer chéo.** Không để hai người sửa cùng một module
   trong cùng tuần nếu chưa thống nhất interface trước.

## Nguồn tham chiếu

- [GroupLens — HetRec 2011](https://grouplens.org/datasets/hetrec-2011/)
- [LF AI & Data Recommenders — project lifecycle](https://recommenders-team.github.io/recommenders/intro.html)
- [Recommenders — evaluation module](https://recommenders-team.github.io/recommenders/evaluation.html)
- [RecBole — training and evaluation settings](https://recbole.io/docs/v1.0.0/user_guide/train_eval_intro.html)
- [`implicit` — Collaborative Filtering for implicit datasets](https://github.com/benfred/implicit)
- [DVC — command workflow](https://dvc.org/doc/command-reference/)
- [DVC — pipeline parameterization](https://dvc.org/blog/dvc-2-0-release/)
- [MLflow — experiment tracking](https://mlflow.org/docs/latest/ml/tracking/)
- [GitHub Projects — quickstart](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/quickstart-for-projects)
- [GitHub — required status checks](https://docs.github.com/en/pull-requests/reference/status-checks)
