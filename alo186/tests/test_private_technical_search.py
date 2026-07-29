from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import load_effective_manifest  # noqa: E402
from inject_private_search import generate_index  # noqa: E402


def read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


def test_source_contracts() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    routes = [route for route in manifest["routes"] if route["canonicalPath"] == "/arama/"]
    assert len(routes) == 1
    assert routes[0]["source"] == "alo186/arama/index.html"
    assert routes[0]["type"] == "tool"
    assert manifest["version"] >= 39

    html = read("alo186/arama/index.html")
    app = read("alo186/arama/app.js")
    core = read("alo186/arama/core.js")
    generator = read("alo186/deployment/inject_private_search.py")
    pipeline = read("alo186/deployment/inject_shortlist_growth.py")
    placeholder = json.loads(read("alo186/arama/search-index.json"))

    assert 'rel="canonical" href="https://www.alo186.com/arama/"' in html
    assert 'type="search"' in html
    assert 'maxlength="120"' in html
    assert "WebApplication" in html and "FAQPage" in html
    assert "ham sorgu gönderilmez" in html
    assert "ALO186 arıza ya da şikâyet kaydı almaz" in html
    assert 'href="tel:112"' in html
    assert 'href="/edas-bul"' in html
    assert './core.js' in html and './app.js' in html
    assert "amazon.com" not in html.casefold()
    assert '<textarea' not in html.casefold()
    assert 'type="email"' not in html.casefold()
    assert 'type="tel"' not in html.casefold()

    assert "query_length" in app and "token_count" in app and "result_count" in app
    assert "query:" not in app, "Ham arama metni analytics parametresi olmamalı"
    assert "localStorage" not in app and "sessionStorage" not in app
    assert "#q=" in app, "Paylaşılabilir sorgu yalnız URL fragmentinde tutulmalı"
    assert "textContent = entry.title" in app and "textContent = entry.description" in app
    assert "innerHTML" not in app, "Arama sonuçları ham HTML olarak oluşturulmamalı"

    assert "SAFETY_TOKENS" in core
    assert "OFFICIAL_TOKENS" in core
    assert "PRODUCT_TOKENS" in core
    assert "entry.canonicalPath === '/karar-motoru'" in core
    assert "['tool','calculator'].includes(entry.bucket)" in core

    assert "commercialRankingExcluded" in generator
    assert '"price"' in generator and '"stock"' in generator and '"rating"' in generator
    assert "if robots and \"noindex\"" in generator
    assert "canonical_path == CANONICAL_PATH" in generator
    assert "rawQueryStored" in generator and "commercialRankingUsed" in generator
    assert "search-index.json" in generator
    assert "data-alo186-search-card" in generator

    consolidation_position = pipeline.index("apply_content_consolidation(site, base_path)")
    search_position = pipeline.index("run_private_search(site, base_path)")
    assert consolidation_position < search_position, "Alias içerikler arama indeksi oluşturulmadan önce çıkarılmalı"

    assert placeholder["entryCount"] == 0
    assert placeholder["entries"] == []
    assert "sunucuya gönderilmez" in placeholder["privacy"]


def test_generator_excludes_noindex_and_prefixes_project_urls() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        (site / "arama").mkdir(parents=True)
        (site / "arama/index.html").write_text("<!doctype html><h1>Arama</h1>", encoding="utf-8")
        (site / "tool").mkdir(parents=True)
        (site / "tool/index.html").write_text(
            """<!doctype html><html><head><title>UPS Süre Testi | ALO186</title><meta name=\"description\" content=\"UPS çalışma süresini hesaplayın.\"></head><body><h1>UPS kaç saat çalışır?</h1><script type=\"application/ld+json\">{\"@context\":\"https://schema.org\",\"@type\":\"DefinedTerm\",\"name\":\"UPS çalışma süresi\"}</script></body></html>""",
            encoding="utf-8",
        )
        (site / "alias").mkdir(parents=True)
        (site / "alias/index.html").write_text(
            "<!doctype html><html><head><title>Eski UPS sayfası</title><meta name=\"robots\" content=\"noindex,follow\"></head><body><h1>Eski içerik</h1></body></html>",
            encoding="utf-8",
        )
        release = {
            "generatedAt": "2026-07-29",
            "routeCount": 3,
            "routes": [
                {"canonicalPath": "/arama/", "source": "alo186/arama/index.html", "type": "tool"},
                {"canonicalPath": "/tool/", "source": "alo186/tool/index.html", "type": "calculator"},
                {"canonicalPath": "/alias", "source": "alo186/alias/index.html", "type": "article"},
            ],
        }
        (site / "alo186-release.json").write_text(json.dumps(release), encoding="utf-8")

        payload = generate_index(site, "/chatgpt")
        assert payload["entryCount"] == 1
        entry = payload["entries"][0]
        assert entry["canonicalPath"] == "/tool/"
        assert entry["url"] == "/chatgpt/tool/"
        assert entry["bucket"] == "calculator"
        assert "UPS çalışma süresi" in entry["topics"]
        assert not any(item["canonicalPath"] == "/alias" for item in payload["entries"])
        assert payload["commercialRankingExcluded"] == [
            "price", "stock", "rating", "seller", "warranty", "affiliateCommission"
        ]


def main() -> None:
    test_source_contracts()
    test_generator_excludes_noindex_and_prefixes_project_urls()
    print(json.dumps({
        "ok": True,
        "route": "/arama/",
        "rawQueryStored": False,
        "commercialRankingUsed": False,
        "noindexAliasesExcluded": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
