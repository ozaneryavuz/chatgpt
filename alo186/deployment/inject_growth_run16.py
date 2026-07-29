from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROUTES = {
    "mode2": "/hesaplama/tasinabilir-ev-sarj-cihazi-priz-uygunluk/",
    "mini": "/hesaplama/modem-ont-mini-ups-sure-saglik-gunlugu/",
    "voltage": "/hesaplama/priz-tipi-gerilim-monitoru-uygunluk/",
}
SOURCES = {key: f"alo186/{route.strip('/')}/index.html" for key, route in ROUTES.items()}
HUB = Path("hesaplama/index.html")
PORTAL = Path("elektrik-portali/index.html")
PRODUCT = Path("akilli-urun-secimi/index.html")
CORPORATE = Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html")
MARKERS = {
    HUB: 'data-alo186-growth-run16-tools="true"',
    PORTAL: 'data-alo186-growth-run16-evidence="true"',
    PRODUCT: 'data-alo186-growth-run16-affiliate="true"',
    CORPORATE: 'data-alo186-growth-run16-service="true"',
}


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def inject_before_main_end(path: Path, marker: str, content: str) -> int:
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return 0
    if "</main>" not in text:
        raise RuntimeError(f"main kapanışı bulunamadı: {path}")
    path.write_text(text.replace("</main>", content + "</main>", 1), encoding="utf-8")
    return 1


def inject_entries(site: Path, base_path: str) -> int:
    mode2, mini, voltage = (public_url(base_path, ROUTES[key]) for key in ("mode2", "mini", "voltage"))
    injected = 0
    injected += inject_before_main_end(site / HUB, MARKERS[HUB], f'''<section {MARKERS[HUB]} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#f5f8fd"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Satın alma öncesi güven · gerçek süre · kanıt kapsamı</span><h2 style="color:#071631">Üç yeni güven ve tekrar ziyaret aracı</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px"><a href="{mode2}"><strong>Taşınabilir EV şarj ve priz uygunluğu</strong><br>Mode 2 cihazı priz, devre, PE ve sıcaklık kapısıyla değerlendirin.</a><a href="{mini}"><strong>Mini UPS gerçek süre sağlığı</strong><br>İlk kısa süreden önce tam şarj ve eşit yükle yeniden test yapın.</a><a href="{voltage}"><strong>Priz tipi gerilim monitörü</strong><br>Ön gözlem ile EDAŞ/profesyonel güç kalitesi kaydını ayırın.</a></div></section>''')
    injected += inject_before_main_end(site / PORTAL, MARKERS[PORTAL], f'''<section {MARKERS[PORTAL]} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#fff"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Kanıt kapsamını doğru seçin</span><h2 style="color:#071631">Priz gözlemini resmî teknik kalite ölçümü sanmayın</h2><p>Tek priz, bina geneli, üç faz, harmonik ve EDAŞ teknik kalite ölçümü farklı cihaz ve süreçler gerektirir. Taşınabilir EV şarjında ise ürün seçmeden önce priz ve devre güvenliği doğrulanır.</p><div style="display:flex;flex-wrap:wrap;gap:12px"><a href="{voltage}">Gerilim ölçüm kapsamını seç →</a><a href="{mode2}">Mode 2 priz güvenliğini aç →</a></div></section>''')
    injected += inject_before_main_end(site / PRODUCT, MARKERS[PRODUCT], f'''<section {MARKERS[PRODUCT]} style="max-width:1180px;margin:34px auto;padding:24px;border:1px solid #dfbd57;border-radius:22px;background:#fff9e8"><span style="font-size:.78rem;font-weight:900;color:#785200;text-transform:uppercase;letter-spacing:.06em">Affiliate öncesi fail-closed kapı</span><h2 style="color:#071631">Ürün bağlantısı yalnız gerçek ihtiyaç ve güvenlik kanıtı oluşursa açılır</h2><p><a href="{mode2}">Mode 2 araç</a> günlük/yüksek akımlı veya tehlikeli priz kullanımını ticari rotaya göndermez. <a href="{mini}">Mini UPS günlüğü</a> ilk düşük sürede yeniden test ister. <a href="{voltage}">Gerilim monitörü</a> bina, komşu, üç faz, harmonik ve resmî ölçüm niyetinde affiliate yolunu kapatır.</p><small>Satış ortaklığı yalnız nitelendirilmiş kategori bağlantısının yanında açıklanır; fiyat, stok, puan, satıcı ve garanti gösterilmez.</small></section>''')
    injected += inject_before_main_end(site / CORPORATE, MARKERS[CORPORATE], f'''<section class="specialist-services" {MARKERS[CORPORATE]}><div class="specialist-heading"><span class="eyebrow">Kanıtlı süreklilik ve güç kalitesi</span><h2>EV priz kabulü, ağ yedekleme süresi ve gerilim olayını profesyonel ölçüm işine dönüştürün</h2><p>Ücretsiz araçlar kişisel veri istemeden ön dosya oluşturur. Günlük EV şarjı, tekrar eden mini UPS kaybı veya bina geneli gerilim olayı; ürün satışından önce devre kabulü, süre testi ya da güç kalitesi kaydına yönelir.</p></div><div class="actions"><a href="{mode2}">EV priz ön dosyası</a><a href="{mini}">Mini UPS süre kaydı</a><a href="{voltage}">Gerilim kanıt kapsamı</a></div></section>''')
    return injected


