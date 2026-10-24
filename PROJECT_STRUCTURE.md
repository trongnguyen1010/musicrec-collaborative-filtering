# Bộ khung và cấu trúc dự án MusicRec

## Mục tiêu kiến trúc và trạng thái

Đây là modular monorepo Python cho khuyến nghị nghệ sĩ. Cấu trúc dưới đây mô tả trách nhiệm hiện có và hướng hoàn thiện; không xác nhận mọi module, pipeline hoặc cơ chế phát hành đã hoạt động.

Thứ tự thực hiện theo [kế hoạch từng bước](docs/WEEKLY_IMPLEMENTATION_PLAN.md) và [quy tắc phát triển](DEVELOPMENT_RULES.md). Mô hình nền trước, M1/M2 sau, prototype sau lựa chọn mô hình. API/UI online dự kiến chỉ nạp artifact để suy luận; không huấn luyện trong HTTP request.

```text
src/musicrec/
  data/          kiểm tra schema, làm sạch, split, biến đổi và mapping
  recommenders/  sáu baseline, sau đó M1/M2 theo bước được phép
  evaluation/    evaluator chung cho ranking và các chỉ số bổ sung
  artifacts/     thông tin phiên bản và kiểm tra artifact khi đến bước đóng gói
  serving/       ứng viên, lọc lịch sử và fallback khi đến bước prototype
  api/           FastAPI và schema
  ui/            Streamlit gọi API
```

## Vị trí các thành phần

| Đường dẫn | Trách nhiệm |
| --- | --- |
| configs/, params.yaml | Cấu hình; phải đối chiếu với phương pháp đã thống nhất trước khi chạy, chưa coi mặc định cũ là quyết định nghiên cứu. |
| data/ | Nguồn và dữ liệu dẫn xuất, giữ tách biệt; không commit dataset vào Git. |
| notebooks/ | EDA/phân tích khi đến bước; logic dùng lại chuyển vào src/ hoặc scripts/. |
| scripts/ | Điểm chạy từng bước; không tự nối các bước chưa được phép. |
| tests/ | Kiểm tra phù hợp với thay đổi và ví dụ tính tay; không chạy thực nghiệm ngoài phạm vi để kiểm tra tài liệu. |
| outputs/runs/ | Vị trí dự kiến cho run riêng: cấu hình, dự đoán, metric và thời gian; không ghi đè. |
| artifacts/releases/ | Artifact được chọn để demo sau thực nghiệm; không phải mọi lần thử đều là release. |
| docs/reports/ | Các bản Word đầy đủ đã bàn giao; tên `33_BaoCaoKhoaLuan_CaoTrongNguyen_LeKhacGiaKhang_DD-MM-YYYY.docx`, giữ nguyên nội dung bản cũ. Bản mới trùng ngày lưu trong thư mục con Vn theo DEVELOPMENT_RULES.md. |
| docs/adr/ | Quyết định kiến trúc đã có; không bắt buộc tạo thêm ADR. |

## Luồng nghiên cứu dự kiến

```text
kiểm tra nguồn → EDA → làm sạch → split → biểu diễn → evaluator
→ từng baseline → tinh chỉnh được phép → so sánh validation
→ M1 → M2 → khóa cấu hình → test cuối → đóng gói và prototype
```

Đây là các lần làm riêng có điểm dừng. Chưa phải cam kết rằng một lệnh DVC có thể chạy đúng toàn bộ luồng. DVC/MLflow hiện có có thể được dùng khi cần; không yêu cầu thiết lập remote/tracking server để thay thế kiểm chứng phương pháp.

Khảo sát mở rộng ngày 24/10/2026 ưu tiên implicit ALS rồi BPR-MF, dự phòng SLIM. Nếu được phép và còn thời gian trước mốc 15/11, nhánh này nằm sau tổng hợp validation sáu baseline, trước chốt nền M1 và test; thiếu thời gian thì sau demo. Chưa tạo module/config hoặc đổi giao diện fit/predict/recommend/API. Khi triển khai vẫn dùng recommenders/ và evaluator chung; điều kiện, ngân sách và ảnh hưởng khi đổi nền M1 ở [kế hoạch hiện hành](docs/WEEKLY_IMPLEMENTATION_PLAN.md#thực-nghiệm-bổ-sung-có-giới-hạn). M2 vẫn dùng ItemCF theo protocol riêng.

Mỗi run phải có config, seed, phiên bản mã và tình trạng thay đổi chưa commit, hash dữ liệu/split, biến đổi, dự đoán, metric và thời gian. CSV/JSON cùng các tệp kết quả là đủ nếu truy vết và tái lập được. Khi đến bước release, lưu model, mapping, biến đổi, metadata, config, metric và manifest; ID MLflow chỉ cần khi thực sự sử dụng MLflow.

## Quy trình thay đổi

- Giữ lịch sử Git; không đưa lại mã/đầu ra của đợt đã bỏ vào quy trình mới nếu chưa được phép.
- Một thay đổi có mục tiêu rõ, review và kiểm tra phù hợp. Quy tắc PR/CI áp dụng khi chuẩn bị PR; không tạo công việc quản lý riêng để trì hoãn bước nghiên cứu.
- Thay đổi chỉ Markdown kiểm tra nội dung, liên kết và diff; không yêu cầu chạy huấn luyện hoặc xử lý dữ liệu.
- Hoàn thành bước phải có giải thích và dừng theo yêu cầu người dùng, không đồng nghĩa đã phát hành hệ thống.
