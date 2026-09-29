from pathlib import Path
import pytest


@pytest.mark.slow
def test_streamlit_initial_render():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=90).run()
    assert not app.exception
    assert any("VoltVAR AI" in title.value for title in app.title)
    next(button for button in app.button if button.label == "Optimallaşdır").click()
    app.run()
    assert not app.exception
    assert app.success
