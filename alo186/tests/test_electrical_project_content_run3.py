from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/electrical-project-content-run3-v296.json"

PAGES = {
    "/haberler/kisa-devre-gerilim-dusumu-kablo-koruma-secicilik-hesap-raporu": {
        "file": SITE / "haberler/kisa-devre-gerilim-dusumu-kablo-koruma-secicilik-hesap-raporu/index.html",
        "sources": ("webstore.iec.ch/en/publication/68454", "webstore.iec.ch/en/publication/28432", "webstore.iec.ch/en/publication/103734"),
        "tokens": ("Kısa cevap", "Gerekli girdiler", "Teslim edilmesi gereken çıktılar", "Seçicilik matrisi", "İşverenin talep etmesi gereken kanıtlar"),
    },
    "/haberler/mekanik-kuvvet-motor-vfd-mcc-besleme-kontrol-projesi": {
        "file": SITE / "haberler/mekanik-kuvvet-motor-vfd-mcc-besleme-kontrol-projesi/index.html",
        "sources": ("webstore.iec.ch/en/publication/74487", "webstore.iec.ch/en/publication/111823", "webstore.iec.ch/en/publication/62103"),
        "tokens": ("Kısa cevap", "Gerekli girdiler", "Teslim edilmesi gereken çıktılar", "BMS/SCADA I/O listesi", "İşverenin talep etmesi gereken kanıtlar"),
    },
    "/haberler/aydinlatma-hesap-kontrol-gunisigi-devreye-alma-projesi": {
        "file": SITE / "haberler/aydinlatma-hesap-kontrol-gunisigi-devreye-alma-projesi/index.html",
        "sources": ("iso.org/standard/76342", "iso.org/standard/65883", "iso.org/standard/70361"),
        "tokens": ("Kısa cevap", "Gerekli girdiler", "Teslim edilmesi gereken çıktılar", "Devreye alma", "İşverenin talep etmesi gereken kanıtlar"),
    },
}

REQUIRED_SECTIONS = (
    "Arama niyeti ve hedef kullanıcı",
    "Kapsam",
    "Gerekli girdiler",
    "Teslim edilmesi gereken çıktılar",
    "Disiplinler arası bağımlılıklar",
    "Kritik kontrol noktaları",
    "Kapsam dışı hususlar",
    "Sık yapılan hatalar",
    "İşverenin talep etmesi gereken kanıtlar",
    "Doğrulanan güncel kaynaklar",
    "İlgili ALO186 içerikleri",
    "Güvenli sonraki adım",
)


def schema_from(html: str) -> dict:
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert len(blocks) == 1, f"Tek JSON-LD bloğu bekleniyordu, bulunan: {len(blocks)}"
    return json.loads(blocks[0])


def schema_types(value: object) -> set[str]:
    values: set[str] = set()
    if isinstance(value, dict):
        kind = value.get("@type")
        if isinstance(kind, str):
            values.add(kind)
        elif isinstance(kind, list):
            values.update(str(item) for item in kind)
        for child in value.values():
            values.update(schema_types(child))
    elif isinstance(value, list):
        for child in value:
            values.update(schema_types(child))
    return values


def text_content(html: str) -> str:
    value = re.sub(r"<script\b.*?</script>", " ", html, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip()


def direct_answer_tokens(html: str) -> set[str]:
    match = re.search(r'<div class="answer">(.*?)</div>', html, re.S)
    assert match, "Doğrudan cevap bulunamadı"
    words = re.findall(r"[a-zçğıöşü0-9]+", text_content(match.group(1)).casefold())
    stop = {"ve", "ile", "için", "bir", "bu", "de", "da", "her", "aynı", "olarak", "sonra"}
    return {word for word in words if len(word) > 3 and word not in stop}


def jaccard(left: set[str], right: set[str]) -> float:
    return len(left & right) / max(1, len(left | right))


def all_route_records() -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    base = json.loads((SITE / "deployment/routing-manifest.json").read_text(encoding="utf-8"))
    for raw in base.get("routes", []):
        route = raw.get("canonicalPath") or raw.get("path")
        source = raw.get("source") or raw.get("file")
        if route and source:
            records.append((str(route), str(source)))
    for path in sorted((SITE / "deployment/routing-overlays").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for raw in payload.get("routes", []):
            route = raw.get("canonicalPath") or raw.get("path")
            source = raw.get("source") or raw.get("file")
            if route and source:
                records.append((str(route), str(source)))
    return records


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 296
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(PAGES)

    records = all_route_records()
    for route in PAGES:
        matches = [(path, source) for path, source in records if path == route]
        assert len(matches) == 1, f"Canonical rota tekil değil: {route} -> {matches}"

    answers: dict[str, set[str]] = {}
    for route, config in PAGES.items():
        html = config["file"].read_text(encoding="utf-8")
        folded = html.casefold()
        visible = text_content(html)

        assert '<meta name="viewport"' in html
        assert f'<link rel="canonical" href="https://alo186.com{route}">' in html
        assert html.count("<h1>") == 1
        assert len(visible) > 5000
        assert "5 Ağustos 2026" in visible
        assert "ALO186" in visible
        for institution in ("EDAŞ", "TEDAŞ", "EPDK", "EMO", "GİB"):
            assert institution in visible, (route, institution)
        assert "mevzuata tam uyum garantisi vermez" in visible
        assert "affiliate içerik değildir" in visible
        assert "amazon.com.tr" not in folded and "amzn.to" not in folded
        assert "alo186rehber-21" not in folded

        for section in REQUIRED_SECTIONS:
            assert section in visible, (route, section)
        for token in config["tokens"]:
            assert token in visible, (route, token)
        for source in config["sources"]:
            assert source in folded, (route, source)

        schema = schema_from(html)
        kinds = schema_types(schema)
        assert {"Article", "FAQPage", "BreadcrumbList", "Question", "Answer"}.issubset(kinds)
        assert not {"Product", "Offer", "AggregateRating", "Review"}.intersection(kinds)
        serialized = json.dumps(schema, ensure_ascii=False)
        assert serialized.count('"@type": "Question"') == 4
        assert route in serialized
        assert "2026-08-05" in serialized

        internal_links = set(re.findall(r'href="(/[^"]+)"', html))
        assert "/elektrik-portali" in internal_links
        assert "/kurumsal-elektrik-surekliligi-on-degerlendirme" in internal_links
        assert len(internal_links) >= 7, (route, internal_links)
        answers[route] = direct_answer_tokens(html)

    routes = list(PAGES)
    for index, route in enumerate(routes):
        for other in routes[index + 1 :]:
            score = jaccard(answers[route], answers[other])
            assert score < 0.48, f"Doğrudan cevaplar fazla benzer: {route} / {other} = {score:.2f}"

    print(json.dumps({
        "ok": True,
        "version": 296,
        "newRoutes": routes,
        "articleFaqBreadcrumb": True,
        "mobileViewport": True,
        "officialSources": True,
        "affiliateLinks": 0,
        "commercialSchema": 0,
        "canonicalCollisions": 0,
        "directAnswerSimilarityGuard": 0.48,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
