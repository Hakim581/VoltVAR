"""Leakage-safe short-horizon synthetic load forecasting."""
import math
import numpy as np
import pandas as pd

from .profiles import history

HORIZONS = (1, 2, 4)  # 15, 30, 60 minutes


def _model_prediction(train_x, train_y, test_x, seed: int):
    """Use sklearn where loadable; a transparent trained ridge fallback on locked hosts."""
    try:
        from sklearn.ensemble import HistGradientBoostingRegressor
    except Exception:  # locked Windows hosts may reject a compiled sklearn extension
        x = train_x.to_numpy(dtype=float)
        z = test_x.to_numpy(dtype=float)
        mean, std = x.mean(axis=0), x.std(axis=0)
        std[std < 1e-9] = 1.0
        x = np.column_stack((np.ones(len(x)), (x - mean) / std))
        z = np.column_stack((np.ones(len(z)), (z - mean) / std))
        penalty = np.eye(x.shape[1]) * 2.0
        penalty[0, 0] = 0.0
        coefficients = np.linalg.solve(x.T @ x + penalty, x.T @ train_y.to_numpy())
        return "Ridge (NumPy fallback)", z @ coefficients
    model = HistGradientBoostingRegressor(max_iter=80, max_leaf_nodes=15, random_state=seed)
    model.fit(train_x, train_y)
    return "HistGradientBoosting", model.predict(test_x)


def feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    t = pd.to_datetime(frame.timestamp)
    hour = t.dt.hour + t.dt.minute / 60
    features = pd.DataFrame({
        "hour_sin": np.sin(hour * 2 * np.pi / 24),
        "hour_cos": np.cos(hour * 2 * np.pi / 24),
        "dow": t.dt.dayofweek,
        "weekend": (t.dt.dayofweek >= 5).astype(int),
    })
    for target in ("p_mw", "q_mvar"):
        for lag in (0, 1, 2, 4, 96):
            features[f"{target}_lag{lag}"] = frame[target].shift(lag)
        features[f"{target}_mean4"] = frame[target].rolling(4).mean()
        features[f"{target}_std4"] = frame[target].rolling(4).std()
    return features


def evaluate_forecasts(cfg: dict, days: int = 70, seed: int = 123) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = history(cfg, days=days, seed=seed)
    feature = feature_frame(raw)
    results = []
    example = []
    for horizon in HORIZONS:
        for target in ("p_mw", "q_mvar"):
            y = raw[target].shift(-horizon)
            valid = feature.notna().all(axis=1) & y.notna()
            x, y, current = feature.loc[valid], y.loc[valid], raw.loc[valid, target]
            split = int(len(x) * 0.8)  # time ordered, no shuffle
            train_x, test_x = x.iloc[:split], x.iloc[split:]
            train_y, test_y = y.iloc[:split], y.iloc[split:]
            model_name, model_prediction = _model_prediction(train_x, train_y, test_x, seed)
            predictions = {
                "Persistence": current.iloc[split:].to_numpy(),
                model_name: model_prediction,
            }
            scores = {}
            for name, prediction in predictions.items():
                mae = float(np.mean(np.abs(test_y.to_numpy() - prediction)))
                rmse = float(math.sqrt(np.mean((test_y.to_numpy() - prediction) ** 2)))
                scores[name] = mae
                results.append({"horizon_min": horizon * 15, "target": target, "model": name,
                                "mae": mae, "rmse": rmse, "train_rows": len(train_x), "test_rows": len(test_x)})
            winner = min(scores, key=scores.get)
            example.append({"horizon_min": horizon * 15, "target": target, "selected": winner,
                            "latest_actual": float(current.iloc[-1]),
                            "next_forecast": float(predictions[winner][-1]),
                            "last_test_actual": float(test_y.iloc[-1])})
    return pd.DataFrame(results), pd.DataFrame(example)
