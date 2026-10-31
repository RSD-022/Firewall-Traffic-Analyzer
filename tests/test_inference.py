import sys
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from inference import (
    DEFAULT_FEATURES,
    auto_sum_bytes,
    auto_sum_packets,
    check_consistency_warnings,
    get_probability_table,
    predict_dataframe,
    validate_features,
)


class DummyModel:
    def predict(self, X):
        return ["Allow"] * len(X)


class InferenceTests(unittest.TestCase):
    def setUp(self):
        self.row = {key: 1 for key in DEFAULT_FEATURES}

    def test_input_valid(self):
        X = validate_features(pd.DataFrame([self.row]), DEFAULT_FEATURES)
        self.assertEqual(X.shape, (1, 11))

    def test_missing_column_fails(self):
        self.row.pop("Bytes")
        with self.assertRaisesRegex(ValueError, "Required columns missing"):
            validate_features(pd.DataFrame([self.row]), DEFAULT_FEATURES)

    def test_output(self):
        output = predict_dataframe(DummyModel(), pd.DataFrame([self.row]), DEFAULT_FEATURES)
        self.assertEqual(output.loc[0, "Predicted Action"], "Allow")

    def test_bad_port(self):
        self.row["Source Port"] = 70000
        with self.assertRaisesRegex(ValueError, "ports"):
            validate_features(pd.DataFrame([self.row]), DEFAULT_FEATURES)


class TestAutoSum(unittest.TestCase):
    def test_auto_sum_bytes(self):
        self.assertEqual(auto_sum_bytes(100, 200), 300)

    def test_auto_sum_packets(self):
        self.assertEqual(auto_sum_packets(5, 7), 12)


class TestConsistencyWarnings(unittest.TestCase):
    def test_no_warnings_when_consistent(self):
        df = pd.DataFrame([{
            "Bytes": 300, "Bytes Sent": 100, "Bytes Received": 200,
            "Packets": 10, "pkts_sent": 4, "pkts_received": 6,
        }])
        self.assertEqual(check_consistency_warnings(df), [])

    def test_bytes_mismatch(self):
        df = pd.DataFrame([{
            "Bytes": 999, "Bytes Sent": 100, "Bytes Received": 200,
            "Packets": 10, "pkts_sent": 4, "pkts_received": 6,
        }])
        warnings = check_consistency_warnings(df)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Bytes", warnings[0])

    def test_packets_mismatch(self):
        df = pd.DataFrame([{
            "Bytes": 300, "Bytes Sent": 100, "Bytes Received": 200,
            "Packets": 999, "pkts_sent": 4, "pkts_received": 6,
        }])
        warnings = check_consistency_warnings(df)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Packets", warnings[0])


class TestProbabilityTable(unittest.TestCase):
    """Test get_probability_table with a tiny fitted pipeline."""

    @classmethod
    def setUpClass(cls):
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.tree import DecisionTreeClassifier

        rng = np.random.RandomState(42)
        n = 40
        X_train = pd.DataFrame({
            f"f{i}": rng.rand(n) for i in range(3)
        })
        y_train = pd.Series(["allow", "deny", "drop", "reset-both"] * (n // 4))
        cls.pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", DecisionTreeClassifier(max_depth=2, random_state=42)),
        ])
        cls.pipe.fit(X_train, y_train)
        cls.features = [f"f{i}" for i in range(3)]
        cls.X_test = pd.DataFrame({f"f{i}": [0.5] for i in range(3)})

    def test_returns_dataframe(self):
        table = get_probability_table(self.pipe, self.X_test)
        self.assertIsNotNone(table)
        self.assertIsInstance(table, pd.DataFrame)
        self.assertEqual(table.shape[0], 1)
        self.assertEqual(table.shape[1], 4)

    def test_columns_are_classes(self):
        table = get_probability_table(self.pipe, self.X_test)
        self.assertIn("allow", table.columns)
        self.assertIn("deny", table.columns)

    def test_probabilities_sum_to_one(self):
        table = get_probability_table(self.pipe, self.X_test)
        self.assertAlmostEqual(table.iloc[0].sum(), 1.0, places=5)

    def test_no_proba_model(self):
        """Model without predict_proba returns None."""
        table = get_probability_table(DummyModel(), self.X_test)
        self.assertIsNone(table)


if __name__ == "__main__":
    unittest.main()
