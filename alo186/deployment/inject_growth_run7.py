from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROUTES = {
    "experiment": "/hesaplama/7-gunluk-cihaz-tuketim-deneyi/",
    "workorder": "/hesaplama/elektrikci-is-emri-ozeti/",
    "bill": "/fatura-analizi",
}
HUB = Path("hesaplama/index.html")
PORTAL = Path("elektrik-portali/index.html")
PRODUCT = Path("amazon-elektrik-urunleri/index.html")
BILL = Path("fatura-analizi/index.html")
HUB_MARKER = 'data-alo186-growth-run7-tools="true"'
PORTAL_MARKER = 'data-alo186-growth-run7-journey="true"'
PRODUCT_MARKER = 'data-alo186-growth-run7-measurement="true"'
JOURNAL_MARKER = 'data-alo186-growth-run7-journal="true"'


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
        f'<a class="tool-card" {HUB_MARKER} href="{public_url(base_path, ROUTES["experiment"])}"><span class="eyebrow">7 gün · watt/kWh · ölçüm güveni</span><h2>Cihaz Tüketim Deneyi</h2><p>Faturadaki artışı tahminle değil, güvenli ve zaman sınırlı cihaz ölçümüyle daraltın.</p><b>Ölçüm planını oluştur →</b></a>'
        f'<a class="tool-card" href="{public_url(base_path, ROUTES["workorder"])}"><span class="eyebrow">Belirti · ölçüm talebi · kapanış kanıtı</span><h2>Elektrikçi İş Emri Özeti</h2><p>Arıza belirtisini kişisel veri vermeden tarafsız kontrol ve kabul kapsamına dönüştürün.</p><b>İş emrini hazırla →</b></a>'
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
    section = f'''<section {PORTAL_MARKER} style="max-width:1120px;margin:34px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#f5f8fd"><span style="font-size:.78rem;font-weight:900;color:#174bb9;text-transform:uppercase;letter-spacing:.06em">Ölç → karşılaştır → doğru uzmana aktar</span><h2 style="color:#071631;margin:.4rem 0">Fatura artışını aylık kayda, cihaz deneyine ve tarafsız iş emrine dönüştürün.</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px"><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['bill'])}#aylik-tuketim-gunlugu"><strong>Aylık kWh Günlüğü</strong><br><span>Fatura tutarı yerine kWh eğilimini yerel kayıtta izleyin.</span></a><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['experiment'])}"><strong>7 Günlük Cihaz Deneyi</strong><br><span>Hangi yükün artışa katkısını ölçülebilir plana çevirin.</span></a><a style="padding:16px;border:1px solid #dce5ef;border-radius:15px;background:#fff;color:#071631;text-decoration:none" href="{public_url(base_path, ROUTES['workorder'])}"><strong>Elektrikçi İş Emri</strong><br><span>Belirti, ölçüm ve kapanış beklentisini aynı kapsamda yazın.</span></a></div></section>'''
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
    section = f'''<section class="section" {PRODUCT_MARKER}><span class="eyebrow">Satın almadan önce ölçüm</span><h2>Enerji ölçer almak yerine önce neyi ve nasıl ölçeceğinizi belirleyin.</h2><p class="lead">7 günlük deney, cihazın priz tipi ölçüme uygun olup olmadığını ayırır. Sabit, yüksek güçlü veya motorlu yüklerde affiliate yolu kapanır; mevcut uygun ölçeriniz varsa yeni ürün önerilmez.</p><div class="actions"><a class="button secondary" href="{public_url(base_path, ROUTES['experiment'])}">7 günlük tüketim deneyini aç</a></div><div class="affiliate-disclosure"><strong>Satış ortaklığı sınırı:</strong> Deney sonucunda yalnız güvenli tak-çalıştır ölçüm ihtiyacı doğrulanırsa kategori rehberine geçilir. Fiyat, stok, puan, satıcı ve garanti ALO186 üzerinde kopyalanmaz.</div></section>'''
    if "</main>" not in text:
        raise RuntimeError("Amazon ürün merkezi main kapanışı bulunamadı")
    path.write_text(text.replace("</main>", section + "</main>", 1), encoding="utf-8")
    return 1


