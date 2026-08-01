from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SLUGS = (
    "bess-hucre-sicaklik-farki-hvac-sivi-sogutma-derating",
    "dc-hizli-sarj-izolasyon-hatasi-imd-arac-istasyon-ayrimi",
    "frekans-inverteri-motor-autotune-statik-doner-id-run",
)

overlay_path = ROOT / "deployment" / "routing-overlays" / "content-authority-run94.json"
overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
assert overlay["version"] == 160
assert overlay["generatedAt"] == "2026-08-01"
assert len(overlay["routes"]) == 3
routes = {item["canonicalPath"]: item for item in overlay["routes"]}

for slug in SLUGS:
    page = ROOT / "haberler" / slug / "index.html"
    assert page.exists()
    raw = page.read_text(encoding="utf-8")
    assert raw.count("<h1>") == 1
    assert f'https://alo186.com/haberler/{slug}' in raw
    assert f'/haberler/{slug}' in routes
    assert routes[f'/haberler/{slug}']["source"] == f'alo186/haberler/{slug}/index.html'
    assert '"@type":"Article"' in raw
    assert '"@type":"FAQPage"' in raw
    assert '"@type":"BreadcrumbList"' in raw
    assert raw.count('"@type":"DefinedTerm"') >= 10
    assert raw.count('"@type":"Question"') >= 5
    assert "Son doğrulama: 1 Ağustos 2026" in raw
    assert "Doğrudan cevap" in raw
    assert "10 adımlık" in raw
    assert "Teknik dosyada bulunması gereken 14 alan" in raw
    assert "Mevcut içerikten görev ayrımı" in raw
    assert "Bağımsızlık ve uygulama sınırı" in raw
    assert len(re.findall(r'href="/[^"]+"', raw)) >= 12

print("ALO186 içerik otoritesi run94: PASS")
