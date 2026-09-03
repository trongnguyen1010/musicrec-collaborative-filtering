# Kế hoạch triển khai MusicRec cho hai thành viên

## Phạm vi và giả định

- Thời lượng mặc định: **12 tuần**, từ 2026-09-07 đến 2026-11-29.
- Thành viên A: **Cao Trọng Nguyên** — owner chính của data, evaluation và experiment analysis.
- Thành viên B: **Lê Khắc Gia Khang** — owner chính của recommender, serving/API và demo.
- Ownership mặc định không có nghĩa mỗi người chỉ biết một nửa; mọi PR do người còn lại review.
- Nếu lịch chính thức khác, giữ thứ tự dependency và dịch toàn bộ mốc tuần.
- Đối tượng gợi ý mặc định: **artist**; bài toán chính: **top-N từ implicit feedback**.

## Các milestone

| Milestone | Hạn | Điều kiện đạt |
| --- | --- | --- |
| M0 — Foundation green | Cuối Tuần 1 | Clean install; lint/format/mypy/test xanh; scope được duyệt. |
| M1 — Reproducible data/eval | Cuối Tuần 3 | DVC tái chạy; split và evaluator chung được khóa bằng test. |
| M2 — Classical CF complete | Cuối Tuần 5 | Popularity, User-kNN, Item-kNN chạy cùng protocol. |
| M3 — Model selection | Cuối Tuần 8 | Implicit MF, tuning, reranking; chọn model chỉ từ validation. |
| M4 — Demo release | Cuối Tuần 10 | Artifact nạp vào API/UI; integration và smoke test pass. |
| M5 — Thesis evidence frozen | Cuối Tuần 12 | Chạy test cuối; bằng chứng truy vết được; demo/runbook hoàn chỉnh. |

## Quy tắc tránh xung đột

### Ownership theo vùng

| Vùng | Owner viết chính | Reviewer |
| --- | --- | --- |
| `src/musicrec/data/`, `evaluation/`, data scripts/docs | A | B |
| `src/musicrec/recommenders/`, model configs | B | A |
| `src/musicrec/api/`, `serving/`, `ui/` | B | A |
| `artifacts/`, DVC/MLflow, CI/release docs | A | B |
| Interface chung, `pyproject.toml`, `params.yaml`, `dvc.yaml`, API schema | Owner issue | Người còn lại + ADR nếu đổi contract |

### Luồng Git bắt buộc

1. Mỗi task có GitHub Issue với owner, tuần, estimate, acceptance criteria và dependency.
2. Một branch/issue: `feat/<issue>-<name>`, `fix/...`, `docs/...`, `research/...`.
3. Tránh PR vượt khoảng 400 dòng logic nếu có thể tách; generated file không tính.
4. Cập nhật branch từ `main` trước khi chuyển PR sang Ready for review.
5. Chỉ một người sửa shared contract tại một thời điểm; merge contract trước consumer.
6. PR ghi `Closes #...`, test evidence và screenshot/bảng metric khi phù hợp.
7. Không merge khi CI đỏ, chưa approve hoặc acceptance criteria chưa đạt.
8. Không đánh giá năng suất bằng số commit, số dòng code hay số giờ online.

## Definition of Ready

Task chỉ vào tuần hiện tại khi có: mục tiêu gắn milestone/research question; một owner; reviewer;
input/dependency sẵn sàng; đầu ra cụ thể; acceptance criteria kiểm tra được; estimate theo dãy
1, 2, 3, 5, 8. Task 8 điểm phải cân nhắc tách nhỏ.

## Definition of Done

Task chỉ Done khi:

- PR đã merge vào `main`;
- test mới/regression test phù hợp pass;
- `ruff check`, `ruff format --check`, `mypy`, `pytest` đều pass;
- data/config/seed/metric/run ID đã ghi nếu là experiment;
- docs/ADR/schema cập nhật nếu contract đổi;
- không commit secret, raw data, model lớn hay output local;
- reviewer xác nhận acceptance criteria bằng evidence trong issue/PR.

## Lịch làm việc theo tuần

### Tuần 1 — 07/09 đến 13/09: khóa scope và làm foundation xanh

**Mục tiêu:** hai máy cài/chạy giống nhau; chốt bài toán artist top-N implicit CF.

**Thành viên A**

- Viết problem statement, 2-3 research question và metric quyết định model.
- Hoàn thiện data card từ README HetRec: URL, license, checksum, schema, thống kê.
- Tạo tiny fixture để test pipeline.
- Đầu ra: README/data-card, ADR evaluation scope, fixture và validation tests.
- Cách làm: tính SHA-256; kiểm tra dtype/null/duplicate/positive weight; xác nhận item là artist;
  ghi rõ random leave-one-out vì dataset không có timestamp.

