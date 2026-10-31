"""Intelligent Firewall Traffic Analyzer — Streamlit application.

Run from repository root: streamlit run src/app.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from inference import DEFAULT_FEATURES, get_features, load_metadata, load_trusted_pipeline, predict_dataframe

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "raw" / "log2.csv"
MODEL_FILE = ROOT / "models" / "firewall_pipeline.joblib"
META_FILE = ROOT / "models" / "metadata.json"
METRICS_FILE = ROOT / "models" / "metrics.json"
MAX_CSV_BYTES = 20 * 1024 * 1024
MAX_ROWS = 100_000

st.set_page_config(page_title="Firewall Intelligence", page_icon="🛡️", layout="wide")
st.markdown("""<style>
.block-container{padding-top:1.7rem;padding-bottom:3rem}
[data-testid="stMetric"]{background:#121d2d0d;border:1px solid #80808022;border-radius:12px;padding:12px}
</style>""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def read_csv_cached(path: str, modtime: float) -> pd.DataFrame:
    return pd.read_csv(path)


@st.cache_resource(show_spinner=False)
def get_pipeline(path: str, modtime: float):
    return load_trusted_pipeline(Path(path))


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
    st.caption(description)


try:
    metadata = load_metadata(META_FILE)
    features = get_features(metadata)
except (ValueError, json.JSONDecodeError) as exc:
    metadata = {}
    features = DEFAULT_FEATURES.copy()
    st.error(f"Invalid model metadata: {exc}")

with st.sidebar:
    st.title("🛡️ Firewall Intelligence")
    st.caption("Intelligent Firewall Traffic Analyzer")
    page = st.radio("Navigation", [
        "Overview", "Traffic Analytics", "Manual Prediction",
        "Batch Prediction", "Model Performance", "About",
    ], label_visibility="collapsed")
    st.divider()
    st.success("Model available" if MODEL_FILE.is_file() else "Dataset/visualization mode")
    st.caption("Research prototype · Historical traffic classification")

if page == "Overview":
    section_heading("Network Traffic Overview", "Understand historical firewall traffic and classification patterns.")
    df = load_data()
    if df is None:
        st.info("Default dataset not found at data/raw/log2.csv. Add the project dataset to activate overview analytics.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Traffic records", f"{len(df):,}")
        m2.metric("Dataset fields", f"{len(df.columns):,}")
        m3.metric("Observed actions", int(df["Action"].nunique()) if "Action" in df else "N/A")
        m4.metric("Missing values", int(df.isna().sum().sum()))
        st.subheader("Action distribution")
        if "Action" in df:
            st.bar_chart(df["Action"].value_counts().rename_axis("Action").rename("Records"))
        else:
            st.warning("The dataset has no Action column.")
        st.subheader("Data preview")
        st.dataframe(df.head(30), use_container_width=True, hide_index=True)

elif page == "Traffic Analytics":
    section_heading("Traffic Analytics", "Explore distributions, traffic volumes and filtering.")
    df = load_data()
    if df is None:
        st.info("Add data/raw/log2.csv to enable analytics.")
    else:
        filtered = df
        if "Action" in df:
            labels = sorted(df["Action"].dropna().astype(str).unique().tolist())
            selected = st.multiselect("Filter by observed firewall action", labels, default=labels)
            filtered = df[df["Action"].astype(str).isin(selected)]
        numeric_columns = filtered.select_dtypes(include="number").columns.tolist()
        if numeric_columns:
            field = st.selectbox("Analyze numeric feature", numeric_columns,
                                 index=numeric_columns.index("Bytes") if "Bytes" in numeric_columns else 0)
            st.subheader(f"Distribution of {field}")
            values = filtered[field].dropna()
            if not values.empty:
                st.bar_chart(values.value_counts(bins=25, sort=False).rename("Rows"))
                st.dataframe(values.describe().to_frame("Statistic").T, use_container_width=True)
            else:
                st.info("No data remains after filtering.")
            if len(numeric_columns) >= 2:
                st.subheader("Feature relationship")
                c1, c2 = st.columns(2)
                x = c1.selectbox("X axis", numeric_columns, index=0)
                y = c2.selectbox("Y axis", numeric_columns,
                                 index=1 if len(numeric_columns) > 1 else 0)
                sample = filtered[[x, y]].dropna().sample(n=min(1500, len(filtered)), random_state=42) if len(filtered) else filtered[[x,y]]
                if not sample.empty:
                    st.scatter_chart(sample, x=x, y=y)
        else:
            st.info("No numeric columns available for plotting.")
        st.caption("Statistics are descriptive observations from historical logs, not forecasts.")

elif page == "Manual Prediction":
    section_heading("Manual Prediction", "Enter the 11 input characteristics of one network flow.")
    st.info("A trained full preprocessing + classifier pipeline is required to generate predictions.") if not MODEL_FILE.is_file() else None
    defaults = {"Source Port": 50000, "Destination Port": 443,
                "NAT Source Port": 50000, "NAT Destination Port": 443,
                "Bytes": 2048, "Bytes Sent": 1024, "Bytes Received": 1024,
                "Packets": 20, "Elapsed Time (sec)": 1.0,
                "pkts_sent": 10, "pkts_received": 10}
    with st.form("manual_predict"):
        entries = {}
        cols = st.columns(2)
        for i, feature in enumerate(features):
            with cols[i % 2]:
                is_duration = feature == "Elapsed Time (sec)"
                max_port = 65535 if "Port" in feature else None
                default = defaults.get(feature, 0)
                entries[feature] = st.number_input(
                    feature, min_value=0.0 if is_duration else 0,
                    max_value=max_port, value=float(default) if is_duration else int(default),
                    step=0.1 if is_duration else 1,
                )
        submitted = st.form_submit_button("Predict firewall action", type="primary", use_container_width=True)
    if submitted:
        if not MODEL_FILE.is_file():
            st.warning("Prediction unavailable: ask the ML teammate to export models/firewall_pipeline.joblib.")
        else:
            try:
                model = selected_model()
                result = predict_dataframe(model, pd.DataFrame([entries]), features)
                st.success(f"Predicted firewall action: **{result['Predicted Action'].iloc[0]}**")
                if "Model Confidence" in result:
                    st.metric("Model's estimated confidence", f"{result['Model Confidence'].iloc[0]:.1%}")
                st.caption("This is a model prediction, not a rule enforced by a real firewall.")
            except Exception as exc:
                st.error(f"Prediction failed. Confirm your model and feature schema: {exc}")

elif page == "Batch Prediction":
    section_heading("Batch Prediction", "Upload firewall records as CSV and export predicted actions.")
    st.caption("The CSV must contain all training input columns. The Action column is optional and is never used as input.")
    st.code(",".join(features), language="text")
    uploaded = st.file_uploader("Choose a traffic CSV", type=["csv"])
    if uploaded is not None:
        try:
            df = safe_upload(uploaded)
            st.write(f"Loaded **{len(df):,}** rows")
            st.dataframe(df.head(10), use_container_width=True)
            if not MODEL_FILE.is_file():
                st.warning("No trained pipeline was exported yet. CSV upload works, but predictions are disabled.")
            elif st.button("Run batch prediction", type="primary"):
                model = selected_model()
                output = predict_dataframe(model, df, features)
                st.success(f"Predicted actions for {len(output):,} records.")
                st.dataframe(output.head(50), use_container_width=True)
                st.subheader("Predicted action distribution")
                st.bar_chart(output["Predicted Action"].value_counts())
                st.download_button(
                    "Download predictions CSV", data=output.to_csv(index=False).encode("utf-8"),
                    file_name="firewall_predictions.csv", mime="text/csv",
                )
                st.caption("Prediction columns are model outputs; uploaded observed labels, if any, remain distinct.")
        except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as exc:
            st.error(f"Invalid CSV: {exc}")
        except Exception as exc:
            st.error(f"Prediction failed. Verify the exported pipeline and schema: {exc}")

elif page == "Model Performance":
    section_heading("Model Performance", "Display the real results saved during offline evaluation.")
    if not METRICS_FILE.is_file():
        st.info("Metrics unavailable. Export models/metrics.json from your training notebook. Do not invent metrics.")
    else:
        try:
            metrics = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
            if not isinstance(metrics, dict):
                raise ValueError("metrics.json must be a JSON object")
            st.subheader("Selected model")
            st.write(metrics.get("model_name", metadata.get("model_name", "Not specified")))
            keymap = [("Accuracy", "accuracy"), ("Macro F1", "macro_f1"),
                      ("Weighted F1", "weighted_f1")]
            metric_cols = st.columns(3)
            for col, (label, key) in zip(metric_cols, keymap):
                val = metrics.get(key)
                col.metric(label, f"{float(val):.3f}" if isinstance(val, (float, int)) else "Not provided")
            if isinstance(metrics.get("model_comparison"), list):
                st.subheader("Model comparison")
                st.dataframe(pd.DataFrame(metrics["model_comparison"]), use_container_width=True)
            if isinstance(metrics.get("confusion_matrix"), list):
                st.subheader("Confusion matrix (held-out test set)")
                cm = pd.DataFrame(metrics["confusion_matrix"])
                labels = metrics.get("class_labels")
                if isinstance(labels, list) and len(labels) == len(cm) and len(labels) == len(cm.columns):
                    cm.index = [f"Actual: {v}" for v in labels]
                    cm.columns = [f"Predicted: {v}" for v in labels]
                st.dataframe(cm, use_container_width=True)
            st.caption("All reported results must be computed on a held-out test set or clearly labeled otherwise.")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            st.error(f"Unable to load evaluation metrics: {exc}")

else:
    section_heading("About the Project", "Academic Data Mining research prototype for network security.")
    st.markdown("""
### Objective
Predict the action associated with historical firewall traffic using supervised classification.

### Labels
`Allow`, `Deny`, `Drop`, and `Reset-Both`.

### Pipeline
Historical CSV → data cleaning → fitted preprocessing → classifier → predicted action.

### Responsibilities
- Data team: cleaning, exploratory analysis and statistics
- ML team: feature engineering, training, tuning, evaluation and model export
- App/UI team: user interface, upload flow, visualization, inference integration and documentation

### Limitations
This is **not** a deployed firewall, intrusion detection system or enforcement policy.
Its results may not generalize to unseen networks or shifted traffic distributions.
Do not upload sensitive real customer traffic unless authorized.
""")
    st.caption("Dataset: UCI Internet Firewall Data | Software: Python + Streamlit + scikit-learn")
