from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROUTES = {
    "movein": "/hesaplama/yeni-ev-elektrik-guvenligi-devir-kontrolu/",
    "restart": "/hesaplama/kesinti-sonrasi-guvenli-yeniden-baslatma-plani/",
    "baseload": "/hesaplama/gece-baz-yuk-standby-tuketim-deneyi/",
}
SOURCES = {key: f"alo186/{route.strip('/')}/index.html" for key, route in ROUTES.items()}
CANONICALS = {key: f"https://www.alo186.com{route}" for key, route in ROUTES.items()}
ENTRY_MARKER = 'data-alo186-growth-run19-entry="true"'
TARGETS = {
    Path("hesaplama/index.html"): (
        "Taşınma, kesinti sonrası yeniden başlatma ve gece baz yükü",
        "Yeni konutta görünür elektrik riskini sınıflandırın, kesinti sonrası yük sırasını hazırlayın ve gece sayaç farkından kendi baz yük geçmişinizi oluşturun.",
    ),
    Path("elektrik-portali/index.html"): (
        "Ürün almadan önce tesisat, olay ve tüketim kanıtı",
        "Sabit tesisat sorununu taşınabilir ürünle kapatmayın; kesinti sonrası güvenli sırayı ve tekrarlanan gece baz yük artışını ayrı değerlendirin.",
    ),
    Path("akilli-urun-secimi/index.html"): (
        "Affiliate kategorisi yalnız gerçek ve tekrarlanan ihtiyatta açılır",
        "Yeni evde tehlike/sabit tesisat sorunu, kesinti sonrası ilk belirsizlik ve tek yüksek gece ölçümü ticari sonuç üretmez.",
    ),
    Path("amazon-elektrik-urunleri/index.html"): (
        "Satın alma niyetini güvenlik ve kendi ölçüm geçmişinizle nitelendirin",
        "Düşük riskli kategori rehberi yalnız sabit tesisat kapısı temiz, mevcut çözüm yetersiz ve ihtiyaç tekrarlanan kanıtla doğrulanmışsa açılır.",
    ),
    Path("kesintiye-hazirlik-atolyesi/index.html"): (
        "Kesinti kiti kadar yeniden başlatma sırası da önemlidir",
        "Elektrik geri geldiğinde kritik haberleşme, soğutma, IT ve motorlu yükleri aynı anda değil, güvenli fazlarla devreye alın.",
    ),
    Path("fatura-analizi/index.html"): (
        "Aylık kWh artışını gece baz yük deneyiyle ayırın",
        "Tarife ve fatura tutarı yerine sayaç farkından ortalama wattı hesaplayın; yalnız aynı koşuldaki tekrarlanan artışı inceleyin.",
    ),
}


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def append_sitemap(site: Path) -> None:
    path = site / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    for canonical in CANONICALS.values():
        if f"<loc>{canonical}</loc>" not in text:
            text = text.replace("</urlset>", f"<url><loc>{canonical}</loc></url></urlset>", 1)
    path.write_text(text, encoding="utf-8")


def append_search(site: Path, base_path: str) -> None:
    path = site / "arama/search-index.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.setdefault("entries", [])
    known = {item.get("canonicalPath") for item in entries if isinstance(item, dict)}
    metadata = {
        "movein": {
            "title": "Yeni Ev ve Kiralık Konut Elektrik Güvenliği Devir Kontrolü",
            "description": "Pano, RCD, priz, uzatma kablosu, büyük cihaz ve alarm bulgularını sınıflandırın; sabit tesisat sorununda ürün yolunu kapatın.",
            "bucket": "calculator",
            "keywords": ["yeni ev elektrik kontrolü", "kiralık ev elektrik güvenliği", "taşınma elektrik kontrol listesi", "RCD priz pano"],
        },
        "restart": {
            "title": "Elektrik Kesintisi Sonrası Güvenli Yeniden Başlatma Planı",
            "description": "Modem, buzdolabı, kombi, IT, motor, klima ve EV şarj yüklerini güvenli yeniden başlatma fazlarına ayırın.",
            "bucket": "calculator",
            "keywords": ["elektrik kesintisi sonrası cihazları açma", "yeniden enerjilendirme sırası", "cold start", "UPS jeneratör yük sırası"],
        },
        "baseload": {
            "title": "Gece Baz Yük ve Standby Tüketim Deneyi",
            "description": "Sayaç başlangıç ve bitiş kWh değerlerinden gece ortalama wattı hesaplayın ve yalnız aynı koşuldaki kendi geçmişinizle karşılaştırın.",
            "bucket": "calculator",
            "keywords": ["gece elektrik tüketimi", "baz yük", "standby tüketim", "sayaçtan watt hesaplama", "hayalet tüketim"],
        },
    }
    for key, route in ROUTES.items():
        if route in known:
            continue
        item = metadata[key]
        entries.append({
            "canonicalPath": route,
            "url": public_url(base_path, route),
            "title": item["title"],
            "description": item["description"],
            "bucket": item["bucket"],
            "keywords": item["keywords"],
        })
    payload["entryCount"] = len(entries)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def insert_entries(site: Path, base_path: str) -> int:
    movein = public_url(base_path, ROUTES["movein"])
    restart = public_url(base_path, ROUTES["restart"])
    baseload = public_url(base_path, ROUTES["baseload"])
    count = 0
    for relative, (title, body) in TARGETS.items():
        path = site / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if ENTRY_MARKER in text or "</main>" not in text:
            continue
        section = f'''<section {ENTRY_MARKER} style="max-width:1160px;margin:30px auto;padding:24px;border:1px solid #d9e3ef;border-radius:22px;background:#f4f8fd"><span style="font-size:.76rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.07em">Taşınma · yeniden başlatma · kendi bazınız</span><h2 style="color:#071631">{title}</h2><p>{body}</p><div style="display:flex;flex-wrap:wrap;gap:12px"><a href="{movein}" style="font-weight:850;color:#174bb9">Yeni ev devir kontrolü →</a><a href="{restart}" style="font-weight:850;color:#174bb9">Kesinti sonrası plan →</a><a href="{baseload}" style="font-weight:850;color:#174bb9">Gece baz yük deneyi →</a></div><small style="display:block;margin-top:12px;color:#58677c">Tehlike ve sabit tesisat sorunu ticari yolu kapatır. Tek olay veya tek yüksek ölçüm yeni ürün kararı değildir. Affiliate ilişkisi yalnız nitelikli kategori rehberinin yanında açıklanır.</small></section>'''
        path.write_text(text.replace("</main>", section + "</main>", 1), encoding="utf-8")
        count += 1
    return count


