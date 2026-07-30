(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186UsbCTrustGrowthRun54=api;
  if(root&&root.document){
    const boot=()=>api.init(root.document,root.localStorage);
    if(root.document.readyState==='loading')root.document.addEventListener('DOMContentLoaded',boot,{once:true});
    else boot();
  }
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const PROFILE_KEY='alo186-usbc-intent-profile-v1';
  const PROFILE_TTL_MS=30*86400000;
  const BOOLEAN_FIELDS=[
    'needPortable','needMultiPortCharging','needHub','needDisplay',
    'needHubEthernet','needHubCardReader','needHub4k60','needHub10Gbps'
  ];
  const VALUE_FIELDS=['useCase','requiredW','cableRole'];

  function unique(values){return [...new Set(values)];}
  function allowedProfile(profile,now=new Date()){
    if(!profile||typeof profile!=='object')return null;
    const expiresAt=new Date(profile.expiresAt);
    if(Number.isNaN(expiresAt.getTime())||expiresAt<=now)return null;
    const values={};
    for(const id of VALUE_FIELDS){
      if(profile.values&&typeof profile.values[id]==='string')values[id]=profile.values[id];
    }
    const flags={};
    for(const id of BOOLEAN_FIELDS)flags[id]=Boolean(profile.flags&&profile.flags[id]);
    return {
      createdAt:String(profile.createdAt||''),
      expiresAt:expiresAt.toISOString(),
      values,
      flags
    };
  }

  function loadProfile(storage,now=new Date()){
    if(!storage)return null;
    try{
      const profile=allowedProfile(JSON.parse(storage.getItem(PROFILE_KEY)),now);
      if(!profile)storage.removeItem(PROFILE_KEY);
      return profile;
    }catch(_error){storage.removeItem(PROFILE_KEY);return null;}
  }

  function collectProfile(document,now=new Date()){
    const values={};
    for(const id of VALUE_FIELDS){
      const field=document.getElementById(id);
      if(field)values[id]=String(field.value||'');
    }
    const flags={};
    for(const id of BOOLEAN_FIELDS){
      const field=document.getElementById(id);
      flags[id]=Boolean(field&&field.checked);
    }
    return {
      createdAt:now.toISOString(),
      expiresAt:new Date(now.getTime()+PROFILE_TTL_MS).toISOString(),
      values,
      flags
    };
  }

  function saveProfile(storage,document,now=new Date()){
    if(!storage)return null;
    const profile=collectProfile(document,now);
    storage.setItem(PROFILE_KEY,JSON.stringify(profile));
    return profile;
  }

  function restoreProfile(document,profile){
    if(!profile)return false;
    for(const [id,value] of Object.entries(profile.values||{})){
      const field=document.getElementById(id);
      if(field&&[...field.options||[]].some((option)=>option.value===value))field.value=value;
    }
    for(const [id,value] of Object.entries(profile.flags||{})){
      const field=document.getElementById(id);
      if(field)field.checked=Boolean(value);
    }
    return true;
  }

  function createNotice(document){
    if(document.getElementById('run54-ranking-note'))return;
    const products=document.getElementById('products');
    if(!products||!products.parentNode)return;
    const note=document.createElement('section');
    note.id='run54-ranking-note';
    note.className='panel';
    note.innerHTML='<h2>Neden ilk seçenek önce gösteriliyor?</h2><p>Ürünler fiyatına veya komisyonuna göre değil; doğrulanmış ihtiyacı karşılayan <strong>en düşük gereksiz güç, port ve özellik farkından</strong> başlayarak sıralanır. İlk kart minimum yeterli başlangıçtır; daha yüksek etiket değeri tek başına daha doğru seçim değildir.</p><p class="muted">Mevcut ürününüz ihtiyacı karşılıyorsa sonuç satın almamadır. Bu sıralama fiyat, stok, puan veya garanti değerlendirmesi değildir.</p>';
    products.parentNode.insertBefore(note,products);
  }

  function decorateProducts(document){
    const products=document.getElementById('products');
    if(!products)return;
    for(const section of products.querySelectorAll('section')){
      const cards=[...section.querySelectorAll('.product-card')];
      if(!cards.length)continue;
      let explanation=section.querySelector('[data-run54-ranking]');
      if(!explanation){
        explanation=document.createElement('p');
        explanation.dataset.run54Ranking='true';
        explanation.className='muted';
        explanation.textContent='Sıralama: minimum yeterli teknik başlangıç → doğrulanmış alternatifler. Daha pahalı veya daha yüksek etiketli ürün varsayımı kullanılmaz.';
        const grid=section.querySelector('.product-grid');
        section.insertBefore(explanation,grid||null);
      }
      cards.forEach((card,index)=>{
        card.dataset.run54Rank=String(index+1);
        const title=card.querySelector('h3');
        if(index===0&&title&&!card.querySelector('[data-run54-minimum]')){
          const tag=document.createElement('span');
          tag.className='tag';
          tag.dataset.run54Minimum='true';
          tag.textContent='Minimum yeterli başlangıç';
          title.insertAdjacentElement('beforebegin',tag);
        }
        const link=card.querySelector('[data-affiliate]');
        if(link){
          link.textContent=index===0
            ? 'Minimum yeterli Amazon satış ortaklığı seçeneğini aç'
            : 'Doğrulanmış Amazon satış ortaklığı alternatifini aç';
          link.setAttribute('aria-label',`${link.textContent}: ${title?title.textContent:'ürün'}`);
        }
      });
    }
  }

  function createProfilePanel(document,storage){
    if(document.getElementById('run54-profile-panel'))return;
    const saved=document.getElementById('saved');
    if(!saved||!saved.parentNode)return;
    const panel=document.createElement('div');
    panel.id='run54-profile-panel';
    panel.className='record';
    panel.innerHTML='<strong>30 günlük teknik niyet profili</strong><p class="muted" data-run54-profile-status>Henüz teknik niyet profili kaydedilmedi.</p><button type="button" class="button" data-run54-clear-profile>Teknik niyet profilini sil</button>';
    saved.parentNode.insertBefore(panel,saved);
    const status=panel.querySelector('[data-run54-profile-status]');
    const profile=loadProfile(storage,new Date());
    if(profile){
      restoreProfile(document,profile);
      status.textContent=`${profile.expiresAt.slice(0,10)} tarihine kadar yalnız kullanım amacı ve teknik ihtiyaçlar geri yüklendi. Kanıt kutuları, tehlike durumu ve mevcut ürün yeterliliği özellikle geri yüklenmedi; yeniden doğrulayın.`;
    }
    panel.querySelector('[data-run54-clear-profile]').addEventListener('click',()=>{
      if(storage)storage.removeItem(PROFILE_KEY);
      status.textContent='Teknik niyet profili bu cihazdan silindi.';
    });
    const save=document.getElementById('save');
    if(save)save.addEventListener('click',()=>{
      const next=saveProfile(storage,document,new Date());
      if(next)status.textContent=`Teknik niyet profili ${next.expiresAt.slice(0,10)} tarihine kadar kaydedildi. Kanıt ve mevcut ürün kontrolleri sonraki ziyarette yeniden istenir.`;
    });
  }

  function init(document,storage){
    const form=document.getElementById('shortlist-form');
    if(!form)return;
    createNotice(document);
    createProfilePanel(document,storage);
    const products=document.getElementById('products');
    if(products&&typeof MutationObserver!=='undefined'){
      const observer=new MutationObserver(()=>decorateProducts(document));
      observer.observe(products,{childList:true,subtree:true});
    }
    decorateProducts(document);
  }

  return {
    PROFILE_KEY,PROFILE_TTL_MS,BOOLEAN_FIELDS:unique(BOOLEAN_FIELDS),VALUE_FIELDS:unique(VALUE_FIELDS),
    allowedProfile,loadProfile,collectProfile,saveProfile,restoreProfile,decorateProducts,init
  };
});
