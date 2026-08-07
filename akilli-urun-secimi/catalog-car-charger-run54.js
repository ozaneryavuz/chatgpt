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
    }
  ];

  for(const product of products){
    if(!catalog.products.some((current)=>current.id===product.id||current.asin===product.asin))catalog.products.push(product);
  }

  if(typeof catalog.knowledgeGraphSummary==='function'){
    const previousSummary=catalog.knowledgeGraphSummary.bind(catalog);
    catalog.knowledgeGraphSummary=(options={})=>({...previousSummary(options),version:'2026-07-30-run54',generatedAt:'2026-07-30'});
  }
  catalog.__carChargerAffiliateRun54=true;

  if(root&&root.document){
    const id='alo186-affiliate-knowledge-graph';
    const current=root.document.getElementById(id);
    if(current)current.remove();
    const script=root.document.createElement('script');
    script.id=id;
    script.type='application/ld+json';
    script.dataset.generated='alo186-affiliate-knowledge-graph-run54';
    script.textContent=JSON.stringify(catalog.knowledgeGraph());
    root.document.head.appendChild(script);
  }
  return catalog;
});
