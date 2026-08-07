'use strict';
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root){root.ALO186CoolingChoice=api;if(root.document)api.mount(root.document);}
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  const ROUTE='/hesaplama/vantilator-hava-sogutucu-klima-karar/';
  const n=(v)=>Number(v);
  const round=(v,d=2)=>Number(n(v).toFixed(d));
  function calculate(data){
    const hours=Math.max(0,n(data.hoursPerDay));
    const days=Math.max(0,n(data.days));
    const energy=(w)=>round(Math.max(0,n(w))*hours*days/1000,2);
    return {
      fanKwh:energy(data.fanW),
      coolerKwh:energy(data.coolerW),
      portableAcKwh:energy(data.portableAcW),
      splitAcKwh:energy(data.splitAcW),
      humidityBand:n(data.humidityPct)<=45?'dry':n(data.humidityPct)>=60?'humid':'transition'
    };
  }
  function decide(data){
    const calc=calculate(data);
    const confirms=Boolean(data.confirmNeed&&data.confirmLabel&&data.confirmAffiliate);
    const temp=n(data.indoorTempC), humidity=n(data.humidityPct);
    if(data.heatEmergency||data.unconscious||data.confusion)return {...calc,code:'medical_emergency',commerce:false,category:'none',tone:'danger',title:'Sıcak çarpması şüphesinde 112’yi arayın',summary:'Bilinç değişikliği, nöbet, bayılma veya çok sıcak-kuru cilt tıbbi acildir. Ürün seçimi yapmayın; kişiyi güvenli biçimde serin alana alın ve 112 desteği isteyin.'};
    if(data.electricalDanger)return {...calc,code:'electrical_danger',commerce:false,category:'none',tone:'danger',title:'Elektrikli soğutma cihazını kullanmayın',summary:'Duman, erime, su teması, elektrik çarpması, sıcak priz veya yanık kokusunda enerjiyi güvenli biçimde ayırın ve yetkili elektrikçiden destek alın.'};
    if(data.activeOutage)return {...calc,code:'active_outage',commerce:false,category:'none',tone:'warn',title:'Aktif kesintide yeni ürün teslimatı çözüm değildir',summary:'Önce resmî kesinti kanalını, güvenli serin alanı, gölgeleme, su ve mevcut test edilmiş düşük güçlü cihazları kullanın.'};
    if(!Number.isFinite(temp)||!Number.isFinite(humidity)||temp<10||temp>55||humidity<10||humidity>100)return {...calc,code:'invalid',commerce:false,category:'none',tone:'warn',title:'Sıcaklık ve nem verisini doğrulayın',summary:'İç ortam sıcaklığını ve bağıl nemi güvenli bir termometre-higrometre veya güvenilir cihaz göstergesinden girin.'};
    if(temp>=40)return {...calc,code:'extreme_heat',commerce:false,category:'none',tone:'danger',title:'Vantilatörü tek başına güvenlik çözümü kabul etmeyin',summary:'40°C ve üzerindeki iç ortamda fan vücudu daha fazla ısıtabilir. Serin bir yere geçin, riskli kişileri kontrol edin ve sağlık belirtisinde 112’yi arayın.'};
    if(data.vulnerablePerson&&temp>=32)return {...calc,code:'vulnerable',commerce:false,category:'none',tone:'warn',title:'Riskli kişi için yalnız cihaz karşılaştırması yeterli değil',summary:'Bebek, ileri yaş, gebelik veya kronik hastalık durumunda serin alan, sıvı, sağlık önerisi ve düzenli kontrol planını önceliklendirin.'};
    if(data.outdoorAir==='poor'&&data.strategy==='night_ventilation')return {...calc,code:'air_quality',commerce:false,category:'none',tone:'warn',title:'Dış hava kalitesi uygun değilken pencere havalandırmasını erteleyin',summary:'Dış hava kalitesi kötü veya dumanlıysa gece havalandırması yerine güvenli iç ortam serinletme planı kullanın.'};
    if(data.strategy==='evaporative'&&(humidity>=60||!data.crossVentilation||!data.waterSafe))return {...calc,code:'evaporative_unsuitable',commerce:false,category:'none',tone:'warn',title:'Hava soğutucu için nem ve havalandırma koşulu uygun değil',summary:'Evaporatif cihazlar sıcak-kuru koşul ve sürekli hava çıkışı ister. Nemli ortam, kapalı oda veya güvenli su yönetimi yoksa daha fazla nem ve sınırlı konfor oluşabilir.'};
    if(data.existingSolution&&data.realComfortTest&&data.noDamage)return {...calc,code:'no_buy',commerce:false,category:'none',tone:'ok',title:'Mevcut serinleme planı yeterli — yeni ürün almayın',summary:'Mevcut cihaz güvenli çalışıyor, hedeflenen kişiyi/alanı serinletiyor ve gerçek sıcak gün testini geçtiyse yalnız yeni model için değişim gerekmez.'};
    if(data.strategy==='whole_room' || (temp>=35&&humidity>=60))return {...calc,code:'ac_assessment',commerce:false,category:'ac_assessment',tone:'info',title:'Oda soğutması için klima kapasitesi ve elektrik altyapısını doğrulayın',summary:'Fan ve evaporatif cihaz oda sıcaklığını güvenilir biçimde kontrol etmeyebilir. Önce ücretsiz BTU ve elektrik altyapısı testine geçin; doğrudan ürün seçmeyin.'};
    if(!confirms)return {...calc,code:'confirm',commerce:false,category:'none',tone:'info',title:'Önce üç güven onayını tamamlayın',summary:'Mevcut çözümün yetersizliğini, ürün etiketini tekrar kontrol edeceğinizi ve sonraki sayfanın satış ortaklığı bağlantıları içerebileceğini ayrı ayrı onaylayın.'};
    if(data.strategy==='evaporative'&&humidity<=45&&data.crossVentilation&&data.waterSafe)return {...calc,code:'eligible_cooler',commerce:true,category:'evaporative_cooler',tone:'ok',title:'Koşullu hava soğutucu sınıfı açıldı',summary:'Yalnız sıcak-kuru, havalandırılabilen ve su yönetimi güvenli bir ortam için; gerçek W, hazne temizliği ve üretici oda şartlarını karşılaştırın.'};
    return {...calc,code:'eligible_fan',commerce:true,category:'fan',tone:'ok',title:'Koşullu vantilatör / hava dolaştırıcı sınıfı açıldı',summary:'Kişisel serinleme için, 40°C altındaki ortamda ve mevcut cihaz yetersizse; gerçek W, ses, devrilme koruması ve kullanım alanını karşılaştırın.'};
  }
  function read(doc){const id=(x)=>doc.getElementById(x);return {heatEmergency:id('heatEmergency').checked,unconscious:id('unconscious').checked,confusion:id('confusion').checked,electricalDanger:id('electricalDanger').checked,activeOutage:id('activeOutage').checked,vulnerablePerson:id('vulnerablePerson').checked,indoorTempC:id('indoorTempC').value,humidityPct:id('humidityPct').value,outdoorAir:id('outdoorAir').value,strategy:id('strategy').value,crossVentilation:id('crossVentilation').checked,waterSafe:id('waterSafe').checked,existingSolution:id('existingSolution').checked,realComfortTest:id('realComfortTest').checked,noDamage:id('noDamage').checked,fanW:id('fanW').value,coolerW:id('coolerW').value,portableAcW:id('portableAcW').value,splitAcW:id('splitAcW').value,hoursPerDay:id('hoursPerDay').value,days:id('days').value,confirmNeed:id('confirmNeed').checked,confirmLabel:id('confirmLabel').checked,confirmAffiliate:id('confirmAffiliate').checked};}
  function esc(s){return String(s).replace(/[&<>"']/g,(c)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  function mount(doc){const form=doc.getElementById('coolingChoiceForm');if(!form)return;const result=doc.getElementById('result');const affiliate=doc.getElementById('affiliate');let last=null;const render=()=>{last=decide(read(doc));result.className='result '+last.tone;result.innerHTML='<h2>'+esc(last.title)+'</h2><p>'+esc(last.summary)+'</p><div class="metrics"><span><b>'+esc(last.fanKwh)+'</b> kWh fan</span><span><b>'+esc(last.coolerKwh)+'</b> kWh hava soğutucu</span><span><b>'+esc(last.portableAcKwh)+'</b> kWh portatif klima</span><span><b>'+esc(last.splitAcKwh)+'</b> kWh split klima</span></div><small>kWh değerleri yalnız girdiğiniz etiket W, saat ve gün üzerinden hesaplanır; TL, tarife veya tasarruf vaadi değildir.</small>';affiliate.classList.toggle('hidden',!last.commerce);affiliate.dataset.category=last.category||'none';};form.addEventListener('submit',(e)=>{e.preventDefault();render();result.scrollIntoView({behavior:'smooth',block:'start'});});doc.getElementById('exportJson').addEventListener('click',()=>{if(!last)render();const a=doc.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify({route:ROUTE,createdAt:new Date().toISOString(),input:read(doc),decision:last},null,2)],{type:'application/json'}));a.download='alo186-serinleme-karari.json';a.click();URL.revokeObjectURL(a.href);});}
  return {calculate,decide,mount,ROUTE};
});