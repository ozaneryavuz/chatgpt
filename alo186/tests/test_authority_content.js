const assert=require('assert');
const fs=require('fs');
const path=require('path');

const repoRoot=path.resolve(__dirname,'../..');
const required={
  'ev-sarj-cihazi-icin-ev-tesisati-uygun-mu':['EPDK','IEC 60364-7-722','RDC-DD','yetkili'],
  'ges-elektrik-kesintisinde-calisir-mi':['anti-islanding','ada modu','batarya','yetkili'],
  'jenerator-transfer-salteri-neden-gerekir':['geri besleme','transfer','erkek–erkek','yetkili'],
  'elektrik-kesintisi-cihaz-hasari-edas-basvurusu':['EPDK','10 iş günü','servis raporu','dağıtım şirketi'],
  'prizde-topraklama-var-mi-priz-test-cihazi':['toprak elektrodu','çevrim empedansı','RCD','yetkili'],
  'saf-sinus-modifiye-sinus-inverter-farki':['aktif PFC','kalkış gücü','saf sinüs','tıbbi cihaz'],
  'kacak-akim-rolesi-tip-a-tip-ac-farki':['Tip AC','Tip A','RDC-DD','30 mA','yetkili elektrikçi'],
  'ev-tipi-enerji-depolama-kac-kwh-olmali':['kritik yük','kWh','kW','kullanılabilir kapasite','BMS'],
  'harmonik-nedir-thd-cihazlari-nasil-etkiler':['THDv','THDi','nötr','PCC','aktif harmonik filtre'],
  'ups-online-line-interactive-offline-farki':['line-interactive','online çift dönüşüm','transfer süresi','AVR','bypass'],
  'parafudr-gerilim-koruma-rolesi-farki':['SPD','gerilim izleme rölesi','sürekli aşırı gerilim','kontaktör','Tip 1'],
  'vpp-sanal-guc-santrali-nedir':['VPP','Toplayıcılık Lisansı','Talep Tarafı Katılımı','telemetri','gelir garantisi'],
  'kacak-akim-rolesi-neden-surekli-atar':['birikimli kaçak akım','nötr karışması','yetkili elektrikçi','köprülemek','112'],
  'ev-sarjinda-dinamik-yuk-yonetimi':['dinamik yük yönetimi','akım trafoları','fail-safe','güç artışı','EPDK'],
  'planli-elektrik-kesintisi-ne-kadar-once-bildirilir':['48 saat','kalıcı veri saklayıcısı','bildirimli kesinti','dağıtım şirketi','ALO186 resmî kesinti kaydı almaz'],
  'topraklama-direnci-kac-ohm-olmali':['RA × IΔn ≤ 50 V','toprak elektrodu direnci','PE sürekliliği','arıza çevrim empedansı','yetkili elektrikçi'],
  'notr-kopmasi-nasil-anlasilir':['nötr kopması','yıldız noktası','112','186','neutral cable break'],
  'lisanssiz-ges-mahsuplasma-ihtiyac-fazlasi':['öz tüketim','mahsuplaşma','ihtiyaç fazlası','YEKDEM','gelir garantisi'],
  'ups-akusu-ne-zaman-degisir':['self-test','3–5 yıl','20–25°C','runtime','eski ve yeni batarya'],
  'jenerator-ups-birlikte-calisir-mi':['jeneratör','UPS','online çift dönüşüm','frekans','harmonik','transfer'],
  'gunes-paneli-inverter-clipping-dc-ac-orani':['DC/AC oranı','clipping','PVWatts','MPPT','yıllık enerji'],
  'elektrik-panosunda-termal-kamera-kontrolu':['emisivite','gevşek bağlantı','ark parlaması','yetkili personel','sürekli termal izleme'],
  'faz-dengesizligi-faz-kaybi-motoru-nasil-etkiler':['faz sırası','faz kaybı','gerilim dengesizliği','akım dengesizliği','motor koruma rölesi'],
  'kompanzasyon-panosu-reaktif-guc-neden-bozulur':['akım trafosu','kondansatör kademesi','detuned','rezonans','deşarj süresi'],
  'ges-fazlasi-ile-elektrikli-arac-sarji':['PV fazlası','tek faz–üç faz geçişi','Eco Mode','fail-safe','öz tüketim'],
  'lifepo4-ev-bataryasi-guvenligi-bms-termal-kacak':['LiFePO4','BMS','termal kaçak','UL 9540A','DC sigorta'],
  'paralel-ups-n-arti-1-yedeklilik-nedir':['N+1','paralel UPS','yük paylaşımı','ortak bypass','tek hata noktası'],
  'power-station-gunes-paneli-nasil-secilir':['Voc','Vmp','Isc','Imp','MPPT','polarite'],
  'tip-2-ev-sarj-kablosu-nasil-secilir':['Type 2','Mode 3','16 A','32 A','uzatma kablosu'],
  'kacak-akim-rolesi-test-dugmesi-ne-siklikla':['TEST düğmesi','altı aylık','aylık','IΔn','köprülemek']
};

