(function(root,factory){
  const catalog=root&&root.Alo186ProductCatalog
    ? root.Alo186ProductCatalog
    : (typeof module==='object'&&module.exports ? require('../../urun-eslestirme/catalog-sales-extension.js') : null);
  const api=factory(catalog);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186UsbCShortlist=api;
  if(root&&root.document)api.init(root.document,root.localStorage);
})(typeof globalThis!=='undefined'?globalThis:this,function(catalog){
  'use strict';
  if(!catalog)throw new Error('ALO186 ürün kataloğu yüklenemedi.');

  const STORAGE_KEY='alo186-usb-c-shortlist-v1';
  const TTL_MS=30*86400000;
  const LIMIT=6;
  const LABELS={
    usb_c_charger:'USB-C PD/PPS şarj cihazı',
    usb_c_cable:'USB-C güç ve veri kablosu',
    powerbank:'USB-C powerbank',
    usb_c_hub:'USB-C hub / dock',
    display_cable:'USB-C görüntü kablosu'
  };

  function unique(values){return [...new Set(values)];}
  function requiredCategories(input={}){
    const categories=['usb_c_charger','usb_c_cable'];
    if(input.useCase==='travel'||input.needPortable)categories.push('powerbank');
    if(input.useCase==='desk'||input.needHub)categories.push('usb_c_hub');
    if(input.useCase==='desk'||input.needDisplay)categories.push('display_cable');
    return unique(categories);
  }
  function productPower(product){
    const a=product&&product.attributes||{};
    if(product.category==='usb_c_cable')return Number(a.maxPowerW||0);
    if(product.category==='powerbank')return Number(a.singleDeviceMaxW||a.maxOutputW||0);
    if(product.category==='usb_c_charger')return Number(a.singleDeviceMaxW||a.maxOutputW||0);
    return Number(a.maxPowerW||a.pdPassThroughW||a.passThroughW||0);
  }
  function publicEligible(product,now){
    return Boolean(product&&product.status==='verified_listing'&&catalog.publicAffiliateEligible(product,{now}));
  }
  function eligibleProducts(category,input={},now=new Date()){
    const minPower=Number(input.requiredW||0);
    return catalog.products
      .filter((product)=>product.category===category&&publicEligible(product,now))
      .filter((product)=>['usb_c_hub','display_cable'].includes(category)||productPower(product)>=minPower)
      .sort((a,b)=>{
        const ap=productPower(a)||9999;
        const bp=productPower(b)||9999;
        return Math.abs(ap-minPower)-Math.abs(bp-minPower)||a.name.localeCompare(b.name,'tr');
      })
      .slice(0,3);
  }
  function evaluate(input={},now=new Date()){
    const categories=requiredCategories(input);
    if(input.hazard){
      return {status:'hazard',categories,missing:[],products:{},message:'Isınma, erime, koku, şişme, kıvılcım veya hasarlı kablo seçildi. Ticari rota kapalıdır.'};
    }
    if(!input.devicePowerKnown){
      return {status:'evidence_required',categories,missing:categories,products:{},message:'Cihazın kabul ettiği USB-C güç ve protokol bilinmeden ürün kısa listesi açılmaz.'};
    }
    if(categories.includes('usb_c_hub')&&!input.hostDataKnown){
      return {status:'evidence_required',categories,missing:['usb_c_hub'],products:{},message:'Hub için kaynak USB-C portunun veri yeteneği doğrulanmalıdır.'};
    }
    if(categories.includes('display_cable')&&!input.hostVideoKnown){
      return {status:'evidence_required',categories,missing:['display_cable'],products:{},message:'Görüntü ürünü için kaynak portun DisplayPort Alt Mode veya Thunderbolt desteği doğrulanmalıdır.'};
    }
    const existing=input.existing||{};
    const missing=categories.filter((category)=>existing[category]!==true);
    if(!missing.length){
      return {status:'no_buy',categories,missing,products:{},message:'Mevcut şarj zinciri ihtiyacı karşılıyor. Yeni ürün satın almak gerekli değildir.'};
    }
    const products=Object.fromEntries(missing.map((category)=>[category,eligibleProducts(category,input,now)]));
    return {status:'qualified',categories,missing,products,message:'Yalnız eksik bileşenler için doğrulanmış teknik kısa liste oluşturuldu.'};
  }

  function cleanStored(value,now=new Date()){
    if(!value||typeof value!=='object'||!Array.isArray(value.ids))return null;
    const expiresAt=new Date(value.expiresAt);
    if(Number.isNaN(expiresAt.getTime())||expiresAt<=now)return null;
    return {...value,ids:unique(value.ids.map(String)).slice(0,LIMIT)};
  }
  function loadShortlist(storage,now=new Date()){
    if(!storage)return null;
    try{
      const value=cleanStored(JSON.parse(storage.getItem(STORAGE_KEY)),now);
      if(!value)storage.removeItem(STORAGE_KEY);
      return value;
    }catch(_error){storage.removeItem(STORAGE_KEY);return null;}
  }
  function saveShortlist(storage,ids,now=new Date()){
    if(!storage)throw new Error('Tarayıcı depolaması kullanılamıyor.');
    const cleanIds=unique((ids||[]).map(String)).slice(0,LIMIT);
    const payload={createdAt:now.toISOString(),expiresAt:new Date(now.getTime()+TTL_MS).toISOString(),ids:cleanIds};
    storage.setItem(STORAGE_KEY,JSON.stringify(payload));
    return payload;
  }
  function createIcs(payload,now=new Date()){
    const date=new Date(now.getTime()+30*86400000).toISOString().slice(0,10).replaceAll('-','');
    const names=(payload&&payload.ids||[]).map((id)=>catalog.products.find((product)=>product.id===id)).filter(Boolean).map((product)=>product.name).join(', ');
    return ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//USB-C Kisa Liste//TR','BEGIN:VEVENT',`UID:alo186-usbc-${now.getTime()}@alo186.com`,`DTSTART;VALUE=DATE:${date}`,'SUMMARY:ALO186 USB-C uyumluluk kısa listesini yeniden kontrol et',`DESCRIPTION:${names||'USB-C şarj zinciri'} — cihaz gücü, kablo etiketi ve port yeteneklerini yeniden doğrulayın. Mevcut sistem yeterliyse yeni ürün almayın.`,'URL:https://alo186.com/hesaplama/usb-c-set-kisa-listesi/','END:VEVENT','END:VCALENDAR'].join('\r\n');
  }
  function escapeHtml(value){return String(value??'').replace(/[&<>'"]/g,(char)=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));}
  function facts(product){
    const a=product.attributes||{};
    const list=[];
    const power=productPower(product);
    if(power)list.push(`${power} W sınıfı`);
    if(a.capacityMah)list.push(`${Number(a.capacityMah).toLocaleString('tr-TR')} mAh`);
    if(a.lengthM)list.push(`${a.lengthM} m`);
    if(a.usbCPorts)list.push(`${a.usbCPorts} USB-C port`);
    if(a.dataGbps)list.push(`${a.dataGbps} Gbps veri`);
    if(a.displayResolution)list.push(String(a.displayResolution));
    return list.slice(0,4);
  }

  function init(document,storage){
    const form=document.getElementById('shortlist-form');
    if(!form)return;
    const result=document.getElementById('result');
    const products=document.getElementById('products');
    const gate=document.getElementById('gate');
    const saved=document.getElementById('saved');
    let lastDecision=null;

    function collect(){
      const useCase=document.getElementById('useCase').value;
      return {
        useCase,
        requiredW:Number(document.getElementById('requiredW').value),
        needPortable:document.getElementById('needPortable').checked,
        needHub:document.getElementById('needHub').checked,
        needDisplay:document.getElementById('needDisplay').checked,
        devicePowerKnown:document.getElementById('devicePowerKnown').checked,
        hostDataKnown:document.getElementById('hostDataKnown').checked,
        hostVideoKnown:document.getElementById('hostVideoKnown').checked,
        hazard:document.getElementById('hazard').checked,
        existing:Object.fromEntries(Object.keys(LABELS).map((key)=>[key,document.getElementById(`existing-${key}`).checked]))
      };
    }
    function gateReady(){return ['actualMissing','compatibilityChecked','affiliateAccepted'].every((id)=>document.getElementById(id).checked);}
    function syncGate(){
      const ready=gateReady();
      document.querySelectorAll('[data-affiliate]').forEach((link)=>{link.setAttribute('aria-disabled',ready?'false':'true');link.tabIndex=ready?0:-1;});
    }
    function productCard(product,category){
      const factsHtml=facts(product).map((item)=>`<li>${escapeHtml(item)}</li>`).join('');
      const strengths=(product.strengths||[]).slice(0,2).map((item)=>`<li>${escapeHtml(item)}</li>`).join('');
      const limits=(product.limits||[]).slice(0,2).map((item)=>`<li>${escapeHtml(item)}</li>`).join('');
      return `<article class="card product-card"><span class="tag">${escapeHtml(LABELS[category])}</span><h3>${escapeHtml(product.name)}</h3><p class="muted">Teknik doğrulama: ${escapeHtml(product.verifiedAt)}</p><ul class="facts">${factsHtml}${strengths}</ul><p><strong>Sınırlar</strong></p><ul class="facts">${limits}</ul><label class="check"><input type="checkbox" data-pick="${escapeHtml(product.id)}"><span>Teknik kısa listeme ekle</span></label><a class="button primary" data-affiliate aria-disabled="true" rel="sponsored nofollow noopener" target="_blank" href="${escapeHtml(product.url)}">Amazon satış ortaklığı seçeneğini aç</a></article>`;
    }
    function render(decision){
      lastDecision=decision;
      const klass=decision.status==='no_buy'?'ok':decision.status==='hazard'?'bad':'warn';
      result.classList.remove('hidden');
      result.innerHTML=`<h2>Sonuç</h2><div class="status ${klass}"><strong>${escapeHtml(decision.message)}</strong></div>${decision.missing.length?`<p>Eksik sınıflar: ${decision.missing.map((key)=>escapeHtml(LABELS[key])).join(', ')}</p>`:''}`;
      if(decision.status!=='qualified'){
        products.innerHTML='';gate.classList.add('hidden');return;
      }
      products.innerHTML=decision.missing.map((category)=>{
        const matches=decision.products[category]||[];
        if(!matches.length)return `<section><h2>${escapeHtml(LABELS[category])}</h2><div class="status warn">Taze ve doğrudan doğrulanmış ürün bulunmadı. <a href="../../akilli-urun-secimi/?kategori=${encodeURIComponent(category)}">Teknik kategori yolunu açın</a>.</div></section>`;
        return `<section><h2>${escapeHtml(LABELS[category])}</h2><div class="grid product-grid">${matches.map((product)=>productCard(product,category)).join('')}</div></section>`;
      }).join('');
      gate.classList.remove('hidden');
      syncGate();
    }
    function renderSaved(){
      const payload=loadShortlist(storage,new Date());
      if(!payload){saved.innerHTML='<p class="muted">Henüz saklanmış kısa liste yok.</p>';return;}
      const records=payload.ids.map((id)=>catalog.products.find((product)=>product.id===id)).filter(Boolean);
      saved.innerHTML=`<p class="muted">${escapeHtml(payload.expiresAt.slice(0,10))} tarihine kadar cihazınızda tutulur.</p>${records.map((product)=>`<div class="record"><strong>${escapeHtml(product.name)}</strong><br><small>${escapeHtml(LABELS[product.category]||product.category)}</small></div>`).join('')||'<p>Kayıtlı ürün kalmadı.</p>'}`;
    }
    form.addEventListener('submit',(event)=>{event.preventDefault();render(evaluate(collect(),new Date()));result.focus();});
    gate.addEventListener('change',syncGate);
    document.addEventListener('click',(event)=>{const link=event.target.closest('[data-affiliate]');if(link&&link.getAttribute('aria-disabled')!=='false')event.preventDefault();});
    document.getElementById('save').addEventListener('click',()=>{
      if(!lastDecision||lastDecision.status!=='qualified')return;
      const ids=[...document.querySelectorAll('[data-pick]:checked')].map((input)=>input.dataset.pick);
      saveShortlist(storage,ids,new Date());renderSaved();
    });
    document.getElementById('export').addEventListener('click',()=>{
      const payload=loadShortlist(storage,new Date());if(!payload)return;
      const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download='alo186-usb-c-kisa-liste.json';link.click();URL.revokeObjectURL(link.href);
    });
    document.getElementById('calendar').addEventListener('click',()=>{
      const payload=loadShortlist(storage,new Date());if(!payload)return;
      const blob=new Blob([createIcs(payload,new Date())],{type:'text/calendar'});const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download='alo186-usb-c-30-gun-kontrol.ics';link.click();URL.revokeObjectURL(link.href);
    });
    renderSaved();
  }

  return {STORAGE_KEY,TTL_MS,LIMIT,LABELS,requiredCategories,productPower,eligibleProducts,evaluate,cleanStored,loadShortlist,saveShortlist,createIcs,init};
});