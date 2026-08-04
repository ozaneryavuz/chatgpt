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
  {slug:'ges-inverter-sebeke-gerilimi-yuksek-hatasi',required:['şebeke gerilimi','şebeke empedansı','on dakikalık ortalama','ülke ayarı','dağıtım şirketi'],cta:'/edas-bul',fresh:true},
  {slug:'power-station-gunes-paneli-nasil-secilir',required:['Voc','Vmp','Isc','Imp','MPPT','polarite'],cta:'/hesaplama/gunes-paneli-power-station-uygunluk/',fresh:true},
  {slug:'tip-2-ev-sarj-kablosu-nasil-secilir',required:['Type 2','Mode 3','16 A','32 A','uzatma kablosu'],cta:'/hesaplama/ev-sarj-uygunluk/',fresh:true},
  {slug:'kacak-akim-rolesi-test-dugmesi-ne-siklikla',required:['TEST düğmesi','altı aylık','aylık','IΔn','köprülemek'],cta:'/hesaplama/ekipman-bakim-plani/',fresh:true},
  {slug:'elektrik-sayaci-arizali-mi-fatura-itirazi',required:['EPDK','1 yıl','%30','dağıtım şirketi','tedarik şirketi'],cta:'/fatura-analizi',fresh:true},
  {slug:'v2l-v2h-v2g-farki-cift-yonlu-sarj',required:['V2L','V2H','V2G','ISO 15118-20','gelir garantisi'],cta:'/hesaplama/ev-sarj-uygunluk/',fresh:true},
  {slug:'batarya-c-rate-dod-kullanilabilir-kapasite',required:['C-rate','DoD','SoC','kullanılabilir kWh','çevrim ömrü'],cta:'/hesaplama/inverter-uygunluk/',fresh:true},
  {slug:'elektrik-arizasinda-edas-mi-tedarikci-mi-aranir',required:['dağıtım şirketi','görevli tedarik şirketi','186','15 iş günü','ALO186 resmî kayıt almaz'],cta:'/edas-bul',fresh:true},
  {slug:'elektrik-kesintisinde-buzdolabi-dondurucu-kac-saat-dayanir',required:['4 saat','48 saat','24 saat','4°C','Şüpheli gıdayı tatmayın'],cta:'/hesaplama/kesinti-hazirlik-plani/',fresh:true},
  {slug:'ges-inverter-izolasyon-direnci-dusuk-hatasi',required:['Low insulation resistance','PV string','yağmur','DC konnektör','yetkili kişi'],cta:'/hesaplama/ekipman-bakim-plani/',fresh:true},
  {slug:'inverter-dusuk-voltaj-alarmi-neden-verir',required:['low battery voltage','DC gerilim düşümü','kablo kesiti','BMS','yetkili kişi'],cta:'/hesaplama/inverter-uygunluk/',fresh:true},
  {slug:'ups-va-watt-farki-nasil-hesaplanir',required:['VA','Watt','güç faktörü','W = VA × PF','runtime'],cta:'/hesaplama/ups-suresi/',fresh:true},
  {slug:'jenerator-balkonda-garajda-calistirilir-mi',required:['20 feet','yaklaşık 6 metre','karbonmonoksit','112','CO alarmı'],cta:'/hesaplama/jenerator-karbonmonoksit-guvenlik-kontrolu/',fresh:true,verifiedAt:'4 Ağustos 2026'},
  {slug:'kacak-akim-rolesi-kac-amper-kac-ma-olmali',required:['40 A 30 mA','RCCB','RCBO','nominal akım','yetkili elektrikçi'],cta:'/karar-motoru',fresh:true},
  {slug:'notr-toprak-arasi-gerilim-kac-volt-olmali',required:['nötr-toprak gerilimi','IR gerilim düşümü','triplen harmonik','186','112'],cta:'/karar-motoru',fresh:true},
  {slug:'ges-inverter-afci-dc-ark-hatasi',required:['AFCI','DC ark','PV konnektör','112','yetkili GES personeli'],cta:'/hesaplama/ekipman-bakim-plani/',fresh:true},
  {slug:'ups-bypass-modu-nedir-neden-gecer',required:['static bypass','maintenance bypass','koşullandırılmamış güç','batarya yedeği kullanılamaz','ark parlaması'],cta:'/hesaplama/ekipman-bakim-plani/',fresh:true,portalOptional:true},
  {slug:'jenerator-ats-amf-farki-nedir',required:['Automatic Transfer Switch','Automatic Mains Failure','şebeke arızası','jeneratör start komutu','4 kutuplu'],cta:'/hesaplama/jenerator-gucu-secimi/',fresh:true,portalOptional:true},
  {slug:'parafudr-uc-up-in-imax-iimp-ne-demek',required:['Uc','Up','In','Imax','Iimp','Isccr'],cta:'/hesaplama/parafudr-risk-testi/',fresh:true,portalOptional:true},
  {slug:'ups-overload-asiri-yuk-alarmi-neden-verir',required:['UPS overload','VA veya Watt','kalkış gücü','yüksüz durumda','bataryaya geçiş'],cta:'/hesaplama/ups-suresi/',fresh:true,portalOptional:true},
  {slug:'jenerator-voltaj-frekans-dalgalanmasi-neden-olur',required:['motor devri','governor','AVR','yük adımı','V/Hz'],cta:'/hesaplama/jenerator-gucu-secimi/',fresh:true,portalOptional:true},
  {slug:'elektrikli-arac-sarj-olmuyor-wallbox-neden-baslamiyor',required:['zamanlanmış şarj','control pilot','port kilidi','RCD','112'],cta:'/hesaplama/ev-sarj-uygunluk/',fresh:true,portalOptional:true},
  {slug:'ups-surekli-otuyor-bip-sesi-ne-anlama-gelir',required:['On Battery','Low Battery','Replace Battery','Disconnected Battery','overload'],cta:'/hesaplama/ups-suresi/',fresh:true,portalOptional:true},
  {slug:'jenerator-mars-basmiyor-calismiyor-ne-yapilmali',required:['electric start battery','fuel shut-off valve','low oil shutdown','choke','112'],cta:'/hesaplama/ekipman-bakim-plani/',fresh:true,portalOptional:true},
  {slug:'ev-sarj-kablosu-prizi-isiniyor-ne-yapilmali',required:['thermal derating','Wall plug temperature high','Charge handle temperature high','Wall Connector wiring','112'],cta:'/hesaplama/ev-sarj-kablosu-uygunluk/',fresh:true,portalOptional:true},
  {slug:'ev-sarj-gucu-neden-dusuk-yavas-sarj',required:['onboard charger','tek faz','üç faz','dinamik yük yönetimi','thermal derating'],cta:'/hesaplama/ev-sarj-uygunluk/',fresh:true,portalOptional:true},
  {slug:'ges-inverter-sicakta-guc-dusuruyor-temperature-derating',required:['temperature derating','soğutma kanatları','havalandırma','doğrudan güneş ışınımı','yetkili GES personeli'],cta:'/hesaplama/ekipman-bakim-plani/',fresh:true,portalOptional:true},
  {slug:'ups-akusu-sarj-olmuyor-batarya-dolmuyor',required:['battery disconnected','10 saat','24 saat','bypass','self-test'],cta:'/hesaplama/ups-aku-degisim-uygunluk/',fresh:true,portalOptional:true},
  {slug:'elektrik-gerilimi-dusuk-yuksek-edas-olcum-talebi',required:['teknik kalite','bir haftalık ölçüm','15 iş günü','dağıtım şirketi','ALO186 resmî kayıt almaz'],cta:'/edas-bul',fresh:true,portalOptional:true},
  {slug:'ups-sebeke-varken-bataryaya-geciyor',required:['input sensitivity','Boost','Trim','THD','firmware'],cta:'/hesaplama/gerilim-koruma-cozum-secici/',fresh:true,portalOptional:true},
  {slug:'jenerator-calisiyor-elektrik-uretmiyor-ne-yapilmali',required:['main line circuit breaker','GFCI','bilinen sağlam','yetkili servis','erkek–erkek'],cta:'/hesaplama/ekipman-bakim-plani/',fresh:true,portalOptional:true},
  {slug:'lifepo4-batarya-sogukta-sarj-edilir-mi',required:['5°C','Allowed-To-Charge','low temperature cut-off','BMS','kalıcı hasar'],cta:'/hesaplama/inverter-uygunluk/',fresh:true,portalOptional:true},
  {slug:'parafudr-baglanti-kablosu-neden-kisa-olmali',required:['50 cm','let-through voltage','indüktans','gereksiz kıvrım','yetkili elektrikçi'],cta:'/hesaplama/parafudr-risk-testi/',fresh:true,portalOptional:true},
  {slug:'jenerator-devreye-girince-kacak-akim-rolesi-neden-atar',required:['solid neutral','switched neutral','4 kutuplu ATS','ayrı türetilmiş sistem','yetkili elektrikçi'],cta:'/hesaplama/jenerator-gucu-secimi/',fresh:true,portalOptional:true},
  {slug:'elektrik-sayaci-degisti-eski-yeni-endeks-fatura-kontrolu',required:['sayaç seri numarası','ilk ve son endeks','okuma tarihleri','değiştirilen sayaç','görevli tedarik şirketi'],cta:'/fatura-analizi',fresh:true,portalOptional:true},
  {slug:'notr-akimi-faz-akimindan-yuksek-neden-olur',required:['3. harmonik','triplen harmonik','58,5 A','THDi','yetkili elektrik mühendisi'],cta:'/isletme-surekliligi',fresh:true,portalOptional:true},
  {slug:'batarya-soc-soh-farki-kapasite-saglik-nasil-anlasilir',required:['State of Charge','State of Health','kullanılabilir kapasite','iç direnç','yüzde 80'],cta:'/hesaplama/inverter-uygunluk/',fresh:true,portalOptional:true},
  {slug:'kacak-akim-rolesi-tip-s-selektivite-nedir',required:['Tip S','seçicilik','IΔn','zaman gecikmesi','yetkili elektrikçi'],cta:'/karar-motoru',fresh:true,portalOptional:true},
  {slug:'jenerator-dusuk-yuk-wet-stacking-nedir',required:['wet stacking','%30','load bank','egzoz slobber','yetkili servis'],cta:'/hesaplama/jenerator-gucu-secimi/',fresh:true,portalOptional:true},
  {slug:'ups-aku-string-dengesizligi-zayif-aku-nasil-anlasilir',required:['battery string','iç direnç','eski ve yeni','tüm string','yetkili UPS servisi'],cta:'/hesaplama/ups-aku-degisim-uygunluk/',fresh:true,portalOptional:true},
  {slug:'ev-sarj-istasyonu-tip-b-rcd-rdc-dd-secimi',required:['Tip B','Tip A','RDC-DD','6 mA DC','30 mA','yetkili elektrikçi'],cta:'/hesaplama/ev-sarj-uygunluk/',fresh:true,portalOptional:true},
  {slug:'topraklama-direnci-ariza-cevrim-empedansi-farki',required:['RA','Ze','Zs','R1 + R2','otomatik açma','RCD'],cta:'/karar-motoru',fresh:true,portalOptional:true},
  {slug:'detuned-reaktor-aktif-harmonik-filtre-farki',required:['detuned reaktör','aktif harmonik filtre','rezonans','5. harmonik','THDi','tuning frequency'],cta:'/isletme-surekliligi',fresh:true,portalOptional:true},
  {slug:'kacak-akim-rolesi-tip-f-nedir-inverterli-cihazlar',required:['IEC/EN 62423','tek fazlı frekans dönüştürücü','yüksek frekanslı artık akım','Tip B','yetkili elektrikçi'],cta:'/karar-motoru',fresh:true,portalOptional:true},
  {slug:'parafudr-yedek-sigorta-scpd-nasil-secilir',required:['SCPD','maksimum yedek sigorta','SCCR','branch wiring','through wiring','yetkili elektrikçi'],cta:'/hesaplama/parafudr-risk-testi/',fresh:true,portalOptional:true},
  {slug:'vpp-batarya-cevrim-rezerv-garanti-sozlesmesi',required:['Toplayıcılık Lisansı','Talep Tarafı Katılımı','minimum SoC rezervi','baseline','çevrim/throughput','gelir garantisi yok'],cta:'/hesaplama/elektrik-surekliligi-olgunluk-skoru/',fresh:true,portalOptional:true}
];
assert.strictEqual(articles.length,75,'İçerik kalite testi 75 teknik makaleyi kapsamalı.');

