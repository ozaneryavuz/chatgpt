from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROUTES = {
    "followup": "/hesaplama/kesinti-sonrasi-takip-dosyasi/",
    "receipts": "/karar-makbuzlari/",
    "official": "/elektrik-kesintisi",
    "workorder": "/hesaplama/elektrikci-is-emri-ozeti/",
    "compare": "/hesaplama/teknik-urun-karsilastirma/",
    "aftercare": "/hesaplama/urun-sonrasi-guvenlik-kontrolu/",
    "evidence": "/hesaplama/elektrik-kanit-envanteri/",
    "spec": "/hesaplama/teknik-sartname-talep-paketi/",
    "service": "/hizmet-secici/",
}
HUB = Path("hesaplama/index.html")
PORTAL = Path("elektrik-portali/index.html")
GATEWAY = Path("index.html")
HUB_MARKER = 'data-alo186-growth-run8-tools="true"'
PORTAL_MARKER = 'data-alo186-growth-run8-journey="true"'
GATEWAY_MARKER = 'data-alo186-growth-run8-gateway="true"'
CONTEXT_MARKER = 'data-alo186-growth-run8-context="true"'


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
        f'<a class="tool-card" {HUB_MARKER} href="{public_url(base_path, ROUTES["followup"])}"><span class="eyebrow">Kesinti · cihaz etkisi · 10 iş günü</span><h2>Kesinti Sonrası Takip Dosyası</h2><p>Resmî kayıt, teknik kanıt ve cihaz hasarı adımlarını kişisel veri vermeden aynı zaman çizelgesine alın.</p><b>Takip dosyasını oluştur →</b></a>'
        f'<a class="tool-card" href="{public_url(base_path, ROUTES["receipts"])}"><span class="eyebrow">Yerel JSON · 180 gün · no-buy</span><h2>Teknik Karar Makbuzları</h2><p>ALO186 araçlarından indirdiğiniz güvenli karar makbuzlarını tek merkezde yeniden kontrol edin.</p><b>Makbuz merkezini aç →</b></a>'
    )
    marker = '<section id="araclar" class="tool-grid">'
    if marker not in text:
        raise RuntimeError("Hesaplama merkezi araç grid başlangıcı bulunamadı")
    path.write_text(text.replace(marker, marker + cards, 1), encoding="utf-8")
    return 2


def inject_portal(site: Path, base_path: str) -> int:
    path = site / PORTAL
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if PORTAL_MARKER in text:
        return 0
    section = f'''<section {PORTAL_MARKER} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#f5f8fd"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Olaydan karara, karardan yeniden kontrole</span><h2 style="color:#071631;margin:.4rem 0">Kesinti kaydını kanıta, teknik kararı tekrar ziyaret nedenine dönüştürün.</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px"><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['followup'])}"><strong>Kesinti Takip Dosyası</strong><br><span>Resmî kayıt, cihaz etkisi ve eksik kanıtı ayırın.</span></a><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['receipts'])}"><strong>Karar Makbuzları</strong><br><span>Ücretsiz araç sonuçlarını yerel olarak yeniden kontrol edin.</span></a><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['service'])}"><strong>Hizmet Uygunluğu</strong><br><span>Ücretsiz veya resmî adım yeterliyse ücretli yolu kapatın.</span></a></div></section>'''
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
    card = f'<a class="card" {GATEWAY_MARKER} href="{public_url(base_path, ROUTES["followup"])}"><strong>Kesinti sonrası kayıt ve kanıt dosyası oluşturun</strong><p>ALO186 başvuru almaz; resmî kayıt, cihaz etkisi ve teknik belge boşluğunu kişisel veri paylaşmadan ayırır.</p><span>Takip dosyasını aç →</span></a>'
    for match in re.finditer(r'<section\b[^>]*>', text, re.I):
        classes = re.search(r'class=["\']([^"\']*)["\']', match.group(0), re.I)
        if classes and "grid" in classes.group(1).split():
            path.write_text(text[: match.end()] + card + text[match.end() :], encoding="utf-8")
            return 1
    return 0


