from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROUTES = {
    "ev_cable": "/amazon-elektrik-urunleri/type-2-ev-sarj-kablosu-secimi",
    "ups_battery": "/amazon-elektrik-urunleri/ups-yedek-akusu-kartus-secimi",
    "outlet_tester": "/amazon-elektrik-urunleri/priz-rcd-test-cihazi-secimi",
}
SOURCES = {
    "ev_cable": "alo186/amazon-elektrik-urunleri/type-2-ev-sarj-kablosu-secimi/index.html",
    "ups_battery": "alo186/amazon-elektrik-urunleri/ups-yedek-akusu-kartus-secimi/index.html",
    "outlet_tester": "alo186/amazon-elektrik-urunleri/priz-rcd-test-cihazi-secimi/index.html",
}
PRODUCT_HUB = Path("amazon-elektrik-urunleri/index.html")
PRODUCT_CENTER = Path("akilli-urun-secimi/index.html")
PORTAL = Path("elektrik-portali/index.html")
CORPORATE = Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html")
HUB_MARKER = 'data-alo186-growth-run10-hub="true"'
CENTER_MARKER = 'data-alo186-growth-run10-center="true"'
PORTAL_MARKER = 'data-alo186-growth-run10-journey="true"'
CORPORATE_MARKER = 'data-alo186-growth-run10-service="true"'
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
SITEMAP_TAGS = {"urlset", "url", "loc", "lastmod", "changefreq", "priority"}


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def inject_product_hub(site: Path, base_path: str) -> int:
    path = site / PRODUCT_HUB
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if HUB_MARKER in text:
        return 0
    text = text.replace("7 özel rehber", "10 özel rehber")
    text = text.replace("yedi ayrı ihtiyacı", "on ayrı ihtiyacı")
    text = text.replace("Yedi ayrı ihtiyacı", "On ayrı ihtiyacı")
    text = text.replace("Yeni üç rehber, mevcut dört sayfanın arama niyetini tekrar etmez.", "Her rehber ayrı arama niyeti, teknik eşik ve ticari güven kapısı taşır.")
    cards = (
        f'<article class="card route-card" {HUB_MARKER}><span class="number">08</span><h3>Type 2 EV şarj kablosu</h3><p>Tek/üç faz, 16/32 A, 7,4/11/22 kW ve gerekli uzunluğu araç-wallbox zinciriyle doğrulayın.</p><ul><li>Önce ücretsiz uygunluk testi</li><li>Onboard charger sınırı</li><li>Yalnız doğrulama sonrası affiliate</li></ul><div class="actions"><a class="button primary" href="{public_url(base_path, ROUTES["ev_cable"])}">Type 2 kablo rehberini aç</a></div></article>'
        f'<article class="card route-card"><span class="number">09</span><h3>UPS yedek aküsü ve kartuşu</h3><p>Tam UPS modeli, kartuş kodu, DC gerilim, batarya adedi ve string bütünlüğünü doğrulayın.</p><ul><li>Eski-yeni batarya karıştırma yok</li><li>Runtime kanıtı</li><li>Profesyonel-only; doğrudan mağaza yok</li></ul><div class="actions"><a class="button primary" href="{public_url(base_path, ROUTES["ups_battery"])}">UPS batarya rehberini aç</a></div></article>'
        f'<article class="card route-card"><span class="number">10</span><h3>Priz ve RCD test cihazı</h3><p>LED kablolama göstergesi ile loop, izolasyon, RCD süre ve ramp testini aynı şey sanmayın.</p><ul><li>Ölçüm kapsamı ayrımı</li><li>Yanlış güveni önleme</li><li>Profesyonel-only; doğrudan mağaza yok</li></ul><div class="actions"><a class="button primary" href="{public_url(base_path, ROUTES["outlet_tester"])}">Test cihazı rehberini aç</a></div></article>'
    )
    anchor = '<article class="card route-card"><span class="number">07</span>'
    start = text.find(anchor)
    if start < 0:
        # Ürün merkezi daha yeni görev bazlı düzene geçtiyse eski sıralı kart
        # enjeksiyonunu güvenle atla. Eski büyüme koşusunun yeni merkezi bozmasına
        # veya tüm yayın artifactını durdurmasına izin verme.
        return 0
    article_end = text.find("</article>", start)
    grid_end = text.find("</div>", article_end + len("</article>"))
    if grid_end < 0:
        raise RuntimeError("Ürün rehberleri grid kapanışı bulunamadı")
    text = text[:grid_end] + cards + text[grid_end:]
    path.write_text(text, encoding="utf-8")
    return 3


