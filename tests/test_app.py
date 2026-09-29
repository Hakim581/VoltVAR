from pathlib import Path
import pytest


@pytest.mark.slow
def test_streamlit_guided_flow_and_reset():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=90).run()
    assert not app.exception
    assert any("VoltVAR AI" in title.value for title in app.title)
    next(button for button in app.button if button.label == "NÜMAYİŞƏ BAŞLA").click()
    app.run()
    assert not app.exception
    assert any("ŞƏBƏKƏNİN CARİ VƏZİYYƏTİ" in title.value for title in app.title)
    assert len(app.metric) == 6
    next(button for button in app.button if button.label == "NÖVBƏTİ ADDIM").click()
    app.run()
    assert not app.exception
    next(button for button in app.button if "AĞIR SƏNAYE YÜKÜ" in button.label).click()
    app.run()
    next(button for button in app.button if button.label == "İŞ REJİMİNİ TƏTBİQ ET").click()
    app.run()
    assert not app.exception
    assert any("NƏ DƏYİŞDİ" in heading.value for heading in app.subheader)
    next(button for button in app.button if button.label == "NÖVBƏTİ ADDIM").click()
    app.run()
    next(button for button in app.button if button.label == "ŞƏBƏKƏNİ OPTİMALLAŞDIR").click()
    app.run()
    assert not app.exception
    assert any("TÖVSİYƏ OLUNAN" in heading.value for heading in app.subheader)
    next(radio for radio in app.radio if radio.label == "Görünüş rejimi").set_value("MÜHƏNDİSLİK REJİMİ")
    app.run()
    assert not app.exception
    assert any("Digər hesablanmış tənzimləmə variantları" in item.label for item in app.get("expander"))
    next(button for button in app.button if button.label == "NƏTİCƏLƏRƏ BAX").click()
    app.run()
    assert not app.exception
    assert any("OPTİMALLAŞDIRMANIN NƏTİCƏSİ" in heading.value for heading in app.subheader)
    next(button for button in app.button if button.label == "SIFIRLA").click()
    app.run()
    assert not app.exception
    assert any(button.label == "NÜMAYİŞƏ BAŞLA" for button in app.button)
