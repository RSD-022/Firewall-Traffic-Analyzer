"""Intelligent Firewall Traffic Analyzer — Streamlit application.

Run from repository root: python -m streamlit run src/app.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from inference import (
    DEFAULT_FEATURES,
    auto_sum_bytes,
    auto_sum_packets,
    check_consistency_warnings,
    get_features,
    get_probability_table,
    load_metadata,
    load_trusted_pipeline,
    predict_dataframe,
    validate_features,
)
from statistical_tests import (
    chi_square_nat_source_port,
    conflicting_label_groups,
    deduplicate,
    duplicate_summary,
    format_p_value,
    kruskal_bytes_by_action,
    outlier_summary,
)
from visualization import (
    ACTION_COLORS,
    action_frequency_bar,
    boxplot_log_bytes_by_action,
    class_comparison_bar,
    class_distribution_donut,
    confusion_matrix_heatmap,
    contingency_heatmap,
    feature_importance_bar,
    histogram_with_kde,
    metric_comparison_bar,
    nat_source_port_status,
    probability_bar_chart,
    spearman_heatmap,
    top_n_destination_ports,
)
from theme import apply_theme, sidebar_header_html, page_divider_html, action_badge_html, footer_html

# ---------------------------------------------------------------------------
# Paths — support env-var overrides for dev/test
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "raw" / "log2.csv"

_default_model = str(ROOT / "models" / "firewall_pipeline.joblib")
_default_meta = str(ROOT / "models" / "metadata.json")
_default_metrics = str(ROOT / "models" / "metrics.json")

MODEL_FILE = Path(os.environ.get("FIREWALL_MODEL_FILE", _default_model))
META_FILE = Path(os.environ.get("FIREWALL_META_FILE", _default_meta))
METRICS_FILE = Path(os.environ.get("FIREWALL_METRICS_FILE", _default_metrics))

_using_test_artifacts = (
    str(MODEL_FILE) != _default_model
    or str(META_FILE) != _default_meta
    or str(METRICS_FILE) != _default_metrics
)

MAX_CSV_BYTES = 20 * 1024 * 1024
MAX_ROWS = 100_000

# ---------------------------------------------------------------------------
# Page config & global style
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Firewall Intelligence", page_icon="🛡️", layout="wide")

# Inject security-console theme (CSS only, no content change)
apply_theme()

if _using_test_artifacts:
    st.error("🧪 **TEST ARTIFACT** — not the team's trained model. "
             "Environment variable(s) override the default model/metadata/metrics paths.")

# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def read_csv_cached(path: str, modtime: float) -> pd.DataFrame:
    return pd.read_csv(path)


@st.cache_resource(show_spinner=False)
def get_pipeline(path: str, modtime: float):
    return load_trusted_pipeline(Path(path))


@st.cache_data(show_spinner=False)
def compute_duplicate_summary(path: str, modtime: float) -> dict:
    df = pd.read_csv(path)
    return duplicate_summary(df)


@st.cache_data(show_spinner=False)
def compute_conflicts(path: str, modtime: float) -> pd.DataFrame:
    df = pd.read_csv(path)
    return conflicting_label_groups(df)


@st.cache_data(show_spinner=False)
def compute_kruskal(path: str, modtime: float, dedup: bool = False) -> dict:
    df = pd.read_csv(path)
    if dedup:
        df = deduplicate(df)
    return kruskal_bytes_by_action(df)


@st.cache_data(show_spinner=False)
def compute_chi2(path: str, modtime: float, dedup: bool = False) -> dict:
    df = pd.read_csv(path)
    if dedup:
        df = deduplicate(df)
    result = chi_square_nat_source_port(df)
    # Convert contingency_table to serialisable form for cache
    result["contingency_table"] = result["contingency_table"].to_dict()
    return result


@st.cache_data(show_spinner=False)
def compute_outlier_summary(path: str, modtime: float) -> pd.DataFrame:
    df = pd.read_csv(path)
    return outlier_summary(df)


def selected_model():
    if not MODEL_FILE.is_file():
        return None
    return get_pipeline(str(MODEL_FILE), MODEL_FILE.stat().st_mtime)


def load_data() -> pd.DataFrame | None:
    if DATA_FILE.is_file():
        return read_csv_cached(str(DATA_FILE), DATA_FILE.stat().st_mtime)
    return None


def safe_upload(upload) -> pd.DataFrame:
    if upload.size > MAX_CSV_BYTES:
        raise ValueError("CSV larger than 20 MB. Select a smaller sample.")
    df = pd.read_csv(upload)
    if len(df) > MAX_ROWS:
        raise ValueError("Upload more than 100,000 rows; please split it into smaller files.")
    return df


def section_heading(title: str, description: str):
    st.title(title)
    st.markdown(page_divider_html(), unsafe_allow_html=True)
    st.caption(description)


# ---------------------------------------------------------------------------
# Metadata / features
# ---------------------------------------------------------------------------
try:
    metadata = load_metadata(META_FILE)
    features = get_features(metadata)
except (ValueError, json.JSONDecodeError) as exc:
    metadata = {}
    features = DEFAULT_FEATURES.copy()
    st.error(f"Invalid model metadata: {exc}")

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    # Decorative: shield logo + system-status panel (replaces plain title/caption/success)
    st.markdown(
        sidebar_header_html(MODEL_FILE.is_file(), _using_test_artifacts),
        unsafe_allow_html=True,
    )
    st.divider()
    page = st.radio("Navigation", [
        "Overview", "Data Quality", "Traffic Analytics", "Statistics",
        "Manual Prediction", "Batch Prediction", "Model Performance", "About & FAQ",
    ], label_visibility="collapsed")


# ===================================================================
# PAGE: Overview
# ===================================================================
if page == "Overview":
    section_heading("Network Traffic Overview",
                    "Understand historical firewall traffic and classification patterns.")
    df = load_data()
    if df is None:
        st.info("Default dataset not found at data/raw/log2.csv. "
                "Add the project dataset to activate overview analytics.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Traffic records", f"{len(df):,}")
        m2.metric("Dataset fields", f"{len(df.columns):,}")
        m3.metric("Observed actions",
                  int(df["Action"].nunique()) if "Action" in df else "N/A")
        m4.metric("Missing values", int(df.isna().sum().sum()))

        st.subheader("Action distribution")
        if "Action" in df.columns:
            counts = df["Action"].value_counts()
            fig = class_distribution_donut(counts)
            st.plotly_chart(fig, key="overview_donut")
        else:
            st.warning("The dataset has no Action column.")

        st.subheader("Data preview")
        st.dataframe(df.head(30), hide_index=True)

        st.subheader("Known limitations")
        st.warning(
            "**Extreme class imbalance** — `reset-both` has only 54 rows "
            "(0.08 %) vs 37,640 for `allow`.\n\n"
            "**Possible target leakage** — NAT ports and byte/packet counts "
            "may be determined *after* the firewall action, meaning they "
            "could leak the target into the features.\n\n"
            "**Single firewall policy** — the data reflects one specific "
            "policy configuration; results may not generalise to other "
            "networks or rule sets.",
            icon="⚠️",
        )


# ===================================================================
# PAGE: Data Quality
# ===================================================================
elif page == "Data Quality":
    section_heading("Data Quality",
                    "Assessment of duplicates, conflicts and outliers in the full dataset.")
    st.info("All statistics on this page use the **full dataset** (65,532 rows), "
            "without any filtering.", icon="ℹ️")
    df = load_data()
    if df is None:
        st.info("Add data/raw/log2.csv to enable data quality checks.")
    else:
        modtime = DATA_FILE.stat().st_mtime
        path_str = str(DATA_FILE)

        # --- Duplicates ---
        st.subheader("Duplicate rows")
        dup = compute_duplicate_summary(path_str, modtime)
        c1, c2, c3 = st.columns(3)
        c1.metric("Extra copies", f"{dup['extra_copies']:,}",
                  help="Rows that duplicate an earlier row (keep='first')")
        c2.metric("Rows in repeated groups", f"{dup['rows_in_groups']:,}",
                  help="All rows belonging to any repeated group (keep=False)")
        c3.metric("Distinct rows", f"{dup['distinct_rows']:,}")
        pct = dup["extra_copies"] / len(df) * 100
        st.caption(f"{dup['extra_copies']:,} extra copies = {pct:.2f}% of the dataset; "
                   f"{dup['rows_in_groups']:,} rows belong to repeated groups; "
                   f"{dup['distinct_rows']:,} distinct rows after deduplication.")

        # --- Conflicting labels ---
        st.subheader("Conflicting labels")
        conflicts = compute_conflicts(path_str, modtime)
        if len(conflicts) == 0:
            st.success("No conflicting labels found.")
        else:
            total_rows = int(conflicts["total_rows"].sum())
            st.write(f"**{len(conflicts)} groups** covering **{total_rows} rows** have "
                     "identical 11-feature vectors with more than one Action label.")
            st.dataframe(conflicts, hide_index=True)

        # --- Class share before vs after dedup ---
        st.subheader("Class share: before vs after deduplication")
        before = df["Action"].value_counts()
        after = deduplicate(df)["Action"].value_counts()
        fig = class_comparison_bar(before, after)
        st.plotly_chart(fig, key="dq_class_compare")

        # --- Outlier table ---
        st.subheader("Outlier candidates")
        outliers = compute_outlier_summary(path_str, modtime)
        st.dataframe(outliers, hide_index=True)
        st.caption("Values above P99 are candidates for review, not necessarily errors.")


# ===================================================================
# PAGE: Traffic Analytics
# ===================================================================
elif page == "Traffic Analytics":
    section_heading("Traffic Analytics",
                    "Explore distributions, traffic volumes and filtering.")
    df = load_data()
    if df is None:
        st.info("Add data/raw/log2.csv to enable analytics.")
    else:
        # ----- Sidebar filters (only on this page) -----
        with st.sidebar:
            st.subheader("Filters")
            if "Action" in df.columns:
                all_actions = sorted(df["Action"].dropna().astype(str).unique().tolist())
                sel_actions = st.multiselect("Action", all_actions, default=all_actions,
                                             key="ta_action_filter")
            else:
                sel_actions = None

            if "Destination Port" in df.columns:
                port_search = st.text_input("Destination port search",
                                            key="ta_port_search",
                                            help="Comma-separated port numbers")
            else:
                port_search = ""

            if "Bytes" in df.columns:
                bmin, bmax = int(df["Bytes"].min()), int(df["Bytes"].max())
                bytes_range = st.slider("Bytes range", bmin, bmax, (bmin, bmax),
                                        key="ta_bytes_range")
            else:
                bytes_range = None

            if "Elapsed Time (sec)" in df.columns:
                tmin = int(df["Elapsed Time (sec)"].min())
                tmax = int(df["Elapsed Time (sec)"].max())
                time_range = st.slider("Elapsed Time range", tmin, tmax, (tmin, tmax),
                                       key="ta_time_range")
            else:
                time_range = None

            exclude_dupes = st.toggle("Exclude exact duplicates", value=False,
                                      key="ta_exclude_dupes")

        # ----- Apply filters -----
        filtered = df.copy()
        if sel_actions is not None:
            filtered = filtered[filtered["Action"].astype(str).isin(sel_actions)]
        if port_search:
            try:
                ports = [int(p.strip()) for p in port_search.split(",") if p.strip()]
                if ports:
                    filtered = filtered[filtered["Destination Port"].isin(ports)]
            except ValueError:
                st.warning("Invalid port number in search.")
        if bytes_range is not None:
            filtered = filtered[
                (filtered["Bytes"] >= bytes_range[0]) & (filtered["Bytes"] <= bytes_range[1])
            ]
        if time_range is not None:
            filtered = filtered[
                (filtered["Elapsed Time (sec)"] >= time_range[0])
                & (filtered["Elapsed Time (sec)"] <= time_range[1])
            ]
        if exclude_dupes:
            filtered = deduplicate(filtered)

        st.caption(f"**{len(filtered):,}** rows selected")

        if len(filtered) == 0:
            st.info("No rows match the current filters. Adjust the sidebar filters "
                    "to see data.")
        else:
            # ----- Tabs -----
            tab_desc, tab_miss, tab_dist, tab_freq, tab_corr, tab_table = st.tabs([
                "Descriptive statistics", "Missing values", "Distributions",
                "Frequencies", "Correlation", "Data table",
            ])

            numeric_cols = filtered.select_dtypes(include="number").columns.tolist()

            # Tab: Descriptive statistics
            with tab_desc:
                if numeric_cols:
                    stats = filtered[numeric_cols].describe(
                        percentiles=[0.25, 0.5, 0.75, 0.99]
                    ).T
                    stats = stats.rename(columns={"50%": "median", "99%": "P99"})
                    st.dataframe(stats, height=450)
                else:
                    st.info("No numeric columns in filtered data.")

            # Tab: Missing values
            with tab_miss:
                miss_count = filtered.isna().sum()
                miss_pct = (miss_count / len(filtered) * 100).round(2)
                miss_df = pd.DataFrame({"Count": miss_count, "%": miss_pct})
                st.dataframe(miss_df)

            # Tab: Distributions
            with tab_dist:
                if numeric_cols:
                    dist_col = st.selectbox("Feature", numeric_cols, key="ta_dist_col")
                    log_toggle = st.toggle("Apply log1p transform", key="ta_log_toggle")
                    fig = histogram_with_kde(filtered[dist_col], title=f"Distribution of {dist_col}",
                                            log_transform=log_toggle)
                    st.plotly_chart(fig, key="ta_dist_chart")
                else:
                    st.info("No numeric columns available.")

            # Tab: Frequencies
            with tab_freq:
                if "Action" in filtered.columns:
                    st.subheader("Action frequency")
                    action_counts = filtered["Action"].value_counts()
                    st.plotly_chart(action_frequency_bar(action_counts), key="ta_freq_action")

                if "Destination Port" in filtered.columns:
                    st.subheader("Top destination ports")
                    n_ports = st.slider("Number of ports", 5, 50, 15, key="ta_topn_slider")
                    st.plotly_chart(top_n_destination_ports(filtered, n=n_ports),
                                   key="ta_freq_ports")

                if "NAT Source Port" in filtered.columns:
                    st.subheader("NAT Source Port status")
                    st.plotly_chart(nat_source_port_status(filtered), key="ta_freq_nat")

            # Tab: Correlation
            with tab_corr:
                port_cols = ["Source Port", "Destination Port",
                             "NAT Source Port", "NAT Destination Port"]
                include_ports = st.checkbox("Include port columns (identifiers)",
                                           value=False, key="ta_corr_ports")
                corr_cols = numeric_cols if include_ports else [
                    c for c in numeric_cols if c not in port_cols
                ]
                if len(corr_cols) >= 2:
                    st.plotly_chart(spearman_heatmap(filtered[corr_cols]),
                                   key="ta_corr_heatmap")
                else:
                    st.info("Not enough numeric columns for a correlation matrix.")

            # Tab: Data table
            with tab_table:
                st.dataframe(filtered, hide_index=True)
                csv_data = filtered.to_csv(index=False).encode("utf-8")
                st.download_button("Download filtered CSV", data=csv_data,
                                   file_name="filtered_firewall_data.csv",
                                   mime="text/csv")

        st.caption("Statistics are descriptive observations from historical logs, "
                   "not forecasts.")


# ===================================================================
# PAGE: Statistics
# ===================================================================
elif page == "Statistics":
    section_heading("Statistical Tests",
                    "Kruskal-Wallis and Chi-square tests on the full dataset, "
                    "shown for original and deduplicated data.")
    df = load_data()
    if df is None:
        st.info("Add data/raw/log2.csv to enable statistical tests.")
    else:
        modtime = DATA_FILE.stat().st_mtime
        path_str = str(DATA_FILE)

        col_orig, col_dedup = st.columns(2)

        # --- Kruskal-Wallis ---
        st.subheader("a) Kruskal-Wallis H test: Bytes across Action classes")
        kw_orig = compute_kruskal(path_str, modtime, dedup=False)
        kw_dedup = compute_kruskal(path_str, modtime, dedup=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Original data**")
            st.metric("H statistic", f"{kw_orig['H']:.4f}")
            st.metric("p-value", format_p_value(kw_orig["p_value"]))
            st.metric("ε² (epsilon squared)", f"{kw_orig['epsilon_squared']:.4f}")
            st.metric("n", f"{kw_orig['n']:,}")
        with c2:
            st.markdown("**Deduplicated data**")
            st.metric("H statistic", f"{kw_dedup['H']:.4f}")
            st.metric("p-value", format_p_value(kw_dedup["p_value"]))
            st.metric("ε² (epsilon squared)", f"{kw_dedup['epsilon_squared']:.4f}")
            st.metric("n", f"{kw_dedup['n']:,}")

        st.plotly_chart(boxplot_log_bytes_by_action(df), key="stat_boxplot")

        st.info(
            "**Interpretation:** The Kruskal-Wallis test rejects the null hypothesis "
            "that the distribution of Bytes is the same across all four Action groups "
            "(H ≈ 44,288, p < 1e-300). The effect size ε² ≈ 0.68 indicates a large "
            "association between Action and Bytes. "
            "Results remain highly significant after deduplication.",
            icon="📊",
        )

        st.divider()

        # --- Chi-square ---
        st.subheader("b) Chi-square: NAT Source Port status × Action")
        chi_orig = compute_chi2(path_str, modtime, dedup=False)
        chi_dedup = compute_chi2(path_str, modtime, dedup=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Original data**")
            st.metric("χ²", f"{chi_orig['chi2']:.4f}")
            st.metric("df", str(chi_orig["df"]))
            st.metric("p-value", format_p_value(chi_orig["p_value"]))
            st.metric("Cramér's V", f"{chi_orig['cramers_v']:.4f}")
            st.metric("Min expected count", f"{chi_orig['min_expected']:.2f}")
        with c2:
            st.markdown("**Deduplicated data**")
            st.metric("χ²", f"{chi_dedup['chi2']:.4f}")
            st.metric("df", str(chi_dedup["df"]))
            st.metric("p-value", format_p_value(chi_dedup["p_value"]))
            st.metric("Cramér's V", f"{chi_dedup['cramers_v']:.4f}")
            st.metric("Min expected count", f"{chi_dedup['min_expected']:.2f}")

        # Contingency table
        st.markdown("**Contingency table (original data)**")
        ct_df = pd.DataFrame(chi_orig["contingency_table"])
        st.dataframe(ct_df)
        st.plotly_chart(contingency_heatmap(ct_df, title="NAT Source Port status × Action"),
                        key="stat_chi_heatmap")

        st.info(
            "**Interpretation:** NAT Source Port status (zero vs nonzero) and Action are "
            "very strongly associated (χ² ≈ 63,183, Cramér's V ≈ 0.98). "
            "This near-perfect association persists after deduplication.",
            icon="📊",
        )

        st.warning(
            "**Caution:** Association ≠ causation. NAT source ports may only be assigned "
            "*after* the firewall decides to allow traffic, meaning the NAT port status "
            "could reflect the action rather than predict it (**target-leakage risk**). "
            "These tests demonstrate statistical relationships in the data but do not "
            "establish causal direction. No model performance claims are made here.",
            icon="⚠️",
        )


# ===================================================================
# PAGE: Manual Prediction
# ===================================================================
elif page == "Manual Prediction":
    section_heading("Manual Prediction",
                    "Enter the input characteristics of one network flow.")

    if not MODEL_FILE.is_file():
        st.warning("No trained pipeline found. Ask the ML teammate to export "
                   "`models/firewall_pipeline.joblib`.")

    # --- Preset buttons ---
    st.subheader("Example inputs")
    st.caption("These fill the form with sample values. They do not state which action "
               "the model is expected to produce.")

    def _apply_preset(values: dict):
        for k, v in values.items():
            st.session_state[f"mp_{k}"] = v

    presets = {
        "HTTPS-like": {
            "Source Port": 52000, "Destination Port": 443,
            "NAT Source Port": 52000, "NAT Destination Port": 443,
            "Bytes": 4096, "Bytes Sent": 2048, "Bytes Received": 2048,
            "Packets": 12, "Elapsed Time (sec)": 2.0,
            "pkts_sent": 6, "pkts_received": 6,
        },
        "SMB port 445": {
            "Source Port": 49200, "Destination Port": 445,
            "NAT Source Port": 0, "NAT Destination Port": 0,
            "Bytes": 512, "Bytes Sent": 256, "Bytes Received": 256,
            "Packets": 6, "Elapsed Time (sec)": 0.5,
            "pkts_sent": 3, "pkts_received": 3,
        },
        "VNC port 5900": {
            "Source Port": 51500, "Destination Port": 5900,
            "NAT Source Port": 0, "NAT Destination Port": 0,
            "Bytes": 1024, "Bytes Sent": 600, "Bytes Received": 424,
            "Packets": 8, "Elapsed Time (sec)": 1.0,
            "pkts_sent": 4, "pkts_received": 4,
        },
    }

    preset_cols = st.columns(len(presets))
    for col, (label, vals) in zip(preset_cols, presets.items()):
        with col:
            st.button(label, on_click=_apply_preset, args=(vals,), key=f"preset_{label}",
                      width="stretch")

    # Detect auto-sum features
    _has_bytes_trio = (
        "Bytes" in features and "Bytes Sent" in features and "Bytes Received" in features
    )
    _has_pkt_trio = (
        "Packets" in features and "pkts_sent" in features and "pkts_received" in features
    )

    defaults = {"Source Port": 50000, "Destination Port": 443,
                "NAT Source Port": 50000, "NAT Destination Port": 443,
                "Bytes": 2048, "Bytes Sent": 1024, "Bytes Received": 1024,
                "Packets": 20, "Elapsed Time (sec)": 1.0,
                "pkts_sent": 10, "pkts_received": 10}

    with st.form("manual_predict"):
        entries: dict[str, float | int] = {}
        cols = st.columns(2)
        for i, feature in enumerate(features):
            with cols[i % 2]:
                is_duration = feature == "Elapsed Time (sec)"
                max_port = 65535 if "Port" in feature else None

                # Get default: prefer session_state preset, else static default
                ss_key = f"mp_{feature}"
                if ss_key in st.session_state:
                    default = st.session_state[ss_key]
                else:
                    default = defaults.get(feature, 0)

                # Auto-computed fields shown as read-only info
                if _has_bytes_trio and feature == "Bytes":
                    sent_val = st.session_state.get("mp_Bytes Sent", defaults.get("Bytes Sent", 0))
                    recv_val = st.session_state.get("mp_Bytes Received", defaults.get("Bytes Received", 0))
                    auto_val = int(auto_sum_bytes(sent_val, recv_val))
                    st.text_input(f"{feature} (auto-computed: Sent + Received)",
                                  value=str(auto_val), disabled=True,
                                  key=f"mp_display_{feature}")
                    entries[feature] = auto_val
                    continue
                if _has_pkt_trio and feature == "Packets":
                    sent_val = st.session_state.get("mp_pkts_sent", defaults.get("pkts_sent", 0))
                    recv_val = st.session_state.get("mp_pkts_received", defaults.get("pkts_received", 0))
                    auto_val = int(auto_sum_packets(sent_val, recv_val))
                    st.text_input(f"{feature} (auto-computed: sent + received)",
                                  value=str(auto_val), disabled=True,
                                  key=f"mp_display_{feature}")
                    entries[feature] = auto_val
                    continue

                entries[feature] = st.number_input(
                    feature,
                    min_value=0.0 if is_duration else 0,
                    max_value=max_port,
                    value=float(default) if is_duration else int(default),
                    step=0.1 if is_duration else 1,
                    key=ss_key,
                )
        submitted = st.form_submit_button("Predict firewall action", type="primary",
                                          width="stretch")

    if submitted:
        if not MODEL_FILE.is_file():
            st.warning("Prediction unavailable: ask the ML teammate to export "
                       "models/firewall_pipeline.joblib.")
        else:
            try:
                model = selected_model()
                input_df = pd.DataFrame([entries])
                result = predict_dataframe(model, input_df, features)
                predicted = str(result["Predicted Action"].iloc[0])
                color = ACTION_COLORS.get(predicted.lower(), "#888")

                # Styled pill badge (replaces the plain markdown span)
                st.markdown(action_badge_html(predicted, color), unsafe_allow_html=True)

                # Probability bar chart
                X_val = validate_features(input_df, features)
                prob_table = get_probability_table(model, X_val)
                if prob_table is not None:
                    classes = list(prob_table.columns)
                    probs = prob_table.iloc[0].tolist()
                    fig = probability_bar_chart(classes, probs, predicted)
                    st.plotly_chart(fig, key="mp_proba_chart")
                else:
                    st.caption("No probability available for this model.")

                st.caption("This is a model prediction, not a rule enforced by a real firewall.")
            except Exception as exc:
                st.error(f"Prediction failed. Confirm your model and feature schema: {exc}")

    with st.expander("Limitations of this prediction"):
        st.markdown(
            "- The model was trained on **historical single-policy data** from one firewall.\n"
            "- `reset-both` has only **54 training samples** — predictions for this class "
            "are particularly uncertain.\n"
            "- The model may rely on **NAT port patterns and byte/packet counts** that could "
            "reflect the firewall decision rather than predict it (potential target leakage).\n"
            "- Predictions are **not security policies**; do not use them to enforce firewall rules."
        )


# ===================================================================
# PAGE: Batch Prediction
# ===================================================================
elif page == "Batch Prediction":
    section_heading("Batch Prediction",
                    "Upload firewall records as CSV and export predicted actions.")
    st.caption("The CSV must contain all training input columns. "
               "The Action column is optional and is never used as input.")
    st.code(",".join(features), language="text")

    # Template download
    template_csv = ",".join(features) + "\n"
    st.download_button("Download header-only CSV template",
                       data=template_csv.encode("utf-8"),
                       file_name="firewall_template.csv",
                       mime="text/csv")

    uploaded = st.file_uploader("Choose a traffic CSV", type=["csv"])
    if uploaded is not None:
        try:
            df = safe_upload(uploaded)
            st.write(f"Loaded **{len(df):,}** rows")
            st.dataframe(df.head(10), hide_index=True)

            # Consistency warnings
            for w in check_consistency_warnings(df):
                st.warning(w)

            if not MODEL_FILE.is_file():
                st.warning("No trained pipeline was exported yet. "
                           "CSV upload works, but predictions are disabled.")
            elif st.button("Run batch prediction", type="primary"):
                model = selected_model()
                output = predict_dataframe(model, df, features)
                st.success(f"Predicted actions for {len(output):,} records.")
                st.dataframe(output.head(50), hide_index=True)

                st.subheader("Predicted action distribution")
                pred_counts = output["Predicted Action"].value_counts()
                colors = [ACTION_COLORS.get(a.lower(), "#888") for a in pred_counts.index]
                fig = go.Figure(go.Bar(
                    x=pred_counts.index, y=pred_counts.values,
                    marker_color=colors,
                ))
                fig.update_layout(title="Predicted actions", height=400,
                                  xaxis_title="Action", yaxis_title="Count")
                fig.update_layout(template="fw_dark")
                st.plotly_chart(fig, key="bp_pred_dist")

                # If uploaded CSV has an Action column, show observed vs predicted
                if "Action" in df.columns:
                    st.subheader("Observed vs predicted counts")
                    obs = df["Action"].value_counts().rename("Observed")
                    pred_c = output["Predicted Action"].value_counts().rename("Predicted")
                    comparison = pd.concat([obs, pred_c], axis=1).fillna(0).astype(int)
                    st.dataframe(comparison)
                    st.caption("⚠️ This comparison is **NOT** a held-out evaluation "
                               "if these rows were used for training the model.")

                st.download_button(
                    "Download predictions CSV",
                    data=output.to_csv(index=False).encode("utf-8"),
                    file_name="firewall_predictions.csv", mime="text/csv",
                )
                st.caption("Prediction columns are model outputs; "
                           "uploaded observed labels, if any, remain distinct.")
        except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as exc:
            st.error(f"Invalid CSV: {exc}")
        except Exception as exc:
            st.error(f"Prediction failed. Verify the exported pipeline and schema: {exc}")


# ===================================================================
# PAGE: Model Performance
# ===================================================================
elif page == "Model Performance":
    section_heading("Model Performance",
                    "Display the real results saved during offline evaluation.")
    if not METRICS_FILE.is_file():
        st.info("Metrics unavailable. Export models/metrics.json from your training "
                "notebook. Do not invent metrics.")
    else:
        try:
            metrics = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
            if not isinstance(metrics, dict):
                raise ValueError("metrics.json must be a JSON object")

            st.subheader("Selected model")
            st.write(metrics.get("model_name",
                                 metadata.get("model_name", "Not specified")))

            keymap = [("Accuracy", "accuracy"), ("Macro F1", "macro_f1"),
                      ("Weighted F1", "weighted_f1")]
            metric_cols = st.columns(3)
            for col, (label, key) in zip(metric_cols, keymap):
                val = metrics.get(key)
                col.metric(label,
                           f"{float(val):.3f}" if isinstance(val, (float, int)) else "Not provided")

            # --- Model comparison (OPTIONAL) ---
            if isinstance(metrics.get("model_comparison"), list) and metrics["model_comparison"]:
                st.subheader("Model comparison")
                comp_df = pd.DataFrame(metrics["model_comparison"])
                st.dataframe(comp_df, hide_index=True)
                # Metric selector bar chart
                numeric_metric_cols = [c for c in comp_df.columns
                                       if c != "model" and c != "best_params"
                                       and pd.api.types.is_numeric_dtype(comp_df[c])]
                if numeric_metric_cols and "model" in comp_df.columns:
                    sel_metric = st.selectbox("Metric to compare", numeric_metric_cols,
                                             key="mp_metric_select")
                    st.plotly_chart(metric_comparison_bar(comp_df, sel_metric),
                                   key="mp_metric_bar")

            # --- Confusion matrix (OPTIONAL) ---
            cm_data = metrics.get("confusion_matrices") or metrics.get("confusion_matrix")
            if cm_data is not None:
                st.subheader("Confusion matrix (held-out test set)")

                if isinstance(cm_data, dict):
                    # Multiple models
                    model_names = list(cm_data.keys())
                    sel_cm_model = st.selectbox("Model", model_names, key="mp_cm_model")
                    cm_entry = cm_data[sel_cm_model]
                    if isinstance(cm_entry, dict):
                        matrix = cm_entry.get("matrix", cm_entry)
                        labels = cm_entry.get("class_labels",
                                              metrics.get("class_labels", []))
                    else:
                        matrix = cm_entry
                        labels = metrics.get("class_labels", [])
                elif isinstance(cm_data, list):
                    matrix = cm_data
                    labels = metrics.get("class_labels", [])
                else:
                    matrix = None
                    labels = []

                if matrix is not None:
                    normalize = st.toggle("Normalize (row %)", value=False,
                                         key="mp_cm_normalize")
                    if not isinstance(labels, list) or len(labels) != len(matrix):
                        labels = [f"Class {i}" for i in range(len(matrix))]
                    fig = confusion_matrix_heatmap(matrix, labels, normalize=normalize)
                    st.plotly_chart(fig, key="mp_cm_heatmap")

            # --- Per-class metrics (OPTIONAL) ---
            if isinstance(metrics.get("per_class"), list) and metrics["per_class"]:
                st.subheader("Per-class metrics")
                st.dataframe(pd.DataFrame(metrics["per_class"]), hide_index=True)

            # --- Feature importances (OPTIONAL) ---
            if isinstance(metrics.get("feature_importances"), list) and metrics["feature_importances"]:
                st.subheader("Feature importances")
                st.plotly_chart(feature_importance_bar(metrics["feature_importances"]),
                                key="mp_feat_imp")

            # --- Training features ---
            st.subheader("Training feature columns")
            st.code(", ".join(features), language="text")

            st.warning(
                "`reset-both` has very few samples (54 in the full dataset), so its "
                "per-class metrics are uncertain and may not generalise.",
                icon="⚠️",
            )
            st.caption("All reported results must be computed on a held-out test set "
                       "or clearly labelled otherwise.")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            st.error(f"Unable to load evaluation metrics: {exc}")


# ===================================================================
# PAGE: About & FAQ
# ===================================================================
elif page == "About & FAQ":
    section_heading("About the Project",
                    "Academic Data Mining research prototype for network security.")

    st.markdown("""