**Thành viên B**

- Sửa toàn bộ lỗi lint/format/mypy hiện tại.
- Chọn dependency workflow, ưu tiên `uv`; tạo `uv.lock`; đồng bộ README và CI.
- Sửa optional dependency để CI type-check UI, hoặc tạo type boundary có lý do và smoke job riêng.
- Đầu ra: clean-install guide, lock file và CI xanh.

**Kiểm tra chung:** tạo hai clean venv/clone và làm theo README; chạy bốn quality gates; đọc chéo
scope/ADR trước khi code model.

**Exit criteria:** M0 đạt; không còn TODO về source/license; scope được hai người duyệt.

### Tuần 2 — 14/09 đến 20/09: data pipeline và reproducibility

**Mục tiêu:** raw → validated → processed tái lập; config thật sự điều khiển code.

**Thành viên A**

- Chuyển data logic reusable từ scripts vào `src/musicrec/data/`.
- Implement validation report, duplicate aggregation, min-interaction filtering, log/confidence
  transform và deterministic ID mapping.
- Test schema lỗi, zero/negative weight, duplicate, empty data và determinism.

**Thành viên B**

- Khởi tạo DVC, cấu hình remote dùng chung và document credential setup.
- Chuẩn hóa CLI/config loader; nối `params`/`deps` DVC với code.
- Tạo pipeline smoke test bằng tiny fixture trên CI, không kéo full dataset.

**Kiểm tra chung:** chạy pipeline hai lần, lần hai không chạy lại stage; đổi một filter parameter và
xác nhận chỉ downstream liên quan bị invalidated.

**Exit criteria:** có `.dvc/`, `dvc.lock`, remote guide; data stats khớp data card; cùng
input/config sinh cùng output hash trên hai máy.

### Tuần 3 — 21/09 đến 27/09: split và evaluator chung

**Mục tiêu:** khóa “sân thi đấu” trước khi so model.

**Thành viên A**

- Implement random leave-one-out per user; log user bị loại.
- Implement Precision/Recall/NDCG/MAP@K, coverage, average popularity/novelty, diversity, latency.
- Sửa Precision@K dùng mẫu số K; test công thức bằng ví dụ tính tay.

**Thành viên B**

- Mở rộng `Recommender`/adapter để evaluator gọi mọi model thống nhất.
- Implement candidate mode `full`; nếu thêm sampled mode phải có seed/config riêng.
- Hoàn thiện Popularity save/load và unknown-user fallback contract.

**Kiểm tra chung:** golden metric tests; train không giao val/test theo `(user,item)`; recommendation
không chứa seen item; cùng seed cho cùng split/metric.

**Exit criteria:** M1 đạt; evaluator không có nhánh riêng theo model; test set đóng băng và chưa dùng
chọn hyperparameter.

### Tuần 4 — 28/09 đến 04/10: User-based CF

**Mục tiêu:** có User-kNN sparse và benchmark với Popularity.

**Thành viên A**

- Thiết kế experiment matrix cho neighbors, similarity và normalization.
- Viết oracle tests cho similarity, tie, unknown user và exclude-seen.
- Theo dõi memory/time và segment low-history/high-history.

**Thành viên B**

- Implement sparse User-kNN, tránh dense user-item matrix.
- Thêm save/load, config validation, deterministic tie-breaking và reason code.
- Log params, metrics, Git/data/config hash và artifact vào MLflow.

**Kiểm tra chung:** profile tiny/full data; review công thức bằng matrix tính tay; so validation với
Popularity bằng cả accuracy, coverage và latency.

**Exit criteria:** correctness tests pass, không OOM, run provenance đầy đủ.

### Tuần 5 — 05/10 đến 11/10: Item-based CF

**Mục tiêu:** có Item-kNN và bảng so sánh classical CF công bằng.

**Thành viên A**

- Mở rộng report; tính variability/confidence interval theo user khi phù hợp.
- Phân tích popularity bias, catalog coverage và cold/low-history segments.
- Review Item-kNN bằng oracle matrix.

**Thành viên B**

- Implement sparse Item-kNN cosine; TF-IDF/BM25 chỉ là ablation có config.
- Thêm neighbor cache, batch recommend, save/load và performance tests.
- Dùng chung base utilities, không copy evaluator/data logic.

**Kiểm tra chung:** cùng split, candidate set và K; báo cáo metric, wall time, peak memory.

**Exit criteria:** M2 đạt; ba baseline có reproducible runs; chưa nhìn test để chọn model.

### Tuần 6 — 12/10 đến 18/10: implicit matrix factorization

