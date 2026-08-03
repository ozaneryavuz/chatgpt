from __future__ import annotations

import hashlib
import json
import re
import tempfile
from pathlib import Path

from alo186.deployment.inject_competitor_gap_affiliate_v250 import apply as apply_v250
from alo186.deployment.inject_competitor_gap_affiliate_v251 import apply as apply_v251
from alo186.deployment.inject_location_schema_v253 import apply as apply_v253
from alo186.deployment.materialize_location_pages_v253 import materialize


def page(title: str) -> str:
    return (
        '<!doctype html><html lang="tr"><head><meta charset="utf-8">'
        f'<title>{title}</title></head><body><main><h1>{title}</h1></main></body></html>'
    )


def jsonld(text: str, marker: str) -> dict:
    pattern = re.compile(
        rf'<script\b(?=[^>]*{re.escape(marker)})[^>]*>(.*?)</script>',
        re.IGNORECASE | re.DOTALL,
    )
    matches = pattern.findall(text)
    assert len(matches) == 1, (marker, len(matches))
    return json.loads(matches[0])


def walk(value):
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from walk(nested)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seed(site: Path) -> None:
    routes = (
        ("amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici", "Kombi seçici"),
        ("edas-bul", "EDAŞ bul"),
        ("acil-numaralar", "Acil numaralar"),
        ("haberler/ups-mi-tasinabilir-guc-istasyonu-mu", "UPS mi güç istasyonu mu"),
        ("haberler/korumali-priz-ne-zaman-yeterli-degildir", "Korumalı priz"),
        ("karar-motoru", "Karar motoru"),
        ("hesaplama/kesinti-hazirlik-plani", "Kesinti hazırlık planı"),
    )
    for route, title in routes:
        target = site / route
        target.mkdir(parents=True)
        (target / "index.html").write_text(page(title), encoding="utf-8")
    (site / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://alo186.com/sitemap.xml\n",
        encoding="utf-8",
    )
    (site / "sitemap.xml").write_text(
        "<?xml version='1.0' encoding='utf-8'?>\n"
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "</urlset>\n",
        encoding="utf-8",
    )


def run_chain(repo: Path, site: Path) -> dict[str, object]:
    materialize_report = materialize(repo, site)
    apply_v250(repo, site)
    apply_v251(repo, site)
    schema_report = apply_v253(repo, site)
    return {"materialize": materialize_report, "schema": schema_report}


