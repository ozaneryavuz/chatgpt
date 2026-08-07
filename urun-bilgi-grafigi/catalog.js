(function(root){
  'use strict';
  if(typeof module==='object'&&module.exports){
    try{
      module.exports=require('../akilli-urun-secimi/catalog.js');
    }catch(error){
      module.exports=require('../urun-eslestirme/catalog.js');
    }
    return;
  }
  if(!root.Alo186ProductCatalog){
    throw new Error('ALO186 ürün kataloğu önce yüklenmelidir.');
  }
})(typeof globalThis!=='undefined'?globalThis:this);
