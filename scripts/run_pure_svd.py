"""Chạy PureSVD hạng 32 cố định trên tập xác thực: đối chứng điểm đại diện hoặc kiểm tra
nhị phân/log ở Bước 13.
"""

import os

for variable in ["OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "BLIS_NUM_THREADS"]:
    os.environ[variable] = "1"

from run_baseline import main  # noqa: E402

if __name__ == "__main__":
    main("pure_svd")
