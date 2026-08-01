from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {
    "/hesaplama/ev-cihaz-kwh-aylik-maliyet-olcum-plani/": ROOT / "hesaplama/ev-cihaz-kwh-aylik-maliyet-olcum-plani/index.html",
    "/hesaplama/buzdolabi-dondurucu-kesinti-soguk-zincir-plani/": ROOT / "hesaplama/buzdolabi-dondurucu-kesinti-soguk-zincir-plani/index.html",
    "/amazon-elektrik-urunleri/olculmus-ihtiyac-listem/": ROOT / "amazon-elektrik-urunleri/olculmus-ihtiyac-listem/index.html",
}
OVERLAY = ROOT / "deployment/routing-overlays/178-measured-growth.json"
COMMERCIAL = ROOT / "amazon-elektrik-urunleri/commercial.js"


def inline_javascript(html: str) -> str:
    chunks = re.findall(r'<script(?![^>]*application/ld\+json)[^>]*>(.*?)</script>', html, flags=re.S | re.I)
    return "\n".join(chunks)


def check_js(source: str, name: str) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=f"-{name}.js", delete=False) as handle:
        handle.write(source)
        path = handle.name
    subprocess.run(["node", "--check", path], check=True, capture_output=True, text=True)


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 178
    declared = {item["canonicalPath"]: item for item in overlay["routes"]}
    assert set(declared) == set(ROUTES)
    assert len(declared) == 3

    for route, path in ROUTES.items():
        text = path.read_text(encoding="utf-8")
        assert '<meta name="viewport"' in text
        assert f'<link rel="canonical" href="https://alo186.com{route}">' in text
        assert '"@type":"FAQPage"' in text
        assert '"@type":"BreadcrumbList"' in text
        assert 'Product' not in text
        assert '"Offer"' not in text
        assert 'aggregateRating' not in text
        assert 'availability' not in text
        assert 'href="https://www.amazon.com.tr' not in text
        assert 'alo186rehber-21' in text
        assert 'sponsored nofollow noopener' in text
        assert 'Fiyat' in text and 'stok' in text and 'garanti' in text.lower()
        assert 'ALO186' in text and ('kamu kurumu değildir' in text or 'kamu kurumu' in text)
        assert 'new Blob' in text and '.ics' in text and '.json' in text
        check_js(inline_javascript(text), path.parent.name)

    energy = ROUTES["/hesaplama/ev-cihaz-kwh-aylik-maliyet-olcum-plani/"].read_text(encoding="utf-8")
    assert 'kendi güncel faturanızdan girin' in energy
    assert "['motor','heater','fixed']" in energy
    assert 'Mevcut güvenli ölçüm çözümünüz yeterli. Yeni ürün almayın.' in energy
    assert all(marker in energy for marker in ('id="need"', 'id="spec"', 'id="ad"'))

    cold = ROUTES["/hesaplama/buzdolabi-dondurucu-kesinti-soguk-zincir-plani/"].read_text(encoding="utf-8")
    assert "phase!=='prepare'" in cold
    assert 'Aktif kesintide mağaza yolu kapalı' in cold
    assert 'Mevcut termometre, soğutucu ve jel paket planınızı kullanın; yeni ürün almayın.' in cold
    assert 'foodsafety.gov/food-safety-charts/food-safety-during-power-outage' in cold
    assert 'fda.gov/food/food-safety-during-emergencies' in cold

    shortlist = ROUTES["/amazon-elektrik-urunleri/olculmus-ihtiyac-listem/"].read_text(encoding="utf-8")
    assert 'candidates.slice(0,3)' in shortlist
    assert 'Fiyat veya komisyon sıralaması yok' not in shortlist or 'fiyat, stok, puan, komisyon' in shortlist
    assert 'Yeni ürün almayın' in shortlist or 'yeni ürün almayın' in shortlist
    assert 'measured_shortlist_created' in shortlist
    assert 'measured_shortlist_product_select' in shortlist
    assert all(marker in shortlist for marker in ('id="need"', 'id="spec"', 'id="ad"'))

    commercial = COMMERCIAL.read_text(encoding="utf-8")
    check_js(commercial, "commercial")
    assert "const measuredShortlistRoute = '/amazon-elektrik-urunleri/olculmus-ihtiyac-listem/'" in commercial
    assert 'function injectMeasuredShortlistEntry()' in commercial
    assert "section.dataset.measuredShortlistEntryV178 = 'true'" in commercial
    assert 'measured_shortlist_v178_entry_view' in commercial
    assert 'data-commercial-route="measured-shortlist-v178"' in commercial
    assert 'injectMeasuredShortlistEntry();' in commercial
    assert 'href="https://www.amazon.com.tr' not in commercial

    print(json.dumps({
        "ok": True,
        "version": 178,
        "routes": sorted(ROUTES),
        "maxShortlist": 3,
        "staticAmazonLinks": 0,
        "activeOutageCommerce": False,
        "mainProductCenterEntry": True,
        "jsonIcsOutputs": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
