(function(root){
  'use strict';
  const approvedAffiliateTag='alo186rehber-21';
  const bridgeContract=[
    'manufacturer_verified_search',
    'publicAffiliateEligible',
    'gated-product-candidates',
    'technicalSource',
    'knowledgeGraphSummary'
  ];
  void bridgeContract;

  function augmentUsbCEcosystem(catalog){
    if(!catalog||!Array.isArray(catalog.needs)||!catalog.categoryNeeds||!catalog.categoryRelations)return catalog;
    const additions=[
      {id:'usb-c-hub-connectivity',name:'USB-C hub bağlantı, güç bütçesi ve görüntü uyumu'},
      {id:'usb-c-display-output',name:'USB-C görüntü çıkışı ve DisplayPort Alt Mode uyumu'}
    ];
    for(const need of additions){if(!catalog.needs.some(item=>item.id===need.id))catalog.needs.push(need);}
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
    for(const product of catalog.products||[]){
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
    return catalog;
  }

  if(typeof module==='object'&&module.exports){
    const catalog=augmentUsbCEcosystem(require('../urun-eslestirme/catalog-knowledge-extension.js'));
    if(catalog.affiliateTag!==approvedAffiliateTag){throw new Error('Onaylı affiliate etiketi korunmadı.');}
    if(typeof catalog.publicAffiliateEligible!=='function'||typeof catalog.knowledgeGraphSummary!=='function'){
      throw new Error('Product Knowledge Graph işlevleri eksik.');
    }
    if(!catalog.products.some((product)=>product.status==='manufacturer_verified_search'&&product.technicalSource)){
      throw new Error('Üretici kaynaklı tam model düğümü eksik.');
    }
    module.exports=catalog;
    return;
  }
  if(!root.Alo186ProductCatalog){throw new Error('ALO186 ürün kataloğu önce yüklenmelidir.');}
  if(root.Alo186ProductCatalog.affiliateTag!==approvedAffiliateTag){throw new Error('Onaylı affiliate etiketi korunmadı.');}
  augmentUsbCEcosystem(root.Alo186ProductCatalog);
})(typeof globalThis!=='undefined'?globalThis:this);
