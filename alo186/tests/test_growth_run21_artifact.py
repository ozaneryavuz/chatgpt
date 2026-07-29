from __future__ import annotations

import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--site", type=Path, required=True)
parser.add_argument("--base-path", default="")
args = parser.parse_args()
site = args.site.resolve()
base = "" if not args.base_path or args.base_path == "/" else "/" + args.base_path.strip("/")
route = site / "hesaplama/kesinti-hazirlik-envanteri/index.html"
assert route.is_file()
assert "doğrudan mağaza bağlantısı yoktur" in route.read_text(encoding="utf-8").lower()
amazon = (site / "amazon-elektrik-urunleri/index.html").read_text(encoding="utf-8")
assert 'data-alo186-risk-gate-run21="true"' in amazon
assert "Önce teknik uygunluğu doğrula" in amazon
for relative in ["hesaplama/index.html", "elektrik-portali/index.html", "akilli-urun-secimi/index.html", "amazon-elektrik-urunleri/index.html"]:
    assert 'data-alo186-growth-run21-entry="true"' in (site / relative).read_text(encoding="utf-8")
search = json.loads((site / "arama/search-index.json").read_text(encoding="utf-8"))
assert any(item.get("canonicalPath") == "/hesaplama/kesinti-hazirlik-envanteri/" for item in search["entries"])
release = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
meta = release["outagePreparednessInventory"]
assert meta["recordLimit"] == 12 and meta["recordTtlDays"] == 365 and meta["reviewDays"] == 90
assert meta["directAffiliateLinksAdded"] == 0 and meta["officialAffiliationClaimed"] is False
manifest = json.loads((site / "manifest.webmanifest").read_text(encoding="utf-8"))
expected = base + "/hesaplama/kesinti-hazirlik-envanteri/"
assert any(item.get("url") == expected for item in manifest.get("shortcuts", []))
assert expected in (site / "sw.js").read_text(encoding="utf-8")
print(json.dumps({"ok": True, "basePath": base, "route": expected}, ensure_ascii=False))
