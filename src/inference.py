"""Trustworthy inference helpers shared by Streamlit and unit tests.

The saved joblib must contain a *fitted full sklearn Pipeline* (preprocessing +
classifier). Never pass untrusted joblib artifacts to joblib.load.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

DEFAULT_FEATURES = [
    "Source Port", "Destination Port", "NAT Source Port", "NAT Destination Port",
    "Bytes", "Bytes Sent", "Bytes Received", "Packets", "Elapsed Time (sec)",
    "pkts_sent", "pkts_received",
]
EXPECTED_CLASSES = ("allow", "deny", "drop", "reset-both")


def get_features(metadata: dict[str, Any] | None = None) -> list[str]:
    if metadata and isinstance(metadata.get("feature_columns"), list):
        fields = metadata["feature_columns"]
        if fields and all(isinstance(x, str) for x in fields):
            return fields
    return DEFAULT_FEATURES.copy()


def load_metadata(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("metadata.json must contain an object")
    return raw


def load_trusted_pipeline(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"Missing trained model: {path}")
    return joblib.load(path)


def validate_features(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    if df.empty:
        raise ValueError("There are no data rows to predict.")
    if not df.columns.is_unique:
        raise ValueError("Duplicate CSV column names are not supported.")
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError("Required columns missing: " + ", ".join(missing))
    X = df.loc[:, columns].copy()
    for col in columns:
        X[col] = pd.to_numeric(X[col], errors="coerce")
    if X.isna().any().any():
        bad = X.columns[X.isna().any()].tolist()
        raise ValueError("Missing or non-numeric values in: " + ", ".join(bad))
    if not bool(np.isfinite(X.to_numpy(dtype=float)).all()):
        raise ValueError("All input values must be finite numbers.")
    if (X < 0).any().any():
        raise ValueError("Traffic counters, durations and ports cannot be negative.")
    for col in ("Source Port", "Destination Port", "NAT Source Port", "NAT Destination Port"):
        if col in X.columns and ((X[col] > 65535) | (X[col] % 1 != 0)).any():
            raise ValueError(f"{col} must contain integer ports between 0 and 65535.")
    return X


def predict_dataframe(model, df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    X = validate_features(df, features)
    pred = model.predict(X)
    if len(pred) != len(df):
        raise ValueError("Prediction length does not match input rows.")
    out = df.copy()
    out["Predicted Action"] = pred
    if hasattr(model, "predict_proba"):
        try:
            proba = np.asarray(model.predict_proba(X))
            if proba.ndim == 2 and proba.shape[0] == len(X):
                out["Model Confidence"] = np.round(proba.max(axis=1), 4)
        except (AttributeError, NotImplementedError):
            pass  # Some classifiers/pipelines do not expose probabilities.
    return out
