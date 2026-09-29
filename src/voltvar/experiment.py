"""Fair 96-step comparisons: independent controllers, identical seeded load inputs."""
from dataclasses import dataclass
import pandas as pd

from .control import DeviceState, optimize, traditional
from .network import build_network
from .power import run_powerflow, set_loads
from .profiles import day_profile


@dataclass
class DayResult:
    samples: pd.DataFrame
    summary: pd.DataFrame


def run_day(cfg: dict, model: str = "synthetic", scenario: str = "normal",
            seed: int | None = None) -> DayResult:
    profile = day_profile(cfg["profile"]["seed"] if seed is None else seed)
    records = []
    for label in ("No Control", "Traditional", "VoltVAR AI"):
        net = build_network(model, cfg)
        state = DeviceState(controller=label)
        for step, row in profile.iterrows():
            state.minute = int(step * cfg["profile"]["minutes"])
            factors = {k: float(row[k]) for k in ("residential", "commercial", "industrial", "motor")}
            if label == "No Control":
                set_loads(net, scenario, cfg, factors)
                metrics = run_powerflow(net, state.caps, state.tap, cfg)
                state.previous_metrics = metrics
            elif label == "Traditional":
                outcome = traditional(net, state, scenario, cfg, factors)
                state, metrics = outcome["state"], outcome["after"]
            else:
                outcome = optimize(net, state, scenario, cfg, factors)
                state, metrics = outcome["state"], outcome["after"]
            records.append({"timestamp": row.timestamp, "controller": label,
                            "p_loss_kw": metrics["p_loss_mw"] * 1000,
                            "q_source_mvar": metrics["q_source_mvar"],
                            "source_pf": metrics["source_pf"],
                            "vmin_pu": metrics["vmin_pu"], "vmax_pu": metrics["vmax_pu"],
                            "voltage_violations": metrics["voltage_violations"],
                            "max_loading_percent": max(metrics["max_line_loading_percent"], metrics["max_trafo_loading_percent"]),
                            "cb_operations": state.cb_operations, "tap_operations": state.tap_operations,
                            "cb1": state.caps[0], "cb2": state.caps[1], "cb3": state.caps[2], "tap": state.tap})
    samples = pd.DataFrame(records)
    summary = samples.groupby("controller", sort=False).agg(
        energy_loss_kwh=("p_loss_kw", lambda s: s.sum() * cfg["profile"]["minutes"] / 60),
        mean_source_pf=("source_pf", "mean"), min_voltage_pu=("vmin_pu", "min"),
        max_voltage_pu=("vmax_pu", "max"),
        violation_intervals=("voltage_violations", lambda s: int((s > 0).sum())),
        max_loading_percent=("max_loading_percent", "max"),
        cb_operations=("cb_operations", "max"), tap_operations=("tap_operations", "max"),
    ).reset_index()
    return DayResult(samples, summary)
