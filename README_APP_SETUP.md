## Installation and Setup

### What you need
- Python 3.11 or newer
- Git
- About 1 GB of free disk space
- (Optional) VS Code or JupyterLab, only if you want to run the notebooks

Check your Python version first:

```bash
python --version        # on Linux/macOS you may need: python3 --version
```

---

### Step 1: Download the project
```bash
git clone <https://github.com/RSD-022/Firewall-Traffic-Analyzer.git>
cd Firewall-Traffic-Analyzer
```

### Step 2: Create a virtual environment
A virtual environment keeps the project's packages separate from the rest of your computer.

```bash
python -m venv .venv
```

Activate it:

| System | Command |
|---|---|
| Linux / macOS | `source .venv/bin/activate` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (Command Prompt) | `.venv\Scripts\activate.bat` |

You should now see `(.venv)` at the start of your terminal line. Repeat this activation command every time you open a new terminal.

### Step 3: Install the packages
```bash
python -m pip install -r requirements.txt
```

This installs the dashboard (Streamlit, Plotly), the machine learning tools (scikit-learn, pandas, NumPy, SciPy), the notebook tools (JupyterLab) and the test tool (pytest). All versions are fixed in `requirements.txt` so everyone gets the same setup.

> **Important:** keep scikit-learn at version **1.9.1**. The trained model file was saved with that version and may not load with another.
> A lighter `requirements-app.txt` (dashboard only) exists in the repository , Use it if you only want to run the app and not the notebooks.

### Step 4: Add the dataset
1. Download the **UCI Internet Firewall Data** (dataset #542) from the UCI Machine Learning Repository. from "https://archive.ics.uci.edu/dataset/542/internet+firewall+data"
2. Save the file as:

```
data/raw/log2.csv
```

Create the `data/raw/` folders if they don't exist. Without this file, the Overview, Data Quality, Traffic Analytics and Statistics pages show a message asking you to add it.

### Step 5: Get the trained model
The prediction pages need three files in the `models/` folder:

| File | What it is |
|---|---|
| `firewall_pipeline.joblib` | The trained model (preprocessing and classifier) |
| `metadata.json` | Expected input columns and class labels |
| `metrics.json` | Evaluation results for the Model Performance page |

**If these files are already in `models/`, skip to Step 6.**

If not, create them by running these notebooks from top to bottom (JupyterLab or VS Code, using the `.venv` kernel):

1. `notebooks/01_eda_and_cleaning.ipynb`
2. `notebooks/02_preprocessing_encoding.ipynb` (creates the train and test files)
3. `notebooks/03_model_training_evaluation.ipynb` (trains the models and exports the three files above)

Notebook 04 (`04_ml_improvement_experiments.ipynb`) is optional and only adds extra analysis.

### Step 6: Start the dashboard
Run this from the project's main folder:

```bash
python -m streamlit run src/app.py
```

Your browser should open automatically. If not, go to **http://localhost:8501**. To stop the app, press `Ctrl + C` in the terminal.

### Step 7: Check that it works
Open each page in the sidebar:

| Page | What you should see |
|---|---|
| Overview | Record counts and an action distribution chart |
| Data Quality | Duplicate, conflict and outlier tables |
| Traffic Analytics | Filters and chart tabs |
| Statistics | Kruskal-Wallis and Chi-square results |
| Manual Prediction | A form that returns a predicted action |
| Batch Prediction | CSV upload and prediction download |
| Model Performance | Accuracy, macro-F1, confusion matrix |
| About & FAQ | Project objective, methodology, limitations |

If a page shows a warning instead, see Troubleshooting below.

---

### Optional: run the automated tests
```bash
python -m pytest -q
```

### Optional: try the app without the real model
To test the prediction pages before running Notebook 03, you can use a quick demo model:

```bash
# 1. Create a demo model (requires data/raw/log2.csv)
python tests/dev_toy_pipeline.py

# 2. Point the app to it (Linux / macOS)
export FIREWALL_MODEL_FILE=/tmp/firewall_toy_pipeline.joblib
export FIREWALL_META_FILE=/tmp/firewall_toy_metadata.json
export FIREWALL_METRICS_FILE=tests/fixtures/sample_metrics_FAKE.json

# 3. Start the app
python -m streamlit run src/app.py
```

On Windows PowerShell, use `$env:FIREWALL_MODEL_FILE="..."` instead of `export`. The app then shows a red **TEST ARTIFACT** banner. The demo model and its metrics are for testing only and must never be reported as the project's results.

---

### Troubleshooting

| Problem | Solution |
|---|---|
| `python` or `pip` not found | Reinstall Python and tick "Add Python to PATH", or use `python3`. |
| Import errors (`No module named ...`) | Activate the virtual environment (Step 2) and run commands from the project's main folder. |
| "Default dataset not found" | Add `data/raw/log2.csv` (Step 4). |
| "No trained pipeline found" | Add or generate the files in `models/` (Step 5). |
| "Metrics unavailable" | `models/metrics.json` is missing. Run Notebook 03. |
| Model fails to load | Run `pip show scikit-learn` and check that the version is 1.9.1. |
| Port 8501 already in use | Run `python -m streamlit run src/app.py --server.port 8502`. |
| "Invalid CSV" on Batch Prediction | Use the template from the page. The file must contain every model input column, be under 20 MB, and have at most 100,000 rows. |

---
