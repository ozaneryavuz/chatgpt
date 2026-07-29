(function(root){
  'use strict';
  const approvedAffiliateTag='alo186rehber-21';
  if(typeof module==='object'&&module.exports){
    const catalog=require('../urun-eslestirme/catalog-knowledge-extension.js');
    if(catalog.affiliateTag!==approvedAffiliateTag){
      throw new Error('Onaylı affiliate etiketi korunmadı.');
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