def append_sitemap(site: Path) -> None:
    path = site / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    for route in ROUTES.values():
        loc = f"https://www.alo186.com{route}"
        if f"<loc>{loc}</loc>" not in text:
            text = text.replace("</urlset>", f"<url><loc>{loc}</loc></url></urlset>", 1)
    path.write_text(text, encoding="utf-8")


def append_search(site: Path, base_path: str) -> None:
    path = site / "arama/search-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.setdefault("entries", [])
    known = {item.get("canonicalPath") for item in entries if isinstance(item, dict)}
    metadata = {
        "mode2": ("Taşınabilir EV Şarj Cihazı ve Priz Uygunluk Günlüğü", "Mode 2 IC-CPD cihazını priz, PE, devre, koruma, sıcaklık ve kullanım sıklığıyla değerlendirin.", "calculator", ["Mode 2", "IC-CPD", "taşınabilir EV şarj", "Schuko şarj", "priz ısınıyor"]),
        "mini": ("Modem ve ONT Mini UPS Gerçek Süre Sağlık Günlüğü", "Mini UPS gerçek çalışma süresini tam şarj, eşit yük ve yeniden test kanıtıyla izleyin.", "calculator", ["mini UPS süre testi", "modem UPS kaç saat", "ONT yedekleme", "mini UPS batarya sağlığı"]),
        "voltage": ("Priz Tipi Gerilim Monitörü Uygunluk ve 7 Günlük Kanıt Günlüğü", "Basit min/max gözlemini bina geneli, harmonik ve EDAŞ teknik kalite ölçümünden ayırın.", "calculator", ["priz tipi voltmetre", "gerilim monitörü", "voltaj kaydedici", "7 günlük gerilim", "EDAŞ ölçüm"]),
    }
    for key, route in ROUTES.items():
        if route in known:
            continue
        title, description, bucket, keywords = metadata[key]
        entries.append({"canonicalPath": route, "url": public_url(base_path, route), "title": title, "description": description, "bucket": bucket, "keywords": keywords})
    data["entryCount"] = len(entries)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def patch_catalog(site: Path) -> int:
    path = site / "akilli-urun-secimi" / "catalog.js"
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    additions = []
    if "id:'ev_mobile_charger'" not in text:
        additions.append("{id:'ev_mobile_charger',name:'Taşınabilir Mode 2 EV şarj cihazı',mode:'guide',risk:'safety',affiliatePolicy:'after_tool',nextStepUrl:'https://www.alo186.com/hesaplama/tasinabilir-ev-sarj-cihazi-priz-uygunluk/',nextStepLabel:'Önce priz, PE, devre, IC-CPD ve sıcaklık güvenliğini doğrula',description:'Günlük kullanım, priz/devre belirsizliği, yüksek akım, uzatma-adaptör veya ısınma varken ürün rotası açılmaz.',searchQuery:'Mode 2 taşınabilir EV şarj cihazı IC-CPD sıcaklık algılama'}")
    if "id:'voltage_monitor'" not in text:
        additions.append("{id:'voltage_monitor',name:'Priz tipi gerilim monitörü ve kayıt cihazı',mode:'guide',risk:'measurement',affiliatePolicy:'after_tool',nextStepUrl:'https://www.alo186.com/hesaplama/priz-tipi-gerilim-monitoru-uygunluk/',nextStepLabel:'Önce olay kapsamı, kayıt süresi ve resmî ölçüm gereğini değerlendir',description:'Yalnız düşük riskli tek priz/oda ön gözlemi için nitelendirilir; bina, komşu, üç faz, harmonik ve resmî teknik kalite için profesyonel ölçüm gerekir.',searchQuery:'priz tipi voltaj gerilim monitörü min max zaman kayıt'}")
    if not additions:
        return 0
    marker = "\n  ];\n\n  const products="
    if marker not in text:
        raise RuntimeError("catalog categories kapanışı bulunamadı")
    text = text.replace(marker, ",\n    " + ",\n    ".join(additions) + marker, 1)
    path.write_text(text, encoding="utf-8")
    return len(additions)


