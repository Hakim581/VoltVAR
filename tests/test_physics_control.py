import math
import pytest

from voltvar.config import load_config
from voltvar.control import DeviceState, advance, optimize, permitted, traditional
from voltvar.network import build_network
from voltvar.power import run_powerflow, set_loads
from voltvar.profiles import day_profile


@pytest.fixture(scope="module")
def cfg():
    return load_config()


def test_both_networks_build_and_converge(cfg):
    for name, buses in (("synthetic", 16), ("ieee33", 34)):
        net = build_network(name, cfg)
        set_loads(net, "normal", cfg)
        result = run_powerflow(net, (False,) * 3, 0, cfg)
        assert len(net.bus) == buses
        assert result["converged"]
        assert len(net["_voltvar"]["capacitors"]) == 3


def test_power_balance_and_loss_result(cfg):
    net = build_network("synthetic", cfg)
    set_loads(net, "normal", cfg)
    result = run_powerflow(net, (False,) * 3, 0, cfg)
    assert abs(result["p_balance_error_mw"]) < 1e-5
    assert result["p_loss_mw"] == pytest.approx(net.res_line.pl_mw.sum() + net.res_trafo.pl_mw.sum())
    assert result["source_pf"] == pytest.approx(abs(result["p_source_mw"]) / math.hypot(result["p_source_mw"], result["q_source_mvar"]))


def test_capacitor_sign_is_verified_by_ac_flow(cfg):
    net = build_network("synthetic", cfg)
    set_loads(net, "heavy", cfg)
    off = run_powerflow(net, (False,) * 3, 0, cfg)
    on = run_powerflow(net, (True, False, False), 0, cfg)
    assert net.shunt.q_mvar.iloc[0] < 0
    assert on["capacitor_injection_mvar"] > 0
    assert on["q_source_mvar"] < off["q_source_mvar"]


def test_hv_tap_direction_is_verified_by_ac_flow(cfg):
    net = build_network("synthetic", cfg)
    set_loads(net, "normal", cfg)
    low_tap = run_powerflow(net, (False,) * 3, -1, cfg)
    neutral = run_powerflow(net, (False,) * 3, 0, cfg)
    high_tap = run_powerflow(net, (False,) * 3, 1, cfg)
    assert low_tap["vmin_pu"] > neutral["vmin_pu"] > high_tap["vmin_pu"]


def test_heavy_load_physically_degrades_network(cfg):
    net = build_network("synthetic", cfg)
    set_loads(net, "normal", cfg)
    normal = run_powerflow(net, (False,) * 3, 0, cfg)
    set_loads(net, "heavy", cfg)
    heavy = run_powerflow(net, (False,) * 3, 0, cfg)
    assert heavy["q_source_mvar"] > normal["q_source_mvar"]
    assert heavy["source_pf"] < normal["source_pf"]
    assert heavy["p_loss_mw"] > normal["p_loss_mw"]
    assert heavy["vmin_pu"] < normal["vmin_pu"]


def test_heavy_optimizer_selects_best_eligible_safe_score(cfg):
    net = build_network("synthetic", cfg)
    result = optimize(net, DeviceState(), "heavy", cfg)
    safe = [r for r in result["candidates"] if r["safe"]]
    assert safe
    assert result["selected"]["score"]["total"] == pytest.approx(min(r["score"]["total"] for r in safe))
    assert result["after"]["p_loss_mw"] < result["before"]["p_loss_mw"]
    assert result["after"]["vmin_pu"] > result["before"]["vmin_pu"]
    assert len(result["candidates"]) > 1


def test_reduction_decompensates_when_dwell_elapsed(cfg):
    net = build_network("synthetic", cfg)
    heavy = optimize(net, DeviceState(), "heavy", cfg)
    state = heavy["state"]
    state.minute = 45
    reduced = optimize(net, state, "reduction", cfg)
    assert sum(reduced["state"].caps) < sum(state.caps)
    assert reduced["before"]["q_source_mvar"] < 0
    assert reduced["after"]["q_source_mvar"] > reduced["before"]["q_source_mvar"]


def test_unavailable_bank_and_locked_tap_cannot_move(cfg):
    net = build_network("synthetic", cfg)
    state = DeviceState()
    result = optimize(net, state, "heavy", cfg, available=(False, True, True), tap_locked=True)
    assert all(not r["caps"][0] and r["tap"] == state.tap for r in result["candidates"])
    assert not result["state"].caps[0]
    assert result["state"].tap == state.tap


def test_dwell_and_daily_switching_limits(cfg):
    state = DeviceState(caps=(True, False, False), minute=15, cb_last=[0, -100000, -100000])
    assert not permitted(state, (False, False, False), 0, cfg)
    state.minute = 30
    assert permitted(state, (False, False, False), 0, cfg)
    state.cb_operations = cfg["operating"]["capacitor_max_daily_operations"]
    assert not permitted(state, (False, False, False), 0, cfg)


def test_state_counts_actual_changes(cfg):
    state = DeviceState(minute=60)
    changed = advance(state, (True, False, True), -1, {"p_loss_mw": 0.1})
    assert changed.cb_operations == 2
    assert changed.tap_operations == 1
    assert changed.cb_last == [60, -100000, 60]
    assert changed.tap_last == 60


def test_traditional_uses_actual_ac_result(cfg):
    net = build_network("synthetic", cfg)
    result = traditional(net, DeviceState(), "heavy", cfg)
    assert result["after"]["converged"]
    assert result["state"].cb_operations <= 1
    assert abs(result["after"]["p_balance_error_mw"]) < 1e-5


def test_seeded_profiles_and_physical_reactive_relation(cfg):
    a, b, c = day_profile(42), day_profile(42), day_profile(43)
    assert len(a) == 96
    assert a.equals(b)
    assert not a.equals(c)
    assert a.residential.iloc[78] > a.residential.iloc[52]
