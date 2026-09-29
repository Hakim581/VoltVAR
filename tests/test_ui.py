"""Presentation interpretation checks against backend-provided values."""

from voltvar.config import load_config
from voltvar.ui.interpretation import COMPARISON_KEYS, change_lines, comparison_rows, operating_status
from voltvar.ui.text import GLOSSARY, METRICS, SCENARIOS, STEPS, T


def test_workflow_and_terms():
    assert len(STEPS) == 4
    assert len(SCENARIOS) == 4
    assert T["on"] == "Qoşulu" and T["off"] == "Açıq"
    assert "reaktiv güc" in METRICS["q_source_mvar"][0].lower()
    assert "YAGT" in GLOSSARY
    assert len(GLOSSARY) >= 15


def test_interpretation_uses_supplied_values_only():
    before = {"p_loss_mw": 0.1234, "q_source_mvar": 2.10, "source_pf": 0.810,
              "vmin_pu": 0.940, "vmax_pu": 1.01, "peak_line_current_ka": 0.320,
              "max_line_loading_percent": 50, "max_trafo_loading_percent": 70,
              "voltage_violations": 1}
    after = before | {"p_loss_mw": 0.1004, "q_source_mvar": 1.55, "source_pf": 0.910,
                      "vmin_pu": 0.960, "voltage_violations": 0}
    rows = comparison_rows(before, after, load_config())
    assert len(rows) == len(COMPARISON_KEYS) == 7
    assert rows[0][T["result_columns"][1]] == "123.4 kW"
    assert rows[0][T["result_columns"][2]] == "100.4 kW"
    assert rows[0][T["result_columns"][3]] == "-23.0 kW"
    assert "2.10 MVAr → 1.55 MVAr" in change_lines(before, after)[0]
    assert operating_status(before, load_config()) == T["outside_status"]
    assert operating_status(after, load_config()) == T["normal_status"]
