#!/usr/bin/env python
"""Train a quick toy pipeline for development/testing.

This script trains a minimal DecisionTreeClassifier on data/raw/log2.csv and
saves it (along with metadata and fake metrics) to a user-specified path.
It NEVER writes into the models/ directory.

Usage:
    python tests/dev_toy_pipeline.py [OUTPUT_PATH]

Default output: /tmp/firewall_toy_pipeline.joblib

After running, set the environment variables printed by this script to use the
toy model with Streamlit:

    export FIREWALL_MODEL_FILE=/tmp/firewall_toy_pipeline.joblib
    export FIREWALL_META_FILE=/tmp/firewall_toy_metadata.json
    export FIREWALL_METRICS_FILE=tests/fixtures/sample_metrics_FAKE.json
    python -m streamlit run src/app.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "raw" / "log2.csv"

FEATURE_COLUMNS = [
    "Source Port", "Destination Port", "NAT Source Port", "NAT Destination Port",
    "Bytes", "Bytes Sent", "Bytes Received", "Packets", "Elapsed Time (sec)",
    "pkts_sent", "pkts_received",
]


def main():
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/firewall_toy_pipeline.joblib")
    meta_output = output.with_name(output.stem.replace("pipeline", "metadata") + ".json")

    if not DATA_FILE.is_file():
        print(f"ERROR: {DATA_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Reading {DATA_FILE} ...")
    df = pd.read_csv(DATA_FILE)

    X = df[FEATURE_COLUMNS]
    y = df["Action"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y,
    )

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", DecisionTreeClassifier(max_depth=5, random_state=42)),
    ])
    print("Training DecisionTreeClassifier(max_depth=5) ...")
    pipe.fit(X_train, y_train)

    train_acc = pipe.score(X_train, y_train)
    test_acc = pipe.score(X_test, y_test)
    print(f"  Train accuracy: {train_acc:.4f}")
    print(f"  Test accuracy:  {test_acc:.4f}")

    # Save model
    joblib.dump(pipe, output)
    print(f"Model saved → {output}")

    # Save metadata
    meta = {
        "model_name": "DecisionTreeClassifier (toy, max_depth=5)",
        "feature_columns": FEATURE_COLUMNS,
    }
    meta_output.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Metadata saved → {meta_output}")

    # Print env vars
    print()
    print("Set these environment variables to use the toy model:")
    print(f"  export FIREWALL_MODEL_FILE={output}")
    print(f"  export FIREWALL_META_FILE={meta_output}")
    print(f"  export FIREWALL_METRICS_FILE={ROOT / 'tests' / 'fixtures' / 'sample_metrics_FAKE.json'}")


if __name__ == "__main__":
    main()
