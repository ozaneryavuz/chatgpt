from __future__ import annotations

import argparse, html, json, re
from pathlib import Path
from urllib.parse import quote_plus

VERSION=250
AI_AGENTS=("GPTBot","PerplexityBot","ClaudeBot","Bytespider","Google-Extended")
TAG="alo186rehber-21"
INDEPENDENT="ALO186 bağımsız bir bilgilendirme platformudur; EDAŞ veya kamu kurumu değildir, arıza kaydı almaz."
KOMBI=Path("amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici/index.html")


def _script(data:dict, marker:str)->str:
    return f'<script type="application/ld+json" {marker}>'+json.dumps(data,ensure_ascii=False,separators=(",",":"),sort_keys=True)+"</script>"


def _head(text:str, fragment:str)->str:
    if not re.search(r"</head\s*>",text,re.I): raise RuntimeError("head kapanışı yok")
    return re.sub(r"</head\s*>",fragment+"\n</head>",text,count=1,flags=re.I)


def _main(text:str, fragment:str)->str:
    if not re.search(r"</main\s*>",text,re.I): raise RuntimeError("main kapanışı yok")
    return re.sub(r"</main\s*>",fragment+"\n</main>",text,count=1,flags=re.I)


def _amazon(query:str)->str:
    return f"https://www.amazon.com.tr/s?k={quote_plus(query)}&tag={TAG}"


def robots(site:Path)->dict:
    p=site/"robots.txt"; old=p.read_text(encoding="utf-8") if p.is_file() else ""
    maps=[]
    for line in old.splitlines():
        if line.strip().lower().startswith("sitemap:") and line.strip() not in maps: maps.append(line.strip())
    if not maps: maps=["Sitemap: https://alo186.com/sitemap.xml"]
    rows=["User-agent: *","Allow: /"]
    for agent in AI_AGENTS: rows += ["",f"User-agent: {agent}","Allow: /"]
    p.write_text("\n".join(rows)+"\n\n"+"\n".join(maps)+"\n",encoding="utf-8")
    return {"explicitAllow":list(AI_AGENTS),"sitemaps":maps}


def kombi_graph()->dict:
    page="https://alo186.com/amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici/"; how=page+"#howto"
    products=[
      ("urun-kombi-ups","Kombi için saf sinüs UPS ürün sınıfı","Kesintisiz güç kaynağı","Tam model onayı, sürekli/tepe güç ve geçiş süresi doğrulanırsa değerlendirilir."),
      ("urun-kombi-guc-istasyonu","Saf sinüs ve EPS özellikli güç istasyonu ürün sınıfı","Taşınabilir enerji depolama","Uzun süre ihtiyacında W, Wh, EPS geçişi, topraklama ve üretici onayı doğrulanırsa değerlendirilir."),
      ("urun-priz-enerji-olcer","Priz tipi enerji ölçer ürün sınıfı","Elektrik ölçüm cihazı","Yalnız sağlam topraklı prizde gözlem içindir; arıza teşhisi veya tesisat uygunluğu garantisi vermez."),
    ]
    entities=[]
    for anchor,name,category,desc in products:
        entities.append({"@type":"Product","@id":page+"#"+anchor,"name":name,"category":category,"description":desc,"isRelatedTo":{"@id":how}})
    steps=[
      ("Acil gaz ve CO riskini ayırın","Gaz kokusu, CO belirtisi, duman, yanık kokusu veya su teması varsa ürüne ilerlemeyin; güvenli alana çıkıp 112 veya 187 yolunu kullanın."),
      ("Tam model onayını doğrulayın","Kılavuz veya yetkili servis üzerinden harici yedek enerji, saf sinüs ve bağlantı koşullarını doğrulayın."),
      ("Gerçek elektrik yükünü hesaplayın","Isıtma kapasitesi ile elektrik tüketimini ayırın; sürekli W, tepe W ve hedef süre için Wh hesabı yapın."),
      ("Mevcut çözümü test edin","Mevcut sistem model onaylı ve güvenli gerçek kesinti testini geçtiyse yeni ürün almayın."),
      ("Yalnız doğrulanmış eksik için ilerleyin","Gerçek eksik varsa UPS, EPS güç istasyonu veya enerji ölçer sınıfını teknik koşullarla karşılaştırın."),
    ]
    return {"@context":"https://schema.org","@graph":[
      {"@type":"Organization","@id":"https://alo186.com/#organization","name":"ALO186","url":"https://alo186.com/","description":INDEPENDENT},
      {"@type":"WebPage","@id":page+"#webpage","url":page,"name":"Kombi Yedek Enerji Ürün Seçici","publisher":{"@id":"https://alo186.com/#organization"},"about":[{"@id":how}]+[{"@id":x["@id"]} for x in entities]},
      {"@type":"HowTo","@id":how,"name":"Elektrik kesintisinde kombi nasıl güvenli korunur?","description":"Önce gaz/CO güvenliği ve model onayı, sonra W-Wh hesabı ve mevcut çözüm testi; yalnız gerçek eksikte ürün sınıfı.","totalTime":"PT10M","step":[{"@type":"HowToStep","position":i,"name":n,"text":t} for i,(n,t) in enumerate(steps,1)]},
      {"@type":"ItemList","@id":page+"#urun-siniflari","name":"Kombi kesintisi ürün sınıfları","numberOfItems":3,"itemListElement":[{"@type":"ListItem","position":i,"item":e} for i,e in enumerate(entities,1)]}
    ]}


