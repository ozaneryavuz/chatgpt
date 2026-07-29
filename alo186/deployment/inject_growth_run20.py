from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROUTES = {
    "chain": "/hesaplama/usb-c-sarj-zinciri-uygunluk/",
    "acceptance": "/hesaplama/usb-c-urun-kabul-testi/",
    "graph": "/urun-bilgi-grafigi/usb-c-ekosistemi/",
}
SOURCES = {key: f"alo186/{route.strip('/')}/index.html" for key, route in ROUTES.items()}
CANONICALS = {key: f"https://www.alo186.com{route}" for key, route in ROUTES.items()}
ENTRY_MARKER = 'data-alo186-growth-run20-entry="true"'
TARGETS = {
    Path("hesaplama/index.html"): ("USB-C zincirini ve satın alma sonrası kabulü doğrulayın", "Cihaz–protokol–adaptör–kablo darboğazını ayırın; ürün geldikten sonra güç, sıcaklık ve kararlılığı karşılaştırılabilir testle kabul edin."),
    Path("elektrik-portali/index.html"): ("USB-C etiketlerini tek başına yeterli kanıt saymayın", "Watt, 3 A/5 A, e-marker, PD/PPS, veri ve görüntü işlevlerini aynı zincirde değerlendirin."),
    Path("akilli-urun-secimi/index.html"): ("Doğrudan affiliate kategorisinden önce mevcut zinciri test edin", "Mevcut adaptör, kablo veya powerbank güvenli ve yeterliyse satın almama sonucunu koruyun."),
    Path("amazon-elektrik-urunleri/index.html"): ("USB-C alışveriş niyetini teknik kanıtla nitelendirin", "Affiliate kategori yalnız gerçek darboğaz, yetersiz mevcut ekipman ve açık satış ortaklığı bildirimi sonrasında açılır."),
    Path("urun-bilgi-grafigi/index.html"): ("USB-C ürün düğümlerini bir ekosistem grafiğinde görün", "Cihaz, protokol, adaptör, kablo ve powerbank ilişkisini semantik kategori düğümleriyle inceleyin."),
    Path("index.html"): ("USB-C adaptör veya kablo almadan önce zinciri doğrulayın", "Yavaş şarjı tek ürüne bağlamayın; güvenli mevcut zincir yeterliyse yeni ürün almayın."),
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
        "chain": ("USB-C Şarj Cihazı ve Kablo Uygunluk Testi", "Cihaz, PD/PPS adaptör ve kablonun güç, akım, e-marker ve protokol uyumunu değerlendirin.", "calculator", ["usb c şarj cihazı kablo uyumu", "pd pps", "45w adaptör 60w kablo", "5a e-marker"]),
        "acceptance": ("USB-C Şarj Cihazı, Kablo ve Hub Kabul Testi", "Yeni USB-C ürünü gerçek güç, sıcaklık, kararlılık, veri ve görüntü işleviyle kabul edin.", "calculator", ["usb c ürün testi", "şarj cihazı ısınıyor", "hub görüntü vermiyor", "kablo kabul testi"]),
        "graph": ("USB-C Şarj Ekosistemi Bilgi Grafiği", "Cihaz, protokol, adaptör, kablo ve powerbank ilişkisini Knowledge Graph üzerinde inceleyin.", "commerce-guide", ["usb c bilgi grafiği", "usb c ekosistemi", "adaptör kablo powerbank", "usb pd pps"]),
    }
    for key, route in ROUTES.items():
        if route in known:
            continue
        title, description, bucket, keywords = metadata[key]
        entries.append({"canonicalPath": route, "url": public_url(base_path, route), "title": title, "description": description, "bucket": bucket, "keywords": keywords})
    payload["entryCount"] = len(entries)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def insert_entries(site: Path, base_path: str) -> int:
    chain = public_url(base_path, ROUTES["chain"])
    acceptance = public_url(base_path, ROUTES["acceptance"])
    graph = public_url(base_path, ROUTES["graph"])
    count = 0
    for relative, (title, body) in TARGETS.items():
        path = site / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if ENTRY_MARKER in text or "</main>" not in text:
            continue
        section = f'''<section {ENTRY_MARKER} style="max-width:1160px;margin:30px auto;padding:24px;border:1px solid #d9e3ef;border-radius:22px;background:#f4f8fd"><span style="font-size:.76rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.07em">USB-C zinciri · kabul testi · Knowledge Graph</span><h2 style="color:#071631">{title}</h2><p>{body}</p><div style="display:flex;flex-wrap:wrap;gap:12px"><a href="{chain}" style="font-weight:850;color:#174bb9">Zincir uygunluk testi →</a><a href="{acceptance}" style="font-weight:850;color:#174bb9">Ürün kabul testi →</a><a href="{graph}" style="font-weight:850;color:#174bb9">USB-C bilgi grafiği →</a></div><small style="display:block;margin-top:12px;color:#58677c">Isı, koku, erime, gevşeklik veya hasarda ticari yol kapanır. İlk düşük sonuç yeni ürün kararı değildir. Affiliate ilişki kategori rehberinin yanında açıkça belirtilir.</small></section>'''
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
    added = []
    for route in ROUTES.values():
        url = public_url(base_path, route)
        if url not in current:
            current.append(url); added.append(url)
    if added:
        path.write_text(text[:match.start(1)] + json.dumps(current, ensure_ascii=False) + text[match.end(1):], encoding="utf-8")
    return added


