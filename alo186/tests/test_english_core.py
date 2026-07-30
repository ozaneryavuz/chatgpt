from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/english-core-run1.json"
EN_ROOT = ROOT / "alo186/en"
TURKISH_PORTAL = ROOT / "alo186/index.html"
TURKISH_FINDER = ROOT / "alo186/turkiye-arama/index.html"
COMPANIES_JS = ROOT / "alo186/turkiye-arama/companies.js"

ENGLISH_PAGES = {
    "/en/": EN_ROOT / "index.html",
    "/en/electricity-outage-turkey/": EN_ROOT / "electricity-outage-turkey/index.html",
    "/en/electricity-distribution-company-finder/": EN_ROOT / "electricity-distribution-company-finder/index.html",
    "/en/emergency-numbers-turkey/": EN_ROOT / "emergency-numbers-turkey/index.html",
    "/en/about/": EN_ROOT / "about/index.html",
    "/en/editorial-methodology/": EN_ROOT / "editorial-methodology/index.html",
    "/en/sources/": EN_ROOT / "sources/index.html",
    "/en/privacy/": EN_ROOT / "privacy/index.html",
    "/en/contact/": EN_ROOT / "contact/index.html",
    "/en/affiliate-disclosure/": EN_ROOT / "affiliate-disclosure/index.html",
}

TURKISH_ROUTED_PAGES = {
    "/elektrik-kesintisi": ROOT / "alo186/elektrik-kesintisi/index.html",
    "/acil-numaralar": ROOT / "alo186/acil-numaralar/index.html",
    "/hakkimizda": ROOT / "alo186/hakkimizda/index.html",
    "/yayin-ilkeleri": ROOT / "alo186/yayin-ilkeleri/index.html",
    "/kaynaklar": ROOT / "alo186/kaynaklar/index.html",
    "/gizlilik": ROOT / "alo186/gizlilik/index.html",
    "/iletisim": ROOT / "alo186/iletisim/index.html",
    "/yasal/amazon-satis-ortakligi": ROOT / "alo186/yasal/amazon-satis-ortakligi/index.html",
}

LANGUAGE_PAIRS = {
    "/en/": ("/elektrik-portali", TURKISH_PORTAL),
    "/en/electricity-outage-turkey/": (
        "/elektrik-kesintisi",
        TURKISH_ROUTED_PAGES["/elektrik-kesintisi"],
    ),
    "/en/electricity-distribution-company-finder/": ("/edas-bul", TURKISH_FINDER),
    "/en/emergency-numbers-turkey/": (
        "/acil-numaralar",
        TURKISH_ROUTED_PAGES["/acil-numaralar"],
    ),
    "/en/about/": ("/hakkimizda", TURKISH_ROUTED_PAGES["/hakkimizda"]),
    "/en/editorial-methodology/": (
        "/yayin-ilkeleri",
        TURKISH_ROUTED_PAGES["/yayin-ilkeleri"],
    ),
    "/en/sources/": ("/kaynaklar", TURKISH_ROUTED_PAGES["/kaynaklar"]),
    "/en/privacy/": ("/gizlilik", TURKISH_ROUTED_PAGES["/gizlilik"]),
    "/en/contact/": ("/iletisim", TURKISH_ROUTED_PAGES["/iletisim"]),
    "/en/affiliate-disclosure/": (
        "/yasal/amazon-satis-ortakligi",
        TURKISH_ROUTED_PAGES["/yasal/amazon-satis-ortakligi"],
    ),
}

CORE_CALL_PAGES = {
    "/en/",
    "/en/electricity-outage-turkey/",
    "/en/electricity-distribution-company-finder/",
    "/en/emergency-numbers-turkey/",
}

SAFETY_PAGES = {
    "/en/",
    "/en/electricity-outage-turkey/",
    "/en/emergency-numbers-turkey/",
}

TURKISH_SAFETY_PAGES = {
    "/elektrik-kesintisi",
    "/acil-numaralar",
}