def journal_style() -> str:
    return '''<style data-alo186-growth-run7-journal-style="true">#aylik-tuketim-gunlugu{max-width:1180px;margin:44px auto;padding:28px;border:1px solid #dce5ef;border-radius:24px;background:#fff;box-shadow:0 16px 40px rgba(7,22,49,.08)}#aylik-tuketim-gunlugu h2{color:#071631;font-size:clamp(1.8rem,4vw,2.7rem);margin:.35rem 0}.gr7-note{padding:15px;border-radius:14px;background:#eef4ff;color:#173968}.gr7-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:18px 0}.gr7-grid label{display:grid;gap:6px;font-weight:800}.gr7-grid input,.gr7-grid select{min-height:46px;padding:9px 11px;border:1px solid #9dafc2;border-radius:10px;font:inherit;background:#fff}.gr7-actions{display:flex;flex-wrap:wrap;gap:9px;margin:15px 0}.gr7-actions button,.gr7-actions a{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:9px 14px;border:2px solid #071631;border-radius:10px;background:#071631;color:#fff;font:inherit;font-weight:850;text-decoration:none;cursor:pointer}.gr7-actions .alt{background:#fff;color:#071631}.gr7-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:15px 0}.gr7-metrics div{padding:14px;border-radius:13px;background:#f4f8fd}.gr7-metrics strong{display:block;color:#071631;font-size:1.35rem}.gr7-table{width:100%;border-collapse:collapse}.gr7-table th,.gr7-table td{padding:9px;border-bottom:1px solid #dce5ef;text-align:left}.gr7-small{font-size:.9rem;color:#58677c}.gr7-hidden{display:none!important}@media(max-width:720px){.gr7-grid,.gr7-metrics{grid-template-columns:1fr}.gr7-actions>*{width:100%}.gr7-table{font-size:.86rem}}</style>'''


def journal_section(base_path: str) -> str:
    experiment = public_url(base_path, ROUTES["experiment"])
    return f'''<section id="aylik-tuketim-gunlugu" {JOURNAL_MARKER}><span class="eyebrow">Yeni · kişisel verisiz tekrar ziyaret</span><h2>Aylık Elektrik Tüketim Günlüğü</h2><p>Her ay yalnız dönem ve kWh değerini kaydedin. Tarife, fatura tutarı, adres, abone numarası veya sayaç kimliği tutulmaz. Kayıtlar bu tarayıcıda 400 gün saklanır.</p><div class="gr7-note"><strong>Satın almama sınırı:</strong> Tüketim artışı tek başına yeni cihaz veya enerji ölçer ihtiyacını kanıtlamaz. Önce dönem gün sayısı, kullanım değişikliği ve ölçüm kalitesi kontrol edilir.</div><form id="gr7JournalForm"><div class="gr7-grid"><label>Dönem<input id="gr7Month" type="month" required></label><label>Tüketim (kWh)<input id="gr7Kwh" type="number" min="0" max="100000000" step="0.01" required></label><label>Veri kaynağı<select id="gr7Source"><option value="invoice">Faturadaki dönem kWh değeri</option><option value="meter">Sayaç / enerji yönetim sistemi</option><option value="estimate">Tahmini değer</option></select></label></div><div class="gr7-actions"><button type="submit">Aylık kaydı ekle</button><button id="gr7Clear" class="alt" type="button">Yerel günlüğü sil</button></div></form><section id="gr7Output" class="gr7-hidden" aria-live="polite"><div class="gr7-metrics"><div><span>Son kayıt</span><strong id="gr7Latest">—</strong></div><div><span>Önceki aya göre</span><strong id="gr7Change">—</strong></div><div><span>Son 3 kayıt ortalaması</span><strong id="gr7Average">—</strong></div></div><p id="gr7Insight" class="gr7-note"></p><div style="overflow:auto"><table class="gr7-table"><thead><tr><th>Dönem</th><th>kWh</th><th>Kaynak</th><th></th></tr></thead><tbody id="gr7Rows"></tbody></table></div><div class="gr7-actions"><button id="gr7Export" type="button">JSON günlüğü indir</button><button id="gr7Ics" class="alt" type="button">Gelecek ay hatırlat</button><a class="alt" href="{experiment}">7 günlük cihaz deneyini aç</a></div><p class="gr7-small">Cihaz deneyi sayfasındaki kategori rehberi daha sonra açıkça belirtilmiş Amazon satış ortaklığı bağlantısı içerebilir. Bu günlük doğrudan mağaza bağlantısı göstermez.</p></section></section>'''