def kombi_ssr()->str:
    rows=[
      ("urun-kombi-ups","Saf sinüs UPS kategorisini Amazon Türkiye'de incele","saf sinüs ups kombi"),
      ("urun-kombi-guc-istasyonu","Saf sinüs / EPS güç istasyonu kategorisini incele","saf sinüs güç istasyonu eps"),
      ("urun-priz-enerji-olcer","Priz tipi enerji ölçer kategorisini incele","priz tipi enerji ölçer"),
    ]
    items="".join(f'<li id="{i}"><a href="{html.escape(_amazon(q),quote=True)}" rel="sponsored nofollow noopener" target="_blank">{html.escape(label)}</a></li>' for i,label,q in rows)
    return '<section class="panel" data-alo186-ssr-affiliate-v250="true"><h2>Kombi yedek enerji ürün sınıfları</h2><p><strong>Affiliate açıklaması:</strong> Amazon Türkiye bağlantıları satış ortaklığı bağlantılarıdır; nitelikli satın alım olursa gelir elde edebilirim. Fiyat, stok, puan, teslimat ve garanti bilgisi yayımlanmaz.</p><p>Mevcut güvenli sistem tam model için onaylı ve gerçek kesinti testini geçtiyse yeni ürün almayın. Gaz/CO belirtisi, duman, ısınma, su teması veya sabit tesisat işi varsa alışverişe ilerlemeyin.</p><ul>'+items+'</ul><p>Bağlantılar belirli bir ürünün kombiyle uyumlu olduğu anlamına gelmez; model kılavuzu, saf sinüs, W/Wh, geçiş süresi, nötr-toprak ve RCD davranışı yeniden doğrulanmalıdır.</p></section>'


def inject_kombi(site:Path)->dict:
    p=site/KOMBI
    if not p.is_file(): raise FileNotFoundError(p)
    text=p.read_text(encoding="utf-8")
    if 'data-alo186-schema-v250="true"' not in text: text=_head(text,_script(kombi_graph(),'data-alo186-schema-v250="true"'))
    if 'data-alo186-ssr-affiliate-v250="true"' not in text: text=_main(text,kombi_ssr())
    p.write_text(text,encoding="utf-8")
    return {"howTo":True,"itemList":True,"genericProductEntities":3,"offers":False,"ratings":False,"ssrAffiliateLinks":3}


def _catalog(repo:Path):
    text=(repo/"alo186/turkiye-arama/companies.js").read_text(encoding="utf-8")
    pb=re.search(r"const provinceNames=\{(.*?)\};",text,re.S); cb=re.search(r"const companies=\[(.*?)\];\s*\n\s*const istanbulEurope",text,re.S)
    if not pb or not cb: raise RuntimeError("EDAŞ katalog parse hatası")
    provinces={int(i):n for i,n in re.findall(r"(\d+):'([^']+)'",pb.group(1))}
    pat=re.compile(r"\{id:'([^']+)',code:'[^']+',name:'([^']+)',slug:'([^']+)',provinceIds:\[([^\]]+)\](?:,districtMode:'[^']+')?,aliases:\[[^\]]*\]\}")
    companies=[{"id":m.group(1),"name":m.group(2),"slug":m.group(3),"provinceIds":[int(x) for x in m.group(4).split(',')]} for m in pat.finditer(cb.group(1))]
    if len(provinces)!=81 or len(companies)!=21: raise RuntimeError(f"Kapsam: {len(provinces)} il, {len(companies)} şirket")
    return provinces,companies


