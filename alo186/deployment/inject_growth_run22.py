from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROUTE = "/hesaplama/aydinlatma-ihtiyac-ve-ampul-uygunluk/"
CANONICAL = "https://www.alo186.com" + ROUTE
SOURCE = "alo186/hesaplama/aydinlatma-ihtiyac-ve-ampul-uygunluk/index.html"
ENTRY_MARKER = 'data-alo186-growth-run22-entry="true"'
DEEP_LINK_MARKER = 'data-alo186-lighting-deeplink-run22="true"'
TARGETS = {
    Path("hesaplama/index.html"): ("Aydınlatma ihtiyacını ürün almadan sınıflandırın", "Mevcut ampul yeterliyse kullanmaya devam edin; yalnız gerçek eksikte lümen, Kelvin, CRI, duy ve ortam koşullarına göre kategori açın."),
    Path("elektrik-portali/index.html"): ("Ampul wattına değil görevine bakın", "Salon, çalışma, koridor ve dış alan ihtiyacını mevcut ürünle karşılaştırın; güvenli ürün için satın almama sonucu alın."),
    Path("akilli-urun-secimi/index.html"): ("Aydınlatma kategorisini teknik kanıtla açın", "Lümen, Kelvin, dimmer, duy ve ortam etiketi bilinmeden ürün bağlantısı açılmaz."),
    Path("amazon-elektrik-urunleri/index.html"): ("Aydınlatma ürünlerini doğru karta daraltın", "Yedi aydınlatma ürün yolundan yalnız ihtiyacınıza uyan kartı açın; mevcut ürün yeterliyse satın almayın."),
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
            "title": "Aydınlatma İhtiyacı ve Mevcut Ampul Uygunluk Merkezi",
            "description": "Mevcut ampul veya armatürün yeterliliğini lümen, Kelvin, CRI, duy, dimmer ve ortam koşullarıyla değerlendirin; yalnız gerçek eksikte kategoriye ilerleyin.",
            "bucket": "calculator",
            "keywords": [
                "kaç lümen ampul almalıyım",
                "salon için kaç kelvin",
                "e27 led ampul seçimi",
                "sensörlü ampul mü armatür mü",
                "led ampul dimmer uyumu",
                "dış mekan projektör ip sınıfı",
                "led ampul titriyor ısınıyor",
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
        shortcuts.append({"name": "Aydınlatma Uygunluk Merkezi", "short_name": "Aydınlatma Seçimi", "url": url})
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
        card = f'<section class="content-section" {ENTRY_MARKER}><div class="panel"><span class="eyebrow">Lümen · Kelvin · CRI · mevcut ürün</span><h2>{title}</h2><p>{description}</p><div class="actions"><a class="btn btn-secondary" href="{href}">Aydınlatma uygunluk merkezini aç</a></div><small>Doğrudan mağaza bağlantısı yoktur; kategori yalnız güvenli ve doğrulanmış eksikte açılır.</small></div></section>'
        text = text.replace("</main>", card + "</main>", 1) if "</main>" in text else text + card
        path.write_text(text, encoding="utf-8")
        count += 1
    return count


def inject_lighting_deeplink(site: Path) -> bool:
    path = site / "amazon-elektrik-urunleri/index.html"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    if DEEP_LINK_MARKER in text:
        return False
    script = r'''<script data-alo186-lighting-deeplink-run22="true">(function(){'use strict';const map={
'e27-led-ampul':'E27 LED ampul','sensorlu-led-ampul':'Sensörlü LED ampul','sensorlu-tavan-armaturu':'Sensörlü tavan armatürü','dis-mekan-led-projektor':'Dış mekân LED projektör','solar-dis-mekan-lambasi':'Solar dış mekân lambası','ayarlanabilir-calisma-lambasi':'Ayarlanabilir çalışma lambası','24v-led-serit-seti':'24 V LED şerit seti'};
const params=new URLSearchParams(location.search),slug=params.get('kategori');if(!slug||!map[slug])return;const wanted=map[slug].toLocaleLowerCase('tr-TR');const nodes=[...document.querySelectorAll('article,section,li,.card')];const target=nodes.find(node=>(node.textContent||'').toLocaleLowerCase('tr-TR').includes(wanted));if(!target)return;target.dataset.alo186LightingTarget='true';target.setAttribute('tabindex','-1');target.scrollIntoView({behavior:'smooth',block:'center'});target.focus({preventScroll:true});const note=document.createElement('div');note.className='affiliate-disclosure';note.dataset.alo186LightingQualification='true';note.innerHTML='<strong>Nitelikli aydınlatma yönlendirmesi:</strong> Bu karta lümen, Kelvin, CRI, bağlantı ve mevcut ürün kontrolünden sonra ulaştınız. Mevcut ürün yeterliyse satın alma gerekli değildir. Aşağıdaki mağaza bağlantıları Amazon satış ortaklığı bağlantılarıdır.';target.insertBefore(note,target.firstChild);})();</script>'''
    text = text.replace("</body>", script + "</body>", 1)
    path.write_text(text, encoding="utf-8")
    return True


def update_release(site: Path, base_path: str, entries: int, deeplink: bool, offline: bool) -> None:
    path = site / "alo186-release.json"
    release = json.loads(path.read_text(encoding="utf-8"))
    routes = release.setdefault("routes", [])
    if not any(item.get("canonicalPath") == ROUTE for item in routes if isinstance(item, dict)):
        routes.append({"canonicalPath": ROUTE, "source": SOURCE, "type": "tool"})
    release["routeCount"] = len(routes)
    release["lightingSuitabilityCenter"] = {
        "version": 1,
        "basePath": base_path,
        "route": public_url(base_path, ROUTE),
        "entryCardsInjected": entries,
        "qualifiedCategoryDeepLink": deeplink,
        "offline": True,
        "recordLimit": 8,
        "recordTtlDays": 365,
        "reviewDays": 180,
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
        payload["lightingSuitabilityCenter"] = release["lightingSuitabilityCenter"]
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
    required = site / "hesaplama/aydinlatma-ihtiyac-ve-ampul-uygunluk/index.html"
    if not required.is_file():
        raise FileNotFoundError(f"Aydınlatma uygunluk rotası artifactta eksik: {required}")
    append_sitemap(site)
    append_search(site, base_path)
    entries = insert_entries(site, base_path)
    deeplink = inject_lighting_deeplink(site)
    offline = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_release(site, base_path, entries, deeplink, offline)
    recompute(site)
    return {"ok": True, "route": public_url(base_path, ROUTE), "entries": entries, "qualifiedDeepLink": deeplink, "offline": True}
