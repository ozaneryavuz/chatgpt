'use strict';
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root){root.ALO186JumpStarter=api;if(root.document)api.mount(root.document);}
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  const ROUTE='/hesaplama/aku-takviye-cihazi-jump-starter-uygunluk/';
  const bool=(v)=>Boolean(v);

  function decide(data){
    const confirmations=bool(data.confirmNeed&&data.confirmManual&&data.confirmAffiliate);
    if(data.danger||data.batteryDamage||data.frozenBattery){
      return {code:'danger',commerce:false,tone:'danger',title:'Takviye işlemini durdurun',summary:'Duman, erime, sızıntı, şişme, çatlak, donmuş akü veya elektrik çarpması riski varsa takviye denemeyin. Güvenli alana geçin ve yol yardım/servis desteği kullanın.'};
    }
    if(data.activeRoadside&& !data.existingTested){
      return {code:'active',commerce:false,tone:'warn',title:'Aktif arızada yeni ürün teslimatı çözüm değildir',summary:'Aracı güvenli konuma alın, araç üreticisinin yol yardım ve takviye talimatını izleyin. Henüz alınmamış bir cihazı anlık çözüm saymayın.'};
    }
    if(data.vehicleClass==='ev'||data.vehicleClass==='hybrid_high_voltage'){
      return {code:'special_vehicle',commerce:false,tone:'warn',title:'Araç üreticisi ve yol yardım rotası gerekli',summary:'Elektrikli veya yüksek gerilimli hibrit araçlarda 12 V yardımcı akü işlemi model talimatına bağlıdır. Genel jump starter seçimi yapmayın.'};
    }
    if(data.systemVoltage!=='12'){
      return {code:'voltage',commerce:false,tone:'warn',title:'Bu tüketici akışı yalnız doğrulanmış 12 V sistem içindir',summary:'24 V, 48 V veya çift akülü sistemlerde profesyonel araç elektriği desteği gerekir.'};
    }
    if(!data.manualVerified||!data.connectionPointsVerified||!data.batteryTypeVerified){
      return {code:'evidence',commerce:false,tone:'warn',title:'Araç ve akü kanıtı eksik',summary:'Tam model kullanım kılavuzu, izin verilen takviye noktaları, 12 V sistem ve akü kimyası doğrulanmadan cihaz seçmeyin.'};
    }
    if(data.batteryType==='lithium'&&!data.lithiumApproved){
      return {code:'lithium',commerce:false,tone:'warn',title:'Lityum marş aküsü için genel cihaz seçmeyin',summary:'Araç ve jump starter üreticisinin aynı kimyayı açıkça desteklediği doğrulanmalıdır.'};
    }
    if(data.existingTested&&data.existingVoltageMatch&&data.existingVehicleMatch&&data.existingPhysicalSafe&&data.existingChargeReady){
      return {code:'no_buy',commerce:false,tone:'ok',title:'Mevcut jump starter yeterli — yeni ürün almayın',summary:'Gerilim, araç/akü sınıfı, fiziksel durum, şarj seviyesi ve üretici talimatı karşılanıyor. Cihazı periyodik olarak şarj ve gerçek görev öncesi kontrol edin.'};
    }
    if(!data.existingPhysicalSafe&&data.hasExisting){
      return {code:'replace_service',commerce:false,tone:'danger',title:'Hasarlı cihazı kullanmayın veya şarj etmeyin',summary:'Şişme, darbe, kablo/kelepçe hasarı, aşırı ısınma veya geri çağırma şüphesi varsa üretici ve yetkili atık/servis kanalını kullanın.'};
    }
    if(!confirmations){
      return {code:'confirm',commerce:false,tone:'info',title:'Önce üç güven onayını tamamlayın',summary:'Gerçek ihtiyaç, tam model/akü uyumu ve satış ortaklığı bilgisini ayrı ayrı doğrulayın.'};
    }
    return {code:'eligible',commerce:true,tone:'ok',title:'Koşullu ürün sınıfı açıldı',summary:'Yalnız 12 V araç, doğrulanmış akü kimyası, araç üreticisi takviye izni ve fiziksel güvenlik koşullarıyla jump starter sınıfını karşılaştırın. Pazarlama “peak amp” değerini tek başına yeterli saymayın.'};
  }

  function read(doc){
    const id=(x)=>doc.getElementById(x);
    return {
      danger:id('danger').checked,batteryDamage:id('batteryDamage').checked,frozenBattery:id('frozenBattery').checked,
      activeRoadside:id('mode').value==='active',vehicleClass:id('vehicleClass').value,systemVoltage:id('systemVoltage').value,
      manualVerified:id('manualVerified').checked,connectionPointsVerified:id('connectionPointsVerified').checked,
      batteryTypeVerified:id('batteryTypeVerified').checked,batteryType:id('batteryType').value,lithiumApproved:id('lithiumApproved').checked,
      hasExisting:id('hasExisting').checked,existingTested:id('existingTested').checked,existingVoltageMatch:id('existingVoltageMatch').checked,
      existingVehicleMatch:id('existingVehicleMatch').checked,existingPhysicalSafe:id('existingPhysicalSafe').checked,existingChargeReady:id('existingChargeReady').checked,
      confirmNeed:id('confirmNeed').checked,confirmManual:id('confirmManual').checked,confirmAffiliate:id('confirmAffiliate').checked
    };
  }
  function escapeHtml(s){return String(s).replace(/[&<>"']/g,(c)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  function mount(doc){
    const form=doc.getElementById('jumpForm'); if(!form)return;
    const result=doc.getElementById('result'); const affiliate=doc.getElementById('affiliate'); let last=null;
    const render=()=>{last=decide(read(doc));result.className='result '+last.tone;result.innerHTML='<h2>'+escapeHtml(last.title)+'</h2><p>'+escapeHtml(last.summary)+'</p>';affiliate.classList.toggle('hidden',!last.commerce);};
    form.addEventListener('submit',(e)=>{e.preventDefault();render();result.scrollIntoView({behavior:'smooth',block:'start'});});
    doc.getElementById('exportJson').addEventListener('click',()=>{if(!last)render();const blob=new Blob([JSON.stringify({route:ROUTE,createdAt:new Date().toISOString(),input:read(doc),decision:last},null,2)],{type:'application/json'});const a=doc.createElement('a');a.href=URL.createObjectURL(blob);a.download='alo186-jump-starter-uygunluk.json';a.click();URL.revokeObjectURL(a.href);});
    doc.getElementById('calendar').addEventListener('click',()=>{const d=new Date();d.setDate(d.getDate()+90);const stamp=(x)=>x.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z');const ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Vehicle Battery Check//TR','BEGIN:VEVENT','UID:'+Date.now()+'@alo186.com','DTSTAMP:'+stamp(new Date()),'DTSTART:'+stamp(d),'SUMMARY:Araç aküsü ve jump starter 90 günlük kontrolü','DESCRIPTION:Şarj seviyesi fiziksel durum kablo kelepçe geri çağırma ve araç kılavuzu uyumunu yeniden kontrol edin.','END:VEVENT','END:VCALENDAR'].join('\r\n');const a=doc.createElement('a');a.href=URL.createObjectURL(new Blob([ics],{type:'text/calendar'}));a.download='alo186-arac-aku-90-gun.ics';a.click();URL.revokeObjectURL(a.href);});
  }
  return {decide,mount,ROUTE};
});