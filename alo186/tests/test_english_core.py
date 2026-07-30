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

PAGES = {
    "/en/": EN_ROOT / "index.html",
    "/en/electricity-outage-turkey/": EN_ROOT / "electricity-outage-turkey/index.html",
    "/en/electricity-distribution-company-finder/": EN_ROOT / "electricity-distribution-company-finder/index.html",
    "/en/emergency-numbers-turkey/": EN_ROOT / "emergency-numbers-turkey/index.html",
}

SAFETY_PAGES = {
    "/en/",
    "/en/electricity-outage-turkey/",
    "/en/emergency-numbers-turkey/",
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


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 102
    assert overlay["generatedAt"] == "2026-07-30"
    routes = {item["canonicalPath"]: item for item in overlay["routes"]}
    assert set(routes) == set(PAGES)

    titles: set[str] = set()
    descriptions: set[str] = set()
    canonicals: set[str] = set()

    for route, page in PAGES.items():
        html = page.read_text(encoding="utf-8")
        folded = html.casefold()
        assert '<html lang="en">' in html
        assert 'name="robots" content="index,follow,max-image-preview:large"' in html
        assert "<h1" in html and "Direct answer:" in html
        assert "Independent" in html
        assert 'href="tel:112"' in html
        assert 'href="tel:186"' in html
        assert 'href="/en/' in html
        assert 'lang="tr"' in html
        assert '"inLanguage":"en"' in html
        assert '"@type":"FAQPage"' in html
        assert '"@type":"BreadcrumbList"' in html or route == "/en/"
        assert "Last reviewed: 30 July 2026" in html

        title = extract(r"<title>(.*?)</title>", html)
        description = extract(r'<meta name="description" content="([^"]+)"', html)
        canonical = extract(r'<link rel="canonical" href="([^"]+)"', html)
        assert canonical == f"https://www.alo186.com{route}"
        assert len(title) >= 35
        assert 110 <= len(description) <= 200
        titles.add(title)
        descriptions.add(description)
        canonicals.add(canonical)

        for forbidden in (
            "rel=\"sponsored",
            "amazon",
            "limited stock",
            "buy now",
            "guaranteed restoration",
            "official alo186 service",
        ):
            assert forbidden.casefold() not in folded, (route, forbidden)

        if route in SAFETY_PAGES:
            assert "affiliate" not in folded
            assert "sponsored" not in folded

    assert len(titles) == len(PAGES)
    assert len(descriptions) == len(PAGES)
    assert len(canonicals) == len(PAGES)

    english_home = PAGES["/en/"].read_text(encoding="utf-8")
    assert 'hreflang="tr-TR" href="https://www.alo186.com/elektrik-portali"' in english_home
    assert 'hreflang="en" href="https://www.alo186.com/en/"' in english_home
    assert 'hreflang="x-default" href="https://www.alo186.com/elektrik-portali"' in english_home

    turkish_portal = TURKISH_PORTAL.read_text(encoding="utf-8")
    assert '<html lang="tr">' in turkish_portal
    assert 'hreflang="tr-TR" href="https://www.alo186.com/elektrik-portali"' in turkish_portal
    assert 'hreflang="en" href="https://www.alo186.com/en/"' in turkish_portal
    assert 'hreflang="x-default" href="https://www.alo186.com/elektrik-portali"' in turkish_portal
    assert 'href="/en/" lang="en" hreflang="en"' in turkish_portal
    assert '"inLanguage":"tr-TR"' in turkish_portal
    assert '"workTranslation"' in turkish_portal

    english_finder = PAGES["/en/electricity-distribution-company-finder/"].read_text(encoding="utf-8")
    assert 'hreflang="tr-TR" href="https://www.alo186.com/edas-bul"' in english_finder
    assert 'hreflang="en" href="https://www.alo186.com/en/electricity-distribution-company-finder/"' in english_finder
    assert 'src="/edas-bul/companies.js"' in english_finder
    assert 'src="/en/assets/finder.js"' in english_finder
    assert "81 provinces" in english_finder
    assert "21 electricity distribution regions" in english_finder
    for company in COMPANIES:
        assert company in english_finder, company

    finder_js = (EN_ROOT / "assets/finder.js").read_text(encoding="utf-8")
    for token in ("Alo186Companies", "companyForProvince", "istanbulEurope", "istanbulAsia", "No personal data was used"):
        assert token in finder_js
    assert "fetch(" not in finder_js
    assert "localStorage" not in finder_js
    assert "geolocation" not in finder_js.casefold()

    companies_js = COMPANIES_JS.read_text(encoding="utf-8")
    province_block = extract(r"const provinceNames=\{(.*?)\};", companies_js)
    province_ids = {int(value) for value in re.findall(r"(?:^|,)\s*(\d+)\s*:", province_block)}
    assert province_ids == set(range(1, 82))
    assert companies_js.count("provinceIds:") == 21

    turkish_finder = TURKISH_FINDER.read_text(encoding="utf-8")
    assert 'hreflang="tr-TR" href="https://www.alo186.com/edas-bul"' in turkish_finder
    assert 'hreflang="en" href="https://www.alo186.com/en/electricity-distribution-company-finder/"' in turkish_finder
    assert 'href="/en/electricity-distribution-company-finder/" lang="en"' in turkish_finder
    assert '"inLanguage":"tr-TR"' in turkish_finder

    print(
        json.dumps(
            {
                "routingVersion": 102,
                "englishRoutes": list(PAGES),
                "provinces": len(province_ids),
                "companies": 21,
                "verifiedAt": "2026-07-30",
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
