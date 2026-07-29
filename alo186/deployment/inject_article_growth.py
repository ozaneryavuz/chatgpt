from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date, datetime
from html import escape, unescape
from pathlib import Path

FOLLOWUP_PATH = "/hesaplama/teknik-takip-listem/"
ASSET_CSS = "/assets/article-growth.css"
ASSET_JS = "/assets/article-growth.js"
DEPLOYMENT_ASSETS = Path(__file__).with_name("assets")
ARTICLE_MARKER = 'data-alo186-article-next-step="true"'
INVENTORY_MARKER = 'data-alo186-inventory-strip="true"'
ENTRY_MARKER = 'data-alo186-followup-entry-card="true"'
PORTAL = Path("elektrik-portali/index.html")
GATEWAY = Path("index.html")
VERSION = 1

OFFICIAL_PATTERNS = (
    r"edas", r"elektrik-kesintisi", r"planli-elektrik-kesintisi", r"tazminat",
    r"elektrik-sayaci", r"fatura-itirazi", r"tedarikci-mi-aranir", r"teknik-kalite",
    r"dusuk-yuksek-voltaj", r"lisanssiz-ges-mahsuplasma", r"cihaz-hasari",
)
CONSUMER_RULES: tuple[tuple[str, str, str], ...] = (
    (r"powerbank", "/hesaplama/powerbank-usb-c-uygunluk/", "Powerbank ve USB-C uygunluğunu hesaplayın"),
    (r"power-station-gunes-paneli|power-station", "/hesaplama/power-station-kapasite-eps-uygunluk/", "Gerekli Wh, W ve EPS uygunluğunu hesaplayın"),
    (r"modem|mini-ups", "/hesaplama/modem-internet-yedekleme/", "Modem ve ONT için gerçek enerji ihtiyacını hesaplayın"),
    (r"ups-akusu-ne-zaman-degisir|ups-va-watt|ups-online-line-interactive-offline|ups-eco-modu", "/hesaplama/ups-aku-degisim-uygunluk/", "UPS ve akü ihtiyacını teknik verilerle doğrulayın"),
    (r"duman-alarmi", "/hesaplama/duman-alarmi-yerlesim-bakim-uygunluk/", "Duman alarmı yerleşim ve bakım kontrolünü yapın"),
    (r"akilli-priz|enerji-olcer", "/hesaplama/akilli-priz-enerji-olcer-uygunluk/", "Akıllı priz veya enerji ölçer uygunluğunu test edin"),
    (r"akim-korumali-grup-priz|korumali-priz", "/hesaplama/akim-korumali-grup-priz-uygunluk/", "Grup priz teknik sınırlarını kontrol edin"),
    (r"tip-2-ev-sarj-kablosu", "/hesaplama/ev-sarj-kablosu-uygunluk/", "Type 2 kablo uyumunu araç ve şarj noktasıyla doğrulayın"),
    (r"acil-aydinlatma", "/hesaplama/acil-aydinlatma-sure-uygunluk/", "Acil aydınlatma süre ve bakım uygunluğunu kontrol edin"),
    (r"uzatma-kablosu", "/hesaplama/uzatma-kablosu-uygunluk/", "Uzatma kablosu akım ve kullanım uygunluğunu test edin"),
)


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + str(route or "").lstrip("/")
    return f"{base_path}{route}" if base_path else route


def canonical_route_path(value: str, base_path: str) -> str:
    text = str(value or "").strip()
    trailing = text.endswith("/") and text != "/"
    raw = "/" + text.strip("/")
    if base_path and raw.startswith(base_path + "/"):
        raw = raw[len(base_path) :]
    if trailing and raw != "/" and not raw.endswith("/"):
        raw += "/"
    return raw


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()


def h1_text(html: str) -> str:
    match = re.search(r"<h1\b[^>]*>(.*?)</h1>", html, re.I | re.S)
    return clean_text(match.group(1)) if match else "Teknik rehber"


def latest_modified(html: str) -> str | None:
    match = re.search(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})"', html)
    return match.group(1) if match else None