def inject_product_center(site: Path, base_path: str) -> int:
    path = site / PRODUCT_CENTER
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if CENTER_MARKER in text:
        return 0
    section = f'''<section {CENTER_MARKER} style="max-width:1180px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#f5f8fd"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Yüksek niyet · güven kapısı · üç yeni yol</span><h2 style="color:#071631;margin:.4rem 0">Ürün aramasından önce teknik uygunluğu veya profesyonel ölçüm ihtiyacını ayırın.</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px"><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['ev_cable'])}"><strong>Type 2 EV kablosu</strong><br><span>Yalnız araç-wallbox-faz-akım doğrulamasından sonra affiliate yolu açılabilir.</span></a><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['ups_battery'])}"><strong>UPS batarya kartuşu</strong><br><span>Tam model ve string kapsamı bilinmiyorsa mağaza değil teknik inceleme açılır.</span></a><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['outlet_tester'])}"><strong>Priz/RCD test cihazı</strong><br><span>LED gösterge ile ölçümlü tesisat kabulünü birbirinden ayırın.</span></a></div><p style="margin-bottom:0;color:#58677c"><strong>Satış ortaklığı sınırı:</strong> Bu bölüm doğrudan mağaza bağlantısı içermez. Fiyat, stok, puan, satıcı ve garanti gösterilmez; mevcut çözüm yeterliyse satın almama geçerlidir.</p></section>'''
    if "</main>" not in text:
        raise RuntimeError("Akıllı ürün merkezi main kapanışı bulunamadı")
    path.write_text(text.replace("</main>", section + "</main>", 1), encoding="utf-8")
    return 1


def inject_portal(site: Path, base_path: str) -> int:
    path = site / PORTAL
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if PORTAL_MARKER in text:
        return 0
    section = f'''<section {PORTAL_MARKER} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#fff"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Arama niyetinden güvenli dönüşüme</span><h2 style="color:#071631;margin:.4rem 0">EV kablosu, UPS bataryası ve priz testi için alışverişten önce doğru karar yolunu açın.</h2><p>Type 2 kabloda doğrulanmış tüketici ürünü yolu; UPS bataryası ve priz/RCD testinde ise model veya ölçüm yetkinliği nedeniyle profesyonel-only yol kullanılır.</p><div style="display:flex;flex-wrap:wrap;gap:10px"><a href="{public_url(base_path, ROUTES['ev_cable'])}">EV kablosunu doğrula →</a><a href="{public_url(base_path, ROUTES['ups_battery'])}">UPS batarya kapsamını doğrula →</a><a href="{public_url(base_path, ROUTES['outlet_tester'])}">Priz testi sınırını öğren →</a></div></section>'''
    if "</main>" not in text:
        return 0
    path.write_text(text.replace("</main>", section + "</main>", 1), encoding="utf-8")
    return 1


def inject_corporate(site: Path, base_path: str) -> int:
    path = site / CORPORATE
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if CORPORATE_MARKER in text:
        return 0
    section = f'''<section class="specialist-services" {CORPORATE_MARKER}><div class="specialist-heading"><span class="eyebrow">Ürün talebini ölçülebilir hizmet kapsamına dönüştürün</span><h2>Yanlış batarya veya test cihazı almak yerine model ve ölçüm kapsamını doğrulayın.</h2><p>UPS batarya kartuşunda tam model/string eşleşmesi; priz ve RCD testinde kalibre cihaz, test yöntemi ve kapanış raporu hazırlanır. Ücretli hizmet zorunlu değildir.</p></div><div class="service-link-grid"><a class="service-link-card" href="{public_url(base_path, ROUTES['ups_battery'])}"><span>Model bazlı inceleme</span><h3>UPS batarya değişim kapsamı</h3><p>Runtime, tam model, kartuş kodu, set bütünlüğü ve güvenli çalışma planını doğrulayın.</p><b>Batarya karar yolunu aç →</b></a><a class="service-link-card" href="{public_url(base_path, ROUTES['outlet_tester'])}"><span>Ölçüm bazlı inceleme</span><h3>Priz ve RCD kabul kapsamı</h3><p>Loop, PEFC, RCD süre/ramp, izolasyon ve rapor ihtiyacını basit LED göstergeden ayırın.</p><b>Ölçüm kapsamını aç →</b></a></div></section>'''
    marker = '<section class="request-grid">'
    if marker in text:
        text = text.replace(marker, section + marker, 1)
    elif "</main>" in text:
        text = text.replace("</main>", section + "</main>", 1)
    else:
        return 0
    path.write_text(text, encoding="utf-8")
    return 1


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _load_or_recover_sitemap(text: str) -> tuple[ET.Element, bool]:
    try:
        root = ET.fromstring(text)
        if _local_name(root.tag) != "urlset":
            raise ET.ParseError("Sitemap kökü urlset değil")
        return root, False
    except ET.ParseError:
        # Eski büyüme betikleri XML'e metin eklediği için tek bir bozuk etiket
        # tüm yayını durdurabiliyordu. Geçerli loc kayıtlarını kurtarıp güvenli
        # ve ad alanı uyumlu bir sitemap ağacı kur.
        root = ET.Element(f"{{{SITEMAP_NS}}}urlset")
        seen: set[str] = set()
        for raw_loc in re.findall(r"<loc\b[^>]*>(.*?)</loc>", text, re.I | re.S):
            loc = html.unescape(re.sub(r"<[^>]+>", "", raw_loc)).strip()
            loc = loc.replace("https://www.alo186.com", "https://alo186.com")
            if not loc or loc in seen:
                continue
            url_node = ET.SubElement(root, f"{{{SITEMAP_NS}}}url")
            loc_node = ET.SubElement(url_node, f"{{{SITEMAP_NS}}}loc")
            loc_node.text = loc
            seen.add(loc)
        return root, True


