from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from finalize_live_quality import run as finalize_live_quality
from finalize_sitemap_uniqueness import run as finalize_sitemap_uniqueness
from repair_live_html_defects import run as repair_live_html_defects

ROUTE = "/hesaplama/home-office-internet-sureklilik-plani/"
CANONICAL = "https://www.alo186.com" + ROUTE
SOURCE = "alo186/hesaplama/home-office-internet-sureklilik-plani/index.html"
ENTRY_MARKER = 'data-alo186-growth-run24-entry="true"'
TARGETS = {
    Path("hesaplama/index.html"): ("Home office internet sürekliliğini test edin", "Modem ve ONT gücü ile operatör altyapısı kesintisini ayırın; kritik yükü ve gerçek enerji açığını hesaplayın."),
    Path("elektrik-portali/index.html"): ("Elektrik varken internet neden yok?", "Yerel cihazlar enerjiliyken upstream erişim ağının çalışıp çalışmadığını kaydedin; gereksiz UPS büyütmeyin."),
    Path("akilli-urun-secimi/index.html"): ("Önce bağlantının nerede kesildiğini bulun", "Yalnız yerel güç açığı doğrulanırsa mini UPS, powerbank veya güç istasyonu kategorisine ilerleyin."),
    Path("amazon-elektrik-urunleri/index.html"): ("Home office için hazır paket değil, kanıtlı eksik", "İnternet operatör tarafında kesiliyorsa daha büyük yerel batarya satın almayın; önce karşılaştırılabilir olay kaydı oluşturun."),
    Path("elektrik-durum-merkezi/index.html"): ("İnternet ve çalışma sürekliliğini ayrı teşhis edin", "Modem/ONT, bilgisayar, mobil yedek ve upstream erişim ağını tek planda değerlendirin."),
}


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    return f"{base_path}/{route.lstrip('/')}" if base_path else "/" + route.lstrip("/")


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
            "title": "Home Office İnternet ve Elektrik Süreklilik Planı",
            "description": "Modem ve ONT yerel güç açığını operatör erişim ağı kesintisinden ayırın; kritik yük enerjisini hesaplayın ve gereksiz ürün almayın.",
            "bucket": "calculator",
            "keywords": [
                "elektrik kesintisinde internet nasıl devam eder",
                "modem ups alsam internet çalışır mı",
                "ont los ışığı elektrik kesintisi",
                "home office elektrik kesintisi",
                "modem mini ups kaç saat",
                "internet kesintisi operatör saha dolabı",
                "laptop modem ups çalışma süresi",
            ],
        })
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_offline(site: Path, base_path: str) -> bool:
    path = site / "sw.js"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        raise RuntimeError("Service worker CRITICAL rota dizisi bulunamadı")
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
        shortcuts.append({"name": "Home Office Süreklilik Planı", "short_name": "İnternet Sürekliliği", "url": url})
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def insert_entries(site: Path, base_path: str) -> int:
    count = 0
    href = public_url(base_path, ROUTE)
    for relative, (title, description) in TARGETS.items():
        path = site / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if ENTRY_MARKER in text:
            continue
        card = f'<section class="content-section" {ENTRY_MARKER}><div class="panel"><span class="eyebrow">Yerel güç · upstream ağ · 30 günlük tatbikat</span><h2>{title}</h2><p>{description}</p><div class="actions"><a class="btn btn-secondary" href="{href}">Home office süreklilik planını aç</a></div><small>Doğrudan mağaza bağlantısı yoktur; mevcut çözüm yeterliyse satın alma gerekli değildir.</small></div></section>'
        text = text.replace("</main>", card + "</main>", 1) if "</main>" in text else text + card
        path.write_text(text, encoding="utf-8")
        count += 1
    return count


def update_release(site: Path, base_path: str, entries: int, offline: bool) -> None:
    path = site / "alo186-release.json"
    release = json.loads(path.read_text(encoding="utf-8"))
    routes = release.setdefault("routes", [])
    if not any(item.get("canonicalPath") == ROUTE for item in routes if isinstance(item, dict)):
        routes.append({"canonicalPath": ROUTE, "source": SOURCE, "type": "tool"})
    release["routeCount"] = len(routes)
    release["homeOfficeContinuity"] = {
        "version": 1,
        "basePath": base_path,
        "route": public_url(base_path, ROUTE),
        "entryCardsInjected": entries,
        "offline": True,
        "recordLimit": 12,
        "recordTtlDays": 365,
        "reviewDays": 30,
        "upstreamFailureSuppressesCommerce": True,
        "repeatedUpstreamEvidenceCount": 2,
        "directAffiliateLinksAdded": 0,
        "noBuyOutcomePreserved": True,
        "hazardCommerceClosed": True,
        "commercialFieldsExcluded": ["price", "stock", "rating", "seller", "warranty"],
        "officialAffiliationClaimed": False,
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages = site / "pages-release.json"
    if pages.is_file():
        payload = json.loads(pages.read_text(encoding="utf-8"))
        payload["routeCount"] = release["routeCount"]
        payload["homeOfficeContinuity"] = release["homeOfficeContinuity"]
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
    required = site / "hesaplama/home-office-internet-sureklilik-plani/index.html"
    if not required.is_file():
        raise FileNotFoundError(f"Home office süreklilik rotası artifactta eksik: {required}")
    append_sitemap(site)
    append_search(site, base_path)
    entries = insert_entries(site, base_path)
    offline = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_release(site, base_path, entries, offline)
    html_shell_repairs = repair_live_html_defects(site, base_path)
    recompute(site)
    sitemap_uniqueness = finalize_sitemap_uniqueness(site)
    technical_quality = finalize_live_quality(site, base_path)
    return {
        "ok": True,
        "route": public_url(base_path, ROUTE),
        "entries": entries,
        "offline": True,
        "htmlShellRepairs": html_shell_repairs,
        "sitemapUniqueness": sitemap_uniqueness,
        "technicalQuality": technical_quality,
    }