def journal_script() -> str:
    return '''<script data-alo186-growth-run7-journal-script="true">(()=>{'use strict';const K='alo186.monthlyKwhJournal.v1',TTL=400*86400000,$=id=>document.getElementById(id),sources={invoice:'Fatura kWh',meter:'Sayaç / EMS',estimate:'Tahmin'};let items=[];function load(){try{const p=JSON.parse(localStorage.getItem(K)||'null');if(!p||p.schema!=='alo186.monthlyKwhJournal.v1'||Date.parse(p.expiresAt)<=Date.now()){localStorage.removeItem(K);return[]}return Array.isArray(p.items)?p.items.filter(x=>/^\\d{4}-\\d{2}$/.test(x.month)&&Number.isFinite(x.kwh)&&x.kwh>=0&&sources[x.source]):[]}catch{return[]}}function save(){localStorage.setItem(K,JSON.stringify({schema:'alo186.monthlyKwhJournal.v1',personalData:false,updatedAt:new Date().toISOString(),expiresAt:new Date(Date.now()+TTL).toISOString(),items}))}function fmt(v){return `${v.toLocaleString('tr-TR',{maximumFractionDigits:2})} kWh`}function download(name,type,text){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),500)}function render(){items.sort((a,b)=>a.month.localeCompare(b.month));$('gr7Output').classList.toggle('gr7-hidden',!items.length);const latest=items.at(-1),prev=items.at(-2);if(!latest)return;$('gr7Latest').textContent=fmt(latest.kwh);const change=prev&&prev.kwh>0?(latest.kwh-prev.kwh)/prev.kwh:null;$('gr7Change').textContent=change===null?'İlk karşılaştırma':`${change>=0?'+':''}${(change*100).toLocaleString('tr-TR',{maximumFractionDigits:1})}%`;const recent=items.slice(-3),avg=recent.reduce((s,x)=>s+x.kwh,0)/recent.length;$('gr7Average').textContent=fmt(avg);let insight='Eğilimi yorumlamadan önce dönem gün sayısını ve kullanım değişikliğini kontrol edin.';if(latest.source==='estimate')insight='Son kayıt tahminidir; karar vermeden önce faturadaki kWh veya uygun ölçümle doğrulayın.';else if(change!==null&&change>=.25)insight='Son kayıt önceki aya göre en az %25 yüksek. Isıtma/soğutma, EV, su ısıtma ve yeni yükleri 7 günlük ölçüm planıyla ayırın.';else if(change!==null&&change<=-.25)insight='Belirgin düşüş var. Dönem gün sayısı, boş kullanım dönemi veya ölçüm kaynağı değişikliğini kontrol edin.';$('gr7Insight').textContent=insight;$('gr7Rows').innerHTML='';[...items].reverse().forEach(x=>{const tr=document.createElement('tr'),td1=document.createElement('td'),td2=document.createElement('td'),td3=document.createElement('td'),td4=document.createElement('td'),b=document.createElement('button');td1.textContent=x.month;td2.textContent=fmt(x.kwh);td3.textContent=sources[x.source];b.type='button';b.textContent='Sil';b.addEventListener('click',()=>{items=items.filter(i=>i.month!==x.month);save();render()});td4.appendChild(b);tr.append(td1,td2,td3,td4);$('gr7Rows').appendChild(tr)})}$('gr7JournalForm')?.addEventListener('submit',e=>{e.preventDefault();const month=$('gr7Month').value,kwh=Number($('gr7Kwh').value),source=$('gr7Source').value;if(!/^\\d{4}-\\d{2}$/.test(month)||!Number.isFinite(kwh)||kwh<0||!sources[source])return;const entry={month,kwh,source};const i=items.findIndex(x=>x.month===month);if(i>=0)items[i]=entry;else items.push(entry);save();render()});$('gr7Clear')?.addEventListener('click',()=>{localStorage.removeItem(K);items=[];render()});$('gr7Export')?.addEventListener('click',()=>download('alo186-aylik-kwh-gunlugu.json','application/json',JSON.stringify({schema:'alo186.monthlyKwhJournal.v1',personalData:false,exportedAt:new Date().toISOString(),items},null,2)));$('gr7Ics')?.addEventListener('click',()=>{const d=new Date();d.setMonth(d.getMonth()+1,3);const y=`${d.getFullYear()}${String(d.getMonth()+1).padStart(2,'0')}${String(d.getDate()).padStart(2,'0')}`;download('alo186-aylik-kwh-hatirlatici.ics','text/calendar',['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Aylik kWh Gunlugu//TR','BEGIN:VEVENT',`DTSTART:${y}T090000`,`DTEND:${y}T093000`,'SUMMARY:Elektrik tüketim kWh kaydını ekle','DESCRIPTION:Fatura tutarı yerine dönem kWh değerini ALO186 aylık günlüğüne ekle.','END:VEVENT','END:VCALENDAR'].join('\\r\\n'))});items=load();render()})();</script>'''


