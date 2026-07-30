(function(root,factory){
  const current=root&&root.Alo186ProductCatalog
    ? root.Alo186ProductCatalog
    : (typeof module==='object'&&module.exports ? require('./catalog-sales-extension.js') : null);
  const api=factory(current,root);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186ProductCatalog=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(catalog,root){
  'use strict';

  if(!catalog)throw new Error('ALO186 ürün kataloğu yüklenemedi.');
  if(catalog.__qualifiedCommerceRun53)return catalog;
  if(catalog.affiliateTag!=='alo186rehber-21')throw new Error('Affiliate etiketi korunmadı.');
  if(typeof catalog.amazonProductUrl!=='function'||typeof catalog.publicAffiliateEligible!=='function'){
    throw new Error('Katalog güven işlevleri eksik.');
  }

  const product={
    id:'ugreen-nexode-140w-90322',
    category:'usb_c_charger',
    asin:'B0B127GW4D',
    mpn:'90322',
    name:'UGREEN Nexode 90322 140 W PD 3.1 GaN Şarj Cihazı',
    brand:'UGREEN',
    status:'verified_listing',
    verifiedAt:'2026-07-30',
    attributes:{
      maxOutputW:140,
      maxSingleDeviceW:140,
      totalOutputW:140,
      usbCPorts:2,
      usbAPorts:1,
      totalPorts:3,
      multiPort:true,
      gan:true,
      pd31:true,
      pps:true,
      samsungSfc2:true,
      includedCableMaxW:240
    },
    strengths:[
      'Tek USB-C portta 140 W PD 3.1 sınıfı',
      'İki USB-C ve bir USB-A port',
      'PPS ve Samsung 45 W hızlı şarj profili',
      '240 W sınıfı USB-C kablo pakete dâhil'
    ],
    limits:[
      '140 W yalnız uyumlu PD 3.1 cihaz ve 5 A E-marker kabloyla elde edilir',
      'Birden fazla cihaz bağlandığında güç portlar arasında paylaşılır',
      'Paket içeriği ve bölge fişi Amazon ürün sayfasında yeniden doğrulanmalıdır'
    ],
    sourceNote:'ASIN B0B127GW4D ile UGREEN 90322 model eşleşmesi; 140 W tek port/Toplam sınıfı, iki USB-C + bir USB-A, PD 3.1, PPS ve 240 W kablo bilgileri UGREEN resmî teknik sayfaları ve Amazon Türkiye ürün kaydıyla 30 Temmuz 2026 tarihinde doğrulandı. Fiyat, stok, puan, satıcı ve garanti yayımlanmaz.',
    technicalSource:'https://eu.ugreen.com/products/ugreen-nexode-140w-usb-c-wall-charger',
    needIds:['usb-c-fast-charging'],
    relatedTools:['/hesaplama/usb-c-sarj-zinciri-uygunluk/','/hesaplama/usb-c-set-kisa-listesi/','/hesaplama/usb-c-urun-kabul-testi/'],
    relatedGuides:['/urun-bilgi-grafigi/usb-c-ekosistemi/'],
    requiredEvidence:['cihazın kabul ettiği PD 3.1 güç profili','tek port ve çoklu port güç dağılımı','5 A E-marker kablo','Amazon’daki 90322/B0B127GW4D eşleşmesi'],
    url:catalog.amazonProductUrl('B0B127GW4D')
  };

  if(!catalog.products.some((item)=>item.id===product.id||item.asin===product.asin))catalog.products.push(product);

  const previousSummary=typeof catalog.knowledgeGraphSummary==='function'
    ? catalog.knowledgeGraphSummary.bind(catalog)
    : null;
  if(previousSummary){
    catalog.knowledgeGraphSummary=(options={})=>({
      ...previousSummary(options),
      version:'2026-07-30-run53',
      generatedAt:'2026-07-30',
      qualifiedCommerce:{
        verifiedChargerAdded:product.id,
        singleDeviceW:140,
        directAffiliateLinksAdded:1,
        commercialFieldsExcluded:['price','stock','rating','review','seller','delivery','warranty','availability']
      }
    });
  }

  catalog.__qualifiedCommerceRun53=true;

  if(root&&root.document&&typeof catalog.knowledgeGraph==='function'){
    const id='alo186-affiliate-knowledge-graph';
    const current=root.document.getElementById(id);
    if(current)current.remove();
    const script=root.document.createElement('script');
    script.id=id;
    script.type='application/ld+json';
    script.dataset.generated='alo186-affiliate-knowledge-graph-run53';
    script.textContent=JSON.stringify(catalog.knowledgeGraph());
    root.document.head.appendChild(script);
  }

  return catalog;
});
