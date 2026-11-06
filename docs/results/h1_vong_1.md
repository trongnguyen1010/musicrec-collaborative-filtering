# Kết quả H1 vòng 1: hậu xử lý phổ trên ALS, validation seed 42

Ngày chạy: 27/10/2026, kết thúc lúc 06:04:15 UTC, trên máy Windows cục bộ. Mọi con số trong tài liệu này đến từ **một lần chạy** `outputs/runs/h1_round1_validation_seed42_20261027/` (các tệp `points_validation_seed_42.csv`, `lock_h1.json`, `spectral_audit.json`, `metrics.json`). Thiết kế theo [đặc tả H1](../tai-lieu-tham-khao/khao-sat-huong-moi/DAC_TA_H1_THONG_NHAT_SAU_DEBATE.md), mục 3–7.

Nhãn bằng chứng đã được hai bên nhận (đặc tả, mục 11):

> Đánh giá bổ sung cho mục tiêu giảm thiên lệch đã có trước; phương pháp, tiêu chí và cấu hình cụ thể được thiết kế sau khi kết quả test đợt đầu đã được xem. Việc chọn bổ sung dùng validation và khóa trước lần chấm mới. Kết quả trên test dùng lại không được coi là xác nhận hoàn toàn độc lập cho giả thuyết mới.

## Tóm tắt

- **Cổng phát triển dừng nhánh phổ.** Trạng thái `stop_all_spectral_configurations_dominated_by_direct_control`: cả 6 cấu hình phổ nằm trong biên NDCG đều bị ít nhất một cấu hình phạt độ phổ biến trực tiếp trội (NDCG không thấp hơn và Non-head exposure cao hơn).
- **Kết luận hẹp:** chưa thấy giá trị thêm của can thiệp phổ trong ngân sách và giao thức này. Kết quả **không** cho phép kết luận mọi phương pháp phổ đều thất bại.
- Không cấu hình phổ nào được khóa. Theo đặc tả, không chạy seed 43/44, không chấm test, không sang vòng đối chứng 2 và không mở rộng lưới.
- Đối chứng phạt trực tiếp được khóa là β = 0,5. Bootstrap phát triển của nó **chưa đạt** điều kiện không suy giảm NDCG: cận dưới một phía của z_N là −0,001544, p_N = 0,1904.
- Nền ALS nạp lại tái lập đúng NDCG@10 validation 0,1974331612 của lần chạy chính thức.

## 1. Câu hỏi và phạm vi

Câu hỏi (đặc tả, mục 2): hậu xử lý thành phần phổ chính của ma trận điểm ALS, với mức sửa chung hoặc theo người dùng, có tăng tỷ lệ vị trí gợi ý cho nghệ sĩ ngoài head trong khi NDCG@10 không giảm quá 5% tương đối so với chính nền ALS không? Trong ngân sách công bố, nó tạo được vùng đánh đổi nào so với phạt độ phổ biến trực tiếp?

| Mục | Giá trị |
| --- | --- |
| Nền | ALS Chương 4 đã khóa: 32 nhân tố, regularization 0,1, confidence 1 + ln(1 + count); chỉ checkpoint seed 42; không fit lại |
| Điểm H1 | s'ᵤᵢ = sᵤᵢ − γᵤ·σ₁·l₁(u)·r₁(i), phổ của S = PQᵀ tính qua QR mỏng của hai nhân tố |
| Hai loại γ | γ chung: γᵤ = γ₀; γ theo sai lệch: γᵤ = γ₀·min(1, dᵤ/d_ref) |
| Lưới γ₀ | {0; 0,1; 0,25; 0,5; 0,75; 1} cho mỗi loại |
| Đối chứng | s = s_norm − β·p(i), min–max theo user trên catalog chưa nghe trong train; β ∈ {0; 0,01; 0,025; 0,05; 0,1; 0,25; 0,5; 1} |
| Ngân sách | 11 cấu hình phổ + 8 cấu hình phạt trực tiếp − 1 nền trùng = **18 danh sách** |
| Dữ liệu đánh giá | Validation, che train; 1.877 user, 1.865 user có đích trong catalog |

## 2. Môi trường và nguồn

