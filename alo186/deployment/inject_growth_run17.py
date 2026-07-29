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
TARGETS = {
    Path("hesaplama/index.html"): 'data-alo186-growth-run17-tools="true"',
    Path("elektrik-portali/index.html"): 'data-alo186-growth-run17-evidence="true"',
    Path("akilli-urun-secimi/index.html"): 'data-alo186-growth-run17-trust="true"',
    Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html"): 'data-alo186-growth-run17-service="true"',
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
    blocks = {
        Path("hesaplama/index.html"): f'''<section {TARGETS[Path("hesaplama/index.html")]} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#f5f8fd"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Priz güvenliği · gerçek süre · doğru kanıt kapsamı</span><h2 style="color:#071631">Üç yüksek niyetli kullanıcı yolculuğu</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px"><a href="{mode2}"><strong>Mode 2 EV şarj ve priz uygunluğu</strong><br>Üründen önce priz, PE, devre ve sıcaklık sınırını doğrulayın.</a><a href="{mini}"><strong>Mini UPS gerçek süre sağlığı</strong><br>Affiliate yolunu yalnız iki karşılaştırılabilir başarısız testten sonra değerlendirin.</a><a href="{voltage}"><strong>Gerilim monitörü kanıt kapsamı</strong><br>Tek priz gözlemi ile resmî ve profesyonel ölçümü ayırın.</a></div></section>''',
        Path("elektrik-portali/index.html"): f'''<section {TARGETS[Path("elektrik-portali/index.html")]} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#fff"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Güvenli karar ve kanıt</span><h2 style="color:#071631">Yeni cihaz almak yerine önce kök nedeni ve kanıt amacını belirleyin</h2><p>Mode 2 EV şarjında tesis kabulü, mini UPS'te tekrarlanan gerçek süre kaybı ve gerilim olayında ölçüm kapsamı birbirinden ayrılır.</p><div style="display:flex;flex-wrap:wrap;gap:12px"><a href="{mode2}">EV priz güvenliğini aç →</a><a href="{mini}">Mini UPS test döngüsü →</a><a href="{voltage}">Gerilim kanıt yolu →</a></div></section>''',
        Path("akilli-urun-secimi/index.html"): f'''<section {TARGETS[Path("akilli-urun-secimi/index.html")]} style="max-width:1180px;margin:34px auto;padding:24px;border:1px solid #dfbd57;border-radius:22px;background:#fff9e8"><span style="font-size:.78rem;font-weight:900;color:#785200;text-transform:uppercase;letter-spacing:.06em">Affiliate öncesi güven kapıları</span><h2 style="color:#071631">Mode 2 ve gerilim monitörü satışa açılmaz; mini UPS iki test ister</h2><p><a href="{mode2}">Mode 2 aracı</a> güvenlik ve tesis kanıtı tamamlanmadan mağaza yönlendirmesi göstermez. <a href="{voltage}">Gerilim monitörü aracı</a> resmî ölçüm izlenimi yaratmaz. <a href="{mini}">Mini UPS günlüğü</a> yalnız aynı yük/hedefle iki karşılaştırılabilir başarısız testten sonra açıklamalı kategori yolunu açabilir.</p><small>Fiyat, stok, puan, satıcı veya garanti yayımlanmaz; mevcut çözüm yeterliyse satın almama sonucu korunur.</small></section>''',
        Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html"): f'''<section class="specialist-services" {TARGETS[Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html")]}><div class="specialist-heading"><span class="eyebrow">Bağımsız teknik dönüşüm</span><h2>EV priz kabulü ve güç kalitesi kaydını satıştan ayrı yönetin</h2><p>Günlük/yüksek akımlı Mode 2 kullanımında devre, termal ve koruma kabulü; bina/üç faz/harmonik olaylarında ise dağıtım şirketi sürecinden ayrı bağımsız ölçüm kapsamı oluşturulur. Ücretsiz araç çıktısı ücretli hizmet zorunluluğu değildir.</p></div><div class="actions"><a href="{mode2}">EV priz ön dosyası</a><a href="{voltage}">Gerilim kapsam ön dosyası</a></div></section>''',
    }
    return sum(inject_before_main_end(site / path, TARGETS[path], block) for path, block in blocks.items())


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
        "mode2": ("Taşınabilir EV Şarj Cihazı ve Priz Uygunluk Günlüğü", "Mode 2 IC-CPD kullanımını priz, PE, devre, koruma ve sıcaklık kanıtıyla değerlendirin.", ["Mode 2", "IC-CPD", "taşınabilir EV şarj", "priz ısınıyor", "EV priz kabulü"]),
        "mini": ("Modem ve ONT Mini UPS Gerçek Süre Sağlık Günlüğü", "Mini UPS gerçek çalışma süresini aynı yük, hedef, tam şarj ve iki karşılaştırılabilir testle izleyin.", ["mini UPS süre testi", "modem UPS kaç saat", "ONT yedekleme", "mini UPS batarya sağlığı"]),
        "voltage": ("Priz Tipi Gerilim Monitörü Uygunluk ve 7 Günlük Kanıt Günlüğü", "Tek priz ön gözlemini dağıtım şirketi teknik kalite ve profesyonel güç kalitesi kaydından ayırın.", ["priz tipi voltmetre", "gerilim monitörü", "7 günlük gerilim", "EDAŞ ölçüm", "güç kalitesi logger"]),
    }
    for key, route in ROUTES.items():
        if route in known:
            continue
        title, description, keywords = metadata[key]
        entries.append({"canonicalPath": route, "url": public_url(base_path, route), "title": title, "description": description, "bucket": "calculator", "keywords": keywords})
    data["entryCount"] = len(entries)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, injected: int) -> None:
    path = site / "alo186-release.json"
    release = json.loads(path.read_text(encoding="utf-8"))
    routes = release.setdefault("routes", [])
    known = {item.get("canonicalPath") for item in routes if isinstance(item, dict)}
    for key, route in ROUTES.items():
        if route not in known:
            routes.append({"canonicalPath": route, "source": SOURCES[key], "type": "calculator"})
    release["routeCount"] = len(routes)
    release["growthRun17"] = {
        "version": 1,
        "routes": list(ROUTES.values()),
        "entryPointsInjected": injected,
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "qualifiedAffiliateFlows": ["mini_ups_after_two_comparable_failed_tests"],
        "professionalServiceFlows": ["mode2_ev_outlet_and_circuit_acceptance", "building_and_power_quality_logging_separate_from_official_process"],
        "affiliateDisclosureRequired": True,
        "unverifiedCommercialFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "officialApprovalClaimed": False,
        "officialInstitutionImpressionPrevented": True,
        "emergencyCommerceClosed": True,
        "mode2CommerceClosed": True,
        "voltageMonitorCommerceClosed": True,
        "miniUpsRepeatedComparableFailureRequired": True,
        "mode2JournalTtlDays": 540,
        "miniUpsJournalTtlDays": 730,
        "voltageMonitorJournalTtlDays": 365,
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["routeCount"] = len(routes)
        pages["growthRun17"] = {
            "version": 1,
            "basePath": base_path,
            "routes": [public_url(base_path, route) for route in ROUTES.values()],
            "entryPointsInjected": injected,
            "directAffiliateLinksAdded": 0,
            "mode2CommerceClosed": True,
            "voltageMonitorCommerceClosed": True,
            "miniUpsRepeatedComparableFailureRequired": True,
        }
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_offline(site: Path, base_path: str) -> int:
    path = site / "sw.js"
    if not path.is_file():
        return 0
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
    for name, route in [("Mode 2 Priz Güvenliği", ROUTES["mode2"]), ("Mini UPS Süre Sağlığı", ROUTES["mini"]), ("Gerilim Kanıt Kapsamı", ROUTES["voltage"])]:
        url = public_url(base_path, route)
        if not any(isinstance(item, dict) and item.get("url") == url for item in shortcuts):
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
        if not target.is_file() or not target.with_name("app.js").is_file():
            raise FileNotFoundError(f"Growth run17 rota veya app eksik: {target}")
    injected = inject_entries(site, base_path)
    append_sitemap(site)
    append_search(site, base_path)
    update_release(site, base_path, injected)
    offline_added = add_offline(site, base_path)
    update_manifest(site, base_path)
    recompute(site)
    return {
        "ok": True,
        "basePath": base_path,
        "routes": [public_url(base_path, route) for route in ROUTES.values()],
        "entryPointsInjected": injected,
        "offlineAdded": offline_added,
        "directAffiliateLinksAdded": 0,
        "rawPersonalDataCollected": False,
        "officialApprovalClaimed": False,
        "mode2CommerceClosed": True,
        "voltageMonitorCommerceClosed": True,
        "miniUpsRepeatedComparableFailureRequired": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 güven ve gelir büyümesi run17 yayın katmanı")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
