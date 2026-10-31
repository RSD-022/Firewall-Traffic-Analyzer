"""Statistical tests and data-quality helpers — pure pandas/scipy, no Streamlit imports.

Functions operate on the full 12-column firewall DataFrame (data/raw/log2.csv).
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, gaussian_kde, kruskal


# ---------------------------------------------------------------------------
# Data-quality helpers
# ---------------------------------------------------------------------------

ALL_COLUMNS = [
    "Source Port", "Destination Port", "NAT Source Port", "NAT Destination Port",
    "Action", "Bytes", "Bytes Sent", "Bytes Received", "Packets",
    "Elapsed Time (sec)", "pkts_sent", "pkts_received",
]


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Drop exact duplicate rows (all 12 columns)."""
    return df.drop_duplicates()


def duplicate_summary(df: pd.DataFrame) -> dict[str, int]:
    """Return counts related to duplicate rows.

    Keys:
      extra_copies   – rows beyond the first occurrence (keep='first')
      rows_in_groups – rows that belong to any repeated group (keep=False)
      distinct_rows  – unique rows after deduplication
    """
    extra_copies = int(df.duplicated(keep="first").sum())
    rows_in_groups = int(df.duplicated(keep=False).sum())
    distinct_rows = len(df) - extra_copies
    return {
        "extra_copies": extra_copies,
        "rows_in_groups": rows_in_groups,
        "distinct_rows": distinct_rows,
    }


def conflicting_label_groups(df: pd.DataFrame) -> pd.DataFrame:
    """Identify feature-vector groups that carry more than one Action label.

    Returns a DataFrame with the 11 feature columns, a 'num_actions' column,
    and a 'total_rows' column for each conflicting group.
    """
    feature_cols = [c for c in df.columns if c != "Action"]
    grouped = df.groupby(feature_cols, sort=False).agg(
        num_actions=("Action", "nunique"),
        total_rows=("Action", "size"),
    ).reset_index()
    conflicts = grouped[grouped["num_actions"] > 1].copy()
    return conflicts


# ---------------------------------------------------------------------------
# Statistical tests
# ---------------------------------------------------------------------------

def kruskal_bytes_by_action(df: pd.DataFrame) -> dict[str, Any]:
    """Kruskal-Wallis H test: Bytes across the four Action classes.

    Returns dict with keys: H, p_value, epsilon_squared, n.
    """
    groups = [grp["Bytes"].values for _, grp in df.groupby("Action")]
    H, p = kruskal(*groups)
    n = len(df)
    eps2 = H / (n - 1)
    return {"H": float(H), "p_value": float(p), "epsilon_squared": float(eps2), "n": n}


def chi_square_nat_source_port(df: pd.DataFrame) -> dict[str, Any]:
    """Chi-square test of independence: NAT Source Port status (zero vs nonzero) × Action.

    Uses correction=False.  Returns dict with chi2, df, p_value, cramers_v,
    min_expected, contingency_table (DataFrame).
    """
    nat_status = pd.Series(
        np.where(df["NAT Source Port"] == 0, "zero", "nonzero"),
        index=df.index,
        name="NAT_status",
    )
    ct = pd.crosstab(nat_status, df["Action"])
    chi2, p, dof, expected = chi2_contingency(ct, correction=False)
    n = len(df)
    min_dim = min(ct.shape[0] - 1, ct.shape[1] - 1)
    cramers_v = float(np.sqrt(chi2 / (n * min_dim)))
    return {
        "chi2": float(chi2),
        "df": int(dof),
        "p_value": float(p),
        "cramers_v": cramers_v,
        "min_expected": float(expected.min()),
        "contingency_table": ct,
    }


def format_p_value(p: float) -> str:
    """Human-readable p-value; handle near-zero underflow."""
    if p <= 0 or p < 1e-300:
        return "< 1e-300 (numerical underflow)"
    return f"{p:.4e}"


# ---------------------------------------------------------------------------
# Outlier summary
# ---------------------------------------------------------------------------

def outlier_summary(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Compute median, P99, max, count > P99 for selected numeric columns."""
    if columns is None:
        columns = ["Bytes", "Packets", "Elapsed Time (sec)"]
    rows = []
    for col in columns:
        if col not in df.columns:
            continue
        s = df[col].dropna()
        p99 = float(np.percentile(s, 99))
        rows.append({
            "Feature": col,
            "Median": float(s.median()),
            "P99": p99,
            "Max": float(s.max()),
            "Count > P99": int((s > p99).sum()),
        })
    return pd.DataFrame(rows)
