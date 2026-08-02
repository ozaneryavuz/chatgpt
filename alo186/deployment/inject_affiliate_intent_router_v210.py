from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

MARKER = 'data-alo186-affiliate-intent-v210="true"'
STYLE_MARKER = 'data-alo186-affiliate-intent-v210-style="true"'
SCRIPT_MARKER = 'data-alo186-affiliate-intent-v210-script="true"'
TARGET = Path("amazon-elektrik-urunleri/index.html")
TTL_DAYS = 14


def normalize_base_path(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def router_markup(base_path: str) -> str:
    routes = {
        "internet": {
            "tool": public_url(base_path, "/hesaplama/modem-internet-yedekleme/"),
            "commercial": public_url(base_path, "/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/"),
            "title": "İnternet sürekliliği",
            "summary": "Modem, ONT ve router için gerilim, akım, konnektör, polarite, gerçek W ve hedef süreyi doğrulayın.",
        },
        "communication": {
            "tool": public_url(base_path, "/hesaplama/powerbank-usb-c-uygunluk/"),
            "commercial": public_url(base_path, "/amazon-elektrik-urunleri/dogrulanmis-tak-calistir-urunler/"),
            "title": "Telefon ve USB-C iletişimi",
            "summary": "mAh yerine Wh, port gücü, kablo ve cihaz protokolünü birlikte kontrol edin.",
        },
        "lighting": {
            "tool": public_url(base_path, "/hesaplama/elektrik-kesintisi-kiti/"),
            "commercial": public_url(base_path, "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/"),
            "title": "Gece aydınlatması",
            "summary": "El feneri, kafa feneri ve alan ışığını kullanım süresi, pil türü ve görev alanına göre ayırın.",
        },
        "cold": {
            "tool": public_url(base_path, "/haberler/elektrik-kesintisinde-buzdolabi-dondurucu-kac-saat-dayanir"),
            "commercial": public_url(base_path, "/amazon-elektrik-urunleri/buzdolabi-dondurucu-kesinti-gida-guvenligi-secici/"),
            "title": "Gıda ve soğuk zincir",
            "summary": "Kapak açma, sıcaklık ölçümü, kesinti süresi ve pasif soğutma açığını önce doğrulayın.",
        },
        "measurement": {
            "tool": public_url(base_path, "/hesaplama/akilli-priz-enerji-olcer-uygunluk/"),
            "commercial": public_url(base_path, "/amazon-elektrik-urunleri/ev-elektrik-olcum-koruma-urunleri/"),
            "title": "Tüketim ölçümü",
            "summary": "Yalnız düşük riskli fişli yüklerde W, A, kWh, kalkış gücü ve ürün etiketini doğrulayın.",
        },
        "mobile": {
            "tool": public_url(base_path, "/hesaplama/gunes-paneli-power-station-uygunluk/"),
            "commercial": public_url(base_path, "/amazon-elektrik-urunleri/kamp-arac-elektrik-urunleri/"),
            "title": "Kamp, araç ve taşınabilir enerji",
            "summary": "Sürekli W, tepe W, Wh, PV giriş sınırı ve gerçek kullanım süresini birlikte değerlendirin.",
        },
        "compare": {
            "tool": public_url(base_path, "/hesaplama/teknik-urun-karsilastirma/"),
            "commercial": "",
            "title": "Teknik ürün karşılaştırması",
            "summary": "Adayları fiyat veya puanla değil, belgelenmiş teknik gereksinimlerle karşılaştırın.",
        },
        "fixed": {
            "tool": public_url(base_path, "/kurumsal-elektrik-surekliligi-on-degerlendirme"),
            "commercial": "",
            "title": "Sabit tesisat veya profesyonel sistem",
            "summary": "Yüksek güç, sabit montaj, üç faz ve kritik sistemlerde tüketici affiliate yolu uygun değildir.",
        },
    }
    decision = public_url(base_path, "/elektrik-durum-merkezi/")
    recheck = public_url(base_path, "/hesaplama/elektrik-kesintisi-kiti/")
    route_json = json.dumps(routes, ensure_ascii=False).replace("</", "<\\/")

    return f'''<section class="affiliate-intent-router" {MARKER} aria-labelledby="affiliateIntentTitle">
  <div class="affiliate-intent-copy">
    <span class="eyebrow">30 saniyelik ihtiyaç yönlendiricisi</span>
    <h2 id="affiliateIntentTitle">Hangi ürün sayfasından başlamanız gerektiğini bulun.</h2>
    <p>Ürün adı seçmek yerine sürdürmek istediğiniz görevi, yaklaşık kesinti süresini ve mevcut çözümünüzün durumunu işaretleyin. Sonuç önce ücretsiz teknik aracı gösterir; mağaza yolu yalnız gerçek açık varsa görünür.</p>
  </div>
  <form class="affiliate-intent-form" data-affiliate-intent-form novalidate>
    <label><span>1. Hangi görevi sürdürmek istiyorsunuz?</span>
      <select name="need" required>
        <option value="">Seçin</option>
        <option value="internet">Modem, ONT ve internet</option>
        <option value="communication">Telefon, tablet ve USB-C</option>
        <option value="lighting">Şarjlı fener ve gece aydınlatması</option>
        <option value="cold">Buzdolabı, dondurucu ve soğuk zincir</option>
        <option value="measurement">Enerji tüketimini ölçme</option>
        <option value="mobile">Kamp, araç ve taşınabilir enerji</option>
        <option value="compare">Üç ürünü teknik olarak karşılaştırma</option>
        <option value="fixed">Sabit tesisat, yüksek güç veya profesyonel sistem</option>
      </select>
    </label>
    <label><span>2. Yaklaşık ne kadar süre hedefliyorsunuz?</span>
      <select name="duration" required>
        <option value="">Seçin</option>
        <option value="short">0–2 saat</option>
        <option value="medium">2–8 saat</option>
        <option value="long">8 saatten fazla</option>
        <option value="unknown">Henüz bilmiyorum</option>
      </select>
    </label>
    <label><span>3. Mevcut çözümünüzün durumu nedir?</span>
      <select name="status" required>
        <option value="">Seçin</option>
        <option value="none">Yok veya gerçek ihtiyacı karşılamıyor</option>
        <option value="untested">Var fakat gerçek test yapılmadı</option>
        <option value="sufficient">Güvenli gerçek testte yeterli</option>
        <option value="unsafe">Hasarlı, ıslak, aşırı ısınan veya riskli</option>
      </select>
    </label>
    <div class="affiliate-intent-actions">
      <button class="button primary" type="submit">Güvenli başlangıcı göster</button>
      <button class="button secondary" type="button" data-affiliate-intent-reset>Seçimleri temizle</button>
    </div>
  </form>
  <div class="affiliate-intent-resume" data-affiliate-intent-resume hidden>
    <strong>Önceki seçiminiz cihazınızda bulundu.</strong>
    <button class="button secondary" type="button" data-affiliate-intent-resume-button>Kaldığım yerden devam et</button>
  </div>
  <div class="affiliate-intent-result" data-affiliate-intent-result role="status" aria-live="polite" hidden></div>
  <p class="affiliate-intent-note"><strong>Satış ortaklığı açıklaması:</strong> Bazı sonraki dış bağlantılardan komisyon kazanılabilir; kullanıcıya ek maliyet yansımaz. ALO186 ürün satıcısı, EDAŞ veya kamu kurumu değildir. Fiyat, stok, puan, satıcı, teslimat ve garanti yayımlanmaz.</p>
</section>
<script type="application/json" data-affiliate-intent-routes>{route_json}</script>
<script type="application/json" data-affiliate-intent-config>{{"ttlDays":{TTL_DAYS},"decision":"{decision}","recheck":"{recheck}"}}</script>'''


def style_block() -> str:
    return f'''<style {STYLE_MARKER}>
.affiliate-intent-router{{margin:2rem 0;padding:clamp(1.1rem,3vw,2rem);border:1px solid rgba(62,167,255,.3);border-radius:24px;background:linear-gradient(145deg,rgba(9,32,70,.98),rgba(10,48,83,.96));box-shadow:0 18px 50px rgba(3,13,32,.22);color:#f7fbff}}
.affiliate-intent-copy{{max-width:820px}}
.affiliate-intent-copy h2{{margin:.35rem 0 .65rem;font-size:clamp(1.55rem,3vw,2.25rem)}}
.affiliate-intent-copy p,.affiliate-intent-note{{color:#cfe1f4}}
.affiliate-intent-form{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem;margin-top:1.25rem}}
.affiliate-intent-form label{{display:grid;gap:.45rem;font-weight:700}}
.affiliate-intent-form select{{width:100%;min-height:48px;border-radius:12px;border:1px solid rgba(170,210,245,.35);background:#fff;color:#10233d;padding:.75rem;font:inherit}}
.affiliate-intent-actions{{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:.75rem}}
.affiliate-intent-result,.affiliate-intent-resume{{margin-top:1rem;padding:1rem;border-radius:16px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.18)}}
.affiliate-intent-result h3{{margin:0 0 .45rem}}
.affiliate-intent-result p{{margin:.35rem 0;color:#e4effa}}
.affiliate-intent-result .result-actions{{display:flex;flex-wrap:wrap;gap:.7rem;margin-top:.85rem}}
.affiliate-intent-result .no-buy{{display:inline-block;margin-top:.5rem;padding:.45rem .7rem;border-radius:999px;background:#dff8e8;color:#123f27;font-weight:800}}
.affiliate-intent-result .blocked{{display:inline-block;margin-top:.5rem;padding:.45rem .7rem;border-radius:999px;background:#ffe4df;color:#6b1a11;font-weight:800}}
.affiliate-intent-resume{{display:flex;align-items:center;justify-content:space-between;gap:1rem}}
.affiliate-intent-note{{margin:1rem 0 0;font-size:.92rem}}
@media(max-width:820px){{.affiliate-intent-form{{grid-template-columns:1fr}}.affiliate-intent-resume{{align-items:flex-start;flex-direction:column}}}}
</style>'''


def script_block() -> str:
    return f'''<script {SCRIPT_MARKER}>
(()=>{{
  const root=document.querySelector('[data-alo186-affiliate-intent-v210="true"]');
  if(!root)return;
  const form=root.querySelector('[data-affiliate-intent-form]');
  const result=root.querySelector('[data-affiliate-intent-result]');
  const resume=root.querySelector('[data-affiliate-intent-resume]');
  const resumeButton=root.querySelector('[data-affiliate-intent-resume-button]');
  const resetButton=root.querySelector('[data-affiliate-intent-reset]');
  const routes=JSON.parse(document.querySelector('[data-affiliate-intent-routes]').textContent);
  const config=JSON.parse(document.querySelector('[data-affiliate-intent-config]').textContent);
  const key='alo186_affiliate_intent_v210';
  const allowed={{need:Object.keys(routes),duration:['short','medium','long','unknown'],status:['none','untested','sufficient','unsafe']}};
  const track=(event,extra={{}})=>{{window.dataLayer=window.dataLayer||[];window.dataLayer.push({{event,...extra,alo186_no_pii:true}});}};
  const valid=(data)=>allowed.need.includes(data.need)&&allowed.duration.includes(data.duration)&&allowed.status.includes(data.status);
  const load=()=>{{try{{const saved=JSON.parse(localStorage.getItem(key)||'null');if(!saved||!valid(saved)||Date.now()>saved.expiresAt){{localStorage.removeItem(key);return null}}return saved}}catch(_e){{localStorage.removeItem(key);return null}}}};
  const save=(data)=>{{try{{localStorage.setItem(key,JSON.stringify({{...data,expiresAt:Date.now()+config.ttlDays*86400000}}))}}catch(_e){{}}}};
  const setValues=(data)=>{{form.elements.need.value=data.need;form.elements.duration.value=data.duration;form.elements.status.value=data.status}};
  const link=(href,label,kind='primary')=>`<a class="button ${{kind}}" href="${{href}}" data-affiliate-intent-link>${{label}}</a>`;
  const render=(data,fromResume=false)=>{{
    const route=routes[data.need];
    const durationNote=data.duration==='long'?'Uzun süre hedefinde enerji kapasitesi, şarj süresi ve profesyonel kurulum sınırı ayrıca doğrulanmalıdır.':data.duration==='unknown'?'Önce gerçek yük ve hedef süreyi ölçerek belirsizliği azaltın.':'Seçilen süreyi etiket kapasitesiyle değil gerçek testle doğrulayın.';
    let html=`<h3>${{route.title}}</h3><p>${{route.summary}}</p><p>${{durationNote}}</p>`;
    let event='affiliate_intent_result';
    if(data.status==='unsafe'){{
      html+=`<span class="blocked">Ticari yol kapalı</span><p>Hasarlı, ıslak, şişmiş, aşırı ısınan veya yanık kokulu ekipmanı kullanmayın. Enerjili bölüme müdahale etmeden güvenli karar yoluna ilerleyin.</p><div class="result-actions">${{link(config.decision,'Güvenli karar merkezini aç')}}</div>`;
      event='affiliate_intent_blocked';
    }}else if(data.status==='sufficient'){{
      html+=`<span class="no-buy">Mevcut güvenli çözüm yeterli — yeni ürün almayın.</span><p>Yeni ürün yerine mevcut çözümün bakım ve tekrar test tarihini planlayın.</p><div class="result-actions">${{link(config.recheck,'Mevcut sistemi yeniden test et')}}</div>`;
      event='affiliate_intent_no_buy';
    }}else if(data.need==='fixed'){{
      html+=`<span class="blocked">Tüketici affiliate yolu uygun değil</span><p>Sabit tesisat, yüksek güç, üç faz ve profesyonel sistemlerde proje, koruma koordinasyonu ve yetkin uygulama gerekir.</p><div class="result-actions">${{link(route.tool,'Profesyonel kapsamı incele')}}</div>`;
      event='affiliate_intent_professional';
    }}else{{
      html+=`<div class="result-actions">${{link(route.tool,'Önce ücretsiz teknik aracı aç')}}`;
      if(data.status==='none'&&route.commercial)html+=link(route.commercial,'Teknik açık doğrulanırsa ürün seçiciyi aç','secondary');
      if(data.status==='untested')html+=`<span class="no-buy">Önce test; henüz satın alma yok.</span>`;
      html+='</div>';
    }}
    result.innerHTML=html;result.hidden=false;save(data);track(event,{{need:data.need,duration:data.duration,status:data.status,resumed:fromResume}});
  }};
  form.addEventListener('submit',(e)=>{{e.preventDefault();const data={{need:form.elements.need.value,duration:form.elements.duration.value,status:form.elements.status.value}};if(!valid(data)){{result.hidden=false;result.innerHTML='<p>Lütfen üç seçimi de tamamlayın.</p>';return}}render(data)}});
  resetButton.addEventListener('click',()=>{{form.reset();result.hidden=true;resume.hidden=true;try{{localStorage.removeItem(key)}}catch(_e){{}}track('affiliate_intent_reset')}});
  resumeButton.addEventListener('click',()=>{{const saved=load();if(!saved)return;setValues(saved);render(saved,true);resume.hidden=true;track('affiliate_intent_resume')}});
  root.addEventListener('click',(e)=>{{const a=e.target.closest('[data-affiliate-intent-link]');if(a)track('affiliate_intent_cta_click',{{destination:new URL(a.href,location.href).pathname}})}});
  const saved=load();if(saved){{resume.hidden=false;track('affiliate_intent_resume_available')}}
  track('affiliate_intent_router_view');
}})();
</script>'''


def recompute_checksums(site: Path) -> None:
    checksum_path = site / "checksums.sha256"
    if checksum_path.exists():
        checksum_path.unlink()
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(site).as_posix()}"
        for path in sorted(item for item in site.rglob("*") if item.is_file())
    ]
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str) -> None:
    release_path = site / "pages-release.json"
    if not release_path.is_file():
        return
    release = json.loads(release_path.read_text(encoding="utf-8"))
    release["affiliateIntentRouter"] = {
        "version": 210,
        "basePath": base_path,
        "taskCount": 8,
        "questionCount": 3,
        "localResumeTtlDays": TTL_DAYS,
        "personalDataCollected": False,
        "directAmazonLinks": 0,
        "noBuyOutcome": True,
        "unsafeCommerceBlocked": True,
        "fixedInstallationAffiliateBlocked": True,
    }
    release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def inject(site: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    page = site / TARGET
    if not page.is_file():
        raise FileNotFoundError(f"Affiliate ürün merkezi eksik: {page}")
    text = page.read_text(encoding="utf-8")
    if MARKER in text:
        return {"ok": True, "basePath": base_path, "injected": False, "target": TARGET.as_posix()}
    anchor = '<section class="section" aria-labelledby="priorityTitle">'
    if anchor not in text:
        raise RuntimeError("Affiliate ürün merkezi öncelik bölümü bulunamadı")
    text = text.replace(anchor, router_markup(base_path) + "\n\n" + anchor, 1)
    if "</head>" not in text or "</body>" not in text:
        raise RuntimeError("Affiliate ürün merkezi HTML kapanış etiketleri eksik")
    text = text.replace("</head>", style_block() + "\n</head>", 1)
    text = text.replace("</body>", script_block() + "\n</body>", 1)
    page.write_text(text, encoding="utf-8")
    update_release(site, base_path)
    recompute_checksums(site)
    return {
        "ok": True,
        "basePath": base_path,
        "injected": True,
        "target": TARGET.as_posix(),
        "taskCount": 8,
        "questionCount": 3,
        "resumeTtlDays": TTL_DAYS,
        "directAmazonLinks": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 affiliate ürün merkezine güvenli ihtiyaç yönlendiricisi ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(inject(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
