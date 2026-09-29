"""Configuration loading and explicit engineering input checks."""
from pathlib import Path
import yaml

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "config.yaml"


def load_config(path: str | Path = DEFAULT_CONFIG) -> dict:
    with Path(path).open(encoding="utf-8") as stream:
        cfg = yaml.safe_load(stream)
    op, obj, synthetic = cfg["operating"], cfg["objective"], cfg["synthetic"]
    if not 0 < op["voltage_min_pu"] < op["voltage_max_pu"]:
        raise ValueError("Invalid simulation voltage bounds")
    if op["max_loading_percent"] <= 0 or any(op[k] < 0 for k in ("capacitor_dwell_minutes", "tap_dwell_minutes", "capacitor_max_daily_operations", "tap_max_daily_operations")):
        raise ValueError("Invalid switching or loading limit")
    if synthetic["tap_min"] >= synthetic["tap_max"] or synthetic["tap_step_percent"] <= 0:
        raise ValueError("Invalid OLTC range")
    if len(synthetic["capacitors"]) != 3 or any(c["mvar"] <= 0 for c in synthetic["capacitors"]):
        raise ValueError("Three positive capacitor sizes required")
    if any(obj[k] < 0 for k in ("loss", "voltage", "reactive", "switching", "cb_switch_cost", "tap_switch_cost", "minimum_improvement")) or sum(obj[k] for k in ("loss", "voltage", "reactive", "switching")) <= 0:
        raise ValueError("Invalid objective weights")
    for name, scenario in cfg["scenarios"].items():
        if scenario["load_factor"] <= 0 or scenario["motor_factor"] <= 0 or not 0 < scenario["motor_pf"] <= 1:
            raise ValueError(f"Invalid scenario: {name}")
    return cfg
