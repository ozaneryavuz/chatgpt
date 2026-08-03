from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from sitemap_routes import ensure_canonical_routes

ROUTES = {
    "damage": "/hesaplama/cihaz-hasari-basvuru-takibi/",
    "home": "/hesaplama/ev-elektrik-guvenligi-kontrolu/",
    "co": "/hesaplama/karbonmonoksit-alarmi-jenerator-guvenligi/",
}
SOURCES = {
    "damage": "alo186/hesaplama/cihaz-hasari-basvuru-takibi/index.html",
    "home": "alo186/hesaplama/ev-elektrik-guvenligi-kontrolu/index.html",
    "co": "alo186/hesaplama/karbonmonoksit-alarmi-jenerator-guvenligi/index.html",
}
HUB = Path("hesaplama/index.html")
PORTAL = Path("elektrik-portali/index.html")
PRODUCT = Path("amazon-elektrik-urunleri/index.html")
BUSINESS = Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html")
HUB_MARKER = 'data-alo186-growth-run9-tools="true"'
PORTAL_MARKER = 'data-alo186-growth-run9-journey="true"'
PRODUCT_MARKER = 'data-alo186-growth-run9-affiliate="true"'
BUSINESS_MARKER = 'data-alo186-growth-run9-business="true"'


def normalize_base_path(value: str) -> str:
    value = str(value or "").strip()
    return "" if not value or value == "/" else "/" + value.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def inject_before_main(path: Path, marker: str, section: str) -> int:
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return 0
    if "</main>" not in text:
        return 0
    path.write_text(text.replace("</main>", section + "</main>", 1), encoding="utf-8")
    return 1


def inject_hub(site: Path, base_path: str) -> int:
    path = site / HUB
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if HUB_MARKER in text:
        return 0
    cards = (
        f'<a class="tool-card" {HUB_MARKER} href="{public_url(base_path, ROUTES["damage"])}"><span class="eyebrow">10 iş günü · kanıt · resmî kanal</span><h2>Cihaz Hasarı Başvuru Takibi</h2><p>Kesinti veya gerilim olayı sonrası süreyi, kanıtları ve EDAŞ işlem durumunu kişisel veri vermeden izleyin.</p><b>Takip dosyasını oluştur →</b></a>'
        f'<a class="tool-card" href="{public_url(base_path, ROUTES["home"])}"><span class="eyebrow">Priz · kablo · RCD · yangın önleme</span><h2>Ev Elektrik Güvenliği Kontrolü</h2><p>Sabit tesisat riskini düşük riskli hazırlık ihtiyacından ayırın; güvenliyse satın almama sonucunu koruyun.</p><b>Ev kontrolünü başlat →</b></a>'
        f'<a class="tool-card" href="{public_url(base_path, ROUTES["co"])}"><span class="eyebrow">CO · jeneratör · alarm · temiz hava</span><h2>CO Alarmı ve Jeneratör Güvenliği</h2><p>Jeneratör konumu, egzoz, CO alarmı ve belirti durumunu acil güvenlik kapısıyla değerlendirin.</p><b>CO güvenliğini kontrol et →</b></a>'
    )
    anchor = '<section id="araclar" class="tool-grid">'
    if anchor not in text:
        raise RuntimeError("Hesaplama merkezi araç grid başlangıcı bulunamadı")
    path.write_text(text.replace(anchor, anchor + cards, 1), encoding="utf-8")
    return 3


def inject_entries(site: Path, base_path: str) -> int:
    portal = f'''<section {PORTAL_MARKER} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#f5f8fd"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Olayı belgeleyin · evi kontrol edin · görünmez riski ayırın</span><h2 style="color:#071631;margin:.4rem 0">Güveni satış baskısıyla değil, doğru zamanda doğru kanıtla büyütün.</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px"><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['damage'])}"><strong>Cihaz Hasarı Takibi</strong><br><span>10 iş günlük süreç, kanıt ve resmî başvuru durumunu izleyin.</span></a><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['home'])}"><strong>Ev Güvenliği Kontrolü</strong><br><span>Priz, kablo, koruma ve yangın hazırlığını tek listede ayırın.</span></a><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['co'])}"><strong>CO ve Jeneratör Güvenliği</strong><br><span>Tehlikeli konumda ürün yolunu kapatın; güvenli durumda alarm kapsamını kontrol edin.</span></a></div></section>'''
    product = f'''<section class="section" {PRODUCT_MARKER}><span class="eyebrow">Yeni güvenlik kapısı · CO alarmı</span><h2>CO alarmı, tehlikeli jeneratör kullanımını güvenli yapmaz.</h2><p class="lead">Önce jeneratör konumu, egzoz, belirti ve mevcut alarm kapsamını ücretsiz araçta doğrulayın. İç veya binaya yakın jeneratör kullanımında bütün affiliate yolları kapanır.</p><div class="actions"><a class="button secondary" href="{public_url(base_path, ROUTES['co'])}">CO ve jeneratör güvenliğini kontrol et</a><a class="button secondary" href="{public_url(base_path, ROUTES['home'])}">Ev elektrik güvenliğini kontrol et</a></div><div class="affiliate-disclosure"><strong>Reklam / satış ortaklığı sınırı:</strong> Yalnız güvenli kaynak koşulu ve gerçek alarm açığı doğrulanırsa teknik ürün merkezi açılabilir. Doğrudan ürün, fiyat, stok, puan veya garanti bilgisi bu panelde gösterilmez.</div></section>'''
    business = f'''<section {BUSINESS_MARKER} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#fff"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Ücretli incelemeden önce ücretsiz kanıt hazırlığı</span><h2 style="color:#071631;margin:.4rem 0">Hasar dosyasını ve bina güvenliği boşluklarını ölçülebilir kapsama dönüştürün.</h2><p>Cihaz hasarı takibi resmî başvuru değildir; ev güvenlik kontrolü de tesisat onayı değildir. Ücretsiz çıktılar, gereken servis raporu, elektrikçi iş emri veya bağımsız teknik inceleme kapsamını netleştirir.</p><div style="display:flex;flex-wrap:wrap;gap:10px"><a href="{public_url(base_path, ROUTES['damage'])}">Hasar takip dosyasını hazırla →</a><a href="{public_url(base_path, ROUTES['home'])}">Ev güvenliği ön kontrolünü aç →</a></div></section>'''
    return (
        inject_before_main(site / PORTAL, PORTAL_MARKER, portal)
        + inject_before_main(site / PRODUCT, PRODUCT_MARKER, product)
        + inject_before_main(site / BUSINESS, BUSINESS_MARKER, business)
    )


