(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;root.Alo186SupplierReadiness=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const documents=[
    {id:'model',label:'Tam marka ve model / ürün kodu',weight:12},
    {id:'datasheet',label:'Resmî teknik veri sayfası',weight:14},
    {id:'manual',label:'Güncel kullanım ve kurulum kılavuzu',weight:14},
    {id:'compliance',label:'Uygunluk ve standart belgelerinin gerçek kapsamı',weight:12},
    {id:'official_url',label:'Güncel resmî ürün veya destek URL’si',weight:10},
    {id:'limits',label:'Desteklenmeyen ve sınırlı kullanım senaryoları',weight:8}
  ];
  const allowed={
    category:['ups','portable','ev','solar','safety','measurement'],
    type:['data','sponsored','category','document'],
    readiness:['complete','partial','unknown'],
    goal:['accuracy','education','visibility','launch']
  };

  function valid(group,value){return allowed[group].includes(String(value));}
  function selectedSet(values){return new Set(Array.isArray(values)?values.map(String):[]);}
  function assess(input={}){
    const data={};for(const key of Object.keys(allowed))data[key]=valid(key,input[key])?String(input[key]):allowed[key][0];
    const selected=selectedSet(input.documents);
    let score=documents.reduce((sum,item)=>sum+(selected.has(item.id)?item.weight:0),0);
    score+=data.readiness==='complete'?20:data.readiness==='partial'?10:0;
    score+=data.type==='data'||data.type==='document'?10:5;
    score=Math.min(100,score);
    const missing=documents.filter((item)=>!selected.has(item.id));
    const band=score>=85&&missing.length<=1?'ready':score>=58?'partial':'prepare';
    const label=band==='ready'?'Teknik doğrulamaya hazır':band==='partial'?'Kısmen hazır':'Kaynak paketi eksik';
    const next=band==='ready'?'Talebi gönderip kapsam, etiketleme ve ücret koşullarını yazılı teyit edin.':band==='partial'?'Eksik kaynakları tamamlayın; sponsorlu görünürlükten önce teknik veri doğrulamasıyla başlayın.':'Önce tam model, resmî veri sayfası, kılavuz ve kullanım sınırlarını hazırlayın.';
    return {data,score,band,label,selected:[...selected],missing,next};
  }

  function brief(readable,assessment){
    return ['ALO186 Tedarikçi ve Üretici İş Birliği Teknik Hazırlık Özeti','',`Hazırlık skoru: ${assessment.score}/100 — ${assessment.label}`,`Ürün alanı: ${readable.category}`,`İş birliği türü: ${readable.type}`,`Kaynak hazırlığı: ${readable.readiness}`,`Hedef: ${readable.goal}`,'','Eksik veya yeniden doğrulanacak kaynaklar:',...(assessment.missing.length?assessment.missing.map((item)=>`- ${item.label}`):['- Eksik zorunlu kaynak görünmüyor; kapsam yine editoryal incelemeden geçer.']),'',`Sonraki adım: ${assessment.next}`,'','Bağımsızlık koşulu: Ödeme organik teknik sıralamayı, güvenlik uyarısını, kaynak eleştirisini veya satın almama sonucunu değiştiremez.'].join('\n');
  }

  return {documents,allowed,assess,brief};
});
