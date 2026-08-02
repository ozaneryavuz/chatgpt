from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

VERSION = 213
TARGET = Path("elektrik-portali/index.html")
MARKER = 'data-alo186-portal-purchase-checkpoint-v213="true"'
STYLE_MARKER = 'data-alo186-portal-purchase-checkpoint-v213-style="true"'
SCRIPT_MARKER = 'data-alo186-portal-purchase-checkpoint-v213-script="true"'


def normalize_base_path(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def count_direct_amazon_links(text: str) -> int:
    lowered = text.casefold()
    return lowered.count("amazon.com.tr/") + lowered.count("amazon.com/") + lowered.count("amzn.to/")


def checkpoint(base_path: str) -> str:
    lanes = [
        (
            "internet",
            "İnternet bağlantısını sürdür",
            "Modem ve ONT’nin gerçek voltaj, akım, polarite ve hedef süresini önce hesaplayın.",
            "/hesaplama/modem-internet-yedekleme/",
            "Ücretsiz süre hesabı",
            "/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/",
            "Teknik ürün seçici",
        ),
        (
            "phone_light",
            "Telefon ve güvenli ışığı hazırla",
            "Powerbank, USB-C kablo ve şarjlı aydınlatmayı Wh, port gücü ve kullanım süresine göre ayırın.",
            "/hesaplama/powerbank-usb-c-uygunluk/",
            "USB-C uygunluk hesabı",
            "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
            "Hazırlık ürün seçici",
        ),
        (
            "cold_chain",
            "Gıda ve soğuk zinciri koru",
            "Önce kapak açma süresi, sıcaklık ölçümü ve pasif soğutma planını doğrulayın.",
            "/haberler/elektrik-kesintisinde-buzdolabi-dondurucu-kac-saat-dayanir",
            "Soğuk kalma rehberi",
            "/amazon-elektrik-urunleri/buzdolabi-dondurucu-kesinti-gida-guvenligi-secici/",
            "Soğuk zincir seçici",
        ),
    ]
    cards = "\n".join(
        f'''<article class="ppc-card" data-portal-lane="{key}">
          <span class="ppc-kicker">{index:02d}</span><h3>{title}</h3><p>{description}</p>
          <div class="ppc-actions"><a href="{public_url(base_path, free_route)}" data-portal-checkpoint-link="free">{free_label} →</a><a href="{public_url(base_path, selector_route)}" data-portal-checkpoint-link="selector">{selector_label} →</a></div>
          <button type="button" data-portal-retest="{key}" data-portal-retest-label="{title}">30 günlük tekrar kontrolünü takvime ekle</button>
        </article>'''
        for index, (key, title, description, free_route, free_label, selector_route, selector_label) in enumerate(lanes, start=1)
    )
    return f'''<section class="portal-purchase-checkpoint" {MARKER} aria-labelledby="portal-purchase-checkpoint-title">
      <div class="ppc-head"><div><span class="ppc-label">Satış ortaklığı içerebilir · Satın alma en son adım</span><h2 id="portal-purchase-checkpoint-title">Kesintide hangi görevi sürdürmeniz gerektiğini seçin.</h2></div><p>ALO186 ürün satıcısı, EDAŞ veya kamu kurumu değildir. Fiyat, stok, puan, satıcı ve garanti yayımlanmaz.</p></div>
      <div class="ppc-no-buy"><strong>Mevcut güvenli çözüm gerçek testte yeterliyse yeni ürün almayın.</strong> Islak, hasarlı, şişmiş veya aşırı ısınan ekipmanda ürün seçimine ilerlemeyin.</div>
      <div class="ppc-grid">{cards}</div>
      <p class="ppc-disclosure"><strong>Affiliate açıklaması:</strong> Teknik seçicilerden sonra bazı Amazon bağlantıları gösterilebilir. Nitelikli satın alımlardan ALO186 gelir elde edebilir; kullanıcıya ek maliyet yansımaz. Mağaza bağlantısı, ihtiyaç ve elektriksel uygunluk doğrulandıktan sonra açılmalıdır.</p>
    </section>'''


def styles() -> str:
    return f'''<style {STYLE_MARKER}>
.portal-purchase-checkpoint{{margin:34px 0;padding:26px;border:1px solid #cbd8ea;border-radius:24px;background:linear-gradient(180deg,#f8fbff 0%,#eef4fc 100%);box-shadow:0 16px 38px rgba(7,22,49,.08)}}
.ppc-head{{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(240px,.65fr);gap:22px;align-items:end}}.ppc-head h2{{margin:.35rem 0 0;font-size:clamp(1.55rem,3vw,2.3rem);line-height:1.15;color:#0b2148}}.ppc-head p{{margin:0;color:#50617a}}
.ppc-label{{display:inline-flex;padding:6px 10px;border-radius:999px;background:#0e3974;color:#fff;font-size:.78rem;font-weight:850;letter-spacing:.03em}}
.ppc-no-buy{{margin:18px 0;padding:14px 16px;border-left:4px solid #17824b;background:#edf9f2;color:#294636;border-radius:8px}}.ppc-no-buy strong{{display:block;margin-bottom:3px}}
.ppc-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}}.ppc-card{{display:flex;flex-direction:column;min-width:0;padding:20px;border:1px solid #d7e1ef;border-radius:18px;background:#fff}}.ppc-kicker{{font-size:.78rem;font-weight:900;color:#1f5fd1;letter-spacing:.08em}}.ppc-card h3{{margin:.45rem 0 .5rem;color:#14213d}}.ppc-card p{{margin:0 0 1rem;color:#596a82}}
.ppc-actions{{display:grid;gap:8px;margin-top:auto}}.ppc-actions a,.ppc-card button{{min-height:44px;display:flex;align-items:center;justify-content:center;border-radius:11px;font-weight:800;text-decoration:none;text-align:center}}.ppc-actions a:first-child{{background:#0e3974;color:#fff}}.ppc-actions a:last-child{{border:1px solid #8caee6;color:#174c9c;background:#f6f9ff}}.ppc-card button{{margin-top:9px;padding:10px;border:1px dashed #9aabc3;background:#fff;color:#465872;cursor:pointer}}
.ppc-actions a:focus-visible,.ppc-card button:focus-visible{{outline:3px solid #ffbf47;outline-offset:2px}}.ppc-disclosure{{margin:16px 0 0;color:#516078;font-size:.9rem}}
@media(max-width:900px){{.ppc-head{{grid-template-columns:1fr}}.ppc-grid{{grid-template-columns:1fr}}}}@media(max-width:620px){{.portal-purchase-checkpoint{{margin:24px 0;padding:20px;border-radius:18px}}}}
</style>'''


def script() -> str:
    return f'''<script {SCRIPT_MARKER}>
(()=>{{
  const root=document.querySelector('[data-alo186-portal-purchase-checkpoint-v213="true"]');
  if(!root)return;
  const push=(event,params)=>{{window.dataLayer=window.dataLayer||[];window.dataLayer.push({{event,...params}});}};
  push('portal_purchase_checkpoint_view',{{version:{VERSION}}});
  root.querySelectorAll('[data-portal-checkpoint-link]').forEach(link=>link.addEventListener('click',()=>{{
    const lane=link.closest('[data-portal-lane]')?.dataset.portalLane||'unknown';
    push('portal_purchase_checkpoint_click',{{version:{VERSION},lane,link_type:link.dataset.portalCheckpointLink}});
  }}));
  const dateValue=(date)=>`${{date.getFullYear()}}${{String(date.getMonth()+1).padStart(2,'0')}}${{String(date.getDate()).padStart(2,'0')}}`;
  root.querySelectorAll('[data-portal-retest]').forEach(button=>button.addEventListener('click',()=>{{
    const start=new Date();start.setDate(start.getDate()+30);
    const end=new Date(start);end.setDate(end.getDate()+1);
    const label=button.dataset.portalRetestLabel||'Elektrik kesintisi hazırlığı';
    const lines=[
      'BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Portal Retest V213//TR','CALSCALE:GREGORIAN',
      'BEGIN:VEVENT',`UID:alo186-v213-${{button.dataset.portalRetest}}-${{Date.now()}}@alo186.com`,
      `DTSTART;VALUE=DATE:${{dateValue(start)}}`,`DTEND;VALUE=DATE:${{dateValue(end)}}`,
      `SUMMARY:ALO186 - ${{label}} yeniden kontrolü`,
      'DESCRIPTION:Mevcut ekipmanı gerçek kullanımda yeniden test edin. Yeterliyse yeni ürün almayın. Hasarlı ekipmanı kullanmayın.',
      'URL:https://alo186.com/elektrik-portali','END:VEVENT','END:VCALENDAR'
    ];
    const blob=new Blob([lines.join('\\r\\n')],{{type:'text/calendar;charset=utf-8'}});
    const url=URL.createObjectURL(blob);const anchor=document.createElement('a');
    anchor.href=url;anchor.download=`alo186-${{button.dataset.portalRetest}}-30-gun.ics`;
    document.body.appendChild(anchor);anchor.click();anchor.remove();URL.revokeObjectURL(url);
    push('portal_purchase_retest_download',{{version:{VERSION},lane:button.dataset.portalRetest}});
  }}));
}})();
</script>'''


def insertion_point(text: str) -> int:
    needle = "Elektrik ürünlerini karşılaştır"
    found = text.find(needle)
    if found >= 0:
        section = text.rfind("<section", 0, found)
        if section >= 0:
            return section
        return found
    for fallback in ("Rehberlerinizi seçin", "</main>"):
        found = text.find(fallback)
        if found >= 0:
            section = text.rfind("<section", 0, found) if fallback != "</main>" else -1
            return section if section >= 0 else found
    raise RuntimeError("Portal satın alma kontrol noktası için yerleştirme noktası bulunamadı")


def inject_page(path: Path, base_path: str) -> tuple[bool, int]:
    if not path.is_file():
        raise FileNotFoundError(f"Elektrik portalı artifactı bulunamadı: {path}")
    text = path.read_text(encoding="utf-8", errors="strict")
    direct_before = count_direct_amazon_links(text)
    injected = False
    if MARKER not in text:
        if "</head>" not in text or "</body>" not in text:
            raise RuntimeError(f"Portal HTML kapanışları eksik: {path}")
        text = text.replace("</head>", styles() + "\n</head>", 1)
        point = insertion_point(text)
        text = text[:point] + checkpoint(base_path) + "\n\n" + text[point:]
        text = text.replace("</body>", script() + "\n</body>", 1)
        injected = True
    path.write_text(text, encoding="utf-8")
    return injected, direct_before


def update_release(site: Path, base_path: str, injected: bool, direct_links_observed: int) -> None:
    path = site / "pages-release.json"
    if not path.is_file():
        return
    release = json.loads(path.read_text(encoding="utf-8"))
    release["portalPurchaseCheckpoint"] = {
        "version": VERSION,
        "basePath": base_path,
        "injected": injected,
        "directAmazonLinksObservedBeforeCheckpoint": direct_links_observed,
        "directAmazonLinksChanged": False,
        "taskLaneCount": 3,
        "directAmazonLinksInModule": 0,
        "affiliateDisclosureVisible": True,
        "noBuyVisible": True,
        "unsafeEquipmentBlockVisible": True,
        "retestReminder": "ics_30_days",
        "events": [
            "portal_purchase_checkpoint_view",
            "portal_purchase_checkpoint_click",
            "portal_purchase_retest_download",
        ],
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute_checksums(site: Path) -> None:
    path = site / "checksums.sha256"
    if not path.exists():
        return
    path.unlink()
    lines = [
        f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}"
        for item in sorted(candidate for candidate in site.rglob("*") if candidate.is_file())
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def inject(site: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    injected, direct_links_observed = inject_page(site / TARGET, base_path)
    update_release(site, base_path, injected, direct_links_observed)
    recompute_checksums(site)
    return {
        "ok": True,
        "version": VERSION,
        "basePath": base_path,
        "injected": injected,
        "directAmazonLinksObservedBeforeCheckpoint": direct_links_observed,
        "directAmazonLinksChanged": False,
        "taskLaneCount": 3,
        "retestReminder": "ics_30_days",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 elektrik portalına güven kapılı satın alma kontrolü ve 30 günlük tekrar test hatırlatıcısı ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(inject(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
