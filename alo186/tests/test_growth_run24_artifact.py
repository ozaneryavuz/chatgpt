from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROUTE = "/hesaplama/home-office-internet-sureklilik-plani/"
SOURCE_PAGE = Path(__file__).resolve().parents[1] / "hesaplama/home-office-internet-sureklilik-plani/index.html"

parser = argparse.ArgumentParser()
parser.add_argument("--site", type=Path)
parser.add_argument("--base-path", default="")
args = parser.parse_args()

if args.site is None:
    assert SOURCE_PAGE.is_file()
    source_html = SOURCE_PAGE.read_text(encoding="utf-8")
    assert "affiliateAccepted" in source_html
    assert "Satın alma gerekli değildir" in source_html
    assert "repeatedUpstream" in source_html
    assert "Ticari yol kapalı" in source_html
    assert "amazon.com.tr" not in source_html.lower()
    print(json.dumps({"ok": True, "mode": "source", "route": ROUTE}, ensure_ascii=False))
    raise SystemExit(0)

site = args.site.resolve()
base = "" if not args.base_path or args.base_path == "/" else "/" + args.base_path.strip("/")
public = f"{base}{ROUTE}" if base else ROUTE

release_path = site / "alo186-release.json"
assert release_path.is_file()
release = json.loads(release_path.read_text(encoding="utf-8"))
canonical_origin = str(release.get("canonicalHost") or "").rstrip("/")
assert canonical_origin in {"https://alo186.com", "https://www.alo186.com"}
canonical = canonical_origin + ROUTE

page = site / "hesaplama/home-office-internet-sureklilik-plani/index.html"
assert page.is_file()
html = page.read_text(encoding="utf-8")
assert canonical in html
assert "affiliateAccepted" in html
assert "Satın alma gerekli değildir" in html
assert "repeatedUpstream" in html
assert "amazon.com.tr" not in html.lower()
assert canonical in (site / "sitemap.xml").read_text(encoding="utf-8")
search = json.loads((site / "arama/search-index.json").read_text(encoding="utf-8"))
assert any(item.get("canonicalPath") == ROUTE and item.get("url") == public for item in search.get("entries", []))
critical_match = re.search(r"const CRITICAL=(\[.*?\]);", (site / "sw.js").read_text(encoding="utf-8"), re.S)
assert critical_match and public in json.loads(critical_match.group(1))
manifest = json.loads((site / "manifest.webmanifest").read_text(encoding="utf-8"))
assert any(item.get("url") == public for item in manifest.get("shortcuts", []))
for relative in ["hesaplama/index.html", "elektrik-portali/index.html", "akilli-urun-secimi/index.html", "amazon-elektrik-urunleri/index.html", "elektrik-durum-merkezi/index.html"]:
    assert 'data-alo186-growth-run24-entry="true"' in (site / relative).read_text(encoding="utf-8")
meta = release["homeOfficeContinuity"]
assert meta["recordLimit"] == 12 and meta["recordTtlDays"] == 365 and meta["reviewDays"] == 30
assert meta["repeatedUpstreamEvidenceCount"] == 2 and meta["upstreamFailureSuppressesCommerce"] is True
assert meta["directAffiliateLinksAdded"] == 0 and meta["noBuyOutcomePreserved"] is True and meta["hazardCommerceClosed"] is True
pages = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
assert str(pages.get("canonicalHost") or "").rstrip("/") == canonical_origin
assert pages["homeOfficeContinuity"]["route"] == public
print(json.dumps({"ok": True, "mode": "artifact", "route": public, "basePath": base, "canonicalOrigin": canonical_origin}, ensure_ascii=False))
