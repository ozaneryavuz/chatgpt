from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

MEASUREMENT_ID_RE = re.compile(r"^G-[A-Z0-9]{6,20}$")
MARKER = 'data-alo186-ga4-consent="true"'
REPORT_FILE = "ga4-release.json"
CONSENT_STORAGE_KEY = "alo186_analytics_consent_v1"
CONSENT_TTL_DAYS = 180


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + str(route or "").lstrip("/")
    return f"{base_path}{route}" if base_path else route


def validate_measurement_id(value: str) -> str:
    measurement_id = str(value or "").strip().upper()
    if measurement_id and not MEASUREMENT_ID_RE.fullmatch(measurement_id):
        raise ValueError(
            "GA4 measurement ID geçersiz; G- ile başlayan 6-20 büyük harf/rakam bekleniyor."
        )
    return measurement_id


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def consent_bundle(measurement_id: str, cookie_policy_url: str, base_path: str = "") -> str:
    mid = _json(measurement_id)
    policy = _json(cookie_policy_url)
    storage_key = _json(CONSENT_STORAGE_KEY)
    base = _json(normalize_base_path(base_path))
    ttl_ms = CONSENT_TTL_DAYS * 24 * 60 * 60 * 1000
    return fr'''<!-- ALO186 GA4: kullanıcı onayı olmadan Google ağına istek gönderilmez -->
<style {MARKER}>
.alo186-consent{{position:fixed;z-index:2147483000;inset:auto 12px 12px;max-width:760px;margin:auto;padding:18px;border:1px solid #cbd7e6;border-radius:18px;background:#fff;color:#10243a;box-shadow:0 18px 60px rgba(7,22,49,.24);font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
.alo186-consent[hidden]{{display:none!important}}.alo186-consent strong{{display:block;font-size:1.08rem;margin-bottom:6px}}.alo186-consent p{{margin:0 0 12px}}.alo186-consent-actions{{display:flex;flex-wrap:wrap;gap:10px}}.alo186-consent button,.alo186-consent a,.alo186-consent-settings{{min-height:44px;padding:10px 14px;border:2px solid #174bb9;border-radius:12px;background:#fff;color:#103f9b;font:700 15px/1.2 system-ui,-apple-system,Segoe UI,sans-serif;display:inline-flex;align-items:center;justify-content:center;text-decoration:none;cursor:pointer}}.alo186-consent button:focus-visible,.alo186-consent a:focus-visible,.alo186-consent-settings:focus-visible{{outline:4px solid #ffbf47;outline-offset:3px}}.alo186-consent-settings{{position:fixed;z-index:2147482999;right:12px;bottom:12px;display:none}}.alo186-consent-settings[data-visible="true"]{{display:inline-flex}}@media(max-width:620px){{.alo186-consent{{inset:auto 8px 8px;padding:16px}}.alo186-consent-actions>*{{flex:1 1 145px}}}}
</style>
<div class="alo186-consent" id="alo186-consent" role="dialog" aria-labelledby="alo186-consent-title" aria-describedby="alo186-consent-copy" hidden>
  <strong id="alo186-consent-title">Analitik tercihiniz</strong>
  <p id="alo186-consent-copy">ALO186'i geliştirmek için Google Analytics yalnız açık onayınızdan sonra yüklenir. Reddederseniz site aynı şekilde çalışır ve Google analitik etiketi başlatılmaz.</p>
  <div class="alo186-consent-actions">
    <button type="button" data-alo186-consent-choice="denied">Yalnız gerekli</button>
    <button type="button" data-alo186-consent-choice="granted">Analitiğe izin ver</button>
    <a href={policy}>Ayrıntılar</a>
  </div>
</div>
<button type="button" class="alo186-consent-settings" id="alo186-consent-settings" aria-controls="alo186-consent">Çerez ayarları</button>
<script {MARKER}>
(function(){{
  'use strict';
  const ID={mid};
  const STORAGE_KEY={storage_key};
  const BASE={base};
  const TTL={ttl_ms};
  const banner=document.getElementById('alo186-consent');
  const settings=document.getElementById('alo186-consent-settings');
  let loaded=false;
  window.dataLayer=window.dataLayer||[];
  window.gtag=window.gtag||function(){{window.dataLayer.push(arguments);}};
  window.gtag('consent','default',{{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',wait_for_update:500}});
  window.gtag('set','allow_google_signals',false);
  window.gtag('set','allow_ad_personalization_signals',false);

  function readChoice(){{
    try{{
      const value=JSON.parse(localStorage.getItem(STORAGE_KEY)||'null');
      if(!value||!['granted','denied'].includes(value.choice)||Date.now()>Number(value.expiresAt||0))return null;
      return value.choice;
    }}catch(_error){{return null;}}
  }}
  function writeChoice(choice){{
    try{{localStorage.setItem(STORAGE_KEY,JSON.stringify({{choice:choice,savedAt:Date.now(),expiresAt:Date.now()+TTL}}));}}catch(_error){{}}
  }}
  function sanitizedLocation(){{
    const url=new URL(location.href);
    const kept=new URLSearchParams();
    ['utm_source','utm_medium','utm_campaign','utm_content','utm_term'].forEach(function(key){{
      const value=(url.searchParams.get(key)||'').trim().slice(0,100);
      if(value&&/^[\p{{L}}\p{{N}} _.,+\-/]+$/u.test(value))kept.set(key,value);
    }});
    return url.origin+url.pathname+(kept.toString()?'?'+kept.toString():'');
  }}
  function loadAnalytics(){{
    if(loaded||window['ga-disable-'+ID])return;
    loaded=true;
    window.gtag('consent','update',{{analytics_storage:'granted',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'}});
    const script=document.createElement('script');
    script.async=true;
    script.src='https://www.googletagmanager.com/gtag/js?id='+encodeURIComponent(ID);
    script.setAttribute('data-alo186-ga4-loader','true');
    document.head.appendChild(script);
    window.gtag('js',new Date());
    window.gtag('config',ID,{{send_page_view:false,page_location:sanitizedLocation(),page_path:location.pathname,page_title:document.title,allow_google_signals:false,allow_ad_personalization_signals:false}});
    window.gtag('event','page_view',{{page_location:sanitizedLocation(),page_path:location.pathname,page_title:document.title}});
  }}
  function clearAnalyticsCookies(){{
    const names=document.cookie.split(';').map(function(item){{return item.split('=')[0].trim();}}).filter(function(name){{return name==='_ga'||name.startsWith('_ga_');}});
    const domains=['',location.hostname,location.hostname.replace(/^www\./,''),'.'+location.hostname.replace(/^www\./,'')];
    names.forEach(function(name){{domains.forEach(function(domain){{document.cookie=name+'=; Max-Age=0; path=/; SameSite=Lax'+(domain?'; domain='+domain:'');}});}});
  }}
  function setChoice(choice){{
    writeChoice(choice);
    banner.hidden=true;
    settings.dataset.visible='true';
    if(choice==='granted'){{window['ga-disable-'+ID]=false;loadAnalytics();}}
    else{{window['ga-disable-'+ID]=true;window.gtag('consent','update',{{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'}});clearAnalyticsCookies();}}
  }}
  function classifyLink(anchor){{
    const raw=anchor.getAttribute('href')||'';
    let url;
    try{{url=new URL(raw,location.href);}}catch(_error){{return null;}}
    const rel=(anchor.getAttribute('rel')||'').toLowerCase();
    const host=url.hostname.toLowerCase();
    if(!['http:','https:','tel:'].includes(url.protocol))return null;
    const path=url.pathname.toLowerCase();
    const logicalPath=BASE&&(path===BASE||path.startsWith(BASE+'/'))?(path.slice(BASE.length)||'/'):path;
    if(url.protocol==='tel:'&&url.pathname.replace(/\D/g,'')==='186')return ['call_186_click','official_phone'];
    if(url.protocol==='tel:')return null;
    if(rel.includes('sponsored')||host.includes('amazon.'))return ['affiliate_click','amazon'];
    if(url.origin!==location.origin)return ['outbound_click',host.slice(0,80)];
    if(logicalPath.startsWith('/edas-bul'))return ['edas_finder_open','internal'];
    if(logicalPath.startsWith('/karar-motoru')||logicalPath.startsWith('/elektrik-durum-merkezi'))return ['decision_engine_open','internal'];
    if(logicalPath.startsWith('/hesaplama/'))return ['calculator_open',logicalPath.split('/').filter(Boolean).slice(0,2).join('_').slice(0,80)];
    return null;
  }}
  function track(name,params){{
    if(readChoice()!=='granted'||!loaded||!/^[a-z][a-z0-9_]{{0,39}}$/.test(name))return;
    const safe={{}};
    ['destination_type','route_group','action_type','content_group'].forEach(function(key){{
      const value=String((params||{{}})[key]||'').trim().slice(0,80);
      if(value&&/^[\p{{L}}\p{{N}} _./-]+$/u.test(value))safe[key]=value;
    }});
    window.gtag('event',name,safe);
  }}
  window.alo186Analytics={{track:track,getConsent:readChoice,setConsent:setChoice,measurementId:ID}};
  document.addEventListener('click',function(event){{
    const button=event.target.closest('[data-alo186-consent-choice]');
    if(button){{setChoice(button.dataset.alo186ConsentChoice);return;}}
    const anchor=event.target.closest('a[href]');
    if(!anchor)return;
    const classified=classifyLink(anchor);
    if(classified)track(classified[0],{{destination_type:classified[1],route_group:location.pathname.split('/').filter(Boolean)[0]||'home'}});
  }},{{capture:true}});
  settings.addEventListener('click',function(){{banner.hidden=false;banner.querySelector('button').focus();}});
  const choice=readChoice();
  if(choice==='granted'){{settings.dataset.visible='true';loadAnalytics();}}
  else if(choice==='denied'){{window['ga-disable-'+ID]=true;settings.dataset.visible='true';}}
  else banner.hidden=false;
}})();
</script>'''


