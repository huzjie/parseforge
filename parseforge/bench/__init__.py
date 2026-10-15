"""OmniDocBench-style evaluation for structured document parsing."""
from .metrics import (
    region_accuracy,
    cell_accuracy,
    series_mse,
    json_structure_f1,
)
from .omnidocbench import OmniDocBench, run_bench, run_train_demo

__all__ = [
    "region_accuracy",
    "cell_accuracy",
    "series_mse",
    "json_structure_f1",
    "OmniDocBench",
    "run_bench",
    "run_train_demo",
]
