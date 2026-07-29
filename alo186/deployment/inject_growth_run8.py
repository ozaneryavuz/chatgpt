from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROUTES = {
    "vpp": "/hesaplama/vpp-esnek-yuk-hazirlik/",
    "ev": "/hesaplama/apartman-site-ev-sarj-karar-paketi/",
    "runtime": "/hesaplama/yedek-guc-runtime-saglik-gunlugu/",
}
SOURCES = {
    "vpp": "alo186/hesaplama/vpp-esnek-yuk-hazirlik/index.html",
    "ev": "alo186/hesaplama/apartman-site-ev-sarj-karar-paketi/index.html",
    "runtime": "alo186/hesaplama/yedek-guc-runtime-saglik-gunlugu/index.html",
}
HUB = Path("hesaplama/index.html")
PORTAL = Path("elektrik-portali/index.html")
PRODUCT = Path("amazon-elektrik-urunleri/index.html")
BUSINESS = Path("kurumsal-on-degerlendirme/index.html")
HUB_MARKER = 'data-alo186-growth-run8-tools="true"'
PORTAL_MARKER = 'data-alo186-growth-run8-journey="true"'
PRODUCT_MARKER = 'data-alo186-growth-run8-affiliate="true"'
BUSINESS_MARKER = 'data-alo186-growth-run8-business="true"'


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
        f'<a class="tool-card" {HUB_MARKER} href="{public_url(base_path, ROUTES["vpp"])}"><span class="eyebrow">VPP · telemetri · kontrol · gelir garantisi yok</span><h2>VPP ve Esnek Yük Hazırlığı</h2><p>GES, batarya, EV ve esnek yükleri veri, kontrol ve kullanılabilirlik kanıtıyla ön değerlendirin.</p><b>Hazırlık ön dosyasını oluştur →</b></a>'
        f'<a class="tool-card" href="{public_url(base_path, ROUTES["ev"])}"><span class="eyebrow">Otopark · besleme · ölçüm · yönetim</span><h2>Apartman ve Site EV Şarj Karar Paketi</h2><p>Wallbox teklifinden önce park, kapasite, gider paylaşımı, proje ve kabul gündemini hazırlayın.</p><b>Karar paketini oluştur →</b></a>'
        f'<a class="tool-card" href="{public_url(base_path, ROUTES["runtime"])}"><span class="eyebrow">Runtime · batarya eğilimi · 540 gün</span><h2>Yedek Güç Sağlık Günlüğü</h2><p>Mini UPS, UPS ve güç istasyonunda çalışma süresini karşılaştırın; ihtiyaç yoksa satın almayın.</p><b>Runtime kaydı ekle →</b></a>'
    )
    marker = '<section id="araclar" class="tool-grid">'
    if marker not in text:
        raise RuntimeError("Hesaplama merkezi araç grid başlangıcı bulunamadı")
    path.write_text(text.replace(marker, marker + cards, 1), encoding="utf-8")
    return 3


def inject_portal(site: Path, base_path: str) -> int:
    path = site / PORTAL
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if PORTAL_MARKER in text:
        return 0
    section = f'''<section {PORTAL_MARKER} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#f5f8fd"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Kanıtla hazırla · doğru kapsama ilerle · tekrar ölç</span><h2 style="color:#071631;margin:.4rem 0">Yüksek değerli enerji kararlarını ürün veya gelir vaadiyle değil, teknik hazırlıkla başlatın.</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px"><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['vpp'])}"><strong>VPP Hazırlık Ön Dosyası</strong><br><span>Ölçüm, telemetri, kontrol ve kullanılabilirlik boşluklarını görün.</span></a><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['ev'])}"><strong>EV Şarj Karar Paketi</strong><br><span>Apartman ve site için yönetim gündemi ile teknik keşfi ayırın.</span></a><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['runtime'])}"><strong>Runtime Sağlık Günlüğü</strong><br><span>Mevcut yedek gücü aynı yükte izleyin; yeterliyse değiştirmeyin.</span></a></div></section>'''
    if "</main>" not in text:
        raise RuntimeError("Elektrik portalı main kapanışı bulunamadı")
    path.write_text(text.replace("</main>", section + "</main>", 1), encoding="utf-8")
    return 1


def inject_product(site: Path, base_path: str) -> int:
    path = site / PRODUCT
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if PRODUCT_MARKER in text:
        return 0
    section = f'''<section class="section" {PRODUCT_MARKER}><span class="eyebrow">Satış sonrası kanıt · tekrar ziyaret</span><h2>Mini UPS veya güç istasyonunu yalnız yaşına bakarak değiştirmeyin.</h2><p class="lead">Runtime günlüğü aynı yük ve şarj koşulundaki testleri karşılaştırır. Süre ihtiyacı karşılanıyorsa satın almama sonucu korunur; fiziksel güvenlik belirtisinde bütün ticari yollar kapanır.</p><div class="actions"><a class="button secondary" href="{public_url(base_path, ROUTES['runtime'])}">Runtime sağlık günlüğünü aç</a></div><div class="affiliate-disclosure"><strong>Reklam / satış ortaklığı sınırı:</strong> Yalnız doğrulanmış ve tekrarlayan performans açığında teknik kategori rehberi gösterilebilir. Sonraki rehber Amazon satış ortaklığı bağlantıları içerebilir; fiyat, stok, puan, satıcı ve garanti yalnız mağazanın güncel sayfasında doğrulanır.</div></section>'''
    if "</main>" not in text:
        raise RuntimeError("Amazon ürün merkezi main kapanışı bulunamadı")
    path.write_text(text.replace("</main>", section + "</main>", 1), encoding="utf-8")
    return 1


