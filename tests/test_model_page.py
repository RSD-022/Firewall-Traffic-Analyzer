import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from visualization import confusion_matrix_heatmap, metric_comparison_bar

import pandas as pd

M = [[10, 1], [3, 2]]
L = ["a", "b"]


class ModelPageTests(unittest.TestCase):
    def test_counts_axis_title(self):
        fig = confusion_matrix_heatmap(M, L, normalize=False)
        self.assertIn("absolute counts", fig.layout.yaxis.title.text)

    def test_normalized_axis_title(self):
        fig = confusion_matrix_heatmap(M, L, normalize=True)
        self.assertIn("row-normalized", fig.layout.yaxis.title.text)

    def test_normalized_rows_sum_to_one(self):
        fig = confusion_matrix_heatmap(M, L, normalize=True)
        for row in fig.data[0].z:
            self.assertAlmostEqual(sum(row), 1.0)

    def test_comparison_title_says_cross_validation(self):
        df = pd.DataFrame({"model": ["x"], "f1_macro_mean": [0.5]})
        fig = metric_comparison_bar(df, "f1_macro_mean")
        self.assertIn("Cross-validation", fig.layout.title.text)

    @unittest.skipUnless((ROOT / "models" / "metrics.json").is_file(), "no metrics.json")
    def test_real_metrics_have_test_scores(self):
        m = json.loads((ROOT / "models" / "metrics.json").read_text())
        self.assertIn("accuracy", m.get("test", m))


if __name__ == "__main__":
    unittest.main()
