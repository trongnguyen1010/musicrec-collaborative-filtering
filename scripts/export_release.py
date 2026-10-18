"""Export the validation-selected models after locked test evaluation succeeds."""

import argparse

from musicrec.artifacts.release import export_release
from musicrec.configuration import ROOT

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", required=True)
    parser.add_argument("--data-run", required=True)
    parser.add_argument("--destination", default="artifacts/releases/v0.2.0")
    args = parser.parse_args()
    print(export_release(ROOT / args.study, ROOT / args.data_run, ROOT / args.destination))