**Mục tiêu:** hoàn thành model-based CF phù hợp implicit feedback.

**Thành viên A**

- Viết ADR chọn implicit ALS/BPR; định nghĩa preference, confidence và negative sampling.
- Chuẩn bị evaluation harness/sanity checks.
- Thiết kế search space theo ngân sách compute.

**Thành viên B**

- Implement adapter ALS/BPR bằng thư viện `implicit` hoặc implementation có test.
- Save/load factors và mappings; seed; batch recommend; exclude seen.
- Nếu giữ `SVDRecommender`, ghi chính xác loss và cách xử lý unobserved.

**Kiểm tra chung:** compare mọi model bằng một command; reload model cho kết quả giống trong tolerance.

**Exit criteria:** fit chỉ dùng train; artifact load được; terminology trong code/report thống nhất.

### Tuần 7 — 19/10 đến 25/10: tuning và ablation

**Mục tiêu:** chọn hyperparameter có kỷ luật và biết thành phần nào tạo cải thiện.

**Thành viên A**

- Chạy search trên validation; lưu parent/child MLflow runs và resource usage.
- Ablation raw vs log/confidence, factors/neighbors, weighting và filter thresholds.
- Tổng hợp theo user segment và practical significance.

**Thành viên B**

- Tối ưu batch scoring/caching dựa trên profiler.
- Thêm config validation/fail-fast.
- Benchmark trước/sau; không đổi evaluator để nâng metric.

**Kiểm tra chung:** đóng search space trước khi chạy; review runs thiếu tag/hash; chọn tối đa hai
candidate cho Tuần 8.

**Exit criteria:** không cherry-pick run không lý do; có bảng ablation và selection record.

### Tuần 8 — 26/10 đến 01/11: reranking, model selection và freeze

**Mục tiêu:** cân bằng relevance với diversity/popularity và chốt candidate.

**Thành viên A**

- Định nghĩa objective/constraint cho reranker, chỉ dùng validation.
- Vẽ trade-off NDCG/Recall với coverage/diversity/popularity.
- Viết model-selection report và limitations.

**Thành viên B**

- Implement reranker tách khỏi base model; weights từ config.
- Test rank stability, duplicate, seen item, K bound và determinism.
- Chuẩn hóa reason cho base/reranked/fallback.

**Kiểm tra chung:** duyệt candidate bằng rubric từ Tuần 1; freeze config; thay đổi sau freeze phải có
issue và lý do.

**Exit criteria:** M3 đạt; một primary candidate và một fallback; test chưa dùng tuning.

### Tuần 9 — 02/11 đến 08/11: release artifact và serving

**Mục tiêu:** offline artifact là hợp đồng duy nhất của online service.

**Thành viên A**

- Hoàn thiện manifest: version, Git SHA, data version, MLflow run ID, seed, config hash, metrics,
  timestamp, schema và artifact checksums.
- Implement exporter, compatibility/checksum tests, model card và approval checklist.

**Thành viên B**

- Thay seed model trong API bằng startup artifact loader; fail-fast nếu artifact lỗi.
- Implement unknown user, temporary history và fallback thật.
- Đồng bộ `/health`, `/metrics`, `/recommend` và API docs.

**Kiểm tra chung:** làm hỏng checksum/schema để xác nhận loader từ chối; API không fit model; đo
p50/p95 latency.

**Exit criteria:** release load/restart ổn định; contract tests pass; version khớp manifest.

### Tuần 10 — 09/11 đến 15/11: UI, end-to-end và demo hardening

**Mục tiêu:** demo rõ giá trị nghiên cứu, không chỉ in JSON.

**Thành viên A**

- Sinh figures/tables từ run IDs và kiểm tra truy vết.
- Viết setup/recovery runbook, test fresh-clone reproduction.
- Chuẩn bị known-user, low-history, cold-start và error scenarios.

**Thành viên B**

- Hoàn thiện Streamlit: artist metadata, score/reason, fallback và error state.
- Thêm API integration/smoke tests và deployment script tối thiểu.
- Chỉ thêm Docker nếu cần demo nhất quán; pin dependency và healthcheck.

**Kiểm tra chung:** một người vận hành đúng runbook, người kia đóng vai người dùng; rehearsal và
ghi mọi lỗi thành issue.

**Exit criteria:** M4 đạt; clean setup chạy được; không phụ thuộc máy cá nhân hay lộ secret/trace.

### Tuần 11 — 16/11 đến 22/11: test set và bằng chứng cuối

**Mục tiêu:** sinh kết quả cuối sau khi model/config freeze.

**Thành viên A**

- Chạy test set một đợt được ghi nhận; lưu run ID và các hash.
- Sinh bảng/hình cuối, error/segment analysis, limitations và threats to validity.
- Đối chiếu công thức báo cáo với implementation/tests.

