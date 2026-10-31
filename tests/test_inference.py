import sys
from pathlib import Path
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from inference import DEFAULT_FEATURES, predict_dataframe, validate_features


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


if __name__ == "__main__":
    unittest.main()