for(const article of articles){
  const file=path.join(repoRoot,'alo186/haberler',article.slug,'index.html');
  assert(fs.existsSync(file),`Makale bulunamadı: ${article.slug}`);
  const html=fs.readFileSync(file,'utf8');
  const canonical=`https://www.alo186.com/haberler/${article.slug}`;
  assert(html.toLowerCase().includes('<!doctype html>'));
  assert(html.includes(`rel="canonical" href="${canonical}"`),`Canonical eksik: ${article.slug}`);
  assert(html.includes('meta name="description"'),`Description eksik: ${article.slug}`);
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
    const expectedVerificationDate=article.verifiedAt||'28 Temmuz 2026';
    assert(html.includes(`Son doğrulama: ${expectedVerificationDate}`),`Doğrulama tarihi eksik: ${article.slug}`);
    assert(html.includes('Kaynaklar ve doğrulama'),`Görünür kaynak bölümü eksik: ${article.slug}`);
  }
  assert(!/<form\b/i.test(html),`Makale kişisel veri/form istememeli: ${article.slug}`);
  assert(!/amazon\.com\.tr/i.test(html),`Teknik makalede doğrudan Amazon URL'si olmamalı: ${article.slug}`);
  assert(!/fiyatı\s+\d|stokta|puanı\s+\d/i.test(html),`Doğrulanmamış ticari bilgi riski: ${article.slug}`);
  assert(!/kesinlikle güvenlidir|her durumda güvenlidir|sonucu garanti eder/i.test(html),`Aşırı kesin güvenlik iddiası riski: ${article.slug}`);
  for(const text of article.required){
    assert(html.toLocaleLowerCase('tr').includes(text.toLocaleLowerCase('tr')),`Zorunlu ifade eksik (${text}): ${article.slug}`);
  }
  assert.strictEqual((html.match(/<h1\b/g)||[]).length,1,`Tek H1 olmalı: ${article.slug}`);
}

