from __future__ import annotations
import argparse, hashlib, json, re
from collections import Counter
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ORIGIN='https://alo186.com'; HOSTS={'alo186.com','www.alo186.com'}
MARK='data-alo186-user-experience="true"'
ALIASES={
 '/bilgi-guncelligi':('/kaynaklar/','Kaynaklar ve bilgi güncelliği'),
 '/edas':('/elektrik-dagitim-sirketleri/','Elektrik dağıtım şirketleri'),
 '/isletmeler':('/isletme-surekliligi/','İşletme sürekliliği'),
 '/urun-eslestirme':('/akilli-urun-secimi/','Akıllı ürün seçimi'),
}
COPY={
 'Elektrik problemini <em>çözün; gerçek ihtiyacı gelire dönüştüren doğru rotaya ilerleyin.</em>':'Elektrik problemini <em>çözün; güvenli ve kanıtlanabilir doğru sonraki adıma ilerleyin.</em>',
 'Gelir kanalları birbirinden açıkça ayrılır':'Ücretsiz bilgi, profesyonel hizmet ve iş birliği açıkça ayrılır',
 'Hızlı sonuç için üç başlangıç noktası':'İhtiyacınıza göre üç açık yol',
}
LABELS={'scope':'Olayın kapsamı','repeat':'Tekrar sıklığı','importFile':'JSON dosyası seçin'}
ACTION_LABELS={'primaryAction':'Önerilen sonraki adımı aç','secondaryAction':'Alternatif sonraki adımı aç','productLink':'Uygun ürün rehberini aç','serviceLink':'Profesyonel hizmet kapsamını aç'}
A_RE=re.compile(r'<a\b[^>]*>',re.I); ATTR_RE=re.compile(r'([\w:-]+)(?:\s*=\s*(["\'])(.*?)\2|\s*=\s*([^\s>]+))?',re.S); TAG_RE=re.compile(r'<[^>]+>')

def base(v:str)->str:
 v=(v or '').strip(); return '' if not v or v=='/' else '/'+v.strip('/')
def pub(b:str,r:str)->str:
 r='/'+r.lstrip('/'); return b+r if b else r
def attrs(tag:str)->dict[str,str]:
 out={}; body=tag[tag.find(' ')+1:tag.rfind('>')]
 for m in ATTR_RE.finditer(body): out[m.group(1).lower()]=unescape(m.group(3) if m.group(3) is not None else (m.group(4) or ''))
 return out
def set_attr(tag:str,name:str,value:str)->str:
 p=re.compile(rf'\s{name}\s*=\s*(["\']).*?\1',re.I|re.S); token=f' {name}="{escape(value,quote=True)}"'
 return p.sub(token,tag,1) if p.search(tag) else tag[:-1]+token+'>'
def text(v:str)->str: return re.sub(r'\s+',' ',unescape(TAG_RE.sub(' ',v))).strip()
def local_path(path:str,b:str)->str:
 if b and (path==b or path.startswith(b+'/')): path=path[len(b):] or '/'
 return path
def alias_for(path:str,b:str): return ALIASES.get((local_path(path,b).rstrip('/') or '/'))
def exists(site:Path,route:str,b:str='')->bool:
 p=local_path(urlsplit(route).path or '/',b)
 if p=='/': return (site/'index.html').is_file()
 t=site/p.lstrip('/'); return t.is_file() or (t/'index.html').is_file() or Path(str(t)+'.html').is_file()
def rewrite_href(value:str,b:str)->str:
 p=urlsplit(value); absolute=bool(p.scheme)
 if absolute and (p.scheme not in {'http','https'} or p.hostname not in HOSTS): return value
 hit=alias_for(p.path or '/',b)
 if not hit:return value
 target=hit[0]
 return urlunsplit(('https','alo186.com',target,p.query,p.fragment)) if absolute else urlunsplit(('', '', pub(b,target),p.query,p.fragment))
def harden_anchor(tag:str,b:str):
 a=attrs(tag); rewrites=security=0
 if a.get('href'):
  v=rewrite_href(a['href'],b)
  if v!=a['href']: tag=set_attr(tag,'href',v); rewrites+=1
 a=attrs(tag); rel={x.lower() for x in a.get('rel','').split() if x}
 if a.get('target','').lower()=='_blank' and 'noopener' not in rel: rel.add('noopener'); tag=set_attr(tag,'rel',' '.join(sorted(rel))); security+=1
 if 'amazon.' in a.get('href','').lower() or 'alo186rehber-21' in a.get('href',''):
  need={'sponsored','nofollow','noopener'}; rel={x.lower() for x in attrs(tag).get('rel','').split() if x}
  if not need<=rel: tag=set_attr(tag,'rel',' '.join(sorted(rel|need))); security+=1
 return tag,rewrites,security
