"""The brief's sequential live demo, evaluated with actual AC power flow."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from voltvar.config import load_config
from voltvar.network import build_network
from voltvar.power import run_powerflow, set_loads
from voltvar.control import DeviceState, optimize, traditional
from voltvar.experiment import run_day
from voltvar.forecast import evaluate_forecasts


def compact(m):
    return {k: round(m[k], 5) for k in ("p_source_mw", "q_source_mvar", "source_pf", "p_loss_mw", "vmin_pu", "vmax_pu", "peak_line_current_ka", "max_trafo_loading_percent")}


def main():
    cfg = load_config()
    net = build_network("synthetic", cfg)
    state = DeviceState(controller="VoltVAR AI")
    set_loads(net, "normal", cfg)
    normal = run_powerflow(net, state.caps, state.tap, cfg)
    heavy = optimize(net, state, "heavy", cfg)
    state = heavy["state"]
    state.minute = 45  # allow the configured 30-minute capacitor dwell to elapse
    reduction = optimize(net, state, "reduction", cfg)
    state = reduction["state"]
    state.minute = 45
    unavailable = optimize(net, state, "heavy", cfg, available=(False, True, True))
    locked = optimize(net, state, "heavy", cfg, tap_locked=True)
    daily = run_day(cfg)
    ieee = build_network("ieee33", cfg)
    ieee_base = optimize(ieee, DeviceState(controller="VoltVAR AI"), "normal", cfg)
    ieee_local = traditional(ieee, DeviceState(controller="Traditional"), "normal", cfg)
    forecast_scores, forecast_example = evaluate_forecasts(cfg)
    output = {
        "normal": compact(normal),
        "heavy_before": compact(heavy["before"]), "heavy_after": compact(heavy["after"]),
        "heavy_action": {"caps": heavy["state"].caps, "tap": heavy["state"].tap, "status": heavy["status"], "candidate_count": len(heavy["candidates"])},
        "reduction_before": compact(reduction["before"]), "reduction_after": compact(reduction["after"]),
        "reduction_action": {"caps": reduction["state"].caps, "tap": reduction["state"].tap, "status": reduction["status"]},
        "unavailable_action": {"caps": unavailable["state"].caps, "tap": unavailable["state"].tap},
        "locked_action": {"caps": locked["state"].caps, "tap": locked["state"].tap},
        "daily_comparison": daily.summary.to_dict(orient="records"),
        "ieee33_before": compact(ieee_base["before"]), "ieee33_after": compact(ieee_base["after"]),
        "ieee33_traditional": compact(ieee_local["after"]),
        "ieee33_status": ieee_base["status"],
        "forecast_scores": forecast_scores.to_dict(orient="records"),
        "forecast_example": forecast_example.to_dict(orient="records"),
    }
    path = Path(__file__).resolve().parents[1] / "data" / "generated"
    path.mkdir(parents=True, exist_ok=True)
    (path / "acceptance.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    daily.samples.to_csv(path / "day_samples.csv", index=False)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