def assert_local_page(path: Path, *, expected_name: str, expected_canonical: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert 'data-alo186-location-page-v253="true"' in text
    assert text.count('data-alo186-local-service-v251="true"') == 1
    assert expected_name in text
    assert f'<link rel="canonical" href="{expected_canonical}">' in text
    assert 'href="tel:186"' in text
    assert 'href="tel:112"' in text
    assert "amazon.com.tr" not in text.lower()

    graph = jsonld(text, 'data-alo186-local-service-v251="true"')
    nodes = list(walk(graph))
    types = {node.get("@type") for node in nodes if isinstance(node.get("@type"), str)}
    assert {
        "WebPage",
        "Question",
        "Answer",
        "ItemList",
        "Organization",
        "Service",
        "ServiceChannel",
        "ContactPoint",
        "GovernmentOrganization",
        "GovernmentService",
    }.issubset(types), types
    services = [node for node in nodes if node.get("@type") == "Service"]
    government_services = [node for node in nodes if node.get("@type") == "GovernmentService"]
    assert len(services) == 1
    assert len(government_services) == 1
    assert government_services[0]["name"] == "112 Acil Çağrı Hizmeti"
    assert all("EDAŞ" not in str(node.get("name", "")) for node in government_services)
    contact_numbers = {
        str(node.get("telephone"))
        for node in nodes
        if node.get("@type") == "ContactPoint"
    }
    assert {"112", "186"}.issubset(contact_numbers)
    questions = [node for node in nodes if node.get("@type") == "Question"]
    assert len(questions) == 1
    assert questions[0]["name"].endswith("elektrik kesintisi için nere aranır?")
    decisions = [
        node
        for node in nodes
        if node.get("@type") == "ItemList" and node.get("numberOfItems") == 2
    ]
    assert len(decisions) == 1


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    with tempfile.TemporaryDirectory(prefix="alo186-v253-") as raw:
        site = Path(raw)
        seed(site)
        first = run_chain(repo, site)

        province_pages = list((site / "il").glob("*/index.html"))
        company_pages = list((site / "dagitim-sirketleri").glob("*/index.html"))
        assert len(province_pages) == 81
        assert len(company_pages) == 21
        assert first["materialize"]["provincePages"] == 81
        assert first["materialize"]["companyPages"] == 21
        assert first["schema"]["central"] == {
            "services": 81,
            "specificProvinceUrls": 81,
            "serviceChannels": 81,
        }
        assert first["schema"]["local"] == {
            "provincePages": 81,
            "companyPages": 21,
            "governmentService112Pages": 102,
            "questionPages": 102,
            "privateEdasGovernmentServiceCount": 0,
        }
        assert first["schema"]["sitemap"] == {
            "expected": 102,
            "present": 102,
            "duplicates": 0,
        }
        assert first["schema"]["affiliateLinksOnLocationPages"] == 0
        assert first["schema"]["javascriptRequired"] is False

        assert_local_page(
            site / "il/mugla/index.html",
            expected_name="Muğla elektrik kesintisi",
            expected_canonical="https://alo186.com/il/mugla",
        )
        assert_local_page(
            site / "il/istanbul/index.html",
            expected_name="İstanbul elektrik kesintisi",
            expected_canonical="https://alo186.com/il/istanbul",
        )
        assert_local_page(
            site / "dagitim-sirketleri/adm-elektrik/index.html",
            expected_name="ADM Elektrik",
            expected_canonical="https://alo186.com/dagitim-sirketleri/adm-elektrik",
        )
        assert_local_page(
            site / "dagitim-sirketleri/bedas/index.html",
            expected_name="BEDAŞ",
            expected_canonical="https://alo186.com/dagitim-sirketleri/bedas",
        )

        central_text = (site / "edas-bul/index.html").read_text(encoding="utf-8")
        central_graph = jsonld(central_text, 'data-alo186-service-catalog-v250="true"')
        central_services = [
            node
            for node in walk(central_graph)
            if node.get("@type") == "Service" and "#service-" in str(node.get("@id", ""))
        ]
        assert len(central_services) == 81
        assert all(str(node.get("url", "")).startswith("https://alo186.com/il/") for node in central_services)
        assert all(
            node.get("availableChannel", {}).get("serviceUrl") == node.get("url")
            for node in central_services
        )
        assert not any(node.get("@type") == "GovernmentService" for node in walk(central_graph))

        sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
        assert sitemap.count("<loc>https://alo186.com/il/") == 81
        assert sitemap.count("<loc>https://alo186.com/dagitim-sirketleri/") == 21

        sample_paths = [
            site / "il/mugla/index.html",
            site / "il/istanbul/index.html",
            site / "dagitim-sirketleri/adm-elektrik/index.html",
            site / "dagitim-sirketleri/bedas/index.html",
            site / "edas-bul/index.html",
            site / "sitemap.xml",
        ]
        before = {path: sha(path) for path in sample_paths}
        second = run_chain(repo, site)
        after = {path: sha(path) for path in sample_paths}
        assert before == after
        assert second["schema"]["jsonLdSyntax"] == "pass"
        assert second["schema"]["visibleContentParity"] == "pass"

        report = json.loads((site / "alo186-location-schema-v253.json").read_text(encoding="utf-8"))
        assert report["version"] == 253
        assert report["local"]["provincePages"] == 81
        assert report["local"]["companyPages"] == 21
        assert report["local"]["governmentService112Pages"] == 102
        assert report["privateEdasSchema"] == "Organization + Service + ServiceChannel(186)"
        assert report["governmentServiceSchema"] == "112 Acil Çağrı Hizmeti only"

    print("ALO186 location pages & schema v253: PASS")


if __name__ == "__main__":
    main()
