from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
manifest = json.loads((ROOT / "alo186/deployment/live-domain-integration.json").read_text(encoding="utf-8"))
workflow = (ROOT / ".github/workflows/alo186-live-domain-acceptance.yml").read_text(encoding="utf-8")

assert manifest["productionOrigin"] == "https://www.alo186.com"
assert manifest["apexOrigin"] == "https://alo186.com"
assert len(manifest["requiredRoutes"]) >= 6
for route in [
    "/hesaplama/aydinlatma-ihtiyac-ve-ampul-uygunluk/",
    "/hesaplama/kesinti-hazirlik-envanteri/",
    "/akilli-urun-secimi/",
    "/sitemap.xml",
]:
    assert route in manifest["requiredRoutes"]
    assert route in workflow
for token in [
    "Bağımsız bilgilendirme platformudur",
    "Amazon.*satış ortaklığı",
    "Mevcut ürün yeterliyse",
    "priceCurrency|aggregateRating|availability",
]:
    assert token in workflow
print(json.dumps({"ok": True, "routes": len(manifest["requiredRoutes"])}, ensure_ascii=False))
