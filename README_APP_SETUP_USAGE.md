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








## Usage

### 1. Launch the Streamlit application

```bash
python -m streamlit run src/app.py
```

The app opens at **http://localhost:8501**. Use the sidebar to switch between the 8 pages. Press `Ctrl + C` in the terminal to stop it.

| Page | Use it to |
|---|---|
| Overview | See record counts, the action distribution and known limitations |
| Data Quality | Inspect duplicates, conflicting labels and outliers |
| Traffic Analytics | Filter the data and explore distributions, frequencies and correlations |
| Statistics | View the Kruskal-Wallis and Chi-square test results |
| Manual Prediction | Classify a single network flow |
| Batch Prediction | Classify many flows from a CSV file |
| Model Performance | Review the evaluation of the trained model |
| About & FAQ | Read the objective, methodology and limitations |

### 2. Run the Jupyter notebooks

**Option A: JupyterLab**
```bash
jupyter lab
```
Open the `notebooks/` folder in the browser window that appears.

**Option B: VS Code**
Open the `.ipynb` file and choose the `.venv` Python environment as the kernel (top right).

Run each notebook **from top to bottom** (Restart & Run All), in this order:

| Notebook | Purpose |
|---|---|
| `01_eda_and_cleaning.ipynb` | Exploratory analysis and data cleaning |
| `02_preprocessing_encoding.ipynb` | Encoding, scaling, and creation of the train and test files |
| `03_model_training_evaluation.ipynb` | Compares the six classifiers, tunes the best one, evaluates it once on the test set and exports the model |
| `04_ml_improvement_experiments.ipynb` | Optional: rare-class analysis, feature ablation and importance |

Notebook 03 needs the files created by Notebook 02. Model training and tuning can take several minutes (the KNN comparison alone takes about 3 minutes).

### 3. Use the classification functionality

The model predicts one of four firewall actions: `allow`, `deny`, `drop` or `reset-both`.

**Single flow (Manual Prediction)**
1. Open **Manual Prediction**.
2. Click an example (**HTTPS-like**, **SMB port 445**, **VNC port 5900**) or enter your own values.
3. Fill in the fields: Source Port, Destination Port, NAT Source Port, NAT Destination Port, Bytes Sent, Bytes Received, Packets sent, Packets received and Elapsed Time. *Bytes* and *Packets* totals are computed automatically.
4. Click **Predict firewall action**.
5. Read the predicted action and the bar chart of model scores.

**Many flows (Batch Prediction)**
1. Open **Batch Prediction**.
2. Click **Download header-only CSV template**.
3. Fill the template with your records. All the model's input columns are required. An `Action` column is optional and is never used as input.
4. Upload the file (maximum 20 MB and 100,000 rows) and check the preview and any warnings.
5. Click **Run batch prediction**.
6. Review the predictions, the distribution chart and, if your file had an `Action` column, the observed vs predicted counts.
7. Click **Download predictions CSV**.

> Model scores are not calibrated probabilities. For KNN, they are the share of neighbour votes. Predictions describe historical firewall behaviour and are not security decisions.

### 4. Where to find the results

| Result | Location |
|---|---|
| Trained model | `models/firewall_pipeline.joblib` |
| Model settings and input columns | `models/metadata.json` |
| Test metrics, confusion matrix, model comparison | `models/metrics.json` (shown on the **Model Performance** page) |
| Model comparison, feature ablation and classification report tables | `reports/` (`model_comparison.csv`, `feature_ablation.csv`, `classification_report.csv`) |
| Train and test splits | `data/processed/train.csv` and `test.csv` |
| Batch predictions | `firewall_predictions.csv`, downloaded through your browser (usually your **Downloads** folder) |
| Filtered traffic data | `filtered_firewall_data.csv`, downloaded from the **Traffic Analytics** data table tab |
