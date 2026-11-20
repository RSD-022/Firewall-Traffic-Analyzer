# Intelligent Firewall Traffic Analyzer

Data Mining mini-project (EMP, 2026/2027) — supervised classification of firewall log records into the action taken by the firewall: `allow`, `deny`, `drop` or `reset-both`.

**Contents:** [1. Context, objectives and dataset](#1-context-objectives-and-dataset) · [2. Installation and local execution](#2-installation-and-local-execution) · [3. Team roles and contribution matrix](#3-team-roles-and-contribution-matrix) · [4. Key results](#4-key-results) · [Repository structure](#repository-structure) · [Documentation](#documentation)

---

## 1. Context, objectives and dataset

### Problem statement

Modern firewalls generate large amounts of traffic logs that are hard to analyse by hand. This project uses data mining and supervised machine learning to learn, from historical logs, which action the firewall applied to a network flow, and to predict it for new flows:

`Network flow features  →  Machine learning model  →  Firewall action`

### Objectives

1. Clean and explore the data, and test statistical hypotheses about the relation between traffic features and the firewall action.
2. Train, tune and compare the six classifiers of the course (Zero-R, KNN, Decision Tree, Random Forest, Naive Bayes, SVM) with a leakage-free protocol.
3. Deploy the selected model in an interactive Streamlit application (traffic analytics, single-flow and batch prediction, model performance).

### Scope and system behaviour

This project is a **predictive and analytical model, not an active enforcement agent**. It does not sit inline on the network path or block connections in real time. It predicts the historical action associated with a flow, which is useful for:

1. **Policy auditing:** a flow predicted as `deny`/`drop` but logged as `allow` points to a possible gap or conflict in the rule base.
2. **Offline log intelligence:** bulk historical logs can be scored to surface traffic that resembles blocked signatures.
3. **Decision support:** an analytical assistant that helps analysts understand past decisions on ambiguous traffic.

### Dataset

| Item | Value |
|---|---|
| Name and source | Internet Firewall Data — [UCI Machine Learning Repository #542](https://archive.ics.uci.edu/dataset/542/internet+firewall+data) |
| Size | 65,532 records × 12 columns (11 features + target), no missing values; `data/raw/log2.csv` (2.9 MB) is included in the repository |
| Features | Source Port, Destination Port, NAT Source Port, NAT Destination Port, Bytes, Bytes Sent, Bytes Received, Packets, Elapsed Time (sec), pkts_sent, pkts_received |
| Target | `Action` — allow (57.4 %), deny (22.9 %), drop (19.6 %), reset-both (0.08 %, 54 records) |
| After cleaning | 8,362 exact duplicates removed → 57,170 unique records; group-aware 80/20 split: 45,736 train / 11,434 test |

Ports are treated as **categorical identifiers** (one-hot encoded, ports seen fewer than 50 times grouped as "infrequent"), not as quantities. Byte, packet and time features are heavily right-skewed and are transformed with `log1p` followed by standardisation.

---

## 2. Installation and local execution

**Requirements:** Python 3.11 or newer, Git. Tested on Linux with Python 3.14 and scikit-learn 1.9.1.

```bash
# 1. Clone the repository
git clone https://github.com/RSD-022/Firewall-Traffic-Analyzer.git
cd Firewall-Traffic-Analyzer

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3a. Install the application dependencies (enough to run the dashboard)
pip install -r requirements-app.txt

# 3b. Or install everything needed to re-run the notebooks
pip install -r requirements.txt

# 4. Launch the application (opens http://localhost:8501)
streamlit run src/app.py

# 5. Run the automated tests (88 tests)
pytest -q
```

The dataset, the trained pipeline (`models/firewall_pipeline.joblib`) and its metrics are included, so the application works immediately after installation; no download is needed.

**Reproducing the results.** Run the notebooks in order from the repository root:

| Notebook | Purpose | Main outputs |
|---|---|---|
| `01_eda_and_cleaning` | Data quality audit, EDA, statistical tests | cleaned data, EDA figures |
| `02_preprocessing_encoding` | Deduplication, group-aware train/test split, encoding design | `data/processed/train.csv`, `test.csv` |
| `03_model_training_evaluation` | First benchmark, feature ablations, leakage audits | `reports/*.csv` |
| `04_ml_improvement_experiments` | Rare-class experiments (class weights, thresholds, importance) | `reports/*.csv` |
| `05_full_tuning_benchmark` | GridSearchCV on all six models, ROC/PR curves, significance tests (≈ 20–30 min) | `reports/tuning/`, `docs/latex/figures/ch05/` |
| `06_final_model_export` | Final model selection and export for the application | `models/`, decision-tree rules |
| `07_statistical_tests` | Assumption checks, Kruskal–Wallis on all features, Dunn post-hoc, χ², Spearman | `reports/*tests*.csv`, `docs/latex/figures/ch03/` |

Detailed usage of each application page: [README_APP_SETUP_USAGE.md](README_APP_SETUP_USAGE.md).

---

## 3. Team roles and contribution matrix

Members are identified by their student codes only.

| Code | Role | Main responsibilities |
|---|---|---|
| **RSD-022** | Team leader — data preparation, EDA and statistics | Coordination, data cleaning, EDA, statistical tests, preprocessing pipeline, final tuning benchmark and model export |
| **RSD-020** | Machine learning | Model training and evaluation, first benchmark, ablations and rare-class experiments |
| **RSD-009** | Streamlit application | Dashboard architecture, visualisations, prediction pages, model integration, automated tests |
| **RSD-002** | Documentation | README, application guide, report |

**Contribution matrix** (● main author, ○ contributor):

| Deliverable | RSD-022 | RSD-020 | RSD-009 | RSD-002 |
|---|:-:|:-:|:-:|:-:|
| Data cleaning, EDA and statistical tests (`notebooks/01`, `07`, `src/statistical_tests.py`) | ● | ○ | ○ | |
| Preprocessing and split (`notebooks/02`, `src/preprocessing.py`) | ● | ○ | | |
| Model benchmark and ablations (`notebooks/03`, `04`, `src/models.py`) | ○ | ● | | |
| Full tuning and final model (`notebooks/05`, `06`, `models/`) | ● | | | |
| Streamlit application (`src/app.py`, `visualization.py`, `theme.py`, `inference.py`) | | ○ | ● | |
| Automated tests (`tests/`) | ○ | ○ | ● | |
| Documentation (`README*.md`) | ○ | | ○ | ● |
| Report (`docs/latex/`, `docs/Rapport_MiniProject.pdf`) | ● | ○ | ○ | ● |

The full per-member history is visible with `git shortlog -sn --no-merges` and in the merged pull requests.

---

## 4. Key results

### Evaluation protocol

- **Group-aware cross-validation:** `StratifiedGroupKFold(n_splits=5)` on the training set, where the group is a hash of the 11 features, so identical flows never appear in both the training and validation folds (otherwise duplicates would inflate the scores).
- **Selection metric: macro-F1.** Accuracy is misleading here (predicting `allow` everywhere already gives 57 %); macro-F1 gives the rare `reset-both` class the same weight as `allow`.
- **Hyperparameter optimisation:** `GridSearchCV` on **every** model, inside the same folds, with the preprocessing refitted in each fold (no leakage). The test set is used once, after selection.

### Model comparison

CV = mean ± standard deviation of macro-F1 over the 5 folds; test = held-out set (11,434 flows, 11 `reset-both`).

| Model | Best hyperparameters (GridSearchCV) | CV macro-F1 | Test macro-F1 | Test ROC-AUC (OvR) | Reset-both recall | ms / 1,000 flows |
|---|---|---|---|---|---|---|
| **Decision Tree (selected)** | gini, max_depth = 20, min_samples_leaf = 1, ccp_alpha = 0 | 0.8478 ± 0.038 | **0.790** | **0.998** | 1 / 11 | **8.6** |
| Random Forest | 200 trees, max_features = 0.5, min_samples_leaf = 2 | 0.8479 ± 0.038 | 0.790 | 0.998 | 1 / 11 | 692 |
| KNN | k = 5, Manhattan distance, distance weighting | 0.8478 ± 0.038 | 0.790 | 0.931 | 1 / 11 | 243 |
| SVM (SVC)¹ | RBF kernel, C = 10, γ = scale | 0.8417 ± 0.052 | 0.790 | 0.996 | 1 / 11 | 13 |
| Gaussian Naive Bayes | var_smoothing = 1e-5 | 0.7076 ± 0.006 | 0.710 | 0.993 | **11 / 11** | 7.4 |
| Zero-R (baseline) | majority class (`most_frequent`), fixed | 0.1979 ± 0.000 | 0.198 | 0.500 | 0 / 11 | 13.0 |

¹ Kernel SVC was tuned on a stratified sample of 12,043 training rows (≤ 4,000 per class, all `reset-both` rows) because its cost grows about quadratically with the number of rows. Kernel study: RBF 0.842 > polynomial 0.836 ≈ linear 0.836.

### Statistical tests

Main analysis on the 57,170 unique flows (duplicates would violate the independence assumption); results on the original data are given as a sensitivity check in `notebooks/07_statistical_tests.ipynb`. With n ≈ 57,000 almost every test is significant, so conclusions rest on **effect sizes**.

| # | Test | Question | Why this test | Result |
|---|---|---|---|---|
| 1 | Shapiro–Wilk, Brown–Forsythe | Are the ANOVA assumptions (normality, equal variances) met? | Must be checked before choosing between ANOVA and a rank-based test | Normality rejected in all four actions even after log1p (largest p = 2.1e-6); variances differ (W = 6,217, p < 1e-300) → **ANOVA is not valid, non-parametric tests are used** |
| 2 | Kruskal–Wallis + ε², BH correction | Does each numeric feature differ between actions? | Non-parametric alternative to ANOVA for 4 independent groups; 7 features tested, so false-discovery-rate correction | All 7 features differ (p < 1e-300). Largest effects: Elapsed Time ε² = 0.70, Packets 0.66, Bytes 0.61 |
| 3 | Dunn post-hoc (Holm) + Cliff's δ | Which pairs of actions differ? | Kruskal–Wallis only says that *some* group differs; Dunn uses the same ranks, δ measures each difference | Every pair with `allow` differs strongly (\|δ\| ≥ 0.7). Elapsed Time does **not** separate deny / drop / reset-both (δ ≈ 0, p = 1). deny vs reset-both differ on Bytes (δ = −0.50, p = 5e-7) but on only 54 flows |
| 4 | χ² of independence + Cramér's V | Are NAT source-port status and destination port associated with the action? | Two categorical variables; Cochran's rule checked; Monte Carlo p-value (999 permutations) when expected counts < 5 | NAT status: χ² = 55,264, df = 3, V = 0.98. Destination port (top 10 + other): χ² = 88,899, df = 30, V = 0.72, Monte Carlo p = 0.001 |
| 5 | Spearman ρ, BH correction | Which numeric features are redundant? | Skewed, non-normal data → rank correlation instead of Pearson | Volume features are almost collinear (Bytes Received–pkts_received ρ = 0.98, Bytes–Bytes Sent 0.95), which explains their near-zero permutation importance |
| 6 | Friedman | Do the three best models differ in CV macro-F1? | Non-parametric test for k ≥ 3 models evaluated on the same folds | χ² = 0.93, p = 0.63 → **no significant difference** |
| 7 | McNemar (exact) | Do Random Forest and Decision Tree make different errors on the test set? | Standard paired test for two classifiers on one test set | 0 discordant flows, p = 1 → identical predictions |

### Interpretation and final choice

- Random Forest, KNN and Decision Tree are statistically tied on macro-F1. Following the selection rule fixed before looking at the test set (*among statistically tied models, keep the simplest and fastest*), the **Decision Tree** is deployed: it can be read as firewall-like rules, predicts ~80× faster than the Random Forest, and its scores separate the classes much better than KNN's (ROC-AUC 0.998 vs 0.931).
- The three large classes are almost perfectly classified (F1 ≥ 0.995). The limit is **`reset-both`**: 10 of its 11 test flows are predicted as `deny`, because both actions block the connection and have nearly identical traffic profiles. Only 43 training examples exist. Naive Bayes recalls all of them but wrongly labels about 31 % of `deny` flows as `reset-both`, a trade-off that is discussed in the report.
- The most important inputs (permutation importance on the test set) are **Elapsed Time** and **Destination Port**, followed by NAT Destination Port, Packets and Bytes Sent. The first split of the tree separates flows by duration; ports 445, 3389, 22 and 53 then route flows to `drop`, `reset-both`, `deny` and `allow` branches.
- **Limitations:** NAT ports and elapsed time may only be known after the firewall's decision (feature-availability analysis in `notebooks/03_model_training_evaluation.ipynb` and `reports/feature_availability.csv`); the data come from a single network; historical labels reflect one firewall policy, not ground truth.

---

## Repository structure

```text
├── .streamlit/                         Streamlit configuration
├── data/
│   ├── raw/log2.csv                    Original UCI dataset
│   └── processed/                      Group-aware train/test split
├── docs/
│   ├── latex/                          Report LaTeX sources and figures
│   └── Rapport_MiniProject.pdf         Final academic report
├── models/
│   ├── firewall_pipeline.joblib        Fitted preprocessing + classifier pipeline
│   ├── metadata.json                   Selected model, features, hyperparameters
│   └── metrics.json                    Test and cross-validation results shown in the app
├── notebooks/                          01 → 07 (see section 2)
├── reports/                            CSV outputs; reports/tuning/ = grid searches and final comparison
├── src/
│   ├── app.py                          Streamlit application entry point
│   ├── inference.py                    Loads the pipeline and predicts
│   ├── preprocessing.py                ColumnTransformer and feature sets
│   ├── models.py                       Model definitions and artifact loading
│   ├── statistical_tests.py            Statistical tests used in the EDA
│   ├── visualization.py                Plotly figures
│   └── theme.py                        Application theme
├── tests/                              Automated tests (pytest)
├── README.md
├── README_APP_SETUP_USAGE.md           Application user guide
├── requirements.txt                    Full environment (notebooks + app)
└── requirements-app.txt                Application only
```

## Documentation

- **Academic report:** [docs/Rapport_MiniProject.pdf](docs/Rapport_MiniProject.pdf)
- **Application user guide:** [README_APP_SETUP_USAGE.md](README_APP_SETUP_USAGE.md)
- **Notebooks:** [notebooks/](notebooks/)
