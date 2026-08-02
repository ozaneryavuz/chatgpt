from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

from apply_content_consolidation import apply as apply_content_consolidation
from inject_article_growth import run as run_article_growth
from inject_commerce_trust import run as run_commerce_trust
from inject_growth_run6 import run as run_growth_run6
from inject_growth_run7 import run as run_growth_run7
from inject_growth_run8 import run as run_growth_run8
from inject_growth_run9 import run as run_growth_run9
from inject_growth_run10 import run as run_growth_run10
from inject_growth_run11 import run as run_growth_run11
from inject_growth_run12 import run as run_growth_run12
from inject_growth_run13 import run as run_growth_run13
from inject_growth_run14 import run as run_growth_run14
from inject_growth_run15 import run as run_growth_run15
from inject_growth_run18 import run as run_growth_run18
from inject_growth_run19 import run as run_growth_run19
from inject_growth_run21 import run as run_growth_run21
from inject_handoff_growth import run as run_handoff_growth
from inject_private_search import run as run_private_search
from inject_revenue_trust_proof import run as run_revenue_trust_proof
from inject_retention_growth import run as run_retention_growth
from normalize_article_followup_paths import run as normalize_article_followup_paths
from normalize_consolidated_release import run as normalize_consolidated_release

CANONICAL = "https://www.alo186.com/hesaplama/teknik-urun-karsilastirma/"
CANONICAL_PATH = "/hesaplama/teknik-urun-karsilastirma/"
SOURCE = "alo186/hesaplama/teknik-urun-karsilastirma/index.html"
HUB = Path("hesaplama/index.html")
PORTAL = Path("elektrik-portali/index.html")
GATEWAY = Path("index.html")
PRODUCT = Path("akilli-urun-secimi/index.html")
COMMERCE_HUB = Path("amazon-elektrik-urunleri/index.html")
HUB_MARKER = 'data-alo186-shortlist-hub-card="true"'
PORTAL_MARKER = 'data-alo186-shortlist-entry-card="true"'
PRODUCT_MARKER = 'data-alo186-shortlist-product-card="true"'