def inject_html(html: str, bundle: str) -> tuple[str, bool]:
    if MARKER in html:
        return html, False
    match = re.search(r"</body\s*>", html, flags=re.IGNORECASE)
    if not match:
        return html, False
    return html[: match.start()] + bundle + "\n" + html[match.start() :], True


def update_legal_copy(site: Path, base_path: str) -> list[str]:
    del base_path  # Fiziksel artifact rotaları sabittir; public URL yalnız banner bağlantısında kullanılır.
    changed: list[str] = []
    replacements: dict[Path, list[tuple[str, str]]] = {
        site / "yasal" / "cerez" / "index.html": [
            (
                "ALO186 reklam çerezi veya davranışsal hedefleme kullanmaz. Site içindeki temel yönlendirmelerin yararını ölçmek için çerez bırakmayan ve kalıcı cihaz ya da oturum kimliği üretmeyen günlük toplu sayaçlar kullanılır.",
                "ALO186 davranışsal hedefleme veya reklam çerezi kullanmaz. Google Analytics 4 yalnız kullanıcı “Analitiğe izin ver” seçeneğini etkinleştirdiğinde yüklenir; ret hâlinde Google etiketi ve analitik çerezleri çalıştırılmaz. Tercih, birinci taraf yerel depolamada 180 gün saklanır ve Çerez ayarları düğmesinden değiştirilebilir.",
            ),
            (
                "Bu ölçüm; olay türü, herkese açık sayfa sınıfı ve hazırlık planı gibi sınırlı kategorilerle çalışır. Serbest metin, tam URL sorgusu, e-posta, telefon, açık adres, abonelik bilgisi veya hassas konum ölçüme eklenmez.",
                "İzin verildiğinde Google Analytics 4; sayfa görüntüleme, trafik kaynağı, cihaz ve tarayıcı sınıfı, yaklaşık bölge ile önceden tanımlı etkileşim olaylarını ölçebilir. Serbest metin, form içeriği, e-posta, telefon, açık adres, abonelik bilgisi, hassas konum ve izin verilen UTM alanları dışındaki URL sorguları gönderilmez. Google Analytics tarafından kullanılan _ga ve _ga_<ölçüm-kimliği> analitik çerezleri en fazla iki yıl saklanabilir.",
            ),
        ],
        site / "yasal" / "kvkk-aydinlatma" / "index.html": [
            (
                "Site yararını ve yönlendirme akışını geliştirmek için çerezsiz toplu olay sayaçları kullanılabilir. Olay türü ile herkese açık sayfa sınıfı, şirket veya hazırlık planı gibi sınırlı kategoriler günlük toplam sayıya dönüştürülür; kullanıcı ya da oturum kimliği, tam URL sorgusu, form metni, e-posta, telefon, açık adres ve hassas konum bu ölçüm kaydına eklenmez.",
                "Kullanıcı analitiğe açık onay verirse Google Analytics 4; sayfa görüntüleme, trafik kaynağı, cihaz ve tarayıcı sınıfı, yaklaşık bölge ile yalnız önceden tanımlı etkileşim olaylarını işleyebilir. Serbest metin, form içeriği, e-posta, telefon, açık adres, abonelik bilgisi, hassas konum ve izin verilen UTM alanları dışındaki URL sorguları ölçüme gönderilmez. Rıza verilmezse Google etiketi yüklenmez; tercih Çerez ayarları düğmesinden geri alınabilir.",
            ),
            (
                "Günlük toplu kullanım sayaçları hizmeti geliştirme amacıyla en fazla 90 gün saklanır. Bunlar kişi veya cihaz profili oluşturmak, davranışsal reklam göstermek ya da tekil kullanıcıyı izlemek için kullanılmaz.",
                "Google Analytics ölçümü yalnız açık rıza sonrasında etkin olur. Google sinyalleri, reklam depolaması ve reklam kişiselleştirme kapalıdır; Analytics kullanıcı ve olay düzeyi veri saklama ayarı iki ayla sınırlandırılır. Kullanıcı tercihlerini her zaman geri alabilir ve tarayıcısındaki analitik çerezleri daha erken silebilir.",
            ),
        ],
    }
    for path, pairs in replacements.items():
        if not path.is_file():
            raise FileNotFoundError(f"GA4 yasal açıklama rotası eksik: {path.relative_to(site)}")
        html = path.read_text(encoding="utf-8")
        page_changed = False
        for old, new in pairs:
            if new in html:
                continue
            if old not in html:
                raise RuntimeError(f"GA4 yasal açıklama ankrajı bulunamadı: {path.relative_to(site)}")
            html = html.replace(old, new, 1)
            page_changed = True
        if page_changed:
            path.write_text(html, encoding="utf-8")
            changed.append(path.relative_to(site).as_posix())
    return changed


