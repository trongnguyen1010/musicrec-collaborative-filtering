"""Guard release export until the experiment has real, evaluated metrics."""

import json
from pathlib import Path

METRICS_FILE = Path("outputs/metrics.json")


def main() -> None:
    metrics = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
    if metrics.get("status") == "not_evaluated":
        raise RuntimeError("Cannot export a release before the shared evaluator records real metrics")
    raise NotImplementedError("Release packaging is enabled after the first evaluated model")


if __name__ == "__main__":
    main()