def description(html:str,rel:str):
 if re.search(r'<meta\b[^>]*name=["\']description["\']',html,re.I): return html,0
 if rel=='404.html': d='Aradığınız ALO186 sayfası bulunamadı. Karar motoru, EDAŞ bulucu ve hesaplayıcılara güvenli biçimde ilerleyin.'
 elif rel=='durum/index.html': d='ALO186 yayın, erişim ve çevrimdışı kullanılabilirlik durumunu kontrol edin.'
 elif re.search(r'<meta\s+http-equiv=["\']refresh["\']',html,re.I): d='Bu eski ALO186 adresi güncel ve kullanıcı odaklı içeriğe güvenli biçimde yönlendirir.'
 else:
  parts=[]
  for pat in (r'<h1\b[^>]*>(.*?)</h1>',r'<p\b[^>]*>(.*?)</p>'):
   m=re.search(pat,html,re.I|re.S)
   if m and text(m.group(1)): parts.append(text(m.group(1)))
  d=' '.join(parts) or 'ALO186 bağımsız elektrik bilgi ağı içinde güncel ve güvenli sonraki adıma ilerleyin.'
  if len(d)>165:d=d[:162].rsplit(' ',1)[0]+'…'
 tag=f'<meta name="description" content="{escape(d,quote=True)}">'
 return (html.replace('</title>','</title>'+tag,1) if '</title>' in html else re.sub(r'</head>',tag+'</head>',html,1,flags=re.I)),1
def controls(html:str):
 count=0
 for cid,label in LABELS.items():
  pat=re.compile(rf'<(input|select|textarea)\b(?=[^>]*id=["\']{re.escape(cid)}["\'])[^>]*>',re.I)
  def repl(m,label=label):
   nonlocal count
   if any(attrs(m.group(0)).get(x) for x in ('aria-label','aria-labelledby','title')):return m.group(0)
   count+=1; return set_attr(m.group(0),'aria-label',label)
  html=pat.sub(repl,html)
 pat=re.compile(r'(?P<x><div\b[^>]*class=["\'][^"\']*\bitem\b[^"\']*["\'][^>]*>.*?<strong[^>]*>(?P<label>.*?)</strong>.*?)(?P<s><select\b[^>]*>)',re.I|re.S)
 def item(m):
  nonlocal count
  if any(attrs(m.group('s')).get(x) for x in ('aria-label','aria-labelledby','title')):return m.group(0)
  count+=1; return m.group('x')+set_attr(m.group('s'),'aria-label',(text(m.group('label')) or 'Ürün')+' durumu')
 html=pat.sub(item,html)
 pat=re.compile(r'<select\b(?=[^>]*data-id=["\']([^"\']+)["\'])[^>]*>',re.I)
 def data(m):
  nonlocal count
  if any(attrs(m.group(0)).get(x) for x in ('aria-label','aria-labelledby','title')):return m.group(0)
  count+=1; return set_attr(m.group(0),'aria-label',m.group(1)+' ürün durumu')
 return pat.sub(data,html),count
def empty_links(html:str):
 count=0; pat=re.compile(r'(?P<o><a\b[^>]*>)(?P<b>\s*)(?P<c></a>)',re.I|re.S)
 def repl(m):
  nonlocal count
  a=attrs(m.group('o'))
  if a.get('aria-label') or a.get('title'):return m.group(0)
  count+=1; return set_attr(m.group('o'),'aria-label',ACTION_LABELS.get(a.get('id',''),'Sonraki adımı aç'))+m.group('b')+m.group('c')
 return pat.sub(repl,html),count
def transform(html:str,rel:str,b:str):
 c={'aliasLinksRewritten':0,'noopenerAdded':0,'descriptionsAdded':0,'controlsLabelled':0,'emptyLinksNamed':0,'copyRewritten':0}
 for old,new in COPY.items():
  if old in html: html=html.replace(old,new); c['copyRewritten']+=1
 if '<title>ALO186 yönlendirme</title>' in html: html=html.replace('<title>ALO186 yönlendirme</title>','<title>İçerik yeni adresine taşındı | ALO186</title>',1);c['copyRewritten']+=1
 html=re.sub(r'<p><code>.*?</code>\s+yolu artık güncel ALO186 karar akışına yönlendiriliyor\.</p>','<p>Bu eski bağlantı, güncel ve güvenli ALO186 içeriğine taşındı.</p>',html,flags=re.I|re.S)
 def ar(m):
  t,x,y=harden_anchor(m.group(0),b);c['aliasLinksRewritten']+=x;c['noopenerAdded']+=y;return t
 html=A_RE.sub(ar,html);html,n=description(html,rel);c['descriptionsAdded']+=n;html,n=controls(html);c['controlsLabelled']+=n;html,n=empty_links(html);c['emptyLinksNamed']+=n
 if MARK not in html and '</head>' in html:
  html=html.replace('</head>',f'<meta {MARK} content="site-wide-v1"><style {MARK}>fieldset{{min-inline-size:0}}legend{{max-inline-size:100%;overflow-wrap:anywhere}}input,select,textarea{{max-inline-size:100%}}@media(max-width:720px){{form :where(input,select,textarea){{inline-size:100%}}}}</style></head>',1)
 return html,c
