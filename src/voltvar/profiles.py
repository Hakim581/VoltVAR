"""Seeded 15-minute load profiles; Q always follows P and assumed PF."""
import math
import numpy as np
import pandas as pd


def day_profile(seed: int = 42, date: str = "2026-01-15") -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    hours = np.arange(96) / 4
    residential = 0.66 + 0.29 * np.exp(-((hours - 7.5) / 2.0) ** 2) + 0.53 * np.exp(-((hours - 19.5) / 3.0) ** 2)
    commercial = 0.47 + 0.78 / (1 + np.exp(-(hours - 8))) - 0.72 / (1 + np.exp(-(hours - 18)))
    industrial = 0.79 + 0.29 / (1 + np.exp(-(hours - 7))) - 0.24 / (1 + np.exp(-(hours - 19)))
    motor = 0.80 + 0.36 / (1 + np.exp(-(hours - 8))) - 0.30 / (1 + np.exp(-(hours - 18)))
    data = {"timestamp": pd.date_range(date, periods=96, freq="15min")}
    for kind, shape in (("residential", residential), ("commercial", commercial), ("industrial", industrial), ("motor", motor)):
        data[kind] = np.maximum(0.25, shape * (1 + rng.normal(0, 0.018, 96)))
    return pd.DataFrame(data)


def history(cfg: dict, days: int = 70, seed: int = 123) -> pd.DataFrame:
    """Separate synthetic history for forecasting; not operational telemetry."""
    rows = []
    rng = np.random.default_rng(seed)
    for day in range(days):
        date = pd.Timestamp("2026-01-01") + pd.Timedelta(days=day)
        profile = day_profile(seed + day, date.strftime("%Y-%m-%d"))
        weekend = 0.89 if date.dayofweek >= 5 else 1.0
        drift = 1 + 0.07 * math.sin(2 * math.pi * day / 35)
        for _, factor in profile.iterrows():
            p = q = 0.0
            for _, kind, base_p, pf in cfg["synthetic"]["loads"]:
                k = float(factor[kind]) * weekend * drift
                p += base_p * k
                q += base_p * k * math.tan(math.acos(pf))
            p *= 1 + rng.normal(0, 0.008)
            q *= 1 + rng.normal(0, 0.012)
            rows.append((factor.timestamp, p, q))
    return pd.DataFrame(rows, columns=["timestamp", "p_mw", "q_mvar"])
