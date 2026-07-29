from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from inject_growth_run16 import run as run_growth_run16

ROUTES={"ev":"/hesaplama/ev-sarj-kablosu-saglik-gunlugu/","pv":"/hesaplama/ges-panel-temizlik-karar-gunlugu/","ground":"/hesaplama/topraklama-olcum-trend-gunlugu/"}
SOURCES={k:f"alo186/{v.strip('/')}/index.html" for k,v in ROUTES.items()}
TARGETS={
 Path("hesaplama/index.html"):'data-alo186-growth-run15-tools="true"',
 Path("elektrik-portali/index.html"):'data-alo186-growth-run15-safety="true"',
 Path("akilli-urun-secimi/index.html"):'data-alo186-growth-run15-affiliate="true"',
 Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html"):'data-alo186-growth-run15-service="true"',
}

def base(v:str)->str:
 v=str(v or "").strip(); return "" if not v or v=="/" else "/"+v.strip("/")
def url(b:str,r:str)->str:
 r="/"+r.lstrip("/"); return b+r if b else r
def inject(path:Path,marker:str,html:str)->int:
 if not path.is_file(): return 0
 t=path.read_text(encoding="utf-8")
 if marker in t: return 0
 if "</main>" not in t: raise RuntimeError(path)
 path.write_text(t.replace("</main>",html+"</main>",1),encoding="utf-8"); return 1

def entries(site:Path,b:str)->int:
 ev,pv,g=(url(b,ROUTES[k]) for k in ("ev","pv","ground"))
 blocks=[
  f'<section {TARGETS[Path("hesaplama/index.html")]}><h2>Güven ve tekrar ziyaret araçları</h2><a href="{ev}">EV kablo sağlığı</a><a href="{pv}">GES temizlik kararı</a><a href="{g}">Topraklama trendi</a></section>',
  f'<section {TARGETS[Path("elektrik-portali/index.html")]}><h2>Güvenlik ve ölçüm sınırı</h2><a href="{ev}">EV kablo olayı</a><a href="{g}">Topraklama trendi</a></section>',
  f'<section {TARGETS[Path("akilli-urun-secimi/index.html")]}><h2>Affiliate öncesi güven kapısı</h2><a href="{ev}">Type 2 kablo kararını doğrula</a></section>',
  f'<section {TARGETS[Path("kurumsal-elektrik-surekliligi-on-degerlendirme/index.html")]}><h2>Kanıtlı O&amp;M ve ölçüm</h2><a href="{pv}">GES O&amp;M</a><a href="{g}">Topraklama ölçümü</a></section>',
 ]
 return sum(inject(site/p,m,h) for (p,m),h in zip(TARGETS.items(),blocks))

def sitemap(site:Path)->None:
 p=site/"sitemap.xml"; t=p.read_text(encoding="utf-8")
 for r in ROUTES.values():
  loc=f"https://www.alo186.com{r}"
  if f"<loc>{loc}</loc>" not in t: t=t.replace("</urlset>",f"<url><loc>{loc}</loc></url></urlset>",1)
 p.write_text(t,encoding="utf-8")