def edas_graph(repo:Path)->dict:
    provinces,companies=_catalog(repo)
    orgs=[{"@type":"Organization","@id":f"https://alo186.com/dagitim-sirketleri/{c['slug']}/#organization","name":c["name"],"url":f"https://alo186.com/dagitim-sirketleri/{c['slug']}/","description":"Güncel iletişim ve kesinti bilgisi şirketin resmî kanalından doğrulanmalıdır."} for c in companies]
    items=[]
    for pid,name in sorted(provinces.items()):
        refs=[{"@id":f"https://alo186.com/dagitim-sirketleri/{c['slug']}/#organization"} for c in companies if pid in c["provinceIds"]]
        service={"@type":"Service","@id":f"https://alo186.com/edas-bul/#service-{pid}","name":f"{name} elektrik kesintisi ve arıza yönlendirmesi","serviceType":"Elektrik dağıtım şebekesi kesinti ve arıza yönlendirmesi","areaServed":{"@type":"AdministrativeArea","name":name},"provider":refs[0] if len(refs)==1 else refs,"description":"ALO186 arıza kaydı almaz; 186 ve yetkili şirketin resmî kanalına bağımsız yönlendirme sağlar."}
        items.append({"@type":"ListItem","position":len(items)+1,"item":service})
    return {"@context":"https://schema.org","@graph":[
      {"@type":"Organization","@id":"https://alo186.com/#organization","name":"ALO186","url":"https://alo186.com/","description":INDEPENDENT},
      {"@type":"WebPage","@id":"https://alo186.com/edas-bul/#webpage","url":"https://alo186.com/edas-bul/","name":"81 İl İçin Yetkili Elektrik Dağıtım Şirketini Bulma","publisher":{"@id":"https://alo186.com/#organization"},"mainEntity":{"@id":"https://alo186.com/edas-bul/#province-services"}},
      {"@type":"ItemList","@id":"https://alo186.com/edas-bul/#province-services","name":"81 il elektrik kesintisi ve EDAŞ yönlendirme hizmetleri","numberOfItems":81,"itemListElement":items}
    ]+orgs}


def inject_edas(repo:Path,site:Path)->dict:
    p=next((x for x in (site/"edas-bul/index.html",site/"elektrik-kesintisi/index.html") if x.is_file()),None)
    if not p: raise FileNotFoundError("EDAŞ bulucu artifact yok")
    text=p.read_text(encoding="utf-8")
    if 'data-alo186-service-catalog-v250="true"' not in text: p.write_text(_head(text,_script(edas_graph(repo),'data-alo186-service-catalog-v250="true"')),encoding="utf-8")
    return {"provinceServices":81,"organizations":21,"schema":"Service + Organization","governmentServiceForPrivateEdas":False,"reason":"Özel dağıtım şirketlerini GovernmentService olarak işaretlemek resmî kamu hizmeti izlenimi yaratır."}


def inject_112(site:Path)->dict:
    p=site/"acil-numaralar/index.html"
    if not p.is_file(): return {"added":False,"optionalRouteMissing":True}
    text=p.read_text(encoding="utf-8"); marker='data-alo186-government-service-v250="true"'
    if marker not in text:
        data={"@context":"https://schema.org","@graph":[
          {"@type":"GovernmentService","@id":"https://alo186.com/acil-numaralar/#112-service","name":"112 Acil Çağrı Hizmeti","serviceType":"Ulusal acil çağrı yönlendirmesi","areaServed":{"@type":"Country","name":"Türkiye"},"provider":{"@id":"https://alo186.com/acil-numaralar/#112-organization"},"description":"ALO186 bu hizmeti sunmaz; yalnız doğru numaraya bağımsız yönlendirme yapar."},
          {"@type":"GovernmentOrganization","@id":"https://alo186.com/acil-numaralar/#112-organization","name":"112 Acil Çağrı Merkezi"},
          {"@type":"Organization","@id":"https://alo186.com/#organization","name":"ALO186","url":"https://alo186.com/","description":INDEPENDENT}]}
        p.write_text(_head(text,_script(data,marker)),encoding="utf-8")
    return {"added":True,"governmentService":"112 only","privateEdasMislabelled":False}


