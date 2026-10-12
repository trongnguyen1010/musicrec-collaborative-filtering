# Căn cứ nghiên cứu và phạm vi tái hiện

## Tài liệu được chọn

| Nguồn | Đúng HetRec LastFM 2K? | Vai trò trong đợt này | Bằng chứng tái hiện |
|---|---|---|---|
| Yue Deng (2022), *Determinable and interpretable network representation for link prediction*, Scientific Reports 12, 17579, DOI 10.1038/s41598-022-21607-4 | Có, 1.892 user / 17.632 item / 92.834 cặp | Tái hiện Pure-DHC, ProbS, AIProbS ở Bảng 2 | Mã + 30 split công khai; bản cài lại và kiểm chứng tham chiếu |
| RUCAIBox, RecBole-GNN, `results/social/lastfm.md` | Có | Đối chứng BPR; đây là báo cáo benchmark phần mềm | Cấu hình và bảng kết quả công khai; không có checksum split gốc |
| Kowald, Schedl, Lex (2020), *The Unfairness of Popularity Bias in Music Recommendation: A Reproducibility Study* | Không, dùng LFM-1b | Tham khảo thiết kế popularity bias cho M1 | Không nhận là tái hiện HetRec |
| Zanon, da Rocha, Manzato (2022), *Balancing the trade-off between accuracy and diversity in recommender systems with personalized explanations based on Linked Open Data* | Có | Nghiên cứu liên quan M1/metadata, dành giai đoạn sau | Mã công khai nhưng không nằm trong ma trận thực nghiệm đã chốt |

Nguồn chính:

- [Bài Deng bản xuất bản](https://doi.org/10.1038/s41598-022-21607-4), dùng Bảng 2 LastFM.
- [Mã AIProbS ghim snapshot](https://github.com/pitteryue/AIProbS/tree/051ab349c1bfe493cb5eabd3b6ec1fe0c3a3e0f2).
- [Báo cáo benchmark đã ghim](https://github.com/RUCAIBox/RecBole-GNN/blob/9092ac4452224c9c1754d8c4b89b4eb2abaaf71f/results/social/lastfm.md).
- [Kowald: bản tác giả](https://arxiv.org/abs/1912.04696).
- [Zanon: DOI](https://doi.org/10.1016/j.knosys.2022.109333), [mã tác giả](https://github.com/andlzanon/lod-personalized-recommender).

BPR 2009, Sarwar 2001, Hu–Koren–Volinsky 2008 và các tài liệu SVD là cơ sở thuật toán;
chúng có trước bộ HetRec 2011, không phải nguồn số liệu thực nghiệm HetRec trong đợt này.

## Mốc số công bố

| Nguồn | Mô hình | Recall@10 | MRR@10 | NDCG@10 |
|---|---|---:|---:|---:|
| Deng, Bảng 2 | Pure-DHC | 0.004 | 0.006 | 0.003 |
| Deng, Bảng 2 | ProbS | 0.170 | 0.308 | 0.166 |
| Deng, Bảng 2 | AIProbS | 0.184 | 0.340 | 0.183 |
| Benchmark RecBole-GNN | BPR | 0.1761 | 0.3026 | 0.1674 |

Các mốc này **không phải kết quả mới**. BPR benchmark còn công bố Hit@10=0.5573 và
Precision@10=0.0858. Bảng kết quả mới tách nguồn và giao thức, ghi chênh lệch tuyệt
đối/tương đối. Không dùng các số của hai bảng gốc để tuyên bố thắng/thua trực tiếp.

## Các vấn đề cần kiểm soát

1. Lấy đúng 30 split tác giả, không tái tạo bằng seed rồi gọi là split gốc.
2. Giữ ID padding để tái tạo thứ tự; bỏ padding khỏi candidate và thống kê user/item.
3. Graph DHC chỉ chứa train. Tag/friendship không được đưa vào ba model bài báo hoặc BPR.
4. Không đổi implicit binary thành log-count/proxy rating hoặc lọc min-item-5.
5. Đối chiếu phép tính trong mã với phương trình; các nhánh ngoài cosine/max-min+mean
   không được chạy rồi gán chung nhãn AIProbS đã chọn.
6. Đánh giá độc lập metric trên cùng ranking bằng RecBole và evaluator của dự án.
7. Giữ negative sampling, Adam, epoch tối đa và early stopping BPR theo cấu hình;
   không giảm số epoch nhằm tiết kiệm thời gian rồi nhận là benchmark gốc.

## Hướng đưa vào khóa luận

Đợt này kiểm chứng bộ dữ liệu và pipeline Top-N trước. Hướng đề tài vẫn là khuyến nghị
**nghệ sĩ**, không chuyển sang bài toán track, rating thực hoặc hệ thống social-CF.
M1 cần khảo sát mức tập trung phổ biến và long-tail trước khi chốt ngưỡng lọc.
M2 cần xử lý độ phủ tag, artist ngoài metadata và kiểm soát tag từ cặp held-out.
Given-N phải ẩn lịch sử/factor phù hợp, không chỉ cắt danh sách đầu vào ở API.
