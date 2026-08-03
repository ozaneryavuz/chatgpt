from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from sitemap_routes import ensure_canonical_routes

ROUTES = {
    "solar": "/hesaplama/power-station-gunes-paneli-uygunluk/",
    "alarm": "/hesaplama/duman-co-alarmi-bakim-gunlugu/",
    "ats": "/hesaplama/jenerator-ats-test-gunlugu/",
}
SOURCES = {
    "solar": "alo186/hesaplama/power-station-gunes-paneli-uygunluk/index.html",
    "alarm": "alo186/hesaplama/duman-co-alarmi-bakim-gunlugu/index.html",
    "ats": "alo186/hesaplama/jenerator-ats-test-gunlugu/index.html",
}
HUB = Path("hesaplama/index.html")
PORTAL = Path("elektrik-portali/index.html")
PRODUCT = Path("akilli-urun-secimi/index.html")
CORPORATE = Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html")
MARKERS = {
    HUB: 'data-alo186-growth-run11-tools="true"',
    PORTAL: 'data-alo186-growth-run11-journey="true"',
    PRODUCT: 'data-alo186-growth-run11-product-gates="true"',
    CORPORATE: 'data-alo186-growth-run11-service="true"',
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
    solar = public_url(base_path, ROUTES["solar"])
    alarm = public_url(base_path, ROUTES["alarm"])
    ats = public_url(base_path, ROUTES["ats"])
    injected = 0
    injected += inject_before_main_end(
        site / HUB,
        MARKERS[HUB],
        f'''<section {MARKERS[HUB]} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#f5f8fd"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Uyumluluk · bakım · tekrar test</span><h2 style="color:#071631">Üç yeni kişisel verisiz karar aracı</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px"><a href="{solar}"><strong>Power station panel uyumluluğu</strong><br>Voc, Isc, seri-paralel ve üretici kılavuzu kapısı.</a><a href="{alarm}"><strong>Duman/CO alarmı bakım günlüğü</strong><br>Aylık test, ürün yaşı ve doğrulanmış arıza takibi.</a><a href="{ats}"><strong>Jeneratör/ATS test günlüğü</strong><br>Motor egzersizi ile gerçek yük transferini ayırın.</a></div></section>''',
    )
    injected += inject_before_main_end(
        site / PORTAL,
        MARKERS[PORTAL],
        f'''<section {MARKERS[PORTAL]} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#fff"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Tekrar ziyaretin gerçek nedeni</span><h2 style="color:#071631">Satın alma dürtüsü yerine ölçüm ve bakım döngüsü</h2><p>Panel bağlantısını teknik sınırlarla doğrulayın; alarm ve jeneratör sistemlerini yerel günlükle yeniden test edin. Mevcut sistem yeterliyse satın almama geçerlidir.</p><div style="display:flex;flex-wrap:wrap;gap:12px"><a href="{solar}">Panel uyumluluğunu kontrol et →</a><a href="{alarm}">Alarm bakımını kaydet →</a><a href="{ats}">ATS test kanıtını kaydet →</a></div></section>''',
    )
    injected += inject_before_main_end(
        site / PRODUCT,
        MARKERS[PRODUCT],
        f'''<section {MARKERS[PRODUCT]} style="max-width:1180px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#fff9e8"><span style="font-size:.78rem;font-weight:900;color:#785200;text-transform:uppercase;letter-spacing:.06em">Affiliate öncesi kanıt kapıları</span><h2 style="color:#071631">Ürün yolu yalnız gerçek ihtiyaç doğrulanınca açılır</h2><p><a href="{solar}">Power station paneli</a> için elektriksel sınırlar ve üretici kılavuzu; <a href="{alarm}">duman/CO alarmı</a> için hizmet ömrü veya doğrulanmış test başarısızlığı gerekir. Acil tehlikede ticari yol daima kapalıdır.</p><small>Bu bölüm fiyat, stok, puan, satıcı veya garanti göstermez. Satış ortaklığı ilişkisi ürün yolunun yanında açıklanır.</small></section>''',
    )
    injected += inject_before_main_end(
        site / CORPORATE,
        MARKERS[CORPORATE],
        f'''<section class="specialist-services" {MARKERS[CORPORATE]}><div class="specialist-heading"><span class="eyebrow">Süreklilik kanıtı</span><h2>Jeneratör çalışmasını gerçek ATS transfer kabulünden ayırın</h2><p>Yerel test günlüğü ücretsizdir. Kaynak kabulü, yüklü transfer, geri dönüş veya alarm başarısızsa olay kayıtlarıyla bağımsız test kapsamına ilerlenebilir.</p></div><div class="actions"><a href="{ats}">Jeneratör/ATS test günlüğünü aç</a></div></section>''',
    )
    return injected


def append_sitemap(site: Path) -> None:
    ensure_canonical_routes(site / "sitemap.xml", ROUTES.values())


def append_search(site: Path, base_path: str) -> None:
    path = site / "arama/search-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.setdefault("entries", [])
    known = {x.get("canonicalPath") for x in entries if isinstance(x, dict)}
    metadata = {
        "solar": ("Power Station Güneş Paneli Uyumluluğu", "Voc, Isc, güç, seri-paralel, konnektör ve soğuk hava marjı."),
        "alarm": ("Duman ve CO Alarmı Bakım Günlüğü", "Aylık test, üretici ömrü, yeniden test ve güvenli değişim kararı."),
        "ats": ("Jeneratör ve ATS Test Günlüğü", "Yüksüz egzersiz, kaynak kabulü, yüklü transfer, geri dönüş ve alarm kanıtı."),
    }
    for key, route in ROUTES.items():
        if route in known:
            continue
        title, description = metadata[key]
        entries.append({"canonicalPath": route, "url": public_url(base_path, route), "title": title, "description": description, "bucket": "calculator" if key != "ats" else "business", "keywords": [key, "elektrik güvenliği", "yerel günlük", "satın almama"]})
    data["entryCount"] = len(entries)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, injected: int) -> None:
    path = site / "alo186-release.json"
    release = json.loads(path.read_text(encoding="utf-8"))
    routes = release.setdefault("routes", [])
    known = {x.get("canonicalPath") for x in routes if isinstance(x, dict)}
    for key, route in ROUTES.items():
        if route not in known:
            routes.append({"canonicalPath": route, "source": SOURCES[key], "type": "business-tool" if key == "ats" else "calculator"})
    release["routeCount"] = len(routes)
    release["growthRun11"] = {
        "version": 1,
        "routes": list(ROUTES.values()),
        "entryPointsInjected": injected,
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "qualifiedAffiliateFlows": ["power_station_solar", "smoke_alarm", "co_alarm"],
        "professionalServiceFlows": ["generator_ats"],
        "affiliateDisclosureRequired": True,
        "unverifiedCommercialFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "officialApprovalClaimed": False,
        "emergencyCommerceClosed": True,
        "localOnlyJournals": ["alarm", "generator_ats"],
        "alarmJournalTtlDays": 400,
        "generatorAtsJournalTtlDays": 540,
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["routeCount"] = len(routes)
        pages["growthRun11"] = {"version": 1, "basePath": base_path, "routes": [public_url(base_path, r) for r in ROUTES.values()], "entryPointsInjected": injected, "directAffiliateLinksAdded": 0, "emergencyCommerceClosed": True}
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
            current.append(url); added += 1
    if added:
        path.write_text(text[:match.start(1)] + json.dumps(current, ensure_ascii=False) + text[match.end(1):], encoding="utf-8")
    return added


def update_manifest(site: Path, base_path: str) -> None:
    path = site / "manifest.webmanifest"
    if not path.is_file():
        return
    manifest = json.loads(path.read_text(encoding="utf-8"))
    shortcuts = manifest.setdefault("shortcuts", [])
    for name, route in [("Alarm Bakım Günlüğü", ROUTES["alarm"]), ("Jeneratör ATS Günlüğü", ROUTES["ats"])]:
        url = public_url(base_path, route)
        if not any(x.get("url") == url for x in shortcuts if isinstance(x, dict)):
            shortcuts.append({"name": name, "short_name": name, "url": url})
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists(): path.unlink()
    files = sorted(x for x in site.rglob("*") if x.is_file())
    path.write_text("\n".join(f"{hashlib.sha256(x.read_bytes()).hexdigest()}  {x.relative_to(site).as_posix()}" for x in files) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve(); base_path = normalize_base_path(base_path)
    for key, route in ROUTES.items():
        target = site / route.strip("/") / "index.html"
        app = target.with_name("app.js")
        if not target.is_file() or not app.is_file():
            raise FileNotFoundError(f"Growth run11 rota veya app eksik: {target}")
    injected = inject_entries(site, base_path)
    append_sitemap(site); append_search(site, base_path); update_release(site, base_path, injected)
    offline_added = add_offline(site, base_path); update_manifest(site, base_path); recompute(site)
    return {"ok": True, "basePath": base_path, "routes": [public_url(base_path, r) for r in ROUTES.values()], "entryPointsInjected": injected, "offlineAdded": offline_added, "directAffiliateLinksAdded": 0, "rawPersonalDataCollected": False, "emergencyCommerceClosed": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
