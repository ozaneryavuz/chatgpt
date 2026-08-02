from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from inject_boiler_continuity_growth import run as run_boiler_continuity
from inject_growth_run22 import run as run_growth_run22

ROUTE = "/hesaplama/kesinti-hazirlik-envanteri/"
CANONICAL = "https://alo186.com" + ROUTE
SOURCE = "alo186/hesaplama/kesinti-hazirlik-envanteri/index.html"
ENTRY_MARKER = 'data-alo186-growth-run21-entry="true"'
GUARD_MARKER = 'data-alo186-risk-gate-run21="true"'
TARGETS = {
    Path("hesaplama/index.html"): ("Kesinti hazırlık envanterinizi çıkarın", "Mevcut ürünleri kaydedin; çalışan ekipmanı yeniden satın almayın ve yalnız gerçek eksikleri görün."),
    Path("elektrik-portali/index.html"): ("Mevcut ekipmanı önce değerlendirin", "Telefon, internet, aydınlatma ve erken uyarı hazırlığını kişisel veri paylaşmadan kaydedin."),
    Path("akilli-urun-secimi/index.html"): ("Satın almadan önce elinizdekileri sayın", "Test edilmiş ürün yeterliyse satın almama sonucu; yalnız doğrulanmış eksikte kategori rehberi."),
    Path("amazon-elektrik-urunleri/index.html"): ("Hazır paket yerine gerçek eksik", "Kesinti hazırlık envanteriyle yalnız eksik işlevleri belirleyin; test edilmemiş ürünü değiştirmeyin."),
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
    entry = f"<url><loc>{CANONICAL}</loc></url>"
    if "</urlset>" not in text:
        raise RuntimeError("Sitemap kapanış etiketi bulunamadı")
    updated = text.replace("</urlset>", entry + "</urlset>", 1)
    ET.fromstring(updated)
    path.write_text(updated, encoding="utf-8")


def append_search(site: Path, base_path: str) -> None:
    path = site / "arama/search-index.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.setdefault("entries", [])
    if not any(item.get("canonicalPath") == ROUTE for item in entries if isinstance(item, dict)):
        entries.append({
            "canonicalPath": ROUTE,
            "url": public_url(base_path, ROUTE),
            "title": "Kesinti Hazırlık Envanteri ve Ürün İhtiyaç Kontrolü",
            "description": "Mevcut ekipmanı kaydedin, çalışan ürünü yeniden satın almayın, gerçek eksikleri ve 90 günlük test planını belirleyin.",
            "bucket": "calculator",
            "keywords": ["elektrik kesintisi hazırlık listesi", "evde kesinti için gerekli ürünler", "powerbank mini UPS acil aydınlatma", "mevcut ürün yeterli mi", "kesinti ekipmanı test takvimi"],
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
        shortcuts.append({"name": "Kesinti Hazırlık Envanteri", "short_name": "Hazırlık Envanteri", "url": url})
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
        card = f'<section class="content-section" {ENTRY_MARKER}><div class="panel"><span class="eyebrow">Mevcut ekipman · satın almama · 90 günlük test</span><h2>{title}</h2><p>{description}</p><div class="actions"><a class="btn btn-secondary" href="{href}">Kesinti hazırlık envanterini aç</a></div><small>Doğrudan mağaza bağlantısı yoktur; gerçek eksik doğrulanırsa kategori rehberine geçilir.</small></div></section>'
        text = text.replace("</main>", card + "</main>", 1) if "</main>" in text else text + card
        path.write_text(text, encoding="utf-8")
        count += 1
    return count


def inject_risk_gate(site: Path, base_path: str) -> bool:
    path = site / "amazon-elektrik-urunleri/index.html"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    if GUARD_MARKER in text:
        return False
    fallback = public_url(base_path, "/akilli-urun-secimi")
    banner = f'<div class="affiliate-disclosure" {GUARD_MARKER}><strong>Risk bazlı ticari kapı:</strong> Pano, sabit tesisat, yüksek güçlü enerji, GES, jeneratör, EV şarj ve ölçüm gerektiren ürünlerde doğrudan mağaza bağlantısı kapatılır; önce teknik rehber veya uzmanlık sınırı açılır.</div>'
    script = rf'''<script {GUARD_MARKER}>(function(){{'use strict';const patterns=[/pano/i,/rccb/i,/rcbo/i,/otomatik sigorta/i,/kaçak akım/i,/\bspd\b/i,/gerilim rölesi/i,/jeneratör/i,/inverter/i,/mppt/i,/solar dc/i,/ges/i,/elektrikli araç/i,/ev şarj/i,/transfer şalteri/i,/kontaktör/i,/akım trafosu/i,/kablo makarası/i,/dış ortam kauçuk/i];const amazonHost='amazon'+'.com.tr';let gated=0;for(const link of document.querySelectorAll('a[href*="'+amazonHost+'"]')){{const box=link.closest('article,.card,li,section')||link.parentElement;const text=(box?box.textContent:link.textContent)||'';if(!patterns.some(pattern=>pattern.test(text)))continue;const internal=box&&[...box.querySelectorAll('a[href]')].find(item=>item!==link&&!/amazon\.com\.tr/i.test(item.href)&&item.getAttribute('href')&&!item.getAttribute('href').startsWith('#'));link.href=internal?internal.getAttribute('href'):'{fallback}';link.removeAttribute('target');link.removeAttribute('rel');link.dataset.alo186RiskGated='true';link.textContent='Önce teknik uygunluğu doğrula';gated++;}}document.documentElement.dataset.alo186RiskGatedCount=String(gated);}})();</script>'''
    if '<div class="affiliate-disclosure"' in text:
        text = text.replace('<div class="affiliate-disclosure"', banner + '<div class="affiliate-disclosure"', 1)
    else:
        text = text.replace("<main", banner + "<main", 1)
    text = text.replace("</body>", script + "</body>", 1)
    path.write_text(text, encoding="utf-8")
    return True


def update_release(site: Path, base_path: str, entries: int, risk_gate: bool, offline: bool) -> None:
    path = site / "alo186-release.json"
    release = json.loads(path.read_text(encoding="utf-8"))
    routes = release.setdefault("routes", [])
    if not any(item.get("canonicalPath") == ROUTE for item in routes if isinstance(item, dict)):
        routes.append({"canonicalPath": ROUTE, "source": SOURCE, "type": "tool"})
    release["routeCount"] = len(routes)
    release["outagePreparednessInventory"] = {
        "version": 1,
        "basePath": base_path,
        "route": public_url(base_path, ROUTE),
        "entryCardsInjected": entries,
        "riskBasedAffiliateGate": risk_gate,
        "offline": True,
        "recordLimit": 12,
        "recordTtlDays": 365,
        "reviewDays": 90,
        "directAffiliateLinksAdded": 0,
        "commercialFieldsExcluded": ["price", "stock", "rating", "seller", "warranty"],
        "officialAffiliationClaimed": False,
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages = site / "pages-release.json"
    if pages.is_file():
        payload = json.loads(pages.read_text(encoding="utf-8"))
        payload["routeCount"] = release["routeCount"]
        payload["outagePreparednessInventory"] = release["outagePreparednessInventory"]
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
    required = site / "hesaplama/kesinti-hazirlik-envanteri/index.html"
    if not required.is_file():
        raise FileNotFoundError(f"Kesinti hazırlık envanteri artifactta eksik: {required}")
    append_sitemap(site)
    append_search(site, base_path)
    entries = insert_entries(site, base_path)
    risk_gate = inject_risk_gate(site, base_path)
    offline = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_release(site, base_path, entries, risk_gate, offline)
    recompute(site)
    lighting = run_growth_run22(site, base_path)
    boiler = run_boiler_continuity(site, base_path)
    ET.parse(site / "sitemap.xml")
    return {"ok": True, "route": public_url(base_path, ROUTE), "entries": entries, "riskGate": risk_gate, "offline": True, "lightingSuitability": lighting, "boilerContinuity": boiler}