def search(site:Path,b:str)->None:
 p=site/"arama/search-index.json"; d=json.loads(p.read_text(encoding="utf-8")); e=d.setdefault("entries",[]); known={x.get("canonicalPath") for x in e if isinstance(x,dict)}
 meta={
  "ev":("EV Şarj Kablosu Sağlık ve Isınma Günlüğü","Type 2 kablo olaylarını ayırın.","calculator",["Type 2 kablo","kablo ısınıyor"]),
  "pv":("GES Panel Temizlik Karar ve Sonuç Günlüğü","PV temizliğini kanıtla değerlendirin.","calculator",["GES panel temizliği","soiling"]),
  "ground":("Topraklama Ölçüm Trend ve Yeniden Test Günlüğü","Aynı yöntemle trend oluşturun.","business",["topraklama ölçümü","yeniden test"]),
 }
 for k,r in ROUTES.items():
  if r not in known:
   title,desc,bucket,keys=meta[k]; e.append({"canonicalPath":r,"url":url(b,r),"title":title,"description":desc,"bucket":bucket,"keywords":keys})
 d["entryCount"]=len(e); p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def release(site:Path,b:str,count:int)->None:
 p=site/"alo186-release.json"; d=json.loads(p.read_text(encoding="utf-8")); rs=d.setdefault("routes",[]); known={x.get("canonicalPath") for x in rs if isinstance(x,dict)}
 for k,r in ROUTES.items():
  if r not in known: rs.append({"canonicalPath":r,"source":SOURCES[k],"type":"business-tool" if k=="ground" else "calculator"})
 d["routeCount"]=len(rs); d["growthRun15"]={
  "version":1,"routes":list(ROUTES.values()),"entryPointsInjected":count,
  "rawPersonalDataCollected":False,"directAffiliateLinksAdded":0,
  "qualifiedAffiliateFlows":["ev_cable_after_confirmed_portable_cable_issue"],
  "professionalServiceFlows":["fixed_evse_cable_service","pv_soiling_performance_om","grounding_measurement_verification"],
  "affiliateDisclosureRequired":True,"unverifiedCommercialFieldsUsed":[],"noBuyOutcomePreserved":True,
  "officialApprovalClaimed":False,"emergencyCommerceClosed":True,"rooftopCommerceClosed":True,
  "professionalMeasurementOnly":True,"evCableJournalTtlDays":540,"pvCleaningJournalTtlDays":730,"groundingJournalTtlDays":1095}
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 q=site/"pages-release.json"
 if q.is_file():
  x=json.loads(q.read_text(encoding="utf-8")); x["routeCount"]=len(rs); x["growthRun15"]={"version":1,"basePath":b,"routes":[url(b,r) for r in ROUTES.values()],"entryPointsInjected":count,"directAffiliateLinksAdded":0,"emergencyCommerceClosed":True}; q.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def offline(site:Path,b:str)->int:
 p=site/"sw.js"; t=p.read_text(encoding="utf-8"); m=re.search(r"const CRITICAL=(\[.*?\]);",t,re.S)
 if not m:return 0
 a=json.loads(m.group(1)); n=0
 for r in ROUTES.values():
  u=url(b,r)
  if u not in a:a.append(u);n+=1
 if n:p.write_text(t[:m.start(1)]+json.dumps(a,ensure_ascii=False)+t[m.end(1):],encoding="utf-8")
 return n

def manifest(site:Path,b:str)->None:
 p=site/"manifest.webmanifest"
 if not p.is_file():return
 d=json.loads(p.read_text(encoding="utf-8")); a=d.setdefault("shortcuts",[])
 for name,r in [("EV Kablo Sağlığı",ROUTES["ev"]),("GES Temizlik Kararı",ROUTES["pv"]),("Topraklama Trendi",ROUTES["ground"])]:
  u=url(b,r)
  if not any(x.get("url")==u for x in a if isinstance(x,dict)):a.append({"name":name,"short_name":name,"url":u})
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def checksums(site:Path)->None:
 p=site/"checksums.sha256"
 if p.exists():p.unlink()
 fs=sorted(x for x in site.rglob("*") if x.is_file());p.write_text("\n".join(f"{hashlib.sha256(x.read_bytes()).hexdigest()}  {x.relative_to(site).as_posix()}" for x in fs)+"\n",encoding="utf-8")

def run(site:Path,base_path:str="")->dict:
 site=site.resolve();b=base(base_path)
 for r in ROUTES.values():
  p=site/r.strip("/")
  if not (p/"index.html").is_file() or not (p/"app.js").is_file():raise FileNotFoundError(p)
 count=entries(site,b);sitemap(site);search(site,b);release(site,b,count);off=offline(site,b);manifest(site,b);checksums(site)
 r16=run_growth_run16(site,b)
 return {"ok":True,"basePath":b,"routes":[url(b,r) for r in ROUTES.values()],"entryPointsInjected":count,"offlineAdded":off,"directAffiliateLinksAdded":0,"rawPersonalDataCollected":False,"emergencyCommerceClosed":True,"growthRun16":r16}

def main()->None:
 p=argparse.ArgumentParser();p.add_argument("--site",type=Path,required=True);p.add_argument("--base-path",default="");a=p.parse_args();print(json.dumps(run(a.site,a.base_path),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