COMPANIES = (
    "Toroslar EDAŞ",
    "AKEDAŞ",
    "Osmangazi EDAŞ",
    "ARAS EDAŞ",
    "MEDAŞ",
    "YEDAŞ",
    "Başkent EDAŞ",
    "Akdeniz EDAŞ",
    "Çoruh EDAŞ",
    "ADM Elektrik",
    "UEDAŞ",
    "Dicle Elektrik",
    "Fırat EDAŞ",
    "VEDAŞ",
    "SEDAŞ",
    "TREDAŞ",
    "GDZ Elektrik",
    "KCETAŞ",
    "Çamlıbel EDAŞ",
    "BEDAŞ",
    "AYEDAŞ",
)


def extract(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.I | re.S)
    assert match, pattern
    return match.group(1).strip()


def parse_json_ld(html: str, route: str) -> list[dict[str, object]]:
    blocks = re.findall(
        r'<script\s+type="application/ld\+json">(.*?)</script>',
        html,
        re.I | re.S,
    )
    assert blocks, route
    parsed: list[dict[str, object]] = []
    for block in blocks:
        value = json.loads(block)
        assert isinstance(value, dict), route
        parsed.append(value)
    return parsed


def assert_alternates(html: str, english_route: str, turkish_route: str) -> None:
    english_url = f"https://www.alo186.com{english_route}"
    turkish_url = f"https://www.alo186.com{turkish_route}"
    assert f'hreflang="tr-TR" href="{turkish_url}"' in html
    assert f'hreflang="en" href="{english_url}"' in html
    assert f'hreflang="x-default" href="{turkish_url}"' in html


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 106
    assert overlay["generatedAt"] == "2026-07-30"
    routes = {item["canonicalPath"]: item for item in overlay["routes"]}
    assert set(routes) == set(ENGLISH_PAGES) | set(TURKISH_ROUTED_PAGES)

    titles: set[str] = set()
    descriptions: set[str] = set()
    canonicals: set[str] = set()

    for route, page in ENGLISH_PAGES.items():
        html = page.read_text(encoding="utf-8")
        folded = html.casefold()
        assert '<html lang="en">' in html
        assert 'name="robots" content="index,follow,max-image-preview:large"' in html
        assert "<h1" in html and "Direct answer:" in html
        assert "Independent" in html
        assert 'href="/en/' in html
        assert 'lang="tr"' in html
        assert '"inLanguage":"en"' in html
        assert '"@type":"FAQPage"' in html
        assert '"@type":"BreadcrumbList"' in html or route == "/en/"
        assert "PrivacyPolicy" not in html
        assert "<form" not in folded
        parse_json_ld(html, route)

        title = extract(r"<title>(.*?)</title>", html)
        description = extract(r'<meta name="description" content="([^"]+)"', html)
        canonical = extract(r'<link rel="canonical" href="([^"]+)"', html)
        assert canonical == f"https://www.alo186.com{route}"
        assert len(title) >= 35
        assert 100 <= len(description) <= 240
        titles.add(title)
        descriptions.add(description)
        canonicals.add(canonical)

        if route in CORE_CALL_PAGES:
            assert 'href="tel:112"' in html
            assert 'href="tel:186"' in html

        if route in SAFETY_PAGES:
            assert "affiliate" not in folded
            assert "sponsored" not in folded
            assert "amazon" not in folded

        for forbidden in (
            "limited stock",
            "buy now",
            "guaranteed restoration",
            "official alo186 service",
        ):
            assert forbidden not in folded, (route, forbidden)

    assert len(titles) == len(ENGLISH_PAGES)
    assert len(descriptions) == len(ENGLISH_PAGES)
    assert len(canonicals) == len(ENGLISH_PAGES)

    for route, page in TURKISH_ROUTED_PAGES.items():
        html = page.read_text(encoding="utf-8")
        folded = html.casefold()
        assert '<html lang="tr-TR">' in html
        assert 'name="robots" content="index,follow,max-image-preview:large"' in html
        assert "<h1" in html and "Doğrudan cevap:" in html
        assert '"inLanguage":"tr-TR"' in html
        assert '"@type":"FAQPage"' in html
        assert '"@type":"BreadcrumbList"' in html
        assert "PrivacyPolicy" not in html
        assert "<form" not in folded
        parse_json_ld(html, route)
        canonical = extract(r'<link rel="canonical" href="([^"]+)"', html)
        assert canonical == f"https://www.alo186.com{route}"
        if route in TURKISH_SAFETY_PAGES:
            assert 'href="tel:112"' in html
            assert 'href="tel:186"' in html
            assert "affiliate" not in folded
            assert "sponsored" not in folded
            assert "amazon" not in folded

    for english_route, (turkish_route, turkish_page) in LANGUAGE_PAIRS.items():
        english_html = ENGLISH_PAGES[english_route].read_text(encoding="utf-8")
        turkish_html = turkish_page.read_text(encoding="utf-8")
        assert_alternates(english_html, english_route, turkish_route)
        assert_alternates(turkish_html, english_route, turkish_route)
        assert '<html lang="en">' in english_html
        assert '<html lang="tr' in turkish_html

    turkish_portal = TURKISH_PORTAL.read_text(encoding="utf-8")
    assert 'href="/en/" lang="en" hreflang="en"' in turkish_portal
    assert '"inLanguage":"tr-TR"' in turkish_portal
    assert '"workTranslation"' in turkish_portal

    english_finder = ENGLISH_PAGES[
        "/en/electricity-distribution-company-finder/"
    ].read_text(encoding="utf-8")
    assert 'src="/edas-bul/companies.js"' in english_finder
    assert 'src="/en/assets/finder.js"' in english_finder
    assert "81 provinces" in english_finder
    assert "21 electricity distribution regions" in english_finder
    for company in COMPANIES:
        assert company in english_finder, company

    finder_js = (EN_ROOT / "assets/finder.js").read_text(encoding="utf-8")
    for token in (
        "Alo186Companies",
        "companyForProvince",
        "istanbulEurope",
        "istanbulAsia",
        "No personal data was used",
    ):
        assert token in finder_js
    assert "fetch(" not in finder_js
    assert "localStorage" not in finder_js
    assert "geolocation" not in finder_js.casefold()

    companies_js = COMPANIES_JS.read_text(encoding="utf-8")
    province_block = extract(r"const provinceNames=\{(.*?)\};", companies_js)
    province_ids = {
        int(value)
        for value in re.findall(r"(?:^|,)\s*(\d+)\s*:", province_block)
    }
    assert province_ids == set(range(1, 82))
    assert companies_js.count("provinceIds:") == 21

    turkish_finder = TURKISH_FINDER.read_text(encoding="utf-8")
    assert 'href="/en/electricity-distribution-company-finder/" lang="en"' in turkish_finder
    assert '"inLanguage":"tr-TR"' in turkish_finder

    english_emergency = ENGLISH_PAGES[
        "/en/emergency-numbers-turkey/"
    ].read_text(encoding="utf-8")
    turkish_emergency = TURKISH_ROUTED_PAGES["/acil-numaralar"].read_text(
        encoding="utf-8"
    )
    for html in (english_emergency, turkish_emergency):
        assert 'href="tel:187"' in html

    for route in ("/en/contact/", "/en/privacy/"):
        html = ENGLISH_PAGES[route].read_text(encoding="utf-8")
        assert "info@alo186.com" in html
    for route in ("/iletisim", "/gizlilik"):
        html = TURKISH_ROUTED_PAGES[route].read_text(encoding="utf-8")
        assert "info@alo186.com" in html

    print(
        json.dumps(
            {
                "routingVersion": 106,
                "englishRoutes": list(ENGLISH_PAGES),
                "turkishSupportRoutes": list(TURKISH_ROUTED_PAGES),
                "languagePairs": len(LANGUAGE_PAIRS),
                "provinces": len(province_ids),
                "companies": 21,
                "verifiedAt": "2026-07-30",
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
