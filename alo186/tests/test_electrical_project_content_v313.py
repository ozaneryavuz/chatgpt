from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/electrical-project-content-run3-v313.json"
PAGES = {
    "/haberler/62-villa-22-kw-ac-2x180-kw-dc-arac-sarj-altyapisi-projesi": SITE / "haberler/62-villa-22-kw-ac-2x180-kw-dc-arac-sarj-altyapisi-projesi/index.html",
    "/haberler/elektrik-odasi-safti-busbar-kablo-tavasi-yangin-durdurucu-detaylari": SITE / "haberler/elektrik-odasi-safti-busbar-kablo-tavasi-yangin-durdurucu-detaylari/index.html",
    "/haberler/yangin-algilama-acil-anons-cctv-kartli-gecis-data-entegrasyon-projesi": SITE / "haberler/yangin-algilama-acil-anons-cctv-kartli-gecis-data-entegrasyon-projesi/index.html",
}
REQUIRED_SECTIONS = (
    "Arama niyeti ve hedef kullanıcı", "Kapsam", "Gerekli girdiler",
    "Teslim edilmesi gereken proje çıktıları", "Disiplinler arası bağımlılıklar",
    "Kritik kontrol noktaları", "Kapsam dışı hususlar", "Sık yapılan hatalar",
    "İşverenin talep etmesi gereken kanıtlar", "Güncel mevzuat ve standart kaynakları",
    "İlgili iç bağlantılar", "Güvenli sonraki adım", "Bağımsızlık ve sorumluluk açıklaması",
)
OFFICIAL_HOSTS = {
    "www.enerji.gov.tr", "enerji.gov.tr", "www.epdk.gov.tr", "epdk.gov.tr",
    "meslekihizmetler.csb.gov.tr", "webstore.iec.ch", "www.iso.org", "iso.org",
}
FORBIDDEN = (
    "amazon.com.tr", "amzn.to", "alo186rehber-21", '"@type":"Product"',
    '"@type":"Offer"', '"@type":"AggregateRating"', '"price"',
    '"availability"', '"review"', '"warranty"',
)


def visible_text(html: str) -> str:
    value = re.sub(r"<script\b.*?</script>", " ", html, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip()


def schema_types(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        kind = value.get("@type")
        if isinstance(kind, str):
            found.add(kind)
        elif isinstance(kind, list):
            found.update(str(item) for item in kind)
        for child in value.values():
            found.update(schema_types(child))
    elif isinstance(value, list):
        for child in value:
            found.update(schema_types(child))
    return found


def answer_words(html: str) -> set[str] | None:
    match = re.search(r'<div\s+class=["\'][^"\']*\banswer\b[^"\']*["\'][^>]*>(.*?)</div>', html, re.I | re.S)
    if not match:
        return None
    text = visible_text(match.group(1)).casefold()
    stop = {
        "elektrik", "proje", "sistem", "sistemi", "olarak", "önce", "sonra",
        "birlikte", "hangi", "kabul", "gerekli", "kontrol", "doğrudan", "cevap",
    }
    return {
        word for word in re.findall(r"[a-zçğıöşü0-9×]+", text)
        if len(word) > 4 and word not in stop
    }


def jaccard(left: set[str], right: set[str]) -> float:
    return len(left & right) / max(1, len(left | right))


def declared_routes() -> list[str]:
    values: list[str] = []
    manifests = [SITE / "deployment/routing-manifest.json"]
    manifests.extend(sorted((SITE / "deployment/routing-overlays").glob("*.json")))
    for path in manifests:
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for item in payload.get("routes", []):
            route = item.get("canonicalPath") or item.get("path")
            if route:
                values.append(str(route))
    return values


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 313
    assert overlay["generatedAt"] == "2026-08-06"
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(PAGES)
    all_routes = declared_routes()
    assert all(all_routes.count(route) == 1 for route in PAGES)

    answers: dict[str, set[str]] = {}
    titles: set[str] = set()
    descriptions: set[str] = set()

    for route, page in PAGES.items():
        html = page.read_text(encoding="utf-8")
        folded = html.casefold()
        text = visible_text(html)
        assert '<meta name="viewport"' in html and "width=device-width" in html
        assert '<link rel="stylesheet" href="../alo186-article.css">' in html
        assert f'<link rel="canonical" href="https://alo186.com{route}">' in html
        assert '<strong>Doğrudan cevap</strong>' in html
        assert "Son doğrulama: 6 Ağustos 2026" in text
        assert "ALO186; EDAŞ, TEDAŞ, EPDK, EMO, GİB veya başka bir kamu kuruluşu değildir" in text
        assert "proje onayı" in folded and "mevzuata tam uyum" in folded
        assert len(text) > 6500
        assert all(token.casefold() not in folded for token in FORBIDDEN)
        assert not re.search(r"<iframe\b", html, re.I)

        title = re.search(r"<title>(.*?)</title>", html, re.S)
        description = re.search(r'<meta name="description" content="([^"]+)">', html)
        assert title and 35 <= len(title.group(1)) <= 105
        assert description and 90 <= len(description.group(1)) <= 180
        assert title.group(1) not in titles and description.group(1) not in descriptions
        titles.add(title.group(1)); descriptions.add(description.group(1))
        for heading in REQUIRED_SECTIONS:
            assert heading in text, (route, heading)
        assert len(re.findall(r"<h1\b", html, re.I)) == 1

        links = re.findall(r'href=["\']([^"\']+)["\']', html, re.I)
        internal = {link for link in links if link.startswith("/")}
        official = {
            link for link in links
            if link.startswith("https://") and urlparse(link).netloc in OFFICIAL_HOSTS
        }
        assert len(internal) >= 5, (route, internal)
        assert len(official) >= 4, (route, official)

        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        assert len(blocks) == 1
        schema = json.loads(blocks[0])
        kinds = schema_types(schema)
        assert {"Article", "FAQPage", "BreadcrumbList", "Question", "Answer"}.issubset(kinds)
        assert not {"Product", "Offer", "AggregateRating", "Review"}.intersection(kinds)
        graph = schema["@graph"]
        article = next(item for item in graph if item.get("@type") == "Article")
        faq = next(item for item in graph if item.get("@type") == "FAQPage")
        breadcrumb = next(item for item in graph if item.get("@type") == "BreadcrumbList")
        assert article["mainEntityOfPage"] == f"https://alo186.com{route}"
        assert article["datePublished"] == article["dateModified"] == "2026-08-06"
        assert len(faq["mainEntity"]) == 4
        assert breadcrumb["itemListElement"][-1]["item"] == f"https://alo186.com{route}"
        words = answer_words(html)
        assert words
        answers[route] = words

    pairs = list(answers.items())
    for index, (left_route, left_words) in enumerate(pairs):
        for right_route, right_words in pairs[index + 1:]:
            assert jaccard(left_words, right_words) < 0.34, (left_route, right_route)

    for existing in sorted((SITE / "haberler").glob("*/index.html")):
        if existing in PAGES.values():
            continue
        words = answer_words(existing.read_text(encoding="utf-8"))
        if not words:
            continue
        for route, new_words in answers.items():
            score = jaccard(new_words, words)
            assert score < 0.62, (route, existing.as_posix(), score)

    print(json.dumps({
        "ok": True,
        "routingVersion": 313,
        "routes": list(PAGES),
        "articleFaqBreadcrumb": True,
        "canonicalAndMobile": True,
        "officialSourceLinks": True,
        "affiliateAndCommercialSchemaBlocked": True,
        "routeCollisionGuard": True,
        "pairwiseContentOverlapGuard": 0.34,
        "globalContentOverlapGuard": 0.62,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
