from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROUTES = {
    "maintenance": "/hesaplama/elektrik-bakim-takvimi/",
    "service": "/hizmet-secici/",
    "aftercare": "/hesaplama/urun-sonrasi-guvenlik-kontrolu/",
}
HUB = Path("hesaplama/index.html")
PORTAL = Path("elektrik-portali/index.html")
PRODUCT = Path("amazon-elektrik-urunleri/index.html")
CORPORATE = Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html")
HUB_MARKER = 'data-alo186-retention-tools="true"'
PORTAL_MARKER = 'data-alo186-retention-growth="true"'
PRODUCT_MARKER = 'data-alo186-aftercare-entry="true"'
SERVICE_MARKER = 'data-alo186-service-fit-entry="true"'


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def inject_hub(site: Path, base_path: str) -> int:
    path = site / HUB
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if HUB_MARKER in text:
        return 0
    cards = (
        f'<a class="tool-card" {HUB_MARKER} href="{public_url(base_path, ROUTES["maintenance"])}"><span class="eyebrow">Yerel kayıt · JSON · ICS · tekrar kontrol</span><h2>Elektrik Bakım Takvimi</h2><p>RCD, SPD, UPS, jeneratör, topraklama, GES, batarya, EV ve güç kalitesi için bakım ve kanıt tarihlerini kişisel veri vermeden planlayın.</p><b>Bakım takvimini oluştur →</b></a>'
        f'<a class="tool-card" href="{public_url(base_path, ROUTES["aftercare"])}"><span class="eyebrow">Satıştan sonra güvenlik · satın almama</span><h2>Ürün Sonrası Güvenlik Kontrolü</h2><p>Powerbank, mini UPS, güç istasyonu, akıllı priz, grup priz, acil aydınlatma ve duman alarmını kullanım sonrası yeniden değerlendirin.</p><b>Güvenlik kontrolünü aç →</b></a>'
    )
    marker = '<section id="araclar" class="tool-grid">'
    if marker not in text:
        raise RuntimeError("Hesaplama araç grid başlangıcı bulunamadı")
    text = text.replace(marker, marker + cards, 1)
    path.write_text(text, encoding="utf-8")
    return 2


def inject_portal(site: Path, base_path: str) -> int:
    path = site / PORTAL
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if PORTAL_MARKER in text:
        return 0
    section = f'''<section {PORTAL_MARKER} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#f5f8fd"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Tekrar ziyaret ve güvenli dönüşüm</span><h2 style="color:#071631;margin:.4rem 0">Tek seferlik cevap yerine bakım, doğru hizmet ve ürün sonrası kontrol.</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px"><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['maintenance'])}"><strong>Bakım Takvimi</strong><br><span>Kontrol ve kanıt tarihlerini planlayın.</span></a><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['service'])}"><strong>Hangi Hizmet?</strong><br><span>Ücretsiz araç mı, resmî kanal mı, uzman inceleme mi?</span></a><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['aftercare'])}"><strong>Ürün Sonrası Kontrol</strong><br><span>Mevcut ürün güvenliyse yeni ürün almayın.</span></a></div></section>'''
    if "</main>" not in text:
        raise RuntimeError("Elektrik portalı main kapanışı bulunamadı")
    text = text.replace("</main>", section + "</main>", 1)
    path.write_text(text, encoding="utf-8")
    return 1


def inject_product(site: Path, base_path: str) -> int:
    path = site / PRODUCT
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if PRODUCT_MARKER in text:
        return 0
    section = f'''<section class="section" {PRODUCT_MARKER} aria-labelledby="aftercareTitle"><span class="eyebrow">Satıştan sonra güven</span><h2 id="aftercareTitle">Ürün seçimi satın alma anında bitmez.</h2><p class="lead">Mevcut ürününüzün ısınma, hasar, performans, uyum ve bakım durumunu yeniden kontrol edin. Araç doğrudan mağaza bağlantısı göstermez; sorun yoksa satın almama sonucu verir.</p><div class="button-row"><a class="button primary" href="{public_url(base_path, ROUTES['aftercare'])}">Ürün sonrası güvenlik kontrolünü aç</a><a class="button secondary" href="{public_url(base_path, ROUTES['maintenance'])}">Bakım takvimine ekle</a></div></section>'''
    text = text.replace("</main>", section + "</main>", 1)
    path.write_text(text, encoding="utf-8")
    return 1


