(()=>{
  'use strict';
  const core=window.Alo186RuntimeHealthCore;
  const K='alo186.backupRuntimeJournal.v1';
  const $=id=>document.getElementById(id);
  const systems={mini:'Mini UPS',desktop:'Masaüstü UPS',station:'Güç istasyonu'};
  const loads={low:'Düşük',medium:'Orta',high:'Yüksek'};
  const links={mini:'/amazon-elektrik-urunleri/modem-mini-ups-secimi',station:'/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi',desktop:'/haberler/ups-mi-tasinabilir-guc-istasyonu-mu'};
  let items=[];

  function persist(){
    const payload=core.serialize(items);
    items=payload.items;
    if(items.length)localStorage.setItem(K,JSON.stringify(payload));
    else localStorage.removeItem(K);
  }
  function load(){
    try{
      const payload=JSON.parse(localStorage.getItem(K)||'null');
      if(!payload||payload.schema!==K)return [];
      const now=Date.now();
      const normalized=(Array.isArray(payload.items)?payload.items:[])
        .map(item=>core.normalizeEntry(item,payload.expiresAt,now)).filter(Boolean);
      const active=core.pruneEntries(normalized,now);
      const changed=active.length!==normalized.length||normalized.some((item,index)=>JSON.stringify(item)!==JSON.stringify(active[index]));
      if(changed){
        if(active.length)localStorage.setItem(K,JSON.stringify(core.serialize(active,now)));
        else localStorage.removeItem(K);
      }
      return active;
    }catch(_){return []}
  }
  function download(name,type,text){
    const link=document.createElement('a');
    link.href=URL.createObjectURL(new Blob([text],{type}));
    link.download=name;link.click();
    setTimeout(()=>URL.revokeObjectURL(link.href),500);
  }
  function ymd(date){return `${date.getFullYear()}${String(date.getMonth()+1).padStart(2,'0')}${String(date.getDate()).padStart(2,'0')}`}
  function renderRows(){
    const body=$('rows');body.replaceChildren();
    [...items].sort(core.compareOrder).reverse().forEach(item=>{
      const row=document.createElement('tr');
      for(const value of [item.date,systems[item.system],loads[item.load],item.charge==='full'?'Tam':'Kısmi',`${item.minutes} dk`]){
        const cell=document.createElement('td');cell.textContent=value;row.appendChild(cell);
      }
      const action=document.createElement('td');
      const button=document.createElement('button');button.type='button';button.className='alt';button.textContent='Sil';
      button.addEventListener('click',()=>{items=items.filter(entry=>entry.id!==item.id);persist();render(items.at(-1),false)});
      action.appendChild(button);row.appendChild(action);body.appendChild(row);
    });
  }
  function render(focus,scroll=true){
    items=core.pruneEntries(items);
    $('result').classList.toggle('hidden',!items.length);
    if(!items.length)return;
    const assessment=core.assess(items,focus&&items.find(item=>item.id===focus.id)||items.at(-1));
    $('latest').textContent=`${assessment.latest.minutes} dk`;
    $('change').textContent=assessment.change===null?'İlk karşılaştırma':`${assessment.change>=0?'+':''}${(assessment.change*100).toLocaleString('tr-TR',{maximumFractionDigits:1})}%`;
    $('count').textContent=String(items.length);
    $('state').textContent=assessment.label;
    $('state').className=`pill ${assessment.className}`;
    $('title').textContent=assessment.title;
    $('summary').textContent=assessment.summary;
    $('steps').replaceChildren(...assessment.steps.map(text=>{const li=document.createElement('li');li.textContent=text;return li}));
    renderRows();
    $('commercial').classList.toggle('hidden',!assessment.showCommercial);
    $('commercialLink').href=links[assessment.latest.system];
    if(scroll)$('result').scrollIntoView({behavior:'smooth',block:'start'});
  }

  $('date').value=new Date().toISOString().slice(0,10);
  $('form').addEventListener('submit',event=>{
    event.preventDefault();
    const now=Date.now();
    const entry=core.createEntry({
      id:`r${now}`,date:$('date').value,system:$('system').value,load:$('load').value,
      charge:$('charge').value,minutes:Number($('minutes').value),outcome:$('outcome').value,
      hazard:$('heat').checked||$('swell').checked||$('smell').checked||$('leak').checked
    },now);
    if(!entry)return;
    items=core.pruneEntries([...items,entry],now);
    persist();render(entry);
  });
  $('clear').addEventListener('click',()=>{localStorage.removeItem(K);items=[];$('result').classList.add('hidden')});
  $('json').addEventListener('click',()=>download('alo186-yedek-guc-runtime-gunlugu.json','application/json',JSON.stringify({...core.serialize(items),exportedAt:new Date().toISOString()},null,2)));
  $('ics').addEventListener('click',()=>{
    const start=new Date();start.setDate(start.getDate()+90);const end=new Date(start.getTime()+1800000);
    download('alo186-runtime-yeniden-test.ics','text/calendar',`BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//ALO186//Runtime Saglik//TR\r\nBEGIN:VEVENT\r\nUID:${Date.now()}@alo186.com\r\nDTSTART:${ymd(start)}T090000\r\nDTEND:${ymd(end)}T093000\r\nSUMMARY:Yedek guc runtime testini tekrarla\r\nDESCRIPTION:Ayni yuk ve tam sarj kosulunda kontrollu runtime testi yapin.\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n`);
  });
  items=load();if(items.length)render(items.at(-1),false);
})();
