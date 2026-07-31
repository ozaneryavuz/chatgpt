'use strict';
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root){root.ALO186PowerbankFlight=api;if(root.document)api.mount(root.document);}
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  const ROUTE='/hesaplama/powerbank-ucak-wh-kabin-bagaji-uygunluk/';
  const n=(value)=>Number(value);
  const finite=(value)=>Number.isFinite(n(value));
  const round=(value,digits=1)=>Number(n(value).toFixed(digits));
  function energyWh(data){
    if(data.energyMode==='wh')return finite(data.wh)?round(data.wh,2):NaN;
    if(!finite(data.mah)||!finite(data.voltage))return NaN;
    return round((n(data.mah)/1000)*n(data.voltage),2);
  }
  function decide(data){
    const wh=energyWh(data);
    const maxWh=n(data.airlineMaxWh);
    const maxQty=n(data.airlineMaxQty);
    const quantity=n(data.quantity);
    if(data.unsafeBattery)return {code:'unsafe',commerce:false,title:'Bataryayı taşımayın veya kullanmayın',tone:'danger',summary:'Şişme, hasar, aşırı ısınma, sıvı teması veya geri çağırma şüphesi bulunan lityum batarya için ürün karşılaştırması yapılmaz; üretici ve taşıyıcının güvenlik prosedürünü izleyin.'};
    if(!finite(wh)||wh<=0||!finite(maxWh)||maxWh<=0||!finite(maxQty)||maxQty<1||!finite(quantity)||quantity<1)return {code:'invalid',commerce:false,title:'Etiket ve havayolu sınırı eksik',tone:'warn',summary:'Wh ya da mAh+V etiketi ile havayolunun güncel Wh ve adet sınırını doğrulamadan sonuç üretilemez.'};
    if(!data.airlineChecked)return {code:'verify_airline',commerce:false,title:'Önce havayolunun güncel kuralını doğrulayın',tone:'warn',summary:'IATA genel çerçevesi tek başına taşıma onayı değildir. Uçuşu gerçekleştiren havayolunun güncel powerbank ve yedek batarya kuralını kontrol edin.'};
    if((data.kind==='powerbank'||data.kind==='spare')&&!data.cabinOnly)return {code:'checked_bag_block',commerce:false,title:'Kayıtlı bagaja koymayın',tone:'danger',summary:'Powerbank ve yedek lityum bataryalar kabin bagajında, kısa devreye karşı korunmuş biçimde taşınmalıdır; kayıtlı bagaj planıyla devam etmeyin.'};
    if(wh>maxWh)return {code:'over_limit',commerce:false,title:'Girilen havayolu sınırının üzerinde',tone:'danger',summary:`${wh} Wh, doğruladığınız ${maxWh} Wh sınırını aşıyor. ALO186 taşıma onayı vermez; havayoluyla doğrudan görüşmeden seyahate götürmeyin.`};
    if(quantity>maxQty)return {code:'quantity_limit',commerce:false,title:'Girilen adet sınırı aşılıyor',tone:'danger',summary:`${quantity} adet, doğruladığınız ${maxQty} adet sınırını aşıyor. Daha fazla ürün satın almak çözüm değildir; havayolunun güncel kuralını izleyin.`};
    if(!data.terminalProtected)return {code:'terminal_risk',commerce:false,title:'Kısa devre koruması eksik',tone:'danger',summary:'Terminaller, portlar ve cihaz gövdesi kısa devre ve fiziksel hasara karşı korunmadan taşımaya hazırlanmış sayılmaz.'};
    if(data.planUseOnBoard)return {code:'onboard_rule',commerce:false,title:'Uçuş sırasında kullanım kuralını yeniden doğrulayın',tone:'warn',summary:'Bazı havayolları powerbank kullanımını ve şarjını uçuş boyunca yasaklar. Uçakta kullanma planını kaldırın veya taşıyıcının güncel talimatını doğrulayın.'};
    if(data.existingSuitable)return {code:'no_buy',commerce:false,title:'Mevcut powerbank yeterli — yeni ürün almayın',tone:'ok',summary:`Mevcut ürün ${wh} Wh etiketiyle doğruladığınız havayolu sınırında, fiziksel olarak güvenli ve cihaz ihtiyacınızı karşılıyor. Yalnız daha yeni model için değiştirmeyin.`};
    const requiredWh=finite(data.requiredWh)&&n(data.requiredWh)>0?n(data.requiredWh):0;
    if(requiredWh>0&&wh>=requiredWh)return {code:'capacity_ok',commerce:false,title:'Enerji ihtiyacı karşılanıyor — satın alma gerekmez',tone:'ok',summary:`${wh} Wh etiket enerjisi, girdiğiniz ${round(requiredWh,1)} Wh seyahat ihtiyacını karşılıyor. Gerçek kullanılabilir enerji için mevcut USB-C uygunluk aracını kullanın.`};
    const confirmations=Boolean(data.confirmNeed&&data.confirmLabel&&data.confirmAffiliate);
    if(requiredWh>wh&&confirmations)return {code:'qualified',commerce:true,title:'Yalnız doğrulanmış eksik için ürün sınıfı açıldı',tone:'warn',summary:`Mevcut ${wh} Wh, girdiğiniz ${round(requiredWh,1)} Wh ihtiyacın altında. Havayolu sınırını aşmayan, tam Wh etiketi ve USB-C gereksinimi doğrulanabilen ürünleri karşılaştırın.`};
    if(requiredWh>wh)return {code:'need_unconfirmed',commerce:false,title:'Enerji açığı var; ticari geçiş henüz açılmadı',tone:'warn',summary:'Önce mevcut ürünün gerçekten yetersiz olduğunu, tam Wh/USB-C etiketini ve satış ortaklığı bilgisini üç ayrı onayla doğrulayın.'};
    return {code:'plan_first',commerce:false,title:'Önce gerçek seyahat enerji ihtiyacını hesaplayın',tone:'warn',summary:'Yeni powerbank seçmeden önce telefon, tablet veya dizüstünün Wh ihtiyacını ve USB-C PD gücünü mevcut powerbank uygunluk aracıyla belirleyin.'};
  }
  function report(data){return {route:ROUTE,generatedAt:new Date().toISOString(),energyWh:energyWh(data),decision:decide(data),personalData:false,officialApproval:false};}
  function calendar(days=7){
    const start=new Date(Date.now()+Math.max(1,n(days)||7)*86400000);
    const end=new Date(start.getTime()+30*60000);
    const stamp=(date)=>date.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z');
    return ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Powerbank Flight Check//TR','BEGIN:VEVENT',`UID:powerbank-flight-${Date.now()}@alo186.com`,`DTSTAMP:${stamp(new Date())}`,`DTSTART:${stamp(start)}`,`DTEND:${stamp(end)}`,'SUMMARY:Powerbank uçuş ve Wh kontrolü','DESCRIPTION:Havayolunun güncel Wh/adet kuralını, batarya fiziksel durumunu, kabin taşımasını, terminal korumasını ve USB-C ihtiyacını yeniden doğrulayın.','END:VEVENT','END:VCALENDAR'].join('\r\n');
  }
  function download(name,text,type){const blob=new Blob([text],{type});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),0);}
  function read(doc){
    const value=(id)=>doc.getElementById(id)?.value;
    const checked=(id)=>Boolean(doc.getElementById(id)?.checked);
    return {kind:value('kind'),energyMode:value('energyMode'),wh:value('wh'),mah:value('mah'),voltage:value('voltage'),airlineMaxWh:value('airlineMaxWh'),airlineMaxQty:value('airlineMaxQty'),quantity:value('quantity'),requiredWh:value('requiredWh'),airlineChecked:checked('airlineChecked'),cabinOnly:checked('cabinOnly'),terminalProtected:checked('terminalProtected'),planUseOnBoard:checked('planUseOnBoard'),unsafeBattery:checked('unsafeBattery'),existingSuitable:checked('existingSuitable'),confirmNeed:checked('confirmNeed'),confirmLabel:checked('confirmLabel'),confirmAffiliate:checked('confirmAffiliate')};
  }
  function mount(doc){
    const form=doc.getElementById('flightForm');if(!form)return;
    const mode=doc.getElementById('energyMode');
    const syncMode=()=>{doc.getElementById('whField').classList.toggle('hidden',mode.value!=='wh');doc.getElementById('mahFields').classList.toggle('hidden',mode.value!=='mah');};
    mode.addEventListener('change',syncMode);syncMode();
    let last=null;
    form.addEventListener('submit',(event)=>{event.preventDefault();const data=read(doc);const decision=decide(data);last=report(data);const result=doc.getElementById('result');result.className=`result ${decision.tone}`;result.innerHTML=`<h2>${decision.title}</h2><p>${decision.summary}</p><div class="metrics"><div class="metric"><span>Etiket enerjisi</span><strong>${Number.isFinite(energyWh(data))?energyWh(data)+' Wh':'—'}</strong></div><div class="metric"><span>Havayolu sınırı</span><strong>${data.airlineMaxWh||'—'} Wh</strong></div><div class="metric"><span>Adet</span><strong>${data.quantity||'—'} / ${data.airlineMaxQty||'—'}</strong></div><div class="metric"><span>Ticari yol</span><strong>${decision.commerce?'Açık':'Kapalı'}</strong></div></div>`;result.scrollIntoView({behavior:'smooth',block:'start'});doc.getElementById('affiliate').classList.toggle('hidden',!decision.commerce);});
    doc.getElementById('exportJson')?.addEventListener('click',()=>{const data=last||report(read(doc));download('alo186-powerbank-ucus-kontrolu.json',JSON.stringify(data,null,2),'application/json');});
    doc.getElementById('calendar')?.addEventListener('click',()=>download('alo186-powerbank-ucus-kontrolu.ics',calendar(7),'text/calendar'));
  }
  return {ROUTE,energyWh,decide,report,calendar,mount};
});
