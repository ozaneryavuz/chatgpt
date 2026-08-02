from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROUTE = "/hesaplama/kombi-kesinti-yedek-guc-uygunluk/"
CANONICAL = "https://alo186.com" + ROUTE
SOURCE = "alo186/hesaplama/kombi-kesinti-yedek-guc-uygunluk/index.html"
MARKER = 'data-alo186-boiler-continuity-run30="true"'
HUB_CARD_MARKER = 'data-alo186-boiler-hub-card="true"'
TARGETS = {
    Path("elektrik-portali/index.html"): (
        "Kombi kesintide nasıl güvenle çalışır?",
        "Gazlı ve elektrikli sistemi ayırın; etiket W, hedef süre, nötr-toprak/RCD ve mevcut yedek güç kanıtına göre doğru sonraki adımı görün.",
    ),
    Path("akilli-urun-secimi/index.html"): (
        "Kombi için rastgele UPS seçmeyin",
        "Mevcut çözüm yeterliyse satın almama sonucu alın; yalnız gerçek ve doğrulanmış eksikte UPS, power station veya profesyonel rotaya ilerleyin.",
    ),
    Path("amazon-elektrik-urunleri/index.html"): (
        "Kombi yedek gücünü önce teknik olarak doğrulayın",
        "Isıtma kW değeri ile elektrik W değerini ayırın; gaz/CO ve bağlantı risklerinde ticari yolu kapatın.",
    ),
}


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    return f"{base_path}/{route.lstrip('/')}" if base_path else "/" + route.lstrip("/")


def append_sitemap(site: Path) -> None:
    path = site / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if f"<loc>{CANONICAL}</loc>" in text:
        ET.fromstring(text)
        return
    if "</urlset>" not in text:
        raise RuntimeError("Sitemap kapanış etiketi bulunamadı")
    entry = f"<url><loc>{CANONICAL}</loc></url>"
    updated = text.replace("</urlset>", entry + "</urlset>", 1)
    ET.fromstring(updated)
    path.write_text(updated, encoding="utf-8")


def append_search(site: Path, base_path: str) -> None:
    path = site / "arama/search-index.json"
    if not path.is_file():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.setdefault("entries", [])
    if not any(item.get("canonicalPath") == ROUTE for item in entries if isinstance(item, dict)):
        entries.append({
            "canonicalPath": ROUTE,
            "url": public_url(base_path, ROUTE),
            "title": "Kombi Kesinti Yedek Güç ve UPS Uygunluğu",
            "description": "Gazlı kombi, elektrikli kombi ve ısı pompasını ayırın; etiket W, süre, bağlantı, nötr-toprak/RCD ve mevcut yedek güce göre güvenli sonraki adımı belirleyin.",
            "bucket": "calculator",
            "keywords": [
                "kombi elektrik kesintisinde çalışır mı",
                "kombi için kaç va ups",
                "kombi kaç watt çeker",
                "power station kombi çalıştırır mı",
                "kombi saf sinüs ups",
                "kombi nötr toprak ups",
            ],
        })
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def insert_hub_card(site: Path, base_path: str) -> bool:
    path = site / "hesaplama/index.html"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    href = public_url(base_path, ROUTE)
    changed = False
    if HUB_CARD_MARKER not in text:
        card = (
            f'<a class="tool-card" href="{href}" {HUB_CARD_MARKER}>'
            '<span class="eyebrow">Gazlı / elektrikli · gerçek W · Wh · N-PE · CO</span>'
            '<h2>Kombi Kesinti Yedek Güç ve UPS Uygunluğu</h2>'
            '<p>Kombi türü, etiket elektrik gücü, hedef süre, bağlantı, nötr-toprak/RCD, mevcut yedek güç ve güvenlik kanıtına göre satın almama, test, UPS, power station veya profesyonel rota oluşturun.</p>'
            '<b>Kombi süreklilik planını aç →</b></a>'
        )
        opening = '<section id="araclar" class="tool-grid">'
        if opening not in text:
            raise RuntimeError("Hesaplama Merkezi araç grid başlangıcı bulunamadı")
        text = text.replace(opening, opening + card, 1)
        changed = True
    match = re.search(r"(\d+) çekirdek araç", text)
    if match and int(match.group(1)) < 37:
        text = text[:match.start()] + "37 çekirdek araç" + text[match.end():]
        changed = True
    if changed:
        path.write_text(text, encoding="utf-8")
    return changed