def classify(canonical_path: str) -> dict:
    slug = canonical_path.casefold()
    if any(re.search(pattern, slug) for pattern in OFFICIAL_PATTERNS):
        return {
            "lane": "official",
            "primary": "/edas-bul",
            "primaryLabel": "Resmî EDAŞ kanalını bulun",
            "secondary": "/hesaplama/kesinti-gunlugu/",
            "secondaryLabel": "Kesinti ve kanıt kaydını oluşturun",
            "days": 30,
            "boundary": "Bu rota arıza veya başvuru kaydı almaz; affiliate bağlantısı gösterilmez.",
        }
    for pattern, tool, label in CONSUMER_RULES:
        if re.search(pattern, slug):
            return {
                "lane": "consumer",
                "primary": tool,
                "primaryLabel": label,
                "secondary": "/akilli-urun-secimi",
                "secondaryLabel": "Teknik seçimden sonra ürün merkezini açın",
                "days": 90,
                "boundary": "Ürün Merkezi bazı açıkça etiketli satış ortaklığı bağlantıları içerebilir. Mevcut ekipman yeterliyse satın almayın; fiyat, stok, puan ve garanti mağazanın güncel sayfasında doğrulanmalıdır.",
            }
    if "vpp" in slug or "toplayici" in slug:
        primary = "/kurumsal-elektrik-surekliligi-on-degerlendirme"
        primary_label = "VPP ve esneklik için teknik kapsam oluşturun"
    elif any(token in slug for token in ("ges", "pv-", "inverter", "batarya", "ev-sarj", "wallbox", "jenerator", "ups")):
        primary = "/hesaplama/teknik-devir-kabul-paketi/"
        primary_label = "Teknik devir ve kabul kapsamını oluşturun"
    else:
        primary = "/hesaplama/teknik-devir-kabul-paketi/"
        primary_label = "Ölçüm ve kabul kanıtlarını planlayın"
    return {
        "lane": "professional",
        "primary": primary,
        "primaryLabel": primary_label,
        "secondary": "/hesaplama/teknik-teklif-kapsam-karsilastirma/",
        "secondaryLabel": "Teklif kapsamlarını teknik olarak eşitleyin",
        "days": 60,
        "boundary": "Sabit tesisat, pano ve yüksek güçlü sistemlerde affiliate bağlantısı açılmaz; ölçüm, proje ve yetkili uzman sınırı korunur.",
    }


def lane_title(lane: str) -> str:
    return {
        "official": "Resmî kayıt ve kanıt yoluna ilerleyin",
        "consumer": "Satın almadan önce gerçek ihtiyacı doğrulayın",
        "professional": "Makaledeki bilgiyi ölçüm ve kabul adımına dönüştürün",
    }[lane]


def panel_html(canonical_path: str, title: str, route: dict, base_path: str) -> str:
    lane = route["lane"]
    primary = public_url(base_path, route["primary"])
    secondary = public_url(base_path, route["secondary"])
    followup = public_url(base_path, FOLLOWUP_PATH)
    disclosure_class = "alo186-disclosure" if lane == "consumer" else "alo186-boundary"
    return f'''<section class="alo186-next-step" {ARTICLE_MARKER} data-lane="{lane}">
  <span class="alo186-kicker">ALO186 sonraki adım · {escape(lane)}</span>
  <h2>{escape(lane_title(lane))}</h2>
  <p>Bu rehberi yalnız bilgi olarak bırakmayın. Önce ücretsiz teknik kontrolü tamamlayın; mevcut sistem yeterli ve güvenliyse değişim veya satın alma yapmayın.</p>
  <div class="alo186-actions">
    <a href="{escape(primary, quote=True)}" data-alo186-next-step-link data-lane="{lane}" data-action="primary">{escape(route['primaryLabel'])} →</a>
    <a class="secondary" href="{escape(secondary, quote=True)}" data-alo186-next-step-link data-lane="{lane}" data-action="secondary">{escape(route['secondaryLabel'])}</a>
    <button class="followup" type="button" data-alo186-followup-add data-path="{escape(canonical_path, quote=True)}" data-title="{escape(title, quote=True)}" data-lane="{lane}" data-days="{route['days']}">Takip listeme ekle</button>
    <a class="secondary" href="{escape(followup, quote=True)}" data-alo186-next-step-link data-lane="{lane}" data-action="followup-list">Takip listemi aç</a>
  </div>
  <div class="{disclosure_class}">{escape(route['boundary'])}</div>
  <span class="alo186-followup-status" role="status" aria-live="polite"></span>
</section>'''


