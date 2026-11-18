# Đối chiếu mã commit cũ và mới sau khi viết lại lịch sử (18/11/2026)

Ngày 18/11/2026, lịch sử Git của `main` và `research/data-preparation-model-survey` được viết lại để đổi tác giả của 18 commit (từ "Claude" sang trongnguyen1010) và bỏ các dòng `Co-Authored-By`/`Claude-Session` trong lời commit. Việc viết lại chỉ đổi tác giả và lời commit, không đổi nội dung code: cây thư mục (git tree) của mỗi commit mới giống hệt commit cũ tương ứng. Vì vậy mỗi mã commit cũ đều có một mã mới chứa đúng code đó, và các kết quả vẫn tái lập được bằng mã mới.

Các commit trước ngày 26/10/2026 và commit của Lê Khắc Gia Khang giữ nguyên mã. Mọi commit từ 26/10/2026 trở đi trên hai nhánh trên đều đổi mã (kể cả commit vốn do trongnguyen1010 làm tác giả), vì mã commit phụ thuộc vào commit cha.

## Bảng đối chiếu (các mã được nhắc trong repo)

| Mã cũ | Mã mới | Ngày | Nội dung commit |
|---|---|---|---|
| `8d170f9` | `235fdfd` | 26/10/2026 | fix: skip matplotlib cache when comparing Chapter 3 reruns |
| `c8a82fc` | `08cfc0e` | 26/10/2026 | feat: M1 config on the tuned PureSVD binary base (k=16) |
| `e1350ce` | `4581404` | 26/10/2026 | docs: Chapter 3 step 3.3 final design and proposed report edits |
| `7058883` | `ab7d671` | 26/10/2026 | docs: official cloud run and one-time test evaluation for Chapter 4 |
| `717d04b` | `a548469` | 26/10/2026 | feat: lock the M2 selection and score reserved users on test once |
| `09a3336` | `4512873` | | chore: đưa gói release demo vào Git để nhóm pull về là chạy được |
| `9e9350e` | `872f4ba` | 26/10/2026 | docs: khảo sát nghiên cứu 2021–2025 và đề xuất hướng phát triển mới |
| `5a4ed93` | `bded7b1` | | docs: phản hồi ý kiến phản biện của GPT về khảo sát hướng mới |
| `b2c0dbb` | `7d9fcf6` | | docs: consolidate H1 debate and agreed experiment specification |
| `d1ea7d1` | `5f565cb` | | docs: kế hoạch prototype demo FastAPI + Streamlit + Next.js |
| `60b175c` | `e03afe6` | | docs: thêm quy tắc viết báo cáo |
| `26af632` | `7e09c61` | | docs: báo cáo v18 với Chương 5 theo FastAPI + Next.js và sửa Chương 1-3 theo góp ý GVHD |
| `383c8c9` | `5d07022` | | Thêm SHA256SUMS_checkpoints_demo.txt: mã băm các checkpoint của lần chạy chính thức |

Mã đầy đủ 40 ký tự: dùng `git log --format='%H %s' main` và tìm theo nội dung commit.

## Tệp được sửa mã commit

Các tệp `.md` và các tệp JSON không bị khóa bằng mã băm đã được đổi sang mã mới (manifest gói demo, `environment.json`, các `metrics.json`/`lock.json` trong `bo_sung/`, `bo_sung_2/`, `chuong_3/`, `chuong_4_bo_sung_3/`, `chuong_5/release_manifest.json`).

## Tệp giữ nguyên mã cũ

Các tệp dưới đây được khóa bằng mã băm SHA-256 (trong `SHA256SUMS_checkpoints_demo.txt`, `chuong_5/release_manifest.json`, manifest gói demo hoặc `lock.json` khác), hoặc sinh cùng lần chạy với tệp bị khóa. Sửa chúng sẽ làm lệch mã băm, nên giữ nguyên bản ghi gốc và tra mã mới theo bảng trên:

| Tệp | Mã cũ ghi trong tệp | Mã mới tương ứng |
|---|---|---|
| `docs/results/chinh_thuc_cloud_20261026/test/lock.json` | `e1350ce` | `4581404` |
| `docs/results/chinh_thuc_cloud_20261026/test/metrics.json` | `e1350ce` | `4581404` |
| `docs/results/chinh_thuc_cloud_20261026/m2/test/lock.json` | `717d04b` | `a548469` |
| `docs/results/chinh_thuc_cloud_20261026/m2/test/metrics.json` | `717d04b` | `a548469` |
| `docs/results/chinh_thuc_cloud_20261026/m2/validation/metrics.json` | `7058883` | `ab7d671` |