const cta={
  'ev-sarj-cihazi-icin-ev-tesisati-uygun-mu':'/hesaplama/ev-sarj-suresi/',
  'ges-elektrik-kesintisinde-calisir-mi':'/urun-rehberleri/ges-malzemeleri',
  'jenerator-transfer-salteri-neden-gerekir':'/isletme-surekliligi',
  'elektrik-kesintisi-cihaz-hasari-edas-basvurusu':'/edas-bul',
  'prizde-topraklama-var-mi-priz-test-cihazi':'/karar-motoru',
  'saf-sinus-modifiye-sinus-inverter-farki':'/hesaplama/ups-suresi/',
  'kacak-akim-rolesi-tip-a-tip-ac-farki':'/hesaplama/ev-sarj-uygunluk/',
  'ev-tipi-enerji-depolama-kac-kwh-olmali':'/hesaplama/inverter-uygunluk/',
  'harmonik-nedir-thd-cihazlari-nasil-etkiler':'/isletme-surekliligi',
  'ups-online-line-interactive-offline-farki':'/hesaplama/ups-suresi/',
  'parafudr-gerilim-koruma-rolesi-farki':'/hesaplama/parafudr-risk-testi/',
  'vpp-sanal-guc-santrali-nedir':'/isletme-surekliligi',
  'kacak-akim-rolesi-neden-surekli-atar':'/karar-motoru',
  'ev-sarjinda-dinamik-yuk-yonetimi':'/hesaplama/ev-sarj-uygunluk/',
  'planli-elektrik-kesintisi-ne-kadar-once-bildirilir':'/hesaplama/kesinti-gunlugu/',
  'topraklama-direnci-kac-ohm-olmali':'/karar-motoru',
  'notr-kopmasi-nasil-anlasilir':'/hesaplama/gerilim-koruma-cozum-secici/',
  'lisanssiz-ges-mahsuplasma-ihtiyac-fazlasi':'/fatura-analizi',
  'ups-akusu-ne-zaman-degisir':'/hesaplama/ekipman-bakim-plani/',
  'jenerator-ups-birlikte-calisir-mi':'/hesaplama/jenerator-gucu-secimi/',
  'gunes-paneli-inverter-clipping-dc-ac-orani':'/fatura-analizi',
  'elektrik-panosunda-termal-kamera-kontrolu':'/hesaplama/ekipman-bakim-plani/',
  'faz-dengesizligi-faz-kaybi-motoru-nasil-etkiler':'/karar-motoru',
  'kompanzasyon-panosu-reaktif-guc-neden-bozulur':'/isletme-surekliligi',
  'ges-fazlasi-ile-elektrikli-arac-sarji':'/hesaplama/ev-sarj-uygunluk/',
  'lifepo4-ev-bataryasi-guvenligi-bms-termal-kacak':'/hesaplama/ekipman-bakim-plani/',
  'paralel-ups-n-arti-1-yedeklilik-nedir':'/hesaplama/ups-suresi/',
  'power-station-gunes-paneli-nasil-secilir':'/hesaplama/gunes-paneli-power-station-uygunluk/',
  'tip-2-ev-sarj-kablosu-nasil-secilir':'/hesaplama/ev-sarj-uygunluk/',
  'kacak-akim-rolesi-test-dugmesi-ne-siklikla':'/hesaplama/ekipman-bakim-plani/'
};

