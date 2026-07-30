from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "climate": ROOT / "alo186/hesaplama/klima-yedek-guc-uygunluk/index.html",
    "camp": ROOT / "alo186/hesaplama/kamp-karavan-power-station-gunes-paneli-uygunluk/index.html",
    "guide": ROOT / "alo186/sektor-rehberi/yaz-elektrik-kesintisi-hazirlik-merkezi/index.html",
}
ROUTES = {
    "hesaplama/klima-yedek-guc-uygunluk/index.html",
    "hesaplama/kamp-karavan-power-station-gunes-paneli-uygunluk/index.html",
    "sektor-rehberi/yaz-elektrik-kesintisi-hazirlik-merkezi/index.html",
}
OVERLAY = ROOT / "alo186/deployment/routing-overlays/124-summer-continuity.json"


class Audit(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.controls: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        if tag in {"input", "select", "textarea"}:
            self.controls.append(values)


def run(*command: str) -> None:
    subprocess.run(list(command), cwd=ROOT, check=True)


def inline_scripts(text: str) -> list[str]:
    return [
        match.group(1)
        for match in re.finditer(r"<script(?![^>]*application/ld\+json)[^>]*>(.*?)</script>", text, re.I | re.S)
        if match.group(1).strip()
    ]


def audit_page(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    audit = Audit()
    audit.feed(text)
    assert audit.h1 == 1, (path, audit.h1)
    for token in ("<title>", 'name="description"', 'rel="canonical"', "bağımsız", "fiyat", "stok", "satış ortaklığı"):
        assert token in lower, (path, token)
    assert "resmî" in lower or "resmi" in lower or "kamu kurumu" in lower, path
    assert "yeni ürün almay" in lower, path
    for token in (
        '"@type":"Product"', '"@type": "Product"', '"@type":"Offer"', '"@type": "Offer"',
        "priceCurrency", "availability", "aggregateRating", "reviewRating",
        "localStorage", "sessionStorage", "navigator.geolocation", "XMLHttpRequest", "fetch(",
        "amazon.com", "amzn.to",
    ):
        assert token not in text, (path, token)
    personal = re.compile(r"(?:email|e-mail|telefon|phone|adres|address|tckn|kimlik|konum|location|plaka|plate|serial|seri)", re.I)
    for control in audit.controls:
        identity = " ".join(str(control.get(key) or "") for key in ("id", "name", "placeholder", "autocomplete"))
        assert not personal.search(identity), (path, identity)
    return text


climate = audit_page(PAGES["climate"])
for token in (
    "BTU ≠ elektrik W", "btu_only", "split_fixed", "heat_pump",
    "Aktif kesintide satın alma anlık çözüm değildir",
    "Sabit sistem için profesyonel tasarım gerekli",
    "Mevcut kaynak yeterli — yeni ürün almayın",
    "90 günlük yeniden test takvimi indir",
    'rel="sponsored nofollow noopener"', "checks.every",
):
    assert token in climate, token

camp = audit_page(PAGES["camp"])
for token in (
    "12 V buzdolabı", "dailyWh", "solarDailyWh", "vehicle_fixed",
    "Sabit araç tesisatı profesyonel doğrulama gerektirir",
    "Aktif kampta satın alma anlık çözüm değildir",
    "Mevcut sistem yeterli — yeni ürün almayın",
    "Gezi öncesi kontrol takvimi indir",
    'rel="sponsored nofollow noopener"',
):
    assert token in camp, token

guide = audit_page(PAGES["guide"])
for token in (
    "Yaz kesintisini <em>ürün listesiyle değil</em>",
    "60 saniyelik yaz hazırlık planı",
    "Kampanya bildirimi veya kişisel takip kullanılmaz",
    "90 günlük kontrol takvimi indir",
    "Planı JSON olarak indir",
    "../../hesaplama/klima-yedek-guc-uygunluk/",
    "../../hesaplama/kamp-karavan-power-station-gunes-paneli-uygunluk/",
    "../../hesaplama/buzdolabi-dondurucu-yedek-guc-uygunluk/",
    "../../hesaplama/modem-internet-yedekleme/",
):
    assert token in guide, token

for page in PAGES.values():
    for index, script in enumerate(inline_scripts(page.read_text(encoding="utf-8")), 1):
        with tempfile.NamedTemporaryFile("w", suffix=f"-{index}.js", encoding="utf-8", delete=False) as handle:
            handle.write(script)
            temp_js = Path(handle.name)
        try:
            run("node", "--check", str(temp_js))
        finally:
            temp_js.unlink(missing_ok=True)

overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
assert overlay["version"] == 124
assert overlay["generatedAt"] == "2026-07-31"
assert len(overlay["routes"]) == 3
assert {route["canonicalPath"] for route in overlay["routes"]} == {
    "/hesaplama/klima-yedek-guc-uygunluk/",
    "/hesaplama/kamp-karavan-power-station-gunes-paneli-uygunluk/",
    "/sektor-rehberi/yaz-elektrik-kesintisi-hazirlik-merkezi/",
}

with tempfile.TemporaryDirectory(prefix="alo186-summer-v124-") as folder:
    canonical = Path(folder) / "canonical"
    run(sys.executable, "alo186/deployment/build_static_site.py", "--output", str(canonical), "--commit", "summer-v124-test")
    results = []
    for name, base_path in (("custom", ""), ("project", "/chatgpt")):
        target = Path(folder) / name
        subprocess.run(["cp", "-a", str(canonical), str(target)], check=True)
        run(
            sys.executable, "alo186/deployment/prepare_github_pages.py",
            "--site", str(target), "--base-path", base_path,
            "--repository", "ozaneryavuz/chatgpt", "--commit", "summer-v124-test",
        )
        run(sys.executable, "alo186/deployment/smoke_github_pages.py", "--site", str(target), "--base-path", base_path)
        pages = sorted(target.rglob("*.html"))
        assert len(pages) >= 463, len(pages)
        for relative in ROUTES:
            rendered = (target / relative).read_text(encoding="utf-8")
            assert rendered.count('data-alo186-sitewide-ux="true"') == 2, relative
            assert "satış ortaklığı" in rendered.lower(), relative
        sitemap = (target / "sitemap.xml").read_text(encoding="utf-8")
        for route in overlay["routes"]:
            assert route["canonicalPath"] in sitemap, route["canonicalPath"]
        results.append({"target": name, "basePath": base_path, "pages": len(pages), "newRoutes": 3})

print(json.dumps({
    "ok": True,
    "version": 124,
    "actions": ["climate-backup-intent", "camp-caravan-energy-intent", "summer-repeat-visit-hub"],
    "targets": results,
    "unverifiedCommercialClaims": False,
    "directAmazonLinks": False,
    "affiliateDisclosure": True,
    "officialAffiliationClaimed": False,
    "personalDataCollected": False,
}, ensure_ascii=False))
