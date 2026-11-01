"""Reusable model construction, training, and artifact loading helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier

from src.preprocessing import get_feature_columns, make_preprocessor

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = ROOT / "models" / "firewall_pipeline.joblib"
DEFAULT_META_PATH = ROOT / "models" / "metadata.json"
DEFAULT_METRICS_PATH = ROOT / "models" / "metrics.json"

RANDOM_STATE = 42
CLASS_LABELS = ["allow", "deny", "drop", "reset-both"]

MODEL_NAMES = [
    "Dummy (Zero-R)",
    "KNN",
    "Decision Tree",
    "Random Forest",
    "Gaussian Naive Bayes",
    "Linear SVM",
]

PARAM_GRIDS: dict[str, dict[str, list[Any]]] = {
    "Dummy (Zero-R)": {"classifier__strategy": ["most_frequent", "prior"]},
    "KNN": {
        "classifier__n_neighbors": [5, 11, 21],
        "classifier__weights": ["uniform", "distance"],
    },
    "Decision Tree": {
        "classifier__max_depth": [10, 20, None],
        "classifier__min_samples_leaf": [2, 5],
    },
    "Random Forest": {
        "classifier__n_estimators": [100, 150],
        "classifier__min_samples_leaf": [2, 5],
    },
    "Gaussian Naive Bayes": {"classifier__var_smoothing": [1e-9, 1e-8, 1e-7]},
    "Linear SVM": {"classifier__C": [0.1, 1.0, 10.0]},
}


def build_model(
    model_name: str,
    feature_set: str = "full",
    random_state: int = RANDOM_STATE,
) -> Pipeline:
    """Build an end-to-end scikit-learn Pipeline with in-fold preprocessing."""
    preprocessor = make_preprocessor(feature_set)
    if model_name == "Gaussian Naive Bayes":
        preprocessor.set_params(sparse_threshold=0.0)

    estimators = {
        "Dummy (Zero-R)": DummyClassifier(strategy="most_frequent"),
        "KNN": KNeighborsClassifier(n_neighbors=11, weights="distance", n_jobs=-1),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=20,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=random_state,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=150,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=random_state,
        ),
        "Gaussian Naive Bayes": GaussianNB(),
        "Linear SVM": LinearSVC(
            C=1.0,
            class_weight="balanced",
            max_iter=8000,
            random_state=random_state,
        ),
    }
    if model_name not in estimators:
        raise KeyError(f"Unknown model: {model_name}. Expected one of {MODEL_NAMES}")

    return Pipeline([
        ("preprocessing", preprocessor),
        ("classifier", estimators[model_name]),
    ])


def evaluate_predictions(y_true: pd.Series, y_pred: Any) -> dict[str, float]:
    """Compute standard multiclass evaluation metrics on firewall actions."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "f1_macro": float(
            f1_score(y_true, y_pred, labels=CLASS_LABELS, average="macro", zero_division=0)
        ),
        "f1_weighted": float(
            f1_score(y_true, y_pred, labels=CLASS_LABELS, average="weighted", zero_division=0)
        ),
    }


def load_pipeline(model_path: Path | str = DEFAULT_MODEL_PATH) -> Pipeline:
    """Load the fitted firewall inference pipeline from disk."""
    path = Path(model_path)
    if not path.is_file():
        raise FileNotFoundError(f"Trained pipeline not found at {path}")
    return joblib.load(path)


def load_metadata(meta_path: Path | str = DEFAULT_META_PATH) -> dict[str, Any]:
    """Load model metadata JSON from disk."""
    path = Path(meta_path)
    if not path.is_file():
        raise FileNotFoundError(f"Metadata file not found at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_metrics(metrics_path: Path | str = DEFAULT_METRICS_PATH) -> dict[str, Any]:
    """Load evaluation metrics JSON from disk."""
    path = Path(metrics_path)
    if not path.is_file():
        raise FileNotFoundError(f"Metrics file not found at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def predict_flows(
    df: pd.DataFrame,
    pipeline: Pipeline | None = None,
    feature_set: str = "full",
) -> pd.Series:
    """Run predictions on a raw DataFrame using the fitted pipeline."""
    if pipeline is None:
        pipeline = load_pipeline()
    cols = get_feature_columns(feature_set)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")
    preds = pipeline.predict(df[cols])
    return pd.Series(preds, index=df.index, name="Predicted Action")