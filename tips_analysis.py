"""Helpers for the Seaborn `tips` dataset (restaurant bills and tips, 244 meals).

`tips.csv` is the output of ``seaborn.load_dataset("tips")`` used in the notebook, saved so the
dashboard does not need to download it.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

DATA_PATH = Path(__file__).resolve().parent / "tips.csv"
ORDER = {"day": ["Thur", "Fri", "Sat", "Sun"], "time": ["Lunch", "Dinner"], "sex": ["Male", "Female"],
         "smoker": ["Yes", "No"]}


def load_tips(path: str | Path = DATA_PATH) -> pd.DataFrame:
    if Path(path).exists():
        df = pd.read_csv(path)
    else:  # same source as the notebook
        import seaborn as sns
        df = sns.load_dataset("tips")
    for col, cats in ORDER.items():
        df[col] = pd.Categorical(df[col].astype(str), categories=cats)
    df["tip_pct"] = df["tip"] / df["total_bill"] * 100
    return df


def group_summary(df: pd.DataFrame, by: str, metric: str) -> pd.DataFrame:
    """Mean, 95% CI and count of `metric` per group."""
    rows = []
    for name, g in df.groupby(by, observed=True):
        x = g[metric].dropna()
        if len(x) == 0:
            continue
        half = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else np.nan
        rows.append({by: name, "mean": x.mean(), "low": x.mean() - half, "high": x.mean() + half, "n": len(x)})
    return pd.DataFrame(rows)


def compare_groups(df: pd.DataFrame, by: str, metric: str) -> dict | None:
    """Welch t-test for two groups, one-way ANOVA for more. None if fewer than two usable groups."""
    groups = [g[metric].dropna().values for _, g in df.groupby(by, observed=True) if g[metric].notna().sum() > 1]
    if len(groups) < 2:
        return None
    if len(groups) == 2:
        res = stats.ttest_ind(groups[0], groups[1], equal_var=False)
        return {"test": "Welch t-test", "statistic": float(res.statistic), "p": float(res.pvalue)}
    res = stats.f_oneway(*groups)
    return {"test": "one-way ANOVA", "statistic": float(res.statistic), "p": float(res.pvalue)}


def bill_tip_relationship(df: pd.DataFrame) -> dict | None:
    if len(df) < 3:
        return None
    r = stats.pearsonr(df["total_bill"], df["tip"])
    slope, intercept = np.polyfit(df["total_bill"], df["tip"], 1)
    return {"r": float(r.statistic), "p": float(r.pvalue), "slope": float(slope), "intercept": float(intercept)}
