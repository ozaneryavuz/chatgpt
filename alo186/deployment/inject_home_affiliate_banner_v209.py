from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

MARKER = 'data-alo186-home-affiliate-v209="true"'
STYLE_MARKER = 'data-alo186-home-affiliate-v209-style="true"'
SCRIPT_MARKER = 'data-alo186-home-affiliate-v209-script="true"'
TARGETS = (Path("index.html"), Path("elektrik-portali/index.html"))


def normalize_base_path(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def showcase(base_path: str) -> str:
    product_map = public_url(base_path, "/amazon-elektrik-urunleri/konuya-gore-urun-haritasi/")
    decision = public_url(base_path, "/kesinti-cihaz-surekliligi-karar-merkezi/")
    cards = [
        (
            "İnternet kesintisi",
            "Modem ve ONT mini UPS",
            "Gerilim, akım, konnektör, polarite ve hedef süreyi doğrulayın.",
            "/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/",
            "Mini UPS seçiciyi aç",
            "01",
        ),
        (
            "Telefon ve USB-C",
            "Powerbank ve şarj ekipmanı",
            "mAh yerine Wh, port gücü ve kablo görevini birlikte kontrol edin.",
            "/amazon-elektrik-urunleri/dogrulanmis-tak-calistir-urunler/",
            "USB-C ürünlerini incele",
            "02",
        ),
        (
            "Gece hazırlığı",
            "Şarjlı fener ve acil ışık",
            "El feneri, kafa feneri ve alan ışığını gerçek görev süresiyle ayırın.",
            "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
            "Kesinti ürünlerini gör",
            "03",
        ),
        (
            "Soğuk zincir",
            "Termometre ve soğutucu hazırlığı",
            "Kesinti öncesi sıcaklık ölçümü ve pasif soğutma açığını belirleyin.",
            "/amazon-elektrik-urunleri/buzdolabi-dondurucu-kesinti-gida-guvenligi-secici/",
            "Soğuk zincir seçiciyi aç",
            "04",
        ),
        (
            "Tüketim ve koruma",
            "Enerji ölçer ve güvenli priz ürünleri",
            "Düşük riskli fişli cihazlarda ölçüm ihtiyacını ürün almadan önce kanıtlayın.",
            "/amazon-elektrik-urunleri/ev-elektrik-olcum-koruma-urunleri/",
            "Ölçüm ürünlerini incele",
            "05",
        ),
        (
            "Kamp ve araç",
            "Taşınabilir enerji ve solar ekipman",
            "Panel, güç istasyonu, araç buzdolabı ve akü ekipmanını görev bazında seçin.",
            "/amazon-elektrik-urunleri/kamp-arac-enerji-urun-secici/",
            "Kamp enerji seçiciyi aç",
            "06",
        ),
    ]
    card_html = "\n".join(
        f'''<a class="haf-product" href="{public_url(base_path, route)}" data-home-affiliate-product="{number}">
          <span class="haf-number" aria-hidden="true">{number}</span><span class="haf-kicker">{kicker}</span>
          <h3>{title}</h3><p>{description}</p><b>{cta} →</b>
        </a>'''
        for kicker, title, description, route, cta, number in cards
    )
    return f'''<section class="home-affiliate-feature" {MARKER} aria-labelledby="home-affiliate-title">
      <div class="haf-banner">
        <div class="haf-copy"><span class="haf-label">Satış ortaklığı içerebilir · Önce teknik uygunluk</span>
          <h2 id="home-affiliate-title">Kesinti ve elektrik hazırlığınızda gerçekten eksik olan ürünü bulun.</h2>
          <p>ALO186 ürün satıcısı veya resmî kurum değildir. Fiyat, stok, puan ve garanti yayımlamaz. Mevcut güvenli ürün ihtiyacınızı karşılıyorsa yenisini almayın; teknik açık varsa şeffaf ürün seçicisine ilerleyin.</p>
          <div class="haf-actions"><a class="haf-primary" href="{product_map}" data-home-affiliate-banner="product-map">Konuya göre ürün haritasını aç →</a><a class="haf-secondary" href="{decision}" data-home-affiliate-banner="decision">Önce ihtiyacımı doğrula</a></div>
        </div>
        <div class="haf-proof" aria-label="Güven ilkeleri"><strong>Satın alma öncesi 3 kontrol</strong><ol><li>Mevcut ekipman yeterli mi?</li><li>Model ve elektriksel özellikler uyumlu mu?</li><li>Bağlantının satış ortaklığı olduğu açık mı?</li></ol></div>
      </div>
      <div class="haf-heading"><div><span class="eyebrow">En çok aranan hazırlık ürünleri</span><h2>İhtiyaca göre ürün seçicileri</h2></div><p>Doğrudan mağaza yerine önce ücretsiz teknik kontrol açılır.</p></div>
      <div class="haf-grid">{card_html}</div>
      <p class="haf-disclosure"><strong>Affiliate açıklaması:</strong> İlgili seçicilerde bazı Amazon bağlantıları bulunabilir. Nitelikli satın alımlardan gelir elde edilebilir; kullanıcıya ek maliyet yansımaz. Mağaza bağlantıları yalnız açık onay ve teknik uygunluk sonrasında etkinleşir.</p>
    </section>'''


def styles() -> str:
    return f'''<style {STYLE_MARKER}>
.home-affiliate-feature{{margin:34px 0;padding:0;border-radius:26px;scroll-margin-top:20px}}
.haf-banner{{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(250px,.65fr);gap:22px;padding:30px;border:1px solid #bfd0ee;border-radius:24px;background:linear-gradient(135deg,#071631 0%,#123b77 66%,#1f5fd1 100%);color:#fff;box-shadow:0 20px 44px rgba(7,22,49,.16)}}
.haf-copy h2{{margin:.35rem 0 .65rem;font-size:clamp(1.65rem,3.3vw,2.55rem);line-height:1.12;color:#fff}}.haf-copy p{{margin:0;max-width:760px;color:#e9f0ff}}
.haf-label{{display:inline-flex;padding:6px 10px;border:1px solid rgba(255,255,255,.38);border-radius:999px;background:rgba(255,255,255,.1);font-size:.78rem;font-weight:800;letter-spacing:.04em}}
.haf-actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:20px}}.haf-primary,.haf-secondary{{display:inline-flex;align-items:center;justify-content:center;padding:12px 16px;border-radius:12px;font-weight:850;text-decoration:none}}
.haf-primary{{background:#fff;color:#0b2c62}}.haf-secondary{{border:1px solid rgba(255,255,255,.55);color:#fff;background:rgba(255,255,255,.08)}}
.haf-proof{{align-self:stretch;padding:19px;border:1px solid rgba(255,255,255,.28);border-radius:18px;background:rgba(255,255,255,.1)}}.haf-proof strong{{font-size:1.05rem}}.haf-proof ol{{margin:.8rem 0 0;padding-left:1.2rem;color:#edf3ff}}.haf-proof li+li{{margin-top:.5rem}}
.haf-heading{{display:flex;align-items:end;justify-content:space-between;gap:18px;margin:28px 0 14px}}.haf-heading h2{{margin:.2rem 0 0}}.haf-heading p{{margin:0;color:#5b687b}}
.haf-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}}.haf-product{{position:relative;min-height:220px;padding:22px;border:1px solid #dbe3ee;border-radius:18px;background:#fff;color:#14213d;text-decoration:none;box-shadow:0 10px 26px rgba(7,22,49,.06);transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}}
.haf-product:hover,.haf-product:focus-visible{{transform:translateY(-3px);border-color:#8caee6;box-shadow:0 16px 34px rgba(7,22,49,.12)}}.haf-number{{position:absolute;right:18px;top:15px;color:#9aabc3;font-weight:900;font-size:1.35rem}}.haf-kicker{{display:block;padding-right:42px;color:#1f5fd1;font-size:.78rem;font-weight:850;text-transform:uppercase;letter-spacing:.06em}}.haf-product h3{{margin:.55rem 0 .45rem;font-size:1.18rem}}.haf-product p{{margin:0 0 1rem;color:#5b687b}}.haf-product b{{color:#1f5fd1}}
.haf-disclosure{{margin:14px 0 0;padding:13px 15px;border-left:4px solid #1f5fd1;background:#f4f7fb;color:#4e5d73;font-size:.9rem}}
@media(max-width:900px){{.haf-banner{{grid-template-columns:1fr}}.haf-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media(max-width:620px){{.home-affiliate-feature{{margin:24px 0}}.haf-banner{{padding:22px;border-radius:19px}}.haf-actions{{display:grid}}.haf-primary,.haf-secondary{{width:100%}}.haf-heading{{display:block}}.haf-heading p{{margin-top:6px}}.haf-grid{{grid-template-columns:1fr}}.haf-product{{min-height:auto}}}}
</style>'''


def script() -> str:
    return f'''<script {SCRIPT_MARKER}>
(()=>{{
  const push=(event,params)=>{{window.dataLayer=window.dataLayer||[];window.dataLayer.push({{event,...params}});}};
  const root=document.querySelector('[data-alo186-home-affiliate-v209="true"]');
  if(!root)return;
  push('home_affiliate_showcase_view',{{placement:'homepage_v209'}});
  root.querySelectorAll('[data-home-affiliate-banner]').forEach(link=>link.addEventListener('click',()=>push('home_affiliate_banner_click',{{target:link.dataset.homeAffiliateBanner}})));
  root.querySelectorAll('[data-home-affiliate-product]').forEach(link=>link.addEventListener('click',()=>push('home_affiliate_product_click',{{product_slot:link.dataset.homeAffiliateProduct,href:link.getAttribute('href')}})));
}})();
</script>'''


def insertion_point(text: str) -> int:
    needles = (
        '<section class="legal-alert"',
        '<details class="resource-library"',
        '<section class="revenue-sprint"',
        '</main>',
    )
    positions = [text.find(needle) for needle in needles]
    for position in positions:
        if position >= 0:
            return position
    raise RuntimeError("Ana sayfada güvenli banner yerleştirme noktası bulunamadı")


def inject_page(path: Path, base_path: str) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="strict")
    if MARKER in text:
        return False
    if '</head>' not in text or '</body>' not in text:
        raise RuntimeError(f"Eksik HTML kapanışı: {path}")
    text = text.replace('</head>', styles() + '\n</head>', 1)
    point = insertion_point(text)
    text = text[:point] + showcase(base_path) + '\n\n' + text[point:]
    text = text.replace('</body>', script() + '\n</body>', 1)
    path.write_text(text, encoding="utf-8")
    return True


