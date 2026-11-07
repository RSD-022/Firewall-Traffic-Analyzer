import io
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from inference import (DEFAULT_FEATURES, EXPECTED_CLASSES, predict_dataframe,
                       read_batch_csv)


class Upload(io.BytesIO):
    def __init__(self, data, size=None):
        super().__init__(data)
        self.size = len(data) if size is None else size


def csv_bytes(rows, columns=None):
    return pd.DataFrame(rows, columns=columns or DEFAULT_FEATURES).to_csv(index=False).encode()


def good_rows(n=3):
    return [[1] * len(DEFAULT_FEATURES) for _ in range(n)]


class CycleModel:
    def predict(self, X):
        return [EXPECTED_CLASSES[i % 4] for i in range(len(X))]


class BatchCsvTests(unittest.TestCase):
    def test_empty_file(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            read_batch_csv(Upload(b""))

    def test_header_only_has_no_rows(self):
        df = read_batch_csv(Upload((",".join(DEFAULT_FEATURES) + "\n").encode()))
        with self.assertRaisesRegex(ValueError, "no data rows"):
            predict_dataframe(CycleModel(), df, DEFAULT_FEATURES)

    def test_garbage_bytes_rejected(self):
        with self.assertRaises(ValueError):
            read_batch_csv(Upload(b"\xff\xfe\x00\x81\x82\x83\xff"))

    def test_missing_column(self):
        cols = [c for c in DEFAULT_FEATURES if c != "Bytes"]
        df = read_batch_csv(Upload(csv_bytes([[1] * 10], cols)))
        with self.assertRaisesRegex(ValueError, "Required columns missing: Bytes"):
            predict_dataframe(CycleModel(), df, DEFAULT_FEATURES)

    def test_wrong_header_names(self):
        df = read_batch_csv(Upload(csv_bytes(good_rows(), [f"x{i}" for i in range(11)])))
        with self.assertRaisesRegex(ValueError, "Required columns missing"):
            predict_dataframe(CycleModel(), df, DEFAULT_FEATURES)

    def test_non_numeric_value(self):
        rows = good_rows(); rows[1][4] = "abc"
        df = read_batch_csv(Upload(csv_bytes(rows)))
        with self.assertRaisesRegex(ValueError, "non-numeric"):
            predict_dataframe(CycleModel(), df, DEFAULT_FEATURES)

    def test_negative_value(self):
        rows = good_rows(); rows[0][4] = -5
        df = read_batch_csv(Upload(csv_bytes(rows)))
        with self.assertRaisesRegex(ValueError, "negative"):
            predict_dataframe(CycleModel(), df, DEFAULT_FEATURES)

    def test_port_above_65535(self):
        rows = good_rows(); rows[2][0] = 70000
        df = read_batch_csv(Upload(csv_bytes(rows)))
        with self.assertRaisesRegex(ValueError, "ports"):
            predict_dataframe(CycleModel(), df, DEFAULT_FEATURES)

    def test_size_limit(self):
        with self.assertRaisesRegex(ValueError, "larger than"):
            read_batch_csv(Upload(csv_bytes(good_rows()), size=21 * 1024 * 1024))

    def test_row_limit(self):
        with self.assertRaisesRegex(ValueError, "More than"):
            read_batch_csv(Upload(csv_bytes(good_rows(5))), max_rows=3)

    def test_row_count_and_known_labels(self):
        df = read_batch_csv(Upload(csv_bytes(good_rows(9))))
        out = predict_dataframe(CycleModel(), df, DEFAULT_FEATURES)
        self.assertEqual(len(out), len(df))
        self.assertTrue(set(out["Predicted Action"]).issubset(set(EXPECTED_CLASSES)))

    def test_action_column_kept_and_not_used_as_input(self):
        data = pd.DataFrame(good_rows(2), columns=DEFAULT_FEATURES)
        data["Action"] = ["allow", "deny"]
        df = read_batch_csv(Upload(data.to_csv(index=False).encode()))
        out = predict_dataframe(CycleModel(), df, DEFAULT_FEATURES)
        self.assertIn("Action", out.columns)
        self.assertEqual(len(out), 2)

    def test_header_spaces_are_stripped(self):
        header = ", ".join(DEFAULT_FEATURES)
        body = ",".join(["1"] * 11)
        df = read_batch_csv(Upload(f"{header}\n{body}\n".encode()))
        self.assertEqual(list(df.columns), DEFAULT_FEATURES)

    def test_template_header_matches_features(self):
        template = ",".join(DEFAULT_FEATURES) + "\n"
        df = read_batch_csv(Upload(template.encode()))
        self.assertEqual(list(df.columns), DEFAULT_FEATURES)


if __name__ == "__main__":
    unittest.main()
