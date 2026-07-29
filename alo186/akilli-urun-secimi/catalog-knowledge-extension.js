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
  if(typeof module==='object'&&module.exports){
    const catalog=require('../urun-eslestirme/catalog-knowledge-extension.js');
    if(catalog.affiliateTag!==approvedAffiliateTag){
      throw new Error('Onaylı affiliate etiketi korunmadı.');
    }
    if(typeof catalog.publicAffiliateEligible!=='function'||typeof catalog.knowledgeGraphSummary!=='function'){
      throw new Error('Product Knowledge Graph işlevleri eksik.');
    }
    if(!catalog.products.some((product)=>product.status==='manufacturer_verified_search'&&product.technicalSource)){
      throw new Error('Üretici kaynaklı tam model düğümü eksik.');
    }
    module.exports=catalog;
    return;
  }
  if(!root.Alo186ProductCatalog){
    throw new Error('ALO186 ürün kataloğu önce yüklenmelidir.');
  }
  if(root.Alo186ProductCatalog.affiliateTag!==approvedAffiliateTag){
    throw new Error('Onaylı affiliate etiketi korunmadı.');
  }
})(typeof globalThis!=='undefined'?globalThis:this);