def update_release(site: Path, base_path: str, injected: int, catalog_added: int) -> None:
    path = site / "alo186-release.json"
    release = json.loads(path.read_text(encoding="utf-8"))
    routes = release.setdefault("routes", [])
    known = {item.get("canonicalPath") for item in routes if isinstance(item, dict)}
    for key, route in ROUTES.items():
        if route not in known:
            routes.append({"canonicalPath": route, "source": SOURCES[key], "type": "calculator"})
    release["routeCount"] = len(routes)
    release["growthRun16"] = {
        "version": 1,
        "routes": list(ROUTES.values()),
        "entryPointsInjected": injected,
        "catalogCategoriesAdded": catalog_added,
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "qualifiedAffiliateFlows": ["mode2_ev_charger_after_full_socket_and_document_gate", "mini_ups_after_failed_confirmed_runtime_retest", "plug_voltage_monitor_for_low_risk_single_circuit_observation"],
        "professionalServiceFlows": ["ev_outlet_and_dedicated_circuit_acceptance", "network_backup_runtime_verification", "distribution_voltage_quality_and_power_quality_logging"],
        "affiliateDisclosureRequired": True,
        "unverifiedCommercialFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "officialApprovalClaimed": False,
        "emergencyCommerceClosed": True,
        "buildingWideCommerceClosed": True,
        "mode2JournalTtlDays": 540,
        "miniUpsJournalTtlDays": 730,
        "voltageMonitorJournalTtlDays": 365,
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["routeCount"] = len(routes)
        pages["growthRun16"] = {"version": 1, "basePath": base_path, "routes": [public_url(base_path, route) for route in ROUTES.values()], "entryPointsInjected": injected, "directAffiliateLinksAdded": 0, "buildingWideCommerceClosed": True}
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_offline(site: Path, base_path: str) -> int:
    path = site / "sw.js"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        return 0
    current = json.loads(match.group(1))
    added = 0
    for route in ROUTES.values():
        url = public_url(base_path, route)
        if url not in current:
            current.append(url)
            added += 1
    if added:
        path.write_text(text[: match.start(1)] + json.dumps(current, ensure_ascii=False) + text[match.end(1) :], encoding="utf-8")
    return added


def update_manifest(site: Path, base_path: str) -> None:
    path = site / "manifest.webmanifest"
    if not path.is_file():
        return
    manifest = json.loads(path.read_text(encoding="utf-8"))
    shortcuts = manifest.setdefault("shortcuts", [])
    for name, route in [("Mode 2 Priz Uygunluğu", ROUTES["mode2"]), ("Mini UPS Süre Sağlığı", ROUTES["mini"]), ("Gerilim Monitörü", ROUTES["voltage"])]:
        url = public_url(base_path, route)
        if not any(item.get("url") == url for item in shortcuts if isinstance(item, dict)):
            shortcuts.append({"name": name, "short_name": name, "url": url})
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    files = sorted(item for item in site.rglob("*") if item.is_file())
    path.write_text("\n".join(f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}" for item in files) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    for route in ROUTES.values():
        target = site / route.strip("/") / "index.html"
        app = target.with_name("app.js")
        if not target.is_file() or not app.is_file():
            raise FileNotFoundError(f"Growth run16 rota veya app eksik: {target}")
    injected = inject_entries(site, base_path)
    append_sitemap(site)
    append_search(site, base_path)
    catalog_added = patch_catalog(site)
    update_release(site, base_path, injected, catalog_added)
    offline_added = add_offline(site, base_path)
    update_manifest(site, base_path)
    recompute(site)
    return {"ok": True, "basePath": base_path, "routes": [public_url(base_path, route) for route in ROUTES.values()], "entryPointsInjected": injected, "catalogCategoriesAdded": catalog_added, "offlineAdded": offline_added, "directAffiliateLinksAdded": 0, "rawPersonalDataCollected": False, "officialApprovalClaimed": False, "buildingWideCommerceClosed": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