def add_asset_refs(html: str, base_path: str) -> str:
    css = public_url(base_path, ASSET_CSS)
    js = public_url(base_path, ASSET_JS)
    if 'data-alo186-article-growth-css="true"' not in html:
        html = html.replace("</head>", f'<link rel="stylesheet" href="{css}" data-alo186-article-growth-css="true">\n</head>', 1)
    if 'data-alo186-article-growth-js="true"' not in html:
        html = html.replace("</body>", f'<script src="{js}" data-alo186-article-growth-js="true"></script>\n</body>', 1)
    return html


def inject_article(site: Path, route: dict, base_path: str) -> dict | None:
    canonical_path = canonical_route_path(route.get("canonicalPath"), base_path)
    target = site / canonical_path.strip("/") / "index.html"
    if not target.is_file():
        return None
    html = target.read_text(encoding="utf-8", errors="ignore")
    if 'data-alo186-content-alias="true"' in html or ARTICLE_MARKER in html:
        return None
    title = h1_text(html)
    classification = classify(canonical_path)
    panel = panel_html(canonical_path, title, classification, base_path)
    source_match = re.search(r"<section><h2>Kaynak", html, re.I)
    if source_match:
        html = html[: source_match.start()] + panel + html[source_match.start() :]
    else:
        html = html.replace("</article>", panel + "</article>", 1)
    html = add_asset_refs(html, base_path)
    target.write_text(html, encoding="utf-8")
    return {
        "canonicalPath": canonical_path,
        "lane": classification["lane"],
        "reviewDays": classification["days"],
        "modified": latest_modified(html),
    }


def copy_assets(site: Path) -> None:
    target = site / "assets"
    target.mkdir(parents=True, exist_ok=True)
    for name in ("article-growth.css", "article-growth.js"):
        source = DEPLOYMENT_ASSETS / name
        if not source.is_file():
            raise FileNotFoundError(f"Makale büyüme asseti eksik: {source}")
        (target / name).write_bytes(source.read_bytes())


def format_tr_date(value: str | None) -> str:
    if not value:
        return "Yayın paketiyle doğrulandı"
    try:
        parsed = date.fromisoformat(value[:10])
    except ValueError:
        return escape(value)
    months = ("Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık")
    return f"{parsed.day} {months[parsed.month - 1]} {parsed.year}"


def inject_inventory(site: Path, release: dict, records: list[dict], base_path: str) -> bool:
    path = site / PORTAL
    if not path.is_file():
        return False
    html = path.read_text(encoding="utf-8")
    if INVENTORY_MARKER in html:
        return False
    articles = sum(1 for route in release.get("routes", []) if route.get("type") == "article")
    tools = sum(1 for route in release.get("routes", []) if route.get("type") in {"tool", "calculator", "business-tool"})
    aliases = int((release.get("contentConsolidation") or {}).get("aliasCount") or 0)
    dates = sorted(record["modified"] for record in records if record.get("modified"))
    latest = dates[-1] if dates else str(release.get("generatedAt") or "")[:10]
    followup = public_url(base_path, FOLLOWUP_PATH)
    block = f'''<section class="alo186-inventory-strip" {INVENTORY_MARKER} aria-label="Güncel içerik ve araç envanteri">
  <article><strong>{articles}</strong><span>aktif canonical teknik rehber</span></article>
  <article><strong>{tools}</strong><span>karar aracı ve hesaplayıcı</span></article>
  <article><strong>{aliases}</strong><span>tek canonical içerikte birleştirilen tekrar niyeti</span></article>
  <article><strong>{escape(format_tr_date(latest))}</strong><span>en güncel içerik doğrulaması</span></article>
  <p class="alo186-inventory-note">Sayılar yayın envanterinden otomatik hesaplanır; elle yazılmış sayaç değildir. <a href="{escape(followup, quote=True)}">Teknik takip listenizi açın →</a></p>
</section>'''
    hero = re.search(r'<section\b[^>]*class=["\'][^"\']*\bhero\b[^"\']*["\'][^>]*>.*?</section>', html, re.I | re.S)
    if not hero:
        return False
    html = html[: hero.end()] + block + html[hero.end() :]
    html = add_asset_refs(html, base_path)
    path.write_text(html, encoding="utf-8")
    return True


