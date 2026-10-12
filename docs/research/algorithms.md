# Phép tính thực tế trong bản tái hiện

Nguồn: [Deng (2022), phương trình 1–5 và Bảng 2](https://doi.org/10.1038/s41598-022-21607-4),
[mã tác giả đã ghim](https://github.com/pitteryue/AIProbS/tree/051ab349c1bfe493cb5eabd3b6ec1fe0c3a3e0f2).
Điều kiện chia, catalog và mask nằm trong [ADR 0002](../adr/0002-lastfm-reproduction-protocols.md).

## Đầu vào chung

Gọi R là ma trận user × artist: R[u,i]=1 nếu cặp thuộc **train**, ngược lại bằng 0.
Số lượt nghe không tham gia trọng số. Validation/test không xây đồ thị, DHC hoặc
popularity. Catalog vẫn giữ item chưa xuất hiện trong train; padding được giữ khi
tính toán để bảo toàn thứ tự ID nhưng bị loại khỏi ranking.

## Pure-DHC

Đồ thị hai phía có ma trận khối B = [[0,R],[Rᵀ,0]]. Khởi tạo h₀(v)=degree(v).
Mỗi bước cập nhật đồng bộ hₜ₊₁(v) bằng h-index của các giá trị hₜ ở hàng xóm:
số nguyên lớn nhất h sao cho ít nhất h hàng xóm có giá trị ≥h. Lặp đến khi toàn bộ
vector hội tụ. Feature của node là dãy [h₀,h₁,…], bỏ cột hội tụ lặp lại theo code tác giả.
Node cô lập có feature 0.

Điểm user–artist là cosine giữa hai feature. Mẫu số thêm 1e-24 như mã tham chiếu.
Đây là biểu diễn DHC cục bộ của nhánh đang hoạt động, không phải DHC-E toàn cục.

## ProbS

Đặt Dᵤ và Dᵢ là ma trận đường chéo bậc user và item trong train. Nghịch đảo bậc
bằng 0 tại node cô lập. Điểm của toàn bộ user là:

```text
S = R Dᵢ⁻¹ Rᵀ Dᵤ⁻¹ R
```

Triển khai nhân theo batch: W_item=R Dᵢ⁻¹, W_user=Dᵤ⁻¹R,
S_batch=(R_batch W_itemᵀ) W_user. Cách kết hợp này tránh tạo ma trận item × item.

## AIProbS

Tính C[u,i]=cosine(DHC(user),DHC(artist)) nếu R[u,i]=1; ở ô khác C=0.
Chuẩn hóa C theo **từng hàng** để tạo W_user và độc lập theo **từng cột** để tạo
W_item. Mỗi chiều thực hiện min-max có tính cả ô 0, rồi chia từng trọng số cho
tổng của hàng/cột đó. Vector có span=0 được giữ trước bước chia tổng; tổng 0 cho vector 0.

```text
S_batch = (R_batch W_itemᵀ) W_user
```

Trong mã, nhánh `max-min` rồi `mean` thực hiện phép chia **trọng số cho tổng**.
Phương trình (4) trong bản in có cách viết khác (nghịch đảo trọng số/tổng).
Bản này bám phép toán code; chưa có đính chính tác giả để kết luận công thức in là lỗi.
Không trộn kết quả một biến thể công thức khác vào dòng tái hiện AIProbS.

## BPR và đánh giá

RecBole 1.1.1 huấn luyện BPR bằng negative sampling và Adam của thư viện.
Embedding 64, learning rate 0.0005, train batch 4096, trần 5.000 epoch,
stopping_step=50, checkpoint chọn bằng NDCG@10 validation. Adapter chỉ nạp factor
đã ánh xạ lại catalog nguồn và tính tích vô hướng float32. Subclass Trainer chỉ
thay lưu checkpoint nguyên tử và bổ sung trạng thái RNG; không đổi loss/optimizer.

Sau khi fit, mask train cho validation và train+validation cho test, loại PAD,
chọn Top-10 trên toàn catalog bằng `torch.topk` CPU. Recall chia cho số positive;
Precision chia cho 10; MRR lấy nghịch đảo vị trí hit đầu tiên; Hit là biến 0/1;
NDCG nhị phân dùng discount log₂(rank+1) và ideal length min(10, số positive).
Lấy trung bình theo user có ground truth của loader gốc. User không có positive
không được đánh giá; cold-item positive vẫn nằm trong mẫu số Recall/NDCG.

## Bằng chứng tương đương

Ví dụ nhỏ chạy các định nghĩa tác giả không đổi, ProbS đối chiếu công thức đặc
độc lập. Full split 0 thay riêng cấp phát đồ thị/duyệt hàng xóm sang CSR để vừa RAM,
giữ updater DHC, cosine và ComputeSimilarity của tác giả. Sai số tối đa Pure-DHC=0,
AIProbS=1,33e-15, dưới rtol=1e-6/atol=1e-8. Artifact lưu ở
`outputs/research/{tiny,full}_reference_verification.json` cùng patch.

Metric được kiểm tra riêng bằng RecBole trên cùng ranking, gồm vector từng user
với atol=1e-12 và số trung bình làm tròn bốn chữ số. Khớp số làm tròn của bài báo
không thay thế các kiểm chứng số học và giao thức này.
