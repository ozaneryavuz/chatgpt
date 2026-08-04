from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
ROUTES = {
    "/haberler/trafo-jenerator-ups-kritik-yuk-transfer-yuk-atma-tasarimi": ROOT / "alo186/haberler/trafo-jenerator-ups-kritik-yuk-transfer-yuk-atma-tasarimi/index.html",
    "/haberler/acil-aydinlatma-kacis-yolu-proje-hesap-test-kabul": ROOT / "alo186/haberler/acil-aydinlatma-kacis-yolu-proje-hesap-test-kabul/index.html",
    "/haberler/topraklama-yildirimdan-korunma-spd-espotansiyel-koordinasyon-raporu": ROOT / "alo186/haberler/topraklama-yildirimdan-korunma-spd-espotansiyel-koordinasyon-raporu/index.html",
}
OVERLAY = ROOT / "alo186/deployment/routing-overlays/electrical-project-content-run2-v269.json"
REQUIRED_HEADINGS = (
    "Arama niyeti ve hedef kullanıcı",
    "Kapsam",
    "Gerekli girdiler",
    "Teslim edilmesi gereken proje çıktıları",
    "Disiplinler arası bağımlılıklar",
    "Kritik kontrol noktaları",
    "Kapsam dışı hususlar",
    "Sık yapılan hatalar",
    "İşverenin talep etmesi gereken kanıtlar",
    "Güncel mevzuat ve standart kaynakları",
    "İlgili iç bağlantılar",
    "Güvenli sonraki adım",
    "Bağımsızlık ve sorumluluk açıklaması",
)
OFFICIAL_HOSTS = {
    "www.enerji.gov.tr",
    "enerji.gov.tr",
    "meslekihizmetler.csb.gov.tr",
    "teftis.ktb.gov.tr",
    "webstore.iec.ch",
    "www.iso.org",
}
FORBIDDEN_COMMERCIAL = (
    "amazon.com.tr",
    "amzn.to",
    '"@type":"Product"',
    '"@type":"Offer"',
    '"@type":"AggregateRating"',
    '"price"',
    '"availability"',
    '"review"',
    '"warranty"',
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.h1 = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            self.links.append(str(values["href"]))
        if tag == "h1":
            self.h1 += 1


def schema_types(value):
    found = set()
    if isinstance(value, dict):
        item = value.get("@type")
        if isinstance(item, str):
            found.add(item)
        elif isinstance(item, list):
            found.update(item)
        for child in value.values():
            found.update(schema_types(child))
    elif isinstance(value, list):
        for child in value:
            found.update(schema_types(child))
    return found


def normalized_words(text: str) -> set[str]:
    stop = {
        "elektrik",
        "projesi",
        "proje",
        "gerekli",
        "kullanıcı",
        "sonra",
        "olarak",
        "birlikte",
        "doğrulayın",
    }
    return {
        token
        for token in re.findall(r"[a-zçğıöşü0-9]+", text.casefold())
        if len(token) > 4 and token not in stop
    }


def all_declared_routes() -> list[str]:
    paths: list[str] = []
    manifest_paths = [ROOT / "alo186/deployment/routing-manifest.json"]
    manifest_paths.extend(sorted((ROOT / "alo186/deployment/routing-overlays").glob("*.json")))
    for manifest_path in manifest_paths:
        if not manifest_path.is_file():
            continue
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in payload.get("routes", []):
            canonical = item.get("canonicalPath") or item.get("path")
            if canonical:
                paths.append(str(canonical))
    return paths


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 269
    assert overlay["generatedAt"] == "2026-08-04"
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES)
    assert len({item["source"] for item in overlay["routes"]}) == 3

    declared = all_declared_routes()
    for route in ROUTES:
        assert declared.count(route) == 1, (route, declared.count(route))

    direct_answers: dict[str, set[str]] = {}
    titles: set[str] = set()
    descriptions: set[str] = set()

    for route, path in ROUTES.items():
        assert path.is_file(), path
        html = path.read_text(encoding="utf-8")
        folded = html.casefold()
        assert '<meta name="viewport"' in html
        assert 'width=device-width' in html
        assert '<link rel="stylesheet" href="../alo186-article.css">' in html
        assert f'<link rel="canonical" href="https://alo186.com{route}">' in html
        assert "Son doğrulama: 4 Ağustos 2026" in html
        assert "ALO186; EDAŞ, TEDAŞ, EPDK, EMO, GİB veya başka bir kamu kuruluşu değildir" in html
        assert "proje onayı" in folded or "proje veya kabul onayı" in folded
        assert "mevzuata tam uyum" in folded
        assert all(token.casefold() not in folded for token in FORBIDDEN_COMMERCIAL)
        assert not re.search(r"<iframe\b", html, re.I)
        assert not re.search(r"style=[\"'][^\"']*(?:width|min-width):\s*[5-9]\d{2}px", html, re.I)

        title = re.search(r"<title>(.*?)</title>", html, re.S)
        description = re.search(r'<meta name="description" content="([^"]+)">', html)
        assert title and 35 <= len(title.group(1)) <= 100, (route, title.group(1) if title else None)
        assert description and 90 <= len(description.group(1)) <= 180, (route, len(description.group(1)) if description else None)
        assert title.group(1) not in titles
        assert description.group(1) not in descriptions
        titles.add(title.group(1))
        descriptions.add(description.group(1))

        for heading in REQUIRED_HEADINGS:
            assert heading in html, (route, heading)

        parser = PageParser()
        parser.feed(html)
        assert parser.h1 == 1
        internal = [link for link in parser.links if link.startswith("/")]
        external = [link for link in parser.links if link.startswith("https://")]
        assert len(set(internal)) >= 4, (route, internal)
        official = [link for link in external if urlparse(link).netloc in OFFICIAL_HOSTS]
        assert len(set(official)) >= 4, (route, official)
        assert all(urlparse(link).scheme == "https" for link in external)

        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>',
            html,
            re.S,
        )
        assert len(blocks) == 1
        schema = json.loads(blocks[0])
        types = schema_types(schema)
        assert {"Article", "FAQPage", "BreadcrumbList"}.issubset(types), (route, types)
        graph = schema["@graph"]
        article = next(item for item in graph if item.get("@type") == "Article")
        faq = next(item for item in graph if item.get("@type") == "FAQPage")
        breadcrumb = next(item for item in graph if item.get("@type") == "BreadcrumbList")
        assert article["mainEntityOfPage"] == f"https://alo186.com{route}"
        assert article["datePublished"] == "2026-08-04"
        assert article["dateModified"] == "2026-08-04"
        assert len(faq["mainEntity"]) >= 4
        assert breadcrumb["itemListElement"][-1]["item"] == f"https://alo186.com{route}"

        answer = re.search(r'<div class="answer"><strong>Doğrudan cevap</strong>(.*?)</div>', html, re.S)
        assert answer
        direct_answers[route] = normalized_words(re.sub(r"<[^>]+>", " ", answer.group(1)))

    pairs = list(direct_answers.items())
    for index, (left_route, left_words) in enumerate(pairs):
        for right_route, right_words in pairs[index + 1 :]:
            union = left_words | right_words
            similarity = len(left_words & right_words) / len(union) if union else 1.0
            assert similarity < 0.40, (left_route, right_route, similarity)

    print(json.dumps({
        "ok": True,
        "routes": list(ROUTES),
        "routingVersion": 269,
        "articleSchema": True,
        "faqSchema": True,
        "breadcrumbSchema": True,
        "affiliateBlocked": True,
        "mobileGuard": True,
        "officialSourceGuard": True,
        "globalRouteCollisionGuard": True,
        "contentOverlapGuard": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