def insert_grid_card(site: Path, relative: Path, base_path: str, gateway: bool) -> bool:
    path = site / relative
    if not path.is_file():
        return False
    html = path.read_text(encoding="utf-8")
    if ENTRY_MARKER in html:
        return False
    href = public_url(base_path, FOLLOWUP_PATH)
    if gateway:
        card = f'<a class="card alo186-followup-entry-card" {ENTRY_MARKER} href="{href}"><strong>Okuduğunuz teknik rehberleri takip planına alın</strong><p>Ölçüm, bakım ve yeniden kontrol tarihlerini yalnız tarayıcınızda saklayın.</p><span>Teknik Takip Listem →</span></a>'
    else:
        card = f'<a class="card alo186-followup-entry-card" {ENTRY_MARKER} href="{href}"><span class="tag">Yerel kayıt · 12 adım · JSON/ICS</span><h2>Teknik Takip Listem</h2><p>Rehberlerdeki sonraki adımları, satın almama veya teknik ölçüm kararını unutmadan takip edin.</p><b>Takip listesini aç →</b></a>'
    for match in re.finditer(r'<section\b[^>]*>', html, re.I):
        classes = re.search(r'class=["\']([^"\']*)["\']', match.group(0), re.I)
        if classes and "grid" in classes.group(1).split():
            html = html[: match.end()] + card + html[match.end() :]
            html = add_asset_refs(html, base_path)
            path.write_text(html, encoding="utf-8")
            return True
    return False


def add_offline(site: Path, base_path: str) -> list[str]:
    path = site / "sw.js"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        raise RuntimeError("Service worker CRITICAL rota dizisi bulunamadı")
    routes = json.loads(match.group(1))
    additions = [
        public_url(base_path, FOLLOWUP_PATH),
        public_url(base_path, ASSET_CSS),
        public_url(base_path, ASSET_JS),
    ]
    added: list[str] = []
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
    url = public_url(base_path, FOLLOWUP_PATH)
    if not any(isinstance(item, dict) and item.get("url") == url for item in shortcuts):
        shortcuts.append({"name": "Teknik Takip Listem", "short_name": "Teknik Takip", "url": url})
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, records: list[dict], base_path: str, cards: int, inventory: bool, offline: list[str]) -> dict:
    core_path = site / "alo186-release.json"
    release = json.loads(core_path.read_text(encoding="utf-8"))
    lanes = {"official": 0, "consumer": 0, "professional": 0}
    for record in records:
        lanes[record["lane"]] += 1
    metadata = {
        "version": VERSION,
        "articleCount": len(records),
        "laneCounts": lanes,
        "directAffiliateLinksAdded": 0,
        "consumerLaneDisclosureRequired": True,
        "followupRoute": FOLLOWUP_PATH,
        "followupLimit": 12,
        "followupTtlDays": 365,
        "rawNotesStored": False,
    }
    release["articleJourney"] = metadata
    core_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["articleJourney"] = {
            **metadata,
            "followupRoute": public_url(base_path, FOLLOWUP_PATH),
            "entryCardsInjected": cards,
            "inventoryStripInjected": inventory,
            "offlineAssetsAdded": offline,
        }
        pages["offlineCriticalRouteCount"] = int(pages.get("offlineCriticalRouteCount") or 0) + len(offline)
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return metadata


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    lines = [
        f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}"
        for item in sorted(candidate for candidate in site.rglob("*") if candidate.is_file())
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    if not (site / FOLLOWUP_PATH.strip("/") / "index.html").is_file():
        raise FileNotFoundError("Teknik takip listesi rotası artifactta eksik")
    copy_assets(site)
    release = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
    records: list[dict] = []
    for route in release.get("routes", []):
        if route.get("type") != "article":
            continue
        record = inject_article(site, route, base_path)
        if record:
            records.append(record)
    expected = sum(1 for route in release.get("routes", []) if route.get("type") == "article")
    if len(records) != expected:
        raise RuntimeError(f"Makale sonraki-adım kapsamı eksik: enjekte={len(records)}, beklenen={expected}")
    inventory = inject_inventory(site, release, records, base_path)
    cards = int(insert_grid_card(site, PORTAL, base_path, False)) + int(insert_grid_card(site, GATEWAY, base_path, True))
    offline = add_offline(site, base_path)
    update_manifest(site, base_path)
    metadata = update_release(site, records, base_path, cards, inventory, offline)
    recompute(site)
    return {
        "ok": True,
        "basePath": base_path,
        "articleCount": len(records),
        "laneCounts": metadata["laneCounts"],
        "inventoryStripInjected": inventory,
        "entryCardsInjected": cards,
        "offlineAssetsAdded": offline,
        "directAffiliateLinksAdded": 0,
        "followupRoute": public_url(base_path, FOLLOWUP_PATH),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 makalelerine güvenli sonraki-adım, dinamik envanter ve yerel takip yolculuğu ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
