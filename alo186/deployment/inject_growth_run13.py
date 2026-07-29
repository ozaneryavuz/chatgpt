from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROUTES = {
    "damage": "/hesaplama/elektrik-cihaz-hasari-edas-basvuru-paketi/",
    "energy": "/hesaplama/akilli-priz-enerji-anomali-gunlugu/",
    "surge": "/hesaplama/akim-korumali-grup-priz-saglik-gunlugu/",
}
SOURCES = {key: f"alo186/{route.strip('/')}/index.html" for key, route in ROUTES.items()}
HUB = Path("hesaplama/index.html")
PORTAL = Path("elektrik-portali/index.html")
PRODUCT = Path("akilli-urun-secimi/index.html")
CORPORATE = Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html")
MARKERS = {
    HUB: 'data-alo186-growth-run13-tools="true"',
    PORTAL: 'data-alo186-growth-run13-official="true"',
    PRODUCT: 'data-alo186-growth-run13-affiliate="true"',
    CORPORATE: 'data-alo186-growth-run13-service="true"',
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
    damage, energy, surge = (public_url(base_path, ROUTES[key]) for key in ("damage", "energy", "surge"))
    outage = public_url(base_path, "/elektrik-kesintisi/")
    injected = 0
    injected += inject_before_main_end(site / HUB, MARKERS[HUB], f'''<section {MARKERS[HUB]} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#f5f8fd"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Resmî süre · aylık ölçüm · ürün yaşam döngüsü</span><h2 style="color:#071631">Üç yeni güven ve sürdürülebilir büyüme aracı</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px"><a href="{damage}"><strong>Cihaz hasarı EDAŞ başvuru paketi</strong><br>10 iş günlük süreyi, kanıtı ve resmî takip adımlarını düzenleyin.</a><a href="{energy}"><strong>Akıllı priz enerji günlüğü</strong><br>kWh ve çalışma süresini aylık karşılaştırın; tek artışla arıza kararı vermeyin.</a><a href="{surge}"><strong>Grup priz sağlık günlüğü</strong><br>Koruma göstergesi, topraklama uyarısı ve fiziksel durumu periyodik izleyin.</a></div></section>''')
    injected += inject_before_main_end(site / PORTAL, MARKERS[PORTAL], f'''<section {MARKERS[PORTAL]} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#fff"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Kesinti sonrası hak ve kanıt yolu</span><h2 style="color:#071631">Cihaz hasarında süreyi kaçırmadan, kişisel veri vermeden hazırlanın</h2><p>ALO186 başvuru almaz ve haklılık kararı vermez. Ücretsiz paket, 10 iş günlük başvuru süresini ve dağıtım şirketine götürülecek kanıt kontrolünü düzenler.</p><div style="display:flex;flex-wrap:wrap;gap:12px"><a href="{damage}">Başvuru paketini oluştur →</a><a href="{outage}">Görevli EDAŞ kanalını bul →</a></div></section>''')
    injected += inject_before_main_end(site / PRODUCT, MARKERS[PRODUCT], f'''<section {MARKERS[PRODUCT]} style="max-width:1180px;margin:34px auto;padding:24px;border:1px solid #dfbd57;border-radius:22px;background:#fff9e8"><span style="font-size:.78rem;font-weight:900;color:#785200;text-transform:uppercase;letter-spacing:.06em">Affiliate öncesi kullanım ve yaşam döngüsü kanıtı</span><h2 style="color:#071631">Akıllı priz ve grup priz, yalnız doğrulanmış ihtiyaçta kategoriye ilerler</h2><p><a href="{energy}">Enerji anomali günlüğü</a> mevcut ölçüm aracınız yeterliyse satın almama sonucu verir. <a href="{surge}">Grup priz sağlık günlüğü</a> topraklama uyarısı veya fiziksel riskte mağaza yolunu kapatır.</p><small>Satış ortaklığı yalnız sonuçtaki kategori bağlantısının yanında açıklanır. Fiyat, stok, puan, satıcı veya garanti gösterilmez.</small></section>''')
    injected += inject_before_main_end(site / CORPORATE, MARKERS[CORPORATE], f'''<section class="specialist-services" {MARKERS[CORPORATE]}><div class="specialist-heading"><span class="eyebrow">Hasar ve tüketim kanıtı</span><h2>Başvuru, servis ve enerji incelemesi öncesinde kapalı kanıt alanlarını hazırlayın</h2><p>Cihaz hasarı paketi resmî süreyi; enerji günlüğü ise karşılaştırılabilir tüketim geçmişini düzenler. Ücretsiz çıktı, ücretli hizmet veya ekipman zorunluluğu değildir.</p></div><div class="actions"><a href="{damage}">Cihaz hasarı paketini aç</a><a href="{energy}">Enerji günlüğünü aç</a></div></section>''')
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
        "damage": ("Elektrik Cihaz Hasarı EDAŞ Başvuru Paketi", "10 iş günlük başvuru süresi, kapalı kanıt kontrolü ve resmî dağıtım şirketi takibi.", "business"),
        "energy": ("Akıllı Priz Enerji Anomali Günlüğü", "Aylık kWh, çalışma süresi, ortalama güç ve tekrarlayan tüketim değişimi.", "calculator"),
        "surge": ("Akım Korumalı Grup Priz Sağlık Günlüğü", "Koruma göstergesi, topraklama uyarısı, fiziksel sağlık ve doğrulanmış değiştirme ihtiyacı.", "calculator"),
    }
    for key, route in ROUTES.items():
        if route in known:
            continue
        title, description, bucket = metadata[key]
        entries.append({"canonicalPath": route, "url": public_url(base_path, route), "title": title, "description": description, "bucket": bucket, "keywords": [key, "kişisel verisiz", "satın almama", "elektrik güvenliği"]})
    data["entryCount"] = len(entries)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, injected: int) -> None:
    path = site / "alo186-release.json"
    release = json.loads(path.read_text(encoding="utf-8"))
    routes = release.setdefault("routes", [])
    known = {item.get("canonicalPath") for item in routes if isinstance(item, dict)}
    for key, route in ROUTES.items():
        if route not in known:
            routes.append({"canonicalPath": route, "source": SOURCES[key], "type": "business-tool" if key == "damage" else "calculator"})
    release["routeCount"] = len(routes)
    release["growthRun13"] = {
        "version": 1,
        "routes": list(ROUTES.values()),
        "entryPointsInjected": injected,
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "qualifiedAffiliateFlows": ["energy_monitoring_smart_plug", "surge_protected_power_strip"],
        "professionalAndOfficialFlows": ["distribution_company_damage_application", "electrical_wiring_check"],
        "affiliateDisclosureRequired": True,
        "unverifiedCommercialFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "officialApprovalClaimed": False,
        "emergencyCommerceClosed": True,
        "deviceDamageDeadlineBusinessDays": 10,
        "smartPlugJournalTtlDays": 730,
        "surgeStripJournalTtlDays": 540,
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["routeCount"] = len(routes)
        pages["growthRun13"] = {"version": 1, "basePath": base_path, "routes": [public_url(base_path, route) for route in ROUTES.values()], "entryPointsInjected": injected, "directAffiliateLinksAdded": 0, "emergencyCommerceClosed": True}
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_offline(site: Path, base_path: str) -> int:
    path = site / "sw.js"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        return 0
    current = json.loads(match.group(1)); added = 0
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
    manifest = json.loads(path.read_text(encoding="utf-8")); shortcuts = manifest.setdefault("shortcuts", [])
    for name, route in [("Cihaz Hasarı Başvuru", ROUTES["damage"]), ("Akıllı Priz Enerji", ROUTES["energy"]), ("Grup Priz Sağlığı", ROUTES["surge"])]:
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
    site = site.resolve(); base_path = normalize_base_path(base_path)
    for route in ROUTES.values():
        target = site / route.strip("/") / "index.html"
        app = target.with_name("app.js")
        if not target.is_file() or not app.is_file():
            raise FileNotFoundError(f"Growth run13 rota veya app eksik: {target}")
    injected = inject_entries(site, base_path)
    append_sitemap(site); append_search(site, base_path); update_release(site, base_path, injected)
    offline_added = add_offline(site, base_path); update_manifest(site, base_path); recompute(site)
    return {"ok": True, "basePath": base_path, "routes": [public_url(base_path, route) for route in ROUTES.values()], "entryPointsInjected": injected, "offlineAdded": offline_added, "directAffiliateLinksAdded": 0, "rawPersonalDataCollected": False, "emergencyCommerceClosed": True}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--site", type=Path, required=True); parser.add_argument("--base-path", default="")
    args = parser.parse_args(); print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
