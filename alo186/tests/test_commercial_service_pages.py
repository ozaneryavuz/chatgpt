from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
CANONICAL_ORIGIN = "https://alo186.com"
LEGACY_ORIGIN = "https://www.alo186.com"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import load_effective_manifest  # noqa: E402

SERVICES = {
    "/hizmetler/otel-elektrik-surekliligi-denetimi/": {
        "source": "alo186/hizmetler/otel-elektrik-surekliligi-denetimi/index.html",
        "service": "hotel_audit",
        "required_links": [
            "/hesaplama/elektrik-surekliligi-olgunluk-skoru/",
            "/hesaplama/elektrik-surekliligi-pasaportu/",
            "/hesaplama/elektrik-kesintisi-tatbikati/",
        ],
        "required_terms": ["kritik yük", "UPS", "jeneratör", "ATS", "soğuk zincir"],
    },
    "/hizmetler/elektrik-teklif-teknik-inceleme/": {
        "source": "alo186/hizmetler/elektrik-teklif-teknik-inceleme/index.html",
        "service": "proposal_review",
        "required_links": [
            "/hesaplama/teknik-teklif-kapsam-karsilastirma/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hesaplama/elektrik-cozumu-yasam-dongusu-maliyeti/",
        ],
        "required_terms": ["kapsam eşitleme", "kabul", "yüklenici", "bağımsız", "teknik şartname"],
    },
    "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/": {
        "source": "alo186/hizmetler/ges-batarya-ev-sarj-fizibilitesi/index.html",
        "service": "energy_integration",
        "required_links": [
            "/hesaplama/inverter-uygunluk/",
            "/hesaplama/ev-sarj-uygunluk/",
            "/hesaplama/elektrik-cozumu-yasam-dongusu-maliyeti/",
        ],
        "required_terms": ["öz tüketim", "batarya rezervi", "EV", "VPP", "trafo"],
    },
}


