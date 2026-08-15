'use strict';
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root){root.ALO186OutageLighting=api;if(root.document)api.mount(root.document);}
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  const ROUTE='/hesaplama/elektrik-kesintisi-sarjli-ampul-isildak-uygunluk/';
  const n=(value)=>Number(value);
  const finite=(value)=>Number.isFinite(n(value));
  const round=(value,digits=2)=>Number(n(value).toFixed(digits));

  function runtimeHours(data){
    if(data.runtimeMode==='manufacturer')return finite(data.manufacturerRuntimeH)&&n(data.manufacturerRuntimeH)>0?round(data.manufacturerRuntimeH,2):NaN;
    if(!finite(data.batteryWh)||n(data.batteryWh)<=0||!finite(data.lampW)||n(data.lampW)<=0)return NaN;
    const usable=finite(data.usablePct)?Math.min(100,Math.max(1,n(data.usablePct)))/100:0.8;
    return round(n(data.batteryWh)*usable/n(data.lampW),2);
  }

  function decide(data){
    const runtime=runtimeHours(data);
    const required=n(data.requiredHours);
    const areas=n(data.requiredAreas);
    const units=n(data.availableUnits);
    const confirmations=Boolean(data.confirmNeed&&data.confirmEvidence&&data.confirmAffiliate);
    if(data.danger)return {code:'danger',commerce:false,tone:'danger',title:'Önce yangın ve elektrik güvenliği',summary:'Duman, erime, şişmiş batarya, yanık kokusu, su teması, elektrik çarpması veya aşırı ısınmada cihazı kullanmayın ya da şarj etmeyin. Gerekirse 112 ve yetkili servis/elektrikçi rotasına geçin.'};
    if(data.openFlame)return {code:'flame',commerce:false,tone:'danger',title:'Mum veya açık alevi kesinti aydınlatması olarak kullanmayın',summary:'Açık alev yangın riskini artırır. Mevcut güvenli pilli fener, telefon ışığı veya test edilmiş bataryalı armatür gibi alevsiz çözümleri kullanın.'};
    if(['commercial_exit','apartment_egress','fire_system'].includes(data.context)||data.productType==='fixed_emergency')return {code:'regulated',commerce:false,tone:'warn',title:'Kaçış ve ortak alan aydınlatması tüketici ürününe dönüştürülmez',summary:'İşyeri, otel, apartman kaçış yolu, merdiven, çıkış işareti ve yangın güvenliği için şarjlı ampul veya portatif ışıldak, uygun tasarlanmış ve test edilmiş acil aydınlatmanın yerine geçmez. Proje, süre ve periyodik test yetkin kişilerce değerlendirilmelidir.'};
    if(data.mode==='active_outage'&&!data.existingSafeLight)return {code:'active',commerce:false,tone:'warn',title:'Aktif kesintide henüz alınmamış ürün çözüm değildir',summary:'Mevcut güvenli telefon ışığı, pilli fener veya test edilmiş bataryalı lambayı kullanın; merdiven ve ıslak alanlarda hareketi azaltın. Satın alma planını kesinti sonrasına bırakın.'};
    if(!data.physicalSafe)return {code:'physical',commerce:false,tone:'danger',title:'Batarya ve gövde güvenli değil',summary:'Şişme, sızıntı, çatlak, gevşek duy, kablo hasarı, aşırı ısınma veya su teması olan ürünü kullanmayın ve şarj etmeyin.'};
    if(!data.charged||!data.indicatorOk)return {code:'charge',commerce:false,tone:'warn',title:'Önce şarj ve gösterge kanıtını tamamlayın',summary:'Şarj göstergesi, batarya durumu ve üretici talimatı doğrulanmadan kesinti süresi planlanamaz.'};
    if(data.productType==='rechargeable_bulb'&&!data.switchDependencyKnown)return {code:'switch',commerce:false,tone:'warn',title:'Şarjlı ampulün anahtar ve armatür davranışı bilinmiyor',summary:'Bazı şarjlı ampuller kesintide yalnız belirli anahtar/armatür koşullarında çalışır. Tam model kılavuzunu ve gerçek kesinti testini doğrulayın.'};
    if(!data.realOutageTest)return {code:'test',commerce:false,tone:'warn',title:'Gerçek kesinti veya üretici testini tamamlayın',summary:'Yalnız şarj göstergesi, ürünün hedef parlaklık ve süreyi sağlayacağını kanıtlamaz. Güvenli kontrollü test yapın.'};
    if(!finite(runtime)||runtime<=0||!finite(required)||required<=0)return {code:'evidence',commerce:false,tone:'warn',title:'Süre kanıtı eksik',summary:'Üreticinin seçilen parlaklık için çalışma süresini veya batarya Wh ve lamba W değerlerini doğrulamadan sonuç üretilemez.'};
    if(!finite(areas)||areas<1||!finite(units)||units<0)return {code:'coverage_unknown',commerce:false,tone:'warn',title:'Aydınlatılacak alan ve mevcut cihaz sayısını girin',summary:'Tek cihazın süresi yeterli olsa bile merdiven, koridor ve oda kapsamı ayrı değerlendirilmelidir.'};
    const durationOk=runtime>=required;
    const coverageOk=units>=areas;
    if(data.existingSuitable&&durationOk&&coverageOk)return {code:'no_buy',commerce:false,tone:'ok',title:'Mevcut aydınlatma planı yeterli — yeni ürün almayın',summary:`Doğrulanmış yaklaşık ${runtime} saat çalışma süresi ve ${units} cihaz, ${areas} alan için girdiğiniz ihtiyacı karşılıyor. Yalnız daha yeni model için değiştirmeyin.`};
    if(!durationOk&&!confirmations)return {code:'runtime_gap',commerce:false,tone:'warn',title:'Süre açığı var; ticari geçiş henüz açılmadı',summary:`Doğrulanmış süre yaklaşık ${runtime} saat, hedef ${required} saat. Önce parlaklık modu, batarya etiketi, gerçek test ve mevcut alternatifleri doğrulayın.`};
    if(!coverageOk&&!confirmations)return {code:'coverage_gap',commerce:false,tone:'warn',title:'Alan kapsamı yetersiz; önce yerleşim planını doğrulayın',summary:`${areas} alan için ${units} test edilmiş cihaz var. Kaçış yolunu tüketici ürünüyle ikame etmeyin; ev içi düşük riskli kullanımda konum ve mevcut cihazları yeniden planlayın.`};
    if(confirmations&&['home','camping','private_outdoor'].includes(data.context)&&(!durationOk||!coverageOk))return {code:'qualified',commerce:true,tone:'warn',title:'Yalnız doğrulanmış aydınlatma açığı için ürün sınıfı açıldı',summary:'Tam model çalışma süresi, parlaklık modu, batarya güvenliği, şarj yöntemi ve gerçek kesinti testi doğrulanabilen şarjlı ampul, ışıldak, el feneri veya kafa lambası sınıfını karşılaştırın.'};
    return {code:'plan',commerce:false,tone:'warn',title:'Mevcut cihazları aynı parlaklıkta yeniden test edin',summary:'Süre veya alan açığı kanıtlanmadan yeni ürün yolu açılmaz. Önce mevcut telefon ışığı, fener, ampul ve ışıldakları görev bazında test edin.'};
  }

  function report(data){return {route:ROUTE,generatedAt:new Date().toISOString(),runtimeHours:runtimeHours(data),decision:decide(data),personalData:false,officialApproval:false};}
  function calendar(days=90){
    const start=new Date(Date.now()+Math.max(1,n(days)||90)*86400000);
    const end=new Date(start.getTime()+30*60000);
    const stamp=(date)=>date.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z');
    return ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Outage Lighting Check//TR','BEGIN:VEVENT',`UID:outage-lighting-${Date.now()}@alo186.com`,`DTSTAMP:${stamp(new Date())}`,`DTSTART:${stamp(start)}`,`DTEND:${stamp(end)}`,'SUMMARY:Kesinti aydınlatması süre ve güvenlik testi','DESCRIPTION:Batarya fiziksel durumunu, şarj göstergesini, gerçek kesinti davranışını, seçilen parlaklık süresini ve alan kapsamını yeniden test edin.','END:VEVENT','END:VCALENDAR'].join('\r\n');
  }
  function download(name,text,type){const blob=new Blob([text],{type});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),0);}
  function read(doc){
    const value=(id)=>doc.getElementById(id)?.value;
    const checked=(id)=>Boolean(doc.getElementById(id)?.checked);
    return {danger:checked('danger'),openFlame:checked('openFlame'),context:value('context'),mode:value('mode'),productType:value('productType'),runtimeMode:value('runtimeMode'),manufacturerRuntimeH:value('manufacturerRuntimeH'),batteryWh:value('batteryWh'),lampW:value('lampW'),usablePct:value('usablePct'),requiredHours:value('requiredHours'),requiredAreas:value('requiredAreas'),availableUnits:value('availableUnits'),physicalSafe:checked('physicalSafe'),charged:checked('charged'),indicatorOk:checked('indicatorOk'),switchDependencyKnown:checked('switchDependencyKnown'),realOutageTest:checked('realOutageTest'),existingSafeLight:checked('existingSafeLight'),existingSuitable:checked('existingSuitable'),confirmNeed:checked('confirmNeed'),confirmEvidence:checked('confirmEvidence'),confirmAffiliate:checked('confirmAffiliate')};
  }
  function mount(doc){
    const form=doc.getElementById('lightingForm');if(!form)return;let last=null;
    const runtimeMode=doc.getElementById('runtimeMode');
    const sync=()=>{doc.getElementById('manufacturerField').classList.toggle('hidden',runtimeMode.value!=='manufacturer');doc.getElementById('batteryFields').classList.toggle('hidden',runtimeMode.value!=='battery');};
    runtimeMode.addEventListener('change',sync);sync();
    form.addEventListener('submit',(event)=>{event.preventDefault();const data=read(doc);last=report(data);const d=last.decision;const result=doc.getElementById('result');result.className=`result ${d.tone}`;result.innerHTML=`<h2>${d.title}</h2><p>${d.summary}</p><div class="metrics"><div class="metric"><span>Doğrulanmış süre</span><strong>${Number.isFinite(last.runtimeHours)?last.runtimeHours+' saat':'—'}</strong></div><div class="metric"><span>Hedef süre</span><strong>${data.requiredHours||'—'} saat</strong></div><div class="metric"><span>Alan / cihaz</span><strong>${data.requiredAreas||'—'} / ${data.availableUnits||'—'}</strong></div><div class="metric"><span>Ticari yol</span><strong>${d.commerce?'Açık':'Kapalı'}</strong></div></div>`;doc.getElementById('affiliate').classList.toggle('hidden',!d.commerce);result.scrollIntoView({behavior:'smooth',block:'start'});});
    doc.getElementById('exportJson')?.addEventListener('click',()=>download('alo186-kesinti-aydinlatma-kontrolu.json',JSON.stringify(last||report(read(doc)),null,2),'application/json'));
    doc.getElementById('calendar')?.addEventListener('click',()=>download('alo186-kesinti-aydinlatma-kontrolu.ics',calendar(90),'text/calendar'));
  }
  return {ROUTE,runtimeHours,decide,report,calendar,mount};
});