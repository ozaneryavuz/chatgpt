from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROUTES = {
    "extension": "/hesaplama/uzatma-kablosu-kablo-makarasi-uygunluk/",
    "emergency": "/hesaplama/acil-aydinlatma-test-bakim-gunlugu/",
    "voltage": "/hesaplama/gerilim-olayi-edas-olcum-talebi/",
}
SOURCES = {key: f"alo186/{route.strip('/')}/index.html" for key, route in ROUTES.items()}
HUB = Path("hesaplama/index.html")
PORTAL = Path("elektrik-portali/index.html")
PRODUCT = Path("akilli-urun-secimi/index.html")
CORPORATE = Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html")
MARKERS = {
    HUB: 'data-alo186-growth-run14-tools="true"',
    PORTAL: 'data-alo186-growth-run14-official="true"',
    PRODUCT: 'data-alo186-growth-run14-affiliate="true"',
    CORPORATE: 'data-alo186-growth-run14-service="true"',
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
    extension, emergency, voltage = (public_url(base_path, ROUTES[key]) for key in ("extension", "emergency", "voltage"))
    outage = public_url(base_path, "/elektrik-kesintisi/")
    injected = 0
    injected += inject_before_main_end(site / HUB, MARKERS[HUB], f'''<section {MARKERS[HUB]} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#f5f8fd"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Uygunluk · bakım döngüsü · resmî ölçüm hazırlığı</span><h2 style="color:#071631">Üç yeni güven ve tekrar ziyaret aracı</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px"><a href="{extension}"><strong>Uzatma kablosu ve makara uygunluğu</strong><br>Yük, uzunluk, kesit, etiket akımı ve sarılı kullanım riskini ayırın.</a><a href="{emergency}"><strong>Acil aydınlatma test günlüğü</strong><br>Fonksiyon, süre, bakım ve yeniden testi kayıtlı döngüye alın.</a><a href="{voltage}"><strong>Gerilim olayı ve EDAŞ ölçüm talebi</strong><br>Tek gözlem yerine tarihli, kaynak ayrımlı kanıt paketi oluşturun.</a></div></section>''')
    injected += inject_before_main_end(site / PORTAL, MARKERS[PORTAL], f'''<section {MARKERS[PORTAL]} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#fff"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Teknik kalite ve resmî kanal ayrımı</span><h2 style="color:#071631">Düşük-yüksek gerilim olayını kayıtlı ölçüm talebine dönüştürün</h2><p>ALO186 şikâyet almaz veya kusur tespiti yapmaz. Ücretsiz günlük, olay zamanı, kaynak, kapsam ve ölçüm yöntemini düzenleyerek görevli dağıtım şirketi başvurusuna hazırlanmanızı sağlar.</p><div style="display:flex;flex-wrap:wrap;gap:12px"><a href="{voltage}">Gerilim olay paketini oluştur →</a><a href="{outage}">Görevli EDAŞ kanalını bul →</a></div></section>''')
    injected += inject_before_main_end(site / PRODUCT, MARKERS[PRODUCT], f'''<section {MARKERS[PRODUCT]} style="max-width:1180px;margin:34px auto;padding:24px;border:1px solid #dfbd57;border-radius:22px;background:#fff9e8"><span style="font-size:.78rem;font-weight:900;color:#785200;text-transform:uppercase;letter-spacing:.06em">Affiliate öncesi teknik ve yaşam döngüsü kapısı</span><h2 style="color:#071631">Uzatma kablosu ve taşınabilir acil lamba yalnız doğrulanmış ihtiyaçta kategoriye ilerler</h2><p><a href="{extension}">Uzatma kablosu uygunluğu</a> etiket, topraklama, ortam ve makara riskini; <a href="{emergency}">acil aydınlatma günlüğü</a> ise ilk başarısızlık ile doğrulanmış değişim ihtiyacını ayırır.</p><small>Satış ortaklığı yalnız sonuçtaki kategori yolunun yanında açıklanır. Sabit kaçış sisteminde ve tehlike durumunda ticari yol kapalıdır.</small></section>''')
    injected += inject_before_main_end(site / CORPORATE, MARKERS[CORPORATE], f'''<section class="specialist-services" {MARKERS[CORPORATE]}><div class="specialist-heading"><span class="eyebrow">Periyodik kanıt ve ölçüm dönüşümü</span><h2>Acil aydınlatma kabulü ve gerilim kalitesi kaydını aynı kanıt disiplinine alın</h2><p>Fonksiyon/süre test geçmişi ile şebeke, jeneratör ve UPS kaynaklı gerilim olaylarını kişisel verisiz ön dosyada düzenleyin. Ücretsiz çıktı, ücretli hizmet veya ekipman zorunluluğu değildir.</p></div><div class="actions"><a href="{emergency}">Acil aydınlatma günlüğü</a><a href="{voltage}">Gerilim olay paketi</a></div></section>''')
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
        "extension": ("Uzatma Kablosu ve Kablo Makarası Uygunluğu", "Yük, uzunluk, kesit, etiket akımı, topraklama ve sarılı kullanım güvenliği.", "calculator", ["uzatma kablosu", "kablo makarası", "gerilim düşümü", "16 A"]),
        "emergency": ("Acil Aydınlatma Test ve Bakım Günlüğü", "Fonksiyon, süre, bakım sonrası yeniden test ve doğrulanmış değişim ihtiyacı.", "calculator", ["acil aydınlatma", "süre testi", "batarya", "bakım günlüğü"]),
        "voltage": ("Gerilim Olayı Günlüğü ve EDAŞ Ölçüm Talebi", "Düşük-yüksek gerilim, titreme ve faz olaylarını resmî ölçüm talebine hazırlayın.", "business", ["EDAŞ", "teknik kalite", "düşük gerilim", "yüksek gerilim", "ölçüm talebi"]),
    }
    for key, route in ROUTES.items():
        if route in known:
            continue
        title, description, bucket, keywords = metadata[key]
        entries.append({"canonicalPath": route, "url": public_url(base_path, route), "title": title, "description": description, "bucket": bucket, "keywords": keywords})
    data["entryCount"] = len(entries)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, injected: int) -> None:
    path = site / "alo186-release.json"
    release = json.loads(path.read_text(encoding="utf-8"))
    routes = release.setdefault("routes", [])
    known = {item.get("canonicalPath") for item in routes if isinstance(item, dict)}
    for key, route in ROUTES.items():
        if route not in known:
            routes.append({"canonicalPath": route, "source": SOURCES[key], "type": "business-tool" if key == "voltage" else "calculator"})
    release["routeCount"] = len(routes)
    release["growthRun14"] = {
        "version": 1,
        "routes": list(ROUTES.values()),
        "entryPointsInjected": injected,
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "qualifiedAffiliateFlows": ["extension_cord_after_tool", "portable_emergency_light_after_failed_retest"],
        "professionalAndOfficialFlows": ["fixed_emergency_lighting_acceptance", "distribution_company_voltage_quality_measurement", "power_quality_logging"],
        "affiliateDisclosureRequired": True,
        "unverifiedCommercialFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "officialApprovalClaimed": False,
        "emergencyCommerceClosed": True,
        "emergencyLightingJournalTtlDays": 540,
        "voltageEventJournalTtlDays": 365,
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["routeCount"] = len(routes)
        pages["growthRun14"] = {"version": 1, "basePath": base_path, "routes": [public_url(base_path, route) for route in ROUTES.values()], "entryPointsInjected": injected, "directAffiliateLinksAdded": 0, "emergencyCommerceClosed": True}
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
    for name, route in [("Uzatma Kablosu", ROUTES["extension"]), ("Acil Aydınlatma Testi", ROUTES["emergency"]), ("Gerilim Olayı", ROUTES["voltage"])]:
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
            raise FileNotFoundError(f"Growth run14 rota veya app eksik: {target}")
    injected = inject_entries(site, base_path)
    append_sitemap(site); append_search(site, base_path); update_release(site, base_path, injected)
    offline_added = add_offline(site, base_path); update_manifest(site, base_path); recompute(site)
    return {"ok": True, "basePath": base_path, "routes": [public_url(base_path, route) for route in ROUTES.values()], "entryPointsInjected": injected, "offlineAdded": offline_added, "directAffiliateLinksAdded": 0, "rawPersonalDataCollected": False, "emergencyCommerceClosed": True}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--site", type=Path, required=True); parser.add_argument("--base-path", default="")
    args = parser.parse_args(); print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