def update_release(path: Path, *, enabled: bool, measurement_id: str, html_count: int, legal_pages: list[str]) -> None:
    if not path.is_file():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["analytics"] = {
        "provider": "Google Analytics 4" if enabled else None,
        "enabled": enabled,
        "measurementId": measurement_id if enabled else None,
        "consentMode": "basic-opt-in" if enabled else "disabled",
        "tagLoadsBeforeConsent": False,
        "advertisingStorage": "denied",
        "googleSignals": False,
        "adPersonalization": False,
        "queryStringPolicy": "utm-allowlist-only",
        "consentPreferenceTtlDays": CONSENT_TTL_DAYS,
        "requiredUserAndEventDataRetentionMonths": 2 if enabled else None,
        "instrumentedHtmlCount": html_count,
        "legalPagesUpdated": legal_pages,
    }
    quality = payload.get("liveTechnicalQuality")
    if isinstance(quality, dict):
        quality["personalDataCollectionAdded"] = enabled
        quality["directPersonalDataFieldsAdded"] = False
        quality["analyticsRequiresExplicitOptIn"] = enabled
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute_checksums(site: Path) -> None:
    checksum = site / "checksums.sha256"
    if checksum.exists():
        checksum.unlink()
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(site).as_posix()}"
        for path in sorted(item for item in site.rglob("*") if item.is_file())
    ]
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(site: Path, base_path: str, measurement_id: str) -> dict:
    site = site.resolve()
    if not site.is_dir():
        raise FileNotFoundError(f"Pages artifactı bulunamadı: {site}")
    base_path = normalize_base_path(base_path)
    measurement_id = validate_measurement_id(measurement_id)
    enabled = bool(measurement_id)
    html_count = 0
    changed_count = 0
    instrumented_count = 0
    legal_pages: list[str] = []

    if enabled:
        policy_url = public_url(base_path, "/yasal/cerez")
        bundle = consent_bundle(measurement_id, policy_url, base_path)
        for path in sorted(site.rglob("*.html")):
            original = path.read_text(encoding="utf-8", errors="ignore")
            updated, changed = inject_html(original, bundle)
            html_count += 1
            if MARKER in updated:
                instrumented_count += 1
            if changed:
                path.write_text(updated, encoding="utf-8")
                changed_count += 1
        if html_count == 0 or instrumented_count != html_count:
            raise RuntimeError("GA4 consent katmanı bütün HTML sayfalarına enjekte edilemedi.")
        legal_pages = update_legal_copy(site, base_path)

    for name in ("alo186-release.json", "pages-release.json"):
        update_release(
            site / name,
            enabled=enabled,
            measurement_id=measurement_id,
            html_count=instrumented_count,
            legal_pages=legal_pages,
        )

    report = {
        "ok": True,
        "enabled": enabled,
        "measurementId": measurement_id if enabled else None,
        "basePath": base_path,
        "htmlCount": html_count,
        "instrumentedHtmlCount": instrumented_count,
        "newlyInjectedHtmlCount": changed_count,
        "legalPagesUpdated": legal_pages,
        "tagLoadsBeforeConsent": False,
        "advertisingStorage": "denied",
        "googleSignals": False,
        "adPersonalization": False,
        "queryStringPolicy": "utm-allowlist-only",
        "consentPreferenceTtlDays": CONSENT_TTL_DAYS,
        "requiredUserAndEventDataRetentionMonths": 2 if enabled else None,
    }
    (site / REPORT_FILE).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    recompute_checksums(site)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 Pages artifactına açık onaylı GA4 ölçüm katmanı ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    parser.add_argument("--measurement-id", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path, args.measurement_id), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