| Mục | Giá trị |
| --- | --- |
| Máy | Windows 11 (10.0.26200), Intel Core i5-11300H, 8 luồng logic, RAM 16.856.203.264 byte |
| Python | 3.11.9 |
| Thư viện | numpy 2.4.6, scipy 1.17.1, pandas 2.3.3, implicit 0.7.3, pyarrow 19.0.1 |
| Commit khi chạy | `b2c0dbbf49aa38b383364be8a0678f2afca6c7f5`, code H1 lúc đó chưa commit; bản sao code nằm trong `code/` của run và mã băm ghi trong `metrics.json` |
| Thời gian | Toàn lượt 216,99 s; context phổ + gate 10,82 s; context phạt trực tiếp 1,33 s |
| RAM đỉnh | 557.617.152 byte (peak working set của tiến trình) |
| `lock_h1.json` | SHA-256 `cd90b8cc0cb1bfee121c51d532cb5087b2ba7c6e9eeeff476caf55bf85927c32` |

Checkpoint lấy từ lần chạy chính thức trên máy đám mây, chép về `outputs/chinh_thuc_cloud_20261026/`. Cả 83 tệp khớp `SHA256SUMS`. Cả ba seed khớp [lock.json](chinh_thuc_cloud_20261026/test/lock.json) ở `metrics.json`, `confidence.npz`, `factors.npz` và `state.json`. Lượt này chỉ dùng seed 42:

| Tệp seed 42 | SHA-256 |
| --- | --- |
| `factors.npz` | `f724163bad5677bfbaac940525f76bae84e6d282daea5e43ceae34fee3a99c13` |
| `confidence.npz` | `58f6563e35617e6f6630f38cde0ecdb200f46f320d6647fcb44e44067585859f` |
| `state.json` | `af3f25d26cca909a8059d1e2a26a2f00d08922f6589f3c23e3c9a09fa01a1afe` |
| `metrics.json` | `dc18d1e719a8e0f2c6149fd8666ce9721f4dc0e8e691ed186021147100b1f7de` |

Script ghim mã băm mọi tệp đầu vào và kiểm lại khi kết thúc. Một guard chặn mọi lệnh mở `test.parquet`.

**Kiểm tra tái lập nền.** Nền nạp lại cho đúng danh sách trong `recommendations.csv` và đúng `evaluation.json` của run chính thức; script dừng nếu lệch. NDCG@10 = 0,1974331612, khớp `validation_ndcg_at_10_seed42` = 0,19743316124043386 trong lock.

## 3. Nhóm ngoài head

Head là prefix ngắn nhất theo số user train phân biệt, giảm dần, có tổng ≥ 20% số cặp train, cộng mọi nghệ sĩ hòa ở điểm cắt.

| Mục | Giá trị |
| --- | --- |
| Số cặp train M | 74.275 |
| Head | 74 nghệ sĩ, ngưỡng 114 người nghe, chiếm 20,07% số cặp |
| Ngoài head T | 15.324 nghệ sĩ, chiếm 79,93% số cặp |
| SHA-256 danh sách head | `0af685add3806ceadb2413f70f8d1f09f9b68e445f928c4c3ddb2db78b61d044` |
| SHA-256 danh sách ngoài head | `b6e0b19d8cc4503a401d2c6829f7f04a77a8276df1e3dcef30b259305c5d0bc3` |

T gộp cả mid và tail, nên không phải nhóm tail hẹp của Abdollahpouri và cs. (UMAP 2021). Non-head exposure@10 của một user là số vị trí trong top-10 thuộc T chia 10.

## 4. Kiểm toán phổ và gate (chỉ mô tả)

Theo đặc tả, các đại lượng này không làm cổng và không có ngưỡng.

| Đại lượng | Giá trị |
| --- | --- |
| σ₁ … σ₅ | 141,228; 103,484; 75,933; 69,065; 60,188 |
| σ₁/σ₂ | 1,3647 |
| σ₁ − σ₂ | 37,744 |
| Tỷ trọng năng lượng σ₁²/Σσⱼ² | 19,70% |
| Spearman(r₁, số người nghe train) | 0,737 |
| ‖PᵀP − QᵀQ‖_F / ‖QᵀQ‖_F | 64,94 |

