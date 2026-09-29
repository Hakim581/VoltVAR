import pytest

from voltvar.config import load_config
from voltvar.experiment import run_day
from voltvar.forecast import evaluate_forecasts, feature_frame
from voltvar.profiles import history


def test_forecast_features_use_present_and_past_only():
    raw = history(load_config(), days=3)
    altered = raw.copy()
    altered.loc[150:, ["p_mw", "q_mvar"]] *= 10
    a, b = feature_frame(raw), feature_frame(altered)
    assert a.loc[:149].equals(b.loc[:149])


def test_time_split_forecast_trains_and_tests():
    scores, example = evaluate_forecasts(load_config(), days=12)
    assert len(scores) == 12
    assert len(example) == 6
    assert "Persistence" in set(scores.model)
    assert len(set(scores.model)) == 2
    assert (scores.mae >= 0).all() and (scores.rmse >= 0).all()
    assert (scores.train_rows > scores.test_rows).all()


@pytest.mark.slow
def test_96_interval_comparison_has_isolated_state_and_real_energy():
    result = run_day(load_config())
    assert len(result.samples) == 288
    assert result.samples.groupby("controller").size().eq(96).all()
    for _, row in result.summary.iterrows():
        frame = result.samples[result.samples.controller == row.controller]
        assert row.energy_loss_kwh == pytest.approx(frame.p_loss_kw.sum() * 0.25)
    base = result.samples[result.samples.controller == "No Control"]
    assert base.cb_operations.max() == 0 and base.tap_operations.max() == 0
    assert result.samples.groupby("controller").timestamp.apply(tuple).nunique() == 1