def text_content(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def one_tag(html: str, tag: str) -> str:
    matches = re.findall(fr"<{tag}\b[^>]*>(.*?)</{tag}>", html, re.I | re.S)
    assert len(matches) == 1, f"{tag} sayısı 1 olmalı, bulundu={len(matches)}"
    return text_content(matches[0])


def meta_content(html: str, name: str) -> str:
    patterns = [
        fr'<meta\s+name=["\']{re.escape(name)}["\']\s+content=["\']([^"\']*)["\']',
        fr'<meta\s+content=["\']([^"\']*)["\']\s+name=["\']{re.escape(name)}["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.I)
        if match:
            return unescape(match.group(1)).strip()
    return ""


def jsonld_blocks(html: str) -> list[dict]:
    result: list[dict] = []
    for block in re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', html, re.I | re.S):
        payload = json.loads(block)
        if isinstance(payload, dict) and isinstance(payload.get("@graph"), list):
            result.extend(item for item in payload["@graph"] if isinstance(item, dict))
        elif isinstance(payload, dict):
            result.append(payload)
    return result


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 41
    route_map = {route["canonicalPath"]: route for route in manifest["routes"]}
    titles: set[str] = set()
    h1s: set[str] = set()

    for canonical, config in SERVICES.items():
        route = route_map.get(canonical)
        assert route, f"Ticari hizmet rotası routing envanterinde yok: {canonical}"
        assert route["source"] == config["source"]
        assert route["type"] == "service"

        path = REPO_ROOT / config["source"]
        html = path.read_text(encoding="utf-8")
        lower = html.casefold()
        style_path = path.parent / "styles.css"
        assert style_path.is_file() and style_path.stat().st_size > 5000, style_path
        assert '<link rel="stylesheet" href="./styles.css">' in html
        title = one_tag(html, "title")
        h1 = one_tag(html, "h1")
        description = meta_content(html, "description")
        canonical_match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', html, re.I)
        expected = f"{CANONICAL_ORIGIN}{canonical}"
        legacy = f"{LEGACY_ORIGIN}{canonical}"
        assert canonical_match and canonical_match.group(1) == expected
        assert legacy not in html, f"Legacy www service URL kaldı: {canonical}"
        assert 70 <= len(description) <= 220, (canonical, len(description))
        assert title not in titles and h1 not in h1s, "Ticari sayfalar benzersiz title ve H1 taşımalı"
        titles.add(title)
        h1s.add(h1)

        schemas = jsonld_blocks(html)
        types = {item.get("@type") for item in schemas}
        assert {"Service", "FAQPage", "BreadcrumbList"}.issubset(types), (canonical, types)
        service = next(item for item in schemas if item.get("@type") == "Service")
        assert service.get("url") == expected
        assert service.get("areaServed", {}).get("name") == "Türkiye"
        assert isinstance(service.get("hasOfferCatalog", {}).get("itemListElement"), list)
        assert len(service["hasOfferCatalog"]["itemListElement"]) >= 3
        serialized_schema = json.dumps(schemas, ensure_ascii=False).casefold()
        for forbidden_schema in ["aggregaterating", '"price"', '"pricecurrency"']:
            assert forbidden_schema not in serialized_schema, (canonical, forbidden_schema)

        assert "ücretli" in lower and "yazılı olarak teyit" in lower
        assert "alo186" in lower and ("edaş" in lower or "resmî" in lower)
        assert "ürün satın alma zorunluluğu yoktur" in lower or "satın almama" in lower or "mevcut sistem yeterliyse" in lower
        assert "amazon." not in lower and "amzn." not in lower
        assert "<form" not in lower and "<input" not in lower and "<textarea" not in lower
        assert not re.search(r"\b\d{2,}[.,]?\d*\s*(?:tl|₺|usd|eur|€|\$)\b", lower)
        assert f"service={config['service']}" in html
        assert "/kurumsal-elektrik-surekliligi-on-degerlendirme?source=service_page" in html
        for link in config["required_links"]:
            assert f'href="{link}"' in html, (canonical, link)
        plain = text_content(html).casefold()
        for term in config["required_terms"]:
            assert term.casefold() in plain, (canonical, term)
        assert html.count('class="paid-disclosure"') == 1
        assert html.count('class="boundary"') == 1

    corporate = (REPO_ROOT / "alo186/kurumsal-on-degerlendirme/index.html").read_text(encoding="utf-8")
    app = (REPO_ROOT / "alo186/kurumsal-on-degerlendirme/app.js").read_text(encoding="utf-8")
    styles = (REPO_ROOT / "alo186/kurumsal-on-degerlendirme/styles.css").read_text(encoding="utf-8")
    for canonical, config in SERVICES.items():
        assert f'href="{canonical}"' in corporate
        assert config["service"] in app
    assert "Uzmanlaşmış ticari hizmetler" in corporate
    assert "serviceProfiles" in app and "prefillFromServicePage" in app
    assert "source_service" in app
    assert "service-link-grid" in styles and "service-link-card" in styles
    assert "URLSearchParams" in app
    assert "params.get('source') !== 'service_page'" in app
    assert "localStorage" not in app and "sessionStorage" not in app

    shared_style = REPO_ROOT / "alo186/hizmetler/shared/styles.css"
    assert shared_style.is_file() and shared_style.stat().st_size > 5000
    shared_bytes = shared_style.read_bytes()
    for config in SERVICES.values():
        assert (REPO_ROOT / config["source"]).parent.joinpath("styles.css").read_bytes() == shared_bytes

    print(json.dumps({
        "ok": True,
        "canonicalOrigin": CANONICAL_ORIGIN,
        "legacyCanonicalRejected": True,
        "routingVersion": manifest["version"],
        "commercialServicePageCountAdded": len(SERVICES),
        "routes": sorted(SERVICES),
        "sharedScopeBuilder": True,
        "routeLocalAssets": True,
        "directStoreLinks": 0,
        "personalDataFields": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
