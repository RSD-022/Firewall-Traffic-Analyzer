"""Tests for statistical_tests module.

Skipped if data/raw/log2.csv is missing.
"""
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DATA_FILE = ROOT / "data" / "raw" / "log2.csv"


@unittest.skipUnless(DATA_FILE.is_file(), "data/raw/log2.csv not found")
class TestStatisticalTestsOriginal(unittest.TestCase):
    """Tests on the original (non-deduplicated) dataset."""

    @classmethod
    def setUpClass(cls):
        from statistical_tests import deduplicate, duplicate_summary, conflicting_label_groups
        cls.df = pd.read_csv(DATA_FILE)
        cls.dup = duplicate_summary(cls.df)
        cls.conflicts = conflicting_label_groups(cls.df)
        cls.dedup_df = deduplicate(cls.df)

    # --- Duplicate stats ---

    def test_extra_copies(self):
        self.assertEqual(self.dup["extra_copies"], 8362)

    def test_rows_in_repeated_groups(self):
        self.assertEqual(self.dup["rows_in_groups"], 13281)

    def test_distinct_rows(self):
        self.assertEqual(self.dup["distinct_rows"], 57170)

    # --- Conflicting labels ---

    def test_conflicting_groups_count(self):
        self.assertEqual(len(self.conflicts), 9)

    def test_conflicting_rows_total(self):
        total = int(self.conflicts["total_rows"].sum())
        self.assertEqual(total, 46)

    # --- Kruskal-Wallis ---

    def test_kruskal_H(self):
        from statistical_tests import kruskal_bytes_by_action
        result = kruskal_bytes_by_action(self.df)
        self.assertAlmostEqual(result["H"], 44287.9946, delta=0.01)

    def test_kruskal_epsilon_squared(self):
        from statistical_tests import kruskal_bytes_by_action
        result = kruskal_bytes_by_action(self.df)
        self.assertAlmostEqual(result["epsilon_squared"], 0.6758, delta=0.0001)

    # --- Chi-square ---

    def test_chi2(self):
        from statistical_tests import chi_square_nat_source_port
        result = chi_square_nat_source_port(self.df)
        self.assertAlmostEqual(result["chi2"], 63183.4191, delta=0.01)

    def test_chi2_df(self):
        from statistical_tests import chi_square_nat_source_port
        result = chi_square_nat_source_port(self.df)
        self.assertEqual(result["df"], 3)

    def test_cramers_v(self):
        from statistical_tests import chi_square_nat_source_port
        result = chi_square_nat_source_port(self.df)
        self.assertAlmostEqual(result["cramers_v"], 0.9819, delta=0.0001)

    def test_min_expected(self):
        from statistical_tests import chi_square_nat_source_port
        result = chi_square_nat_source_port(self.df)
        self.assertAlmostEqual(result["min_expected"], 23.43, delta=0.01)


@unittest.skipUnless(DATA_FILE.is_file(), "data/raw/log2.csv not found")
class TestStatisticalTestsDedup(unittest.TestCase):
    """Tests on the deduplicated dataset."""

    @classmethod
    def setUpClass(cls):
        from statistical_tests import deduplicate
        cls.df = deduplicate(pd.read_csv(DATA_FILE))

    def test_kruskal_H_dedup(self):
        from statistical_tests import kruskal_bytes_by_action
        result = kruskal_bytes_by_action(self.df)
        self.assertAlmostEqual(result["H"], 34770.9395, delta=0.01)

    def test_chi2_dedup(self):
        from statistical_tests import chi_square_nat_source_port
        result = chi_square_nat_source_port(self.df)
        self.assertAlmostEqual(result["chi2"], 55264.4993, delta=0.01)


class TestFormatPValue(unittest.TestCase):
    """Test format_p_value helper."""

    def test_zero(self):
        from statistical_tests import format_p_value
        self.assertIn("underflow", format_p_value(0.0))

    def test_tiny(self):
        from statistical_tests import format_p_value
        self.assertIn("underflow", format_p_value(1e-310))

    def test_normal(self):
        from statistical_tests import format_p_value
        result = format_p_value(0.05)
        self.assertIn("5.0000e-02", result)


if __name__ == "__main__":
    unittest.main()