const cssText=fs.readFileSync(path.join(repoRoot,'alo186/haberler/alo186-article.css'),'utf8');
assert(cssText.includes('@media(max-width:820px)'),'Mobil breakpoint eksik.');
assert(cssText.includes(':focus-visible'),'Klavye odak stili eksik.');
assert(cssText.includes('prefers-reduced-motion'),'Azaltılmış hareket desteği eksik.');

const sitemap=fs.readFileSync(path.join(repoRoot,'alo186/sitemap.xml'),'utf8');
const routing=JSON.parse(fs.readFileSync(path.join(repoRoot,'alo186/deployment/routing-manifest.json'),'utf8'));
const portal=fs.readFileSync(path.join(repoRoot,'alo186/index.html'),'utf8');
assert.strictEqual(routing.routes.filter(route=>route.type==='article').length,75,'Routing manifest 75 teknik makale içermeli.');
assert(portal.includes('kaynak doğrulamalı rehberler'),'Portal kaynak doğrulamalı rehber ailesini görünür göstermeli; routing ve sitemap tam makale envanterini doğrular.');
for(const article of articles){
  const canonicalPath=`/haberler/${article.slug}`;
  assert(sitemap.includes(`${routing.canonicalHost}${canonicalPath}`),`Sitemap eksik: ${article.slug}`);
  assert(routing.routes.some(route=>route.canonicalPath===canonicalPath&&route.type==='article'),`Routing manifest eksik: ${article.slug}`);
  if(!article.portalOptional){
    assert(portal.includes(`href="${canonicalPath}"`),`Portal kartı eksik: ${article.slug}`);
  }
}

console.log(`ALO186 içerik otoritesi: ${articles.length} makale SEO, AEO, JSON-LD, erişilebilirlik, routing ve güvenlik testlerini geçti.`);