def context_kind(path: Path, html: str) -> str | None:
    rel = path.as_posix().lower()
    lowered = re.sub(r"<[^>]+>", " ", html).lower()
    if "/amazon-elektrik-urunleri/" in rel:
        return "product"
    if re.search(r"kesinti|edaş|dağıtım şirket|cihaz hasar|gerilim çukuru|planlı elektrik", lowered):
        return "outage"
    if re.search(r"ups|jeneratör|ats|akü|inverter|ges|batarya|enerji depolama|ev şarj|harmonik|topraklama|parafudr|kaçak akım", lowered):
        return "technical"
    return None


def context_panel(kind: str, base_path: str) -> str:
    style = 'style="margin:36px auto;padding:22px;border:1px solid #dce5ef;border-radius:20px;background:#f5f8fd"'
    link = 'style="display:block;padding:14px;border:1px solid #dce5ef;border-radius:13px;background:#fff;color:#071631;text-decoration:none"'
    grid = 'style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px"'
    if kind == "outage":
        return f'''<section {CONTEXT_MARKER} data-context="outage" {style}><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase">Bu rehberden sonraki güvenli adım</span><h2 style="color:#071631">Resmî kaydı, teknik kanıtı ve takip tarihini ayırın.</h2><div {grid}><a {link} href="{public_url(base_path, ROUTES['official'])}"><strong>Resmî kanal</strong><br>Yetkili dağıtım şirketini ve 186 hattını bulun.</a><a {link} href="{public_url(base_path, ROUTES['followup'])}"><strong>Takip dosyası</strong><br>Olay ve cihaz etkisi için eksik kanıtı görün.</a><a {link} href="{public_url(base_path, ROUTES['workorder'])}"><strong>Teknik iş emri</strong><br>İç tesisat incelemesi gerekiyorsa ölçüm kapsamını hazırlayın.</a></div><p style="font-size:.9rem;color:#58677c"><strong>ALO186 başvuru almaz.</strong> Kesinti veya hasar tek başına ürün satın alma gerekçesi değildir.</p></section>'''
    if kind == "product":
        return f'''<section {CONTEXT_MARKER} data-context="product" {style}><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase">Satın alma öncesi ve sonrası güven kapısı</span><h2 style="color:#071631">Önce teknik ihtiyacı doğrulayın; mevcut ürün yeterliyse satın almayın.</h2><div {grid}><a {link} href="{public_url(base_path, ROUTES['compare'])}"><strong>Teknik karşılaştırma</strong><br>Fiyat ve puan kullanmadan üç adayı kıyaslayın.</a><a {link} href="{public_url(base_path, ROUTES['aftercare'])}"><strong>Ürün sonrası kontrol</strong><br>Isınma, hasar ve uyumluluğu yeniden değerlendirin.</a><a {link} href="{public_url(base_path, ROUTES['receipts'])}"><strong>Karar makbuzu</strong><br>Satın almama veya yeniden kontrol sonucunu saklayın.</a></div><p style="font-size:.9rem;color:#58677c"><strong>Reklam / satış ortaklığı açıklaması:</strong> Ürün rehberi daha sonra Amazon satış ortaklığı bağlantısı içerebilir. Fiyat, stok, puan, satıcı ve garanti ALO186 tarafından kopyalanmaz.</p></section>'''
    return f'''<section {CONTEXT_MARKER} data-context="technical" {style}><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase">Bilgiden uygulanabilir kapsama</span><h2 style="color:#071631">Önce kanıt ve kapsamı hazırlayın; sonra ücretli hizmet gerekip gerekmediğini seçin.</h2><div {grid}><a {link} href="{public_url(base_path, ROUTES['evidence'])}"><strong>Kanıt envanteri</strong><br>Ölçüm, bakım ve kabul kayıtlarının boşluğunu görün.</a><a {link} href="{public_url(base_path, ROUTES['spec'])}"><strong>Tarafsız şartname</strong><br>Teklif verenlerden aynı teknik teslimleri isteyin.</a><a {link} href="{public_url(base_path, ROUTES['service'])}"><strong>Hizmet uygunluğu</strong><br>Ücretsiz adım yeterliyse ücretli yolu kapatın.</a></div><p style="font-size:.9rem;color:#58677c">ALO186 EDAŞ, üretici servisi veya resmî kabul kuruluşu değildir. Mevcut sistem güvenli ve kanıtlıysa gereksiz değişim önerilmez.</p></section>'''


