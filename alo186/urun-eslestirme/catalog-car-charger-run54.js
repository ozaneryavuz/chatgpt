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
  if(catalog.__carChargerAffiliateRun54)return catalog;
  if(catalog.affiliateTag!=='alo186rehber-21')throw new Error('Onaylı affiliate etiketi korunmadı.');
  if(typeof catalog.knowledgeGraph!=='function'||typeof catalog.publicAffiliateEligible!=='function'){
    throw new Error('Product Knowledge Graph güven işlevleri eksik.');
  }

  const verifiedAt='2026-07-30';
  const growthVerifiedAt='2026-07-31';
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

  if(root&&root.location&&root.history&&typeof root.URL==='function'&&typeof root.history.replaceState==='function'){
    const currentUrl=new root.URL(root.location.href);
    if(currentUrl.searchParams.get('niyet')==='portable_evse'&&!currentUrl.searchParams.has('kategori')){
      currentUrl.searchParams.set('kategori','portable_evse');
      root.history.replaceState(root.history.state,'',currentUrl.toString());
    }
  }

  const need={id:'vehicle-device-charging',name:'Araçta telefon, tablet ve uyumlu dizüstü şarjı'};
  if(Array.isArray(catalog.needs)&&!catalog.needs.some((item)=>item.id===need.id))catalog.needs.push(need);
  if(catalog.categoryNeeds)catalog.categoryNeeds.car_charger=['vehicle-device-charging'];
  if(catalog.categoryRelations){
    catalog.categoryRelations.car_charger={
      tools:['/hesaplama/usb-c-urun-kabul-testi/'],
      guides:['/urun-bilgi-grafigi/usb-c-ekosistemi/'],
      evidence:['araç prizinin 12–24 V ve hasarsız olması','cihazın kabul ettiği USB-C PD/PPS gücü','tek ve çift port güç dağılımı','uygun kablo ve mevcut araç USB çıkışının yetersizliği']
    };
  }
  const relation=catalog.categoryRelations&&catalog.categoryRelations.car_charger
    ? catalog.categoryRelations.car_charger
    : {tools:[],guides:[],evidence:[]};

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
      needIds:['vehicle-device-charging'],relatedTools:[...relation.tools],relatedGuides:[...relation.guides],requiredEvidence:[...relation.evidence],
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
      needIds:['vehicle-device-charging'],relatedTools:[...relation.tools],relatedGuides:[...relation.guides],requiredEvidence:[...relation.evidence],
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
      needIds:['vehicle-device-charging'],relatedTools:[...relation.tools],relatedGuides:[...relation.guides],requiredEvidence:[...relation.evidence],
      url:catalog.amazonProductUrl('B0BT4GWMS3')
    },
    {
      id:'anker-323-a2735-52w',category:'car_charger',asin:'B0BPGSRYFH',mpn:'A2735',
      name:'Anker 323 A2735 52,5 W USB-C ve USB-A Araç Şarj Cihazı',brand:'Anker',
      status:'verified_listing',verifiedAt:growthVerifiedAt,
      attributes:{inputMinV:12,inputMaxV:24,maxOutputW:52.5,maxSingleDeviceW:30,totalOutputW:52.5,usbCPorts:1,usbAPorts:1,usbCMaxW:30,usbAMaxW:22.5,powerIq3:true,activeShield2:true},
      strengths:['Kullanıcı ihtiyacı: araçta bir USB-C telefon/tablet ile ikinci USB-A cihazı aynı anda şarj etme','USB-C portta 30 W, USB-A portta 22,5 W sınıfı','Toplam 52,5 W üretici değeri','12–24 V araç girişi ve ActiveShield 2.0 sıcaklık izleme yaklaşımı'],
      limits:['Satın almama koşulu: aracın mevcut USB çıkışları iki cihazın güç ihtiyacını karşılıyorsa yeni ürün almayın','USB-C port tek başına en fazla 30 W sınıfındadır; daha yüksek güç isteyen dizüstüler için uygun kabul edilmemelidir','Hızlı şarj cihaz ve kablo protokol uyumuna bağlıdır','Araç prizinde gevşeklik, oksitlenme veya ısınma varsa ürünü kullanmadan prizi kontrol ettirin'],
      sourceNote:'Amazon Türkiye ASIN B0BPGSRYFH ile Anker A2735 model eşleşmesi; 12–24 V giriş, toplam 52,5 W, USB-C 30 W ve USB-A 22,5 W alanları Anker resmî teknik kaynağıyla 31 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, satıcı, puan, yorum ve garanti yayımlanmaz.',
      technicalSource:'https://www.anker.com/products/a2735',
      needIds:['vehicle-device-charging'],relatedTools:[...relation.tools],relatedGuides:[...relation.guides],requiredEvidence:[...relation.evidence],
      url:catalog.amazonProductUrl('B0BPGSRYFH')
    },
    {
      id:'ugreen-60980-52w',category:'car_charger',asin:'B082WZ139M',mpn:'60980',
      name:'UGREEN 60980 52,5 W USB-C PD ve USB-A QC Araç Şarj Cihazı',brand:'UGREEN',
      status:'verified_listing',verifiedAt:growthVerifiedAt,
      attributes:{maxOutputW:52.5,maxSingleDeviceW:30,totalOutputW:52.5,usbCPorts:1,usbAPorts:1,usbCMaxW:30,usbAMaxW:22.5,pd:true,qc:true,aluminumBody:true,totalUsbPorts:2},
      strengths:['Kullanıcı ihtiyacı: USB-C PD ve USB-A hızlı şarj kullanan iki mobil cihazı araçta birlikte besleme','Toplam 52,5 W ürün sınıfı','Bir USB-C ve bir USB-A çıkış','Alüminyum gövde ve kısa devre, aşırı ısınma, aşırı akım koruma açıklaması'],
      limits:['Satın almama koşulu: mevcut araç adaptörü ve USB çıkışları cihazlarınızı gereken hızda şarj ediyorsa yeni ürün almayın','İki portun güç dağılımı cihaz protokolüne göre değişebilir; 30 W ve 22,5 W kabulü cihaz/kablo ile doğrulanmalıdır','Üretici Türkiye sayfasındaki giriş voltajı alanı tutarsız göründüğünden araç uyumluluğu satın alma öncesi Amazon ürün sayfasında tekrar kontrol edilmelidir','Hasarlı veya ısınan çakmaklık prizinde kullanılmamalıdır'],
      sourceNote:'Amazon Türkiye ASIN B082WZ139M ile UGREEN 60980 SKU eşleşmesi; 52,5 W ürün sınıfı, USB-C PD, USB-A hızlı şarj, iki port ve koruma özellikleri UGREEN resmî teknik kaynağıyla 31 Temmuz 2026 tarihinde doğrulandı. Kaynaktaki tutarsız giriş voltajı değeri kataloğa aktarılmadı. Fiyat, stok, satıcı, puan, yorum ve garanti yayımlanmaz.',
      technicalSource:'https://www.ugreen.com/tr-tr/products/tr-60980',
      needIds:['vehicle-device-charging'],relatedTools:[...relation.tools],relatedGuides:[...relation.guides],requiredEvidence:[...relation.evidence],
      url:catalog.amazonProductUrl('B082WZ139M')
    },
    {
      id:'ugreen-70594-dual-usbc-40w',category:'car_charger',asin:'B07Z1NPFWC',mpn:'70594',
      name:'UGREEN 70594 Çift USB-C PD 40 W Araç Şarj Cihazı',brand:'UGREEN',
      status:'verified_listing',verifiedAt:growthVerifiedAt,
      attributes:{inputMinV:12,inputMaxV:24,maxOutputW:40,maxSingleDeviceW:20,totalOutputW:40,usbCPorts:2,usbAPorts:0,usbC1MaxW:20,usbC2MaxW:20,pd3:true,aluminumBody:true},
      strengths:['Kullanıcı ihtiyacı: araçta iki USB-C telefonu veya düşük güçlü tableti aynı anda şarj etme','İki USB-C port','Port başına 20 W ve toplam 40 W üretici sınıfı','12–24 V araç girişi, alüminyum gövde ve akıllı güç koruma açıklaması'],
      limits:['Satın almama koşulu: aracınızda iki yeterli USB-C çıkışı varsa veya tek cihaz kullanıyorsanız yeni ürün almayın','Tek port en fazla 20 W sınıfındadır; 25–30 W üzeri isteyen cihazlarda beklenen hızı sağlamaz','Amazon Türkiye ürün başlığında güç değeri farklı görünebildiğinden model numarası 70594 satın alma öncesi tekrar doğrulanmalıdır','Kablolar kutu içeriğine dahil kabul edilmemeli; uygun USB-C kablo ayrıca doğrulanmalıdır'],
      sourceNote:'Amazon Türkiye’de UGREEN 70594 modelinin aktif ürün kaydı ile ASIN B07Z1NPFWC eşleşmesi; 12–24 V giriş, iki USB-C, port başına 20 W ve toplam 40 W alanları güvenilir UGREEN bölgesel teknik kaynağıyla 31 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, satıcı, puan, yorum ve garanti yayımlanmaz.',
      technicalSource:'https://ugreen.com.ru/70594',
      needIds:['vehicle-device-charging'],relatedTools:[...relation.tools],relatedGuides:[...relation.guides],requiredEvidence:[...relation.evidence],
      url:catalog.amazonProductUrl('B07Z1NPFWC')
    }
  ];

  for(const product of products){
    if(!catalog.products.some((current)=>current.id===product.id||current.asin===product.asin))catalog.products.push(product);
  }

  if(typeof catalog.knowledgeGraphSummary==='function'){
    const previousSummary=catalog.knowledgeGraphSummary.bind(catalog);
    catalog.knowledgeGraphSummary=(options={})=>({...previousSummary(options),version:'2026-07-31-run76',generatedAt:'2026-07-31'});
  }
  catalog.__carChargerAffiliateRun54=true;

  if(root&&root.document){
    const id='alo186-affiliate-knowledge-graph';
    const current=root.document.getElementById(id);
    if(current)current.remove();
    const script=root.document.createElement('script');
    script.id=id;
    script.type='application/ld+json';
    script.dataset.generated='alo186-affiliate-knowledge-graph-run76';
    script.textContent=JSON.stringify(catalog.knowledgeGraph());
    root.document.head.appendChild(script);
  }
  return catalog;
});
