from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {
    "start": ROOT / "sektor-rehberi/elektrik-projesine-baslangic-guc-ihtiyaci-yedek-enerji-sistem-cozumleri/index.html",
    "rooms": ROOT / "sektor-rehberi/elektrik-odasi-saft-pano-yerlesim-koordinasyonu/index.html",
    "ev": ROOT / "sektor-rehberi/62-villa-22kw-ac-2x180kw-dc-arac-sarj-projesi/index.html",
}
OVERLAY = ROOT / "deployment/routing-overlays/200-electrical-project-design-content.json"
AUDIT = ROOT / "audits/electrical-project-design-content-v200-2026-08-02.md"
SITEMAP = ROOT / "sitemap-electric-project-v200.xml"
ROBOTS = ROOT / "robots.txt"


def read(path: Path) -> str:
    assert path.exists(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def test_overlay_registers_three_unique_routes() -> None:
    payload = json.loads(read(OVERLAY))
    assert payload["version"] == 200
    assert payload["generatedAt"] == "2026-08-02"
    assert len(payload["routes"]) == 3
    paths = [route["canonicalPath"] for route in payload["routes"]]
    assert len(paths) == len(set(paths)) == 3
    assert {route["type"] for route in payload["routes"]} == {"guide"}
    for route in payload["routes"]:
        assert (ROOT.parent / route["source"]).exists()
        assert route["canonicalPath"].startswith("/") and route["canonicalPath"].endswith("/")


def test_required_seo_aeo_mobile_and_independence_contract() -> None:
    expected = {
        "start": "/sektor-rehberi/elektrik-projesine-baslangic-guc-ihtiyaci-yedek-enerji-sistem-cozumleri/",
        "rooms": "/sektor-rehberi/elektrik-odasi-saft-pano-yerlesim-koordinasyonu/",
        "ev": "/sektor-rehberi/62-villa-22kw-ac-2x180kw-dc-arac-sarj-projesi/",
    }
    titles = []
    for key, path in ROUTES.items():
        html = read(path)
        assert f'<link rel="canonical" href="https://alo186.com{expected[key]}">' in html
        assert '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">' in html
        assert '"@type":"Article"' in html
        assert '"@type":"FAQPage"' in html
        assert '"@type":"BreadcrumbList"' in html
        assert '@media(max-width:800px)' in html
        assert 'class="table-wrap"' in html
        assert 'resmî kurum, EDAŞ, TEDAŞ, EMO, GİB veya kamu kuruluşu değildir' in html
        assert 'mevzuata tam uyum garantisi vermez' in html
        assert '"@type":"Product"' not in html
        assert '"@type":"Offer"' not in html
        assert 'AggregateRating' not in html
        match = re.search(r"<title>(.*?) \| ALO186</title>", html)
        assert match
        titles.append(match.group(1))
    assert len(titles) == len(set(titles)) == 3


def test_every_page_contains_requested_content_framework() -> None:
    required = (
        "Arama niyeti",
        "Hedef kullanıcı",
        "Kısa cevap",
        "Kapsam",
        "Gerekli girdiler",
        "Teslimler",
        "Disiplinler arası bağımlılıklar",
        "Kritik kontrol noktaları",
        "Kapsam dışı",
        "Sık yapılan hatalar",
        "İşverenin talep etmesi gereken kanıtlar",
        "İlgili iç bağlantılar",
        "Güvenli CTA",
        "Doğrulanan birincil ve kurumsal kaynaklar",
    )
    for path in ROUTES.values():
        html = read(path)
        for token in required:
            assert token in html, f"{token}: {path}"
        assert html.count('/sektor-rehberi/') >= 4


def test_project_start_technical_scope() -> None:
    html = read(ROUTES["start"])
    for token in (
        "OG/AG",
        "trafo",
        "jeneratör",
        "UPS",
        "yükleme cetveli",
        "prensip tek hat",
        "kısa devre",
        "gerilim düşümü",
        "seçicilik",
        "harmonik",
        "büyüme rezervi",
        "Tek bir ticari yazılım zorunlu kabul edilmemelidir",
    ):
        assert token.lower() in html.lower(), token


def test_room_shaft_and_fire_coordination_scope() -> None:
    html = read(ROUTES["rooms"])
    for token in (
        "OG hücre",
        "busbar",
        "kablo merdiveni",
        "yangın durdurucu",
        "ekipman taşıma rotası",
        "havalandırma",
        "su borularının",
        "IEC 61439",
        "IEC 61936-1:2021",
    ):
        assert token.lower() in html.lower(), token


def test_ev_arithmetic_is_contextual_not_transformer_selection() -> None:
    html = read(ROUTES["ev"])
    for token in (
        "62 × 22 kW = 1.364 kW",
        "2 × 180 kW = 360 kW",
        "1.724 kW",
        "Bağlantı gücü değildir",
        "dinamik yük yönetimi",
        "RCD/RDC-DD",
        "OCPP",
        "EPDK",
        "IEC 60364-7-722:2018",
        "IEC 61851-1:2017",
        "IEC 61439-7:2022",
    ):
        assert token.lower() in html.lower(), token
    assert "doğrudan talep gücü veya trafo seçimi değildir" in html.lower()


def test_no_unverified_commercial_or_guarantee_claims() -> None:
    joined = "\n".join(read(path) for path in ROUTES.values())
    for phrase in (
        "hemen satın al",
        "stoklar tükenmeden",
        "son fırsat",
        "en ucuz",
        "en iyi fiyat",
        "uygunluk garantisi verir",
        "proje onayı garantisi",
    ):
        assert phrase not in joined.lower()
    assert not re.search(r"\b\d+[.,]?\d*\s*(?:₺|TL)\b", joined)
    assert "amazon.com.tr" not in joined.lower()


def test_dedicated_sitemap_and_robots_registration() -> None:
    sitemap = read(SITEMAP)
    robots = read(ROBOTS)
    assert sitemap.count("<url>") == 3
    for route in (
        "elektrik-projesine-baslangic-guc-ihtiyaci-yedek-enerji-sistem-cozumleri",
        "elektrik-odasi-saft-pano-yerlesim-koordinasyonu",
        "62-villa-22kw-ac-2x180kw-dc-arac-sarj-projesi",
    ):
        assert route in sitemap
    assert "Sitemap: https://alo186.com/sitemap-electric-project-v200.xml" in robots


def test_audit_documents_selection_impact_sources_and_limits() -> None:
    audit = read(AUDIT)
    for heading in (
        "Arama niyeti ve içerik boşluğu",
        "Seçilen üç aksiyon",
        "Kullanıcı yolculuğu",
        "Dönüşüm noktaları",
        "Tekrar ziyaret nedenleri",
        "Beklenen kullanıcı faydası",
        "Beklenen gelir / lead etkisi",
        "Doğrulanan kaynaklar",
        "SEO, AEO ve teknik yayın kontrolleri",
        "Tamamlanamayan kontroller",
    ):
        assert heading in audit


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"electrical project design content v200: {len(tests)} checks passed")
