from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "alo186" / "deployment"))
import guard_commerce_routes_v3 as guard  # noqa: E402


def test_source_contract() -> None:
    hub = (ROOT / "alo186/amazon-elektrik-urunleri/index.html").read_text(encoding="utf-8")
    assert 'rel="canonical" href="https://alo186.com/amazon-elektrik-urunleri"' in hub
    assert '"url":"https://alo186.com/amazon-elektrik-urunleri"' in hub
    assert 'rel="canonical" href="https://alo186.com/amazon-elektrik-urunleri/"' not in hub
    for slug in (
        "akim-korumali-grup-priz-secimi",
        "modem-mini-ups-secimi",
        "acil-aydinlatma-duman-alarmi",
    ):
        text = (ROOT / "alo186/amazon-elektrik-urunleri" / slug / "index.html").read_text(encoding="utf-8")
        assert "https://www.alo186.com" not in text
        assert "Mevcut güvenli ürün ihtiyacınızı karşılıyorsa yeni ürün almayın" in text
        assert "ALO186 bağımsız bilgi platformudur" in text
        assert "ürün satıcısı değildir" in text


def test_closed_choice_form_exception_is_fail_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "amazon-elektrik-urunleri/index.html"
        page.parent.mkdir(parents=True)
        page.write_text('''<section data-alo186-affiliate-intent-v210="true"><form data-affiliate-intent-form><select name="need"></select><select name="duration"></select><select name="status"></select></form></section>''', encoding="utf-8")
        assert guard._trusted_closed_choice_router(Path(tmp)) is True
        page.write_text('''<section data-alo186-affiliate-intent-v210="true"><form data-affiliate-intent-form><select name="need"></select><select name="duration"></select><select name="status"></select><input type="email"></form></section>''', encoding="utf-8")
        assert guard._trusted_closed_choice_router(Path(tmp)) is False


if __name__ == "__main__":
    test_source_contract()
    test_closed_choice_form_exception_is_fail_closed()
    print("ALO186 commerce trust v212: PASS")