def add_offline(site: Path, base_path: str) -> list[str]:
    path = site / "sw.js"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        raise RuntimeError("Service worker CRITICAL rota dizisi bulunamadı")
    current = json.loads(match.group(1))
    added: list[str] = []
    for route in ROUTES.values():
        url = public_url(base_path, route)
        if url not in current:
            current.append(url)
            added.append(url)
    if added:
        path.write_text(text[: match.start(1)] + json.dumps(current, ensure_ascii=False) + text[match.end(1) :], encoding="utf-8")
    return added


def update_manifest(site: Path, base_path: str) -> None:
    path = site / "manifest.webmanifest"
    if not path.is_file():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    shortcuts = payload.setdefault("shortcuts", [])
    candidates = [
        ("Yeni Ev Elektrik Kontrolü", "Ev Devir Kontrolü", ROUTES["movein"]),
        ("Kesinti Sonrası Başlatma", "Yeniden Başlatma", ROUTES["restart"]),
        ("Gece Baz Yük Deneyi", "Baz Yük", ROUTES["baseload"]),
    ]
    for name, short_name, route in candidates:
        url = public_url(base_path, route)
        if not any(isinstance(item, dict) and item.get("url") == url for item in shortcuts):
            shortcuts.append({"name": name, "short_name": short_name, "url": url})
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, cards: int, offline: list[str]) -> None:
    metadata = {
        "version": 1,
        "routes": [public_url(base_path, route) for route in ROUTES.values()],
        "entryPointsInjected": cards,
        "offlineRoutesAdded": offline,
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "qualifiedAffiliateFlows": [
            "move_in_low_risk_categories_after_fixed_wiring_clear",
            "restart_repeated_outage_after_existing_readiness_gap",
            "night_baseload_after_two_repeated_comparable_increases",
        ],
        "professionalServiceFlows": [
            "fixed_wiring_move_in_review",
            "business_restart_and_continuity_review",
            "fixed_or_motor_load_energy_measurement",
        ],
        "hazardCommerceClosed": True,
        "fixedWiringCommerceClosed": True,
        "singleEventCommerceClosed": True,
        "singleHighMeasurementCommerceClosed": True,
        "noBuyOutcomePreserved": True,
        "officialApprovalClaimed": False,
        "unverifiedCommercialFieldsUsed": [],
        "moveInReceiptTtlDays": 365,
        "restartPlanTtlDays": 365,
        "nightBaseloadRecordTtlDays": 540,
        "nightBaseloadRecordLimit": 12,
        "restartDrillDays": 90,
        "baseloadReviewDays": 30,
    }
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    routes = core.setdefault("routes", [])
    known = {item.get("canonicalPath") for item in routes if isinstance(item, dict)}
    for key, route in ROUTES.items():
        if route not in known:
            routes.append({"canonicalPath": route, "source": SOURCES[key], "type": "calculator"})
    core["routeCount"] = len(routes)
    core["growthRun19"] = metadata
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["routeCount"] = len(routes)
        pages["growthRun19"] = metadata
        pages["offlineCriticalRouteCount"] = int(pages.get("offlineCriticalRouteCount") or 0) + len(offline)
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    files = sorted(item for item in site.rglob("*") if item.is_file())
    lines = [f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}" for item in files]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    for key, route in ROUTES.items():
        target = site / route.strip("/") / "index.html"
        if not target.is_file():
            raise FileNotFoundError(f"Growth run19 rota eksik: {key} {target}")
    append_sitemap(site)
    append_search(site, base_path)
    cards = insert_entries(site, base_path)
    offline = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_release(site, base_path, cards, offline)
    recompute(site)
    return {
        "ok": True,
        "basePath": base_path,
        "routes": [public_url(base_path, route) for route in ROUTES.values()],
        "entryPointsInjected": cards,
        "offlineRoutesAdded": offline,
        "directAffiliateLinksAdded": 0,
        "hazardCommerceClosed": True,
        "fixedWiringCommerceClosed": True,
        "singleEventCommerceClosed": True,
        "singleHighMeasurementCommerceClosed": True,
        "noBuyOutcomePreserved": True,
        "unverifiedCommercialFieldsUsed": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 taşınma güvenliği, kesinti sonrası yeniden başlatma ve gece baz yük akışlarını yayınlar.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
