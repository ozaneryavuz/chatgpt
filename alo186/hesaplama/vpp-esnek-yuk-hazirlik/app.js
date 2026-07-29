(()=>{
  'use strict';
  const core=window.Alo186VppReadinessCore,$=id=>document.getElementById(id);let receipt=null;
  function download(name,type,text){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),500)}
  function ymd(d){return `${d.getFullYear()}${String(d.getMonth()+1).padStart(2,'0')}${String(d.getDate()).padStart(2,'0')}`}
  function selected(){return [...document.querySelectorAll('input[name="asset"]:checked')].map(x=>x.value)}
  $('form').addEventListener('submit',event=>{
    event.preventDefault();
    const assessment=core.assess({assets:selected(),values:{history:$('history').value,meter:$('meter').value,telemetry:$('telemetry').value,control:$('control').value,availability:$('availability').value,contract:$('contract').value}});
    receipt={schema:'alo186.vppReadiness.v1',personalData:false,createdAt:new Date().toISOString(),...assessment};
    $('result').classList.remove('hidden');$('state').textContent=assessment.label;$('state').className=`pill ${assessment.className}`;$('title').textContent=assessment.title;$('summary').textContent=assessment.summary;$('score').textContent=`${assessment.score}/${assessment.max}`;$('assets').textContent=assessment.assets.length?`${assessment.assets.length} sınıf`:'Tanımlanmadı';$('steps').replaceChildren(...assessment.steps.map(text=>{const li=document.createElement('li');li.textContent=text;return li}));$('result').scrollIntoView({behavior:'smooth',block:'start'});
  });
  $('json').addEventListener('click',()=>receipt&&download('alo186-vpp-hazirlik-on-dosyasi.json','application/json',JSON.stringify(receipt,null,2)));
  $('ics').addEventListener('click',()=>{const s=new Date();s.setDate(s.getDate()+30);const e=new Date(s.getTime()+1800000);download('alo186-vpp-gozden-gecirme.ics','text/calendar',`BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//ALO186//VPP Hazirlik//TR\r\nBEGIN:VEVENT\r\nUID:${Date.now()}@alo186.com\r\nDTSTART:${ymd(s)}T090000\r\nDTEND:${ymd(e)}T093000\r\nSUMMARY:VPP ve esnek yuk hazirligini yeniden gozden gecir\r\nDESCRIPTION:Veri telemetri kontrol ve kullanilabilirlik eksiklerini yeniden kontrol edin.\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n`)})
})();
