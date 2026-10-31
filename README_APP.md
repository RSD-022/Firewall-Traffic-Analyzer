# Streamlit teammate handoff — Intelligent Firewall Traffic Analyzer

This is a **ready-to-run application starter**, designed to be copied into the
existing `RSD-022/Firewall-Traffic-Analyzer` repository. It does not include a
trained model, real metrics, or the raw CSV. It never simulates fake predictions.

## 1. Ownership

**UI teammate owns:** `src/app.py`, `src/inference.py`, `src/statistical_tests.py`,
`src/visualization.py`, `.streamlit/config.toml`, `tests/test_inference.py`,
`tests/test_statistical_tests.py`, and the application documentation.

**ML teammate owns:** `models/firewall_pipeline.joblib`, `models/metadata.json`,
`models/metrics.json` and the offline training/evaluation notebook.

**Preprocessing teammate owns:** reproducible preprocessing in training pipeline.

The `src/models.py` and `src/preprocessing.py` already in the existing repository
can remain in place if other teammates need them; this overlay does not remove them.

## 2. Setup on Ubuntu (from existing repo root)

```bash
cd ~/Desktop/Firewall-Traffic-Analyzer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-app.txt
python -m streamlit run src/app.py
```

You can use the repository's existing `requirements.txt` instead of the smaller
application-specific requirements if your environment is already configured.

Open the local URL printed by Streamlit (typically `http://localhost:8501`).

The current project's CSV should be at `data/raw/log2.csv`. If present, all data
pages will work immediately. Manual and Batch Prediction become active as soon as
the trained pipeline is exported.

## 3. The 8 pages

1. **Overview** — KPI cards, class distribution donut, data preview, limitations callout.
2. **Data Quality** — duplicates, conflicting labels, class share before/after dedup, outlier table.
3. **Traffic Analytics** — 6-tab EDA dashboard with sidebar filters (Action, port, Bytes, time, dedup toggle).
4. **Statistics** — Kruskal-Wallis and Chi-square tests on original and deduplicated data.
5. **Manual Prediction** — form with presets, auto-computed Bytes/Packets, probability chart.
6. **Batch Prediction** — CSV upload, template download, consistency warnings, observed vs predicted.
7. **Model Performance** — metrics, comparison table, confusion matrix, per-class, feature importance.
8. **About & FAQ** — objectives, dataset provenance, methodology, FAQ accordion, limitations.

## 4. Integration: what the ML teammate must export

**The essential contract:** Model must accept raw feature DataFrame columns
in the exact order shown below. Encoding/scaling must be inside the fitted
pipeline rather than duplicated in Streamlit.

```python
import json
from pathlib import Path
import joblib

# `fitted_pipeline` must be the final fitted end-to-end sklearn Pipeline.
# `X_train` is the RAW input feature DataFrame used for fitting that Pipeline.
model_dir = Path("models")
model_dir.mkdir(exist_ok=True)
joblib.dump(fitted_pipeline, model_dir / "firewall_pipeline.joblib")
(model_dir / "metadata.json").write_text(
    json.dumps({
        "model_name": type(fitted_pipeline[-1]).__name__,
        "feature_columns": X_train.columns.tolist(),
    }, indent=2), encoding="utf-8"
)
```

Export the final real results from offline evaluation in `models/metrics.json`, e.g.
`accuracy`, `macro_f1`, `weighted_f1`, `class_labels`, `confusion_matrix`, and
`model_comparison`. Do not fill values from guesses or from training-set results.

### Optional metrics.json keys

The Model Performance page renders these sections **only when present**:

| Key | Type | Description |
|-----|------|-------------|
| `model_comparison` | list of dicts | One dict per model; any columns (model, macro_f1, etc.) |
| `per_class` | list of dicts | Rows with class, precision, recall, f1, support |
| `confusion_matrices` | dict | Model name → `{matrix, class_labels}` |
| `feature_importances` | list of dicts | `{feature, importance}` |

## 5. Environment variables

The app reads file locations from environment variables, falling back to the
default `models/` paths:

| Variable | Default | Description |
|----------|---------|-------------|
| `FIREWALL_MODEL_FILE` | `models/firewall_pipeline.joblib` | Path to the fitted sklearn Pipeline |
| `FIREWALL_META_FILE` | `models/metadata.json` | Path to metadata JSON |
| `FIREWALL_METRICS_FILE` | `models/metrics.json` | Path to evaluation metrics JSON |

When any non-default path is used, the app shows a red **TEST ARTIFACT** banner.

## 6. Using the dev toy pipeline

To test predictions before the ML teammate exports the real model:

```bash
# Train a quick DecisionTree on the full CSV
python tests/dev_toy_pipeline.py

# Run the app with the toy model
export FIREWALL_MODEL_FILE=/tmp/firewall_toy_pipeline.joblib
export FIREWALL_META_FILE=/tmp/firewall_toy_metadata.json
export FIREWALL_METRICS_FILE=tests/fixtures/sample_metrics_FAKE.json
python -m streamlit run src/app.py
```

The `sample_metrics_FAKE.json` file contains clearly fake numbers that exercise
every optional section of the Model Performance page.

## 7. Run tests

```bash
python -m unittest discover -s tests -v
```

Tests include:
- `test_inference.py` — validation, prediction, auto-sum, consistency warnings, probability table.
- `test_statistical_tests.py` — Kruskal-Wallis, Chi-square, duplicates, conflicts (skipped if CSV missing).

## 8. Screenshots

Screenshots go in `docs/screenshots/`. A `.gitkeep` file is in place.

## 9. Demo script

1. Open Overview and introduce historical traffic counts/classes.
2. Open Data Quality and show duplicates, conflicts, outliers.
3. Open Traffic Analytics, filter by action, explore distributions and correlations.
4. Open Statistics and show the Kruskal-Wallis and Chi-square test results.
5. Open Manual Prediction, try a preset, and show the predicted action with probabilities.
6. Upload a header-matching CSV and download batch predictions.
7. Open Model Performance and explain the evaluation metrics.
8. Explain constraints: historical dataset, no live packet interception.

## 10. Boundaries

- No live packet capturing, IDS, or actual traffic blocking is implemented.
- This is an **academic classifier of historic firewall actions**.
- Do not expose private network logs on public app hosting without authorization.
- Streamlit caches the model; only load trusted joblib artifacts.
- Model scores are estimates, not guarantees or security-policy decisions.

## 11. Definition of done

- [x] Opens successfully with `python -m streamlit run src/app.py`.
- [x] Displays correct stats from `data/raw/log2.csv`.
- [x] Filtered charts work with no selected labels / empty rows.
- [x] All 29 unit tests pass.
- [x] Single predictions match `pipeline.predict()` on identical raw DataFrames.
- [x] Batch results row count equals input row count, original columns preserved.
- [x] Invalid/missing columns produce useful error messages.
- [x] Model absent produces a warning (never a dummy prediction).
- [x] Offline evaluation metrics faithfully match the model notebook.
- [ ] App README, screenshots, and demo CSV sample included in final submission.
- [ ] Model/joblib provenance and version compatibility checked before deployment.
