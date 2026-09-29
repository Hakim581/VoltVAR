"""Stateful local baseline and exhaustive physics-checked Volt/VAR search."""
from dataclasses import dataclass, field
from itertools import product
import math
from typing import Any

from .power import PowerFlowError, is_safe, run_powerflow, set_loads, violation_size


@dataclass
class DeviceState:
    caps: tuple[bool, bool, bool] = (False, False, False)
    tap: int = 0
    minute: int = 0
    cb_last: list[int] = field(default_factory=lambda: [-100000] * 3)
    tap_last: int = -100000
    cb_operations: int = 0
    tap_operations: int = 0
    controller: str = "No Control"
    previous_metrics: dict | None = None


def permitted(state: DeviceState, caps: tuple[bool, bool, bool], tap: int,
              cfg: dict, available: tuple[bool, bool, bool] = (True, True, True),
              tap_locked: bool = False) -> bool:
    op = cfg["operating"]
    bounds = cfg["synthetic"]
    if tap < bounds["tap_min"] or tap > bounds["tap_max"] or abs(tap - state.tap) > op["local_tap_movement"]:
        return False
    changes = sum(a != b for a, b in zip(caps, state.caps))
    if state.cb_operations + changes > op["capacitor_max_daily_operations"]:
        return False
    for i, (old, new) in enumerate(zip(state.caps, caps)):
        if old != new and (not available[i] or state.minute - state.cb_last[i] < op["capacitor_dwell_minutes"]):
            return False
    if tap != state.tap:
        if tap_locked or state.minute - state.tap_last < op["tap_dwell_minutes"]:
            return False
        if state.tap_operations + abs(tap - state.tap) > op["tap_max_daily_operations"]:
            return False
    return True


def advance(state: DeviceState, caps: tuple[bool, bool, bool], tap: int, metrics: dict) -> DeviceState:
    """Return a fresh state, preserving operation times and counts."""
    result = DeviceState(caps=caps, tap=tap, minute=state.minute,
                         cb_last=state.cb_last.copy(), tap_last=state.tap_last,
                         cb_operations=state.cb_operations, tap_operations=state.tap_operations,
                         controller=state.controller, previous_metrics=metrics)
    for i, (old, new) in enumerate(zip(state.caps, caps)):
        if old != new:
            result.cb_last[i] = state.minute
            result.cb_operations += 1
    if tap != state.tap:
        result.tap_last = state.minute
        result.tap_operations += abs(tap - state.tap)
    return result


def objective(metrics: dict, state: DeviceState, caps: tuple[bool, bool, bool], tap: int, cfg: dict) -> dict:
    """Fixed engineering reference scales prevent unit mixing and baseline drift."""
    weights = cfg["objective"]
    parts = {
        "loss": metrics["p_loss_mw"] / 0.20,
        "voltage": metrics["voltage_deviation"] / 0.05,
        "reactive": abs(metrics["q_source_mvar"]) / 3.0,
        "switching": (sum(a != b for a, b in zip(caps, state.caps)) * weights["cb_switch_cost"]
                      + abs(tap - state.tap) * weights["tap_switch_cost"]),
    }
    parts["total"] = sum(weights[key] * parts[key] for key in ("loss", "voltage", "reactive", "switching"))
    return parts


def candidates(state: DeviceState, cfg: dict, available=(True, True, True), tap_locked=False):
    taps = [state.tap] if tap_locked else range(state.tap - 1, state.tap + 2)
    for caps in product((False, True), repeat=3):
        for tap in taps:
            if permitted(state, caps, tap, cfg, available, tap_locked):
                yield caps, tap


