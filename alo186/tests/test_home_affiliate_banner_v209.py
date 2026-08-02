from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "alo186" / "deployment" / "inject_home_affiliate_banner_v209.py"
spec = importlib.util.spec_from_file_location("home_affiliate_v209", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def seed(site: Path) -> None:
    template = '''<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>ALO186</title></head><body><main><section class="hero"><h1>Elektrik</h1></section><section class="task-start"><h2>Görevler</h2></section><section class="legal-alert"><h2>Resmî yol</h2></section></main></body></html>'''
    (site / "index.html").write_text(template, encoding="utf-8")
    portal = site / "elektrik-portali"
    portal.mkdir(parents=True)
    (portal / "index.html").write_text(template, encoding="utf-8")
    (site / "pages-release.json").write_text(json.dumps({"version": 1}), encoding="utf-8")
    (site / "checksums.sha256").write_text("placeholder\n", encoding="utf-8")


def assertions(text: str, base: str = "") -> None:
    section_marker = '<section class="home-affiliate-feature" data-alo186-home-affiliate-v209="true"'
    assert text.count(section_marker) == 1
    assert text.count('data-home-affiliate-product=') == 6
    assert text.count('data-alo186-home-affiliate-v209-style="true"') == 1
    assert text.count('data-alo186-home-affiliate-v209-script="true"') == 1
    assert 'Satış ortaklığı içerebilir' in text
    assert 'Mevcut güvenli ürün ihtiyacınızı karşılıyorsa yenisini almayın' in text
    assert 'Fiyat, stok, puan ve garanti yayımlamaz' in text
    assert 'home_affiliate_showcase_view' in text
    assert 'home_affiliate_banner_click' in text
    assert 'home_affiliate_product_click' in text
    assert 'amazon.com' not in text.lower()
    assert 'alo186rehber-21' not in text
    assert '"@type":"Product"' not in text
    assert '"@type":"Offer"' not in text
    expected = f'{base}/amazon-elektrik-urunleri/konuya-gore-urun-haritasi/' if base else '/amazon-elektrik-urunleri/konuya-gore-urun-haritasi/'
    assert expected in text
    assert text.index(section_marker) < text.index('<section class="legal-alert"')


def test_custom_domain_and_idempotence() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site)
        first = module.inject(site, "")
        assert first["ok"]
        assert len(first["injectedPages"]) == 2
        for relative in module.TARGETS:
            assertions((site / relative).read_text(encoding="utf-8"))
        second = module.inject(site, "")
        assert second["injectedPages"] == []
        for relative in module.TARGETS:
            assertions((site / relative).read_text(encoding="utf-8"))
        release = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
        showcase = release["homeAffiliateShowcase"]
        assert showcase["version"] == 209
        assert showcase["productSelectorCount"] == 6
        assert showcase["directAmazonLinks"] == 0
        assert showcase["affiliateDisclosureVisible"] is True
        assert showcase["existingProductNoBuyVisible"] is True


def test_project_path_links() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site)
        result = module.inject(site, "/chatgpt")
        assert result["basePath"] == "/chatgpt"
        for relative in module.TARGETS:
            assertions((site / relative).read_text(encoding="utf-8"), "/chatgpt")


if __name__ == "__main__":
    test_custom_domain_and_idempotence()
    test_project_path_links()
    print("ALO186 homepage affiliate banner v209: PASS")
