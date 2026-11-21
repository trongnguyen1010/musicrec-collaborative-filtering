"""Kiểm tra thông tin nguồn gốc tối thiểu của một gói mô hình phục vụ."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReleaseManifest:
    """Siêu dữ liệu cần để truy ngược mô hình đang chạy về đúng lần thực nghiệm."""

    model_version: str
    git_sha: str
    data_version: str
    mlflow_run_id: str
    seed: int

    def validate(self) -> None:
        if not all((self.model_version, self.git_sha, self.data_version, self.mlflow_run_id)):
            raise ValueError("release manifest has missing provenance fields")
