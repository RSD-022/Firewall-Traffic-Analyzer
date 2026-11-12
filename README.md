
# Intelligent Firewall Traffic Analyzer

## Project Overview

**Intelligent Firewall Traffic Analyzer** is a Data Mining project developed in the field of computer networks and cybersecurity.

The objective is to build a supervised Machine Learning system capable of analyzing network traffic characteristics and predicting the action applied by a firewall.

The possible firewall actions are:

- Allow
- Deny
- Drop
- Reset-Both

## Problem Statement

Modern firewalls generate large amounts of network traffic logs. Analyzing these logs manually can be difficult and time-consuming.

The goal of this project is to use Data Mining and supervised Machine Learning techniques to learn patterns from historical firewall traffic and predict the firewall action associated with a network flow based on patterns learned from historical data.

The general prediction problem is:

Network Flow Features → Machine Learning Model → Firewall Action

### Scope & System Behavior

It is important to note that **this project is a predictive and analytical model, not an active enforcement agent.**

* **What it *doesn't* do:** It does not sit inline on the network path, intercept live packets, or autonomously decide to block connections in real-time (unlike an active Intrusion Prevention System or inline firewall enforcement tool).
* **What it *does* do:** It analyzes network traffic characteristics and leverages supervised machine learning to predict the most appropriate or historical action associated with a data flow.

#### Why This Predictive Role Matters

Even though the model does not execute live network blocks, its predictive capabilities provide significant value in cybersecurity operations:

1. **Policy Auditing & Consistency Checks:** If the model predicts a `Drop` or `Deny` based on deep traffic patterns, but historical logs indicate an `Allow`, it flags a potential security gap, policy conflict, or loophole in the firewall's rule base.
2. **Offline Log Intelligence:** Security teams can run bulk historical log data through the model to surface anomalies and highlight traffic that mimics blocked signatures but previously slipped through.
3. **Decision Support (Human-in-the-Loop):** It acts as an intelligent analytical assistant for security analysts, helping them understand historical decision rationales and evaluate complex or ambiguous traffic behaviors.

## Dataset

Dataset: **Internet Firewall Data**

Source: **UCI Machine Learning Repository**

Dataset URL:
https://archive.ics.uci.edu/dataset/542/internet+firewall+data

Approximate number of observations: **65,532**

Number of columns: **12**

Target variable:

`Action`

Target classes:

- Allow
- Deny
- Drop
- Reset-Both

## Features

The dataset contains network traffic information including:

- Source Port
- Destination Port
- NAT Source Port
- NAT Destination Port
- Bytes
- Bytes Sent
- Bytes Received
- Packets
- Elapsed Time
- Packets Sent
- Packets Received

The target variable is:

- Action

## App Key Features

