(()=>{
  'use strict';
  const core=window.Alo186EvSharedParkingCore,$=id=>document.getElementById(id);let receipt=null;
  function download(name,type,text){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),500)}
  function ymd(d){return `${d.getFullYear()}${String(d.getMonth()+1).padStart(2,'0')}${String(d.getDate()).padStart(2,'0')}`}
  $('form').addEventListener('submit',event=>{
    event.preventDefault();
    const assessment=core.assess({facility:$('facility').value,use:$('use').value,supply:$('supply').value,parking:$('parking').value,load:$('load').value,management:$('management').value,metering:$('metering').value,evidence:$('evidence').value});
    receipt={schema:'alo186.evSharedParkingDecisionPack.v1',personalData:false,createdAt:new Date().toISOString(),...assessment};
    $('result').classList.remove('hidden');$('state').textContent=assessment.label;$('state').className=`pill ${assessment.className}`;$('title').textContent=assessment.title;$('summary').textContent=assessment.summary;$('score').textContent=`${assessment.score}/${assessment.maxScore}`;$('model').textContent=assessment.model;$('agenda').replaceChildren(...assessment.agenda.map(text=>{const li=document.createElement('li');li.textContent=text;return li}));$('technical').replaceChildren(...assessment.technical.map(text=>{const li=document.createElement('li');li.textContent=text;return li}));$('result').scrollIntoView({behavior:'smooth',block:'start'});
  });
  $('json').addEventListener('click',()=>receipt&&download('alo186-ev-sarj-karar-paketi.json','application/json',JSON.stringify(receipt,null,2)));
  $('print').addEventListener('click',()=>window.print());
  $('ics').addEventListener('click',()=>{const s=new Date();s.setDate(s.getDate()+45);const e=new Date(s.getTime()+1800000);download('alo186-ev-sarj-takip.ics','text/calendar',`BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//ALO186//EV Karar Paketi//TR\r\nBEGIN:VEVENT\r\nUID:${Date.now()}@alo186.com\r\nDTSTART:${ymd(s)}T090000\r\nDTEND:${ymd(e)}T093000\r\nSUMMARY:EV sarj karar paketini yeniden gozden gecir\r\nDESCRIPTION:Park besleme yuk yonetimi olcum proje ve kabul eksiklerini kontrol edin.\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n`)})
})();
