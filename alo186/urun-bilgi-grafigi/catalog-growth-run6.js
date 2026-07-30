(function(root,factory){
  const current=root&&root.Alo186ProductCatalog
    ? root.Alo186ProductCatalog
    : (typeof module==='object'&&module.exports ? require('../urun-eslestirme/catalog-growth-run6.js') : null);
  const api=factory(current);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186ProductCatalog=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(catalog){
  'use strict';
  if(!catalog)throw new Error('ALO186 run6 Product Knowledge Graph yüklenemedi.');
  return catalog;
});
