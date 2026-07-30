(function(root,factory){
  const current=root&&root.Alo186ProductCatalog
    ? root.Alo186ProductCatalog
    : (typeof module==='object'&&module.exports ? require('./catalog-knowledge-extension.js') : null);
  const api=factory(current,root);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186ProductCatalog=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(catalog,root){
  'use strict';

  if(!catalog)throw new Error('ALO186 Product Knowledge Graph yüklenemedi.');
  if(catalog.__salesProductExpansionRun51)return catalog;
  if(catalog.affiliateTag!=='alo186rehber-21')throw new Error('Onaylı affiliate etiketi korunmadı.');
  if(typeof catalog.knowledgeGraph!=='function'||typeof catalog.publicAffiliateEligible!=='function'){
    throw new Error('Product Knowledge Graph güven işlevleri eksik.');
  }

  const verifiedAt='2026-07-30';
  const relation=(category)=>catalog.categoryRelations[category]||{tools:[],guides:[],evidence:[]};
  const unique=(values)=>[...new Set(values.filter(Boolean))];
  const combinedRelations=(...categories)=>({
    tools:unique(categories.flatMap((category)=>relation(category).tools||[])),
    guides:unique(categories.flatMap((category)=>relation(category).guides||[])),
    evidence:unique(categories.flatMap((category)=>relation(category).evidence||[]))
  });

  for(const need of [
    {id:'usb-c-hub-connectivity',name:'USB-C hub bağlantı, güç bütçesi ve görüntü uyumu'},
    {id:'usb-c-display-output',name:'USB-C görüntü çıkışı ve DisplayPort Alt Mode uyumu'}
  ]){
    if(!catalog.needs.some((item)=>item.id===need.id))catalog.needs.push(need);
  }
  catalog.categoryNeeds.usb_c_hub=['usb-c-hub-connectivity'];
  catalog.categoryNeeds.display_cable=['usb-c-display-output'];
  catalog.categoryRelations.usb_c_hub={
    tools:['/hesaplama/usb-c-urun-kabul-testi/'],
    guides:['/urun-bilgi-grafigi/usb-c-ekosistemi/'],
    evidence:['host USB-C veri/görüntü desteği','PD geçiş gücü ve haricî adaptör','port türü ve toplam güç bütçesi','gerekli veri ve görüntü işlevi']
  };
  catalog.categoryRelations.display_cable={
    tools:['/hesaplama/usb-c-urun-kabul-testi/'],
    guides:['/urun-bilgi-grafigi/usb-c-ekosistemi/'],
    evidence:['host DisplayPort Alt Mode veya Thunderbolt desteği','hedef çözünürlük ve yenileme hızı','kablo yönü ve uzunluğu','görüntü zinciri uyumluluğu']
  };

  const smokeCoRelations=combinedRelations('smoke_alarm','co_alarm');
  const additions=[
    {
      id:'ugreen-nexode-100w-4port',category:'usb_c_charger',asin:null,model:'Nexode 100W 4-Port',
      name:'UGREEN Nexode 100 W 4 Port GaN Şarj Cihazı',brand:'UGREEN',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{maxOutputW:100,usbCPorts:3,usbAPorts:1,gan:true,pd3:true,pps:true,qc4:true,scp:true},
      strengths:['100 W toplam çıkış sınıfı','Üç USB-C + bir USB-A','PD 3.0, PPS ve QC protokol kapsamı'],
      limits:['100 W tek port ve çoklu port dağılımı aynı değildir','Kablo sınıfı ve cihaz protokolü gerçek hızı sınırlar','Amazon sonucundaki tam 4 portlu Nexode 100 W model yeniden doğrulanmalıdır'],
      sourceNote:'UGREEN resmî teknik sayfasında 100 W, üç USB-C + bir USB-A, GaN, PD 3.0, PPS ve çoklu port güç dağılımı 30 Temmuz 2026 tarihinde doğrulandı. Tek ASIN iddia edilmez.',
      technicalSource:'https://eu.ugreen.com/collections/gan-chargers/products/ugreen-nexode-100w-usb-c-wall-charger',
      needIds:['usb-c-fast-charging'],relatedTools:relation('usb_c_charger').tools,relatedGuides:relation('usb_c_charger').guides,
      requiredEvidence:['cihazın kabul ettiği W/protokol','çoklu port dağılımı','5 A/e-marker kablo gereği','Amazon’daki tam 4 portlu model'],
      url:catalog.amazonSearchUrl('UGREEN Nexode 100W 4 Port GaN USB C şarj cihazı')
    },
    {
      id:'tp-link-tapo-p115',category:'smart_plug',asin:null,model:'Tapo P115',
      name:'TP-Link Tapo P115 Enerji İzlemeli Akıllı Priz',brand:'TP-Link',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{maxCurrentA:16,maxPowerW:3680,energyMonitoring:true,wifiGHz:2.4,matter:false,localSchedules:true,powerMemory:true,operatingTempMaxC:35},
      strengths:['Enerji izleme','Kompakt yapı','Planlama ve uzaktan kontrol'],
      limits:['Motor/kompresör kalkış akımı ayrıca doğrulanmalıdır','Sabit bağlı veya priz sınırını aşan yüklerde kullanılmamalıdır','Amazon sonucundaki P115 modeli ve bölge sürümü doğrulanmalıdır'],
      sourceNote:'TP-Link Türkiye teknik sayfasında Tapo P115 enerji izleme, 2,4 GHz, planlama ve 16 A / 3680 W sınıfı 30 Temmuz 2026 tarihinde doğrulandı.',
      technicalSource:'https://www.tp-link.com/tr/home-networking/smart-plug/tapo-p115/',
      needIds:['device-energy-measurement'],relatedTools:relation('smart_plug').tools,relatedGuides:relation('smart_plug').guides,
      requiredEvidence:['gerçek yük akımı','yük türü ve kalkış davranışı','uygulama/bulut tercihi','Amazon’daki tam P115 modeli'],
      url:catalog.amazonSearchUrl('TP-Link Tapo P115 enerji izlemeli akıllı priz')
    },
    {
      id:'tp-link-tapo-p115m',category:'smart_plug',asin:null,model:'Tapo P115M',
      name:'TP-Link Tapo P115M Matter Enerji İzlemeli Akıllı Priz',brand:'TP-Link',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{maxCurrentA:16,maxPowerW:3680,energyMonitoring:true,solarEnergyTracking:true,wifiGHz:2.4,matter:true,zeroCross:true,operatingTempMaxC:40},
      strengths:['Matter ekosistem desteği','Enerji ve çift yönlü/güneş enerjisi izleme','Sıfır geçiş algılama'],
      limits:['Matter platformu için üçüncü taraf hub gerekebilir','Yük türü ve kalkış akımı ayrıca doğrulanmalıdır','Amazon sonucundaki tam P115M ve donanım sürümü doğrulanmalıdır'],
      sourceNote:'TP-Link Türkiye resmî sayfasında Tapo P115M Matter, enerji/güneş enerjisi izleme ve sıfır geçiş algılama 30 Temmuz 2026 tarihinde doğrulandı.',
      technicalSource:'https://www.tp-link.com/tr/home-networking/smart-plug/tapo-p115m/',
      needIds:['device-energy-measurement'],relatedTools:relation('smart_plug').tools,relatedGuides:relation('smart_plug').guides,
      requiredEvidence:['gerçek yük akımı','Matter platform/hub uyumu','yük türü','Amazon’daki tam P115M modeli ve donanım sürümü'],
      url:catalog.amazonSearchUrl('TP-Link Tapo P115M Matter enerji izlemeli akıllı priz')
    },
    {
      id:'ecoflow-river-2-max',category:'power_station',asin:null,model:'RIVER 2 Max',
      name:'EcoFlow RIVER 2 Max Taşınabilir Güç İstasyonu',brand:'EcoFlow',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{capacityWh:512,continuousW:500,surgeW:1000,pureSine:true,chemistry:'LFP',epsTransferMs:30,weightKg:6},
      strengths:['512 Wh kapasite','500 W sürekli / 1000 W dalgalanma sınıfı','LFP batarya','30 ms üretici EPS verisi'],
      limits:['1000 W dalgalanma değeri 500 W sürekli gücün yerine kullanılmamalıdır','30 ms geçiş kritik yükte kesintisiz çalışma garantisi değildir','Outlet ve standart ürün varyantları karıştırılmamalıdır'],
      sourceNote:'EcoFlow Türkiye resmî sayfasında RIVER 2 Max için 512 Wh, 500 W çıkış, 1000 W dalgalanma, LFP ve 30 ms geçiş 30 Temmuz 2026 tarihinde doğrulandı.',
      technicalSource:'https://ecoflow.com.tr/urun/ecoflow-river-2-max-tasinabilir-guc-kaynagi/',
      needIds:['portable-backup-energy'],relatedTools:relation('power_station').tools,relatedGuides:relation('power_station').guides,
      requiredEvidence:['yükün sürekli/tepe W değeri','hedef runtime','EPS toleransı','Amazon’daki tam RIVER 2 Max modeli'],
      url:catalog.amazonSearchUrl('EcoFlow RIVER 2 Max 512Wh 500W taşınabilir güç istasyonu')
    },
    {
      id:'ecoflow-delta-2-max',category:'power_station',asin:null,model:'DELTA 2 Max',
      name:'EcoFlow DELTA 2 Max Taşınabilir Güç İstasyonu',brand:'EcoFlow',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{capacityWh:2048,continuousW:2400,surgeW:4800,pureSine:true,chemistry:'LFP',solarPowerMaxW:1000,usbCMaxW:100,epsTransferMs:30,weightKg:23},
      strengths:['2048 Wh kapasite','2400 W sürekli / 4800 W dalgalanma','1000 W solar giriş sınıfı','LFP ve genişletilebilir kapasite'],
      limits:['4800 W dalgalanma sürekli güç değildir','30 ms EPS kritik yük için UPS kabulü değildir','Ev panosuna bağlantı profesyonel proje ve transfer düzeni gerektirir'],
      sourceNote:'EcoFlow Türkiye resmî sayfasında DELTA 2 Max için 2048 Wh, 2400 W AC çıkış, 4800 W dalgalanma, 1000 W solar giriş, LFP ve 30 ms 30 Temmuz 2026 tarihinde doğrulandı.',
      technicalSource:'https://ecoflow.com.tr/urun/ecoflow-delta-2-max-tasinabilir-guc-kaynagi/',
      needIds:['portable-backup-energy'],relatedTools:relation('power_station').tools,relatedGuides:relation('power_station').guides,
      requiredEvidence:['kritik yük kWh/W hesabı','transfer/EPS toleransı','PV Voc/Isc sınırı','Amazon’daki tam DELTA 2 Max modeli'],
      url:catalog.amazonSearchUrl('EcoFlow DELTA 2 Max 2048Wh 2400W taşınabilir güç istasyonu')
    },
    {
      id:'x-sense-xc01-r',category:'co_alarm',asin:null,model:'XC01-R',
      name:'X-Sense XC01-R Dijital Karbonmonoksit Alarmı',brand:'X-Sense',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{sensor:'electrochemical',display:true,measurementRangePpm:'0-300',alarmDb:85,serviceLifeYearsClaim:10,visualAlarm:true},
      strengths:['Elektrokimyasal sensör','Dijital ppm ekranı','≥85 dB sesli ve görsel uyarı'],
      limits:['10 yıllık hizmet ömrü üretici beyanıdır; üretim/değiştirme tarihi doğrulanmalıdır','CO alarmı jeneratörü kapalı veya binaya yakın alanda güvenli yapmaz','Modelin EN 50291 belge kapsamı satın alma öncesi doğrulanmalıdır'],
      sourceNote:'X-Sense Türkiye resmî sayfasında XC01-R için elektrokimyasal sensör, dijital ppm ekranı, 0–300 ppm aralığı ve ≥85 dB 30 Temmuz 2026 tarihinde doğrulandı.',
      technicalSource:'https://x-sense.com.tr/urunler/karbonmonoksit-dedektorleri/xc01r-karbonmonoksit-alarmi',
      needIds:['carbon-monoxide-warning'],relatedTools:relation('co_alarm').tools,relatedGuides:relation('co_alarm').guides,
      requiredEvidence:['tam XC01-R model kodu','EN 50291 belge kapsamı','üretim/değiştirme tarihi','yerleşim ve düzenli test planı'],
      url:catalog.amazonSearchUrl('X-Sense XC01-R karbonmonoksit alarmı dijital ekran')
    },
    {
      id:'samsung-eb-p4520-20k-45w',category:'powerbank',asin:null,model:'EB-P4520',
      name:'Samsung EB-P4520 20.000 mAh 45 W USB-C Powerbank',brand:'Samsung',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{capacityMah:20000,maxOutputW:45,totalOutputW:45,usbCPorts:3,pd3:true,pps:true,weightG:402},
      strengths:['20.000 mAh kapasite','Tek cihazda 45 W sınıfı','Üç USB-C port','PD 3.0 PDO/PPS'],
      limits:['45 W yalnız uyumlu tek cihaz ve uygun kabloyla elde edilir','Üç cihaz eşzamanlı şarjda güç paylaşılır','Amazon sonucunda tam EB-P4520 model ailesi ve bölge kodu doğrulanmalıdır'],
      sourceNote:'Samsung resmî ürün sayfasında EB-P4520 için 20.000 mAh, 45 W, üç USB-C ve PD 3.0 PDO/PPS alanları 30 Temmuz 2026 tarihinde doğrulandı. Tek ASIN iddia edilmez.',
      technicalSource:'https://www.samsung.com/br/mobile-accessories/battery-pack-20-000mah-beige-eb-p4520xupgbr/',
      needIds:['mobile-continuity'],relatedTools:relation('powerbank').tools,relatedGuides:relation('powerbank').guides,
      requiredEvidence:['tam EB-P4520 model kodu','cihazın kabul ettiği USB-C güç ve PPS profili','uygun USB-C kablo','Amazon’daki bölge/varyant eşleşmesi'],
      url:catalog.amazonSearchUrl('Samsung EB-P4520 20000 mAh 45W USB C powerbank')
    },
    {
      id:'ugreen-nexode-x-65w-3port',category:'usb_c_charger',asin:null,model:'Nexode X 65W 3-Port',
      name:'UGREEN Nexode X 65 W 3 Port Mini GaN Şarj Cihazı',brand:'UGREEN',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{maxOutputW:65,maxSingleDeviceW:65,usbCPorts:2,usbAPorts:1,gan:true,pd3:true,pps:true},
      strengths:['Tek USB-C portta 65 W sınıfı','İki USB-C + bir USB-A','45 W PPS desteği','Kompakt GaN tasarım'],
      limits:['65 W tek port gücüdür; üç portta güç bölüşülür','Hız cihaz protokolü ve kablo sınıfıyla sınırlanır','Amazon sonucundaki tam Nexode X 65 W üç port modeli doğrulanmalıdır'],
      sourceNote:'UGREEN resmî Nexode X sayfasında 65 W tek port, iki USB-C + bir USB-A ve PPS desteği 30 Temmuz 2026 tarihinde doğrulandı. Tek ASIN iddia edilmez.',
      technicalSource:'https://eu.ugreen.com/it/products/nexode-x-65w-3-port-mini-gan-usb-c-charger',
      needIds:['usb-c-fast-charging'],relatedTools:relation('usb_c_charger').tools,relatedGuides:relation('usb_c_charger').guides,
      requiredEvidence:['cihazın kabul ettiği W/protokol','eşzamanlı port güç dağılımı','kablo akım/güç sınıfı','Amazon’daki tam Nexode X 65 W modeli'],
      url:catalog.amazonSearchUrl('UGREEN Nexode X 65W 3 Port Mini GaN USB C şarj cihazı')
    },
    {
      id:'ugreen-90440-240w-usb-c',category:'usb_c_cable',asin:null,model:'90440',
      name:'UGREEN 90440 240 W USB-C–USB-C PD 3.1 Kablo',brand:'UGREEN',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{maxPowerW:240,maxCurrentA:5,maxVoltageV:48,pd31:true,pps:true,emarker:true,dataMbps:480,videoSupport:false,lengthM:2},
      strengths:['240 W / 48 V / 5 A teorik güç sınıfı','PD 3.1 ve geriye dönük PD/PPS','E-marker çipi','480 Mbps USB 2.0 veri'],
      limits:['Görüntü ve DisplayPort Alt Mode taşımaz','240 W yalnız uyumlu adaptör ve cihazla mümkündür','Amazon sonucunda SKU 90440 ve uzunluk doğrulanmalıdır'],
      sourceNote:'UGREEN Türkiye resmî SKU 90440 sayfasında 240 W, 48 V/5 A, PD 3.1, E-marker, 480 Mbps ve görüntü taşımadığı bilgileri 30 Temmuz 2026 tarihinde doğrulandı.',
      technicalSource:'https://www.ugreen.com/tr-tr/products/tr-90440',
      needIds:['usb-c-cable-compatibility'],relatedTools:relation('usb_c_cable').tools,relatedGuides:relation('usb_c_cable').guides,
      requiredEvidence:['tam SKU 90440','hedef cihaz ve adaptör W değeri','5 A/e-marker gereği','görüntü gereksiniminin bulunmaması'],
      url:catalog.amazonSearchUrl('UGREEN 90440 240W USB C USB C PD 3.1 kablo 2 metre')
    },
    {
      id:'ecoflow-river-3',category:'power_station',asin:null,model:'RIVER 3',
      name:'EcoFlow RIVER 3 245 Wh 300 W Taşınabilir Güç İstasyonu',brand:'EcoFlow',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{capacityWh:245,continuousW:300,surgeW:600,xBoostW:600,pureSine:true,chemistry:'LFP',epsTransferMs:20,solarPowerMaxW:110,usbCMaxW:100,weightKg:3.55},
      strengths:['245 Wh kapasite','300 W sürekli / 600 W dalgalanma ve X-Boost sınıfı','LFP batarya','110 W solar ve 100 W USB-C'],
      limits:['600 W X-Boost yalnız belirli rezistif yükler için değerlendirilmelidir','<20 ms geçiş her kritik yük için kesintisiz çalışma garantisi değildir','RIVER 3, UPS ve outlet varyantları karıştırılmamalıdır'],
      sourceNote:'EcoFlow Türkiye resmî sayfasında RIVER 3 için 245 Wh, 300 W sürekli, 600 W dalgalanma/X-Boost, LFP, <20 ms, 110 W solar ve 3,55 kg 30 Temmuz 2026 tarihinde doğrulandı.',
      technicalSource:'https://ecoflow.com.tr/urun/ecoflow-river-3-tasinabilir-guc-kaynagi/',
      needIds:['portable-backup-energy'],relatedTools:relation('power_station').tools,relatedGuides:relation('power_station').guides,
      requiredEvidence:['yükün sürekli ve kalkış W değeri','hedef runtime','EPS toleransı','Amazon’daki tam RIVER 3 varyantı'],
      url:catalog.amazonSearchUrl('EcoFlow RIVER 3 245Wh 300W taşınabilir güç istasyonu')
    },
    {
      id:'ecoflow-river-3-plus',category:'power_station',asin:null,model:'RIVER 3 Plus',
      name:'EcoFlow RIVER 3 Plus 286 Wh 600 W Taşınabilir Güç İstasyonu',brand:'EcoFlow',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{capacityWh:286,continuousW:600,xBoostW:1200,pureSine:true,chemistry:'LFP',epsTransferMs:10,solarPowerMaxW:220,expandableWh:858},
      strengths:['286 Wh kapasite','600 W sürekli / 1200 W X-Boost sınıfı','<10 ms üretici UPS verisi','858 Wh’a kadar genişleyebilme'],
      limits:['1200 W X-Boost sürekli güç değildir ve motorlu yükler için kullanılmamalıdır','<10 ms geçiş yine de cihaz toleransıyla test edilmelidir','RIVER 3 Plus ve ek batarya varyantları karıştırılmamalıdır'],
      sourceNote:'EcoFlow Türkiye resmî sayfasında RIVER 3 Plus için 286 Wh, 600 W, 1200 W X-Boost, <10 ms, 220 W solar ve 858 Wh genişleme 30 Temmuz 2026 tarihinde doğrulandı.',
      technicalSource:'https://ecoflow.com.tr/urun/ecoflow-river-3-plus-tasinabilir-guc-kaynagi/',
      needIds:['portable-backup-energy'],relatedTools:relation('power_station').tools,relatedGuides:relation('power_station').guides,
      requiredEvidence:['yükün sürekli ve kalkış W değeri','hedef runtime','UPS geçiş toleransı','Amazon’daki tam RIVER 3 Plus modeli'],
      url:catalog.amazonSearchUrl('EcoFlow RIVER 3 Plus 286Wh 600W taşınabilir güç istasyonu')
    },
    {
      id:'ecoflow-delta-3-plus',category:'power_station',asin:null,model:'DELTA 3 Plus',
      name:'EcoFlow DELTA 3 Plus 1024 Wh 1800 W Taşınabilir Güç İstasyonu',brand:'EcoFlow',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{capacityWh:1024,continuousW:1800,surgeW:3600,xBoostW:2200,pureSine:true,chemistry:'LFP',epsTransferMs:10,solarPowerMaxW:1000,usbCMaxW:140,weightKg:12.5},
      strengths:['1024 Wh kapasite','1800 W sürekli / 3600 W dalgalanma sınıfı','10 ms üretici UPS verisi','1000 W solar ve iki 140 W USB-C'],
      limits:['X-Boost ve dalgalanma değerleri sürekli çıkış değildir','10 ms geçiş kritik cihazın gerçek toleransıyla doğrulanmalıdır','Pano veya sabit tesisat bağlantısı profesyonel transfer düzeni gerektirir'],
      sourceNote:'EcoFlow Türkiye resmî sayfasında DELTA 3 Plus için 1024 Wh, 1800 W, 3600 W dalgalanma, 10 ms, LFP, 1000 W solar ve 12,5 kg 30 Temmuz 2026 tarihinde doğrulandı.',
      technicalSource:'https://ecoflow.com.tr/urun/ecoflow-delta-3-plus-tasinabilir-guc-kaynagi/',
      needIds:['portable-backup-energy'],relatedTools:relation('power_station').tools,relatedGuides:relation('power_station').guides,
      requiredEvidence:['kritik yük W/Wh hesabı','motor kalkış gücü','UPS toleransı','Amazon’daki tam DELTA 3 Plus modeli'],
      url:catalog.amazonSearchUrl('EcoFlow DELTA 3 Plus 1024Wh 1800W taşınabilir güç istasyonu')
    },
    {
      id:'bluetti-ac70p',category:'power_station',asin:null,model:'AC70P',
      name:'BLUETTI AC70P 864 Wh 1000 W Taşınabilir Güç İstasyonu',brand:'BLUETTI',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{capacityWh:864,continuousW:1000,surgeW:1500,powerLiftingW:2000,pureSine:true,chemistry:'LFP',epsTransferMs:20,solarPowerMaxW:500,usbCMaxW:100,weightKg:10.7},
      strengths:['864 Wh kapasite','1000 W sürekli saf sinüs','500 W solar giriş','İki 100 W USB-C ve 20 ms üretici UPS verisi'],
      limits:['2000 W Power Lifting yalnız uygun rezistif yükler içindir','Motor/kompresör kalkışları 1000 W sürekli ve 1500 W dalgalanma sınırıyla değerlendirilmelidir','Amazon sonucunda AC70 ve AC70P karıştırılmamalıdır'],
      sourceNote:'BLUETTI resmî AC70P sayfasında 864 Wh, 1000 W sürekli, 1500 W dalgalanma, 2000 W rezistif Power Lifting, LFP, 500 W solar ve 20 ms 30 Temmuz 2026 tarihinde doğrulandı.',
      technicalSource:'https://www.bluettipower.eu/products/ac70p',
      needIds:['portable-backup-energy'],relatedTools:relation('power_station').tools,relatedGuides:relation('power_station').guides,
      requiredEvidence:['yükün sürekli ve kalkış W değeri','yükün rezistif/motorlu sınıfı','hedef runtime ve UPS toleransı','Amazon’daki tam AC70P modeli'],
      url:catalog.amazonSearchUrl('BLUETTI AC70P 864Wh 1000W taşınabilir güç istasyonu')
    },
    {
      id:'honda-eu22i',category:'generator',asin:null,model:'EU22i',
      name:'Honda EU22i 2200 W İnverter Jeneratör',brand:'Honda',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{ratedW:1800,maxW:2200,inverterTechnology:true,weightKg:21,fuel:'benzin'},
      strengths:['1800 W nominal / 2200 W maksimum güç','İnverter teknolojisi','21 kg taşınabilir sınıf','Yağ seviyesi koruması'],
      limits:['2200 W maksimum değer sürekli güç değildir','Kapalı, yarı kapalı veya binaya yakın kullanım karbonmonoksit riski doğurur','Motor kalkışı, yakıt depolama ve topraklama/transfer düzeni ayrıca değerlendirilmelidir'],
      sourceNote:'Honda resmî EU22i sayfasında 2200 W maksimum, 1800 W nominal, inverter teknolojisi ve 21 kg bilgileri 30 Temmuz 2026 tarihinde doğrulandı. Tek Amazon ASIN’i iddia edilmez.',
      technicalSource:'https://www.honda.co.uk/industrial/products/generators/inverter/eu22i.html',
      needIds:['portable-generation'],relatedTools:relation('generator').tools,relatedGuides:relation('generator').guides,
      requiredEvidence:['sürekli ve kalkış yükleri','yalnız açık alanda güvenli egzoz mesafesi','yakıt ve bakım planı','Amazon’daki tam EU22i modeli ve bölge çıkışı'],
      url:catalog.amazonSearchUrl('Honda EU22i 2200W inverter jeneratör')
    },
    {
      id:'victron-phoenix-vedirect-12-1200',category:'inverter',asin:null,model:'Phoenix VE.Direct 12/1200',
      name:'Victron Phoenix VE.Direct 12/1200 Saf Sinüs İnverter',brand:'Victron Energy',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{inputVoltageV:12,continuousW25C:1150,continuousW40C:1000,timeLimitedW:1200,peakW:1600,outputVoltageV:230,pureSine:true,efficiencyMaxPct:91,transferSwitchBuiltIn:false,protectionClass:'IP21'},
      strengths:['25 °C’de 1150 W sürekli güç','1600 W / 15 s tepe sınıfı','Saf sinüs 230 V çıkış','VE.Direct izleme ve yapılandırma'],
      limits:['Dahili transfer anahtarı veya şarj cihazı yoktur','12 V tarafta yüksek akım için kablo, sigorta ve batarya hesabı zorunludur','1200 model adı 1200 W sürekli güç anlamına gelmez'],
      sourceNote:'Victron Energy resmî VE.Direct 230 V teknik tablosunda 12/1200 için 1150 W sürekli (25 °C), 1000 W sürekli (40 °C), 1600 W/15 s tepe, %91 verim ve dahili transfer anahtarı olmadığı 30 Temmuz 2026 tarihinde doğrulandı.',
      technicalSource:'https://www.victronenergy.com/media/pg/Inverter_VE.Direct_230V_-_HW15/en/technical-specifications.html',
      needIds:['dc-ac-conversion'],relatedTools:relation('inverter').tools,relatedGuides:relation('inverter').guides,
      requiredEvidence:['sürekli ve kalkış W değeri','12 V batarya kapasitesi ve kısa devre akımı','DC kablo/sigorta hesabı','Amazon’daki tam 12/1200 ve priz varyantı'],
      url:catalog.amazonSearchUrl('Victron Phoenix VE Direct 12 1200 saf sinüs inverter')
    },
    {
      id:'x-sense-sc07-mr',category:'smoke_alarm',asin:null,model:'SC07-MR',
      name:'X-Sense SC07-MR Link+ Kombine Duman ve Karbonmonoksit Alarmı',brand:'X-Sense',
      status:'manufacturer_verified_search',verifiedAt,linkMode:'exact_model_search',
      attributes:{smokeSensor:'photoelectric',coSensor:'electrochemical',alarmDb:85,standardSmoke:'EN 14604',standardCo:'EN 50291',rfMHz:869.25,interconnected:true},
      strengths:['Fotoelektrik duman ve elektrokimyasal CO algılama','EN 14604 ve EN 50291 kapsamı','869,25 MHz RF bağlantı','85 dB çift sensör uyarısı'],
      limits:['Tek cihaz yerleşim ve adet planının yerine geçmez','Belge kapsamı ile üretim/değiştirme tarihi satın alma öncesi doğrulanmalıdır','Jeneratörün yanlış konumlandırılmasını veya havalandırma eksikliğini güvenli hale getirmez'],
      sourceNote:'X-Sense Türkiye resmî kombine dedektör sayfasında SC07-MR için fotoelektrik duman + elektrokimyasal CO, EN 14604, EN 50291, 869,25 MHz ve 85 dB 30 Temmuz 2026 tarihinde doğrulandı.',
      technicalSource:'https://x-sense.com.tr/urunler/kombine-dedektorler',
      needIds:['fire-early-warning','carbon-monoxide-warning'],relatedTools:smokeCoRelations.tools,relatedGuides:smokeCoRelations.guides,
      requiredEvidence:unique([...smokeCoRelations.evidence,'tam SC07-MR model kodu','EN 14604 ve EN 50291 belge kapsamı','üretim/değiştirme tarihi','yerleşim ve düzenli test planı']),
      url:catalog.amazonSearchUrl('X-Sense SC07-MR Link Plus duman karbonmonoksit alarmı')
    }
  ];

  for(const product of catalog.products){
    if((product.category==='usb_c_hub'||product.category==='display_cable')&&(!Array.isArray(product.needIds)||!product.needIds.length)){
      product.needIds=[...catalog.categoryNeeds[product.category]];
    }
    if((product.category==='usb_c_hub'||product.category==='display_cable')&&(!Array.isArray(product.relatedTools)||!product.relatedTools.length)){
      product.relatedTools=[...catalog.categoryRelations[product.category].tools];
    }
    if((product.category==='usb_c_hub'||product.category==='display_cable')&&(!Array.isArray(product.relatedGuides)||!product.relatedGuides.length)){
      product.relatedGuides=[...catalog.categoryRelations[product.category].guides];
    }
    if((product.category==='usb_c_hub'||product.category==='display_cable')&&(!Array.isArray(product.requiredEvidence)||!product.requiredEvidence.length)){
      product.requiredEvidence=[...catalog.categoryRelations[product.category].evidence];
    }
  }
  for(const product of additions){
    if(!catalog.products.some((current)=>current.id===product.id||Boolean(product.asin&&current.asin===product.asin)))catalog.products.push(product);
  }

  const previousSummary=catalog.knowledgeGraphSummary.bind(catalog);
  catalog.knowledgeGraphSummary=(options={})=>({...previousSummary(options),version:'2026-07-30-run51',generatedAt:'2026-07-30'});
  catalog.__salesProductExpansionRun50=true;
  catalog.__salesProductExpansionRun51=true;

  if(root&&root.document){
    const id='alo186-affiliate-knowledge-graph';
    const current=root.document.getElementById(id);
    if(current)current.remove();
    const script=root.document.createElement('script');
    script.id=id;
    script.type='application/ld+json';
    script.dataset.generated='alo186-affiliate-knowledge-graph-run51';
    script.textContent=JSON.stringify(catalog.knowledgeGraph());
    root.document.head.appendChild(script);
  }
  return catalog;
});