def append_sitemap(site: Path) -> None:
    path = site / "sitemap.xml"
    if not path.is_file():
        return
    ensure_canonical_routes(path, ROUTES.values())


def add_offline(site: Path, base_path: str) -> list[str]:
    path = site / "sw.js"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        raise RuntimeError("Service worker CRITICAL rota dizisi bulunamadı")
    routes = json.loads(match.group(1))
    added = []
    for route in ROUTES.values():
        url = public_url(base_path, route)
        if url not in routes:
            routes.append(url)
            added.append(url)
    if added:
        path.write_text(text[: match.start(1)] + json.dumps(routes, ensure_ascii=False) + text[match.end(1):], encoding="utf-8")
    return added


def update_manifest(site: Path, base_path: str) -> None:
    path = site / "manifest.webmanifest"
    if not path.is_file():
        return
    manifest = json.loads(path.read_text(encoding="utf-8"))
    shortcuts = manifest.setdefault("shortcuts", [])
    additions = [
        {"name": "Cihaz Hasarı Başvuru Takibi", "short_name": "Hasar Takibi", "url": public_url(base_path, ROUTES["damage"])},
        {"name": "Ev Elektrik Güvenliği", "short_name": "Ev Güvenliği", "url": public_url(base_path, ROUTES["home"])},
        {"name": "CO ve Jeneratör Güvenliği", "short_name": "CO Güvenliği", "url": public_url(base_path, ROUTES["co"])},
    ]
    for item in additions:
        if not any(isinstance(x, dict) and x.get("url") == item["url"] for x in shortcuts):
            shortcuts.append(item)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, cards: int, offline: list[str]) -> None:
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    routes = core.setdefault("routes", [])
    existing = {x.get("canonicalPath") for x in routes if isinstance(x, dict)}
    for key, route in ROUTES.items():
        if route not in existing:
            routes.append({"canonicalPath": route, "source": SOURCES[key], "type": "tool"})
    core["routeCount"] = len(routes)
    contract = {
        "version": 1,
        "routes": list(ROUTES.values()),
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "unverifiedCommercialFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "officialApplicationClaimed": False,
        "legalAdviceClaimed": False,
        "deviceDamageWindowBusinessDays": 10,
        "deviceDamageReminderApproximate": True,
        "homeSafetyReviewDays": 180,
        "coAlarmAffiliateGate": True,
        "indoorGeneratorAffiliateBlocked": True,
    }
    core["growthRun9"] = contract
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["routeCount"] = len(routes)
        pages["growthRun9"] = {**contract, "basePath": base_path, "routes": [public_url(base_path, r) for r in ROUTES.values()], "entryCardsInjected": cards, "offlineAdded": offline}
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    files = sorted(p for p in site.rglob("*") if p.is_file())
    path.write_text("\n".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(site).as_posix()}" for p in files) + "\n", encoding="utf-8")


def run(site: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    for key, route in ROUTES.items():
        target = site / route.strip("/") / "index.html"
        if not target.is_file():
            raise FileNotFoundError(f"Growth run9 rotası artifactta eksik: {key}: {target}")
    cards = inject_hub(site, base_path) + inject_entries(site, base_path)
    append_sitemap(site)
    offline = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_release(site, base_path, cards, offline)
    recompute(site)
    return {"ok": True, "basePath": base_path, "routes": [public_url(base_path, r) for r in ROUTES.values()], "entryCardsInjected": cards, "offlineAdded": offline, "rawPersonalDataCollected": False, "directAffiliateLinksAdded": 0, "noBuyOutcomePreserved": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