const sitemap=fs.readFileSync(path.join(repoRoot,'alo186/sitemap.xml'),'utf8');
const routing=JSON.parse(fs.readFileSync(path.join(repoRoot,'alo186/deployment/routing-manifest.json'),'utf8'));
const portal=fs.readFileSync(path.join(repoRoot,'alo186/index.html'),'utf8');
const articleRoutes=routing.routes.filter(route=>route.type==='article');
assert.strictEqual(articleRoutes.length,30,'Routing manifest 30 teknik makale içermeli.');
assert(portal.includes('30 kaynak doğrulamalı teknik rehber'),'Portal 30 makale sayısını görünür göstermeli.');

for(const route of articleRoutes){
  const slug=route.canonicalPath.split('/').filter(Boolean).pop();
  assert(required[slug],`Zorunlu teknik terimler tanımlanmamış: ${slug}`);
  assert(cta[slug],`CTA tanımlanmamış: ${slug}`);
  const file=path.join(repoRoot,route.source);
  assert(fs.existsSync(file),`Makale bulunamadı: ${slug}`);
  const html=fs.readFileSync(file,'utf8');
  const canonical=`https://www.alo186.com${route.canonicalPath}`;
  assert(html.toLowerCase().includes('<!doctype html>'),`Doctype eksik: ${slug}`);
  assert(html.includes(`rel="canonical" href="${canonical}"`),`Canonical eksik: ${slug}`);
  assert(html.includes('meta name="description"'),`Description eksik: ${slug}`);
  const jsonLd=[...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
  assert(jsonLd.length>0,`JSON-LD bulunamadı: ${slug}`);
  for(const match of jsonLd){
    const parsed=JSON.parse(match[1]);
    const graph=parsed['@graph']||[parsed];
    assert(graph.some(item=>item['@type']==='Article'),`Article schema eksik: ${slug}`);
    assert(graph.some(item=>item['@type']==='FAQPage'),`FAQPage schema eksik: ${slug}`);
  }
  assert(html.includes('../alo186-article.css'),`Ortak CSS eksik: ${slug}`);
  assert(html.includes(cta[slug]),`İç CTA eksik: ${slug}`);
  assert(html.includes('Bağımsız bilgi'),`Bağımsızlık ifadesi eksik: ${slug}`);
  assert(html.includes('Son doğrulama: 28 Temmuz 2026'),`Doğrulama tarihi eksik: ${slug}`);
  assert(html.includes('Kaynaklar ve doğrulama'),`Görünür kaynak bölümü eksik: ${slug}`);
  assert(!/<form\b/i.test(html),`Makale kişisel veri/form istememeli: ${slug}`);
  assert(!/amazon\.com\.tr/i.test(html),`Teknik makalede doğrudan Amazon URL'si olmamalı: ${slug}`);
  assert(!/fiyatı\s+\d|stokta|puanı\s+\d/i.test(html),`Doğrulanmamış ticari bilgi riski: ${slug}`);
  assert(!/kesinlikle güvenlidir|her durumda güvenlidir|sonucu garanti eder/i.test(html),`Aşırı kesin güvenlik iddiası riski: ${slug}`);
  for(const text of required[slug]){
    assert(html.toLocaleLowerCase('tr').includes(text.toLocaleLowerCase('tr')),`Zorunlu ifade eksik (${text}): ${slug}`);
  }
  assert.strictEqual((html.match(/<h1\b/g)||[]).length,1,`Tek H1 olmalı: ${slug}`);
  assert(sitemap.includes(canonical),`Sitemap eksik: ${slug}`);
  assert(portal.includes(`href="${route.canonicalPath}"`),`Portal kartı eksik: ${slug}`);
}

const cssText=fs.readFileSync(path.join(repoRoot,'alo186/haberler/alo186-article.css'),'utf8');
assert(cssText.includes('@media(max-width:820px)'),'Mobil breakpoint eksik.');
assert(cssText.includes(':focus-visible'),'Klavye odak stili eksik.');
assert(cssText.includes('prefers-reduced-motion'),'Azaltılmış hareket desteği eksik.');

console.log('ALO186 içerik otoritesi: 30 makale SEO, AEO, JSON-LD, erişilebilirlik, routing ve güvenlik testlerini geçti.');