def recompute_checksums(site: Path) -> None:
    checksum_path = site / "checksums.sha256"
    if not checksum_path.exists():
        return
    checksum_path.unlink()
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(site).as_posix()}"
        for path in sorted(item for item in site.rglob("*") if item.is_file())
    ]
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_release(site: Path, injected: list[str], base_path: str) -> None:
    path = site / "pages-release.json"
    if not path.is_file():
        return
    release = json.loads(path.read_text(encoding="utf-8"))
    release["homeAffiliateShowcase"] = {
        "version": 209,
        "basePath": base_path,
        "injectedPages": injected,
        "productSelectorCount": 6,
        "directAmazonLinks": 0,
        "affiliateDisclosureVisible": True,
        "existingProductNoBuyVisible": True,
        "events": [
            "home_affiliate_showcase_view",
            "home_affiliate_banner_click",
            "home_affiliate_product_click",
        ],
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def inject(site: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    injected = []
    for relative in TARGETS:
        if inject_page(site / relative, base_path):
            injected.append(relative.as_posix())
    if not injected and not any((site / relative).is_file() for relative in TARGETS):
        raise RuntimeError("Ana sayfa artifactı bulunamadı")
    update_release(site, injected, base_path)
    recompute_checksums(site)
    return {
        "ok": True,
        "version": 209,
        "basePath": base_path,
        "injectedPages": injected,
        "productSelectorCount": 6,
        "directAmazonLinks": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 ana sayfasına güven odaklı affiliate banner ve ürün seçici vitrini ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(inject(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