def inject_bill_journal(site: Path) -> int:
    path = site / BILL
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    if JOURNAL_MARKER in text:
        return 0
    if "</head>" not in text or "</main>" not in text or "</body>" not in text:
        raise RuntimeError("Fatura analizi HTML kapanışları bulunamadı")
    text = text.replace("</head>", journal_style() + "</head>", 1)
    text = text.replace("</main>", journal_section("") + "</main>", 1)
    text = text.replace("</body>", journal_script() + "</body>", 1)
    path.write_text(text, encoding="utf-8")
    return 1


def rewrite_bill_base_path(site: Path, base_path: str) -> None:
    if not base_path:
        return
    path = site / BILL
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    plain = journal_section("")
    prefixed = journal_section(base_path)
    if plain in text:
        text = text.replace(plain, prefixed, 1)
        path.write_text(text, encoding="utf-8")


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
        {"name": "Aylık Elektrik Tüketim Günlüğü", "short_name": "kWh Günlüğü", "url": public_url(base_path, ROUTES["bill"]) + "#aylik-tuketim-gunlugu"},
        {"name": "Elektrikçi İş Emri Özeti", "short_name": "İş Emri", "url": public_url(base_path, ROUTES["workorder"])},
    ]
    for item in additions:
        if not any(isinstance(existing, dict) and existing.get("url") == item["url"] for existing in shortcuts):
            shortcuts.append(item)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, cards: int, offline: list[str]) -> None:
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    core["growthRun7"] = {
        "version": 1,
        "routes": [ROUTES["experiment"], ROUTES["workorder"]],
        "enhancedRoute": ROUTES["bill"],
        "rawPersonalDataCollected": False,
        "billAmountCollected": False,
        "monthlyKwhLocalOnly": True,
        "monthlyJournalTtlDays": 400,
        "directAffiliateLinksAdded": 0,
        "affiliateGate": "safe-plug-load-and-measurement-gap-only",
        "unverifiedCommercialFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "providerRanking": False,
        "paidReferralDisclosureRequired": True,
    }
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["growthRun7"] = {
            "version": 1,
            "basePath": base_path,
            "routes": [public_url(base_path, ROUTES["experiment"]), public_url(base_path, ROUTES["workorder"])],
            "enhancedRoute": public_url(base_path, ROUTES["bill"]) + "#aylik-tuketim-gunlugu",
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
    for key in ("experiment", "workorder"):
        target = site / ROUTES[key].strip("/") / "index.html"
        if not target.is_file():
            raise FileNotFoundError(f"Growth run7 rotası artifactta eksik: {target}")
    cards = inject_hub(site, base_path)
    cards += inject_portal(site, base_path)
    cards += inject_product(site, base_path)
    cards += inject_bill_journal(site)
    rewrite_bill_base_path(site, base_path)
    offline = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_release(site, base_path, cards, offline)
    recompute(site)
    return {
        "ok": True,
        "basePath": base_path,
        "routes": [public_url(base_path, ROUTES["experiment"]), public_url(base_path, ROUTES["workorder"])],
        "enhancedRoute": public_url(base_path, ROUTES["bill"]) + "#aylik-tuketim-gunlugu",
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
