import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from theme import _CSS
from visualization import confusion_matrix_heatmap, spearman_heatmap


class DesignTests(unittest.TestCase):
    def test_active_nav_rule_present(self):
        self.assertIn("label:has(input:checked)", _CSS)

    def test_radio_input_stays_keyboard_reachable(self):
        self.assertNotIn('input[type="radio"] {\n  display: none;', _CSS)

    def test_metric_values_can_wrap(self):
        self.assertIn("white-space: normal", _CSS)

    def test_spearman_heatmap_has_no_fixed_width(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": [3, 2, 1]})
        self.assertIsNone(spearman_heatmap(df).layout.width)

    def test_confusion_matrix_has_no_fixed_width(self):
        fig = confusion_matrix_heatmap([[1, 0], [0, 1]], ["a", "b"])
        self.assertIsNone(fig.layout.width)


if __name__ == "__main__":
    unittest.main()
