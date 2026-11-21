"""Chỉ chạy Bước 11: một cấu hình SVD có độ lệch, chọn vòng lặp trên tập xác thực."""

import os

for variable in ["OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "BLIS_NUM_THREADS"]:
    os.environ[variable] = "1"

from run_baseline import main  # noqa: E402

if __name__ == "__main__":
    main("svd")
