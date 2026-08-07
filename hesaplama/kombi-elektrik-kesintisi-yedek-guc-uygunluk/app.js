(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186BoilerBackup=api;
  if(root&&root.document)api.init(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const RESERVE=1.25;
  const SURGE_RESERVE=1.15;
  const BATTERY_EFF=0.85;
  const USABLE=0.80;
  const ENERGY_RESERVE=1.15;
  const DEFAULT_PF=0.85;
  const DEFAULT_LOAD_FACTOR=70;
  const ROUTE='/hesaplama/kombi-elektrik-kesintisi-yedek-guc-uygunluk/';

  const PRODUCT_LINKS={
    ups:{label:'UPS ürün sınıfını teknik minimumla aç',href:'../../akilli-urun-secimi?kategori=mini_ups'},
    power_station:{label:'Power station ürün sınıfını teknik minimumla aç',href:'../../akilli-urun-secimi?kategori=power_station'}
  };
  const TOOL_LINKS={
    ups:{label:'UPS VA ve topoloji testini aç',href:'../ups-va-topoloji-uygunluk/'},
    runtime:{label:'UPS çalışma süresi hesabını aç',href:'../ups-suresi/'},
    power_station:{label:'Power station kapasite ve EPS testini aç',href:'../power-station-kapasite-eps-uygunluk/'},
    compare:{label:'Yedek güç çözüm seçiciyi aç',href:'../yedek-guc-cozum-secici/'},
    handoff:{label:'Elektrikçi iş emri özeti oluştur',href:'../elektrikci-is-emri-ozeti/'}
  };

  const number=(value)=>{
    const parsed=Number(value);
    return Number.isFinite(parsed)?parsed:null;
  };
  const roundUp=(value,step=10)=>Math.ceil(value/step)*step;

  function deriveLoad(input){
    const labelW=number(input.labelW);
    if(labelW&&labelW>0)return {baseW:labelW,source:'label_w'};
    const voltage=number(input.voltage);
    const current=number(input.ratedCurrent);
    const pf=number(input.powerFactor)||DEFAULT_PF;
    if(voltage&&current&&pf>0)return {baseW:voltage*current*pf,source:'va_pf'};
    return {baseW:null,source:'missing'};
  }

  function sourceAssessment(input,requirements){
    if(input.sourceStatus!=='existing')return {status:'missing',reasons:['Mevcut kaynak bilgisi girilmedi.']};
    const reasons=[];
    const continuous=number(input.sourceContinuousW);
    const surge=number(input.sourceSurgeW);
    const wh=number(input.sourceWh);
    if(!continuous||continuous<requirements.continuousW)reasons.push(`Sürekli güç en az ${requirements.continuousW} W olmalı.`);
    if(!surge||surge<requirements.surgeW)reasons.push(`Tepe güç en az ${requirements.surgeW} W olmalı.`);
    if(!wh||wh<requirements.energyWh)reasons.push(`Nominal enerji en az ${requirements.energyWh} Wh olmalı.`);
    if(input.waveform!=='pure')reasons.push('Saf sinüs çıkış doğrulanmadı.');
    if(input.outputSpec!=='confirmed')reasons.push('230 V / 50 Hz çıkış ve cihaz üretici uygunluğu doğrulanmadı.');
    if(input.startTest!=='success')reasons.push('Kontrollü gerçek başlatma ve alev kararlılığı testi başarılı değil.');
    return {status:reasons.length?'insufficient':'sufficient',reasons};
  }

  function calculate(raw={}){
    const input={
      emergencyGas:Boolean(raw.emergencyGas),
      electricalHazard:Boolean(raw.electricalHazard),
      scenario:raw.scenario||'planning',
      applianceType:raw.applianceType||'unknown',
      connection:raw.connection||'unknown',
      gasAvailable:raw.gasAvailable||'unknown',
      lockout:raw.lockout||'no',
      manufacturerApproval:raw.manufacturerApproval||'unknown',
      transferNeed:raw.transferNeed||'short_break_ok',
      labelW:raw.labelW,
      voltage:raw.voltage,
      ratedCurrent:raw.ratedCurrent,
      powerFactor:raw.powerFactor,
      startupW:raw.startupW,
      otherLoadW:raw.otherLoadW,
      loadFactorPct:raw.loadFactorPct,
      targetHours:raw.targetHours,
      sourceStatus:raw.sourceStatus||'none',
      sourceContinuousW:raw.sourceContinuousW,
      sourceSurgeW:raw.sourceSurgeW,
      sourceWh:raw.sourceWh,
      waveform:raw.waveform||'unknown',
      outputSpec:raw.outputSpec||'unknown',
      startTest:raw.startTest||'untested'
    };

    const result={
      route:ROUTE,
      status:'needs_evidence',
      title:'Önce cihaz ve üretici kanıtını tamamlayın.',
      summary:'Kombi için yedek güç seçimi yalnız watt değerine göre yapılmaz.',
      commerceAllowed:false,
      affiliateDisclosure:'Ürün merkezindeki mağaza bağlantıları Amazon satış ortaklığı bağlantılarıdır. ALO186 ürün satıcısı değildir.',
      officialDisclaimer:'ALO186 doğal gaz dağıtım şirketi, EDAŞ, üretici, yetkili servis veya kamu kurumu değildir.',
      productCategory:null,
      productLink:null,
      toolLinks:[],
      requirements:null,
      source:null,
      actions:[],
      reasons:[]
    };

    if(input.emergencyGas){
      result.status='emergency_gas';
      result.title='Doğal gaz acil durumu: elektrikli yedek güç denemeyin.';
      result.summary='Gaz kokusu, CO alarmı, baş dönmesi veya şüpheli yanma varsa anahtar, priz ve cihaz kullanmayın; güvenli alana çıkın. Doğal gaz acil hattı 187’yi, can güvenliği riski varsa 112’yi arayın.';
      result.actions=['Kıvılcım oluşturabilecek anahtar veya fişe dokunmayın.','Güvenli alana çıkın ve 187 doğal gaz acil hattını arayın.','Baş dönmesi, bayılma, yangın veya can güvenliği riski varsa 112’yi arayın.'];
      result.reasons=['Gaz ve karbonmonoksit riski ticari yolları kapatır.'];
      return result;
    }
    if(input.electricalHazard){
      result.status='emergency_electrical';
      result.title='Elektriksel tehlike: cihazı veya yedek kaynağı çalıştırmayın.';
      result.summary='Duman, kıvılcım, erime, su teması, hasarlı kablo veya elektrik çarpması riski varsa enerjiyi güvenli biçimde kestirin ve uzman desteği alın.';
      result.actions=['Enerjili bölüme yaklaşmayın.','Yangın veya elektrik çarpması riski varsa 112’yi arayın.','Kombi, priz ve yedek kaynağı yetkili servis/elektrikçi kontrolü olmadan tekrar çalıştırmayın.'];
      result.reasons=['Elektriksel tehlike ticari yolları kapatır.'];
      return result;
    }
    if(input.gasAvailable==='no'){
      result.status='no_electrical_solution';
      result.title='Gaz beslemesi yoksa elektrikli yedek kaynak kombiyi çalıştırmaz.';
      result.summary='Önce doğal gaz dağıtım şirketinin resmî kanalı veya 187 üzerinden gaz beslemesini doğrulayın. Elektrik ürünü satın almak bu sorunu çözmez.';
      result.actions=['Gaz vanasına veya tesisata müdahale etmeyin.','Gaz beslemesini resmî dağıtım şirketi kanalından doğrulayın.','Gaz geldiğinde üretici yeniden başlatma adımlarını izleyin.'];
      result.reasons=['Sorun elektrik kapasitesi değil, gaz beslemesidir.'];
      return result;
    }
    if(input.lockout==='yes'){
      result.status='service_required';
      result.title='Arıza kodu veya kilitlenme varsa önce yetkili servis.';
      result.summary='Yedek güç cihaz arızasını, düşük su basıncını, baca/alev sorununu veya sensör hatasını gidermez. Reset işlemini tekrarlamayın.';
      result.actions=['Arıza kodunu not edin.','Kullanım kılavuzundaki kullanıcıya açık tek kontrolü uygulayın.','Sorun sürerse yetkili servis çağırın; ürün satın almayın.'];
      result.reasons=['Arıza kodu elektrik kapasitesi eksikliği olarak kabul edilmez.'];
      return result;
    }
    if(['electric_boiler','heat_pump','commercial'].includes(input.applianceType)){
      result.status='professional';
      result.title='Bu yük tüketici tipi UPS kısa listesine uygun değil.';
      result.summary='Elektrikli kombi, ısı pompası ve ticari ısıtma sistemlerinde yüksek güç, kalkış, sabit tesisat, koruma ve transfer düzeni proje bazında değerlendirilmelidir.';
      result.actions=['Etiket güç/akım, faz ve koruma değerlerini kaydedin.','Yetkili servis ve elektrik mühendisiyle yedek güç projesi hazırlayın.','Prizden prize geri besleme veya geçici kablo kullanmayın.'];
      result.toolLinks=[TOOL_LINKS.handoff,TOOL_LINKS.compare];
      result.reasons=['Yük sınıfı profesyonel projelendirme gerektirir.'];
      return result;
    }
    if(input.applianceType!=='gas_boiler'){
      result.reasons.push('Cihaz türü doğal gazlı konut kombisi olarak doğrulanmadı.');
    }
    if(input.connection!=='plug'){
      result.reasons.push('Fişli, kullanıcıya açık bağlantı doğrulanmadı; sabit veya bilinmeyen bağlantı profesyonel inceleme gerektirir.');
    }
    if(input.manufacturerApproval!=='yes'){
      result.reasons.push('Üretici kılavuzu veya yetkili servis haricî yedek kaynak kullanımını doğrulamadı.');
    }
    const derived=deriveLoad(input);
    if(!derived.baseW)result.reasons.push('Etiket wattı veya gerilim-akım-güç faktörü bilgisi eksik.');
    const targetHours=number(input.targetHours);
    if(!targetHours||targetHours<=0)result.reasons.push('Hedef çalışma süresi girilmedi.');
    if(result.reasons.length){
      result.status=input.connection==='fixed'?'professional':'needs_evidence';
      result.title=input.connection==='fixed'?'Sabit bağlantıda profesyonel transfer incelemesi gerekir.':'Üretici, bağlantı ve etiket kanıtını tamamlayın.';
      result.summary='Kombi elektronik kartı, fanı, pompası ve alev algılama düzeni modelden modele değişir. Nötr-toprak referansı, saf sinüs ve transfer davranışı doğrulanmadan ürün yolu açılmaz.';
      result.actions=['Kombi tam modelini ve kullanım kılavuzunu bulun.','Etiket W/A değerini ve bağlantı biçimini kaydedin.','Yetkili servisten UPS/EPS, saf sinüs ve nötr-toprak koşulunu yazılı olarak doğrulayın.'];
      result.toolLinks=[TOOL_LINKS.handoff];
      return result;
    }

    const baseW=derived.baseW;
    const otherLoadW=Math.max(0,number(input.otherLoadW)||0);
    const loadFactor=Math.min(100,Math.max(20,number(input.loadFactorPct)||DEFAULT_LOAD_FACTOR))/100;
    const startupInput=number(input.startupW);
    const estimatedStartup=startupInput&&startupInput>0?startupInput:baseW*2;
    const continuousW=roundUp((baseW+otherLoadW)*RESERVE,10);
    const surgeW=roundUp((estimatedStartup+otherLoadW)*SURGE_RESERVE,10);
    const averageW=(baseW*loadFactor)+otherLoadW;
    const energyWh=roundUp((averageW*targetHours/(BATTERY_EFF*USABLE))*ENERGY_RESERVE,10);
    const requirements={
      baseW:roundUp(baseW,1),
      continuousW,
      surgeW,
      energyWh,
      targetHours,
      loadFactorPct:Math.round(loadFactor*100),
      startupSource:startupInput?'manufacturer_or_measured':'conservative_default_2x',
      calculationNote:'Planlama değeridir; gerçek runtime, cihaz döngüsü, batarya sıcaklığı, yaş ve inverter verimiyle değişir.'
    };
    result.requirements=requirements;
    result.source=sourceAssessment(input,requirements);

    if(result.source.status==='sufficient'){
      result.status='no_buy';
      result.title='Mevcut kaynak teknik eşikleri karşılıyor: yeni ürün almayın.';
      result.summary='Sürekli W, tepe W, Wh, saf sinüs, 230 V/50 Hz, üretici uygunluğu ve kontrollü gerçek test birlikte yeterli.';
      result.actions=['90 gün içinde kontrollü kesinti testini yineleyin.','Akü/batarya sağlığını ve kablo ısınmasını gözleyin.','Kombi bakımından sonra alev kararlılığı ve hata kodu oluşmadığını yeniden doğrulayın.'];
      result.toolLinks=[TOOL_LINKS.runtime];
      return result;
    }

    if(input.scenario==='active'){
      result.status='active_event';
      result.title='Aktif kesintide ürün teslimatını anlık çözüm saymayın.';
      result.summary='Kombiyi uygunsuz kaynakla denemek yerine güvenli kapanma ve donma riskine karşı üretici talimatını uygulayın. Planlama ve satın alma kesinti sonrasında yapılmalıdır.';
      result.actions=['Kombiyi tekrarlı açıp kapatmayın.','Soğuk hava ve donma riski için üretici kılavuzundaki elektrik kesintisi adımlarını izleyin.','Elektrik geri geldiğinde kontrollü yeniden başlatma yapın; hata varsa servis çağırın.'];
      result.reasons=result.source.reasons;
      result.toolLinks=[TOOL_LINKS.handoff];
      return result;
    }

    if(targetHours>4||baseW+otherLoadW>500){
      result.status='professional';
      result.title='Uzun süre veya yüksek yük için proje bazlı çözüm gerekir.';
      result.summary='Dört saati aşan ısıtma sürekliliği veya 500 W üzeri eşzamanlı yükte batarya, jeneratör, transfer ve yakıt/ventilasyon birlikte ele alınmalıdır.';
      result.actions=['Kritik yükleri kombi, pompa ve kontrol devreleri olarak ayırın.','Yük profili ve hedef süreyi elektrik mühendisiyle doğrulayın.','Sabit tesisata geri besleme yapmayın.'];
      result.reasons=result.source.reasons;
      result.toolLinks=[TOOL_LINKS.compare,TOOL_LINKS.handoff];
      return result;
    }

    const category=input.transferNeed==='no_break'?'ups':'power_station';
    result.status='qualified_gap';
    result.title=category==='ups'?'Doğrulanmış teknik açık: UPS sınıfını karşılaştırın.':'Doğrulanmış teknik açık: power station sınıfını karşılaştırın.';
    result.summary=category==='ups'
      ? 'Kısa transfer gereksiniminde üretici uyumu, saf sinüs, nötr-toprak davranışı, W/VA ve runtime birlikte doğrulanmalıdır.'
      : 'Kısa kesintiyi tolere eden kullanımda sürekli W, tepe W, Wh ve EPS geçiş süresi birlikte doğrulanmalıdır.';
    result.commerceAllowed=true;
    result.productCategory=category;
    result.productLink=PRODUCT_LINKS[category];
    result.actions=['Önce hesaplanan sürekli W, tepe W ve Wh değerlerini ürün teknik sayfasında doğrulayın.','Tek port/toplam güç gibi pazarlama değerlerini değil, AC sürekli çıkış ve gerçek runtime tablosunu kullanın.','Satış ortaklığı bağlantısına yalnız gerçek eksik ve üretici uygunluğu doğrulandıktan sonra ilerleyin.'];
    result.reasons=result.source.reasons;
    result.toolLinks=category==='ups'?[TOOL_LINKS.ups,TOOL_LINKS.runtime]:[TOOL_LINKS.power_station,TOOL_LINKS.compare];
    return result;
  }

  function buildIcs(result,now=new Date()){
    const start=new Date(now.getTime()+90*24*60*60*1000);
    const pad=(value)=>String(value).padStart(2,'0');
    const stamp=(date)=>`${date.getUTCFullYear()}${pad(date.getUTCMonth()+1)}${pad(date.getUTCDate())}T${pad(date.getUTCHours())}${pad(date.getUTCMinutes())}00Z`;
    const summary='Kombi yedek güç ve güvenlik yeniden testi';
    const description=`ALO186 teknik kontrolü: ${result.status}. Etiket W/A, üretici uygunluğu, saf sinüs, 230 V/50 Hz, nötr-toprak koşulu, gerçek başlatma ve batarya sağlığını yeniden doğrulayın. Fiyat veya kampanya kontrolü değildir.`;
    return ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Boiler Backup Retest//TR','BEGIN:VEVENT',`UID:${Date.now()}-boiler@alo186.com`,`DTSTAMP:${stamp(now)}`,`DTSTART:${stamp(start)}`,`SUMMARY:${summary}`,`DESCRIPTION:${description.replace(/\n/g,' ')}`,'DURATION:PT30M','END:VEVENT','END:VCALENDAR'].join('\r\n');
  }

  function download(name,content,type){
    const blob=new Blob([content],{type});
    const url=URL.createObjectURL(blob);
    const link=document.createElement('a');
    link.href=url;link.download=name;link.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }

  function collect(document){
    const get=(id)=>document.getElementById(id);
    return {
      emergencyGas:get('emergencyGas').checked,
      electricalHazard:get('electricalHazard').checked,
      scenario:get('scenario').value,
      applianceType:get('applianceType').value,
      connection:get('connection').value,
      gasAvailable:get('gasAvailable').value,
      lockout:get('lockout').value,
      manufacturerApproval:get('manufacturerApproval').value,
      transferNeed:get('transferNeed').value,
      labelW:get('labelW').value,
      voltage:get('voltage').value,
      ratedCurrent:get('ratedCurrent').value,
      powerFactor:get('powerFactor').value,
      startupW:get('startupW').value,
      otherLoadW:get('otherLoadW').value,
      loadFactorPct:get('loadFactorPct').value,
      targetHours:get('targetHours').value,
      sourceStatus:get('sourceStatus').value,
      sourceContinuousW:get('sourceContinuousW').value,
      sourceSurgeW:get('sourceSurgeW').value,
      sourceWh:get('sourceWh').value,
      waveform:get('waveform').value,
      outputSpec:get('outputSpec').value,
      startTest:get('startTest').value
    };
  }

  function render(document,result){
    const output=document.getElementById('result');
    output.classList.remove('hidden');
    output.dataset.status=result.status;
    document.getElementById('resultTitle').textContent=result.title;
    document.getElementById('resultSummary').textContent=result.summary;
    const metrics=document.getElementById('metrics');
    metrics.innerHTML=result.requirements?`<div><small>Planlama sürekli gücü</small><strong>${result.requirements.continuousW} W</strong></div><div><small>Planlama tepe gücü</small><strong>${result.requirements.surgeW} W</strong></div><div><small>Planlama nominal enerjisi</small><strong>${result.requirements.energyWh} Wh</strong></div>`:'';
    document.getElementById('actions').innerHTML=result.actions.map((item)=>`<li>${item}</li>`).join('');
    document.getElementById('reasons').innerHTML=result.reasons.length?`<h3>Neden?</h3><ul>${result.reasons.map((item)=>`<li>${item}</li>`).join('')}</ul>`:'';
    const links=document.getElementById('links');
    links.innerHTML='';
    for(const item of result.toolLinks||[]){
      const link=document.createElement('a');link.className='btn secondary';link.href=item.href;link.textContent=item.label;links.appendChild(link);
    }
    const commerce=document.getElementById('commerce');
    commerce.classList.toggle('hidden',!result.commerceAllowed);
    const productLink=document.getElementById('productLink');
    if(result.commerceAllowed&&result.productLink){productLink.href=result.productLink.href;productLink.textContent=result.productLink.label;productLink.setAttribute('aria-disabled','true');}
    commerce.querySelectorAll('input[type="checkbox"]').forEach((box)=>{box.checked=false;});
    document.getElementById('disclosure').textContent=result.affiliateDisclosure;
    document.getElementById('officialDisclaimer').textContent=result.officialDisclaimer;
    output.focus();
  }

  function updateCommerceGate(document){
    const productLink=document.getElementById('productLink');
    const checked=[...document.querySelectorAll('#commerce input[type="checkbox"]')].every((box)=>box.checked);
    productLink.setAttribute('aria-disabled',checked?'false':'true');
    productLink.tabIndex=checked?0:-1;
  }

  function init(document){
    const form=document.getElementById('boilerForm');
    if(!form)return;
    let lastResult=null;
    const existingFields=document.getElementById('existingFields');
    const syncExisting=()=>existingFields.classList.toggle('hidden',document.getElementById('sourceStatus').value!=='existing');
    document.getElementById('sourceStatus').addEventListener('change',syncExisting);syncExisting();
    form.addEventListener('submit',(event)=>{event.preventDefault();lastResult=calculate(collect(document));render(document,lastResult);});
    document.getElementById('commerce').addEventListener('change',()=>updateCommerceGate(document));
    document.getElementById('productLink').addEventListener('click',(event)=>{if(event.currentTarget.getAttribute('aria-disabled')!=='false')event.preventDefault();});
    document.getElementById('downloadJson').addEventListener('click',()=>{if(lastResult)download('alo186-kombi-yedek-guc-sonucu.json',JSON.stringify(lastResult,null,2),'application/json');});
    document.getElementById('downloadIcs').addEventListener('click',()=>{if(lastResult)download('alo186-kombi-90-gun-yeniden-test.ics',buildIcs(lastResult),'text/calendar');});
  }

  return {calculate,buildIcs,init};
});
