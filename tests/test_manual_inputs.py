import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from inference import (DEFAULT_FEATURES, apply_derived_totals,
                       predict_dataframe, validate_features)


class DummyModel:
    def predict(self, X):
        return ["allow"] * len(X)


def base_row():
    return {k: 1 for k in DEFAULT_FEATURES}


class ManualInputTests(unittest.TestCase):
    def test_bytes_total_from_submitted_values(self):
        r = apply_derived_totals({**base_row(), "Bytes Sent": 100, "Bytes Received": 200})
        self.assertEqual(r["Bytes"], 300)

    def test_packets_total_from_submitted_values(self):
        r = apply_derived_totals({**base_row(), "pkts_sent": 4, "pkts_received": 6})
        self.assertEqual(r["Packets"], 10)

    def test_original_dict_not_modified(self):
        row = {**base_row(), "Bytes Sent": 5, "Bytes Received": 5, "Bytes": 999}
        apply_derived_totals(row)
        self.assertEqual(row["Bytes"], 999)

    def test_port_443_accepted(self):
        validate_features(pd.DataFrame([{**base_row(), "Destination Port": 443}]), DEFAULT_FEATURES)

    def test_port_65535_accepted(self):
        validate_features(pd.DataFrame([{**base_row(), "Source Port": 65535}]), DEFAULT_FEATURES)

    def test_port_70000_rejected(self):
        with self.assertRaises(ValueError):
            validate_features(pd.DataFrame([{**base_row(), "Source Port": 70000}]), DEFAULT_FEATURES)

    def test_fractional_port_rejected(self):
        with self.assertRaises(ValueError):
            validate_features(pd.DataFrame([{**base_row(), "Source Port": 443.5}]), DEFAULT_FEATURES)

    def test_negative_bytes_rejected(self):
        row = apply_derived_totals({**base_row(), "Bytes Sent": -1, "Bytes Received": 0})
        with self.assertRaises(ValueError):
            validate_features(pd.DataFrame([row]), DEFAULT_FEATURES)

    def test_nan_rejected(self):
        with self.assertRaises(ValueError):
            validate_features(pd.DataFrame([{**base_row(), "Elapsed Time (sec)": float("nan")}]),
                              DEFAULT_FEATURES)

    def test_valid_input_gives_exactly_one_prediction(self):
        row = apply_derived_totals({**base_row(), "Bytes Sent": 100, "Bytes Received": 200})
        out = predict_dataframe(DummyModel(), pd.DataFrame([row]), DEFAULT_FEATURES)
        self.assertEqual(len(out), 1)
        self.assertEqual(out.loc[0, "Bytes"], 300)


if __name__ == "__main__":
    unittest.main()