def append_sitemap(site: Path) -> None:
    path = site / "sitemap.xml"
    if not path.is_file():
        return
    root, _recovered = _load_or_recover_sitemap(path.read_text(encoding="utf-8"))
    namespace = root.tag.split("}", 1)[0].lstrip("{") if "}" in root.tag else SITEMAP_NS
    ns = f"{{{namespace}}}"

    # Ad alanı taşımayan eski ekleri de tek ve standart sitemap ad alanına al.
    for element in root.iter():
        if isinstance(element.tag, str) and _local_name(element.tag) in SITEMAP_TAGS:
            element.tag = f"{ns}{_local_name(element.tag)}"

    present: set[str] = set()
    for url_node in root.findall(f"{ns}url"):
        loc_node = url_node.find(f"{ns}loc")
        if loc_node is None or not loc_node.text:
            continue
        loc_node.text = loc_node.text.strip().replace("https://www.alo186.com", "https://alo186.com")
        present.add(loc_node.text)

    for route in ROUTES.values():
        loc = f"https://alo186.com{route}"
        if loc in present:
            continue
        url_node = ET.SubElement(root, f"{ns}url")
        loc_node = ET.SubElement(url_node, f"{ns}loc")
        loc_node.text = loc
        present.add(loc)

    ET.register_namespace("", namespace)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)
    # Yazılan dosyanın sonraki büyüme adımlarına geçmeden parse edilebilir
    # olduğunu garanti et.
    ET.parse(path)


def append_search(site: Path, base_path: str) -> None:
    path = site / "arama/search-index.json"
    if not path.is_file():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.setdefault("entries", [])
    known = {item.get("canonicalPath") for item in entries if isinstance(item, dict)}
    additions = {
        "ev_cable": ("Type 2 EV Şarj Kablosu Seçimi", "Tek/üç faz, 16/32 A, 7,4/11/22 kW ve kablo uzunluğu uygunluğu."),
        "ups_battery": ("UPS Yedek Aküsü ve Kartuş Seçimi", "Tam UPS modeli, kartuş kodu, DC gerilim, batarya adedi ve string bütünlüğü."),
        "outlet_tester": ("Priz ve RCD Test Cihazı Seçimi", "LED priz tester, loop ölçümü, RCD açma süresi ve ramp testinin görev ayrımı."),
    }
    for key, route in ROUTES.items():
        if route in known:
            continue
        title, description = additions[key]
        entries.append({"canonicalPath": route, "url": public_url(base_path, route), "title": title, "description": description, "bucket": "commercial-guide", "keywords": [key, "elektrik güvenliği", "uygunluk", "satın almama"]})
    data["entryCount"] = len(entries)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, injected: int) -> None:
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    routes = core.setdefault("routes", [])
    known = {item.get("canonicalPath") for item in routes if isinstance(item, dict)}
    for key, route in ROUTES.items():
        if route not in known:
            routes.append({"canonicalPath": route, "source": SOURCES[key], "type": "commercial-guide"})
    core["routeCount"] = len(routes)
    core["growthRun10"] = {
        "version": 1,
        "routes": list(ROUTES.values()),
        "entryPointsInjected": injected,
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "qualifiedAffiliateCategories": ["ev_cable"],
        "professionalOnlyCategories": ["ups_battery", "outlet_tester"],
        "unverifiedCommercialFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "affiliateDisclosureRequired": True,
        "officialApprovalClaimed": False,
    }
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["routeCount"] = len(routes)
        pages["growthRun10"] = {
            "version": 1,
            "basePath": base_path,
            "routes": [public_url(base_path, route) for route in ROUTES.values()],
            "entryPointsInjected": injected,
            "directAffiliateLinksAdded": 0,
            "professionalOnlyCategories": ["ups_battery", "outlet_tester"],
        }
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
    for route in ROUTES.values():
        target = site / route.strip("/") / "index.html"
        if not target.is_file():
            raise FileNotFoundError(f"Growth run10 rotası artifactta eksik: {target}")
    injected = inject_product_hub(site, base_path)
    injected += inject_product_center(site, base_path)
    injected += inject_portal(site, base_path)
    injected += inject_corporate(site, base_path)
    append_sitemap(site)
    append_search(site, base_path)
    update_release(site, base_path, injected)
    recompute(site)
    return {
        "ok": True,
        "basePath": base_path,
        "routes": [public_url(base_path, route) for route in ROUTES.values()],
        "entryPointsInjected": injected,
        "directAffiliateLinksAdded": 0,
        "qualifiedAffiliateCategories": ["ev_cable"],
        "professionalOnlyCategories": ["ups_battery", "outlet_tester"],
        "rawPersonalDataCollected": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 yüksek niyetli EV kablosu, UPS bataryası ve priz/RCD test rehberlerini yayın artifactına ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
