from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "alo186" / "deployment" / "inject_affiliate_intent_router_v210.py"
spec = importlib.util.spec_from_file_location("affiliate_intent_v210", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def seed(site: Path) -> None:
    target = site / "amazon-elektrik-urunleri"
    target.mkdir(parents=True)
    html = '''<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>Ürün merkezi</title></head><body><main><div class="affiliate-disclosure">Satış ortaklığı açıklaması</div><section class="section" aria-labelledby="priorityTitle"><h2 id="priorityTitle">Öncelikli yollar</h2></section></main></body></html>'''
    (target / "index.html").write_text(html, encoding="utf-8")
    (site / "pages-release.json").write_text(json.dumps({"version": 1}), encoding="utf-8")
    (site / "checksums.sha256").write_text("placeholder\n", encoding="utf-8")


def assertions(text: str, base: str = "") -> None:
    assert text.count('data-alo186-affiliate-intent-v210="true"') == 1
    assert text.count('data-alo186-affiliate-intent-v210-style="true"') == 1
    assert text.count('data-alo186-affiliate-intent-v210-script="true"') == 1
    assert "30 saniyelik ihtiyaç yönlendiricisi" in text
    assert "Mevcut güvenli çözüm yeterli — yeni ürün almayın" in text
    assert "Ticari yol kapalı" in text
    assert "Tüketici affiliate yolu uygun değil" in text
    assert "affiliate_intent_router_view" in text
    assert "affiliate_intent_no_buy" in text
    assert "affiliate_intent_blocked" in text
    assert "affiliate_intent_resume" in text
    assert "alo186_affiliate_intent_v210" in text
    assert '"ttlDays":14' in text
    assert "amazon.com" not in text.lower()
    assert "amzn.to" not in text.lower()
    assert "alo186rehber-21" not in text
    assert 'name="email"' not in text
    assert 'name="phone"' not in text
    assert 'name="address"' not in text
    expected = f"{base}/hesaplama/teknik-urun-karsilastirma/" if base else "/hesaplama/teknik-urun-karsilastirma/"
    assert expected in text
    expected_fixed = f"{base}/kurumsal-elektrik-surekliligi-on-degerlendirme" if base else "/kurumsal-elektrik-surekliligi-on-degerlendirme"
    assert expected_fixed in text
    assert text.index('data-alo186-affiliate-intent-v210="true"') < text.index('aria-labelledby="priorityTitle"')


def test_custom_domain_and_idempotence() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site)
        first = module.inject(site, "")
        assert first["ok"] is True
        assert first["injected"] is True
        page = site / module.TARGET
        assertions(page.read_text(encoding="utf-8"))
        second = module.inject(site, "")
        assert second["injected"] is False
        assertions(page.read_text(encoding="utf-8"))
        release = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
        router = release["affiliateIntentRouter"]
        assert router["version"] == 210
        assert router["taskCount"] == 8
        assert router["questionCount"] == 3
        assert router["localResumeTtlDays"] == 14
        assert router["personalDataCollected"] is False
        assert router["directAmazonLinks"] == 0
        assert router["noBuyOutcome"] is True
        assert router["unsafeCommerceBlocked"] is True
        assert router["fixedInstallationAffiliateBlocked"] is True


def test_project_path_links() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site)
        result = module.inject(site, "/chatgpt")
        assert result["basePath"] == "/chatgpt"
        assertions((site / module.TARGET).read_text(encoding="utf-8"), "/chatgpt")


def test_missing_anchor_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        target = site / "amazon-elektrik-urunleri"
        target.mkdir(parents=True)
        (target / "index.html").write_text("<html><head></head><body></body></html>", encoding="utf-8")
        try:
            module.inject(site, "")
        except RuntimeError as exc:
            assert "öncelik bölümü" in str(exc)
        else:
            raise AssertionError("Eksik anchor fail-closed durmadı")


if __name__ == "__main__":
    test_custom_domain_and_idempotence()
    test_project_path_links()
    test_missing_anchor_fails_closed()
    print("ALO186 affiliate intent router v210: PASS")
