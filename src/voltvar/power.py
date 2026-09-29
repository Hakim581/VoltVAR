"""AC power flow and quantities read directly from pandapower results."""
import math
import numpy as np
import pandapower as pp


class PowerFlowError(RuntimeError):
    """Explicit failure instead of an invented or stale network result."""


def set_loads(net, scenario: str, cfg: dict, factors: dict | None = None):
    definition = cfg["scenarios"][scenario]
    factors = factors or {}
    for idx, row in net.load.iterrows():
        kind = row["category"]
        base = float(row["base_mw"])
        multiplier = definition["load_factor"] * factors.get(kind, 1.0) * factors.get("_p_scale", 1.0)
        pf = float(row["base_pf"])
        if kind == "motor":
            multiplier *= definition["motor_factor"]
            pf = definition["motor_pf"]
        p = base * multiplier
        net.load.at[idx, "p_mw"] = p
        net.load.at[idx, "q_mvar"] = p * math.tan(math.acos(pf)) * factors.get("_q_scale", 1.0)


def apply_devices(net, caps: tuple[bool, bool, bool], tap: int):
    for idx, on in zip(net["_voltvar"]["capacitors"], caps):
        net.shunt.at[idx, "in_service"] = bool(on)
    net.trafo.at[net.trafo.index[0], "tap_pos"] = int(tap)


def run_powerflow(net, caps: tuple[bool, bool, bool], tap: int, cfg: dict) -> dict:
    apply_devices(net, caps, tap)
    try:
        pp.runpp(net, algorithm="nr", max_iteration=30, tolerance_mva=1e-8,
                 init="flat", numba=False, calculate_voltage_angles=True)
    except (pp.LoadflowNotConverged, ValueError, FloatingPointError) as exc:
        raise PowerFlowError("POWER FLOW DID NOT CONVERGE") from exc
    if not net.converged:
        raise PowerFlowError("POWER FLOW DID NOT CONVERGE")
    vm = net.res_bus.vm_pu.to_numpy(dtype=float)
    if not np.isfinite(vm).all():
        raise PowerFlowError("POWER FLOW DID NOT CONVERGE: non-finite voltage")
    p_source = float(net.res_ext_grid.p_mw.sum())
    q_source = float(net.res_ext_grid.q_mvar.sum())
    apparent = math.hypot(p_source, q_source)
    p_loss = float(net.res_line.pl_mw.sum() + net.res_trafo.pl_mw.sum())
    q_loss = float(net.res_line.ql_mvar.sum() + net.res_trafo.ql_mvar.sum())
    lower, upper = cfg["operating"]["voltage_min_pu"], cfg["operating"]["voltage_max_pu"]
    line_loading = float(net.res_line.loading_percent.max()) if len(net.res_line) else 0.0
    trafo_loading = float(net.res_trafo.loading_percent.max()) if len(net.res_trafo) else 0.0
    cap_q = -float(net.res_shunt.q_mvar.sum()) if len(net.res_shunt) else 0.0
    p_load = float(net.res_load.p_mw.sum())
    p_shunt = float(net.res_shunt.p_mw.sum()) if len(net.res_shunt) else 0.0
    return {
        "converged": True, "p_source_mw": p_source, "q_source_mvar": q_source,
        "source_pf": abs(p_source) / apparent if apparent > 1e-12 else 1.0,
        "p_loss_mw": p_loss, "q_loss_mvar": q_loss,
        "vmin_pu": float(vm.min()), "vmax_pu": float(vm.max()),
        "vmean_pu": float(vm.mean()), "voltage_deviation": float(np.mean(np.abs(vm - 1.0))),
        "voltage_violations": int(((vm < lower) | (vm > upper)).sum()),
        "max_line_loading_percent": line_loading,
        "max_trafo_loading_percent": trafo_loading,
        "peak_line_current_ka": float(net.res_line.i_ka.max()) if len(net.res_line) else 0.0,
        "capacitor_injection_mvar": cap_q, "tap": int(tap),
        "p_balance_error_mw": p_source - p_load - p_shunt - p_loss,
        "bus_voltages": vm.tolist(),
        "bus_angles_deg": net.res_bus.va_degree.to_list(),
        "line_loading_percent": net.res_line.loading_percent.to_list(),
        "powerflow_iterations": net.get("_ppc", {}).get("iterations"),
    }


def is_safe(metrics: dict, cfg: dict) -> bool:
    op = cfg["operating"]
    return (metrics["voltage_violations"] == 0 and
            metrics["max_line_loading_percent"] <= op["max_loading_percent"] and
            metrics["max_trafo_loading_percent"] <= op["max_loading_percent"] and
            metrics["q_source_mvar"] >= -0.05)


def violation_size(metrics: dict, cfg: dict) -> float:
    op = cfg["operating"]
    vm = np.asarray(metrics["bus_voltages"])
    voltage = np.maximum(op["voltage_min_pu"] - vm, 0).sum() + np.maximum(vm - op["voltage_max_pu"], 0).sum()
    overload = max(0, metrics["max_line_loading_percent"] - op["max_loading_percent"]) / 100
    overload += max(0, metrics["max_trafo_loading_percent"] - op["max_loading_percent"]) / 100
    reverse_q = max(0, -0.05 - metrics["q_source_mvar"])
    return float(voltage * 10 + overload + reverse_q)