**Thành viên B**

- Chạy performance/load smoke, release integrity và end-to-end regression.
- Hoàn thiện architecture/API/deployment sections và diagram.
- Chỉ fix lỗi blocking; đổi model sau test freeze phải tạo release mới và giải trình.

**Kiểm tra chung:** review từng claim “tốt hơn”; số liệu phải map về MLflow run/manifest; kiểm tra
citation và license.

**Exit criteria:** evidence immutable; không có số chép tay không truy vết; critical bugs bằng 0.

### Tuần 12 — 23/11 đến 29/11: nghiệm thu, bàn giao và buffer

**Mục tiêu:** hoàn thiện chất lượng, không thêm feature.

**Thành viên A**

- Audit reproducibility/data/report và đóng checklist thesis evidence.
- Chuẩn bị Q&A về dataset, protocol, metric, bias và statistical validity.
- Archive release/data metadata theo chính sách.

**Thành viên B**

- Audit source/API/UI/security và đóng checklist demo.
- Chuẩn bị Q&A về algorithm, complexity, serving và trade-offs.
- Tạo release tag, changelog và rollback instructions sau khi duyệt.

**Kiểm tra chung:** hai full rehearsals từ clean state; thử API restart/artifact invalid; chỉ sửa
P0/P1, không thêm feature.

**Exit criteria:** M5 đạt; CI xanh trên tag; người còn lại thực hiện runbook thành công.

## Nhịp kiểm tra tiến độ

### Hằng ngày, bất đồng bộ — tối đa 5 phút/người

Mỗi người cập nhật issue bằng ba dòng: đầu ra/evidence đã xong; việc tiếp theo trong 24 giờ; blocker
cần ai xử lý và trước khi nào.

### Giữa tuần — 30 phút

- kiểm tra dependency, blocker và workload;
- task có nguy cơ trễ phải tách scope/đổi owner trước thứ Năm;
- review contract trước implementation;
- tối đa một task In Progress/người.

### Cuối tuần — 60 phút

1. Demo đầu ra chạy thật.
2. Kiểm acceptance criteria và Definition of Done.
3. Ghi planned points, accepted points, carry-over và lý do.
4. Ghi defects, CI failures, review turnaround và reproducibility.
5. Chỉ commit tối đa 80% capacity tuần sau; giữ 20% cho review/integration/lỗi.

## Rubric chất lượng tuần

| Tiêu chí | Trọng số | Cách chấm |
| --- | ---: | --- |
| Đầu ra được nghiệm thu | 35% | Điểm task merged + accepted / điểm cam kết |
| Correctness và test | 25% | CI, test biên/regression, leakage/determinism |
| Reproducibility/evidence | 20% | Config, seed, hash, run ID, command, artifact |
| Integration/review | 15% | PR nhỏ, review chéo, không phá contract |
| Tài liệu/rủi ro | 5% | Docs/ADR cập nhật; blocker/limitation ghi sớm |

- **Xanh (>= 85):** đúng milestone, không có blocker P0.
- **Vàng (70-84):** có carry-over/debt; tuần sau dành capacity xử lý.
- **Đỏ (< 70):** dừng feature mới, lập recovery plan và thu hẹp scope.

Một lỗi leakage, dùng test để tuning, mất tái lập hoặc `main` đỏ quá 24 giờ giới hạn tuần ở mức
Vàng cho đến khi khắc phục.

## Risk register

| Rủi ro | Tín hiệu | Giảm thiểu | Owner |
| --- | --- | --- | --- |
| Dataset/license chưa rõ | Data card còn TODO | Khóa Tuần 1, chưa chạy full experiment | A |
| Protocol không công bằng | Model dùng split/candidate khác | Evaluator chung và golden tests | A |
| Dense matrix/OOM | Memory tăng users × items | Sparse matrix, profile và budget | B |
| Experiment không tái lập | Run thiếu hash/seed | DVC + MLflow validation gate | A |
| API lệch artifact | Fit trong request/seed data | Manifest loader + integration tests | B |
| Xung đột Git | Cùng sửa shared file | Interface PR trước, ownership, WIP limit | Cả hai |
| Trễ tiến độ | Carry-over >20% hai tuần | Cắt P2, giữ baseline/evaluator/demo | Cả hai |

## Không nằm trên critical path

- deep learning, real-time retraining, microservices, Kubernetes;
- mobile app hoặc authentication phức tạp;
- online A/B testing khi không có người dùng thật;
- social/tag hybrid trước khi hoàn tất CF cơ bản;
- tự xây dashboard lớn khi GitHub Projects đã đủ.
