"""Validate the minimum provenance information for a serving artifact."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReleaseManifest:
    """Metadata required to trace a deployed model back to an experiment."""

    model_version: str
    git_sha: str
    data_version: str
    mlflow_run_id: str
    seed: int

    def validate(self) -> None:
        if not all((self.model_version, self.git_sha, self.data_version, self.mlflow_run_id)):
            raise ValueError("release manifest has missing provenance fields")
