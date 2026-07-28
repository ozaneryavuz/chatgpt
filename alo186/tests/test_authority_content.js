const assert=require('assert');
const fs=require('fs');
const path=require('path');

const repoRoot=path.resolve(__dirname,'../..');
const articles=[
  {slug:'ev-sarj-cihazi-icin-ev-tesisati-uygun-mu',required:['EPDK','IEC 60364-7-722','RDC-DD','yetkili'],cta:'/hesaplama/ev-sarj-suresi/'},
  {slug:'ges-elektrik-kesintisinde-calisir-mi',required:['anti-islanding','ada modu','batarya','yetkili'],cta:'/urun-rehberleri/ges-malzemeleri'},
  {slug:'jenerator-transfer-salteri-neden-gerekir',required:['geri besleme','transfer','erkek–erkek','yetkili'],cta:'/isletme-surekliligi'},
  {slug:'elektrik-kesintisi-cihaz-hasari-edas-basvurusu',required:['EPDK','10 iş günü','servis raporu','dağıtım şirketi'],cta:'/edas-bul'},
  {slug:'prizde-topraklama-var-mi-priz-test-cihazi',required:['toprak elektrodu','çevrim empedansı','RCD','yetkili'],cta:'/karar-motoru'},
  {slug:'saf-sinus-modifiye-sinus-inverter-farki',required:['aktif PFC','kalkış gücü','saf sinüs','tıbbi cihaz'],cta:'/hesaplama/ups-suresi/'},
  {slug:'kacak-akim-rolesi-tip-a-tip-ac-farki',required:['Tip AC','Tip A','RDC-DD','30 mA','yetkili elektrikçi'],cta:'/hesaplama/ev-sarj-uygunluk/',fresh:true},
  {slug:'ev-tipi-enerji-depolama-kac-kwh-olmali',required:['kritik yük','kWh','kW','kullanılabilir kapasite','BMS'],cta:'/hesaplama/inverter-uygunluk/',fresh:true},
  {slug:'harmonik-nedir-thd-cihazlari-nasil-etkiler',required:['THDv','THDi','nötr','PCC','aktif harmonik filtre'],cta:'/isletme-surekliligi',fresh:true},
  {slug:'ups-online-line-interactive-offline-farki',required:['line-interactive','online çift dönüşüm','transfer süresi','AVR','bypass'],cta:'/hesaplama/ups-suresi/',fresh:true},
  {slug:'parafudr-gerilim-koruma-rolesi-farki',required:['SPD','gerilim izleme rölesi','sürekli aşırı gerilim','kontaktör','Tip 1'],cta:'/hesaplama/parafudr-risk-testi/',fresh:true},
  {slug:'vpp-sanal-guc-santrali-nedir',required:['VPP','Toplayıcılık Lisansı','Talep Tarafı Katılımı','telemetri','gelir garantisi'],cta:'/isletme-surekliligi',fresh:true},
  {slug:'kacak-akim-rolesi-neden-surekli-atar',required:['birikimli kaçak akım','nötr karışması','yetkili elektrikçi','köprülemek','112'],cta:'/karar-motoru',fresh:true},
  {slug:'ev-sarjinda-dinamik-yuk-yonetimi',required:['dinamik yük yönetimi','akım trafoları','fail-safe','güç artışı','EPDK'],cta:'/hesaplama/ev-sarj-uygunluk/',fresh:true},
  {slug:'planli-elektrik-kesintisi-ne-kadar-once-bildirilir',required:['48 saat','kalıcı veri saklayıcısı','bildirimli kesinti','dağıtım şirketi','ALO186 resmî kesinti kaydı almaz'],cta:'/hesaplama/kesinti-gunlugu/',fresh:true},
  {slug:'topraklama-direnci-kac-ohm-olmali',required:['RA × IΔn ≤ 50 V','toprak elektrodu direnci','PE sürekliliği','arıza çevrim empedansı','yetkili elektrikçi'],cta:'/karar-motoru',fresh:true},
  {slug:'notr-kopmasi-nasil-anlasilir',required:['nötr kopması','yıldız noktası','112','186','neutral cable break'],cta:'/hesaplama/gerilim-koruma-cozum-secici/',fresh:true},
  {slug:'lisanssiz-ges-mahsuplasma-ihtiyac-fazlasi',required:['öz tüketim','mahsuplaşma','ihtiyaç fazlası','YEKDEM','gelir garantisi'],cta:'/fatura-analizi',fresh:true},
  {slug:'ups-akusu-ne-zaman-degisir',required:['self-test','3–5 yıl','20–25°C','runtime','eski ve yeni batarya'],cta:'/hesaplama/ekipman-bakim-plani/',fresh:true},
  {slug:'jenerator-ups-birlikte-calisir-mi',required:['jeneratör','UPS','online çift dönüşüm','frekans','harmonik','transfer'],cta:'/hesaplama/jenerator-gucu-secimi/',fresh:true},
  {slug:'gunes-paneli-inverter-clipping-dc-ac-orani',required:['DC/AC oranı','clipping','PVWatts','MPPT','yıllık enerji'],cta:'/fatura-analizi',fresh:true},
  {slug:'elektrik-panosunda-termal-kamera-kontrolu',required:['emisivite','gevşek bağlantı','ark parlaması','yetkili personel','sürekli termal izleme'],cta:'/hesaplama/ekipman-bakim-plani/',fresh:true},
  {slug:'faz-dengesizligi-faz-kaybi-motoru-nasil-etkiler',required:['faz sırası','faz kaybı','gerilim dengesizliği','akım dengesizliği','motor koruma rölesi'],cta:'/karar-motoru',fresh:true},
  {slug:'kompanzasyon-panosu-reaktif-guc-neden-bozulur',required:['akım trafosu','kondansatör kademesi','detuned','rezonans','deşarj süresi'],cta:'/isletme-surekliligi',fresh:true},
  {slug:'ges-fazlasi-ile-elektrikli-arac-sarji',required:['PV fazlası','tek faz–üç faz geçişi','Eco Mode','fail-safe','öz tüketim'],cta:'/hesaplama/ev-sarj-uygunluk/',fresh:true},
  {slug:'lifepo4-ev-bataryasi-guvenligi-bms-termal-kacak',required:['LiFePO4','BMS','termal kaçak','UL 9540A','DC sigorta'],cta:'/hesaplama/ekipman-bakim-plani/',fresh:true},
  {slug:'paralel-ups-n-arti-1-yedeklilik-nedir',required:['N+1','paralel UPS','yük paylaşımı','ortak bypass','tek hata noktası'],cta:'/hesaplama/ups-suresi/',fresh:true},
  {slug:'parafudr-gostergesi-kirmizi-ne-demek',required:['durum göstergesi','kırmızı','koruma modülü','yetkili elektrikçi','parafudr risk testi'],cta:'/hesaplama/ekipman-bakim-plani/',fresh:true},
  {slug:'jenerator-saatte-kac-litre-yakar',required:['yük yüzdesi','litre/saat','üretici tüketim tablosu','standby','prime'],cta:'/hesaplama/jenerator-gucu-secimi/',fresh:true},
  {slug:'ges-inverter-sebeke-gerilimi-yuksek-hatasi',required:['şebeke gerilimi','şebeke empedansı','on dakikalık ortalama','ülke ayarı','dağıtım şirketi'],cta:'/edas-bul',fresh:true}
];