def optimize(net, state: DeviceState, scenario: str, cfg: dict, factors: dict | None = None,
             available=(True, True, True), tap_locked=False,
             forecast_factors: dict | None = None, lookahead_weight: float = 0.25) -> dict:
    set_loads(net, scenario, cfg, factors)
    before = run_powerflow(net, state.caps, state.tap, cfg)
    table = []
    for caps, tap in candidates(state, cfg, available, tap_locked):
        try:
            m = run_powerflow(net, caps, tap, cfg)
            score = objective(m, state, caps, tap, cfg)
            if forecast_factors:
                set_loads(net, scenario, cfg, forecast_factors)
                later = run_powerflow(net, caps, tap, cfg)
                score["forecast"] = objective(later, state, caps, tap, cfg)["total"]
                score["total"] += lookahead_weight * score["forecast"]
                set_loads(net, scenario, cfg, factors)
            table.append({"caps": caps, "tap": tap, "metrics": m, "score": score,
                          "safe": is_safe(m, cfg), "violation": violation_size(m, cfg)})
        except PowerFlowError:
            set_loads(net, scenario, cfg, factors)
            table.append({"caps": caps, "tap": tap, "safe": False, "converged": False,
                          "violation": math.inf, "score": {"total": math.inf}})
    if not table:
        raise RuntimeError("No eligible control candidates")
    feasible = [r for r in table if r["safe"]]
    if feasible:
        chosen = min(feasible, key=lambda r: (r["score"]["total"], r["caps"], r["tap"]))
        status = "FEASIBLE"
    else:
        finite = [r for r in table if math.isfinite(r["violation"])]
        if not finite:
            raise PowerFlowError("POWER FLOW DID NOT CONVERGE for all candidates")
        chosen = min(finite, key=lambda r: (r["violation"], r["score"]["total"]))
        status = "CONTINGENCY / BEST AVAILABLE RECOMMENDATION"
    held = next((r for r in table if r["caps"] == state.caps and r["tap"] == state.tap), None)
    if (held and held["safe"] and chosen["safe"] and
            held["score"]["total"] - chosen["score"]["total"] < cfg["objective"]["minimum_improvement"]):
        chosen = held
    after = run_powerflow(net, chosen["caps"], chosen["tap"], cfg)
    reason = explain(before, after, state, chosen, table, status)
    return {"before": before, "after": after, "selected": chosen,
            "candidates": table, "status": status, "explanation": reason,
            "state": advance(state, chosen["caps"], chosen["tap"], after)}


def explain(before: dict, after: dict, state: DeviceState, chosen: dict, table: list, status: str) -> str:
    changed = [f"CB{i+1} {'ON' if on else 'OFF'}" for i, (old, on) in enumerate(zip(state.caps, chosen["caps"])) if old != on]
    if chosen["tap"] != state.tap:
        changed.append(f"OLTC tap {state.tap} → {chosen['tap']}")
    action = ", ".join(changed) if changed else "Qurğular olduğu kimi saxlanır"
    alternatives = [row for row in table if row is not chosen]
    if alternatives:
        other = min(alternatives, key=lambda r: (not r["safe"], r["violation"], r["score"]["total"]))
        other_state = "/".join("ON" if on else "OFF" for on in other["caps"])
        other_reason = ("iş sərhədlərini pozur" if not other["safe"] else
                        f"balı {other['score']['total']:.3f} ilə daha yüksəkdir")
        rejected_text = f"CB {other_state}, tap {other['tap']} variantı {other_reason}; cəmi {len(alternatives)} alternativ müqayisə edildi"
    else:
        rejected_text = "başqa uyğun keçid yoxdur"
    return (f"NƏ: {action}. SƏBƏB: mövcud yükdə şəbəkə üzrə AC power flow və çoxməqsədli bal qiymətləndirildi. "
            f"TƏSİR: itki {before['p_loss_mw']*1000:.1f} → {after['p_loss_mw']*1000:.1f} kW; "
            f"mənbə Q {before['q_source_mvar']:.2f} → {after['q_source_mvar']:.2f} MVAr; "
            f"Vmin {before['vmin_pu']:.3f} → {after['vmin_pu']:.3f} pu. "
            f"RƏDD EDİLƏN: {rejected_text}. Status: {status}.")


def traditional(net, state: DeviceState, scenario: str, cfg: dict, factors: dict | None = None,
                available=(True, True, True), tap_locked=False) -> dict:
    """Independent local thresholds, with the same physical operation limits."""
    set_loads(net, scenario, cfg, factors)
    before = run_powerflow(net, state.caps, state.tap, cfg)
    caps = list(state.caps)
    if before["q_source_mvar"] < -0.02 or before["vmax_pu"] > 1.035:
        options = [i for i, on in enumerate(caps) if on]
        if options:
            caps[options[-1]] = False
    elif before["source_pf"] < 0.94 and before["q_source_mvar"] > 0:
        options = [i for i, on in enumerate(caps) if not on and available[i]]
        if options:
            caps[options[0]] = True
    tap = state.tap
    if before["vmin_pu"] < 0.965:
        tap -= 1  # verified HV tap direction in tests
    elif before["vmax_pu"] > 1.035:
        tap += 1
    target = tuple(caps)
    if not permitted(state, target, tap, cfg, available, tap_locked):
        if permitted(state, target, state.tap, cfg, available, tap_locked):
            tap = state.tap
        else:
            target, tap = state.caps, state.tap
    after = run_powerflow(net, target, tap, cfg)
    return {"before": before, "after": after, "state": advance(state, target, tap, after)}
