from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/project-design-v338.json"
ROUTES = {
    "/haberler/62-villa-22-kw-ac-2x180-kw-dc-elektrikli-arac-sarj-altyapisi-proje-tasarimi/": SITE / "haberler/62-villa-22-kw-ac-2x180-kw-dc-elektrikli-arac-sarj-altyapisi-proje-tasarimi/index.html",
    "/haberler/kisa-devre-secicilik-kablo-koruma-gerilim-dusumu-koordinasyon-raporu/": SITE / "haberler/kisa-devre-secicilik-kablo-koruma-gerilim-dusumu-koordinasyon-raporu/index.html",
    "/haberler/yangin-algilama-acil-anons-neden-sonuc-zayif-akim-proje-kabul/": SITE / "haberler/yangin-algilama-acil-anons-neden-sonuc-zayif-akim-proje-kabul/index.html",
}
COMMERCIAL_SCHEMA = {"Product", "Offer", "AggregateRating", "Review"}
REQUIRED_VISIBLE = (
    "arama niyeti",
    "hedef kullanıcı",
    "seo/aeo başlığı",
    "meta",
    "kısa cevap",
    "kapsam",
    "gerekli girdiler",
    "teslimler",
    "disiplinler arası bağımlılıklar",
    "kritik kontrol noktaları",
    "kapsam dışı",
    "sık yapılan hatalar",
    "işveren hangi kanıtları istemeli",
    "ilgili alo186 bağlantıları",
    "güvenli cta",
)


def fold(value: str) -> str:
    return value.casefold().replace("i̇", "i")


def visible_text(html: str) -> str:
    html = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", html, flags=re.I | re.S)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html))).strip()


def schema_types(value: object) -> set[str]:
    out: set[str] = set()
    if isinstance(value, dict):
        kind = value.get("@type")
        if isinstance(kind, str):
            out.add(kind)
        elif isinstance(kind, list):
            out.update(str(item) for item in kind)
        for child in value.values():
            out.update(schema_types(child))
    elif isinstance(value, list):
        for child in value:
            out.update(schema_types(child))
    return out


def schema(html: str) -> object:
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert len(blocks) == 1
    return json.loads(blocks[0])


def normalized_title(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    assert match
    return fold(re.sub(r"\s+", " ", unescape(match.group(1))).strip())


def normalized_h1(html: str) -> str:
    match = re.search(r"<h1\b[^>]*>(.*?)</h1>", html, re.I | re.S)
    assert match
    value = re.sub(r"<[^>]+>", " ", match.group(1))
    return fold(re.sub(r"\s+", " ", unescape(value)).strip())


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 338
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES)
    assert all(item["type"] == "article" for item in overlay["routes"])

    pages = {route: path.read_text(encoding="utf-8") for route, path in ROUTES.items()}
    new_titles: list[str] = []
    new_h1: list[str] = []
    for route, html in pages.items():
        visible = fold(visible_text(html))
        assert f'<link rel="canonical" href="https://alo186.com{route}">' in html
        assert '<meta name="viewport"' in html
        assert len(re.findall(r"<h1\b", html, re.I)) == 1
        assert len(re.findall(r'<meta name="description"', html, re.I)) == 1
        assert "alo186 bağımsız" in visible
        for token in ("edaş", "tedaş", "epdk", "emo", "gib", "kamu kuruluşu"):
            assert token in visible, (route, token)
        assert "proje onayı" in visible
        assert "mevzuata tam uyum garantisi vermez" in visible
        for required in REQUIRED_VISIBLE:
            assert required in visible, (route, required)
        # These are professional engineering pages: commerce must stay absent rather
        # than forcing affiliate wording into content that does not need a product path.
        assert "amazon.com.tr" not in fold(html)
        assert not re.search(r'href=["\'][^"\']*(?:amazon\.com\.tr|amzn\.to)', html, re.I)
        assert not COMMERCIAL_SCHEMA.intersection(schema_types(schema(html)))
        assert {"Article", "FAQPage", "BreadcrumbList"}.issubset(schema_types(schema(html)))
        assert html.count('href="/') >= 3
        assert "@media(max-width:700px)" in html
        new_titles.append(normalized_title(html))
        new_h1.append(normalized_h1(html))

    assert len(set(new_titles)) == 3
    assert len(set(new_h1)) == 3
    for left_idx, left in enumerate(new_h1):
        for right in new_h1[left_idx + 1:]:
            assert SequenceMatcher(None, left, right).ratio() < 0.72, (left, right)

    new_files = {path.resolve() for path in ROUTES.values()}
    other_titles: set[str] = set()
    other_h1: set[str] = set()
    other_html = ""
    for path in (SITE / "haberler").glob("*/index.html"):
        if path.resolve() in new_files:
            continue
        html = path.read_text(encoding="utf-8", errors="ignore")
        other_html += "\n" + html
        title = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
        if title:
            other_titles.add(fold(re.sub(r"\s+", " ", unescape(title.group(1))).strip()))
        h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", html, re.I | re.S)
        if h1:
            text = re.sub(r"<[^>]+>", " ", h1.group(1))
            other_h1.add(fold(re.sub(r"\s+", " ", unescape(text)).strip()))
    assert not set(new_titles).intersection(other_titles)
    assert not set(new_h1).intersection(other_h1)
    for route in ROUTES:
        assert other_html.count(f"https://alo186.com{route}") == 0

    ev = pages[next(route for route in ROUTES if "62-villa" in route)]
    ev_visible = fold(visible_text(ev))
    for token in ("1.724 kw", "62×22 kw", "2×180 kw", "dinamik yük yönetimi", "iec 60364-7-722:2018", "iec 61851-23:2023", "epdk"):
        assert token in ev_visible
    for domain in ("epdk.gov.tr", "webstore.iec.ch"):
        assert domain in ev

    protection = pages[next(route for route in ROUTES if "kisa-devre" in route)]
    protection_visible = fold(visible_text(protection))
    for token in ("iec 60909-0:2026", "23 temmuz 2026", "iec 60364-4-43:2023", "iec 61439-1:2020", "minimum", "maksimum", "jeneratör", "seçicilik"):
        assert token in protection_visible
    for domain in ("webstore.iec.ch", "enerji.gov.tr"):
        assert domain in protection

    fire = pages[next(route for route in ROUTES if "yangin-algilama" in route)]
    fire_visible = fold(visible_text(fire))
    for token in ("neden-sonuç matrisi", "iso 7240-14:2013", "iso 7240-19:2007", "iso 7240-16:2007", "asansör", "damper", "kartlı geçiş", "can güvenliği"):
        assert token in fire_visible
    for domain in ("csb.gov.tr", "iso.org"):
        assert domain in fire

    print(json.dumps({
        "ok": True,
        "routingVersion": 338,
        "newRoutes": list(ROUTES),
        "articleSchema": 3,
        "faqSchema": 3,
        "breadcrumbSchema": 3,
        "mobileViewport": 3,
        "internalLinkFloor": 3,
        "exactCollision": 0,
        "merchantLinks": 0,
        "commercialSchema": 0,
        "unverifiedPriceStockRatingWarranty": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