Độ lệch cân bằng 64,94 cho thấy checkpoint đã chọn epoch theo validation còn xa điểm dừng cân bằng. Vì vậy hướng chính của Q không dùng được thay cho hướng chính của S, khớp với quyết định tính phổ qua S trong đặc tả.
Gate theo sai lệch: d_ref = 0,3783 (phân vị 90 của các dᵤ > 0). Có 1.872/1.877 user với dᵤ > 0 và 188 user ở mức tối đa (trọng số bằng 1). Như vậy gần như mọi user đều được nền gợi ý phổ biến hơn lịch sử của chính họ.

## 5. Bảng 18 cấu hình

N = NDCG@10, E = Non-head exposure@10. Coverage, ARP, A_history và A_target đều tính ở K = 10 trên cùng 1.865 user.

| Cấu hình | N | E | Coverage | ARP | A_history | A_target |
| --- | --- | --- | --- | --- | --- | --- |
| Nền | 0,197433 | 0,544665 | 0,049747 | 138,11 | 0,2345 | 0,2080 |
| γ chung 0,1 | 0,195254 | 0,568418 | 0,050461 | 132,57 | 0,2281 | 0,2028 |
| γ chung 0,25 | 0,192411 | 0,601984 | 0,051370 | 124,63 | 0,2188 | 0,1950 |
| γ chung 0,5 | 0,184647 | 0,663539 | 0,053968 | 110,28 | 0,2018 | 0,1817 |
| γ chung 0,75 | 0,173906 | 0,722895 | 0,056111 | 96,78 | 0,1859 | 0,1702 |
| γ chung 1 | 0,164969 | 0,777962 | 0,058449 | 84,96 | 0,1726 | 0,1622 |
| γ sai lệch 0,1 | 0,196019 | 0,557962 | 0,050136 | 134,89 | 0,2308 | 0,2050 |
| γ sai lệch 0,25 | 0,194812 | 0,576997 | 0,050721 | 130,23 | 0,2253 | 0,2001 |
| γ sai lệch 0,5 | 0,193040 | 0,610456 | 0,052280 | 122,06 | 0,2156 | 0,1919 |
| γ sai lệch 0,75 | 0,189309 | 0,645791 | 0,053838 | 114,24 | 0,2054 | 0,1836 |
| γ sai lệch 1 | 0,184673 | 0,679678 | 0,055527 | 106,36 | 0,1949 | 0,1757 |
| Phạt trực tiếp 0,01 | 0,197140 | 0,548204 | 0,050071 | 137,26 | 0,2333 | 0,2071 |
| Phạt trực tiếp 0,025 | 0,196938 | 0,554853 | 0,051046 | 135,78 | 0,2310 | 0,2051 |
| Phạt trực tiếp 0,05 | 0,196540 | 0,565308 | 0,052150 | 133,59 | 0,2277 | 0,2022 |
| Phạt trực tiếp 0,1 | 0,196454 | 0,584075 | 0,054033 | 129,51 | 0,2213 | 0,1966 |
| Phạt trực tiếp 0,25 | 0,194903 | 0,642413 | 0,061307 | 116,25 | 0,1991 | 0,1780 |
| Phạt trực tiếp 0,5 | 0,189494 | 0,738552 | 0,082543 | 93,22 | 0,1548 | 0,1439 |
| Phạt trực tiếp 1 | 0,068383 | 0,984826 | 0,233147 | 10,68 | 0,3096 | 0,3420 |

A_history và A_target là chỉ số phụ. A_history cũng là đại lượng dùng để đặt gate, nên một phần cải thiện của nó là do thiết kế. A_target dùng nhãn validation.

## 6. Cổng phát triển (đặc tả, mục 6)

Cổng dùng ước lượng điểm trên validation seed 42, ε = 10⁻¹². Biên NDCG = 0,95 × 0,197433 = 0,187562.

