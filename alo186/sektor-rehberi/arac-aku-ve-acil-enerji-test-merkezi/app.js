'use strict';
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root){root.ALO186VehicleEnergyHub=api;if(root.document)api.mount(root.document);}
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  const ROUTE='/sektor-rehberi/arac-aku-ve-acil-enerji-test-merkezi/';
  function buildPlan(data){
    const tasks=[];
    if(data.danger)tasks.push({priority:'P0',task:'Hasarlı, şişmiş, sızıntılı veya aşırı ısınan akü/güç cihazını kullanmayın; yol yardım veya yetkili servis desteği alın.'});
    if(data.failedStart)tasks.push({priority:'P1',task:'Tekrarlayan marş sorununu yalnız takviye cihazıyla maskelemeyin; akü, şarj sistemi, bağlantı ve kaçak tüketim testi planlayın.'});
    if(data.longTrip)tasks.push({priority:'P1',task:'Yolculuk öncesi jump starter şarjı, fiziksel durum, kablo/kelepçe ve araç kılavuzu uyumunu doğrulayın.'});
    if(data.accessoryPower)tasks.push({priority:'P1',task:'12 V priz A/W sınırı, inverter DC giriş akımı, havalandırma ve gerçek yük sıcaklık testini tamamlayın.'});
    if(data.vehicleChanged)tasks.push({priority:'P1',task:'Araç değiştiği için eski jump starter ve inverter uyumunu sıfırdan doğrulayın.'});
    if(data.storedVehicle)tasks.push({priority:'P2',task:'Uzun süre park edilen araçta akü bakım/şarj yöntemini üretici talimatıyla doğrulayın; sabit bağlantıyı uzman olmadan kurmayın.'});
    tasks.push({priority:'P2',task:'90 günde bir taşınabilir cihazların şarj seviyesi, geri çağırma kaydı, kablo, kelepçe, fiş ve gövde durumunu kontrol edin.'});
    return {route:ROUTE,createdAt:new Date().toISOString(),tasks,repeatDays:data.danger||data.failedStart?30:90,commerce:false,personalData:false};
  }
  function read(doc){const id=(x)=>doc.getElementById(x);return {danger:id('danger').checked,failedStart:id('failedStart').checked,longTrip:id('longTrip').checked,accessoryPower:id('accessoryPower').checked,vehicleChanged:id('vehicleChanged').checked,storedVehicle:id('storedVehicle').checked};}
  function esc(s){return String(s).replace(/[&<>"']/g,(c)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  function mount(doc){const form=doc.getElementById('planForm');if(!form)return;const result=doc.getElementById('result');let last=null;const render=()=>{last=buildPlan(read(doc));result.innerHTML='<h2>'+last.repeatDays+' günlük görev planı</h2><ol>'+last.tasks.map((x)=>'<li><strong>'+esc(x.priority)+'</strong> '+esc(x.task)+'</li>').join('')+'</ol><p>Bu merkez doğrudan ürün bağlantısı göstermez. Önce ilgili ücretsiz uygunluk aracını ve mevcut ekipman testini kullanın.</p>';};form.addEventListener('submit',(e)=>{e.preventDefault();render();result.scrollIntoView({behavior:'smooth',block:'start'});});doc.getElementById('exportJson').addEventListener('click',()=>{if(!last)render();const a=doc.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(last,null,2)],{type:'application/json'}));a.download='alo186-arac-acil-enerji-plani.json';a.click();URL.revokeObjectURL(a.href);});doc.getElementById('calendar').addEventListener('click',()=>{if(!last)render();const d=new Date();d.setDate(d.getDate()+last.repeatDays);const stamp=(x)=>x.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z');const ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Vehicle Energy Review//TR','BEGIN:VEVENT','UID:'+Date.now()+'@alo186.com','DTSTAMP:'+stamp(new Date()),'DTSTART:'+stamp(d),'SUMMARY:Araç aküsü ve acil enerji tekrar testi','DESCRIPTION:Akü marş davranışı jump starter şarjı geri çağırma kablo kelepçe 12 V priz ve inverter sıcaklık testini yeniden doğrulayın.','END:VEVENT','END:VCALENDAR'].join('\r\n');const a=doc.createElement('a');a.href=URL.createObjectURL(new Blob([ics],{type:'text/calendar'}));a.download='alo186-arac-acil-enerji-tekrar.ics';a.click();URL.revokeObjectURL(a.href);});}
  return {buildPlan,mount,ROUTE};
});