### Objective
Predict the action associated with historical firewall traffic using supervised
classification on the UCI Internet Firewall Data (dataset #542, 65,532 records).

### Labels
`allow`, `deny`, `drop`, and `reset-both`.

### Methodology
1. **Data collection** — UCI Machine Learning Repository, Internet Firewall Data.
2. **Exploratory analysis** — descriptive statistics, duplicate and conflict
   detection, statistical tests (Kruskal-Wallis, Chi-square).
3. **Preprocessing** — cleaning, encoding, scaling inside an sklearn Pipeline.
4. **Modelling** — supervised classifiers compared via cross-validation on
   balanced metrics (macro F1, weighted F1).
5. **Evaluation** — held-out test set, confusion matrix, per-class metrics.
6. **Deployment** — Streamlit dashboard for interactive exploration and prediction.

### Pipeline
Historical CSV → data cleaning → fitted preprocessing → classifier → predicted action.
""")

    st.subheader("Team")
    team = pd.DataFrame([
        {"Code": "RSD-009", "Responsibility": "Streamlit application"},
        {"Code": "RSD-0XX", "Responsibility": "to be completed"},
        {"Code": "RSD-0XX", "Responsibility": "to be completed"},
        {"Code": "RSD-0XX", "Responsibility": "to be completed"},
    ])
    st.dataframe(team, hide_index=True)

    st.subheader("Frequently asked questions")

    with st.expander("What does each input feature mean?"):
        st.markdown("""
- **Source Port / Destination Port**: TCP/UDP port numbers of the connection
  endpoints (0–65535).
- **NAT Source Port / NAT Destination Port**: Translated port numbers after
  Network Address Translation. A value of 0 typically means NAT was not applied.
- **Bytes**: Total bytes transferred in the session.
- **Bytes Sent / Bytes Received**: Directional byte counts.
- **Packets**: Total number of packets.
- **Elapsed Time (sec)**: Duration of the recorded session.
- **pkts_sent / pkts_received**: Directional packet counts.
""")

    with st.expander("Why does port 445 often map to 'drop' in this dataset?"):
        st.markdown(
            "Port 445 is used by SMB (Server Message Block). Many firewall policies block "
            "inbound SMB traffic because it is a common attack vector for ransomware and "
            "lateral movement. In this particular firewall's policy, connections to port 445 "
            "were overwhelmingly dropped."
        )

    with st.expander("What is target leakage?"):
        st.markdown(
            "Target leakage occurs when the model's input features contain information that "
            "is determined *after* (or as a consequence of) the target variable. For example, "
            "NAT ports are typically assigned only when a connection is allowed, so their "
            "presence (nonzero value) directly reveals the firewall action. Including such "
            "features can inflate model accuracy but does not reflect true predictive power."
        )

    with st.expander("Why can accuracy be misleading under class imbalance?"):
        st.markdown(
            "When one class dominates (here, `allow` is 57.4%), a model that always predicts "
            "`allow` already achieves ~57% accuracy without learning anything. Balanced metrics "
            "like macro F1 weight all classes equally, revealing whether the model handles "
            "minority classes (`reset-both`, only 54 rows) well."
        )

    with st.expander("Why is reset-both so rare?"):
        st.markdown(
            "The `reset-both` action sends TCP RST packets to both endpoints, forcibly "
            "terminating the connection. It is relatively uncommon because most unwanted "
            "traffic is simply denied (rejected with a response) or dropped (silently "
            "discarded). Only 54 out of 65,532 rows carry this label, making it extremely "
            "hard for models to learn reliable patterns for this class."
        )

    st.subheader("Limitations")
    st.markdown("""
- This is **not** a deployed firewall, intrusion detection system or enforcement policy.
- Results may not generalise to unseen networks or shifted traffic distributions.
- Do not upload sensitive real customer traffic unless authorised.
- The model was trained on a single firewall's historical policy; other environments
  may behave differently.
- Extreme class imbalance affects per-class reliability, especially for `reset-both`.
""")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.markdown(
    footer_html(
        "Dataset: UCI Internet Firewall Data (dataset #542) &nbsp;·&nbsp; "
        "Software: Python + Streamlit + scikit-learn &nbsp;·&nbsp; "
        "<strong>This is NOT a real firewall or intrusion-detection product.</strong> "
        "It is an academic Data Mining project for educational purposes only."
    ),
    unsafe_allow_html=True,
)
