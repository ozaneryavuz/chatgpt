from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROUTE = "/hesaplama/usb-c-guc-ve-goruntu-karar-merkezi/"
SOURCE = "alo186/hesaplama/usb-c-guc-ve-goruntu-karar-merkezi/index.html"
CANONICAL = f"https://www.alo186.com{ROUTE}"
ENTRY_MARKER = 'data-alo186-growth-run20-entry="true"'
TARGETS = {
    Path("hesaplama/index.html"): (
        "USB-C güç, hub ve görüntü zincirini tek yerde ayırın",
        "Adaptör, kablo, hub, kaynak portu ve ekran arasındaki gerçek darboğazı bulun; mevcut set yeterliyse satın almayın.",
    ),
    Path("elektrik-portali/index.html"): (
        "Aynı USB-C fişi aynı güç, veri ve görüntü yeteneği değildir",
        "Güç zinciri, DisplayPort Alt Mode ve bağlantı pasaportunu kişisel veri paylaşmadan değerlendirin.",
    ),
    Path("akilli-urun-secimi/index.html"): (
        "Affiliate kategori yalnız doğrulanmış bileşen açığında görünür",
        "Şarj cihazı, kablo, hub ve görüntü kablosunu set halinde değil, yalnız darboğaz oluşturan bileşen üzerinden değerlendirin.",
    ),
    Path("amazon-elektrik-urunleri/index.html"): (
        "USB-C alışveriş niyetini teknik zincirle nitelendirin",
        "Watt etiketi, kablo sınıfı veya hub port sayısı tek başına uyumluluk oluşturmaz; önce ücretsiz karar merkezini kullanın.",
    ),
    Path("katalog-guven-durumu/index.html"): (
        "USB-C ürün düğümlerini gerçek kullanım zincirine bağlayın",
        "Knowledge Graph ürün kayıtlarını güç, görüntü ve bağlantı pasaportu sonuçlarıyla birlikte değerlendirin.",
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
    if f"<loc>{CANONICAL}</loc>" not in text:
        text = text.replace("</urlset>", f"<url><loc>{CANONICAL}</loc></url></urlset>", 1)
    path.write_text(text, encoding="utf-8")


def append_search(site: Path, base_path: str) -> None:
    path = site / "arama/search-index.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.setdefault("entries", [])
    if not any(item.get("canonicalPath") == ROUTE for item in entries if isinstance(item, dict)):
        entries.append({
            "canonicalPath": ROUTE,
            "url": public_url(base_path, ROUTE),
            "title": "USB-C Güç, Kablo, Hub ve Görüntü Uygunluk Merkezi",
            "description": "USB-C güç zincirindeki darboğazı, hub görüntü sorununu ve masaüstü bağlantı boşluklarını kişisel veri toplamadan değerlendirin.",
            "bucket": "calculator",
            "keywords": [
                "USB-C şarj yavaş", "100W kablo", "USB-C hub görüntü vermiyor", "DisplayPort Alt Mode",
                "USB-C dock seçimi", "USB-C hub HDMI çalışmıyor", "masaüstü bağlantı pasaportu"
            ],
        })
    payload["entryCount"] = len(entries)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def insert_entries(site: Path, base_path: str) -> int:
    href = public_url(base_path, ROUTE)
    count = 0
    for relative, (title, body) in TARGETS.items():
        path = site / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if ENTRY_MARKER in text or "</main>" not in text:
            continue
        section = f'''<section {ENTRY_MARKER} style="max-width:1160px;margin:30px auto;padding:24px;border:1px solid #d9e3ef;border-radius:22px;background:#f4f8fd"><span style="font-size:.76rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.07em">USB-C güç zinciri · görüntü teşhisi · 365 günlük pasaport</span><h2 style="color:#071631">{title}</h2><p>{body}</p><a href="{href}" style="display:inline-flex;min-height:44px;align-items:center;font-weight:900;color:#174bb9">USB-C karar merkezini aç →</a><small style="display:block;margin-top:12px;color:#58677c">Doğrudan mağaza bağlantısı yoktur. Teknik eksik, mevcut ürün yetersizliği ve satış ortaklığı açıklaması birlikte doğrulanmadan kategori yolu açılmaz.</small></section>'''
        path.write_text(text.replace("</main>", section + "</main>", 1), encoding="utf-8")
        count += 1
    return count


def add_offline(site: Path, base_path: str) -> bool:
    path = site / "sw.js"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        raise RuntimeError("Service worker CRITICAL rota dizisi bulunamadı")
    routes = json.loads(match.group(1))
    url = public_url(base_path, ROUTE)
    if url in routes:
        return False
    routes.append(url)
    path.write_text(text[: match.start(1)] + json.dumps(routes, ensure_ascii=False) + text[match.end(1) :], encoding="utf-8")
    return True


def update_manifest(site: Path, base_path: str) -> None:
    path = site / "manifest.webmanifest"
    if not path.is_file():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    shortcuts = payload.setdefault("shortcuts", [])
    url = public_url(base_path, ROUTE)
    if not any(isinstance(item, dict) and item.get("url") == url for item in shortcuts):
        shortcuts.append({"name": "USB-C Güç ve Görüntü Kararı", "short_name": "USB-C Kararı", "url": url})
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, cards: int, offline_added: bool) -> None:
    metadata = {
        "version": 1,
        "route": public_url(base_path, ROUTE),
        "entryPointsInjected": cards,
        "offline": True,
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "affiliateCategories": ["usb_c_charger", "usb_c_cable", "usb_c_hub", "usb_c_display_cable"],
        "qualifiedAffiliateFlows": ["power_chain_component_gap", "display_path_component_gap", "desktop_passport_component_gap"],
        "hazardCommerceClosed": True,
        "unknownCapabilityCommerceClosed": True,
        "noBuyOutcomePreserved": True,
        "officialApprovalClaimed": False,
        "unverifiedCommercialFieldsUsed": [],
        "passportRecordLimit": 6,
        "passportTtlDays": 365,
        "passportReviewDays": 180,
    }
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    routes = core.setdefault("routes", [])
    if not any(item.get("canonicalPath") == ROUTE for item in routes if isinstance(item, dict)):
        routes.append({"canonicalPath": ROUTE, "source": SOURCE, "type": "calculator"})
    core["routeCount"] = len(routes)
    core["growthRun20"] = metadata
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["routeCount"] = len(routes)
        pages["growthRun20"] = metadata
        if offline_added:
            pages["offlineCriticalRouteCount"] = int(pages.get("offlineCriticalRouteCount") or 0) + 1
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    files = sorted(item for item in site.rglob("*") if item.is_file())
    path.write_text("\n".join(f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}" for item in files) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    target = site / ROUTE.strip("/") / "index.html"
    if not target.is_file():
        raise FileNotFoundError(f"Growth run20 rota eksik: {target}")
    append_sitemap(site)
    append_search(site, base_path)
    cards = insert_entries(site, base_path)
    offline_added = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_release(site, base_path, cards, offline_added)
    recompute(site)
    return {
        "ok": True,
        "basePath": base_path,
        "route": public_url(base_path, ROUTE),
        "entryPointsInjected": cards,
        "offlineAdded": offline_added,
        "directAffiliateLinksAdded": 0,
        "rawPersonalDataCollected": False,
        "threeActions": ["power_chain", "display_diagnosis", "desktop_passport"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
