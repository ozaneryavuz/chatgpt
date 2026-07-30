(function(root,factory){
  const current=root&&root.Alo186ProductCatalog
    ? root.Alo186ProductCatalog
    : (typeof module==='object'&&module.exports ? require('./catalog-sales-extension.js') : null);
  const api=factory(current,root);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186ProductCatalog=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(catalog,root){
  'use strict';

  if(!catalog)throw new Error('ALO186 Product Knowledge Graph yüklenemedi.');
  if(catalog.__affiliateProductExpansionV104)return catalog;
  if(catalog.affiliateTag!=='alo186rehber-21')throw new Error('Onaylı affiliate etiketi korunmadı.');
  if(typeof catalog.knowledgeGraph!=='function'||typeof catalog.publicAffiliateEligible!=='function'){
    throw new Error('Product Knowledge Graph güven işlevleri eksik.');
  }

  const verifiedAt='2026-07-30';
  const category={
    id:'car_charger',
    name:'Araç içi USB telefon ve dizüstü şarj cihazı',
    mode:'direct',
    risk:'consumer',
    affiliatePolicy:'verified_direct',
    description:'Araç çakmaklık gerilimi, cihazın USB-C PD/PPS ihtiyacı, tek ve çift port güç dağılımı ile uygun kablo birlikte doğrulanır. Aracın mevcut USB çıkışı ihtiyacı karşılıyorsa yeni ürün alınmaz.',
    searchQuery:'araç içi USB C PD PPS şarj cihazı 30W 65W'
  };
  if(!catalog.categories.some((item)=>item.id===category.id))catalog.categories.push(category);

  const portableEvseCategory={
    id:'portable_evse',
    name:'Taşınabilir elektrikli araç şarj cihazı (EVSE)',
    mode:'guide',
    risk:'safety',
    affiliatePolicy:'after_tool',
    nextStepUrl:'https://alo186.com/hesaplama/tasinabilir-ev-sarj-priz-uygunluk/',
    nextStepLabel:'Önce priz, devre, PE, RCD/DC koruma ve akım uygunluğunu test et',
    description:'Taşınabilir EVSE etiketi, prizin ve tesisatın aynı akımı güvenle taşıdığını kanıtlamaz. Priz sınıfı, ayrı devre, PE sürekliliği, RCD/DC kaçak koruması, belgelenmiş sürekli akım, araç kabulü, konnektör ve dış ortam koşulları doğrulanmalıdır.',
    searchQuery:'taşınabilir EV şarj cihazı EVSE Type 2 CEE Schuko ayarlanabilir akım'
  };
  if(!catalog.categories.some((item)=>item.id===portableEvseCategory.id))catalog.categories.push(portableEvseCategory);

  const displayCategory=catalog.getCategory('display_cable');
  if(displayCategory){
    displayCategory.name='USB-C, HDMI ve DisplayPort görüntü kablosu';
    displayCategory.description='Kaynak cihazın görüntü çıkışı, HDMI/DisplayPort standardı, kablo yönü, çözünürlük, yenileme hızı ve uzunluk birlikte doğrulanır. Konnektör uyumu tek başına görüntü veya yüksek yenileme garantisi değildir.';
    displayCategory.searchQuery='USB C HDMI 2.1 DisplayPort 1.4 4K 144Hz 8K kablo';
  }

  if(root&&root.location&&root.history&&typeof root.URL==='function'&&typeof root.history.replaceState==='function'){
    const currentUrl=new root.URL(root.location.href);
    if(currentUrl.searchParams.get('niyet')==='portable_evse'&&!currentUrl.searchParams.has('kategori')){
      currentUrl.searchParams.set('kategori','portable_evse');
      root.history.replaceState(root.history.state,'',currentUrl.toString());
    }
  }

  const needs=[
    {id:'vehicle-device-charging',name:'Araçta telefon, tablet ve uyumlu dizüstü şarjı'},
    {id:'phone-fast-charging',name:'Telefon ve tablette doğru USB-C hızlı şarj zinciri'},
    {id:'high-power-usbc-laptop',name:'65–140 W USB-C dizüstü güç zinciri'},
    {id:'portable-workstation',name:'Seyahat ve esnek çalışma bağlantı seti'},
    {id:'high-refresh-display',name:'Yüksek çözünürlük ve yenileme hızlı görüntü bağlantısı'},
    {id:'usbc-video-output',name:'USB-C görüntü çıkışı ve Alt Mode uyumu'}
  ];
  if(Array.isArray(catalog.needs))for(const need of needs)if(!catalog.needs.some((item)=>item.id===need.id))catalog.needs.push(need);
  if(catalog.categoryNeeds){
    catalog.categoryNeeds.car_charger=['vehicle-device-charging'];
    catalog.categoryNeeds.usb_c_charger=[...new Set([...(catalog.categoryNeeds.usb_c_charger||[]),'phone-fast-charging','high-power-usbc-laptop'])];
    catalog.categoryNeeds.usb_c_hub=[...new Set([...(catalog.categoryNeeds.usb_c_hub||[]),'portable-workstation','usbc-video-output'])];
    catalog.categoryNeeds.display_cable=[...new Set([...(catalog.categoryNeeds.display_cable||[]),'high-refresh-display','usbc-video-output'])];
  }
  if(catalog.categoryRelations){
    catalog.categoryRelations.car_charger={
      tools:['/hesaplama/usb-c-urun-kabul-testi/'],
      guides:['/urun-bilgi-grafigi/usb-c-ekosistemi/'],
      evidence:['araç prizinin 12–24 V ve hasarsız olması','cihazın kabul ettiği USB-C PD/PPS gücü','tek ve çift port güç dağılımı','uygun kablo ve mevcut araç USB çıkışının yetersizliği']
    };
  }
  const relation=(categoryId)=>catalog.categoryRelations&&catalog.categoryRelations[categoryId]
    ? catalog.categoryRelations[categoryId]
    : {tools:[],guides:[],evidence:[]};

  function baseFields(categoryId,needIds,intentIds,userNeed,bestFor,noBuyWhen,requiredEvidence){
    const rel=relation(categoryId);
    return {
      needIds,
      intentIds,
      userNeed,
      bestFor,
      noBuyWhen,
      requiredEvidence:requiredEvidence||[...(rel.evidence||[])],
      relatedTools:[...(rel.tools||[])],
      relatedGuides:[...(rel.guides||[])]
    };
  }

  const carRelation=relation('car_charger');
  const products=[
    {
      id:'belkin-ccb001-24w-dual-usba',category:'car_charger',asin:'B08558MGST',mpn:'CCB001btBK',
      name:'Belkin BoostCharge CCB001 Çift USB-A 24 W Araç Şarj Cihazı',brand:'Belkin',
      status:'verified_listing',verifiedAt,
      attributes:{inputMinV:12,inputMaxV:12,maxOutputW:24,maxSingleDeviceW:12,totalOutputW:24,usbCPorts:0,usbAPorts:2,maxCurrentA:4.8,pd:false,pps:false,powerIndicator:true},
      strengths:['Kullanıcı ihtiyacı: araçta iki temel USB-A cihazı aynı anda şarj etme','Her portta 12 W, toplam 24 W üretici sınıfı','İki USB-A port','Güç göstergesi'],
      limits:['Satın almama koşulu: aracın mevcut USB çıkışı veya elinizdeki şarj cihazı iki cihaz için yeterliyse yeni ürün almayın','USB-C PD/PPS hızlı şarj sağlamaz','24 W toplam güç iki port arasında 12 W + 12 W olarak kullanılır','Kablo kutu içeriği ve cihaz uçları satın alma öncesi doğrulanmalıdır'],
      sourceNote:'Amazon Türkiye ASIN B08558MGST ile CCB001btBK model eşleşmesi; 12 V giriş, iki USB-A, port başına 12 W ve toplam 24 W alanları Belkin resmî teknik kaynağıyla 30 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, satıcı, puan, yorum ve garanti yayımlanmaz.',
      technicalSource:'https://www.belkin.com/in/p/dual-usb-a-car-charger-24w/CCB001btBK.html',
      needIds:['vehicle-device-charging'],intentIds:['seyahat-karavan'],relatedTools:[...carRelation.tools],relatedGuides:[...carRelation.guides],requiredEvidence:[...carRelation.evidence],
      userNeed:'Araçta iki düşük güçlü USB-A cihazını eşzamanlı şarj etmek',bestFor:['USB-A kablolu telefon ve küçük cihazlar','12 V araç prizi'],noBuyWhen:['Araçtaki mevcut USB çıkışları yeterliyse','USB-C PD/PPS gerekiyorsa'],
      url:catalog.amazonProductUrl('B08558MGST')
    },
    {
      id:'belkin-cca004-30w-usbc',category:'car_charger',asin:'B0BTP9GF27',mpn:'CCA004btBK',
      name:'Belkin BoostCharge CCA004 USB-C PD/PPS 30 W Araç Şarj Cihazı',brand:'Belkin',
      status:'verified_listing',verifiedAt,
      attributes:{inputMinV:12,inputMaxV:24,maxOutputW:30,maxSingleDeviceW:30,totalOutputW:30,usbCPorts:1,usbAPorts:0,pd:true,pps:true,usbIfCertified:true,powerIndicator:true,operatingTempMinC:0,operatingTempMaxC:40},
      strengths:['Kullanıcı ihtiyacı: araçta tek USB-C telefon veya tableti 30 W sınıfında şarj etme','30 W USB-C Power Delivery','PPS desteği','USB-IF sertifikası ve kompakt yapı'],
      limits:['Satın almama koşulu: aracın mevcut USB-C portu cihazın gerekli gücünü sağlıyorsa yeni ürün almayın','Tek portludur; ikinci cihaz için ayrı çıkış sağlamaz','30 W yalnız cihaz ve kablo uyumluysa kullanılabilir','Dizüstü bilgisayarın gerektirdiği güç 30 W üzerindeyse uygun kabul edilmemelidir'],
      sourceNote:'Amazon Türkiye ASIN B0BTP9GF27 ile CCA004btBK model eşleşmesi; 12–24 V giriş, tek USB-C, 30 W PD/PPS ve çalışma sıcaklığı alanları Belkin resmî teknik kaynağıyla 30 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, satıcı, puan, yorum ve garanti yayımlanmaz.',
      technicalSource:'https://www.belkin.com/p/30w-usb-c-car-charger/CCA004btBK.html',
      needIds:['vehicle-device-charging'],intentIds:['seyahat-karavan','mobil-enerji'],relatedTools:[...carRelation.tools],relatedGuides:[...carRelation.guides],requiredEvidence:[...carRelation.evidence],
      userNeed:'Araçta tek USB-C telefon veya tableti PD/PPS ile şarj etmek',bestFor:['30 W veya daha düşük USB-C cihazlar','12–24 V araç prizi'],noBuyWhen:['Araç USB-C portu gereken gücü sağlıyorsa','İki cihaz veya 30 W üzeri dizüstü gücü gerekiyorsa'],
      url:catalog.amazonProductUrl('B0BTP9GF27')
    },
    {
      id:'bix-bxac65c-65w',category:'car_charger',asin:'B0BT4GWMS3',mpn:'BXAC65C',
      name:'Bix BXAC65C 65 W USB-C PD ve 18 W USB-A Araç Şarj Cihazı',brand:'Bix',
      status:'verified_listing',verifiedAt,
      attributes:{inputMinV:12,inputMaxV:24,maxOutputW:65,maxSingleDeviceW:65,dualPortCombinedW:24,usbCPorts:1,usbAPorts:1,pd3:true,qc3:true,usbCMaxW:65,usbAMaxW:18,pullTab:true},
      strengths:['Kullanıcı ihtiyacı: araçta USB-C dizüstü/telefon ile ikinci USB-A cihazı şarj etme','Tek USB-C portta 65 W PD 3.0 sınıfı','USB-A portta 18 W QC 3.0 sınıfı','12–24 V araç girişi ve çıkarma halkası'],
      limits:['Satın almama koşulu: mevcut araç USB-C çıkışı cihazın gereken gücünü ve ikinci cihaz ihtiyacını karşılıyorsa yeni ürün almayın','İki port birlikte kullanıldığında üretici verisi 5 V / 4,8 A, yaklaşık 24 W toplamdır; 65 W + 18 W eşzamanlı değildir','65 W için uygun USB-C kablo ve cihaz PD profili gerekir','Araç prizinde gevşeklik, ısınma veya hasar varsa ürünü kullanmadan prizi kontrol ettirin'],
      sourceNote:'Amazon Türkiye ASIN B0BT4GWMS3 ile BXAC65C model eşleşmesi; 12–24 V giriş, USB-C 65 W PD 3.0, USB-A 18 W QC 3.0 ve iki portta 5 V / 4,8 A alanları Bix resmî teknik kaynağıyla 30 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, satıcı, puan, yorum ve garanti yayımlanmaz.',
      technicalSource:'https://bix.com.tr/65w-cift-portlu-pd-arac-sarji-beyaz/',
      needIds:['vehicle-device-charging'],intentIds:['seyahat-karavan','dizustu-yuksek-guc'],relatedTools:[...carRelation.tools],relatedGuides:[...carRelation.guides],requiredEvidence:[...carRelation.evidence],
      userNeed:'Araçta 65 W USB-C cihazla ikinci USB-A cihazı şarj etmek',bestFor:['Tek port kullanımında 65 W PD cihazlar','12–24 V araç prizi'],noBuyWhen:['İki port birlikteyken 65 W bekleniyorsa','Araç prizi gevşek veya ısınıyorsa'],
      url:catalog.amazonProductUrl('B0BT4GWMS3')
    },
    {
      id:'spigen-ach08701-20w',category:'usb_c_charger',asin:'B0DWT5G6QQ',mpn:'ACH08701',
      name:'Spigen ACH08701 20 W USB-C PD 3.0 GaN Şarj Cihazı',brand:'Spigen',
      status:'verified_listing',verifiedAt,
      attributes:{maxOutputW:20,maxSingleDeviceW:20,totalOutputW:20,usbCPorts:1,usbAPorts:0,pd3:true,gan:true,pps:false},
      strengths:['Tek cihazda 20 W USB-C PD 3.0','Tek portlu kompakt GaN yapı','Aşırı ısınma, aşırı akım ve kısa devre koruması üretici açıklamasında yer alır'],
      limits:['20 W üzeri tablet veya dizüstü ihtiyacı için yeterli kabul edilmemelidir','Kablo kutuya dahil değildir','Cihazın hızlı şarj protokolü ve kablo ayrıca doğrulanmalıdır'],
      sourceNote:'Amazon Türkiye ASIN B0DWT5G6QQ ile ACH08701 model eşleşmesi; 20 W, tek USB-C, USB PD 3.0 ve GaN alanları Spigen Türkiye teknik sayfasıyla 30 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, puan, yorum, satıcı ve garanti yayımlanmaz.',
      technicalSource:'https://www.spigen.com.tr/urun/spigen-20w-usb-c-mini-hizli-sarj-aleti-samsung-pps-sarj-isisini-dusurur-gan-destekli-akim-korumali-guc-adaptoru-iphone-android-ipad-type-c-ee201-white-ach08701',
      ...baseFields('usb_c_charger',['phone-fast-charging'],['telefon-hizli-sarj','seyahat-calisma-seti','mobil-enerji'],'Telefon ve küçük tablet için tek portlu 20 W USB-C şarj cihazı seçmek',['20 W veya daha düşük USB-C PD cihazlar','Seyahat ve yedek adaptör kullanımı'],['Mevcut adaptör cihazı gereken hızda ve güvenle şarj ediyorsa','Birden fazla port veya 20 W üzeri güç gerekiyorsa'],['cihazın kabul ettiği güç','USB-C PD profili','kablo uçları ve güç sınıfı','tek port ihtiyacının yeterli olması']),
      url:catalog.amazonProductUrl('B0DWT5G6QQ')
    },
    {
      id:'ugreen-nexode-140w-90549',category:'usb_c_charger',asin:'B0B127GW4D',mpn:'90549',
      name:'UGREEN Nexode 90549 140 W PD 3.1 Üç Port GaN Şarj Cihazı',brand:'UGREEN',
      status:'verified_listing',verifiedAt,
      attributes:{maxOutputW:140,maxSingleDeviceW:140,totalOutputW:140,usbCPorts:2,usbAPorts:1,pd31:true,pps:true,qc4:true,gan:true,includedCableW:240,includedCableM:1},
      strengths:['Tek USB-C portta 140 W PD 3.1 sınıfı','İki USB-C ve bir USB-A','PPS ve QC protokol kapsamı','1 m / 240 W USB-C kablo ürün paketinde belirtilmiştir'],
      limits:['140 W için cihazın USB PD 3.1 EPR kabulü gerekir','Çoklu port kullanımında güç paylaşılır','Dahil kablonun veri ve görüntü özellikleri ayrıca doğrulanmalıdır'],
      sourceNote:'UGREEN 90549 teknik sayfası ile Amazon ürün kimliği B0B127GW4D eşleştirildi; 140 W, iki USB-C + bir USB-A, PD 3.1, PPS ve 1 m 240 W kablo alanları 30 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, puan, yorum, satıcı ve garanti yayımlanmaz.',
      technicalSource:'https://ugreen.com.tr/urun/ugreen-nexode-140w-usb-type-c-qc-4-0-pd-3-1-gan-3-portlu-hizli-sarj-cihazi/',
      ...baseFields('usb_c_charger',['high-power-usbc-laptop','portable-workstation'],['dizustu-yuksek-guc','seyahat-calisma-seti'],'100 W üzeri USB-C dizüstü ve çoklu cihaz güç zinciri kurmak',['USB PD 3.1 destekli yüksek güçlü dizüstüler','Tek adaptörle telefon ve dizüstü kullananlar'],['Cihaz 65 W veya daha düşük güçle ihtiyacı karşılıyorsa','PD 3.1/EPR veya uygun kablo doğrulanmadıysa'],['dizüstünün kabul ettiği W','USB PD 3.1/EPR desteği','tek port ve toplam güç dağılımı','kablo güç sınıfı']),
      url:catalog.amazonProductUrl('B0B127GW4D')
    },
    {
      id:'apple-140w-a2452',category:'usb_c_charger',asin:'B0D232C5JJ',mpn:'A2452',
      name:'Apple A2452 140 W USB-C Güç Adaptörü',brand:'Apple',
      status:'verified_listing',verifiedAt,
      attributes:{maxOutputW:140,maxSingleDeviceW:140,totalOutputW:140,usbCPorts:1,usbAPorts:0,pd:true,pd31:true,cableIncluded:false},
      strengths:['Tek USB-C çıkışta 140 W sınıfı','Apple 16 inç MacBook Pro hızlı şarj zinciri için resmî olarak tanımlanmıştır','Tek portlu yapı'],
      limits:['Şarj kablosu ayrı satılır','16 inç MacBook Pro hızlı şarjı için modele göre USB-C–MagSafe 3 veya 240 W USB-C kablo gerekir','Daha düşük güçlü cihaz yeni adaptör satın almayı zorunlu kılmaz'],
      sourceNote:'Amazon ürün kimliği B0D232C5JJ ile Apple 140 W USB-C Güç Adaptörü eşleştirildi; 140 W tek USB-C ve A2452 model bilgisi Apple Türkiye destek kaynaklarıyla 30 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, puan, yorum, satıcı ve garanti yayımlanmaz.',
      technicalSource:'https://support.apple.com/tr-tr/102378',
      ...baseFields('usb_c_charger',['high-power-usbc-laptop'],['dizustu-yuksek-guc'],'Uyumlu MacBook için tek portlu 140 W USB-C güç adaptörü seçmek',['16 inç MacBook Pro hızlı şarj zinciri','Tek USB-C port isteyen kullanıcılar'],['Mevcut adaptör önerilen gücü sağlıyorsa','Uygun MagSafe 3 veya 240 W USB-C kablo yoksa','Çoklu cihaz portu gerekiyorsa'],['MacBook tam modeli','önerilen adaptör gücü','MagSafe 3 veya 240 W USB-C kablo','mevcut adaptörün gerçek W değeri']),
      url:catalog.amazonProductUrl('B0D232C5JJ')
    },
    {
      id:'belkin-avc006-4in1',category:'usb_c_hub',asin:'B08X5168HM',mpn:'AVC006btSGY',
      name:'Belkin CONNECT AVC006 4’ü 1 Arada USB-C Hub',brand:'Belkin',
      status:'verified_listing',verifiedAt,
      attributes:{ports:4,hdmiVersion:'1.4',hdmiMax:'4K@30Hz',usbA3Ports:2,dataTransferGbps:5,pdPassThroughW:100,internalPowerW:15,ethernet:false,sdReader:false},
      strengths:['HDMI 1.4 ile 4K@30 Hz','İki USB-A 3.0 port','5 Gbps veri sınıfı','100 W’a kadar PD geçiş sınıfı'],
      limits:['100 W girişten hubın çalışması için 15 W ayrılır','Güç adaptörü dahil değildir','Ethernet ve kart okuyucu içermez','Kaynak USB-C portu görüntü çıkışını desteklemelidir'],
      sourceNote:'Belkin AVC006btSGY resmî teknik sayfası ile Amazon ürün kimliği B08X5168HM eşleştirildi; HDMI 1.4 4K@30 Hz, iki USB-A, 5 Gbps ve 100 W PD geçiş / 15 W iç tüketim alanları 30 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, puan, yorum, satıcı ve garanti yayımlanmaz.',
      technicalSource:'https://www.belkin.com/p/usb-c-4-in-1-multiport-adapter/AVC006btSGY.html',
      ...baseFields('usb_c_hub',['portable-workstation','usbc-video-output'],['seyahat-calisma-seti','ev-ofis-konforu','harici-ekran'],'HDMI ve iki USB-A portunu sade bir USB-C hub ile eklemek',['Seyahat ve küçük masa düzeni','Ethernet veya kart okuyucu gerekmeyen kullanıcılar'],['Mevcut hub gerekli portları sağlıyorsa','4K@60 Hz, Ethernet veya kart okuyucu gerekiyorsa','Host USB-C portunda görüntü çıkışı yoksa'],['host USB-C görüntü desteği','4K@30 Hz sınırının yeterliliği','PD adaptör gücü ve 15 W iç tüketim','gerekli USB-A port sayısı']),
      url:catalog.amazonProductUrl('B08X5168HM')
    },
    {
      id:'ugreen-hdmi21-25911-3m',category:'display_cable',asin:'B0CFF9T3PS',mpn:'25911',
      name:'UGREEN 25911 HDMI 2.1 Ultra High Speed Kablo 3 m',brand:'UGREEN',
      status:'verified_listing',verifiedAt,
      attributes:{connectorA:'HDMI',connectorB:'HDMI',lengthM:3,hdmiVersion:'2.1',maxDataGbps:48,maxResolution:'8K@60Hz',max4KRefreshHz:240,vrr:true,allm:true,earc:true},
      strengths:['48 Gbps HDMI 2.1 sınıfı','8K@60 Hz ve 4K yüksek yenileme sınıfı','VRR, ALLM ve eARC işlevleri','3 metre uzunluk'],
      limits:['Kaynak ve ekranın aynı HDMI 2.1 işlevini desteklemesi gerekir','4K@240 Hz her cihaz zincirinde garanti değildir','Mevcut kablo hedef çözünürlüğü karşılıyorsa yeni ürün gerekmez'],
      sourceNote:'Amazon Türkiye ASIN B0CFF9T3PS ile UGREEN 25911 model eşleşmesi; HDMI 2.1, 48 Gbps, 8K@60 Hz, 4K yüksek yenileme, VRR, ALLM, eARC ve 3 m alanları 30 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, puan, yorum, satıcı ve garanti yayımlanmaz.',
      technicalSource:'https://www.amazon.com.tr/dp/B0CFF9T3PS',
      ...baseFields('display_cable',['high-refresh-display'],['harici-ekran','ev-ofis-konforu'],'HDMI 2.1 kaynak ile ekran arasında yüksek çözünürlük veya yenileme bağlantısı kurmak',['4K@120 Hz oyun/monitör zinciri','eARC veya VRR ihtiyacı'],['Mevcut HDMI kablo hedef modu güvenle çalıştırıyorsa','Kaynak veya ekran HDMI 2.1 özelliğini desteklemiyorsa'],['kaynak HDMI sürümü','ekran HDMI sürümü','hedef çözünürlük/yenileme','3 m uzunluğun sistemle uyumu']),
      url:catalog.amazonProductUrl('B0CFF9T3PS')
    },
    {
      id:'veggieg-vz631-dp14-2m',category:'display_cable',asin:'B0DN61ZDBQ',mpn:'V-Z631',
      name:'VegGieg V-Z631 DisplayPort 1.4 Kablo 2 m',brand:'VegGieg',
      status:'verified_listing',verifiedAt,
      attributes:{connectorA:'DisplayPort',connectorB:'DisplayPort',lengthM:2,displayPortVersion:'1.4',maxDataGbps:32.4,maxResolution:'8K@60Hz',max4KRefreshHz:144,max2KRefreshHz:240},
      strengths:['DisplayPort 1.4 sınıfı','32,4 Gbps bant genişliği','8K@60 Hz / 4K@144 Hz / 2K@240 Hz ürün sınıfı','2 metre uzunluk'],
      limits:['Gerçek çözünürlük ve yenileme ekran kartı ile monitör tarafından da desteklenmelidir','Kablo tipi HDMI değil DisplayPort–DisplayPort’tur','Mevcut kablo hedef modu sağlıyorsa yeni ürün almayın'],
      sourceNote:'Amazon Türkiye ASIN B0DN61ZDBQ ile V-Z631 model eşleşmesi; DisplayPort 1.4, 32,4 Gbps, 8K@60 Hz, 4K@144 Hz, 2K@240 Hz ve 2 m alanları 30 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, puan, yorum, satıcı ve garanti yayımlanmaz.',
      technicalSource:'https://www.amazon.com.tr/dp/B0DN61ZDBQ',
      ...baseFields('display_cable',['high-refresh-display'],['harici-ekran','ev-ofis-konforu'],'DisplayPort kaynak ve monitör arasında yüksek yenileme bağlantısı kurmak',['DisplayPort 1.4 ekran kartı ve monitörler','2 m masaüstü bağlantısı'],['Mevcut kablo hedef yenileme hızını kararlı biçimde sağlıyorsa','Kaynak veya monitör gerekli bant genişliğini desteklemiyorsa'],['kaynak ve ekran DisplayPort sürümü','hedef çözünürlük/yenileme','kablo uzunluğu','ekran kartı ve monitör bant genişliği']),
      url:catalog.amazonProductUrl('B0DN61ZDBQ')
    },
    {
      id:'veggieg-vz623-usbc-dp14-2m',category:'display_cable',asin:'B0DK6QPTFQ',mpn:'V-Z623',
      name:'VegGieg V-Z623 USB-C ↔ DisplayPort 1.4 Çift Yönlü Kablo 2 m',brand:'VegGieg',
      status:'verified_listing',verifiedAt,
      attributes:{connectorA:'USB-C',connectorB:'DisplayPort',lengthM:2,displayPortVersion:'1.4',bidirectional:true,maxResolution:'8K@60Hz',max4KRefreshHz:144,max2KRefreshHz:165,powerDelivery:false},
      strengths:['USB-C ile DisplayPort arasında çift yönlü görüntü','8K@60 Hz / 4K@144 Hz ürün sınıfı','Örgülü 2 metre kablo'],
      limits:['USB-C portu DisplayPort Alt Mode veya uyumlu Thunderbolt görüntü çıkışı sağlamalıdır','Kablo şarj veya PD geçişi sağlamaz','Çözünürlük cihaz ve ekranla sınırlıdır'],
      sourceNote:'Amazon Türkiye ASIN B0DK6QPTFQ ile V-Z623 model eşleşmesi; USB-C ↔ DisplayPort 1.4 çift yön, 8K@60 Hz, 4K@144 Hz ve 2 m alanları 30 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, puan, yorum, satıcı ve garanti yayımlanmaz.',
      technicalSource:'https://www.amazon.com.tr/dp/B0DK6QPTFQ',
      ...baseFields('display_cable',['usbc-video-output','high-refresh-display'],['harici-ekran','dizustu-yuksek-guc'],'USB-C görüntü çıkışını DisplayPort monitöre veya ters yönde bağlamak',['Alt Mode/Thunderbolt destekli dizüstüler','Yüksek yenilemeli DisplayPort ekranlar'],['USB-C portunda görüntü çıkışı yoksa','Aynı kablodan şarj veya veri çevre birimi bağlantısı bekleniyorsa','Mevcut kablo kararlı çalışıyorsa'],['USB-C DisplayPort Alt Mode/Thunderbolt','kablo yönü','hedef çözünürlük/yenileme','şarj geçişi gerekmediği']),
      url:catalog.amazonProductUrl('B0DK6QPTFQ')
    },
    {
      id:'daytona-hc01-usbc-hdmi-18m',category:'display_cable',asin:'B096G51911',mpn:'HC-01',
      name:'Daytona HC-01 USB-C → HDMI Görüntü Kablosu 1,8 m',brand:'Daytona',
      status:'verified_listing',verifiedAt,
      attributes:{connectorA:'USB-C',connectorB:'HDMI',lengthM:1.8,direction:'USB-C to HDMI',maxResolutionClaim:'4K@60Hz',externalPowerRequired:false,powerDelivery:false},
      strengths:['USB-C kaynaktan HDMI ekrana tak-çalıştır görüntü','1,8 metre uzunluk','Haricî güç gerektirmez'],
      limits:['Kaynak USB-C portunda görüntü çıkışı bulunmalıdır','Kablo şarj geçişi sağlamaz','4K/60 Hz sonucu kaynak, ekran ve port standardıyla doğrulanmalıdır','Tek yönlü kullanım varsayılmalıdır'],
      sourceNote:'Amazon Türkiye ASIN B096G51911 ile Daytona HC-01 model eşleşmesi; USB-C → HDMI, 1,8 m, haricî güç gerektirmeme ve 4K/60 Hz ürün beyanı 30 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, puan, yorum, satıcı ve garanti yayımlanmaz.',
      technicalSource:'https://www.amazon.com.tr/dp/B096G51911',
      ...baseFields('display_cable',['usbc-video-output'],['harici-ekran','seyahat-calisma-seti'],'USB-C cihazı HDMI TV, projektör veya monitöre bağlamak',['Sunum ve seyahat bağlantısı','USB-C görüntü çıkışlı dizüstü veya telefonlar'],['Kaynak USB-C portunda görüntü çıkışı yoksa','Aynı bağlantıda şarj geçişi gerekiyorsa','Mevcut hub veya adaptör HDMI ihtiyacını karşılıyorsa'],['kaynak USB-C görüntü desteği','hedef HDMI çözünürlük/yenileme','kablo yönü','şarj geçişi gerekmediği']),
      url:catalog.amazonProductUrl('B096G51911')
    }
  ];

  for(const product of products){
    if(!catalog.products.some((current)=>current.id===product.id||current.asin===product.asin))catalog.products.push(product);
  }

  if(!catalog.__userFocusedProductNodeV104){
    const previousProductNode=catalog.productNode.bind(catalog);
    catalog.productNode=(product,options={})=>{
      const node=previousProductNode(product,options);
      const properties=Array.isArray(node.additionalProperty)?node.additionalProperty:[];
      const add=(name,value)=>{if(value!==null&&value!==undefined&&value!=='')properties.push({'@type':'PropertyValue',name,value});};
      add('Kullanıcı ihtiyacı',product.userNeed);
      for(const item of product.bestFor||[])add('En uygun kullanım',item);
      for(const item of product.noBuyWhen||[])add('Satın almama koşulu',item);
      for(const item of product.requiredEvidence||[])add('Satın alma öncesi kanıt',item);
      node.additionalProperty=properties;
      if(product.bestFor?.length)node.audience={'@type':'Audience',audienceType:product.bestFor.join(' · ')};
      const keywords=[product.userNeed,...(product.bestFor||[]),...(product.intentIds||[])].filter(Boolean);
      if(keywords.length)node.keywords=keywords.join(', ');
      return node;
    };
    catalog.__userFocusedProductNodeV104=true;
  }

  if(typeof catalog.knowledgeGraphSummary==='function'){
    const previousSummary=catalog.knowledgeGraphSummary.bind(catalog);
    catalog.knowledgeGraphSummary=(options={})=>{
      const summary=previousSummary(options);
      const exact=catalog.products.filter((product)=>product.status==='verified_listing');
      return {
        ...summary,
        version:'2026-07-30-v104',
        generatedAt:'2026-07-30',
        productCount:catalog.products.filter((product)=>catalog.isCatalogProduct?catalog.isCatalogProduct(product):true).length,
        exactListingCount:exact.length,
        userFocusedProductCount:catalog.products.filter((product)=>product.userNeed&&product.noBuyWhen?.length).length
      };
    };
  }

  catalog.__carChargerAffiliateRun54=true;
  catalog.__affiliateProductExpansionV104=true;
  catalog.productExpansionV104={
    version:104,
    generatedAt:verifiedAt,
    exactProductsAdded:products.length,
    userFocusedFields:['userNeed','bestFor','noBuyWhen','requiredEvidence','intentIds'],
    newExactProductIds:products.map((product)=>product.id)
  };

  if(root&&root.document){
    const id='alo186-affiliate-knowledge-graph';
    const current=root.document.getElementById(id);
    if(current)current.remove();
    const script=root.document.createElement('script');
    script.id=id;
    script.type='application/ld+json';
    script.dataset.generated='alo186-affiliate-knowledge-graph-v104';
    script.textContent=JSON.stringify(catalog.knowledgeGraph());
    root.document.head.appendChild(script);
  }
  return catalog;
});
