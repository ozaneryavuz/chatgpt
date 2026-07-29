from __future__ import annotations

import argparse
import hashlib
import json
import re
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

ROUTES = {
    "receipt": "/hesaplama/satin-alma-oncesi-teknik-uygunluk-makbuzu/",
    "freshness": "/icerik-guncellik-merkezi/",
    "site_audit": "/hizmetler/site-villa-elektrik-guvenligi-ev-altyapi-denetimi/",
}
FRESHNESS_DATA = "/icerik-guncellik.json"
HUB = Path("hesaplama/index.html")
PORTAL = Path("elektrik-portali/index.html")
GATEWAY = Path("index.html")
PRODUCT = Path("akilli-urun-secimi/index.html")
CORPORATE = Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html")
MARKERS = {
    "hub": 'data-alo186-growth-run7-receipt="true"',
    "portal": 'data-alo186-growth-run7-freshness="true"',
    "gateway": 'data-alo186-growth-run7-gateway="true"',
    "product": 'data-alo186-growth-run7-affiliate-gate="true"',
    "corporate": 'data-alo186-growth-run7-site-audit="true"',
}


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def canonical_route(value: str, base_path: str) -> str:
    raw = "/" + str(value or "").strip("/")
    trailing = str(value or "").endswith("/") and raw != "/"
    if base_path and raw.startswith(base_path + "/"):
        raw = raw[len(base_path) :]
    if trailing and not raw.endswith("/"):
        raw += "/"
    return raw


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def first_match(html: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, html, re.I | re.S)
        if match:
            return clean_text(match.group(1))
    return ""


def title_of(html: str) -> str:
    return first_match(html, [r"<h1\b[^>]*>(.*?)</h1>", r"<title\b[^>]*>(.*?)</title>"]).replace(" | ALO186", "").strip()


def description_of(html: str) -> str:
    return first_match(
        html,
        [
            r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']',
            r'<meta\s+content=["\']([^"\']*)["\']\s+name=["\']description["\']',
            r'<p\b[^>]*class=["\'][^"\']*\blead\b[^"\']*["\'][^>]*>(.*?)</p>',
        ],
    )[:360]


def verified_date(html: str) -> str:
    value = first_match(
        html,
        [
            r'["\']dateModified["\']\s*:\s*["\'](\d{4}-\d{2}-\d{2})["\']',
            r'["\']datePublished["\']\s*:\s*["\'](\d{4}-\d{2}-\d{2})["\']',
            r'(?:Doğrulama|Güncelleme|Son kontrol)[^0-9]{0,30}(\d{1,2}\s+[A-Za-zÇĞİÖŞÜçğıöşü]+\s+20\d{2})',
        ],
    )
    return value or ""


def topics_of(html: str, title: str) -> list[str]:
    topics: list[str] = []
    for block in re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', html, re.I | re.S):
        try:
            payload = json.loads(block)
        except json.JSONDecodeError:
            continue
        stack = [payload]
        while stack:
            value = stack.pop()
            if isinstance(value, dict):
                if value.get("@type") == "DefinedTerm" and value.get("name"):
                    topics.append(str(value["name"]).strip())
                stack.extend(value.values())
            elif isinstance(value, list):
                stack.extend(value)
    mapping = [
        ("UPS", ["ups"]), ("Jeneratör", ["jeneratör", "generator"]), ("GES", ["ges", "güneş", "pv", "inverter"]),
        ("EV şarj", ["ev şarj", "wallbox", "v2g", "v2h", "v2l"]), ("Topraklama", ["topraklama", "eşpotansiyel"]),
        ("Kaçak akım", ["kaçak akım", "rcd", "rccb", "rcbo"]), ("Parafudr", ["parafudr", "spd"]),
        ("Harmonik", ["harmonik", "thd", "kompanzasyon"]), ("EDAŞ ve kesinti", ["edaş", "kesinti", "186", "tazminat"]),
        ("Enerji depolama", ["batarya", "depolama", "bms", "vpp"]),
    ]
    folded = title.casefold()
    for label, needles in mapping:
        if any(needle.casefold() in folded for needle in needles):
            topics.append(label)
    result: list[str] = []
    seen: set[str] = set()
    for topic in topics:
        key = topic.casefold()
        if topic and key not in seen:
            seen.add(key)
            result.append(topic[:70])
    return result[:8] or ["Elektrik güvenliği"]


def source_domains(html: str) -> list[str]:
    domains: set[str] = set()
    for href in re.findall(r'<a\b[^>]*href=["\'](https?://[^"\']+)["\']', html, re.I):
        host = (urlparse(unescape(href)).hostname or "").casefold().removeprefix("www.")
        if host and host not in {"alo186.com"} and not host.endswith(".alo186.com"):
            domains.add(host)
    return sorted(domains)


