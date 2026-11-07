from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]

def test_app_starts():
    at = AppTest.from_file(
        str(ROOT / "src" / "app.py")
    ).run(timeout=30)

    assert not at.exception

def test_manual_prediction_page_starts():
    at = AppTest.from_file(str(ROOT / "src" / "app.py")).run(timeout=30)
    at.sidebar.radio[0].set_value("Manual Prediction").run(timeout=30)
    assert not at.exception


def test_model_performance_page_starts():
    at = AppTest.from_file(str(ROOT / "src" / "app.py")).run(timeout=30)
    at.sidebar.radio[0].set_value("Model Performance").run(timeout=60)
    assert not at.exception