def inject_business(site: Path, base_path: str) -> int:
    path = site / BUSINESS
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if BUSINESS_MARKER in text:
        return 0
    section = f'''<section {BUSINESS_MARKER} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#fff"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Ücretli hizmetten önce ücretsiz kapsam hazırlığı</span><h2 style="color:#071631;margin:.4rem 0">VPP veya ortak EV şarj fikrini teknik ön dosyaya dönüştürün.</h2><p>VPP aracında veri ve kontrol boşluklarını; EV aracında yönetim, kapasite, ölçüm ve kabul gündemini hazırlayın. Sonuç yeterliyse mevcut altyapıyla ilerleme veya satın almama seçeneği korunur.</p><div style="display:flex;flex-wrap:wrap;gap:10px"><a href="{public_url(base_path, ROUTES['vpp'])}">VPP hazırlığını değerlendir →</a><a href="{public_url(base_path, ROUTES['ev'])}">EV karar paketini oluştur →</a></div></section>'''
    if "</main>" not in text:
        return 0
    path.write_text(text.replace("</main>", section + "</main>", 1), encoding="utf-8")
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
        {"name": "VPP ve Esnek Yük Hazırlığı", "short_name": "VPP Hazırlık", "url": public_url(base_path, ROUTES["vpp"])},
        {"name": "Yedek Güç Runtime Sağlığı", "short_name": "Runtime Günlüğü", "url": public_url(base_path, ROUTES["runtime"])},
    ]
    for item in additions:
        if not any(isinstance(existing, dict) and existing.get("url") == item["url"] for existing in shortcuts):
            shortcuts.append(item)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, cards: int, offline: list[str]) -> None:
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    routes = core.setdefault("routes", [])
    existing = {item.get("canonicalPath") for item in routes if isinstance(item, dict)}
    for key, route in ROUTES.items():
        if route not in existing:
            routes.append({"canonicalPath": route, "source": SOURCES[key], "type": "calculator" if key == "runtime" else "business-tool"})
    core["routeCount"] = len(routes)
    core["growthRun8"] = {
        "version": 1,
        "routes": list(ROUTES.values()),
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "unverifiedCommercialFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "aggregatorRanking": False,
        "incomeEstimatePublished": False,
        "officialApprovalClaimed": False,
        "vppReviewDays": 30,
        "evReviewDays": 45,
        "runtimeJournalLocalOnly": True,
        "runtimeJournalTtlDays": 540,
        "paidReferralDisclosureRequired": True,
        "fixedInstallationDirectAffiliate": False,
    }
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["routeCount"] = len(routes)
        pages["growthRun8"] = {
            "version": 1,
            "basePath": base_path,
            "routes": [public_url(base_path, route) for route in ROUTES.values()],
            "entryCardsInjected": cards,
            "offlineAdded": offline,
            "rawPersonalDataCollected": False,
            "directAffiliateLinksAdded": 0,
            "runtimeJournalTtlDays": 540,
        }
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_sitemap(site: Path) -> None:
    path = site / "sitemap.xml"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    for route in ROUTES.values():
        loc = f"https://www.alo186.com{route}"
        if f"<loc>{loc}</loc>" not in text:
            text = text.replace("</urlset>", f"<url><loc>{loc}</loc></url></urlset>", 1)
    path.write_text(text, encoding="utf-8")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    files = sorted(item for item in site.rglob("*") if item.is_file())
    path.write_text(
        "\n".join(f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}" for item in files) + "\n",
        encoding="utf-8",
    )


def run(site: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    for key, route in ROUTES.items():
        target = site / route.strip("/") / "index.html"
        if not target.is_file():
            raise FileNotFoundError(f"Growth run8 rotası artifactta eksik: {key}: {target}")
    cards = inject_hub(site, base_path)
    cards += inject_portal(site, base_path)
    cards += inject_product(site, base_path)
    cards += inject_business(site, base_path)
    append_sitemap(site)
    offline = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_release(site, base_path, cards, offline)
    recompute(site)
    return {
        "ok": True,
        "basePath": base_path,
        "routes": [public_url(base_path, route) for route in ROUTES.values()],
        "entryCardsInjected": cards,
        "offlineAdded": offline,
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "noBuyOutcomePreserved": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
