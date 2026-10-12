# ADR 0002 — Giao thức tái hiện LastFM và giao thức khóa luận

Ngày: 2026-10-12. Trạng thái: accepted.

## Bối cảnh

Báo cáo khóa luận thiết kế implicit artist Top-N và chia khoảng 80/10/10. Script
khung hiện tại lại dùng leave-one-out. Các số bài báo không thể đối chiếu trực tiếp
khi đổi bộ lọc, candidate catalog, ground truth hoặc cách chia.

## Quyết định

| Giao thức | Dữ liệu/chia | Candidate và ground truth | Mục đích |
|---|---|---|---|
| `aiprobs-original` | Binary, không lọc; giữ nguyên 30 split đã lưu của tác giả | Toàn catalog nguồn; bỏ PAD; validation mask train, test mask train+validation; giữ cold-item target | Ba dòng Pure-DHC/ProbS/AIProbS của Deng 2022 và BPR cùng split |
| `recbole-bpr-benchmark` | Binary, không lọc; random theo user 80/10/10; seed 2020/2021/2022, RecBole 1.1.1 | Full sort theo quy tắc RecBole; giữ cold-item target | Khôi phục benchmark BPR từ cấu hình công khai |
| `thesis` | Chưa chạy trong đợt này; thiết kế min-user-5 và 80/10/10 trong DOCX | Warm-start và các loại trừ phải báo cáo riêng | M1/M2 và toàn bộ baseline về sau |

Metric chính: Recall/MRR/NDCG@10; kiểm tra Hit/Precision@10. Precision chia cho K.
Ground truth rỗng: metric hàm trả 0; thí nghiệm chỉ đánh giá các user có positive
theo danh sách native đã xuất, báo cáo số user không được đánh giá. Không tự loại
cold target để nâng điểm. Không refit train+validation cho bảng tái hiện.

Training dùng train duy nhất. DHC/cosine/độ phổ biến không nhìn validation/test.
Điểm bằng nhau trong tái hiện dùng torch.topk CPU trên thứ tự catalog nguồn;
recommend phục vụ ứng dụng dùng ID ổn định và loại item đã nghe.

Nhị phân hóa là phép ánh xạ weight>0 -> 1, không coi missing là dislike đã quan sát.
Các score không phải xác suất đã hiệu chuẩn hoặc dự đoán rating thực.

## Điều chỉnh được công bố

- Mã AIProbS ghim commit `051ab349c1bfe493cb5eabd3b6ec1fe0c3a3e0f2`.
- Chạy các định nghĩa tác giả nguyên trạng trên ví dụ nhỏ. Full split 0 chỉ thay
  cấp phát đồ thị/duyệt neighborhood sang CSR; updater DHC, cosine và
  ComputeSimilarity của tác giả giữ nguyên. Patch và sai số có artifact riêng.
- Công thức (4) in trong bài và phép chia cho tổng ở code không thống nhất.
  Tái hiện code dùng phép toán công khai, không tự gọi khác biệt này là erratum.
- Pickle 2022 chứa `dataset`; bridge RecBole 1.1.1 ánh xạ sang `_dataset`, remap
  storage về CPU. Bảo toàn cặp, mapping, native user set và history được kiểm tra.
- BPR dùng lớp BPR/Trainer của RecBole, không viết lại loss hoặc optimizer.
  Subclass chỉ lưu checkpoint nguyên tử và RNG để phục hồi; cấu hình học giữ nguyên.
- Batch đánh giá BPR tăng từ 64 lên 256 user sau đo CPU trên validation; metric
  không đổi ở độ chính xác của evaluator. Kết quả đo lưu `cpu_thread_benchmark.json`.
- Không có split/hash/seed tường minh của benchmark gốc; seed 2020 suy từ default
  RecBole 1.1.1. Hai seed bổ sung đo biến động, không giả nhận là split xuất bản.

## Hệ quả

Tái hiện **một phần** Bảng 2 LastFM, không gồm DHC-E toàn cục, MovieLens hoặc toàn bộ
baseline học sâu. Không gộp số của hai giao thức. Coverage/ARP/novelty là phân tích
bổ sung, không nhận là metric tái hiện trong bài. Giữ nguyên DOCX gốc.