def generate_freshness(site: Path, base_path: str) -> dict:
    release = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
    entries: list[dict] = []
    for route in release.get("routes", []):
        if route.get("type") != "article":
            continue
        path = canonical_route(route.get("canonicalPath", ""), base_path)
        target = site / path.strip("/") / "index.html"
        if not target.is_file():
            continue
        html = target.read_text(encoding="utf-8", errors="ignore")
        if "data-alo186-content-alias" in html:
            continue
        title = title_of(html)
        if not title:
            continue
        domains = source_domains(html)
        main = first_match(html, [r"<main\b[^>]*>(.*?)</main>"]) or clean_text(html)
        entries.append({
            "canonicalPath": path,
            "url": public_url(base_path, path),
            "title": title,
            "description": description_of(html),
            "verifiedAt": verified_date(html),
            "sourceDomainCount": len(domains),
            "sourceDomains": domains,
            "topics": topics_of(html, title),
            "revision": hashlib.sha256(main.encode("utf-8")).hexdigest()[:16],
        })
    entries.sort(key=lambda item: (item["verifiedAt"], item["title"].casefold()), reverse=True)
    payload = {
        "version": 1,
        "generatedAt": release.get("generatedAt") or "2026-07-29",
        "entryCount": len(entries),
        "privacy": "Arama ve filtre değerleri sunucuya gönderilmez; okundu revizyonları yalnız kullanıcı isterse tarayıcıda tutulur.",
        "commercialRankingExcluded": ["price", "stock", "rating", "seller", "warranty", "affiliateCommission"],
        "entries": entries,
    }
    (site / FRESHNESS_DATA.strip("/")).write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return payload


def inject_hub(site: Path, base_path: str) -> int:
    path = site / HUB
    text = path.read_text(encoding="utf-8")
    if MARKERS["hub"] in text:
        return 0
    card = f'<a class="tool-card" {MARKERS["hub"]} href="{public_url(base_path, ROUTES["receipt"])}"><span class="eyebrow">Affiliate öncesi · satın almama · 24 saat yeniden kontrol</span><h2>Satın Alma Öncesi Teknik Uygunluk Makbuzu</h2><p>Mevcut ürün yeterliyse satın almayın; gerçek ihtiyaç ve uyumluluk doğrulanmadan ürün rehberine ilerlemeyin.</p><b>Karar makbuzunu oluştur →</b></a>'
    marker = '<section id="araclar" class="tool-grid">'
    if marker not in text:
        raise RuntimeError("Hesaplama merkezi araç grid başlangıcı bulunamadı")
    path.write_text(text.replace(marker, marker + card, 1), encoding="utf-8")
    return 1


def inject_product(site: Path, base_path: str) -> int:
    path = site / PRODUCT
    text = path.read_text(encoding="utf-8")
    if MARKERS["product"] in text:
        return 0
    section = f'<section class="content-section" {MARKERS["product"]}><div class="panel"><span class="eyebrow">Affiliate bağlantısından önce bağımsız karar</span><h2>Önce mevcut ürünün yeterliliğini ve teknik uyumluluğu doğrulayın</h2><p>İhtiyaç yalnız indirim veya merak kaynaklıysa, mevcut ürün güvenli ve yeterliyse ya da kritik değerler eksikse satın almama sonucu alın. Bu güven kapısında mağaza bağlantısı yoktur.</p><div class="actions"><a class="btn btn-secondary" href="{public_url(base_path, ROUTES["receipt"])}">Teknik uygunluk makbuzunu oluştur</a></div><small>Sonraki ürün rehberinde satış ortaklığı bağlantısı varsa ilgili bağlantının yanında açıkça belirtilir.</small></div></section>'
    marker = '<section id="matcher"'
    if marker in text:
        text = text.replace(marker, section + marker, 1)
    else:
        text = text.replace("</main>", section + "</main>", 1)
    path.write_text(text, encoding="utf-8")
    return 1


def inject_portal(site: Path, base_path: str) -> int:
    path = site / PORTAL
    text = path.read_text(encoding="utf-8")
    if MARKERS["portal"] in text:
        return 0
    section = f'<section {MARKERS["portal"]} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#f5f8fd"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Kaynak güncelliği ve tekrar ziyaret</span><h2 style="color:#071631;margin:.4rem 0">Yeni veya güncellenmiş teknik rehberleri, doğrulama tarihi ve kaynak alan adlarıyla görün.</h2><p>Arama ve filtreler sunucuya gönderilmez. Okundu işareti yalnız isterseniz tarayıcıda saklanır; fiyat, stok, puan veya komisyon sıralamaya girmez.</p><a style="display:inline-flex;min-height:44px;align-items:center;color:#174bb9;font-weight:900" href="{public_url(base_path, ROUTES["freshness"])}">İçerik Güncellik Merkezini aç →</a></section>'
    if "</main>" not in text:
        raise RuntimeError("Elektrik portalı main kapanışı bulunamadı")
    path.write_text(text.replace("</main>", section + "</main>", 1), encoding="utf-8")
    return 1