def inject_service(site: Path, base_path: str) -> int:
    path = site / CORPORATE
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if SERVICE_MARKER in text:
        return 0
    section = f'''<section {SERVICE_MARKER} class="specialist-services" aria-labelledby="service-fit-title"><div class="specialist-heading"><span class="eyebrow">Ücretli hizmetten önce uygunluk</span><h2 id="service-fit-title">Her teknik sorun ücretli hizmet gerektirmez.</h2><p>Resmî kanal, ücretsiz araç, belge hazırlığı veya ücretli profesyonel hizmet arasındaki doğru yolu kişisel veri vermeden belirleyin.</p></div><div class="service-link-grid"><a class="service-link-card" href="{public_url(base_path, ROUTES['service'])}"><span>Baskısız hizmet seçimi</span><h3>Hangi Elektrik Hizmeti Gerekli?</h3><p>Risk, karar aşaması ve kanıt durumuna göre ücretsiz yol veya uygun profesyonel kapsamı görün.</p><b>Hizmet seçiciyi aç →</b></a><a class="service-link-card" href="{public_url(base_path, ROUTES['maintenance'])}"><span>Tekrar ziyaret nedeni</span><h3>Elektrik Bakım Takvimi</h3><p>Bakım, test ve kanıt yenileme tarihlerini JSON ve ICS ile planlayın.</p><b>Takvimi oluştur →</b></a><a class="service-link-card" href="{public_url(base_path, ROUTES['aftercare'])}"><span>Satış sonrası güven</span><h3>Ürün Sonrası Kontrol</h3><p>Mevcut ürün yeterliyse değişim veya yeni satın alma yapmayın.</p><b>Kontrolü aç →</b></a></div></section>'''
    marker = '<section class="request-grid">'
    if marker in text:
        text = text.replace(marker, section + marker, 1)
    else:
        text = text.replace("</main>", section + "</main>", 1)
    path.write_text(text, encoding="utf-8")
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
    added: list[str] = []
    for route in ROUTES.values():
        url = public_url(base_path, route)
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
        {"name": "Elektrik Bakım Takvimi", "short_name": "Bakım Takvimi", "url": public_url(base_path, ROUTES["maintenance"])},
        {"name": "Hangi Elektrik Hizmeti?", "short_name": "Hizmet Seçici", "url": public_url(base_path, ROUTES["service"])},
    ]
    known = {item.get("url") for item in shortcuts if isinstance(item, dict)}
    shortcuts.extend(item for item in additions if item["url"] not in known)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, injected: int, offline: list[str]) -> None:
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    core["retentionGrowth"] = {
        "version": 1,
        "routes": ROUTES,
        "entryPointsInjected": injected,
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "unverifiedCommercialFieldsUsed": [],
        "repeatVisitReasons": ["maintenance_due", "aftercare_recheck", "evidence_refresh"],
        "noPaidServiceResultSupported": True,
    }
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["retentionGrowth"] = {
            "version": 1,
            "routes": {key: public_url(base_path, value) for key, value in ROUTES.items()},
            "entryPointsInjected": injected,
            "offlineRoutesAdded": offline,
            "rawPersonalDataCollected": False,
        }
        pages["offlineCriticalRouteCount"] = int(pages.get("offlineCriticalRouteCount") or 0) + len(offline)
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    lines = [f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}" for item in sorted(p for p in site.rglob("*") if p.is_file())]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    for route in ROUTES.values():
        target = site / route.strip("/") / "index.html"
        if not target.is_file():
            raise FileNotFoundError(f"Retention growth rotası artifactta eksik: {target}")
    injected = inject_hub(site, base_path)
    injected += inject_portal(site, base_path)
    injected += inject_product(site, base_path)
    injected += inject_service(site, base_path)
    offline = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_release(site, base_path, injected, offline)
    recompute(site)
    return {
        "ok": True,
        "basePath": base_path,
        "routes": {key: public_url(base_path, value) for key, value in ROUTES.items()},
        "entryPointsInjected": injected,
        "offlineRoutesAdded": offline,
        "directAffiliateLinksAdded": 0,
        "rawPersonalDataCollected": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 bakım, hizmet uygunluğu ve ürün sonrası tekrar ziyaret döngüsünü yayın artifactına ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
