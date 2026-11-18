"""Run Step 10 only: ItemCF L=40, shrinkage=0 on validation, never test."""

from run_baseline import main

if __name__ == "__main__":
    main("item_cf")