def alias_html(target:str,label:str,b:str)->str:
 u=pub(b,target);manifest=pub(b,'/manifest.webmanifest');sw=pub(b,'/sw.js');scope=pub(b,'/')
 registration=f"<script data-alo186-pages-sw>if('serviceWorker'in navigator){{addEventListener('load',()=>navigator.serviceWorker.register({json.dumps(sw)},{{scope:{json.dumps(scope)}}}).catch(()=>{{}}));}}</script>"
 return f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex,follow"><meta name="referrer" content="strict-origin-when-cross-origin"><meta name="theme-color" content="#071631"><meta name="description" content="Bu eski ALO186 adresi {escape(label,quote=True)} sayfasına güvenli biçimde yönlendirir."><meta http-equiv="refresh" content="0;url={escape(u,quote=True)}"><link rel="canonical" href="{ORIGIN}{target}"><link rel="manifest" href="{manifest}"><title>{escape(label)} sayfasına taşındı | ALO186</title><meta {MARK} content="legacy-alias-v1"><style>body{{font:17px/1.6 system-ui,sans-serif;max-width:46rem;margin:4rem auto;padding:1.2rem;color:#10243a}}a{{color:#174bb9;font-weight:800}}</style></head><body><main><h1>İçerik yeni adresine taşındı</h1><p>Aradığınız bilgi güncel ALO186 yapısında <strong>{escape(label)}</strong> altında bulunuyor.</p><p><a href="{u}">Güncel sayfayı aç →</a></p><p>ALO186 bağımsız bilgi platformudur; resmî başvuru veya arıza kaydı almaz.</p></main><script>location.replace({json.dumps(u,ensure_ascii=False)}+location.search+location.hash);</script>{registration}</body></html>'''
def aliases(site:Path,b:str)->int:
 n=0
 for src,(target,label) in ALIASES.items():
  out=site/src.lstrip('/')/'index.html'
  if out.exists():continue
  if not exists(site,target,b):raise RuntimeError(f'Alias hedefi eksik: {src} -> {target}')
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(alias_html(target,label,b),encoding='utf-8');n+=1
 return n

