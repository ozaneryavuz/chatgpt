from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
ROUTES = {
    "/haberler/62-villa-22-kw-ac-2x180-kw-dc-arac-sarj-proje-tasarimi": ROOT / "alo186/haberler/62-villa-22-kw-ac-2x180-kw-dc-arac-sarj-proje-tasarimi/index.html",
    "/haberler/elektrik-odasi-safti-rezervasyon-koordinasyon-kontrol-listesi": ROOT / "alo186/haberler/elektrik-odasi-safti-rezervasyon-koordinasyon-kontrol-listesi/index.html",
    "/haberler/kisa-devre-secicilik-kablo-koruma-koordinasyon-raporu": ROOT / "alo186/haberler/kisa-devre-secicilik-kablo-koruma-koordinasyon-raporu/index.html",
}
OVERLAY = ROOT / "alo186/deployment/routing-overlays/electrical-project-content-run1-v256.json"
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
    "İlgili ALO186 iç bağlantıları",
    "Güvenli sonraki adım",
    "Doğrulanan resmî ve birincil kaynaklar",
    "Sık sorulan sorular",
)
OFFICIAL_HOSTS = {
    "www.epdk.gov.tr",
    "www.enerji.gov.tr",
    "enerji.gov.tr",
    "www.aile.gov.tr",
    "teftis.ktb.gov.tr",
    "intweb.tse.org.tr",
    "webstore.iec.ch",
}
FORBIDDEN_COMMERCIAL = (
    "amazon.com.tr",
    "amzn.to",
    '"@type":"Product"',
    '"@type":"Offer"',
    '"@type":"AggregateRating"',
    '"price"',
    '"availability"',
)


class LinkParser(HTMLParser):
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
    return {
        token
        for token in re.findall(r"[a-zçğıöşü0-9]+", text.casefold())
        if len(token) > 4 and token not in {"elektrik", "projesi", "proje", "gerekli", "kullanıcı"}
    }


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 256
    assert overlay["generatedAt"] == "2026-08-04"
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES)
    assert len({item["source"] for item in overlay["routes"]}) == 3

    direct_answers: dict[str, set[str]] = {}
    for route, path in ROUTES.items():
        assert path.is_file(), path
        html = path.read_text(encoding="utf-8")
        assert '<meta name="viewport"' in html
        assert '<link rel="stylesheet" href="../alo186-article.css">' in html
        assert f'<link rel="canonical" href="https://alo186.com{route}">' in html
        assert "Son doğrulama: 4 Ağustos 2026" in html
        assert "ALO186; EDAŞ, TEDAŞ, EPDK, EMO, GİB veya başka bir kamu kuruluşu değildir" in html
        assert "proje onayı" in html.casefold()
        assert "mevzuata tam uyum garantisi vermez" in html
        assert "affiliate ürün yönlendirmesi yapılmaz" in html
        assert all(token not in html for token in FORBIDDEN_COMMERCIAL)
        assert not re.search(r"<iframe\b", html, re.I)
        assert not re.search(r"style=[\"'][^\"']*(?:width|min-width):\s*[5-9]\d{2}px", html, re.I)

        title = re.search(r"<title>(.*?)</title>", html, re.S)
        description = re.search(r'<meta name="description" content="([^"]+)">', html)
        assert title and 25 <= len(title.group(1)) <= 90
        assert description and 110 <= len(description.group(1)) <= 170, (route, len(description.group(1)))
        for heading in REQUIRED_HEADINGS:
            assert heading in html, (route, heading)

        parser = LinkParser()
        parser.feed(html)
        assert parser.h1 == 1
        internal = [link for link in parser.links if link.startswith("/")]
        external = [link for link in parser.links if link.startswith("https://")]
        assert len(set(internal)) >= 4, (route, internal)
        official = [link for link in external if urlparse(link).netloc in OFFICIAL_HOSTS]
        assert len(set(official)) >= 3, (route, official)

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
            assert similarity < 0.50, (left_route, right_route, similarity)

    print(json.dumps({
        "ok": True,
        "routes": list(ROUTES),
        "articleSchema": True,
        "faqSchema": True,
        "breadcrumbSchema": True,
        "affiliateBlocked": True,
        "mobileGuard": True,
        "contentOverlapGuard": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
