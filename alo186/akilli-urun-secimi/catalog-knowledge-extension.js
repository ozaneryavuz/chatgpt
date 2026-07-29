(function(root){
  'use strict';
  if(typeof module==='object'&&module.exports){
    module.exports=require('../urun-eslestirme/catalog-knowledge-extension.js');
    return;
  }
  if(!root.Alo186ProductCatalog){
    throw new Error('ALO186 ürün kataloğu önce yüklenmelidir.');
  }
})(typeof globalThis!=='undefined'?globalThis:this);
