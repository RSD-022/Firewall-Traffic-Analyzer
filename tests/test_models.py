"""Unit tests for src/models.py and exported model artifacts."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models import (
    CLASS_LABELS,
    DEFAULT_META_PATH,
    DEFAULT_METRICS_PATH,
    DEFAULT_MODEL_PATH,
    MODEL_NAMES,
    PARAM_GRIDS,
    build_model,
    evaluate_predictions,
    load_metadata,
    load_metrics,
    load_pipeline,
    predict_flows,
)
from src.preprocessing import get_feature_columns


class TestModelFactory(unittest.TestCase):
    """Test model construction, training, and prediction on synthetic flows."""

    @classmethod
    def setUpClass(cls) -> None:
        rng = np.random.RandomState(42)
        n_rows = 80
        cols = get_feature_columns("full")
        data = {}
        for col in cols:
            if "Port" in col:
                data[col] = rng.choice([0, 53, 80, 443, 445, 25174], size=n_rows)
            else:
                data[col] = rng.randint(0, 5000, size=n_rows)
        cls.X_synthetic = pd.DataFrame(data)
        cls.y_synthetic = pd.Series(CLASS_LABELS * (n_rows // len(CLASS_LABELS)))

    def test_all_six_models_instantiate(self) -> None:
        self.assertEqual(len(MODEL_NAMES), 6)
        for name in MODEL_NAMES:
            pipe = build_model(name, "full")
            self.assertIn("preprocessing", pipe.named_steps)
            self.assertIn("classifier", pipe.named_steps)
            self.assertIn(name, PARAM_GRIDS)

    def test_unknown_model_raises(self) -> None:
        with self.assertRaises(KeyError):
            build_model("UnknownClassifier", "full")

    def test_all_models_fit_and_predict_full_features(self) -> None:
        for name in MODEL_NAMES:
            pipe = build_model(name, "full")
            pipe.fit(self.X_synthetic, self.y_synthetic)
            preds = pipe.predict(self.X_synthetic.head(10))
            self.assertEqual(len(preds), 10)
            self.assertTrue(set(preds).issubset(set(CLASS_LABELS)))

    def test_feature_scenarios_fit_and_predict(self) -> None:
        for scenario in ["full", "without_nat", "ports_only"]:
            cols = get_feature_columns(scenario)
            pipe = build_model("Decision Tree", scenario)
            pipe.fit(self.X_synthetic[cols], self.y_synthetic)
            preds = pipe.predict(self.X_synthetic[cols].head(5))
            self.assertEqual(len(preds), 5)

    def test_evaluate_predictions_metrics(self) -> None:
        metrics = evaluate_predictions(self.y_synthetic, self.y_synthetic)
        self.assertAlmostEqual(metrics["accuracy"], 1.0)
        self.assertAlmostEqual(metrics["f1_macro"], 1.0)
        self.assertAlmostEqual(metrics["balanced_accuracy"], 1.0)


@unittest.skipUnless(DEFAULT_MODEL_PATH.is_file(), "Exported model artifacts not found")
class TestExportedModelArtifacts(unittest.TestCase):
    """Verify exported joblib pipeline, metadata.json, and metrics.json."""

    def test_metadata_schema(self) -> None:
        meta = load_metadata()
        self.assertIn("model_name", meta)
        self.assertIn("feature_columns", meta)
        self.assertEqual(len(meta["feature_columns"]), 11)
        self.assertEqual(meta.get("class_labels", CLASS_LABELS), CLASS_LABELS)

    def test_metrics_schema(self) -> None:
        metrics = load_metrics()
        self.assertIn("test", metrics)
        self.assertIn("cv_model_comparison", metrics)
        self.assertEqual(len(metrics["cv_model_comparison"]), 6)

    def test_pipeline_inference_smoke_test(self) -> None:
        pipe = load_pipeline()
        cols = get_feature_columns("full")
        sample = pd.DataFrame([{c: 80 if "Port" in c else 120 for c in cols}])
        preds = predict_flows(sample, pipeline=pipe, feature_set="full")
        self.assertEqual(len(preds), 1)
        self.assertIn(preds.iloc[0], CLASS_LABELS)


if __name__ == "__main__":
    unittest.main()