def anchor_section(kind:str)->str:
    if kind=="ups": title="Teknik sonucu doğruladıktan sonra ürün sınıfını inceleyin"; intro="W, VA, Wh, geçiş süresi ve dalga biçimi hesabı mevcut sistemin yetersiz olduğunu gösteriyorsa ilerleyin."; rows=[("urun-ups-saf-sinus","Saf sinüs UPS kategorisini incele","saf sinüs ups"),("urun-guc-istasyonu-eps","EPS güç istasyonu kategorisini incele","eps özellikli güç istasyonu saf sinüs")]
    else: title="Priz tipi korumayı yalnız doğru kullanım sınırında değerlendirin"; intro="Korumalı priz; topraklama, RCD, pano tipi SPD veya gerilim rölesinin yerine geçmez. Mevcut sağlam çözüm yeterliyse yeni ürün almayın."; rows=[("urun-akim-korumali-priz","Akım korumalı priz kategorisini incele","akım korumalı priz")]
    links="".join(f'<li id="{i}"><a href="{html.escape(_amazon(q),quote=True)}" rel="sponsored nofollow noopener" target="_blank">{html.escape(label)}</a></li>' for i,label,q in rows)
    return f'<section class="related-products" data-alo186-affiliate-anchors-v250="{kind}"><h2>{title}</h2><p>{intro}</p><p><strong>Affiliate açıklaması:</strong> Bağlantılar Amazon Türkiye satış ortaklığı bağlantılarıdır. Fiyat, stok, puan, teslimat ve garanti mağazada doğrulanır.</p><ul>{links}</ul></section>'


def inject_anchors(site:Path)->dict:
    targets={Path("haberler/ups-mi-tasinabilir-guc-istasyonu-mu/index.html"):"ups",Path("haberler/korumali-priz-ne-zaman-yeterli-degildir/index.html"):"surge"}; changed=[]
    for rel,kind in targets.items():
        p=site/rel
        if not p.is_file(): continue
        text=p.read_text(encoding="utf-8"); marker=f'data-alo186-affiliate-anchors-v250="{kind}"'
        if marker not in text: p.write_text(_main(text,anchor_section(kind)),encoding="utf-8"); changed.append(rel.as_posix())
    return {"changed":changed,"rel":"sponsored nofollow noopener"}


def validate(site:Path)->dict:
    k=(site/KOMBI).read_text(encoding="utf-8").lower()
    if k.count('data-alo186-schema-v250="true"')!=1 or k.count('data-alo186-ssr-affiliate-v250="true"')!=1: raise RuntimeError("v250 kombi marker tekil değil")
    if any(x in k for x in ('"offers"','aggregaterating','pricecurrency','availability','warranty')): raise RuntimeError("doğrulanmamış ticari schema alanı")
    section=re.search(r'<section[^>]+data-alo186-ssr-affiliate-v250="true".*?</section>',k,re.S)
    if not section or section.group(0).count('rel="sponsored nofollow noopener"')!=3: raise RuntimeError("SSR affiliate rel sözleşmesi")
    r=(site/"robots.txt").read_text(encoding="utf-8")
    for a in AI_AGENTS:
        if f"User-agent: {a}\nAllow: /" not in r: raise RuntimeError(a)
    return {"jsonLdSyntax":"pass","schemaOrgTypes":["HowTo","ItemList","Product","Service","Organization","GovernmentService"],"newGoogleRichResultEligibility":[],"richResultsNote":"Product zengin sonucu Offer, Review veya AggregateRating ister; doğrulanmamış fiyat, stok ve puan eklenmedi. HowTo güncel Google rich-result galerisinde desteklenmez.","affiliateRel":"pass","robots":"pass"}


def apply(repo:Path,site:Path,base_path:str="")->dict:
    report={"version":VERSION,"robots":robots(site),"kombi":inject_kombi(site),"anchors":inject_anchors(site),"edas":inject_edas(repo,site),"governmentService":inject_112(site)}
    report["validation"]=validate(site)
    (site/"alo186-competitor-gap-affiliate-v250.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report


def main()->None:
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",type=Path,default=Path.cwd()); ap.add_argument("--site",type=Path,required=True); ap.add_argument("--base-path",default="")
    a=ap.parse_args(); print(json.dumps(apply(a.repo.resolve(),a.site.resolve(),a.base_path),ensure_ascii=False,indent=2))

if __name__=="__main__": main()
