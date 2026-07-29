from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROUTE = "/hesaplama/aydinlatma-ihtiyac-ve-ampul-uygunluk/"
CANONICAL = "https://www.alo186.com" + ROUTE

parser = argparse.ArgumentParser()
parser.add_argument("--site", type=Path, required=True)
parser.add_argument("--base-path", default="")
args = parser.parse_args()
site = args.site.resolve()
base = "" if not args.base_path or args.base_path == "/" else "/" + args.base_path.strip("/")
public = f"{base}{ROUTE}" if base else ROUTE

page = site / "hesaplama/aydinlatma-ihtiyac-ve-ampul-uygunluk/index.html"
assert page.is_file()
html = page.read_text(encoding="utf-8")
assert CANONICAL in html and "affiliateAccepted" in html and "Satın alma gerekmez" in html
assert "amazon.com.tr" not in html.lower()
assert CANONICAL in (site / "sitemap.xml").read_text(encoding="utf-8")
search = json.loads((site / "arama/search-index.json").read_text(encoding="utf-8"))
assert any(item.get("canonicalPath") == ROUTE and item.get("url") == public for item in search.get("entries", []))
critical_match = re.search(r"const CRITICAL=(\[.*?\]);", (site / "sw.js").read_text(encoding="utf-8"), re.S)
assert critical_match and public in json.loads(critical_match.group(1))
manifest = json.loads((site / "manifest.webmanifest").read_text(encoding="utf-8"))
assert any(item.get("url") == public for item in manifest.get("shortcuts", []))
for relative in ["hesaplama/index.html", "elektrik-portali/index.html", "akilli-urun-secimi/index.html", "amazon-elektrik-urunleri/index.html"]:
    assert 'data-alo186-growth-run22-entry="true"' in (site / relative).read_text(encoding="utf-8")
amazon = (site / "amazon-elektrik-urunleri/index.html").read_text(encoding="utf-8")
assert 'data-alo186-lighting-deeplink-run22="true"' in amazon
release = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
meta = release["lightingSuitabilityCenter"]
assert meta["recordLimit"] == 8 and meta["recordTtlDays"] == 365 and meta["reviewDays"] == 180
assert meta["directAffiliateLinksAdded"] == 0 and meta["noBuyOutcomePreserved"] is True and meta["hazardCommerceClosed"] is True
pages = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
assert pages["lightingSuitabilityCenter"]["route"] == public
print(json.dumps({"ok": True, "route": public, "basePath": base}, ensure_ascii=False))
