# Changelog

Mọi thay đổi đáng chú ý của MusicRec được ghi trong file này theo
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) và Semantic Versioning.

## [Unreleased]

### Added

- Nghiên cứu HetRec LastFM: tải và xác minh nguồn, EDA, dataset card và manifest/DVC cục bộ.
- Giao thức tái hiện một phần Deng (2022): 30 split công khai, Pure-DHC/ProbS/AIProbS
  thưa và adapter BPR huấn luyện bằng RecBole 1.1.1 trong môi trường riêng.
- Evaluator full-catalog với Recall/MRR/NDCG/Hit/Precision@10, kiểm chứng tham chiếu,
  chống rò rỉ và báo cáo từng split; MLflow cục bộ, checkpoint có RNG và dependency lock.

### Fixed

- Precision@K chia cho K khi danh sách ngắn; từ chối listening count NaN/vô hạn/không dương.

### Planned

- Thêm pipeline xử lý HetRec/Last.fm và data validation.
- Cài đặt Popularity, User-based CF, Item-based CF, SVD và reranker.
- Thêm DVC remote và API/UI demo cho pipeline khóa luận.

## [0.1.0] - 2026-08-25

### Added

- Khởi tạo modular monorepo, package `musicrec`, test layout và GitHub Actions CI.
- Thêm khung DVC/MLflow, cấu hình model, API contract và tài liệu vận hành.
- Thêm quy tắc phát triển, changelog và mô tả kiến trúc.
