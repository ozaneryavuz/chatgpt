from pathlib import Path


PORTAL_SOURCE = Path(__file__).resolve().parents[1] / "index.html"


def test_portal_source_uses_current_device_damage_application_deadline() -> None:
    html = PORTAL_SOURCE.read_text(encoding="utf-8")

    assert "Cihaz hasarında başvuru süresi 30 gündür" in html
    assert "<strong>30 gün içinde</strong>" in html
    assert "EDAŞ · cihaz hasarı · 30 gün" in html

    assert "Cihaz hasarında başvuru süresi 10 iş günüdür" not in html
    assert "<strong>10 iş günü içinde</strong>" not in html
    assert "EDAŞ · cihaz hasarı · 10 iş günü" not in html
