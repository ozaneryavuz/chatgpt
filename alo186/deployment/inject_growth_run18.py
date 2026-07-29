from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROUTES = {
    "safety": "/hesaplama/urun-guvenlik-duyurusu-kontrolu/",
    "passport": "/hesaplama/urun-teknik-belge-pasaportu/",
    "kit": "/hesaplama/kesinti-kiti-donemsel-kontrolu/",
}
SOURCES = {key: f"alo186/{route.strip('/')}/index.html" for key, route in ROUTES.items()}
CANONICALS = {key: f"https://www.alo186.com{route}" for key, route in ROUTES.items()}
ENTRY_MARKER = 'data-alo186-growth-run18-entry="true"'
TARGETS = {
    Path("hesaplama/index.html"): (
        "Üç yeni güven ve tekrar kontrol aracı",
        "Ürün güvenlik duyurusu, teknik belge pasaportu ve mevcut kesinti kiti denetimini kişisel veri vermeden tamamlayın.",
    ),
    Path("elektrik-portali/index.html"): (
        "Satın alma öncesi ve sonrası güven döngüsü",
        "Resmî güvenlik duyurusunu kontrol edin, teknik belge boşluklarını kapatın ve mevcut kesinti kitini 90 günde bir yeniden test edin.",
    ),
    Path("akilli-urun-secimi/index.html"): (
        "Affiliate bağlantısından önce belge ve gerçek ihtiyaç",
        "Tam model, üretici kılavuzu, mevcut ürün yeterliliği ve tekrarlayan başarısızlık doğrulanmadan kategori rotasını açmayın.",
    ),
    Path("amazon-elektrik-urunleri/index.html"): (
        "Ürün seçimi satıştan sonra da devam eder",
        "Güvenlik duyurusu ve dönemsel test sonuçları, gereksiz yeniden satın almayı ve riskli ürünü alışveriş akışına göndermeyi önler.",
    ),
    Path("hesaplama/urun-sonrasi-guvenlik-kontrolu/index.html"): (
        "Tek ürün kontrolünü resmî kaynak ve kit döngüsüyle tamamlayın",
        "GÜBİS/Safety Gate araması, teknik belge pasaportu ve 90 günlük kit denetimiyle sonraki adımı kanıtlayın.",
    ),
    Path("kesintiye-hazirlik-atolyesi/index.html"): (
        "Hazırlık planınızı 90 günde bir doğrulayın",
        "Yeni ürün listesi oluşturmak yerine mevcut kitin gerçekten çalıştığını test edin; yeterliyse satın almayın.",
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
        "safety": {
            "title": "Elektrikli Ürün Güvenlik Duyurusu ve Geri Çağırma Kontrolü",
            "description": "Marka ve tam modeli GÜBİS, Safety Gate ve üretici kaynaklarında kontrol etmek için kişisel verisiz yeniden kontrol planı oluşturun.",
            "bucket": "calculator",
            "keywords": ["GÜBİS", "güvensiz ürün", "geri çağırma", "ürün güvenlik duyurusu", "marka model seri"],
        },
        "passport": {
            "title": "Elektrik Ürünü Teknik Belge Pasaportu",
            "description": "Tam model, üretici kılavuzu, elektriksel sınır, uyumluluk, güvenlik ve servis kanıtını affiliate rotasından önce kontrol edin.",
            "bucket": "calculator",
            "keywords": ["ürün teknik belge", "üretici veri sayfası", "affiliate öncesi kontrol", "tam model", "satın almama"],
        },
        "kit": {
            "title": "Elektrik Kesintisi Kiti 90 Günlük Kontrolü",
            "description": "Powerbank, mini UPS, acil aydınlatma, alarm, kablo ve güç istasyonunu dönemsel test edin; ilk başarısızlık ile gerçek değişim ihtiyacını ayırın.",
            "bucket": "calculator",
            "keywords": ["elektrik kesintisi kiti", "90 günlük test", "powerbank kontrol", "mini UPS runtime", "acil aydınlatma testi"],
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
    safety = public_url(base_path, ROUTES["safety"])
    passport = public_url(base_path, ROUTES["passport"])
    kit = public_url(base_path, ROUTES["kit"])
    count = 0
    for relative, (title, body) in TARGETS.items():
        path = site / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if ENTRY_MARKER in text or "</main>" not in text:
            continue
        section = f'''<section {ENTRY_MARKER} style="max-width:1160px;margin:30px auto;padding:24px;border:1px solid #d9e3ef;border-radius:22px;background:#f4f8fd"><span style="font-size:.76rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.07em">Güven · belge · tekrar ziyaret</span><h2 style="color:#071631">{title}</h2><p>{body}</p><div style="display:flex;flex-wrap:wrap;gap:12px"><a href="{safety}" style="font-weight:850;color:#174bb9">Güvenlik duyurusu kontrolü →</a><a href="{passport}" style="font-weight:850;color:#174bb9">Teknik belge pasaportu →</a><a href="{kit}" style="font-weight:850;color:#174bb9">90 günlük kit denetimi →</a></div><small style="display:block;margin-top:12px;color:#58677c">Tehlike durumunda ticari yol kapanır. İlk başarısız test yeni ürün kararı değildir. Affiliate ilişkisi yalnız nitelikli kategori rehberinin yanında açıklanır.</small></section>'''
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
        ("Ürün Güvenlik Kontrolü", "GÜBİS Kontrol", ROUTES["safety"]),
        ("Ürün Belge Pasaportu", "Belge Pasaportu", ROUTES["passport"]),
        ("Kesinti Kiti 90 Gün", "Kit Kontrolü", ROUTES["kit"]),
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
            "technical_evidence_passport_after_all_gates",
            "outage_kit_after_repeated_comparable_failure",
        ],
        "officialSafetySources": ["GÜBİS", "EU Safety Gate", "manufacturer official source"],
        "hazardCommerceClosed": True,
        "firstFailureCommerceClosed": True,
        "noBuyOutcomePreserved": True,
        "officialApprovalClaimed": False,
        "unverifiedCommercialFieldsUsed": [],
        "productSafetyWatchTtlDays": 365,
        "evidencePassportTtlDays": 30,
        "outageKitRecordTtlDays": 730,
        "outageKitReviewDays": 90,
    }
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    routes = core.setdefault("routes", [])
    known = {item.get("canonicalPath") for item in routes if isinstance(item, dict)}
    for key, route in ROUTES.items():
        if route not in known:
            routes.append({"canonicalPath": route, "source": SOURCES[key], "type": "calculator"})
    core["routeCount"] = len(routes)
    core["growthRun18"] = metadata
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["routeCount"] = len(routes)
        pages["growthRun18"] = metadata
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
            raise FileNotFoundError(f"Growth run18 rota eksik: {key} {target}")
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
        "firstFailureCommerceClosed": True,
        "noBuyOutcomePreserved": True,
        "unverifiedCommercialFieldsUsed": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 ürün güvenliği, belge ve kesinti kiti tekrar ziyaret akışlarını yayınlar.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
