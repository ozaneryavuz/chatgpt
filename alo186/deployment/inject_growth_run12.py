from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from sitemap_routes import ensure_canonical_routes

ROUTES = {
    "outage": "/hesaplama/elektrik-kesintisi-dayaniklilik-plani/",
    "rcd": "/hesaplama/kacak-akim-rolesi-olay-gunlugu/",
    "pv": "/hesaplama/ges-aylik-uretim-saglik-gunlugu/",
}
SOURCES = {key: f"alo186/{route.strip('/')}/index.html" for key, route in ROUTES.items()}
HUB = Path("hesaplama/index.html")
PORTAL = Path("elektrik-portali/index.html")
PRODUCT = Path("akilli-urun-secimi/index.html")
CORPORATE = Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html")
MARKERS = {
    HUB: 'data-alo186-growth-run12-tools="true"',
    PORTAL: 'data-alo186-growth-run12-journey="true"',
    PRODUCT: 'data-alo186-growth-run12-affiliate="true"',
    CORPORATE: 'data-alo186-growth-run12-service="true"',
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
    outage, rcd, pv = (public_url(base_path, ROUTES[key]) for key in ("outage", "rcd", "pv"))
    injected = 0
    injected += inject_before_main_end(site / HUB, MARKERS[HUB], f'''<section {MARKERS[HUB]} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#f5f8fd"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Dayanıklılık · olay deseni · aylık performans</span><h2 style="color:#071631">Üç yeni güven ve tekrar ziyaret aracı</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px"><a href="{outage}"><strong>Kesinti dayanıklılık planı</strong><br>Mevcut yedekleri koruyun, gerçek boşluk varsa kategoriye ilerleyin.</a><a href="{rcd}"><strong>RCD olay günlüğü</strong><br>Devre, yük, nem ve tekrar desenini ürün yönlendirmeden kaydedin.</a><a href="{pv}"><strong>GES aylık üretim günlüğü</strong><br>kWh/kWp ve karşılaştırılabilir referansla kalıcı düşüşü ayırın.</a></div></section>''')
    injected += inject_before_main_end(site / PORTAL, MARKERS[PORTAL], f'''<section {MARKERS[PORTAL]} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#fff"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Arama niyetinden kanıt döngüsüne</span><h2 style="color:#071631">Kesinti, koruma açması ve üretim kaybını tekrar ölçülebilir hale getirin</h2><p>Tek olay veya tek ay üzerinden ürün satın almayın. İhtiyaç, olay deseni ve karşılaştırılabilir performans kanıtını yerel olarak izleyin.</p><div style="display:flex;flex-wrap:wrap;gap:12px"><a href="{outage}">Kesinti planını oluştur →</a><a href="{rcd}">RCD olayını kaydet →</a><a href="{pv}">GES üretimini izle →</a></div></section>''')
    injected += inject_before_main_end(site / PRODUCT, MARKERS[PRODUCT], f'''<section {MARKERS[PRODUCT]} style="max-width:1180px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#fff9e8"><span style="font-size:.78rem;font-weight:900;color:#785200;text-transform:uppercase;letter-spacing:.06em">Affiliate öncesi dayanıklılık kapısı</span><h2 style="color:#071631">Yedek güç ürünü yalnız doğrulanmış ihtiyaçta gösterilir</h2><p><a href="{outage}">Kesinti dayanıklılık planı</a>, mevcut powerbank, mini UPS, UPS, power station veya jeneratör yeterliyse satın almama sonucu verir. Tıbbi cihaz, yangın ve sabit tesisat risklerinde ticari yol kapalıdır.</p><small>Fiyat, stok, puan, satıcı veya garanti gösterilmez. Satış ortaklığı ilişkisi yalnız kategori yolunun yanında açıklanır.</small></section>''')
    injected += inject_before_main_end(site / CORPORATE, MARKERS[CORPORATE], f'''<section class="specialist-services" {MARKERS[CORPORATE]}><div class="specialist-heading"><span class="eyebrow">Tekrarlayan teknik kanıt</span><h2>Tek olay yerine RCD deseni ve GES aylık performans geçmişiyle ilerleyin</h2><p>Ücretsiz yerel günlükler, ücretli inceleme öncesinde devre/olay ve üretim/referans kanıtını hazırlar. Tek kayıt hizmet veya ekipman zorunluluğu değildir.</p></div><div class="actions"><a href="{rcd}">RCD olay günlüğünü aç</a><a href="{pv}">GES aylık günlüğünü aç</a></div></section>''')
    return injected


def append_sitemap(site: Path) -> None:
    ensure_canonical_routes(site / "sitemap.xml", ROUTES.values())


def append_search(site: Path, base_path: str) -> None:
    path = site / "arama/search-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.setdefault("entries", [])
    known = {item.get("canonicalPath") for item in entries if isinstance(item, dict)}
    metadata = {
        "outage": ("Elektrik Kesintisi Dayanıklılık Planı", "Kritik ihtiyaç, kesinti süresi, mevcut yedek ve güvenli affiliate kapısı."),
        "rcd": ("Kaçak Akım Rölesi Olay Günlüğü", "Devre, yük, nem, reset ve tekrar eden RCD açma deseni."),
        "pv": ("GES Aylık Üretim Sağlık Günlüğü", "Aylık AC üretim, kWh/kWp, model/geçmiş referansı ve veri tamlığı."),
    }
    for key, route in ROUTES.items():
        if route in known:
            continue
        title, description = metadata[key]
        entries.append({"canonicalPath": route, "url": public_url(base_path, route), "title": title, "description": description, "bucket": "business" if key == "pv" else "calculator", "keywords": [key, "yerel günlük", "satın almama", "elektrik güvenliği"]})
    data["entryCount"] = len(entries)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, injected: int) -> None:
    path = site / "alo186-release.json"
    release = json.loads(path.read_text(encoding="utf-8"))
    routes = release.setdefault("routes", [])
    known = {item.get("canonicalPath") for item in routes if isinstance(item, dict)}
    for key, route in ROUTES.items():
        if route not in known:
            routes.append({"canonicalPath": route, "source": SOURCES[key], "type": "business-tool" if key == "pv" else "calculator"})
    release["routeCount"] = len(routes)
    release["growthRun12"] = {
        "version": 1,
        "routes": list(ROUTES.values()),
        "entryPointsInjected": injected,
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "qualifiedAffiliateFlows": ["mini_ups", "portable_power_station"],
        "professionalServiceFlows": ["rcd_diagnostics", "pv_performance", "medical_continuity"],
        "affiliateDisclosureRequired": True,
        "unverifiedCommercialFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "officialApprovalClaimed": False,
        "emergencyCommerceClosed": True,
        "localOnlyJournals": ["rcd", "pv"],
        "rcdJournalTtlDays": 365,
        "pvJournalTtlDays": 730,
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["routeCount"] = len(routes)
        pages["growthRun12"] = {"version": 1, "basePath": base_path, "routes": [public_url(base_path, route) for route in ROUTES.values()], "entryPointsInjected": injected, "directAffiliateLinksAdded": 0, "emergencyCommerceClosed": True}
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
    for name, route in [("Kesinti Dayanıklılık Planı", ROUTES["outage"]), ("RCD Olay Günlüğü", ROUTES["rcd"]), ("GES Aylık Sağlık", ROUTES["pv"])]:
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
            raise FileNotFoundError(f"Growth run12 rota veya app eksik: {target}")
    injected = inject_entries(site, base_path)
    append_sitemap(site); append_search(site, base_path); update_release(site, base_path, injected)
    offline_added = add_offline(site, base_path); update_manifest(site, base_path); recompute(site)
    return {"ok": True, "basePath": base_path, "routes": [public_url(base_path, route) for route in ROUTES.values()], "entryPointsInjected": injected, "offlineAdded": offline_added, "directAffiliateLinksAdded": 0, "rawPersonalDataCollected": False, "emergencyCommerceClosed": True}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--site", type=Path, required=True); parser.add_argument("--base-path", default="")
    args = parser.parse_args(); print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