def normalize_base_path(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    return f"{base_path}/{route.lstrip('/')}" if base_path else "/" + route.lstrip("/")


def append_sitemap(site: Path) -> None:
    path = site / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    if f"<loc>{CANONICAL}</loc>" not in text:
        entry = f"<url><loc>{CANONICAL}</loc></url>"
        text = text.replace("</urlset>", entry + "</urlset>", 1)
        path.write_text(text, encoding="utf-8")


def append_release(site: Path) -> None:
    path = site / "alo186-release.json"
    release = json.loads(path.read_text(encoding="utf-8"))
    routes = release.setdefault("routes", [])
    if not any(item.get("canonicalPath") == CANONICAL_PATH for item in routes):
        routes.append({"canonicalPath": CANONICAL_PATH, "source": SOURCE, "type": "tool"})
    release["routeCount"] = len(routes)
    release["technicalShortlist"] = {
        "version": 1,
        "candidateLimit": 3,
        "receiptLimit": 6,
        "receiptTtlDays": 45,
        "reviewDays": 14,
        "commercialFieldsExcluded": ["price", "stock", "rating", "seller", "warranty", "asin"],
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_offline(site: Path, base_path: str) -> bool:
    path = site / "sw.js"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        raise RuntimeError("Service worker CRITICAL rota dizisi bulunamadı")
    routes = json.loads(match.group(1))
    url = public_url(base_path, CANONICAL_PATH)
    if url in routes:
        return False
    routes.append(url)
    path.write_text(text[: match.start(1)] + json.dumps(routes, ensure_ascii=False) + text[match.end(1) :], encoding="utf-8")
    return True


def update_pages_release(site: Path, base_path: str, offline_added: bool, cards: int) -> None:
    path = site / "pages-release.json"
    release = json.loads(path.read_text(encoding="utf-8"))
    core = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
    release["routeCount"] = core.get("routeCount")
    release["technicalShortlist"] = {
        "version": 1,
        "basePath": base_path,
        "route": public_url(base_path, CANONICAL_PATH),
        "entryCardsInjected": cards,
        "offline": True,
        "candidateLimit": 3,
        "reviewDays": 14,
    }
    if offline_added:
        release["offlineCriticalRouteCount"] = int(release.get("offlineCriticalRouteCount") or 0) + 1
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_manifest(site: Path, base_path: str) -> None:
    path = site / "manifest.webmanifest"
    if not path.is_file():
        return
    manifest = json.loads(path.read_text(encoding="utf-8"))
    shortcuts = manifest.setdefault("shortcuts", [])
    url = public_url(base_path, CANONICAL_PATH)
    if not any(item.get("url") == url for item in shortcuts if isinstance(item, dict)):
        shortcuts.append({"name": "Teknik Ürün Karşılaştırma", "short_name": "Teknik Kısa Liste", "url": url})
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def raise_count(text: str) -> str:
    match = re.search(r"(\d+) çekirdek araç", text)
    if not match:
        return text
    current = int(match.group(1))
    return text[: match.start(1)] + str(max(current, 34)) + text[match.end(1) :]


def sync_commerce_hub_inventory(site: Path) -> dict:
    path = site / COMMERCE_HUB
    if not path.is_file():
        return {"updated": False, "guideCount": 0, "reason": "hub_missing"}
    text = path.read_text(encoding="utf-8")
    section = re.search(
        r'<section class="section" aria-labelledby="routesTitle">(.*?)</section>',
        text,
        re.S,
    )
    if not section:
        return {"updated": False, "guideCount": 0, "reason": "routes_section_missing"}
    guide_count = len(re.findall(r'<article class="card route-card">', section.group(1)))
    if guide_count < 1:
        return {"updated": False, "guideCount": 0, "reason": "cards_missing"}
    original = text
    text = re.sub(r"\d+ özel rehber", f"{guide_count} özel rehber", text, count=1)
    text = re.sub(
        r"Aynı ürün listesini çoğaltmak yerine [^<]* ayrı ihtiyacı çözüyoruz\.",
        "Aynı ürün listesini çoğaltmak yerine kullanıcıya göre ayrılmış ticari ihtiyaçları çözüyoruz.",
        text,
        count=1,
    )
    if text != original:
        path.write_text(text, encoding="utf-8")
    return {"updated": text != original, "guideCount": guide_count, "reason": "synchronized"}


def insert_hub(site: Path, base_path: str) -> int:
    path = site / HUB
    text = raise_count(path.read_text(encoding="utf-8"))
    if HUB_MARKER in text:
        path.write_text(text, encoding="utf-8")
        return 0
    href = public_url(base_path, CANONICAL_PATH)
    card = f'<a class="tool-card" {HUB_MARKER} href="{href}"><span class="eyebrow">Üç aday · mevcut ürün · karar makbuzu</span><h2>Teknik Ürün Karşılaştırma</h2><p>Marka, fiyat ve puan kullanmadan üç adayın kritik teknik belgelerini karşılaştırın; mevcut ürün yeterliyse satın almama sonucu alın.</p><b>Teknik kısa listeyi oluştur →</b></a>'
    text = text.replace('<section id="araclar" class="tool-grid">', '<section id="araclar" class="tool-grid">' + card, 1)
    path.write_text(text, encoding="utf-8")
    return 1


def insert_grid_card(site: Path, relative: Path, base_path: str, gateway: bool) -> int:
    path = site / relative
    text = path.read_text(encoding="utf-8")
    if PORTAL_MARKER in text:
        return 0
    href = public_url(base_path, CANONICAL_PATH)
    if gateway:
        card = f'<a class="card" {PORTAL_MARKER} href="{href}"><strong>Üç ürün adayını teknik olarak karşılaştırın</strong><p>Marka ve fiyat kullanmadan belge kapsamını görün; mevcut ürün yeterliyse satın almayın.</p><span>Teknik kısa listeyi aç →</span></a>'
    else:
        card = f'<a class="card" {PORTAL_MARKER} href="{href}"><span class="tag">Üç aday · teknik belge · satın almama</span><h2>Teknik Ürün Karşılaştırma</h2><p>Power station, mini UPS, powerbank, EV kablosu ve güvenli tüketici ürünlerini belge kapsamıyla karşılaştırın.</p><b>Kısa listeyi oluştur →</b></a>'
    for match in re.finditer(r'<section\b[^>]*>', text, re.I):
        classes = re.search(r'class=["\']([^"\']*)["\']', match.group(0), re.I)
        if classes and "grid" in classes.group(1).split():
            text = text[: match.end()] + card + text[match.end() :]
            path.write_text(text, encoding="utf-8")
            return 1
    return 0


def insert_product(site: Path, base_path: str) -> int:
    path = site / PRODUCT
    text = path.read_text(encoding="utf-8")
    if PRODUCT_MARKER in text:
        return 0
    href = public_url(base_path, CANONICAL_PATH)
    section = f'<section class="content-section" {PRODUCT_MARKER}><div class="panel"><span class="eyebrow">Karşılaştırma öncesi güven kapısı</span><h2>Üç adayı marka ve fiyat kullanmadan karşılaştırın</h2><p>Mevcut ürünü dördüncü seçenek olarak koruyun. Kritik teknik belge eksikse ürün rotasını açmayın; 14 günlük karar makbuzu oluşturun.</p><div class="actions"><a class="btn btn-secondary" href="{href}">Teknik kısa listeyi aç</a></div><small>Doğrudan mağaza, fiyat, stok, puan veya garanti bilgisi gösterilmez.</small></div></section>'
    marker = '<section id="matcher"'
    if marker in text:
        text = text.replace(marker, section + marker, 1)
    else:
        text = text.replace("</main>", section + "</main>", 1)
    path.write_text(text, encoding="utf-8")
    return 1


def reconcile_sitemap_with_release(site: Path) -> dict:
    sitemap_path=site / "sitemap.xml"
    release_path=site / "alo186-release.json"
    if not sitemap_path.is_file() or not release_path.is_file():
        raise FileNotFoundError("Sitemap veya release envanteri bulunamadı")
    release=json.loads(release_path.read_text(encoding="utf-8"))
    recovered_malformed=False
    try:
        tree=ET.parse(sitemap_path)
        root=tree.getroot()
        namespace=root.tag.split("}")[0].strip("{") if "}" in root.tag else ""
    except ET.ParseError:
        # The release inventory is the fail-closed source of truth. A previous
        # legacy growth injector may leave partially written XML; rebuild only
        # from active canonical routes instead of publishing a broken sitemap.
        namespace="http://www.sitemaps.org/schemas/sitemap/0.9"
        root=ET.Element(f"{{{namespace}}}urlset")
        tree=ET.ElementTree(root)
        recovered_malformed=True
    ns=f"{{{namespace}}}" if namespace else ""
    def normalized_path(value: str) -> str:
        parsed=urlsplit(str(value or "")).path or "/"
        return parsed.rstrip("/") or "/"
    present=set()
    for node in root.findall(f"{ns}url"):
        loc=node.find(f"{ns}loc")
        if loc is not None and loc.text:
            present.add(normalized_path(loc.text))
    added=[]
    canonical_host=str(release.get("canonicalHost") or "https://www.alo186.com").rstrip("/")
    pages_release_path=site / "pages-release.json"
    pages_release=json.loads(pages_release_path.read_text(encoding="utf-8")) if pages_release_path.is_file() else {}
    release_base_path=normalize_base_path(str(pages_release.get("basePath") or ""))
    for route in release.get("routes",[]):
        canonical_path=str(route.get("canonicalPath") or "").strip()
        if not canonical_path:
            continue
        route_path=normalized_path(canonical_path)
        if release_base_path and (route_path == release_base_path or route_path.startswith(release_base_path + "/")):
            route_path=route_path[len(release_base_path):] or "/"
        if route_path in present:
            continue
        url=ET.SubElement(root,f"{ns}url")
        loc=ET.SubElement(url,f"{ns}loc")
        loc.text=f"{canonical_host}{route_path}"
        present.add(route_path)
        added.append(canonical_path)
    ET.register_namespace("",namespace)
    ET.indent(tree,space="  ")
    tree.write(sitemap_path,encoding="utf-8",xml_declaration=True)
    return {"activeRouteCount":len(release.get("routes",[])),"addedCount":len(added),"added":added,"recoveredMalformedSitemap":recovered_malformed,"policy":"active-release-routes-must-exist-in-sitemap"}


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    files = sorted(item for item in site.rglob("*") if item.is_file())
    lines = [f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}" for item in files]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(site: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    required = site / "hesaplama" / "teknik-urun-karsilastirma" / "index.html"
    if not required.is_file():
        raise FileNotFoundError(f"Teknik kısa liste rotası artifactta eksik: {required}")
    append_sitemap(site)
    append_release(site)
    cards = insert_hub(site, base_path)
    cards += insert_grid_card(site, PORTAL, base_path, False)
    cards += insert_grid_card(site, GATEWAY, base_path, True)
    cards += insert_product(site, base_path)
    offline_added = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_pages_release(site, base_path, offline_added, cards)
    recompute(site)
    handoff = run_handoff_growth(site, base_path)
    consolidation = apply_content_consolidation(site, base_path)
    consolidated_release = normalize_consolidated_release(site, base_path)
    site_search = run_private_search(site, base_path)
    article_journey = run_article_growth(site, base_path)
    followup_paths = normalize_article_followup_paths(site, base_path)
    commerce_trust = run_commerce_trust(site, base_path)
    revenue_trust_proof = run_revenue_trust_proof(site, base_path)
    retention_growth = run_retention_growth(site, base_path)
    growth_run6 = run_growth_run6(site, base_path)
    growth_run7 = run_growth_run7(site, base_path)
    growth_run8 = run_growth_run8(site, base_path)
    growth_run9 = run_growth_run9(site, base_path)
    growth_run10 = run_growth_run10(site, base_path)
    growth_run11 = run_growth_run11(site, base_path)
    growth_run12 = run_growth_run12(site, base_path)
    growth_run13 = run_growth_run13(site, base_path)
    growth_run14 = run_growth_run14(site, base_path)
    growth_run15 = run_growth_run15(site, base_path)
    growth_run18 = run_growth_run18(site, base_path)
    growth_run19 = run_growth_run19(site, base_path)
    growth_run21 = run_growth_run21(site, base_path)
    commerce_inventory = sync_commerce_hub_inventory(site)
    sitemap_reconciliation = reconcile_sitemap_with_release(site)
    recompute(site)
    return {
        "ok": True,
        "basePath": base_path,
        "cardsInjected": cards,
        "offlineAdded": offline_added,
        "route": public_url(base_path, CANONICAL_PATH),
        "technicalHandoff": handoff,
        "contentConsolidation": consolidation,
        "consolidatedRelease": consolidated_release,
        "siteSearch": site_search,
        "articleJourney": article_journey,
        "followupPaths": followup_paths,
        "commerceTrust": commerce_trust,
        "revenueTrustProof": revenue_trust_proof,
        "retentionGrowth": retention_growth,
        "growthRun6": growth_run6,
        "growthRun7": growth_run7,
        "growthRun8": growth_run8,
        "growthRun9": growth_run9,
        "growthRun10": growth_run10,
        "growthRun11": growth_run11,
        "growthRun12": growth_run12,
        "growthRun13": growth_run13,
        "growthRun14": growth_run14,
        "growthRun15": growth_run15,
        "growthRun18": growth_run18,
        "growthRun19": growth_run19,
        "growthRun21": growth_run21,
        "commerceInventory": commerce_inventory,
        "sitemapReconciliation": sitemap_reconciliation,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
