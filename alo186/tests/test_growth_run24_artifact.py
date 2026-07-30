from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROUTE = "/hesaplama/home-office-internet-sureklilik-plani/"
CANONICAL = "https://www.alo186.com" + ROUTE

parser = argparse.ArgumentParser()
parser.add_argument("--site", type=Path, required=True)
parser.add_argument("--base-path", default="")
args = parser.parse_args()
site = args.site.resolve()
base = "" if not args.base_path or args.base_path == "/" else "/" + args.base_path.strip("/")
public = f"{base}{ROUTE}" if base else ROUTE

page = site / "hesaplama/home-office-internet-sureklilik-plani/index.html"
assert page.is_file()
html = page.read_text(encoding="utf-8")
assert CANONICAL in html and "affiliateAccepted" in html and "Satın alma gerekli değildir" in html
assert "amazon.com.tr" not in html.lower()
assert CANONICAL in (site / "sitemap.xml").read_text(encoding="utf-8")
search = json.loads((site / "arama/search-index.json").read_text(encoding="utf-8"))
assert any(item.get("canonicalPath") == ROUTE and item.get("url") == public for item in search.get("entries", []))
critical_match = re.search(r"const CRITICAL=(\[.*?\]);", (site / "sw.js").read_text(encoding="utf-8"), re.S)
assert critical_match and public in json.loads(critical_match.group(1))
manifest = json.loads((site / "manifest.webmanifest").read_text(encoding="utf-8"))
assert any(item.get("url") == public for item in manifest.get("shortcuts", []))
for relative in ["hesaplama/index.html", "elektrik-portali/index.html", "akilli-urun-secimi/index.html", "amazon-elektrik-urunleri/index.html", "elektrik-durum-merkezi/index.html"]:
    assert 'data-alo186-growth-run24-entry="true"' in (site / relative).read_text(encoding="utf-8")
release = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
meta = release["homeOfficeContinuity"]
assert meta["recordLimit"] == 12 and meta["recordTtlDays"] == 365 and meta["reviewDays"] == 30
assert meta["repeatedUpstreamEvidenceCount"] == 2 and meta["upstreamFailureSuppressesCommerce"] is True
assert meta["directAffiliateLinksAdded"] == 0 and meta["noBuyOutcomePreserved"] is True and meta["hazardCommerceClosed"] is True
pages = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
assert pages["homeOfficeContinuity"]["route"] == public
print(json.dumps({"ok": True, "route": public, "basePath": base}, ensure_ascii=False))
