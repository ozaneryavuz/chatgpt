from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
CANONICAL_PATH='/hesaplama/teknik-devir-kabul-paketi/'
HUB=Path('hesaplama/index.html');PORTAL=Path('elektrik-portali/index.html');GATEWAY=Path('index.html');SHORTLIST=Path('hesaplama/teknik-urun-karsilastirma/index.html');PLAN=Path('hesaplama/elektrik-planim/index.html')
HUB_MARKER='data-alo186-handoff-hub="true"';CARD_MARKER='data-alo186-handoff-card="true"';SECTION_MARKER='data-alo186-handoff-section="true"'
def norm(v:str)->str:
 c=(v or '').strip();return '' if not c or c=='/' else '/'+c.strip('/')
def url(base,route=CANONICAL_PATH):return f'{base}/{route.lstrip("/")}' if base else '/'+route.lstrip('/')
def raise_count(text):return re.sub(r'\d+ çekirdek araç','35 çekirdek araç',text,count=1)
def insert_hub(site,base):
 p=site/HUB;t=raise_count(p.read_text(encoding='utf-8'))
 if HUB_MARKER in t:p.write_text(t,encoding='utf-8');return 0
 card=f'<a class="tool-card" {HUB_MARKER} href="{url(base)}"><span class="eyebrow">Rol bazlı devir · kabul testi · teknik kapsam</span><h2>Teknik Devir ve Kabul Paketi</h2><p>İşletme sahibi, teknik ekip ve satın alma için eksik belgeyi, kabul adımını, satın almama veya profesyonel kapsamı tek pakette oluşturun.</p><b>Devir paketini oluştur →</b></a>'
 t=t.replace('<section id="araclar" class="tool-grid">','<section id="araclar" class="tool-grid">'+card,1);p.write_text(t,encoding='utf-8');return 1
def insert_grid(site,rel,base,gateway=False):
 p=site/rel;t=p.read_text(encoding='utf-8')
 if CARD_MARKER in t:return 0
 href=url(base);card=(f'<a class="card" {CARD_MARKER} href="{href}"><strong>Teknik kararı ekibe devredin ve kabul edin</strong><p>Eksik belge, gerçek yük testi ve kabul adımı kapanmadan sistemi hazır saymayın.</p><span>Devir paketini aç →</span></a>' if gateway else f'<a class="card" {CARD_MARKER} href="{href}"><span class="tag">Takım devri · kabul kanıtı · satın almama</span><h2>Teknik Devir ve Kabul Paketi</h2><p>UPS, jeneratör, GES, EV, koruma ve düşük riskli ürün kararını rol bazlı görev ve kanıt paketiyle paylaşın.</p><b>Paketi oluştur →</b></a>')
 for m in re.finditer(r'<section\b[^>]*>',t,re.I):
  c=re.search(r'class=["\']([^"\']*)["\']',m.group(0),re.I)
  if c and 'grid' in c.group(1).split():t=t[:m.end()]+card+t[m.end():];p.write_text(t,encoding='utf-8');return 1
 return 0
def insert_section(site,rel,base,kind):
 p=site/rel
 if not p.is_file():return 0
 t=p.read_text(encoding='utf-8')
 if SECTION_MARKER in t:return 0
 href=url(base)
 if kind=='shortlist':title='Kısa listeyi teknik ekip veya satın almaya devredin';body='Aday seçimi bittikten sonra kanıt, kabul testi ve takip tarihini rol bazlı JSON paketiyle paylaşın. Mevcut ürün yeterliyse satın almama kararı korunur.'
 else:title='Plan görevini kanıtlı kabul paketine dönüştürün';body='Elektrik Planım’daki görevi işletme sahibi, teknik ekip ve satın alma arasında aynı kapalı veri setiyle devredin; eksik test kapanmadan tamamlandı saymayın.'
 section=f'<section class="content-section" {SECTION_MARKER}><div class="panel"><span class="eyebrow">Takım ve kabul katmanı</span><h2>{title}</h2><p>{body}</p><div class="actions"><a class="btn btn-secondary" href="{href}">Teknik devir paketini oluştur</a></div><small>Kişisel veri, marka, fiyat, stok, puan, satıcı, garanti veya ASIN taşınmaz.</small></div></section>'
 t=t.replace('</main>',section+'</main>',1);p.write_text(t,encoding='utf-8');return 1
def add_offline(site,base):
 p=site/'sw.js';t=p.read_text(encoding='utf-8');m=re.search(r'const CRITICAL=(\[.*?\]);',t,re.S)
 if not m:raise RuntimeError('Service worker CRITICAL dizisi bulunamadı')
 r=json.loads(m.group(1));u=url(base)
 if u in r:return False
 r.append(u);p.write_text(t[:m.start(1)]+json.dumps(r,ensure_ascii=False)+t[m.end(1):],encoding='utf-8');return True
def update_manifest(site,base):
 p=site/'manifest.webmanifest'
 if not p.is_file():return
 d=json.loads(p.read_text(encoding='utf-8'));s=d.setdefault('shortcuts',[]);u=url(base)
 if not any(x.get('url')==u for x in s if isinstance(x,dict)):s.append({'name':'Teknik Devir ve Kabul Paketi','short_name':'Teknik Devir','url':u})
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def update_release(site,base,cards,offline):
 core=site/'alo186-release.json';d=json.loads(core.read_text(encoding='utf-8'));d['technicalHandoff']={'version':1,'route':CANONICAL_PATH,'recordLimit':6,'ttlDays':180,'roles':['owner','technical','procurement'],'commercialFieldsExcluded':['price','stock','rating','seller','warranty','asin']};core.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 pages=site/'pages-release.json';p=json.loads(pages.read_text(encoding='utf-8'));p['technicalHandoff']={'version':1,'route':url(base),'entryCardsInjected':cards,'offline':True,'recordLimit':6,'ttlDays':180}
 if offline:p['offlineCriticalRouteCount']=int(p.get('offlineCriticalRouteCount') or 0)+1
 pages.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def recompute(site):
 p=site/'checksums.sha256'
 if p.exists():p.unlink()
 p.write_text('\n'.join(f'{hashlib.sha256(x.read_bytes()).hexdigest()}  {x.relative_to(site).as_posix()}' for x in sorted(y for y in site.rglob('*') if y.is_file()))+'\n',encoding='utf-8')
def run(site,base):
 base=norm(base);required=site/'hesaplama/teknik-devir-kabul-paketi/index.html'
 if not required.is_file():raise FileNotFoundError(required)
 cards=insert_hub(site,base)+insert_grid(site,PORTAL,base)+insert_grid(site,GATEWAY,base,True)+insert_section(site,SHORTLIST,base,'shortlist')+insert_section(site,PLAN,base,'plan')
 offline=add_offline(site,base);update_manifest(site,base);update_release(site,base,cards,offline);recompute(site)
 return{'ok':True,'basePath':base,'route':url(base),'entryPoints':cards,'offlineAdded':offline}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--site',type=Path,required=True);ap.add_argument('--base-path',default='');a=ap.parse_args();print(json.dumps(run(a.site.resolve(),a.base_path),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
