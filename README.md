
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

The goal of this project is to use Data Mining and supervised Machine Learning techniques to learn patterns from historical firewall traffic and predict the firewall action associated with a network flow.

The general prediction problem is:

Network Flow Features → Machine Learning Model → Firewall Action

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

## Data Mining Approach

This project follows a **Supervised Classification** approach.

The required Machine Learning algorithms that will be studied are:

1. Zero-R / Dummy Classifier
2. K-Nearest Neighbors
3. Decision Tree
4. Random Forest
5. Naive Bayes
6. Support Vector Machine

Hyperparameter optimization will later be performed using GridSearchCV or RandomizedSearchCV with cross-validation.

## Project Workflow

The project follows the following pipeline:

Raw Dataset
    ↓
Data Understanding
    ↓
Data Cleaning
    ↓
Exploratory Data Analysis
    ↓
Statistical Analysis
    ↓
Preprocessing
    ↓
Train / Test Split
    ↓
Machine Learning Models
    ↓
Hyperparameter Optimization
    ↓
Model Evaluation
    ↓
Model Comparison
    ↓
Streamlit Application

## Repository Structure

```text
Firewall-Traffic-Analyzer/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_eda_and_cleaning.ipynb
│   ├── 02_preprocessing_encoding.ipynb
│   └── 03_model_training_evaluation.ipynb
│
├── src/
│   ├── app.py
│   ├── preprocessing.py
│   └── models.py
│
├── docs/
│
├── README.md
├── requirements.txt
└── .gitignore