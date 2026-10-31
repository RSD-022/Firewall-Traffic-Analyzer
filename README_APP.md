# Streamlit teammate handoff — Intelligent Firewall Traffic Analyzer

This is a **ready-to-run application starter**, designed to be copied into the
existing `RSD-022/Firewall-Traffic-Analyzer` repository. It does not include a
trained model, real metrics, or the raw CSV. It never simulates fake predictions.

## 1. Ownership

**UI teammate owns:** `src/app.py`, `src/inference.py`, `.streamlit/config.toml`,
`tests/test_inference.py`, and the application documentation.

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
streamlit run src/app.py
```

You can use the repository's existing `requirements.txt` instead of the smaller
application-specific requirements if your environment is already configured.

Open the local URL printed by Streamlit (typically `http://localhost:8501`).

The current project's CSV should be at `data/raw/log2.csv`. If present, Overview
and Traffic Analytics will work immediately. Manual and Batch Prediction become
active as soon as the trained pipeline is exported.

## 3. Integration: what the ML teammate must export

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

## 4. Scope of the 6 pages

1. **Overview**: actual CSV dimensions, missing count, observed classes, preview.
2. **Traffic Analytics**: filter by observed action, explore numerical features,
   distribution chart, scatter plot, descriptive statistics.
3. **Manual Prediction**: enter raw values for one record and infer final model action.
4. **Batch Prediction**: CSV upload, input validation, predict rows, export CSV.
5. **Model Performance**: *real* saved evaluation results and confusion matrix.
6. **About**: objectives, provenance, responsibilities, research limitations.

## 5. Run tests

```bash
python -m unittest discover -s tests -v
```

## 6. GitHub workflow

```bash
git checkout -b feature/streamlit-ui
# copy the overlay files into the repository, keeping existing files
python -m unittest discover -s tests -v
git add src/app.py src/inference.py .streamlit/config.toml requirements-app.txt tests/test_inference.py README_APP.md models/README.md
git commit -m "Build Streamlit traffic analytics and prediction interface"
git push -u origin feature/streamlit-ui
```

Then create a pull request to `main`; coordinate with teammates on overlaps.

## 7. Definition of done

- [ ] Opens successfully with `streamlit run src/app.py`.
- [ ] Displays correct stats from `data/raw/log2.csv`.
- [ ] Filtered charts work with no selected labels / empty rows.
- [ ] Single predictions match `pipeline.predict()` on identical raw DataFrames.
- [ ] Batch results row count equals input row count, original columns preserved.
- [ ] Invalid/missing columns produce useful error messages.
- [ ] Model absent produces a warning (never a dummy prediction).
- [ ] Offline evaluation metrics faithfully match the model notebook.
- [ ] App README, screenshots, and demo CSV sample included in final submission.
- [ ] Model/joblib provenance and version compatibility checked before deployment.

## 8. Demo script

1. Open Overview and introduce historical traffic counts/classes.
2. Open Traffic Analytics, select a class and an interesting traffic attribute.
3. Open Manual Prediction and enter a complete realistic sample.
4. Show the predicted class and clarify its interpretation.
5. Upload a header-matching CSV and download batch predictions.
6. Open Model Performance and explain the actual held-out evaluation metrics.
7. Explain constraints: historical dataset, no live packet interception.

## 9. Boundaries

- No live packet capturing, IDS, or actual traffic blocking is implemented.
- This is an **academic classifier of historic firewall actions**.
- Do not expose private network logs on public app hosting without authorization.
- Streamlit caches the model; only load trusted joblib artifacts.
- Model scores are estimates, not guarantees or security-policy decisions.
