from __future__ import annotations

import json
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "ev": ROOT / "alo186/sektor-rehberi/62-villa-22-kw-ac-2x180-kw-dc-sarj-altyapisi-projesi/index.html",
    "rooms": ROOT / "alo186/sektor-rehberi/otel-elektrik-odalari-saftlar-pano-yerlesim-projesi/index.html",
    "critical": ROOT / "alo186/sektor-rehberi/otel-trafo-jenerator-ups-kritik-yuk-tek-hat-projesi/index.html",
}
CANONICALS = {
    "ev": "https://www.alo186.com/sektor-rehberi/62-villa-22-kw-ac-2x180-kw-dc-sarj-altyapisi-projesi/",
    "rooms": "https://www.alo186.com/sektor-rehberi/otel-elektrik-odalari-saftlar-pano-yerlesim-projesi/",
    "critical": "https://www.alo186.com/sektor-rehberi/otel-trafo-jenerator-ups-kritik-yuk-tek-hat-projesi/",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/165-electrical-project-design-content.json"
AUDIT = ROOT / "alo186/audits/electrical-project-design-content-v165-2026-08-01.md"


def read(path: Path) -> str:
    assert path.exists(), f"missing: {path}"
    return path.read_text(encoding="utf-8")


def json_ld(html: str) -> list[dict]:
    blocks = re.findall(
        r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',
        html,
        flags=re.I | re.S,
    )
    assert blocks, "JSON-LD missing"
    return [json.loads(block) for block in blocks]


def main() -> None:
    pages = {name: read(path) for name, path in PAGES.items()}
    required_visible = (
        "Arama niyeti",
        "Hedef kullanıcı",
        "SEO/AEO",
        "Kısa cevap",
        "Proje kapsamı",
        "Gerekli girdiler",
        "Proje teslimleri",
        "Disiplinler arası bağımlılıklar",
        "Kritik kontrol noktaları",
        "Kapsam dışı hususlar",
        "Sık yapılan hatalar",
        "İşverenin talep etmesi gereken kanıtlar",
        "İlgili iç bağlantılar",
        "Güvenli CTA",
    )

    for name, html in pages.items():
        assert f'<link rel="canonical" href="{CANONICALS[name]}">' in html
        assert '<meta name="viewport"' in html
        assert "@media(max-width:780px)" in html
        assert "Bağımsızlık ve sorumluluk sınırı" in html
        assert "ALO186; EDAŞ, TEDAŞ" in html
        assert "proje onayı" in html.lower()
        assert "mevzuata tam uyum" in html.lower()
        assert "Affiliate bağlantısı" in html or "affiliate bağlantısı" in html
        assert "amazon.com" not in html.lower()
        assert '"@type":"Product"' not in html
        assert '"@type":"Offer"' not in html
        assert '"availability"' not in html
        assert '"aggregateRating"' not in html
        for phrase in required_visible:
            assert phrase in html, f"{name}: missing {phrase}"

        graphs = json_ld(html)
        nodes = []
        for graph in graphs:
            nodes.extend(graph.get("@graph", [graph]))
        types = {node.get("@type") for node in nodes}
        assert {"Article", "FAQPage", "BreadcrumbList"} <= types
        article = next(node for node in nodes if node.get("@type") == "Article")
        assert article["mainEntityOfPage"] == CANONICALS[name]

    for name, html in pages.items():
        linked = sum(canonical.replace("https://www.alo186.com", "") in html for canonical in CANONICALS.values())
        assert linked >= 2, f"{name}: insufficient internal links"

    routing = json.loads(read(ROUTING))
    assert routing["version"] == 165
    assert routing["generatedAt"] == "2026-08-01"
    assert len(routing["routes"]) == 3
    paths = [route["canonicalPath"] for route in routing["routes"]]
    assert len(paths) == len(set(paths)) == 3
    assert {f"https://www.alo186.com{path}" for path in paths} == set(CANONICALS.values())
    for route in routing["routes"]:
        assert route["type"] == "guide"
        assert (ROOT / route["source"]).exists()

    all_html = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "alo186").rglob("*.html"))
    for canonical in CANONICALS.values():
        assert all_html.count(f'<link rel="canonical" href="{canonical}">') == 1
    headlines = [
        "62 Villa İçin 22 kW AC ve 2×180 kW DC Şarj Altyapısı Projesi",
        "Otel Elektrik Odaları, Şaftlar ve Pano Yerleşim Projesi",
        "Otel Trafo, Jeneratör ve UPS Kritik Yük Tek Hat Projesi",
    ]
    for headline in headlines:
        assert sum(headline in html for html in pages.values()) == 1

    audit = read(AUDIT)
    for phrase in (
        "İçerik boşluğu",
        "Dönüşüm noktası",
        "Tekrar ziyaret nedenleri",
        "Beklenen kullanıcı faydası",
        "Beklenen gelir/lead etkisi",
        "Doğrulanmamış fiyat, stok, puan",
        "Affiliate bağlantısı yoktur",
        "Tamamlanamayan kontroller",
    ):
        assert phrase in audit

    with tempfile.TemporaryDirectory(prefix="alo186-project-v165-") as temp_dir:
        output = Path(temp_dir)
        subprocess.run(
            [
                "python",
                str(ROOT / "alo186/deployment/build_static_site.py"),
                "--output",
                str(output),
                "--commit",
                "test-project-v165",
            ],
            cwd=ROOT,
            check=True,
        )
        sitemap = ET.parse(output / "sitemap.xml")
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = {node.text for node in sitemap.findall("s:url/s:loc", namespace)}
        assert set(CANONICALS.values()) <= locations
        for canonical in CANONICALS.values():
            relative = canonical.removeprefix("https://www.alo186.com/")
            assert (output / relative / "index.html").exists()

    print("PASS: ALO186 electrical project design content v165 contract")


if __name__ == "__main__":
    main()