def inject_gateway(site: Path, base_path: str) -> int:
    path = site / GATEWAY
    text = path.read_text(encoding="utf-8")
    if MARKERS["gateway"] in text:
        return 0
    card = f'<a class="card" {MARKERS["gateway"]} href="{public_url(base_path, ROUTES["freshness"])}"><strong>Hangi teknik rehber güncellendi?</strong><p>Kaynak doğrulama tarihi ve içerik revizyonunu kişisel veri vermeden izleyin.</p><span>Güncellik merkezini aç →</span></a>'
    for match in re.finditer(r'<section\b[^>]*>', text, re.I):
        classes = re.search(r'class=["\']([^"\']*)["\']', match.group(0), re.I)
        if classes and "grid" in classes.group(1).split():
            path.write_text(text[: match.end()] + card + text[match.end() :], encoding="utf-8")
            return 1
    return 0


def inject_corporate(site: Path, base_path: str) -> int:
    path = site / CORPORATE
    text = path.read_text(encoding="utf-8")
    if MARKERS["corporate"] in text:
        return 0
    card = f'<a class="service-link-card" {MARKERS["corporate"]} href="{public_url(base_path, ROUTES["site_audit"])}"><span>Site, apartman ve villa projesi</span><h3>Elektrik Güvenliği ve EV Altyapı Denetimi</h3><p>Ortak alan, bağımsız bölüm, trafo, jeneratör, topraklama, RCD/SPD ve EV güç tahsisini aynı teknik kabul planında birleştirin.</p><b>Site ve villa denetimini aç →</b></a>'
    marker = '<div class="service-link-grid">'
    if marker not in text:
        raise RuntimeError("Kurumsal hizmet kart grid başlangıcı bulunamadı")
    path.write_text(text.replace(marker, marker + card, 1), encoding="utf-8")
    return 1


def add_offline(site: Path, base_path: str) -> list[str]:
    path = site / "sw.js"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        raise RuntimeError("Service worker CRITICAL rota dizisi bulunamadı")
    routes = json.loads(match.group(1))
    additions = [public_url(base_path, route) for route in ROUTES.values()] + [public_url(base_path, FRESHNESS_DATA)]
    added = []
    for url in additions:
        if url not in routes:
            routes.append(url)
            added.append(url)
    if added:
        path.write_text(text[: match.start(1)] + json.dumps(routes, ensure_ascii=False) + text[match.end(1) :], encoding="utf-8")
    return added


def update_manifest(site: Path, base_path: str) -> None:
    path = site / "manifest.webmanifest"
    if not path.is_file():
        return
    manifest = json.loads(path.read_text(encoding="utf-8"))
    shortcuts = manifest.setdefault("shortcuts", [])
    additions = [
        {"name": "İçerik Güncellik Merkezi", "short_name": "Güncellik", "url": public_url(base_path, ROUTES["freshness"])},
        {"name": "Satın Alma Uygunluk Makbuzu", "short_name": "Satın Alma Kontrolü", "url": public_url(base_path, ROUTES["receipt"])},
    ]
    for item in additions:
        if not any(isinstance(existing, dict) and existing.get("url") == item["url"] for existing in shortcuts):
            shortcuts.append(item)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, payload: dict, cards: int, offline: list[str]) -> None:
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    core["growthRun7"] = {
        "version": 1,
        "routes": list(ROUTES.values()),
        "freshnessEntryCount": payload["entryCount"],
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "commercialRankingFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "affiliateGateBeforeStore": True,
        "sourceFreshnessLocalComparison": True,
        "officialInstitutionImpersonation": False,
        "siteVillaServiceWrittenScopeRequired": True,
    }
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["growthRun7"] = {
            "version": 1,
            "basePath": base_path,
            "routes": [public_url(base_path, route) for route in ROUTES.values()],
            "freshnessData": public_url(base_path, FRESHNESS_DATA),
            "freshnessEntryCount": payload["entryCount"],
            "entryCardsInjected": cards,
            "offlineAdded": offline,
        }
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    files = sorted(item for item in site.rglob("*") if item.is_file())
    path.write_text("\n".join(f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}" for item in files) + "\n", encoding="utf-8")


def run(site: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    for route in ROUTES.values():
        target = site / route.strip("/") / "index.html"
        if not target.is_file():
            raise FileNotFoundError(f"Growth run7 rotası artifactta eksik: {target}")
    payload = generate_freshness(site, base_path)
    cards = inject_hub(site, base_path)
    cards += inject_product(site, base_path)
    cards += inject_portal(site, base_path)
    cards += inject_gateway(site, base_path)
    cards += inject_corporate(site, base_path)
    offline = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_release(site, base_path, payload, cards, offline)
    recompute(site)
    return {
        "ok": True,
        "basePath": base_path,
        "routes": [public_url(base_path, route) for route in ROUTES.values()],
        "freshnessEntryCount": payload["entryCount"],
        "entryCardsInjected": cards,
        "offlineAdded": offline,
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
