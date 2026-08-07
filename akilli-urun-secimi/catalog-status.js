(()=>{
  'use strict';
  const catalog=globalThis.Alo186ProductCatalog;
  const category=document.body?.dataset?.category;
  const target=document.querySelector('[data-category-status]');
  if(!target||!catalog||!category)return;
  const entry=typeof catalog.getCategory==='function'?catalog.getCategory(category):null;
  if(!entry){target.hidden=true;return;}
  const policy=entry.affiliatePolicy||entry.mode||'guide';
  const labels={
    after_tool:'Ürün yolu yalnız ücretsiz teknik uygunluk kontrolünden sonra açılır.',
    professional_only:'Bu kategori profesyonel değerlendirme gerektirir; doğrudan mağaza bağlantısı açılmaz.',
    guide:'Önce teknik rehberi ve satın almama seçeneğini değerlendirin.'
  };
  target.textContent=labels[policy]||labels.guide;
})();
