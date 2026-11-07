import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from inference import DEFAULT_FEATURES, SCORE_COLUMN, predict_dataframe


class ScoreModel:
    classes_ = np.array(["allow", "deny"])

    def predict(self, X):
        return ["allow"] * len(X)

    def predict_proba(self, X):
        return np.tile([0.7, 0.3], (len(X), 1))


class ScoreLabelTests(unittest.TestCase):
    def test_column_is_uncalibrated_score(self):
        df = pd.DataFrame([{k: 1 for k in DEFAULT_FEATURES}])
        out = predict_dataframe(ScoreModel(), df, DEFAULT_FEATURES)
        self.assertIn(SCORE_COLUMN, out.columns)
        self.assertNotIn("Model Confidence", out.columns)
        self.assertAlmostEqual(out.loc[0, SCORE_COLUMN], 0.7)


if __name__ == "__main__":
    unittest.main()
