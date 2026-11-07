from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "src" / "app.py")

PAGES = ["Overview", "Data Quality", "Traffic Analytics", "Statistics",
         "Manual Prediction", "Batch Prediction", "Model Performance",
         "About & FAQ"]


@pytest.mark.parametrize("page", PAGES)
def test_every_page_opens(page):
    at = AppTest.from_file(APP).run(timeout=60)
    at.sidebar.radio[0].set_value(page).run(timeout=90)
    assert not at.exception


@pytest.mark.skipif(not (ROOT / "models" / "firewall_pipeline.joblib").is_file(),
                    reason="trained model not present")
def test_valid_manual_flow_gives_prediction():
    at = AppTest.from_file(APP).run(timeout=60)
    at.sidebar.radio[0].set_value("Manual Prediction").run(timeout=60)
    submit = [b for b in at.button if "Predict firewall action" in b.label]
    assert submit, "submit button not found"
    submit[0].click().run(timeout=90)
    assert not at.exception
    assert not at.error
    assert any("Values sent to the model" in c.value for c in at.caption)


def test_model_missing_warns_and_stays_navigable(monkeypatch, tmp_path):
    monkeypatch.setenv("FIREWALL_MODEL_FILE", str(tmp_path / "missing.joblib"))
    at = AppTest.from_file(APP).run(timeout=60)
    assert not at.exception
    at.sidebar.radio[0].set_value("Manual Prediction").run(timeout=60)
    assert not at.exception
    assert any("No trained pipeline" in w.value for w in at.warning)
    at.sidebar.radio[0].set_value("Overview").run(timeout=60)
    assert not at.exception
