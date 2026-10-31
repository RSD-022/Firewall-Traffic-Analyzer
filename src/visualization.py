"""Plotly figure builders for the Firewall Traffic Analyzer.

All charts use a consistent colour map for the four Action classes.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Fixed action colours
ACTION_COLORS: dict[str, str] = {
    "allow": "#2ecc71",       # green
    "deny": "#e74c3c",        # red
    "drop": "#f39c12",        # amber
    "reset-both": "#9b59b6",  # purple
}

_COLOR_SEQUENCE = [ACTION_COLORS.get(k, "#888") for k in ("allow", "deny", "drop", "reset-both")]


def _action_color_map(actions: list[str] | pd.Index) -> dict[str, str]:
    """Build colour map for the actions present in the data."""
    return {a: ACTION_COLORS.get(a, "#888888") for a in actions}


# ---------------------------------------------------------------------------
# Class distribution
# ---------------------------------------------------------------------------

def class_distribution_donut(counts: pd.Series, title: str = "Action distribution") -> go.Figure:
    """Donut chart from an Action value_counts Series."""
    colors = [ACTION_COLORS.get(a, "#888") for a in counts.index]
    fig = go.Figure(go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=0.45,
        marker=dict(colors=colors),
        textinfo="label+percent",
    ))
    fig.update_layout(title_text=title, showlegend=True, height=400)
    return fig


def class_comparison_bar(before: pd.Series, after: pd.Series) -> go.Figure:
    """Grouped bar chart: class share before vs after deduplication."""
    actions = sorted(set(before.index) | set(after.index))
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Before dedup",
        x=actions,
        y=[before.get(a, 0) for a in actions],
        marker_color=[ACTION_COLORS.get(a, "#888") for a in actions],
        opacity=0.7,
    ))
    fig.add_trace(go.Bar(
        name="After dedup",
        x=actions,
        y=[after.get(a, 0) for a in actions],
        marker_color=[ACTION_COLORS.get(a, "#888") for a in actions],
        opacity=1.0,
    ))
    fig.update_layout(barmode="group", title="Class counts: before vs after deduplication",
                      xaxis_title="Action", yaxis_title="Count", height=420)
    return fig


# ---------------------------------------------------------------------------
# Histogram with optional KDE
# ---------------------------------------------------------------------------

def histogram_with_kde(
    series: pd.Series,
    title: str = "Distribution",
    log_transform: bool = False,
    max_kde_points: int = 5000,
) -> go.Figure:
    """Density histogram + KDE overlay.

    If *log_transform* apply log1p. KDE is computed on at most *max_kde_points*
    sampled values; returns a plain histogram if KDE fails (e.g. constant data).
    """
    vals = series.dropna()
    if log_transform:
        vals = np.log1p(vals)
        title += " (log1p)"

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=vals, histnorm="probability density", name="Histogram",
        marker_color="#36b4a7", opacity=0.65, nbinsx=50,
    ))

    # KDE overlay – best effort
    if len(vals) > 1 and vals.std() > 0:
        try:
            from scipy.stats import gaussian_kde
            sample = vals.sample(n=min(max_kde_points, len(vals)), random_state=42)
            kde = gaussian_kde(sample.values)
            x_grid = np.linspace(float(vals.min()), float(vals.max()), 300)
            fig.add_trace(go.Scatter(
                x=x_grid, y=kde(x_grid), mode="lines",
                name="KDE", line=dict(color="#f1c40f", width=2),
            ))
        except Exception:
            pass  # constant / tiny column

    fig.update_layout(title=title, xaxis_title=series.name or "Value",
                      yaxis_title="Density", height=420, bargap=0.05)
    return fig


# ---------------------------------------------------------------------------
# Frequency bar charts
# ---------------------------------------------------------------------------

def action_frequency_bar(counts: pd.Series) -> go.Figure:
    """Bar chart of Action frequencies."""
    colors = [ACTION_COLORS.get(a, "#888") for a in counts.index]
    fig = go.Figure(go.Bar(x=counts.index, y=counts.values, marker_color=colors))
    fig.update_layout(title="Action frequency", xaxis_title="Action", yaxis_title="Count", height=400)
    return fig


def top_n_destination_ports(df: pd.DataFrame, n: int = 15) -> go.Figure:
    """Top-N destination ports (treated as categories)."""
    counts = df["Destination Port"].astype(str).value_counts().head(n)
    fig = go.Figure(go.Bar(x=counts.index, y=counts.values, marker_color="#36b4a7"))
    fig.update_layout(title=f"Top {n} destination ports", xaxis_title="Port",
                      yaxis_title="Count", height=400, xaxis_type="category")
    return fig


def nat_source_port_status(df: pd.DataFrame) -> go.Figure:
    """Bar: NAT Source Port zero vs nonzero."""
    status = pd.Series(np.where(df["NAT Source Port"] == 0, "zero", "nonzero"))
    counts = status.value_counts()
    fig = go.Figure(go.Bar(x=counts.index, y=counts.values, marker_color=["#e74c3c", "#2ecc71"]))
    fig.update_layout(title="NAT Source Port status", xaxis_title="Status",
                      yaxis_title="Count", height=400)
    return fig


# ---------------------------------------------------------------------------
# Correlation heatmap
# ---------------------------------------------------------------------------

def spearman_heatmap(df: pd.DataFrame, title: str = "Spearman correlation") -> go.Figure:
    """Spearman rank-correlation heatmap for numeric columns in *df*."""
    corr = df.corr(method="spearman")
    fig = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.index,
        colorscale="RdBu_r", zmin=-1, zmax=1,
        text=np.round(corr.values, 2), texttemplate="%{text}",
    ))
    fig.update_layout(title=title, height=550, width=700)
    return fig


# ---------------------------------------------------------------------------
# Boxplot
# ---------------------------------------------------------------------------

def boxplot_log_bytes_by_action(df: pd.DataFrame) -> go.Figure:
    """Box plot of log1p(Bytes) grouped by Action."""
    tmp = df[["Action", "Bytes"]].copy()
    tmp["log1p_Bytes"] = np.log1p(tmp["Bytes"])
    fig = px.box(tmp, x="Action", y="log1p_Bytes",
                 color="Action", color_discrete_map=ACTION_COLORS,
                 title="log1p(Bytes) by Action")
    fig.update_layout(height=450, showlegend=False)
    return fig


# ---------------------------------------------------------------------------
# Contingency heatmap
# ---------------------------------------------------------------------------

def contingency_heatmap(ct: pd.DataFrame, title: str = "Contingency table") -> go.Figure:
    """Heatmap from a cross-tab DataFrame."""
    fig = go.Figure(go.Heatmap(
        z=ct.values, x=[str(c) for c in ct.columns], y=[str(r) for r in ct.index],
        colorscale="Blues",
        text=ct.values, texttemplate="%{text}",
    ))
    fig.update_layout(title=title, height=350)
    return fig


# ---------------------------------------------------------------------------
# Model performance charts
# ---------------------------------------------------------------------------

def metric_comparison_bar(df: pd.DataFrame, metric: str) -> go.Figure:
    """Bar chart comparing a metric across models."""
    fig = go.Figure(go.Bar(
        x=df["model"], y=df[metric], marker_color="#36b4a7",
        text=df[metric].round(4), textposition="outside",
    ))
    fig.update_layout(title=f"Model comparison — {metric}",
                      xaxis_title="Model", yaxis_title=metric, height=420)
    return fig


def confusion_matrix_heatmap(
    matrix: list[list[int | float]],
    labels: list[str],
    normalize: bool = False,
    title: str = "Confusion matrix",
) -> go.Figure:
    """Annotated confusion-matrix heatmap."""
    arr = np.array(matrix, dtype=float)
    if normalize:
        row_sums = arr.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        arr = arr / row_sums
        text = np.vectorize(lambda v: f"{v:.2%}")(arr)
    else:
        text = np.vectorize(lambda v: f"{int(v)}")(arr)

    fig = go.Figure(go.Heatmap(
        z=arr, x=labels, y=labels,
        colorscale="Blues",
        text=text, texttemplate="%{text}",
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Predicted", yaxis_title="Actual",
        height=480, width=520,
    )
    return fig


def feature_importance_bar(importances: list[dict[str, Any]]) -> go.Figure:
    """Horizontal bar chart of feature importances."""
    df = pd.DataFrame(importances).sort_values("importance", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["importance"], y=df["feature"],
        orientation="h", marker_color="#36b4a7",
    ))
    fig.update_layout(title="Feature importances", xaxis_title="Importance",
                      yaxis_title="Feature", height=max(300, len(df) * 30 + 100))
    return fig


def probability_bar_chart(
    classes: list[str],
    probabilities: list[float],
    predicted: str,
) -> go.Figure:
    """Bar chart of per-class probabilities."""
    colors = [ACTION_COLORS.get(c, "#888") for c in classes]
    fig = go.Figure(go.Bar(
        x=classes, y=probabilities,
        marker_color=colors,
        text=[f"{p:.1%}" for p in probabilities],
        textposition="outside",
    ))
    fig.update_layout(
        title=f"Class probabilities (predicted: {predicted})",
        xaxis_title="Action", yaxis_title="Probability",
        height=380, yaxis_range=[0, 1.1],
    )
    return fig
