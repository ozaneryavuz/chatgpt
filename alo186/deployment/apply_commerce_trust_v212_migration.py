from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def update_hub() -> None:
    path = ROOT / "alo186/amazon-elektrik-urunleri/index.html"
    text = path.read_text(encoding="utf-8")
    old = "https://alo186.com/amazon-elektrik-urunleri/"
    new = "https://alo186.com/amazon-elektrik-urunleri"
    if old not in text and new not in text:
        raise RuntimeError("Ürün merkezi canonical kaynağı bulunamadı")
    path.write_text(text.replace(old, new), encoding="utf-8")


def update_legacy_guides() -> None:
    trust = (
        '<div class="trust-boundary" data-alo186-commerce-trust-v212="true">'
        '<strong>Satın almama ve bağımsızlık sınırı:</strong> '
        'Mevcut güvenli ürün ihtiyacınızı karşılıyorsa yeni ürün almayın. '
        'ALO186 bağımsız bilgi platformudur; EDAŞ, kamu kurumu, üretici veya ürün satıcısı değildir.'
        '</div>'
    )
    for slug in (
        "akim-korumali-grup-priz-secimi",
        "modem-mini-ups-secimi",
        "acil-aydinlatma-duman-alarmi",
    ):
        path = ROOT / "alo186/amazon-elektrik-urunleri" / slug / "index.html"
        html = path.read_text(encoding="utf-8")
        html = html.replace("https://www.alo186.com", "https://alo186.com")
        if 'data-alo186-commerce-trust-v212="true"' not in html:
            marker = '<div class="affiliate-disclosure">'
            start = html.find(marker)
            if start < 0:
                raise RuntimeError(f"{slug}: affiliate açıklaması bulunamadı")
            end = html.find("</div>", start)
            if end < 0:
                raise RuntimeError(f"{slug}: affiliate açıklaması kapanışı bulunamadı")
            end += len("</div>")
            html = html[:end] + "\n  " + trust + html[end:]
        path.write_text(html, encoding="utf-8")


def update_guard() -> None:
    path = ROOT / "alo186/deployment/guard_commerce_routes_v3.py"
    code = path.read_text(encoding="utf-8")
    if "_trusted_closed_choice_router" in code:
        return
    sentinel = "# V2'nin ticari sayfa, hizmet, katalog, canonical ve rapor sözleşmeleri aynen\n"
    if sentinel not in code:
        raise RuntimeError("guard v3 ekleme noktası bulunamadı")
    addition = r'''
# Ürün merkezindeki v210 yönlendiricisi kişisel veri istemeyen üç kapalı
# seçimden oluşur. V2'nin bütün <form> etiketlerini kişisel veri formu sayan
# eski kontrolü yalnız bu kesin sözleşme için daraltılır; serbest veya kişisel
# veri alanı eklenirse kapı yeniden kapanır.
_original_validate_commercial_pages = v2.validate_commercial_pages


def _trusted_closed_choice_router(site: Path) -> bool:
    path = v2.route_file(site, "/amazon-elektrik-urunleri")
    if not path.is_file():
        return False
    html = path.read_text(encoding="utf-8", errors="ignore")
    if 'data-alo186-affiliate-intent-v210="true"' not in html:
        return False
    forms = re.findall(r"<form\b(?P<attrs>[^>]*)>(?P<body>.*?)</form>", html, re.I | re.S)
    if len(forms) != 1:
        return False
    attrs, body = forms[0]
    if "data-affiliate-intent-form" not in attrs:
        return False
    if re.search(r"<(?:input|textarea)\b", body, re.I):
        return False
    if re.search(r"\b(?:email|tel|phone|address|surname|file|location|message)\b", body, re.I):
        return False
    names = re.findall(r"<select\b[^>]*\bname=[\"']([^\"']+)[\"']", body, re.I)
    return names == ["need", "duration", "status"]


def validate_commercial_pages(site: Path) -> tuple[list[str], dict]:
    errors, stats = _original_validate_commercial_pages(site)
    if _trusted_closed_choice_router(site):
        blocked = "/amazon-elektrik-urunleri: ticari içerik sayfası kişisel veri formu içermemeli"
        errors = [error for error in errors if error != blocked]
    return errors, stats


v2.validate_commercial_pages = validate_commercial_pages

'''
    path.write_text(code.replace(sentinel, addition + sentinel, 1), encoding="utf-8")


def write_test() -> None:
    path = ROOT / "alo186/tests/test_commerce_trust_v212.py"
    path.write_text(r'''from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "alo186" / "deployment"))
import guard_commerce_routes_v3 as guard  # noqa: E402


def test_source_contract() -> None:
    hub = (ROOT / "alo186/amazon-elektrik-urunleri/index.html").read_text(encoding="utf-8")
    assert 'rel="canonical" href="https://alo186.com/amazon-elektrik-urunleri"' in hub
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
''', encoding="utf-8")


def update_validation_workflow() -> None:
    path = ROOT / ".github/workflows/alo186-affiliate-measurement-v211.yml"
    text = path.read_text(encoding="utf-8")
    needle = "          python alo186/tests/test_affiliate_measurement_v211.py\n"
    if "test_commerce_trust_v212.py" not in text:
        if needle not in text:
            raise RuntimeError("v211 test ekleme noktası bulunamadı")
        text = text.replace(needle, needle + "          python alo186/tests/test_commerce_trust_v212.py\n", 1)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    update_hub()
    update_legacy_guides()
    update_guard()
    write_test()
    update_validation_workflow()
    print("ALO186 commerce trust v212 migration applied")


if __name__ == "__main__":
    main()