def update_manifest(site: Path, base_path: str) -> None:
    path = site / "manifest.webmanifest"
    if not path.is_file():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    shortcuts = payload.setdefault("shortcuts", [])
    for name, short, route in [("USB-C Zincir Testi", "USB-C Uygunluk", ROUTES["chain"]), ("USB-C Ürün Kabulü", "USB-C Kabul", ROUTES["acceptance"]), ("USB-C Bilgi Grafiği", "USB-C Grafiği", ROUTES["graph"])]:
        url = public_url(base_path, route)
        if not any(isinstance(item, dict) and item.get("url") == url for item in shortcuts):
            shortcuts.append({"name": name, "short_name": short, "url": url})
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, cards: int, offline: list[str]) -> None:
    metadata = {
        "version": 1,
        "routes": [public_url(base_path, route) for route in ROUTES.values()],
        "entryPointsInjected": cards,
        "offlineRoutesAdded": offline,
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "qualifiedAffiliateFlows": ["usb_c_chain_after_documented_component_gap", "usb_c_acceptance_after_repeated_comparable_failure"],
        "hazardCommerceClosed": True,
        "firstFailureCommerceClosed": True,
        "existingEquipmentNoBuyPreserved": True,
        "officialApprovalClaimed": False,
        "unverifiedCommercialFieldsUsed": [],
        "chainRecordLimit": 6,
        "chainRecordTtlDays": 180,
        "acceptanceRecordLimit": 12,
        "acceptanceRecordTtlDays": 365,
        "chainReviewDays": 90,
        "acceptanceReviewDays": 30,
    }
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    routes = core.setdefault("routes", [])
    known = {item.get("canonicalPath") for item in routes if isinstance(item, dict)}
    for key, route in ROUTES.items():
        if route not in known:
            routes.append({"canonicalPath": route, "source": SOURCES[key], "type": "calculator" if key != "graph" else "commerce-guide"})
    core["routeCount"] = len(routes); core["growthRun20"] = metadata
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8")); pages["routeCount"] = len(routes); pages["growthRun20"] = metadata
        pages["offlineCriticalRouteCount"] = int(pages.get("offlineCriticalRouteCount") or 0) + len(offline)
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists(): path.unlink()
    files = sorted(item for item in site.rglob("*") if item.is_file())
    path.write_text("\n".join(f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}" for item in files) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve(); base_path = normalize_base_path(base_path)
    for key, route in ROUTES.items():
        target = site / route.strip("/") / "index.html"
        if not target.is_file(): raise FileNotFoundError(f"Growth run20 rota eksik: {key} {target}")
    append_sitemap(site); append_search(site, base_path); cards = insert_entries(site, base_path); offline = add_offline(site, base_path)
    update_manifest(site, base_path); update_release(site, base_path, cards, offline); recompute(site)
    return {"ok": True, "basePath": base_path, "routes": [public_url(base_path, route) for route in ROUTES.values()], "entryPointsInjected": cards, "offlineAdded": offline, "directAffiliateLinksAdded": 0, "rawPersonalDataCollected": False, "hazardCommerceClosed": True, "firstFailureCommerceClosed": True, "noBuyOutcomePreserved": True}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--site", type=Path, required=True); parser.add_argument("--base-path", default=""); args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__": main()
