from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "alo186" / "deployment" / "inject_affiliate_measurement_v210.py"
spec = importlib.util.spec_from_file_location("affiliate_measurement_v210", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def seed(site: Path) -> None:
    (site / "index.html").write_text(
        '''<!doctype html><html><head><title>ALO186</title></head><body>
        <a class="hero-cta" href="https://www.amazon.com.tr/dp/B012345678?tag=alo186rehber-21" target="_blank" rel="nofollow">Ürünü incele</a>
        <a href="https://example.com/source" target="_blank">Kaynak</a>
        <a href="/amazon-elektrik-urunleri/">İç rota</a>
        <script>const template = '<a href="https://www.amazon.com.tr/dp/SHOULD_NOT_CHANGE">x</a>';</script>
        </body></html>''',
        encoding="utf-8",
    )
    page = site / "amazon-elektrik-urunleri" / "modem-mini-ups"
    page.mkdir(parents=True)
    (page / "index.html").write_text(
        '''<!doctype html><html><head><title>Mini UPS</title></head><body>
        <a class="comparison-card" href="https://www.amazon.com.tr/s?k=mini+ups&amp;tag=alo186rehber-21" rel="sponsored">Karşılaştır</a>
        </body></html>''',
        encoding="utf-8",
    )
    dynamic = site / "dynamic"
    dynamic.mkdir()
    (dynamic / "index.html").write_text(
        "<!doctype html><html><head><title>Dinamik</title></head><body><main>Seçici</main></body></html>",
        encoding="utf-8",
    )
    (site / "pages-release.json").write_text(json.dumps({"version": 1}), encoding="utf-8")
    (site / "checksums.sha256").write_text("placeholder\n", encoding="utf-8")


def script_syntax(site: Path) -> None:
    asset = site / module.ASSET_RELATIVE
    assert asset.is_file()
    subprocess.run(["node", "--check", str(asset)], check=True, capture_output=True, text=True)


def assertions(site: Path, base_path: str = "") -> None:
    index = (site / "index.html").read_text(encoding="utf-8")
    product = (site / "amazon-elektrik-urunleri/modem-mini-ups/index.html").read_text(encoding="utf-8")
    dynamic = (site / "dynamic/index.html").read_text(encoding="utf-8")
    expected_src = f"{base_path}/assets/affiliate-measurement-v210.js" if base_path else "/assets/affiliate-measurement-v210.js"
    for text in (index, product, dynamic):
        assert text.count(module.SCRIPT_MARKER) == 1
        assert f'src="{expected_src}"' in text
    script_syntax(site)
    runtime = (site / module.ASSET_RELATIVE).read_text(encoding="utf-8")
    assert "affiliate_page_view" in runtime
    assert "affiliate_click" in runtime
    assert "destination_url" not in runtime
    assert "link_url" not in runtime
    assert "getConsent?.()==='granted'" in runtime
    assert "data-alo186-ga4-loader" in runtime
    assert "window.gtag('event',name,params)" in runtime
    assert "suppressGenericAffiliate" in runtime
    for parameter in (
        "affiliate_network",
        "page_path",
        "content_cluster",
        "link_placement",
        "link_type",
        "product_key",
        "measurement_version",
    ):
        assert parameter in runtime

    direct = re.search(r"<a[^>]+amazon\.com\.tr/dp/[^>]+>", index, re.I)
    assert direct
    direct_tag = direct.group(0)
    assert {"sponsored", "nofollow", "noopener"} <= set((module.get_attr(direct_tag, "rel") or "").split())
    assert module.get_attr(direct_tag, "data-affiliate-network") == "amazon_tr"
    assert module.get_attr(direct_tag, "data-affiliate-link-type") == "direct_product"
    assert len(module.get_attr(direct_tag, "data-affiliate-product-key") or "") == 14

    external = re.search(r"<a[^>]+example\.com/source[^>]+>", index, re.I)
    assert external and "noopener" in set((module.get_attr(external.group(0), "rel") or "").split())
    internal = re.search(r'<a[^>]+href="/amazon-elektrik-urunleri/"[^>]*>', index, re.I)
    assert internal and module.get_attr(internal.group(0), "data-affiliate-network") is None
    assert 'SHOULD_NOT_CHANGE" data-affiliate-network' not in index

    inventory_text = (site / module.INVENTORY_NAME).read_text(encoding="utf-8")
    inventory = json.loads(inventory_text)
    assert inventory["summary"]["scannedPages"] == 3
    assert inventory["summary"]["instrumentedPages"] == 3
    assert inventory["summary"]["staticAffiliatePages"] == 2
    assert inventory["summary"]["staticAffiliateLinks"] == 2
    assert inventory["summary"]["directProductLinks"] == 1
    assert inventory["summary"]["searchLinks"] == 1
    assert inventory["privacy"]["rawDestinationUrlStored"] is False
    assert "amazon.com" not in inventory_text.lower()
    assert "alo186rehber-21" not in inventory_text

    routes = {page["route"] for page in inventory["pages"]}
    expected_home = f"{base_path}/" if base_path else "/"
    expected_product = f"{base_path}/amazon-elektrik-urunleri/modem-mini-ups/" if base_path else "/amazon-elektrik-urunleri/modem-mini-ups/"
    assert {expected_home, expected_product} <= routes

    release = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
    assert release["affiliateMeasurement"]["version"] == 210
    assert release["affiliateMeasurement"]["staticAffiliateLinks"] == 2
    assert release["affiliateMeasurement"]["rawDestinationUrlInAnalytics"] is False
    checksums = (site / "checksums.sha256").read_text(encoding="utf-8")
    assert module.INVENTORY_NAME in checksums
    assert module.ASSET_RELATIVE.as_posix() in checksums


def test_custom_domain_and_idempotence() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site)
        first = module.inject(site, "")
        assert first["ok"] and first["staticAffiliateLinks"] == 2
        assertions(site)
        snapshot = {path.relative_to(site).as_posix(): path.read_bytes() for path in site.rglob("*") if path.is_file()}
        second = module.inject(site, "")
        assert second["ok"]
        assertions(site)
        after = {path.relative_to(site).as_posix(): path.read_bytes() for path in site.rglob("*") if path.is_file()}
        assert snapshot == after


def test_project_path_routes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site)
        result = module.inject(site, "/chatgpt")
        assert result["basePath"] == "/chatgpt"
        assertions(site, "/chatgpt")


if __name__ == "__main__":
    test_custom_domain_and_idempotence()
    test_project_path_routes()
    print("ALO186 affiliate measurement v210: PASS")