def insert_entry_panels(site: Path, base_path: str) -> int:
    href = public_url(base_path, ROUTE)
    count = 0
    for relative, (title, description) in TARGETS.items():
        path = site / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            continue
        section = (
            f'<section class="content-section" {MARKER}><div class="panel">'
            '<span class="eyebrow">Kombi · elektrik etiketi · satın almama · güvenlik kapısı</span>'
            f'<h2>{title}</h2><p>{description}</p>'
            f'<div class="actions"><a class="btn btn-secondary" href="{href}">Kombi yedek güç uygunluğunu aç</a></div>'
            '<small>Bu araçta doğrudan mağaza bağlantısı yoktur. Sonraki ürün rotasında Amazon satış ortaklığı ilişkisi ayrıca açıklanır.</small>'
            '</div></section>'
        )
        text = text.replace("</main>", section + "</main>", 1) if "</main>" in text else text + section
        path.write_text(text, encoding="utf-8")
        count += 1
    return count


def add_offline(site: Path, base_path: str) -> bool:
    path = site / "sw.js"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        return False
    routes = json.loads(match.group(1))
    url = public_url(base_path, ROUTE)
    if url in routes:
        return False
    routes.append(url)
    path.write_text(text[:match.start(1)] + json.dumps(routes, ensure_ascii=False) + text[match.end(1):], encoding="utf-8")
    return True


def update_manifest(site: Path, base_path: str) -> None:
    path = site / "manifest.webmanifest"
    if not path.is_file():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    shortcuts = payload.setdefault("shortcuts", [])
    url = public_url(base_path, ROUTE)
    if not any(item.get("url") == url for item in shortcuts if isinstance(item, dict)):
        shortcuts.append({"name": "Kombi Yedek Güç Uygunluğu", "short_name": "Kombi Yedek Güç", "url": url})
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, entries: int, hub_card: bool, offline: bool) -> None:
    path = site / "alo186-release.json"
    if not path.is_file():
        return
    release = json.loads(path.read_text(encoding="utf-8"))
    routes = release.setdefault("routes", [])
    if not any(item.get("canonicalPath") == ROUTE for item in routes if isinstance(item, dict)):
        routes.append({"canonicalPath": ROUTE, "source": SOURCE, "type": "calculator"})
    release["routeCount"] = len(routes)
    release["boilerContinuitySuitability"] = {
        "version": 1,
        "basePath": base_path,
        "route": public_url(base_path, ROUTE),
        "entryCardsInjected": entries,
        "hubCardInjected": hub_card,
        "offline": offline,
        "recordLimit": 10,
        "recordTtlDays": 365,
        "reviewMonths": 12,
        "directAffiliateLinksAdded": 0,
        "noBuyOutcomePreserved": True,
        "hazardCommerceClosed": True,
        "electricBoilerConsumerCommerceClosed": True,
        "commercialFieldsExcluded": ["price", "stock", "rating", "seller", "delivery", "warranty", "availability"],
        "officialAffiliationClaimed": False,
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages = site / "pages-release.json"
    if pages.is_file():
        payload = json.loads(pages.read_text(encoding="utf-8"))
        payload["routeCount"] = release["routeCount"]
        payload["boilerContinuitySuitability"] = release["boilerContinuitySuitability"]
        if offline:
            payload["offlineCriticalRouteCount"] = int(payload.get("offlineCriticalRouteCount") or 0) + 1
        pages.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    files = sorted(item for item in site.rglob("*") if item.is_file())
    path.write_text("\n".join(f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}" for item in files) + "\n", encoding="utf-8")


def run(site: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    required = site / "hesaplama/kombi-kesinti-yedek-guc-uygunluk/index.html"
    if not required.is_file():
        raise FileNotFoundError(f"Kombi süreklilik rotası artifactta eksik: {required}")
    append_sitemap(site)
    append_search(site, base_path)
    hub_card = insert_hub_card(site, base_path)
    entries = insert_entry_panels(site, base_path)
    offline = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_release(site, base_path, entries, hub_card, offline)
    recompute(site)
    return {
        "ok": True,
        "route": public_url(base_path, ROUTE),
        "hubCard": hub_card,
        "entries": entries,
        "offline": offline,
        "directAffiliateLinksAdded": 0,
    }
