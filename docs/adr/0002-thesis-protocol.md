# Protocol khóa luận trên khang-dev

Ngày quyết định 18/10/2026. Nhóm thống nhất triển khai; chưa có xác nhận GVHD duyệt thay đổi.

Pipeline dùng count gốc dương/hữu hạn, cộng các cặp trùng và không lọc artist theo listener. User dưới 5 artist chỉ nằm trong train. Split theo user, ID sắp ổn định, NumPy default_rng seed 42; validation/test mỗi tập max(1, floor(0.1*n)), train nhận phần còn lại.

Popularity dùng listener phân biệt của train. Catalog chỉ có artist train; ground truth đầy đủ, cold target tính miss. Validation mask train; test mask train và validation nhưng mô hình/hồ sơ vẫn chỉ fit train. Không refit trước kết quả test. Precision chia K, NDCG nhị phân. Cấu hình chỉ chọn trên validation.

CF/SVD/PureSVD sử dụng điểm đại diện từ log2 count và các phân vị train, nội suy linear; BPR sử dụng positive nhị phân và negative chưa quan sát trong train. So sánh các phương án biểu diễn và học, không quy chênh lệch hoàn toàn cho thuật toán.

M1 dùng relevance, cosine tương tác nhị phân và listener penalty. M2 dùng ItemCF, TF-IDF thẻ và Popularity, kiểm chứng trên user tách riêng không tham gia fit hoặc tạo đặc trưng. Không gọi Given-N của user đã học là bằng chứng user mới.

Bản báo cáo đầy đủ mới chỉ xuất khi cần cập nhật phương pháp, số liệu hoặc hiện trạng; giữ nguyên V1 và mọi bản đã phát hành, không bắt buộc báo cáo tiến độ hoặc Markdown song song. Thử nghiệm lastfm-reproduction giữ độc lập vì protocol khác.
