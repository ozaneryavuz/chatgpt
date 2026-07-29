from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROUTES = {
    "topics": "/konu-takip-merkezi/",
    "evidence": "/hesaplama/elektrik-kanit-envanteri/",
    "spec": "/hesaplama/teknik-sartname-talep-paketi/",
}
HUB = Path("hesaplama/index.html")
PORTAL = Path("elektrik-portali/index.html")
GATEWAY = Path("index.html")
CORPORATE = Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html")
HUB_MARKER = 'data-alo186-growth-run6-tools="true"'
PORTAL_MARKER = 'data-alo186-growth-run6-retention="true"'
GATEWAY_MARKER = 'data-alo186-growth-run6-gateway="true"'
CORPORATE_MARKER = 'data-alo186-growth-run6-spec="true"'


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
        f'<a class="tool-card" {HUB_MARKER} href="{public_url(base_path, ROUTES["evidence"])}"><span class="eyebrow">Yerel envanter · JSON · kanıt tazeliği</span><h2>Elektrik Kanıt Envanteri</h2><p>Test, bakım, ölçüm, devreye alma ve as-built kayıtlarının eksik veya yeniden kontrol edilmesi gerekenlerini dosya yüklemeden izleyin.</p><b>Kanıt envanterini aç →</b></a>'
        f'<a class="tool-card" href="{public_url(base_path, ROUTES["spec"])}"><span class="eyebrow">Marka yok · fiyat yok · kabul kriteri</span><h2>Teknik Şartname Talep Paketi</h2><p>UPS, jeneratör, GES, batarya, EV, koruma ve güç kalitesi alımları için aynı kapsamı bütün yüklenicilere gönderin.</p><b>Talep paketini oluştur →</b></a>'
    )
    marker = '<section id="araclar" class="tool-grid">'
    if marker not in text:
        raise RuntimeError("Hesaplama merkezi araç grid başlangıcı bulunamadı")
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
    section = f'''<section {PORTAL_MARKER} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#f5f8fd"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Kişisel verisiz tekrar ziyaret</span><h2 style="color:#071631;margin:.4rem 0">Yeni rehberi, kanıt boşluğunu ve satın alma kapsamını aynı döngüde yönetin.</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px"><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['topics'])}"><strong>Konu Takip Merkezi</strong><br><span>Yeni eşleşen rehberleri e-posta vermeden görün.</span></a><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['evidence'])}"><strong>Kanıt Envanteri</strong><br><span>Test, bakım ve kabul kayıtlarının durumunu izleyin.</span></a><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['spec'])}"><strong>Şartname Talep Paketi</strong><br><span>Tekliften önce ihtiyacı ve kabul kanıtını yazın.</span></a></div></section>'''
    if "</main>" not in text:
        raise RuntimeError("Elektrik portalı main kapanışı bulunamadı")
    path.write_text(text.replace("</main>", section + "</main>", 1), encoding="utf-8")
    return 1


def inject_gateway(site: Path, base_path: str) -> int:
    path = site / GATEWAY
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if GATEWAY_MARKER in text:
        return 0
    card = f'<a class="card" {GATEWAY_MARKER} href="{public_url(base_path, ROUTES["topics"])}"><strong>İlgilendiğiniz elektrik konularındaki yeni rehberleri izleyin</strong><p>E-posta veya bildirim izni vermeden, yeni canonical eşleşmeleri yalnız tarayıcınızda karşılaştırın.</p><span>Konu takip merkezini aç →</span></a>'
    for match in re.finditer(r'<section\b[^>]*>', text, re.I):
        classes = re.search(r'class=["\']([^"\']*)["\']', match.group(0), re.I)
        if classes and "grid" in classes.group(1).split():
            path.write_text(text[: match.end()] + card + text[match.end() :], encoding="utf-8")
            return 1
    return 0


def inject_corporate(site: Path, base_path: str) -> int:
    path = site / CORPORATE
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if CORPORATE_MARKER in text:
        return 0
    section = f'''<section class="specialist-services" {CORPORATE_MARKER}><div class="specialist-heading"><span class="eyebrow">Satın alma öncesi ücretsiz hazırlık</span><h2>Ücretli incelemeden önce aynı teknik kapsamı bütün teklif verenlere gönderin.</h2><p>Marka, fiyat ve puan kullanmadan ihtiyaç, belge, test, kabul ve satın almama kriterlerini talep paketine dönüştürün.</p></div><div class="service-link-grid"><a class="service-link-card" href="{public_url(base_path, ROUTES['spec'])}"><span>Ücretsiz araç</span><h3>Teknik Şartname Talep Paketi</h3><p>UPS, jeneratör, GES, batarya, EV ve koruma sistemleri için yüklenici soru ve kabul taslağı oluşturun.</p><b>Talep paketini hazırla →</b></a><a class="service-link-card" href="{public_url(base_path, ROUTES['evidence'])}"><span>Kanıt hazırlığı</span><h3>Elektrik Kanıt Envanteri</h3><p>Mevcut test, bakım, ölçüm ve kabul kayıtlarının durumunu profesyonel incelemeden önce sınıflandırın.</p><b>Kanıt setini kontrol et →</b></a></div></section>'''
    marker = '<section class="request-grid">'
    if marker not in text:
        raise RuntimeError("Kurumsal ön değerlendirme request grid bulunamadı")
    path.write_text(text.replace(marker, section + marker, 1), encoding="utf-8")
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
    additions = [public_url(base_path, route) for route in ROUTES.values()]
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
        {"name": "Elektrik Konu Takip Merkezi", "short_name": "Konu Takibi", "url": public_url(base_path, ROUTES["topics"])},
        {"name": "Elektrik Kanıt Envanteri", "short_name": "Kanıt Envanteri", "url": public_url(base_path, ROUTES["evidence"])},
    ]
    for item in additions:
        if not any(isinstance(existing, dict) and existing.get("url") == item["url"] for existing in shortcuts):
            shortcuts.append(item)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, cards: int, offline: list[str]) -> None:
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    core["growthRun6"] = {
        "version": 1,
        "routes": list(ROUTES.values()),
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "commercialRankingFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "topicComparisonLocalOnly": True,
        "evidenceFilesUploaded": False,
        "vendorNeutralSpecification": True,
    }
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["growthRun6"] = {
            "version": 1,
            "basePath": base_path,
            "routes": [public_url(base_path, route) for route in ROUTES.values()],
            "entryCardsInjected": cards,
            "offlineAdded": offline,
            "rawPersonalDataCollected": False,
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
            raise FileNotFoundError(f"Growth run6 rotası artifactta eksik: {target}")
    cards = inject_hub(site, base_path)
    cards += inject_portal(site, base_path)
    cards += inject_gateway(site, base_path)
    cards += inject_corporate(site, base_path)
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
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
