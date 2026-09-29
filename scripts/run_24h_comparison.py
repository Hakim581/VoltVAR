"""Reproduce the 96-interval, three-controller engineering comparison."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from voltvar.config import load_config
from voltvar.experiment import run_day

if __name__ == "__main__":
    result = run_day(load_config())
    print(result.summary.to_string(index=False))
