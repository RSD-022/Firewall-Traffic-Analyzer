
"""
Preprocessing utilities for the
Intelligent Firewall Traffic Analyzer.

This module provides reusable preprocessing pipelines
for firewall traffic classification.
"""

import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import (
    StandardScaler,
    OneHotEncoder,
    FunctionTransformer
)


# 1. Define traffic measurement features

TRAFFIC_FEATURES = [
    "Bytes",
    "Bytes Sent",
    "Bytes Received",
    "Packets",
    "Elapsed Time (sec)",
    "pkts_sent",
    "pkts_received"
]


# 2. Define port features

PORT_FEATURES = [
    "Source Port",
    "Destination Port",
    "NAT Source Port",
    "NAT Destination Port"
]


# 3. Define feature sets for experiments

FEATURE_SETS = {
    "full": PORT_FEATURES + TRAFFIC_FEATURES,

    "without_nat": [
        "Source Port",
        "Destination Port"
    ] + TRAFFIC_FEATURES,

    "ports_only": [
        "Source Port",
        "Destination Port"
    ]
}


# 4. Get features for a selected scenario

def get_feature_columns(feature_set="full"):

    if feature_set not in FEATURE_SETS:
        raise ValueError(
            f"Unknown feature set: {feature_set}"
        )

    return FEATURE_SETS[feature_set].copy()


# 5. Build preprocessing pipeline

def make_preprocessor(feature_set="full"):

    selected_features = get_feature_columns(feature_set)

    numeric_cols = [
        col for col in TRAFFIC_FEATURES
        if col in selected_features
    ]

    port_cols = [
        col for col in PORT_FEATURES
        if col in selected_features
    ]

    transformers = []

    # Numeric preprocessing
    if numeric_cols:

        numeric_pipeline = Pipeline([
            ("log", FunctionTransformer(
                np.log1p,
                feature_names_out="one-to-one"
            )),
            ("scaler", StandardScaler())
        ])

        transformers.append((
            "numeric",
            numeric_pipeline,
            numeric_cols
        ))

    # Port encoding
    if port_cols:

        port_encoder = OneHotEncoder(
            handle_unknown="infrequent_if_exist",
            min_frequency=50
        )

        transformers.append((
            "ports",
            port_encoder,
            port_cols
        ))

    # Combine transformations
    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop"
    )

    return preprocessor
