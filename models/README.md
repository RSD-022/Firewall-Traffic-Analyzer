# Export contract (ML teammate → Streamlit teammate)

Required before predictive features can work:

- `firewall_pipeline.joblib`: fitted **complete** scikit-learn Pipeline containing
  all fitted imputation/encoding/scaling and final classification stages.
  Only load models you created or trust; joblib uses pickle.
- `metadata.json`: ordered names of raw input feature columns and optional model name.
- `metrics.json` (recommended): **real**, measured offline model evaluation results.

Minimal `metadata.json`:

```json
{
  "model_name": "Best validated classifier",
  "feature_columns": ["Source Port", "Destination Port", "NAT Source Port", "NAT Destination Port", "Bytes", "Bytes Sent", "Bytes Received", "Packets", "Elapsed Time (sec)", "pkts_sent", "pkts_received"]
}
```

Sample **schema only** for `metrics.json`, replace nulls with actual numerical values:

```json
{
  "model_name": "Name of final classifier",
  "accuracy": null,
  "macro_f1": null,
  "weighted_f1": null,
  "class_labels": [],
  "confusion_matrix": [],
  "model_comparison": []
}
```

Do not create a `metrics.json` with placeholder or fabricated accuracy values in the final submission.
Always split into training/test sets before fitting preprocessing. Export the *fitted*
end-to-end pipeline selected by your model training code.
The notebook and Streamlit app must use the **same exact column names and order**.