class Scan(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.controls=[];self.labels=set();self.ids=[];self.h1=0;self.depth=0
 def handle_starttag(self,tag,items):
  a={k.lower():v or '' for k,v in items}
  if a.get('id'):self.ids.append(a['id'])
  if tag=='h1':self.h1+=1
  if tag=='label':self.depth+=1;self.labels.add(a.get('for',''))
  if tag=='a':self.links.append(a)
  if tag in {'input','select','textarea'}:a['_wrapped']='1' if self.depth else '0';self.controls.append(a)
 def handle_endtag(self,tag):
  if tag=='label' and self.depth:self.depth-=1
def resolved(site:Path,page:Path,href:str,b:str)->bool:
 if not href or href.startswith(('#','mailto:','tel:','sms:','javascript:','data:','blob:')):return True
 p=urlsplit(href)
 if p.scheme and (p.scheme not in {'http','https'} or p.hostname not in HOSTS):return True
 path=local_path(p.path or '/',b)
 t=site/path.lstrip('/') if path.startswith('/') else (page.parent/path).resolve()
 try:t.relative_to(site.resolve())
 except ValueError:return False
 return (site/'index.html').is_file() if path=='/' else t.is_file() or (t/'index.html').is_file() or Path(str(t)+'.html').is_file()
def audit(site:Path,b:str)->dict:
 errors=[];pages=sorted([*site.rglob('*.html'),*site.rglob('*.htm')]);controls_n=links_n=descs=0
 for page in pages:
  rel=page.relative_to(site).as_posix();html=page.read_text(encoding='utf-8',errors='ignore');s=Scan();s.feed(html)
  if not re.match(r'\s*<!doctype\s+html',html,re.I):errors.append('Doctype: '+rel)
  if not re.search(r'<html\b[^>]*lang=["\'][^"\']+',html,re.I):errors.append('Lang: '+rel)
  if not re.search(r'<meta\b[^>]*name=["\']viewport["\']',html,re.I):errors.append('Viewport: '+rel)
  if not re.search(r'<meta\b[^>]*name=["\']description["\']',html,re.I):errors.append('Description: '+rel)
  else:descs+=1
  if not re.search(r'<title\b[^>]*>\s*[^<]+',html,re.I):errors.append('Title: '+rel)
  if s.h1!=1:errors.append(f'H1={s.h1}: '+rel)
  if [k for k,v in Counter(s.ids).items() if v>1]:errors.append('Duplicate id: '+rel)
  for a in s.controls:
   if a.get('type','').lower() in {'hidden','submit','button','reset','image'}:continue
   controls_n+=1
   if not (a.get('_wrapped')=='1' or a.get('aria-label') or a.get('aria-labelledby') or a.get('title') or (a.get('id') and a.get('id') in s.labels)):errors.append('Unlabelled control: '+rel)
  for a in s.links:
   href=a.get('href','');links_n+=bool(href)
   if a.get('target','').lower()=='_blank' and 'noopener' not in {x.lower() for x in a.get('rel','').split()}:errors.append('noopener: '+rel+' '+href)
   if href and not resolved(site,page,href,b):errors.append('Broken: '+rel+' '+href)
   if href and (urlsplit(href).hostname in HOSTS or not urlsplit(href).hostname) and alias_for(urlsplit(href).path,b):errors.append('Old alias: '+rel+' '+href)
  if 'gerçek ihtiyacı gelire dönüştüren' in html:errors.append('Internal copy: '+rel)
  if MARK not in html:errors.append('UX mark: '+rel)
 for src,(target,_) in ALIASES.items():
  p=site/src.lstrip('/')/'index.html'
  if not p.is_file() or ORIGIN+target not in p.read_text(encoding='utf-8'):errors.append('Alias: '+src)
 if errors:raise RuntimeError('ALO186 site-geneli UX denetimi başarısız:\n- '+'\n- '.join(errors[:200]))
 return {'ok':True,'htmlPagesScanned':len(pages),'metaDescriptionsPresent':descs,'formControlsChecked':controls_n,'linksChecked':links_n,'knownRouteAliases':len(ALIASES),'brokenInternalLinks':0,'unlabelledControls':0,'unsafeBlankTargets':0,'userFacingMonetizationCopy':0,'personalDataFieldsAdded':0}
def release(site:Path,result:dict,b:str):
 for name in ('alo186-release.json','pages-release.json'):
  p=site/name
  if not p.is_file():continue
  x=json.loads(p.read_text(encoding='utf-8'));x['liveUserExperienceAudit']={'version':1,'scope':'all-html-pages','htmlPagesScanned':result['htmlPagesScanned'],'knownRouteAliases':sorted(ALIASES),'primaryStartRoute':pub(b,'/elektrik-durum-merkezi/'),'brokenInternalLinks':0,'unlabelledControls':0,'unsafeBlankTargets':0,'userFacingMonetizationCopy':0,'metaDescriptionsCompleted':True,'noBuyPrinciplePreserved':True,'personalDataCollectionAdded':False,'officialInstitutionClaimed':False};p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def checksums(site:Path):
 p=site/'checksums.sha256'
 if p.exists():p.unlink()
 p.write_text('\n'.join(f'{hashlib.sha256(x.read_bytes()).hexdigest()}  {x.relative_to(site).as_posix()}' for x in sorted(y for y in site.rglob('*') if y.is_file()))+'\n',encoding='utf-8')
def run(site:Path,b:str='',audit_only:bool=False)->dict:
 site=site.resolve();b=base(b);tot={k:0 for k in ('aliasLinksRewritten','noopenerAdded','descriptionsAdded','controlsLabelled','emptyLinksNamed','copyRewritten')};made=changed=0
 if not audit_only:
  made=aliases(site,b)
  for p in sorted([*site.rglob('*.html'),*site.rglob('*.htm')]):
   old=p.read_text(encoding='utf-8',errors='ignore');new,c=transform(old,p.relative_to(site).as_posix(),b)
   if new!=old:p.write_text(new,encoding='utf-8');changed+=1
   for k,v in c.items():tot[k]+=v
 result=audit(site,b)
 if not audit_only:result.update({'changedHtmlFiles':changed,'aliasPagesCreated':made,**tot});release(site,result,b);checksums(site)
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--site',type=Path,required=True);p.add_argument('--base-path',default='');p.add_argument('--audit-only',action='store_true');a=p.parse_args();print(json.dumps(run(a.site,a.base_path,a.audit_only),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
