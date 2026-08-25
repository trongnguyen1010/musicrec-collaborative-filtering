"""Create a metrics placeholder; replace with shared evaluator in model milestones."""

import json
from pathlib import Path

OUTPUT_FILE = Path("outputs/metrics.json")


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(
            {
                "status": "not_evaluated",
                "message": "Implement the shared evaluator before reporting thesis metrics.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