- **Historical firewall traffic classification** (allow, deny, drop, reset-both) using supervised machine learning on the UCI Internet Firewall Data (dataset #542).
- **Data quality assessment:** duplicate detection, conflicting-label analysis and outlier screening.
- **Statistical testing:** Kruskal-Wallis (Bytes by action) and Chi-square with Cramér's V (NAT source port status by action), on original and deduplicated data.
- **Comparison of six classifiers** (Dummy baseline, KNN, Decision Tree, Random Forest, Gaussian Naive Bayes, Linear SVM) using group-aware 5-fold cross-validation and macro-F1.
- **Hyperparameter optimization** of the best model with GridSearchCV (selected: KNN, 21 neighbors, distance weighting).
- **Feature ablation and rare-class analysis**, including class weighting, permutation importance and an assessment of feature availability.
- **Interactive Streamlit dashboard** with traffic analytics, single-flow prediction, batch CSV prediction and a model performance page.
- **Trained scikit-learn pipeline** (preprocessing and classifier) exported for inference.



## Data Mining Approach

This project follows a **Supervised Classification** approach.

The required Machine Learning algorithms:

1. Zero-R / Dummy Classifier
2. K-Nearest Neighbors
3. Decision Tree
4. Random Forest
5. Naive Bayes
6. Support Vector Machine

Hyperparameter optimization are performed using GridSearchCV or RandomizedSearchCV with cross-validation.


## Project Pipeline & Architecture

**Phase 1: Data Preparation & Understanding**
= Raw Dataset Collection -> Data Understanding -> Data Cleaning 

**Phase 2: Analysis & Insights**
= Exploratory Data Analysis -> Statistical Analysis 

**Phase 3: Feature Engineering & Setup**
= Preprocessing -> Train / Test Split

**Phase 4: Modeling & Optimization**
= Machine Learning Models -> Hyperparameter Optimization -> Model Evaluation -> Model Comparison 

**Phase 5: Deployment**
= Streamlit Application





## Repository Structure

```text

├──.streamlit/                                # Streamlit configuration settings
|
├──data/                                       # Raw and processed datasets
│   ├── raw/                                   # Original dataset files
│   └── processed/                             # Cleaned and transformed datasets
|
├── docs/                                      # Academic documentation
│   ├── latex/                                 # LaTeX source files
│   ├── md/                                    # Markdown documentation
│   └── Rapport_MiniProject.pdf                # Final academic project report
│
├── models/                                    # Trained models, saved pipelines, and evaluation metadata
│   ├── firewall_pipeline.joblib               # Saved Machine Learning pipeline
│   ├── metadata.json                          # Model metadata and configuration
│   └── metrics.json                           # Model evaluation metrics
|
├── notebooks/                                 # Data analysis and ML experiments
│   ├── 01_eda_and_cleaning.ipynb              # Exploratory data analysis and data cleaning
│   ├── 02_preprocessing_encoding.ipynb        # Data preprocessing, feature transformation, and encoding
│   ├── 03_model_training_evaluation.ipynb     # Supervised model training and metric evaluation
│   └── 04_ml_improvement_experiments.ipynb    # Hyperparameter tuning and model improvement experiments
│
├── reports/                                   # Analytical outputs and generated figures
│
├── src/                                       # Main Python source implementation
│   ├── app.py                                 # Streamlit application entry point
│   ├── inference.py                           # Loads the trained pipeline and performs predictions
│   ├── preprocessing.py                       # Data preprocessing operations
│   ├── models.py                              # Machine Learning model definitions
│   ├── statistical_tests.py                   # Statistical analysis and tests
│   ├── visualization.py                       # Custom visualization functions
│   └── theme.py                               # Application styling and UI theme
│
├── tests/                                     # Automated tests for project components
│

│
├── README.md                                  # Main project documentation
├── README_APP_SETUP_USAGE.md                  # Application-specific documentation and usage guide
├── requirements.txt                           # Core project dependencies
├── requirements-app.txt                       # Web application dependencies

```

## Documentation

The following resources provide additional information about the project, its implementation, and its usage:

- **Academic Report:** [Rapport_MiniProject.pdf](docs/Rapport_MiniProject.pdf) — Detailed explanation of the problem, methodology, experiments, results, and conclusions.
- **Application User Guide:** [README_APP.md](README_APP.md) — Instructions for using the application and exploring its functionalities.
- **Jupyter Notebooks:** [notebooks/](notebooks/) — Step-by-step documentation of data exploration, preprocessing, model training, evaluation, and experiments.
- **Source Code:** [src/](src/) — Implementation of the application's main components and machine learning pipeline.




## Team Contributions

| Member | Role | Responsibilities |
|---|---|---|
| **RSD-022** | Team Leader, Data Preprocessing and EDA | Project coordination, data cleaning, exploratory analysis, preprocessing and encoding pipeline, statistical analysis |
| **RSD-020** | Machine Learning | Model training, evaluation, hyperparameter tuning and model export |
| **RSD-009** | Streamlit Application | Interactive dashboard, visualizations, prediction interfaces and model integration |
| **RSD-002** | Documentation | Project documentation, README, and reporting of features, methodology and limitations |




