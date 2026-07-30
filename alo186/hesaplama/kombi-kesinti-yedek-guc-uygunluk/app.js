(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.Alo186BoilerContinuity=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const KEY='alo186-boiler-continuity-v1';
  const TTL=365*86400000;
  const LIMIT=10;
  const ROUTES={
    ups:{id:'ups',title:'UPS VA ve topoloji uygunluğu',description:'Kısa süreli kesinti için gerçek W, yaklaşık VA, saf sinüs ve transfer sınıfını doğrulayın.',href:'../ups-va-topoloji-uygunluk/?kaynak=kombi'},
    powerStation:{id:'powerStation',title:'Power station kapasite ve EPS uygunluğu',description:'Orta süreli hazırlıkta kullanılabilir Wh, sürekli W, EPS geçişi ve nötr-toprak sınırını ayrı test edin.',href:'../power-station-kapasite-eps-uygunluk/?kaynak=kombi'},
    inverter:{id:'inverter',title:'İnverter ve batarya uygunluğu',description:'Uzun süre veya sabit sistemde DC gerilim, akım, BMS, koruma ve profesyonel bağlantıyı projelendirin.',href:'../inverter-uygunluk/?kaynak=kombi'},
    coAlarm:{id:'coAlarm',title:'Karbonmonoksit alarmı ve yerleşim uygunluğu',description:'Gazlı cihaz bulunan konutta alarm standardı, yerleşimi, yaşı ve test durumunu ayrı değerlendirin.',href:'../karbonmonoksit-alarmi-jenerator-guvenligi/?kaynak=kombi'}
  };

  function finiteOrNull(value){
    if(value===null||value===undefined||value==='')return null;
    const number=Number(value);
    return Number.isFinite(number)?number:null;
  }

  function roundUp(value,step){return Math.ceil(value/step)*step;}

  function normalize(input){
    return {
      stage:['preparedness','active','restored'].includes(input.stage)?input.stage:'preparedness',
      boilerType:['gas','electric','heat_pump','unknown'].includes(input.boilerType)?input.boilerType:'unknown',
      connectionType:['plug','fixed','unknown'].includes(input.connectionType)?input.connectionType:'unknown',
      labelW:Math.max(0,Math.min(30000,finiteOrNull(input.labelW)??0)),
      peakW:Math.max(0,Math.min(50000,finiteOrNull(input.peakW)??0)),
      targetHours:Math.max(.25,Math.min(24,finiteOrNull(input.targetHours)??2)),
      manualChecked:Boolean(input.manualChecked),
      grounded:Boolean(input.grounded),
      neutralEarthVerified:Boolean(input.neutralEarthVerified),
      pressureOk:Boolean(input.pressureOk),
      flueOk:Boolean(input.flueOk),
      coAlarm:Boolean(input.coAlarm),
      existingType:['none','ups','power_station','inverter','generator'].includes(input.existingType)?input.existingType:'none',
      existingW:Math.max(0,Math.min(50000,finiteOrNull(input.existingW)??0)),
      existingWh:Math.max(0,Math.min(200000,finiteOrNull(input.existingWh)??0)),
      existingTested:Boolean(input.existingTested),
      gasSmell:Boolean(input.gasSmell),
      coSymptoms:Boolean(input.coSymptoms),
      electricalHazard:Boolean(input.electricalHazard),
      waterLeak:Boolean(input.waterLeak)
    };
  }

  function designFrom(input){
    const assumedPeak=input.peakW>0?input.peakW:input.labelW*2;
    const designW=roundUp(Math.max(input.labelW*1.5,assumedPeak*1.2),50);
    const designVA=roundUp(designW/.7,100);
    const energyWh=roundUp(input.labelW*input.targetHours*1.6,10);
    return {assumedPeak,designW,designVA,energyWh};
  }

  function classify(raw){
    const input=normalize(raw);
    const emergency=input.gasSmell||input.coSymptoms;
    const physicalHazard=input.electricalHazard||input.waterLeak;
    const productNeeds=[];
    const steps=[];

    if(emergency){
      return {input,severity:'bad',state:'emergency',title:'Gaz veya karbonmonoksit riski var; bütün ticari yollar kapalı.',summary:'Elektrik yedeğini, kombiyi veya sigortayı denemeyin. Gaz kokusunda kıvılcım oluşturabilecek anahtar ve cihazları kullanmayın; ortamdan uzaklaşın. CO belirtisi veya alarmında temiz havaya çıkın ve gerektiğinde 112 üzerinden acil yardım alın.',steps:['Kombi, UPS, power station veya jeneratörü çalıştırmaya çalışmayın.','Yetkili doğalgaz acil/servis kanalını güvenli alandan kullanın.','Belirti yaşayan kişileri kapalı alana geri göndermeyin.'],metrics:null,productNeeds:[],noBuy:true,commerceAllowed:false,commerceDeferred:false};
    }

    if(physicalHazard){
      return {input,severity:'bad',state:'stop',title:'Su teması veya elektriksel hasar var; ürünü ve kombiyi enerjilendirmeyin.',summary:'Fiş, priz, kablo, kombi veya yedek güç kaynağına dokunmayın. Güvenle yapılabiliyorsa enerjiyi yetkili kişiyle kestirin; uygun teknik inceleme olmadan yeniden çalıştırmayın.',steps:['Hasarlı veya su temaslı yedek güç ürününü şarj etmeyin.','Uzatma kablosu ya da çoklu prizle geçici çözüm kurmayın.','Yetkili elektrikçi ve kombi servisi birlikte bağlantı güvenliğini doğrulasın.'],metrics:null,productNeeds:[],noBuy:true,commerceAllowed:false,commerceDeferred:false};
    }

    if(input.boilerType==='electric'||input.boilerType==='heat_pump'){
      return {input,severity:'warn',state:'professional',title:'Bu cihaz küçük UPS veya tüketici power station sınıfında değerlendirilmemeli.',summary:'Elektrikli kombi ve ısı pompası kW düzeyinde yük, trifaze besleme, kompresör/kademe kalkışı veya sabit tesisat gerektirebilir. Tüketici tipi ürün rotası kapalıdır; proje düzeyinde güç, kablo, koruma, transfer ve kaynak hesabı gerekir.',steps:['Cihazın elektrik projesini ve tam model teknik verisini alın.','Sürekli güç, en büyük kalkış/kademe, faz ve eşzamanlı yükü ölçün.','Yetkili elektrik mühendisi/servis ile sabit yedek güç çözümünü projelendirin.'],metrics:null,productNeeds:[],noBuy:true,commerceAllowed:false,commerceDeferred:false};
    }

    if(input.boilerType==='unknown'||input.labelW<=0||!input.manualChecked){
      return {input,severity:'warn',state:'evidence',title:'Ürün seçmek için tam model ve elektrik etiketi kanıtı eksik.',summary:'Isıtma kapasitesi kW değeri elektrik tüketimi değildir. Tam model kullanım/servis dokümanı, maksimum elektrik gücü ve harici yedek kaynak sınırı doğrulanmadan VA veya Wh sonucu satış gerekçesine dönüştürülmez.',steps:['Kombi etiketinden veya üretici teknik sayfasından maksimum elektrik gücünü bulun.','Tam model kılavuzunda elektrik bağlantısı ve kesinti sonrası yeniden başlatma koşullarını kontrol edin.','Belirsizliği yeni ürün alarak kapatmayın; önce ücretsiz teknik kanıtı tamamlayın.'],metrics:null,productNeeds:[],noBuy:true,commerceAllowed:false,commerceDeferred:false};
    }

    const metrics=designFrom(input);

    if(input.connectionType!=='plug'||!input.grounded||!input.neutralEarthVerified||!input.pressureOk||!input.flueOk){
      const missing=[];
      if(input.connectionType!=='plug')missing.push('üreticiye uygun fiş/priz bağlantısı');
      if(!input.grounded)missing.push('işlevsel koruma iletkeni');
      if(!input.neutralEarthVerified)missing.push('nötr-toprak ve RCD davranışı');
      if(!input.pressureOk)missing.push('su basıncı/dolaşım');
      if(!input.flueOk)missing.push('baca, hava ve gaz tesisatı');
      return {input,severity:'warn',state:'professional',title:'Bağlantı ve işletme kanıtı tamamlanmadan yedek güç rotası açılmaz.',summary:`Eksik doğrulamalar: ${missing.join(', ')}. Saf sinüs etiketi bu eksikleri gidermez. Sabit bağlantı ve N-PE/RCD davranışı profesyonel inceleme gerektirir.`,steps:['Kombi servisi tam model elektrik bağlantısını doğrulasın.','Yetkili elektrikçi kaynak değişiminde nötr, PE ve RCD davranışını test etsin.','Kombi basıncı, su dolaşımı ve baca/gaz güvenliği uygun değilse yedek enerji vermeyin.'],metrics,productNeeds:[],noBuy:true,commerceAllowed:false,commerceDeferred:false};
    }

    const existingPresent=input.existingType!=='none';
    const existingEnough=existingPresent&&input.existingW>=metrics.designW&&input.existingWh>=metrics.energyWh;
    if(existingPresent&&!input.existingTested){
      return {input,severity:'warn',state:'test_first',title:'Mevcut yedek güç test edilmeden yeni ürün satın almayın.',summary:'Etiket kapasitesi gerçek kombi çevrimini, transfer davranışını veya hedef süreyi garanti etmez. Kontrollü kesinti testi ve güvenli yeniden başlatma sonucu alınmadan mevcut sistemi yetersiz kabul etmeyin.',steps:['Testi gaz/baca/su ve elektrik güvenliği doğrulandıktan sonra yapın.','Kombinin fan, pompa ve ateşleme çevrimlerini gözleyin.','Gerçek çalışma süresi ile kapanma nedenini kaydedin.'],metrics,productNeeds:[],noBuy:true,commerceAllowed:false,commerceDeferred:false};
    }

    if(existingEnough&&input.existingTested){
      return {input,severity:'ok',state:'no_buy',title:'Mevcut çözüm hedef güç ve süreyi karşılıyor; yeni ürün gerekli değildir.',summary:`Kontrollü test, yaklaşık ${metrics.designW} W tasarım gücü ve ${metrics.energyWh} Wh planlama enerjisi hedefini karşılıyor. Bakım ve aylık test döngüsünü sürdürün.`,steps:['Akü/enerji seviyesini ve test tarihini kaydedin.','Kesinti sonrası kontrollü yeniden başlatma adımını hane halkıyla paylaşın.','Kapasite düşüşü görülmedikçe sırf daha yüksek VA etiketi için ürün değiştirmeyin.'],metrics,productNeeds:[],noBuy:true,commerceAllowed:false,commerceDeferred:false};
    }

    if(input.stage==='active'){
      return {input,severity:'warn',state:'deferred',title:'Aktif kesintide yeni ürün gelmesini beklemek çözüm değildir.',summary:'Mevcut güvenli yedek güç yoksa kombiyi geçici ve doğrulanmamış kablo, inverter veya jeneratör bağlantısıyla çalıştırmayın. Ürün rotası sonraki kesinti hazırlığına ertelenir.',steps:['Donma veya sağlık riski varsa güvenli alternatif ısınma/konaklama planını değerlendirin.','Elektrik geldiğinde kombiyi üretici talimatıyla kontrollü yeniden başlatın.','Sonraki olay için etiket, süre ve bağlantı kanıtını bu araçta kaydedin.'],metrics,productNeeds:[],noBuy:true,commerceAllowed:false,commerceDeferred:true};
    }

    if(input.targetHours>4||input.labelW>500){
      productNeeds.push('inverter');
      if(!input.coAlarm)productNeeds.push('coAlarm');
      return {input,severity:'warn',state:'professional',title:'Uzun süre veya yüksek yük, sabit sistem/profesyonel tasarım gerektirir.',summary:`Yaklaşık başlangıç hedefi ${metrics.designW} W, ${metrics.designVA} VA ve ${metrics.energyWh} Wh düzeyindedir. Dört saati aşan süre veya 500 W üzeri elektrik etiketi tek tüketici ürünüyle güvenli kabul edilmez.`,steps:['İnverter-batarya veya jeneratör kaynak değişimini projelendirin.','Nötr-toprak, RCD, gaz cihazı ve transfer davranışını birlikte test edin.','CO alarmı, havalandırma ve bakım planını ayrı güvenlik katmanı olarak kurun.'],metrics,productNeeds,noBuy:false,commerceAllowed:true,commerceDeferred:false};
    }

    if(input.targetHours<=1.5)productNeeds.push('ups');
    else productNeeds.push('powerStation');
    if(!input.coAlarm)productNeeds.push('coAlarm');
    steps.push(`Yaklaşık başlangıç alt sınırı ${metrics.designW} W gerçek çıkış ve ${metrics.designVA} VA sınıfıdır.`);
    steps.push(`Hedef süre için yaklaşık ${metrics.energyWh} Wh kullanılabilir enerji planlayın; üretici runtime tablosu ve gerçek test sonucu önceliklidir.`);
    steps.push('Saf sinüs, transfer süresi, soğuk başlatma, N-PE ve RCD davranışını tam model üzerinde doğrulayın.');
    return {input,severity:'ok',state:'qualified',title:'Teknik kanıt tamamlandı; yalnız eksik çözüm sınıfına ilerleyin.',summary:'Bu sonuç belirli bir ürünün çalışma süresini garanti etmez. Ürün merkezinde gerçek W, kullanılabilir Wh, transfer ve bağlantı sınırlarını yeniden kontrol edin.',steps,metrics,productNeeds,noBuy:false,commerceAllowed:true,commerceDeferred:false};
  }

  function prune(records,now=Date.now()){
    return (Array.isArray(records)?records:[]).filter(record=>record&&Number.isFinite(record.createdAt)&&now-record.createdAt<TTL).sort((a,b)=>b.createdAt-a.createdAt).slice(0,LIMIT);
  }

  function readRecords(storage,now=Date.now()){
    try{return prune(JSON.parse(storage.getItem(KEY)||'[]'),now);}catch{return [];}
  }

  function writeRecord(storage,result,now=Date.now()){
    const record={createdAt:now,state:result.state,severity:result.severity,boilerType:result.input.boilerType,labelW:result.input.labelW,targetHours:result.input.targetHours,designW:result.metrics?result.metrics.designW:null,designVA:result.metrics?result.metrics.designVA:null,energyWh:result.metrics?result.metrics.energyWh:null,productNeeds:result.productNeeds,noBuy:result.noBuy};
    const records=prune([record,...readRecords(storage,now)],now);
    storage.setItem(KEY,JSON.stringify(records));
    return records;
  }

  function calendarText(start=new Date()){
    const pad=value=>String(value).padStart(2,'0');
    const stamp=date=>`${date.getUTCFullYear()}${pad(date.getUTCMonth()+1)}${pad(date.getUTCDate())}T${pad(date.getUTCHours())}${pad(date.getUTCMinutes())}00Z`;
    const end=new Date(start.getTime()+30*60000);
    return ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Kombi Kesinti Testi//TR','BEGIN:VEVENT',`UID:alo186-boiler-${start.getTime()}@alo186.com`,`DTSTAMP:${stamp(start)}`,`DTSTART:${stamp(start)}`,`DTEND:${stamp(end)}`,'RRULE:FREQ=MONTHLY;COUNT=12','SUMMARY:Kombi yedek güç ve güvenli yeniden başlatma testi','DESCRIPTION:Etiket W, gerçek çıkış W, kullanılabilir Wh, saf sinüs, transfer, nötr-toprak/RCD, CO alarmı ve kontrollü kombi çevrimini yeniden doğrulayın.','END:VEVENT','END:VCALENDAR'].join('\r\n');
  }

  function mount(doc){
    const form=doc.getElementById('boiler-form');
    if(!form)return;
    const resultEl=doc.getElementById('result');
    const commerceEl=doc.getElementById('commerce');
    const productsEl=doc.getElementById('productNeeds');
    const recordsEl=doc.getElementById('records');
    let lastResult=null;

    const value=id=>doc.getElementById(id).value;
    const checked=id=>doc.getElementById(id).checked;
    function collect(){return {stage:value('stage'),boilerType:value('boilerType'),connectionType:value('connectionType'),labelW:value('labelW'),peakW:value('peakW'),targetHours:value('targetHours'),manualChecked:checked('manualChecked'),grounded:checked('grounded'),neutralEarthVerified:checked('neutralEarthVerified'),pressureOk:checked('pressureOk'),flueOk:checked('flueOk'),coAlarm:checked('coAlarm'),existingType:value('existingType'),existingW:value('existingW'),existingWh:value('existingWh'),existingTested:checked('existingTested'),gasSmell:checked('gasSmell'),coSymptoms:checked('coSymptoms'),electricalHazard:checked('electricalHazard'),waterLeak:checked('waterLeak')};}

    function metricsHtml(metrics){
      if(!metrics)return '';
      return `<div class="grid metrics"><div class="metric"><span>Planlama gerçek gücü</span><strong>${metrics.designW.toLocaleString('tr-TR')} W</strong></div><div class="metric"><span>Yaklaşık VA başlangıcı</span><strong>${metrics.designVA.toLocaleString('tr-TR')} VA</strong></div><div class="metric"><span>Planlama enerjisi</span><strong>${metrics.energyWh.toLocaleString('tr-TR')} Wh</strong></div></div>`;
    }

    function gateReady(){return ['actualMissing','technicalChecked','affiliateAccepted'].every(id=>checked(id));}
    function updateGate(){const ready=gateReady();commerceEl.querySelectorAll('.product-card a').forEach(link=>{link.setAttribute('aria-disabled',ready?'false':'true');link.tabIndex=ready?0:-1;});}

    function renderProducts(needs){
      productsEl.innerHTML=needs.map(id=>{const item=ROUTES[id];return `<article class="product-card"><span class="eyebrow">Teknik uygunluk kapısı</span><h3>${item.title}</h3><p>${item.description}</p><a class="button" href="${item.href}" aria-disabled="true">Uygunluk aracını aç</a></article>`;}).join('');
      commerceEl.querySelectorAll('input').forEach(input=>{input.checked=false;});
      updateGate();
    }

    function render(result){
      lastResult=result;
      const className=result.severity==='bad'?'bad':result.severity==='warn'?'warn':'ok';
      resultEl.innerHTML=`<h2>${result.title}</h2><div class="status ${className}">${result.summary}</div>${metricsHtml(result.metrics)}<ol>${result.steps.map(step=>`<li>${step}</li>`).join('')}</ol>${result.noBuy?'<p class="status ok"><strong>Satın almama sonucu:</strong> Yeni ürün şu anda gerekli veya güvenli kabul edilmedi.</p>':''}`;
      resultEl.classList.remove('hidden');
      commerceEl.classList.toggle('hidden',!result.commerceAllowed||!result.productNeeds.length);
      if(result.commerceAllowed&&result.productNeeds.length)renderProducts(result.productNeeds);
      resultEl.focus();
    }

    function renderRecords(){
      const records=readRecords(root.localStorage);
      recordsEl.innerHTML=records.length?records.map(record=>`<div class="record"><strong>${new Date(record.createdAt).toLocaleDateString('tr-TR')}</strong> · ${record.state} · ${record.labelW||'—'} W · ${record.targetHours} saat · ${record.noBuy?'satın alma yok':'takip gerekli'}</div>`).join(''):'<p class="small">Henüz kayıt yok.</p>';
    }

    form.addEventListener('submit',event=>{event.preventDefault();render(classify(collect()));});
    commerceEl.addEventListener('change',updateGate);
    commerceEl.addEventListener('click',event=>{const link=event.target.closest('a[aria-disabled="true"]');if(link)event.preventDefault();});
    doc.getElementById('save').addEventListener('click',()=>{if(!lastResult)return;writeRecord(root.localStorage,lastResult);renderRecords();});
    doc.getElementById('export').addEventListener('click',()=>{const blob=new Blob([JSON.stringify(readRecords(root.localStorage),null,2)],{type:'application/json'});const link=doc.createElement('a');link.href=URL.createObjectURL(blob);link.download='alo186-kombi-sureklilik-kayitlari.json';link.click();URL.revokeObjectURL(link.href);});
    doc.getElementById('calendar').addEventListener('click',()=>{const blob=new Blob([calendarText(new Date())],{type:'text/calendar'});const link=doc.createElement('a');link.href=URL.createObjectURL(blob);link.download='alo186-kombi-aylik-test.ics';link.click();URL.revokeObjectURL(link.href);});
    renderRecords();
  }

  return {KEY,TTL,LIMIT,ROUTES,normalize,designFrom,classify,prune,readRecords,writeRecord,calendarText,mount};
});
