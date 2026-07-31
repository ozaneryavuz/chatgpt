(function(root,factory){
  const current=root&&root.Alo186ProductCatalog
    ? root.Alo186ProductCatalog
    : (typeof module==='object'&&module.exports ? require('./catalog-car-charger-run54.js') : null);
  const api=factory(current,root);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186ProductCatalog=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(catalog,root){
  'use strict';

  if(!catalog)throw new Error('ALO186 Product Knowledge Graph yüklenemedi.');
  if(catalog.__batteryContinuityAffiliateRun75)return catalog;
  if(catalog.affiliateTag!=='alo186rehber-21')throw new Error('Onaylı affiliate etiketi korunmadı.');
  if(typeof catalog.knowledgeGraph!=='function'||typeof catalog.publicAffiliateEligible!=='function'){
    throw new Error('Product Knowledge Graph güven işlevleri eksik.');
  }

  const verifiedAt='2026-07-31';
  const categories=[
    {
      id:'nimh_battery_charger',
      name:'AA/AAA NiMH pil şarj cihazı ve başlangıç seti',
      mode:'direct',
      risk:'consumer',
      affiliatePolicy:'verified_direct',
      description:'Yalnız AA/AAA NiMH pil türü, aynı anda şarj edilen hücre sayısı, kanal düzeni, kesme koruması ve güç girişi doğrulanmış tak-çalıştır şarj cihazlarını karşılaştırır. Uyumlu ve çalışan şarj cihazınız varsa yenisini almayın.',
      searchQuery:'AA AAA NiMH pil şarj cihazı USB otomatik kesme'
    },
    {
      id:'rechargeable_nimh_battery',
      name:'AA/AAA şarj edilebilir NiMH pil',
      mode:'direct',
      risk:'consumer',
      affiliatePolicy:'verified_direct',
      description:'Pil boyutu, NiMH kimyası, 1,2 V nominal gerilim, kapasite, paket adedi ve cihaz üreticisinin şarjlı pil izni birlikte doğrulanır. Düşük tüketimli cihazda mevcut piller yeterliyse yeni pil almayın.',
      searchQuery:'AA AAA NiMH şarj edilebilir pil 1.2V'
    }
  ];
  for(const category of categories){
    if(!catalog.categories.some((item)=>item.id===category.id))catalog.categories.push(category);
  }

  const need={id:'reusable-battery-continuity',name:'Kumanda, oyuncak, kamera ve günlük cihazlarda tekrar kullanılabilir AA/AAA enerji'};
  if(Array.isArray(catalog.needs)&&!catalog.needs.some((item)=>item.id===need.id))catalog.needs.push(need);
  if(catalog.categoryNeeds){
    catalog.categoryNeeds.nimh_battery_charger=[need.id];
    catalog.categoryNeeds.rechargeable_nimh_battery=[need.id];
  }
  if(catalog.categoryRelations){
    catalog.categoryRelations.nimh_battery_charger={
      tools:['/akilli-urun-secimi/'],
      guides:['/amazon-elektrik-urunleri/'],
      evidence:['yalnız AA/AAA NiMH hücre desteği','iki veya dört hücre kanal düzeni','otomatik kesme ve hata algılama','güç girişi ile paket içeriğinin tam model eşleşmesi']
    };
    catalog.categoryRelations.rechargeable_nimh_battery={
      tools:['/akilli-urun-secimi/'],
      guides:['/amazon-elektrik-urunleri/'],
      evidence:['cihazın AA veya AAA boyut gereği','NiMH ve 1,2 V uyumu','kapasite ve paket adedi','uyumlu NiMH şarj cihazının mevcut olması']
    };
  }
  const relation=(category)=>catalog.categoryRelations&&catalog.categoryRelations[category]
    ? catalog.categoryRelations[category]
    : {tools:[],guides:[],evidence:[]};

  const products=[
    {
      id:'duracell-cef14-aa-aaa-set',category:'nimh_battery_charger',asin:'B07BFDVNSJ',mpn:'CEF14',
      name:'Duracell CEF14 AA/AAA NiMH Şarj Cihazı ve 4 Pil Seti',brand:'Duracell',
      status:'verified_listing',verifiedAt,
      attributes:{batteryChemistry:'NiMH',supportedSizes:'AA/AAA',chargeSlots:4,chargePairs:'2 veya 4 pil',chargingPowerMw:1000,chargeTimeHours:'4–8',chargeLevelPercent:'yaklaşık 85–90',ledStatus:true,autoShutoff:true,packageAaCount:2,packageAaaCount:2},
      strengths:[
        'Kullanıcı ihtiyacı: AA ve AAA NiMH kullanan birden fazla günlük cihaz için şarj cihazı ve başlangıç pili edinme',
        'İki veya dört AA/AAA NiMH pili şarj edebilme',
        'LED durum göstergesi ve otomatik kapanma',
        'Satış ortaklığı açıklaması: ürün bağlantısı Amazon satış ortaklığı bağlantısıdır; nitelikli satın alımdan komisyon kazanılabilir'
      ],
      limits:[
        'Satın almama koşulu: çalışan ve AA/AAA NiMH ile uyumlu bir şarj cihazınız varsa yalnız gereken pil boyutunu değerlendirin; yeni set almayın',
        'Piller çiftler hâlinde şarj edilir; tek hücre şarjı için uygun kabul edilmemelidir',
        '4–8 saat ve yaklaşık yüzde 85–90 değerleri pil kapasitesi ve koşula göre değişen üretici sınıfıdır',
        'Alkalin, lityum birincil veya hasarlı piller şarj edilmemelidir'
      ],
      sourceNote:'Amazon Türkiye ASIN B07BFDVNSJ ile CEF14 set eşleşmesi; AA/AAA NiMH, iki veya dört pil, 1000 mW şarj gücü, LED ve otomatik kapanma alanları Duracell resmî teknik kaynağıyla 31 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, satıcı, puan, yorum ve garanti yayımlanmaz.',
      technicalSource:'https://duracell.com/products/cef14',
      needIds:[need.id],relatedTools:[...relation('nimh_battery_charger').tools],relatedGuides:[...relation('nimh_battery_charger').guides],requiredEvidence:[...relation('nimh_battery_charger').evidence],
      url:catalog.amazonProductUrl('B07BFDVNSJ')
    },
    {
      id:'gp-recyko-e411-2700-aa-set',category:'nimh_battery_charger',asin:'B09DPKNDBX',mpn:'E411-270AAHCCS-2CR1',
      name:'GP ReCyko E411 USB Şarj Cihazı ve 4 Adet 2700 mAh AA Pil Seti',brand:'GP Batteries',
      status:'verified_listing',verifiedAt,
      attributes:{batteryChemistry:'NiMH',supportedSizes:'AA/AAA',chargeSlots:4,chargeChannels:2,chargePairs:'2 veya 4 pil',input:'DC 5 V / 1 A',output:'DC 2,8 V; 0,3 A x 2',usbPowered:true,ledCount:2,badBatteryDetection:true,alkalineBatteryDetection:true,deltaVCutoff:true,timerCutoff:true,packageAaCount:4,packageAaCapacityMah:2700},
      strengths:[
        'Kullanıcı ihtiyacı: USB güç kaynağıyla dört AA NiMH pili dönüşümlü kullanan oyuncak, kamera veya kumanda grubunu besleme',
        'AA ve AAA NiMH için dört yuva ve iki şarj kanalı',
        'Hatalı/alkalin pil algılama, eksi delta V ve zamanlayıcı kesmesi',
        'Satış ortaklığı açıklaması: ürün bağlantısı Amazon satış ortaklığı bağlantısıdır; nitelikli satın alımdan komisyon kazanılabilir'
      ],
      limits:[
        'Satın almama koşulu: mevcut USB NiMH şarj cihazınız güvenli çalışıyor ve gereken dört pili karşılıyorsa yeni set almayın',
        'İki kanallı yapı nedeniyle piller iki veya dört adet ve uyumlu çiftler hâlinde şarj edilmelidir',
        'Amazon paketindeki 2700 mAh AA pil adedi ve tam paket kodu satın alma sayfasında yeniden doğrulanmalıdır',
        'USB güç adaptörü ve kablo paket içeriği ayrı kontrol edilmelidir'
      ],
      sourceNote:'Amazon Türkiye ASIN B09DPKNDBX ile E411 ve dört adet 2700 mAh AA set eşleşmesi; E411 için dört yuva, iki kanal, 5 V/1 A USB giriş, 0,3 A x 2 çıkış, LED, hatalı/alkalin pil algılama ve kesme korumaları GP Batteries resmî teknik kaynağıyla 31 Temmuz 2026 tarihinde doğrulandı. Paket kapasitesi Amazon kaydından gelir ve sayfada yeniden kontrol edilir. Fiyat, stok, satıcı, puan, yorum ve garanti yayımlanmaz.',
      technicalSource:'https://intls.gpbatteries.com/products/gp-recyko-4-slot-e411-usb-charger-w-4s-2100mah-aa-batteries',
      needIds:[need.id],relatedTools:[...relation('nimh_battery_charger').tools],relatedGuides:[...relation('nimh_battery_charger').guides],requiredEvidence:[...relation('nimh_battery_charger').evidence],
      url:catalog.amazonProductUrl('B09DPKNDBX')
    },
    {
      id:'duracell-aaa-750-2pack',category:'rechargeable_nimh_battery',asin:'B00DDEVU36',mpn:'5000394107939',
      name:'Duracell Şarj Edilebilir AAA 750 mAh NiMH Pil 2’li Paket',brand:'Duracell',
      status:'verified_listing',verifiedAt,
      attributes:{batteryChemistry:'NiMH',size:'AAA',iecDesignation:'HR03',nominalVoltageV:1.2,capacityMah:750,packageCount:2,preCharged:true,rechargeCyclesClaim:1000,diameterMm:10.5,lengthMm:44.5},
      strengths:[
        'Kullanıcı ihtiyacı: AAA pil kullanan kumanda, kablosuz fare, oyuncak veya benzeri cihazlarda tekrar kullanılabilir enerji',
        'AAA / HR03 boyut, 1,2 V NiMH ve 750 mAh kapasite',
        'Önceden şarjlı iki hücrelik paket',
        'Satış ortaklığı açıklaması: ürün bağlantısı Amazon satış ortaklığı bağlantısıdır; nitelikli satın alımdan komisyon kazanılabilir'
      ],
      limits:[
        'Satın almama koşulu: elinizdeki AAA NiMH piller kapasite ve çalışma süresi ihtiyacını karşılıyorsa yenisini almayın',
        'Cihaz üreticisi yalnız 1,5 V alkalin veya farklı kimya istiyorsa NiMH pil kullanmayın',
        'Yalnız NiMH uyumlu şarj cihazıyla, eş yaş ve eş kapasitedeki hücreler birlikte kullanılmalıdır',
        '1000 şarj döngüsü kullanım ve şarj koşullarına bağlı üretici sınıfıdır; gerçek ömür garantisi olarak yorumlanmamalıdır'
      ],
      sourceNote:'Amazon Türkiye ASIN B00DDEVU36 ile 5000394107939 ürün kodlu iki adet AAA 750 mAh NiMH paket eşleşmesi; AAA/HR03, 1,2 V, 750 mAh ve önceden şarjlı yapı Duracell resmî teknik kaynağıyla 31 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, satıcı, puan, yorum ve garanti yayımlanmaz.',
      technicalSource:'https://duracell.com/techlibrary/regulatory',
      needIds:[need.id],relatedTools:[...relation('rechargeable_nimh_battery').tools],relatedGuides:[...relation('rechargeable_nimh_battery').guides],requiredEvidence:[...relation('rechargeable_nimh_battery').evidence],
      url:catalog.amazonProductUrl('B00DDEVU36')
    }
  ];

  for(const product of products){
    if(!catalog.products.some((current)=>current.id===product.id||current.asin===product.asin))catalog.products.push(product);
  }

  const previousKnowledgeGraph=catalog.knowledgeGraph.bind(catalog);
  catalog.knowledgeGraph=(options={})=>{
    const payload=previousKnowledgeGraph(options);
    const graph=Array.isArray(payload&&payload['@graph'])?payload['@graph']:[];
    const listBase='https://www.alo186.com/urun-bilgi-grafigi/';
    const itemLists=categories.map((category)=>{
      const eligible=products.filter((product)=>product.category===category.id&&catalog.publicAffiliateEligible(product,options));
      const itemListElement=eligible.map((product,index)=>{
        const node=graph.find((candidate)=>candidate&&candidate['@type']==='Product'&&candidate.sku===product.id);
        return node?{'@type':'ListItem',position:index+1,item:{'@id':node['@id']}}:null;
      }).filter(Boolean);
      if(!itemListElement.length)return null;
      return {
        '@id':`${listBase}#itemlist-${category.id}`,
        '@type':'ItemList',
        name:`${category.name} — doğrulanmış ürünler`,
        description:'Fiyat, stok, satıcı, puan, yorum, garanti veya Offer yayımlamadan teknik tazelik ve güven kapılarından geçen Amazon satış ortaklığı ürünleri.',
        numberOfItems:itemListElement.length,
        itemListOrder:'https://schema.org/ItemListOrderAscending',
        itemListElement
      };
    }).filter(Boolean);
    const listIds=new Set(itemLists.map((item)=>item['@id']));
    payload['@graph']=[...graph.filter((node)=>!listIds.has(node&&node['@id'])),...itemLists];
    return payload;
  };

  if(typeof catalog.knowledgeGraphSummary==='function'){
    const previousSummary=catalog.knowledgeGraphSummary.bind(catalog);
    catalog.knowledgeGraphSummary=(options={})=>({...previousSummary(options),version:'2026-07-31-run75',generatedAt:verifiedAt});
  }
  catalog.__batteryContinuityAffiliateRun75=true;

  if(root&&root.document){
    const id='alo186-affiliate-knowledge-graph';
    const current=root.document.getElementById(id);
    if(current)current.remove();
    const script=root.document.createElement('script');
    script.id=id;
    script.type='application/ld+json';
    script.dataset.generated='alo186-affiliate-knowledge-graph-run75';
    script.textContent=JSON.stringify(catalog.knowledgeGraph());
    root.document.head.appendChild(script);
  }
  return catalog;
});
