(function(root){
  'use strict';
  const approvedAffiliateTag='alo186rehber-21';
  const bridgeContract=[
    'manufacturer_verified_search',
    'publicAffiliateEligible',
    'gated-product-candidates',
    'technicalSource',
    'knowledgeGraphSummary',
    'connector-specific-display-relations'
  ];
  void bridgeContract;

  function augmentUsbCEcosystem(catalog){
    if(!catalog||!Array.isArray(catalog.needs)||!catalog.categoryNeeds||!catalog.categoryRelations)return catalog;
    const additions=[
      {id:'usb-c-hub-connectivity',name:'USB-C hub bağlantı, güç bütçesi ve görüntü uyumu'},
      {id:'usb-c-display-output',name:'USB-C görüntü çıkışı ve DisplayPort Alt Mode uyumu'},
      {id:'display-link-compatibility',name:'HDMI ve DisplayPort bağlantı, sürüm ve görüntü modu uyumu'}
    ];
    for(const need of additions){if(!catalog.needs.some(item=>item.id===need.id))catalog.needs.push(need);}

    const hubRelation={
      needs:['usb-c-hub-connectivity'],
      tools:['/hesaplama/usb-c-urun-kabul-testi/'],
      guides:['/urun-bilgi-grafigi/usb-c-ekosistemi/'],
      evidence:['host USB-C veri/görüntü desteği','PD geçiş gücü ve haricî adaptör','port türü ve toplam güç bütçesi','gerekli veri ve görüntü işlevi']
    };
    const usbDisplayRelation={
      needs:['usb-c-display-output'],
      tools:['/hesaplama/usb-c-urun-kabul-testi/'],
      guides:['/urun-bilgi-grafigi/usb-c-ekosistemi/'],
      evidence:['host DisplayPort Alt Mode veya Thunderbolt desteği','hedef çözünürlük ve yenileme hızı','kablo yönü ve uzunluğu','görüntü zinciri uyumluluğu']
    };
    const nativeDisplayRelation={
      needs:['display-link-compatibility'],
      tools:[],
      guides:['/urun-bilgi-grafigi/'],
      evidence:['kaynak ve hedef konektör','HDMI veya DisplayPort sürümü','hedef çözünürlük ve yenileme hızı','kablo yönü ve uzunluğu']
    };

    catalog.categoryNeeds.usb_c_hub=[...hubRelation.needs];
    catalog.categoryNeeds.display_cable=[...usbDisplayRelation.needs,...nativeDisplayRelation.needs];
    catalog.categoryRelations.usb_c_hub={tools:[...hubRelation.tools],guides:[...hubRelation.guides],evidence:[...hubRelation.evidence]};
    catalog.categoryRelations.display_cable={
      tools:[],
      guides:['/urun-bilgi-grafigi/'],
      evidence:['kaynak ve hedef konektör','HDMI veya DisplayPort sürümü','hedef çözünürlük ve yenileme hızı','kablo yönü ve uzunluğu']
    };

    for(const product of catalog.products||[]){
      if(product.category==='usb_c_hub'){
        if(!Array.isArray(product.needIds)||!product.needIds.length)product.needIds=[...hubRelation.needs];
        if(!Array.isArray(product.relatedTools)||!product.relatedTools.length)product.relatedTools=[...hubRelation.tools];
        if(!Array.isArray(product.relatedGuides)||!product.relatedGuides.length)product.relatedGuides=[...hubRelation.guides];
        if(!Array.isArray(product.requiredEvidence)||!product.requiredEvidence.length)product.requiredEvidence=[...hubRelation.evidence];
      }
      if(product.category==='display_cable'){
        const connectorA=String(product.attributes&&product.attributes.connectorA||'').trim().toUpperCase();
        const relation=connectorA==='USB-C'?usbDisplayRelation:nativeDisplayRelation;
        product.needIds=[...relation.needs];
        product.relatedTools=[...relation.tools];
        product.relatedGuides=[...relation.guides];
        product.requiredEvidence=[...relation.evidence];
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
