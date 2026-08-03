from __future__ import annotations

import html as html_lib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
HUB_PATH = ROOT / "alo186/amazon-elektrik-urunleri/index.html"
ORIGIN = "https://alo186.com"
ROUTE_PREFIX = "/amazon-elektrik-urunleri/"
EXPECTED_PATHS = {
    "/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/",
    "/amazon-elektrik-urunleri/nas-ups-usb-snmp-uygunluk-secici/",
    "/amazon-elektrik-urunleri/guvenlik-kamerasi-nvr-poe-ups-secici/",
    "/amazon-elektrik-urunleri/alarm-paneli-aku-uygunluk-secici/",
    "/amazon-elektrik-urunleri/cpap-yedek-guc-uygunluk-secici/",
    "/amazon-elektrik-urunleri/mobil-hotspot-4g-5g-yedek-internet-secici/",
}


def load_item_list_urls() -> tuple[str, set[str]]:
    source = HUB_PATH.read_text(encoding="utf-8")
    match = re.search(
        r'<script\s+type="application/ld\+json">\s*(.*?)\s*</script>',
        source,
        flags=re.DOTALL,
    )
    assert match, "Ürün merkezi JSON-LD bloğu bulunamadı"
    payload = json.loads(html_lib.unescape(match.group(1)))
    graph = payload.get("@graph")
    assert isinstance(graph, list), "JSON-LD @graph dizisi eksik"
    item_list = next(
        (
            item
            for item in graph
            if isinstance(item, dict)
            and item.get("@type") == "ItemList"
            and item.get("name") == "Yüksek niyetli güvenli ürün seçim rotaları"
        ),
        None,
    )
    assert item_list, "Öncelikli ürün seçimi ItemList düğümü bulunamadı"
    entries = item_list.get("itemListElement")
    assert isinstance(entries, list) and entries, "ItemList rotaları boş"
    urls = {
        entry.get("url")
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("url"), str)
    }
    assert len(urls) == len(entries), "ItemList URL alanları eksik veya yineleniyor"
    return source, urls


def test_product_hub_jsonld_routes_are_canonical_and_clickable() -> None:
    source, urls = load_item_list_urls()
    paths: set[str] = set()

    for url in urls:
        parsed = urlparse(url)
        assert f"{parsed.scheme}://{parsed.netloc}" == ORIGIN, f"Canonical origin sapması: {url}"
        assert parsed.path.startswith(ROUTE_PREFIX), f"Ürün merkezi rota ayıracı eksik: {url}"
        assert parsed.query == "" and parsed.fragment == "", f"JSON-LD rotası temiz değil: {url}"
        assert f'href="{parsed.path}"' in source, f"JSON-LD rotasının görünür eş bağlantısı yok: {url}"
        paths.add(parsed.path)

    assert paths == EXPECTED_PATHS
    assert "https://alo186.com/amazon-elektrik-urunlerimodem" not in source
    assert "https://alo186.com/amazon-elektrik-urunlerinas" not in source
    assert "https://alo186.com/amazon-elektrik-urunleriguvenlik" not in source
    assert "https://alo186.com/amazon-elektrik-urunlerialarm" not in source
    assert "https://alo186.com/amazon-elektrik-urunlericpap" not in source
    assert "https://alo186.com/amazon-elektrik-urunlerimobil" not in source


if __name__ == "__main__":
    test_product_hub_jsonld_routes_are_canonical_and_clickable()
    print(json.dumps({"ok": True, "routes": len(EXPECTED_PATHS), "origin": ORIGIN}))