def inject_contextual_panels(site: Path, base_path: str) -> dict[str, int]:
    counts = {"outage": 0, "technical": 0, "product": 0}
    candidates: list[Path] = []
    for directory in ("haberler", "sektor-rehberi", "amazon-elektrik-urunleri"):
        root = site / directory
        if root.is_dir():
            candidates.extend(root.rglob("index.html"))
    for path in sorted(set(candidates)):
        html = path.read_text(encoding="utf-8")
        if CONTEXT_MARKER in html or "</main>" not in html:
            continue
        kind = context_kind(path, html)
        if not kind:
            continue
        path.write_text(html.replace("</main>", context_panel(kind, base_path) + "</main>", 1), encoding="utf-8")
        counts[kind] += 1
    return counts


def add_offline(site: Path, base_path: str) -> list[str]:
    path = site / "sw.js"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        raise RuntimeError("Service worker CRITICAL rota dizisi bulunamadı")
    routes = json.loads(match.group(1))
    additions = [public_url(base_path, ROUTES["followup"]), public_url(base_path, ROUTES["receipts"])]
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
        {"name": "Kesinti Sonrası Takip Dosyası", "short_name": "Kesinti Takibi", "url": public_url(base_path, ROUTES["followup"])},
        {"name": "Teknik Karar Makbuzları", "short_name": "Karar Makbuzları", "url": public_url(base_path, ROUTES["receipts"])},
    ]
    for item in additions:
        if not any(isinstance(existing, dict) and existing.get("url") == item["url"] for existing in shortcuts):
            shortcuts.append(item)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, cards: int, offline: list[str], contexts: dict[str, int]) -> None:
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    core["growthRun8"] = {
        "version": 1,
        "routes": [ROUTES["followup"], ROUTES["receipts"]],
        "rawPersonalDataCollected": False,
        "uploadedFilesStored": False,
        "receiptTtlDays": 180,
        "outageReceiptTtlDays": 60,
        "directAffiliateLinksAdded": 0,
        "unverifiedCommercialFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "officialAffiliationClaimed": False,
        "contextualPanels": contexts,
    }
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["growthRun8"] = {
            "version": 1,
            "basePath": base_path,
            "routes": [public_url(base_path, ROUTES["followup"]), public_url(base_path, ROUTES["receipts"])],
            "entryCardsInjected": cards,
            "offlineAdded": offline,
            "contextualPanels": contexts,
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
    for key in ("followup", "receipts"):
        target = site / ROUTES[key].strip("/") / "index.html"
        if not target.is_file():
            raise FileNotFoundError(f"Growth run8 rotası artifactta eksik: {target}")
    cards = inject_hub(site, base_path)
    cards += inject_portal(site, base_path)
    cards += inject_gateway(site, base_path)
    contexts = inject_contextual_panels(site, base_path)
    offline = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_release(site, base_path, cards, offline, contexts)
    recompute(site)
    return {
        "ok": True,
        "basePath": base_path,
        "routes": [public_url(base_path, ROUTES["followup"]), public_url(base_path, ROUTES["receipts"])],
        "entryCardsInjected": cards,
        "contextualPanels": contexts,
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