for(const article of articles){
  const file=path.join(repoRoot,'alo186/haberler',article.slug,'index.html');
  assert(fs.existsSync(file),`Makale bulunamadı: ${article.slug}`);
  const html=fs.readFileSync(file,'utf8');
  const canonical=`https://www.alo186.com/haberler/${article.slug}`;
  assert(html.toLowerCase().includes('<!doctype html>'));
  assert(html.includes(`rel="canonical" href="${canonical}"`),`Canonical eksik: ${article.slug}`);
  assert(html.includes('meta name="description"'),`Description eksik: ${article.slug}`);
  assert(html.includes('application/ld+json'),`JSON-LD eksik: ${article.slug}`);
  const jsonLd=[...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
  assert(jsonLd.length>0,`JSON-LD bulunamadı: ${article.slug}`);
  for(const match of jsonLd){
    const parsed=JSON.parse(match[1]);
    const graph=parsed['@graph']||[parsed];
    assert(graph.some(item=>item['@type']==='Article'),`Article schema eksik: ${article.slug}`);
    assert(graph.some(item=>item['@type']==='FAQPage'),`FAQPage schema eksik: ${article.slug}`);
  }
  assert(html.includes('../alo186-article.css'),`Ortak CSS eksik: ${article.slug}`);
  assert(html.includes(article.cta),`İç CTA eksik: ${article.slug}`);
  assert(html.includes('Bağımsız bilgi'),`Bağımsızlık ifadesi eksik: ${article.slug}`);
  if(article.fresh){
    assert(html.includes('Son doğrulama: 28 Temmuz 2026'),`Doğrulama tarihi eksik: ${article.slug}`);
    assert(html.includes('Kaynaklar ve doğrulama'),`Görünür kaynak bölümü eksik: ${article.slug}`);
  }
  assert(!/<form\b/i.test(html),`Makale kişisel veri/form istememeli: ${article.slug}`);
  assert(!/amazon\.com\.tr/i.test(html),`Teknik makalede doğrudan Amazon URL'si olmamalı: ${article.slug}`);
  assert(!/fiyatı\s+\d|stokta|puanı\s+\d/i.test(html),`Doğrulanmamış ticari bilgi riski: ${article.slug}`);
  assert(!/kesinlikle güvenlidir|her durumda güvenlidir|sonucu garanti eder/i.test(html),`Aşırı kesin güvenlik iddiası riski: ${article.slug}`);
  for(const text of article.required){
    assert(html.toLocaleLowerCase('tr').includes(text.toLocaleLowerCase('tr')),`Zorunlu güvenlik/teknik ifade eksik (${text}): ${article.slug}`);
  }
  const h1=(html.match(/<h1\b/g)||[]).length;
  assert.strictEqual(h1,1,`Tek H1 olmalı: ${article.slug}`);
}

const css=path.join(repoRoot,'alo186/haberler/alo186-article.css');
assert(fs.existsSync(css),'Makale CSS dosyası eksik.');
const cssText=fs.readFileSync(css,'utf8');
assert(cssText.includes('@media(max-width:820px)'), 'Mobil breakpoint eksik.');
assert(cssText.includes(':focus-visible'), 'Klavye odak stili eksik.');
assert(cssText.includes('prefers-reduced-motion'), 'Azaltılmış hareket desteği eksik.');

const sitemap=fs.readFileSync(path.join(repoRoot,'alo186/sitemap.xml'),'utf8');
const routing=JSON.parse(fs.readFileSync(path.join(repoRoot,'alo186/deployment/routing-manifest.json'),'utf8'));
const portal=fs.readFileSync(path.join(repoRoot,'alo186/index.html'),'utf8');
for(const article of articles){
  const canonicalPath=`/haberler/${article.slug}`;
  assert(sitemap.includes(`https://www.alo186.com${canonicalPath}`),`Sitemap eksik: ${article.slug}`);
  assert(routing.routes.some(route=>route.canonicalPath===canonicalPath&&route.type==='article'),`Routing manifest eksik: ${article.slug}`);
  assert(portal.includes(`href="${canonicalPath}"`),`Portal kartı eksik: ${article.slug}`);
}

console.log(`ALO186 içerik otoritesi: ${articles.length} makale SEO, AEO, JSON-LD, erişilebilirlik, routing ve güvenlik testlerini geçti.`);