1. **Cấu hình phổ được xét** (γ₀ > 0, N ≥ biên, E > E nền): γ chung 0,1 và 0,25; γ sai lệch 0,1, 0,25, 0,5 và 0,75. Bị loại vì N dưới biên: γ chung 0,5, 0,75, 1 và γ sai lệch 1.
2. **Đối chứng khả thi** (β > 0, N ≥ biên): β = 0,01; 0,025; 0,05; 0,1; 0,25; 0,5. β = 1 bị loại (N = 0,068383).
3. **Quan hệ trội.** Mỗi cấu hình phổ được xét đều bị trội:

   | Cấu hình phổ | Bị trội bởi phạt trực tiếp |
   | --- | --- |
   | γ chung 0,1 | β = 0,1 |
   | γ chung 0,25 | β = 0,25 |
   | γ sai lệch 0,1 | β = 0,05; 0,1 |
   | γ sai lệch 0,25 | β = 0,1; 0,25 |
   | γ sai lệch 0,5 | β = 0,25 |
   | γ sai lệch 0,75 | β = 0,5 |

   Có β dương khả thi và mọi cấu hình phổ đều bị trội, nên **dừng nhánh phổ** và không tiến sang vòng đối chứng nâng cao. Trường hợp "không có β dương khả thi" ở bước 4 không xảy ra.
4. **Khóa:** không có cấu hình phổ nào (γ chung: không; γ sai lệch: không; đại diện: không).
5. **Đối chứng phạt trực tiếp được khóa:** β = 0,5 (N = 0,189494, E = 0,738552), chọn theo E lớn nhất → N lớn nhất → β nhỏ nhất.

## 7. Bootstrap phát triển cho đối chứng đã khóa

Đây là **bằng chứng phát triển**: cấu hình được chọn và đánh giá trên cùng validation, nên CI không phải mức bảo đảm sau lựa chọn. Bootstrap cặp theo user, B = 10.000, seed 42, 1.865 user. Không có cấu hình phổ nào được khóa nên chỉ tính cho β = 0,5.

| Contrast | Trung bình | Cận dưới một phía 95% | CI hai phía 95% | p một phía |
| --- | --- | --- | --- | --- |
| z_N = a − 0,95·b | 0,001932 | −0,001544 | [−0,002234; 0,006104] | 0,1904 |
| z_E = e − e_nền | 0,193887 | 0,189008 | [0,188097; 0,199732] | 0,0001 (= 1/(B+1)) |

p_joint = max(p_N, p_E) = 0,1904. Cận dưới của z_N âm, nên trên validation đối chứng này **chưa có bằng chứng** không suy giảm NDCG quá 5%, dù điểm ước lượng của nó nằm trong biên.

## 8. Diễn giải và những gì không làm

- Trong vùng NDCG thuộc biên, phạt trực tiếp đạt E và coverage cao hơn cấu hình phổ có NDCG gần bằng. Ví dụ: β = 0,25 có N 0,194903, E 0,642413, coverage 0,0613; γ sai lệch 0,5 có N 0,193040, E 0,610456, coverage 0,0523.
- Giới hạn của kết luận: chỉ một thành phần phổ, một nền ALS, một seed chọn và lưới đã khóa. Các phương pháp phổ khác (nhiều thành phần, điều chuẩn khi huấn luyện như ReSN, phép chiếu theo node như PPD) chưa được kiểm ở đây.
- Theo đặc tả, **không** làm: xác nhận seed 43/44, chấm test, vòng đối chứng 2 (M1 trên ALS, H1-top100, PPD-MF), mở rộng lưới γ hoặc β, đổi metric hay đổi nền.
- Đối chứng phạt trực tiếp không được so trực tiếp hệ số β với M1, vì M1 chuẩn hóa min–max trong top-100.

## 9. Lệnh tái lập

```bash
.venv/Scripts/python.exe -B scripts/run_h1.py --output-dir outputs/runs/h1_round1_validation_seed42_<máy>_<ngày>
```

Cần có `outputs/chinh_thuc_cloud_20261026/` (representations và ba checkpoint ALS) khớp `SHA256SUMS` và lock. Đường dẫn ở [h1.yaml](../../configs/models/h1.yaml). Thư mục output phải chưa tồn tại. Code gồm [spectral.py](../../src/musicrec/recommenders/spectral.py), [direct_penalty.py](../../src/musicrec/recommenders/direct_penalty.py), [exposure.py](../../src/musicrec/evaluation/exposure.py), [h1_gate.py](../../src/musicrec/evaluation/h1_gate.py), [inference.py](../../src/musicrec/evaluation/inference.py) và [run_h1.py](../../scripts/run_h1.py).
