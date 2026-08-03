from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from inject_affiliate_product_graph import run as run_affiliate_product_graph
from sitemap_routes import ensure_canonical_routes

ROUTES = {
    "ev": "/hesaplama/ev-sarj-kablosu-saglik-gunlugu/",
    "pv": "/hesaplama/ges-panel-temizlik-karar-gunlugu/",
    "ground": "/hesaplama/topraklama-olcum-trend-gunlugu/",
}
SOURCES = {key: f"alo186/{route.strip('/')}/index.html" for key, route in ROUTES.items()}
HUB = Path("hesaplama/index.html")
PORTAL = Path("elektrik-portali/index.html")
PRODUCT = Path("akilli-urun-secimi/index.html")
CORPORATE = Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html")
MARKERS = {
    HUB: 'data-alo186-growth-run15-tools="true"',
    PORTAL: 'data-alo186-growth-run15-safety="true"',
    PRODUCT: 'data-alo186-growth-run15-affiliate="true"',
    CORPORATE: 'data-alo186-growth-run15-service="true"',
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
    ev, pv, ground = (public_url(base_path, ROUTES[key]) for key in ("ev", "pv", "ground"))
    injected = 0
    injected += inject_before_main_end(site / HUB, MARKERS[HUB], f'''<section {MARKERS[HUB]} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#f5f8fd"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Olay kanıtı · bakım kararı · profesyonel trend</span><h2 style="color:#071631">Üç yeni güven ve tekrar ziyaret aracı</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px"><a href="{ev}"><strong>EV şarj kablosu sağlık günlüğü</strong><br>Isınma, kesinti ve fiziksel hasarı araç, wallbox ve kablo arasında ayırın.</a><a href="{pv}"><strong>GES panel temizlik karar günlüğü</strong><br>Takvim yerine karşılaştırılabilir üretim ve görünür kirlenme kanıtı kullanın.</a><a href="{ground}"><strong>Topraklama ölçüm trendi</strong><br>Aynı nokta ve yöntemle yeniden test döngüsü oluşturun.</a></div></section>''')
    injected += inject_before_main_end(site / PORTAL, MARKERS[PORTAL], f'''<section {MARKERS[PORTAL]} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#fff"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Güvenlik ve ölçüm sınırı</span><h2 style="color:#071631">Hasarlı EV bağlantısını ve karşılaştırılamayan topraklama değerini ürünle gizlemeyin</h2><p>EV kablo olayı için kullanımı durdurma kapısı; topraklama için nokta, yöntem, saha koşulu ve profesyonel ölçüm kanıtı oluşturuldu.</p><div style="display:flex;flex-wrap:wrap;gap:12px"><a href="{ev}">EV kablo olayını kaydet →</a><a href="{ground}">Topraklama trendini aç →</a></div></section>''')
    injected += inject_before_main_end(site / PRODUCT, MARKERS[PRODUCT], f'''<section {MARKERS[PRODUCT]} style="max-width:1180px;margin:34px auto;padding:24px;border:1px solid #dfbd57;border-radius:22px;background:#fff9e8"><span style="font-size:.78rem;font-weight:900;color:#785200;text-transform:uppercase;letter-spacing:.06em">Affiliate öncesi arıza ve uyumluluk kapısı</span><h2 style="color:#071631">Type 2 kablo kategorisi yalnız taşınabilir kablo sorunu doğrulanırsa açılır</h2><p><a href="{ev}">EV kablo sağlık günlüğü</a>, fiziksel hasarı ve tekrarlayan olayı çapraz kontrolle ayırır. Sabit wallbox kablosu, su/kir veya belirsiz kök neden ticari rotaya gönderilmez.</p><small>Satış ortaklığı yalnız nitelendirilmiş kategori bağlantısının yanında açıklanır. GES temizlik ve topraklama araçlarında affiliate bulunmaz.</small></section>''')
    injected += inject_before_main_end(site / CORPORATE, MARKERS[CORPORATE], f'''<section class="specialist-services" {MARKERS[CORPORATE]}><div class="specialist-heading"><span class="eyebrow">Tekrarlayan O&amp;M ve ölçüm hizmeti</span><h2>GES kirlenme kaybı ile topraklama ölçüm trendini kanıtlı bakım döngüsüne alın</h2><p>Temizlik öncesi/sonrası normalize performans, güvenli erişim ve aynı yöntemli topraklama yeniden testleri kişisel verisiz ön dosyada düzenlenir. Ücretsiz çıktı, ücretli hizmet veya ekipman zorunluluğu değildir.</p></div><div class="actions"><a href="{pv}">GES temizlik günlüğü</a><a href="{ground}">Topraklama trend günlüğü</a></div></section>''')
    return injected


def append_sitemap(site: Path) -> None:
    ensure_canonical_routes(site / "sitemap.xml", ROUTES.values())


def append_search(site: Path, base_path: str) -> None:
    path = site / "arama/search-index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.setdefault("entries", [])
    known = {item.get("canonicalPath") for item in entries if isinstance(item, dict)}
    metadata = {
        "ev": ("EV Şarj Kablosu Sağlık ve Isınma Günlüğü", "Type 2 kablo ısınması, kesinti, kilit ve fiziksel hasar olaylarını ayırın.", "calculator", ["Type 2 kablo", "EV şarj kablosu ısınıyor", "şarj kesildi", "kablo hasarı"]),
        "pv": ("GES Panel Temizlik Karar ve Sonuç Günlüğü", "PV temizliğini karşılaştırılabilir üretim, kirlenme, yağış ve erişim güvenliğiyle değerlendirin.", "calculator", ["GES panel temizliği", "soiling", "kWh/kWp", "PV bakım"]),
        "ground": ("Topraklama Ölçüm Trend ve Yeniden Test Günlüğü", "Topraklama direnci ve çevrim ölçümlerini aynı nokta, yöntem ve koşulla karşılaştırın.", "business", ["topraklama ölçümü", "kazıksız pens", "kazıklı ölçüm", "yeniden test", "ölçüm trendi"]),
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
            routes.append({"canonicalPath": route, "source": SOURCES[key], "type": "business-tool" if key == "ground" else "calculator"})
    release["routeCount"] = len(routes)
    release["growthRun15"] = {
        "version": 1,
        "routes": list(ROUTES.values()),
        "entryPointsInjected": injected,
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "qualifiedAffiliateFlows": ["ev_cable_after_confirmed_portable_cable_issue"],
        "professionalServiceFlows": ["fixed_evse_cable_service", "pv_soiling_performance_om", "grounding_measurement_verification"],
        "affiliateDisclosureRequired": True,
        "unverifiedCommercialFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "officialApprovalClaimed": False,
        "emergencyCommerceClosed": True,
        "rooftopCommerceClosed": True,
        "professionalMeasurementOnly": True,
        "evCableJournalTtlDays": 540,
        "pvCleaningJournalTtlDays": 730,
        "groundingJournalTtlDays": 1095,
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["routeCount"] = len(routes)
        pages["growthRun15"] = {"version": 1, "basePath": base_path, "routes": [public_url(base_path, route) for route in ROUTES.values()], "entryPointsInjected": injected, "directAffiliateLinksAdded": 0, "emergencyCommerceClosed": True}
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
        path.write_text(text[:match.start(1)] + json.dumps(current, ensure_ascii=False) + text[match.end(1):], encoding="utf-8")
    return added


def update_manifest(site: Path, base_path: str) -> None:
    path = site / "manifest.webmanifest"
    if not path.is_file():
        return
    manifest = json.loads(path.read_text(encoding="utf-8"))
    shortcuts = manifest.setdefault("shortcuts", [])
    for name, route in [("EV Kablo Sağlığı", ROUTES["ev"]), ("GES Temizlik Kararı", ROUTES["pv"]), ("Topraklama Trendi", ROUTES["ground"])]:
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
            raise FileNotFoundError(f"Growth run15 rota veya app eksik: {target}")
    injected = inject_entries(site, base_path)
    append_sitemap(site)
    append_search(site, base_path)
    update_release(site, base_path, injected)
    offline_added = add_offline(site, base_path)
    update_manifest(site, base_path)
    recompute(site)
    product_graph = run_affiliate_product_graph(site, base_path)
    return {
        "ok": True,
        "basePath": base_path,
        "routes": [public_url(base_path, route) for route in ROUTES.values()],
        "entryPointsInjected": injected,
        "offlineAdded": offline_added,
        "directAffiliateLinksAdded": 0,
        "rawPersonalDataCollected": False,
        "emergencyCommerceClosed": True,
        "affiliateProductKnowledgeGraph": product_graph,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
