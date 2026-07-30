from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "alo186" / "mevzuat"
ROUTE = "/mevzuat/"
CANONICAL = "https://www.alo186.com/mevzuat/"
REQUIRED_FILES = [
    "index.html", "styles.css", "app.js", "catalog.json", "catalog-core.json",
    "catalog-rules.json", "catalog-decisions.json", "catalog-related.json",
    "catalog-historical.json",
]
REQUIRED_CATEGORIES = {
    "Kanunlar", "Bakanlar Kurulu Kararları", "Mahkeme Kararları", "Yönetmelikler",
    "Tebliğler", "Usul ve Esaslar", "Yöntem ve Metodolojiler", "Kurul Kararları",
    "Tarife Kurul Kararları", "Diğer Mevzuatlar", "Mülga Tebliğler", "Mülga Yönetmelikler",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_catalog(root: Path):
    meta = read_json(root / "catalog.json")
    rows = []
    for item in meta["files"]:
        path = root / item["path"]
        assert path.is_file(), f"Katalog parçası eksik: {path}"
        chunk = read_json(path)
        assert chunk["entryColumns"] == ["title", "category", "status"]
        assert len(chunk["entries"]) == item["count"], (item["path"], len(chunk["entries"]), item["count"])
        rows.extend(chunk["entries"])
    return meta, rows


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold()).strip()


def assert_source_contract() -> dict:
    for name in REQUIRED_FILES:
        assert (MODULE / name).is_file(), f"Modül dosyası eksik: {name}"
    html = (MODULE / "index.html").read_text(encoding="utf-8")
    js = (MODULE / "app.js").read_text(encoding="utf-8")
    css = (MODULE / "styles.css").read_text(encoding="utf-8")
    meta, rows = load_catalog(MODULE)

    assert meta["schemaVersion"] == 3
    assert meta["source"]["officialTextPrevails"] is True
    assert urlparse(meta["source"]["url"]).hostname in {"epdk.gov.tr", "www.epdk.gov.tr"}
    assert meta["coverage"]["fullLegalTextMirrored"] is False
    assert meta["coverage"]["duplicateTitlesCollapsed"] is True
    assert meta["coverage"]["historicalEntriesIncluded"] is True
    assert meta["coverage"]["dailyOfficialDiffPlanned"] is True
    assert len(rows) == meta["coverage"]["uniqueEntryCount"] == 217
    assert sum(item["count"] for item in meta["categories"]) == 217
    assert {item["name"] for item in meta["categories"]} == REQUIRED_CATEGORIES
    assert len({f"{normalize(row[1])}::{normalize(row[0])}" for row in rows}) == len(rows)
    assert all(len(row) == 3 and row[0] and row[1] in REQUIRED_CATEGORIES for row in rows)
    titles = "\n".join(row[0] for row in rows)
    for token in [
        "6446 sayılı Elektrik Piyasası Kanunu",
        "Elektrik Piyasası Tüketici Hizmetleri Yönetmeliği",
        "Elektrik Piyasasında Lisanssız Elektrik Üretim Yönetmeliği",
        "Elektrik Piyasasında Depolama Faaliyetleri Yönetmeliği",
        "Elektrik Piyasasında Toplayıcılık Faaliyeti Yönetmeliği",
        "Elektrik Piyasası Ölçüm Sistemleri Yönetmeliği",
        "Mülga",
    ]:
        assert token in titles, f"Zorunlu mevzuat başlığı eksik: {token}"

    assert '<link rel="canonical" href="https://www.alo186.com/mevzuat/">' in html
    for schema_type in ["CollectionPage", "Dataset", "DefinedTermSet", "FAQPage", "BreadcrumbList"]:
        assert f'"@type":"{schema_type}"' in html
    for phrase in [
        "Elektrik Mevzuat Atlası", "EPDK resmî listesi", "Mülga ayrımı",
        "ALO186, EPDK, EDAŞ", "Resmî Gazete", "Kişisel verisiz çalışma dosyası",
    ]:
        assert phrase in html
    assert "catalog.json" in js and "meta.files" in js
    assert "localStorage" not in js and "sessionStorage" not in js and "geolocation" not in js
    assert not re.search(r"fetch\(['\"]https?://", js)
    assert "@media(max-width:720px)" in css and "prefers-reduced-motion" in css
    forbidden = re.compile(r"amazon\.|alo186rehber-21|aggregateRating|priceCurrency|availability|\"@type\":\"Product\"|\"@type\":\"Offer\"", re.I)
    assert not forbidden.search(html + js)
    assert not re.search(r'type=["\'](?:email|tel|text|file)["\']|<textarea', html, re.I)

    overlay = read_json(ROOT / "alo186/deployment/routing-overlays/102-epdk-elektrik-mevzuat-atlasi.json")
    assert overlay["version"] == 102
    assert overlay["routes"] == [{"source": "alo186/mevzuat/index.html", "canonicalPath": ROUTE, "type": "collection"}]
    sync = (ROOT / "alo186/deployment/sync_epdk_electricity_legislation.py").read_text(encoding="utf-8")
    for token in ["SOURCE_HOSTS", "MIN_ENTRIES = 150", "diff(old", "renamedCount", "--no-write", "write(args.output"]:
        assert token in sync
    return {"entries": len(rows), "categories": len(REQUIRED_CATEGORIES)}


def assert_site(site: Path, base_path: str) -> None:
    base_path = "" if not base_path or base_path == "/" else "/" + base_path.strip("/")
    module = site / "mevzuat"
    for name in REQUIRED_FILES:
        assert (module / name).is_file(), f"Artifact mevzuat dosyası eksik: {name}"
    html = (module / "index.html").read_text(encoding="utf-8")
    assert CANONICAL in html
    assert not re.search(r"amazon\.|aggregateRating|priceCurrency|availability", html, re.I)
    sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
    assert f"<loc>{CANONICAL}</loc>" in sitemap
    search_path = site / "arama/search-index.json"
    assert search_path.is_file(), "Teknik Arama indeksi eksik"
    search = read_json(search_path)
    entry = next(item for item in search.get("entries", []) if item.get("canonicalPath") == ROUTE)
    expected = f"{base_path}{ROUTE}" if base_path else ROUTE
    assert entry["url"] in {ROUTE, expected}
    assert "Mevzuat" in entry["title"] or "mevzuat" in entry.get("description", "").lower()
    meta, rows = load_catalog(module)
    assert len(rows) == meta["coverage"]["uniqueEntryCount"] >= 150


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    result = assert_source_contract()
    if args.site:
        assert_site(args.site.resolve(), args.base_path)
        result["site"] = str(args.site)
        result["basePath"] = args.base_path
    print(json.dumps({"ok": True, "route": ROUTE, **result}, ensure_ascii=False))


if __name__ == "__main__":
    main()
