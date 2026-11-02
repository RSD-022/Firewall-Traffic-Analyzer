from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]

def test_app_starts():
    at = AppTest.from_file(
        str(ROOT / "src" / "app.py")
    ).run(timeout=30)

    assert not at.exception