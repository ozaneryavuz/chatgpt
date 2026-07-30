(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186PumpBackup=api;
  if(root&&root.document)api.init(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const SQRT3=Math.sqrt(3);
  const PF_DEFAULT=0.8;
  const RESERVE=1.25;
  const BATTERY_EFF=0.85;
  const USABLE=0.8;
  const START_MULTIPLIER={direct:6,soft:3,vfd:1.5};
  const STORAGE_KEY='alo186-pump-backup-records-v1';
  const MAX_RECORDS=8;
  const TTL_DAYS=365;
  const REVIEW_DAYS=90;
  const DAY_MS=24*60*60*1000;
  const ROUTE='/hesaplama/hidrofor-pompa-yedek-guc-uygunluk/';

  const CATEGORY_LINKS={
    generator:{label:'Jeneratör ürün sınıfını aç',href:'../../akilli-urun-secimi?kategori=generator'},
    power_station:{label:'Güç istasyonu ürün sınıfını aç',href:'../../akilli-urun-secimi?kategori=power_station'},
    inverter:{label:'İnverter ürün sınıfını aç',href:'../../akilli-urun-secimi?kategori=inverter'}
  };
  const TOOL_LINKS={
    generator:{label:'Jeneratör güç hesabını aç',href:'../jenerator-gucu-secimi/'},
    inverter:{label:'İnverter uygunluk testini aç',href:'../inverter-uygunluk/'},
    power:{label:'Power station uygunluk testini aç',href:'../power-station-kapasite-eps-uygunluk/'},
    handoff:{label:'Elektrikçi iş emri özetini aç',href:'../elektrikci-is-emri-ozeti/'},
    outcome:{label:'Çözüm sonucunu kaydet',href:'../cozum-sonucu/'}
  };

  const n=value=>{
    const raw=String(value??'').trim().replace(',','.');
    if(!raw)return null;
    const parsed=Number(raw);
    return Number.isFinite(parsed)?parsed:null;
  };
  const uniq=values=>[...new Set(values.filter(Boolean))];
  const round=(value,digits=1)=>Number(value.toFixed(digits));
  const safeText=(value,max=180)=>String(value??'').replace(/[<>]/g,'').trim().slice(0,max);

  function base(status,title,summary){
    return {status,title,summary,issues:[],steps:[],metrics:null,commerceCategories:[],toolKeys:[],commerceClosed:true};
  }

  function calculations(input){
    const phase=input.phase==='three'?3:1;
    const voltage=n(input.voltage);
    const current=n(input.ratedCurrent);
    const pf=n(input.powerFactor)??PF_DEFAULT;
    const otherW=n(input.otherLoadW)??0;
    const hours=n(input.targetHours);
    const multiplier=START_MULTIPLIER[input.startMethod]??null;
    if(!voltage||!current||!multiplier||!hours)return null;

    const kva=(phase===3?SQRT3:1)*voltage*current/1000;
    const runningW=kva*pf*1000;
    const startW=runningW*multiplier;
    const totalRunningW=runningW+otherW;
    const requiredContinuousW=totalRunningW*RESERVE;
    const requiredSurgeW=(startW+otherW)*1.15;
    const requiredWh=totalRunningW*hours/BATTERY_EFF/USABLE;

    return {
      phase,voltage,current,pf,mult:multiplier,
      kva:round(kva,2),runningW:round(runningW),startW:round(startW),
      totalRunningW:round(totalRunningW),requiredContinuousW:round(requiredContinuousW),
      requiredSurgeW:round(requiredSurgeW),requiredWh:round(requiredWh),targetHours:round(hours,2)
    };
  }

  function evaluate(input={}){
    if(input.emergency){
      const result=base('emergency','Acil: pompa devresini kullanmayın','Su, duman, kıvılcım, yanık kokusu veya elektrik çarpması riski varken hesap ve ticari yönlendirme yapılmaz.');
      result.issues=['Su ile elektrik ekipmanı aynı alandaysa enerjiyi güvenli biçimde kesmeden yaklaşmayın.'];
      result.steps=['Güvenliyse ana enerjiyi kesin; suya veya ıslak ekipmana dokunmayın.','Yangın, yaralanma veya elektrik çarpması riski varsa 112’yi arayın.'];
      return result;
    }

    if(input.environment==='wet'&&input.protection!=='rated'){
      const result=base('stop','Islak ortam koruması doğrulanmadan kullanmayın','Pompa gövdesi, fiş, priz, uzatma kablosu ve yedek kaynak ıslak ortam için uygun değilse elektrik çarpması riski oluşur.');
      result.issues=['Üretici ortam/IP sınırı veya kaçak akım koruması doğrulanmadı.'];
      result.steps=['Kuru ve güvenli bağlantı noktası sağlayın; üretici talimatını ve koruma düzenini doğrulayın.'];
      return result;
    }

    if(['fire','sewage_hazard'].includes(input.pumpType)){
      const result=base('professional','Kritik pompa sistemi profesyonel tasarım gerektirir','Yangın pompası veya tehlikeli ortam atık su pompası tüketici tipi ürün seçimine açılamaz.');
      result.issues=['Kaynak yedekliliği, transfer, koruma, alarm ve periyodik test birlikte projelendirilmelidir.'];
      result.steps=['Yetkili elektrik ve mekanik proje uzmanıyla sistem mimarisini doğrulayın.'];
      result.toolKeys=['handoff'];
      return result;
    }

    const evidence=[];
    const pfInput=n(input.powerFactor);
    const otherInput=n(input.otherLoadW);
    if(!['single','three'].includes(input.phase))evidence.push('Faz bilgisi doğrulanmadı.');
    if(!n(input.voltage)||n(input.voltage)<100||n(input.voltage)>500)evidence.push('Etiket gerilimi 100–500 V aralığında doğrulanmadı.');
    if(!n(input.ratedCurrent)||n(input.ratedCurrent)<=0||n(input.ratedCurrent)>200)evidence.push('Motor etiket akımı doğrulanmadı.');
    if(pfInput!==null&&(pfInput<0.4||pfInput>1))evidence.push('Güç faktörü 0,40–1,00 aralığında olmalıdır.');
    if(otherInput!==null&&(otherInput<0||otherInput>10000))evidence.push('Diğer eşzamanlı yük 0–10.000 W aralığında olmalıdır.');
    if(!START_MULTIPLIER[input.startMethod])evidence.push('Kalkış yöntemi bilinmiyor.');
    if(!n(input.targetHours)||n(input.targetHours)<=0||n(input.targetHours)>48)evidence.push('Hedef çalışma süresi 0–48 saat aralığında doğrulanmadı.');
    if(input.connection==='unknown')evidence.push('Pompanın fişli mi sabit bağlı mı olduğu bilinmiyor.');
    if(input.sourceStatus==='existing'&&input.sourceType==='auto')evidence.push('Mevcut kaynağın sınıfını doğrulayın: jeneratör, power station veya inverter seçin.');
    if(evidence.length){
      const result=base('evidence_required','Önce motor etiketini ve bağlantıyı doğrulayın','Faz, volt, amper, kalkış yöntemi ve süre bilinmeden jeneratör veya inverter seçilmez.');
      result.issues=evidence;
      result.steps=['Motor etiketindeki V, A, faz ve varsa cosφ değerini kaydedin.','Kontaktör, soft starter veya sürücü olup olmadığını doğrulayın.'];
      result.toolKeys=['handoff'];
      return result;
    }

    const metrics=calculations(input);
    if(!metrics)return base('evidence_required','Hesap için gerekli veri eksik','Sayısal bilgiler tamamlanmadan ürün yolu açılmaz.');

    const fixed=input.connection==='fixed';
    const highPower=metrics.runningW>1500;
    const three=input.phase==='three';
    const borehole=input.pumpType==='borehole';
    if(fixed||three||highPower||borehole){
      const result=base('professional','Pompa ve yedek kaynak koordinasyonu uzman doğrulaması gerektirir','Sabit bağlı, trifaze, kuyu tipi veya yüksek güçlü pompalarda yalnız watt hesabı yeterli değildir.');
      result.metrics=metrics;
      result.issues=uniq([
        fixed&&'Sabit tesisat bağlantısı transfer ve koruma koordinasyonu gerektirir.',
        three&&'Trifaze motorda faz sırası, dengesizlik ve jeneratör gerilim regülasyonu doğrulanmalıdır.',
        borehole&&'Kuyu pompasında kablo uzunluğu, gerilim düşümü ve kuru çalışma koruması değerlendirilmelidir.',
        highPower&&'Motor gücü tüketici tipi taşınabilir kaynak sınırını aşıyor.'
      ]);
      result.steps=['Yetkili elektrik uzmanına etiket, kablo, koruma, kalkış ve transfer verilerini doğrulatın.','Jeneratör veya sürücüyü yalnız sürekli güç değil kalkış ve kısa devre davranışıyla seçin.'];
      result.toolKeys=['generator','inverter','handoff'];
      return result;
    }

    if(input.sourceStatus==='existing'){
      const continuous=n(input.sourceContinuousW);
      const surge=n(input.sourceSurgeW);
      const wh=n(input.sourceWh);
      const batteryNeeded=['power_station','inverter'].includes(input.sourceType);
      const missing=continuous===null||continuous<=0||surge===null||surge<=0||(batteryNeeded&&(wh===null||wh<=0));
      if(missing){
        const result=base('evidence_required','Mevcut kaynağın sürekli, tepe ve enerji değerini doğrulayın','Sadece model adı veya maksimum pazarlama gücü yeterli değildir.');
        result.metrics=metrics;
        result.issues=['Kaynağın pozitif sürekli W, tepe W ve bataryalıysa Wh değeri eksik.'];
        result.steps=['Üretici teknik sayfasındaki aynı model ve çıkış koşullarını doğrulayın.'];
        return result;
      }
      const continuousOk=continuous>=metrics.requiredContinuousW;
      const surgeOk=surge>=metrics.requiredSurgeW;
      const whOk=!batteryNeeded||wh>=metrics.requiredWh;
      if(continuousOk&&surgeOk&&whOk){
        const generator=input.sourceType==='generator';
        const result=base('no_buy','Mevcut kaynak güç eşiklerini karşılıyorsa yeni ürün almayın',generator?'Girilen etiket değerlerine göre mevcut jeneratör sürekli ve kalkış gücü eşiklerini karşılıyor; hedef süre için yakıt ve üretici çalışma süresini ayrıca doğrulayın.':'Girilen etiket değerlerine göre mevcut bataryalı kaynak sürekli güç, kalkış ve hedef enerji eşiklerini karşılıyor.');
        result.metrics=metrics;
        result.steps=generator?['Pompayı gerçek yük altında kontrollü başlatma testiyle doğrulayın.','Hedef süre için yakıt kapasitesi, yük oranı, havalandırma ve üretici çalışma süresini doğrulayın.']:['Pompayı gerçek yük altında kontrollü başlatma ve süre testiyle doğrulayın.','Kablo, priz, RCD ve susuz çalışma korumasını periyodik kontrol edin.'];
        result.toolKeys=['outcome'];
        return result;
      }
    }

    let category='generator';
    if(input.sourceType==='power_station'||(input.sourceType==='auto'&&metrics.requiredSurgeW<=2200&&metrics.requiredWh<=2000&&metrics.targetHours<=4))category='power_station';
    else if(input.sourceType==='inverter')category='inverter';

    const result=base('conditional_purchase','Kaynak yetersiz veya eksik; yalnız hesaplanan sınıfa ilerleyin','Bu sonuç belirli marka/model onayı değildir. Sürekli güç, kalkış gücü ve enerji kapasitesi birlikte doğrulanmalıdır.');
    result.metrics=metrics;
    result.issues=[
      `En az yaklaşık ${metrics.requiredContinuousW} W sürekli güç gerekir.`,
      `Kalkış için yaklaşık ${metrics.requiredSurgeW} W kısa süreli kapasite gerekir.`,
      ...(['power_station','inverter'].includes(category)?[`Hedef süre için yaklaşık ${metrics.requiredWh} Wh nominal enerji gerekir.`]:[])
    ];
    result.steps=['Üretici sayfasında sürekli güç ile tepe gücü ayırın.','Motor kalkışına izin verilen süreyi ve dalga biçimini doğrulayın.','Fiş, kablo, RCD ve kuru çalışma korumasını ürün seçiminden ayrı değerlendirin.'];
    result.commerceCategories=[category];
    result.toolKeys=[category==='generator'?'generator':category==='inverter'?'inverter':'power'];
    result.commerceClosed=false;
    return result;
  }

  function normalizeRecord(value={},now=new Date()){
    const createdAt=Number.isFinite(Date.parse(value.createdAt))?new Date(value.createdAt):new Date(now);
    const metrics=value.metrics&&typeof value.metrics==='object'?value.metrics:{};
    const input=value.input&&typeof value.input==='object'?value.input:{};
    return {
      id:safeText(value.id||`pump-${createdAt.getTime()}-${Math.random().toString(36).slice(2,8)}`,80),
      createdAt:createdAt.toISOString(),
      reviewAt:new Date(createdAt.getTime()+REVIEW_DAYS*DAY_MS).toISOString(),
      expiresAt:new Date(createdAt.getTime()+TTL_DAYS*DAY_MS).toISOString(),
      status:safeText(value.status,40),
      title:safeText(value.title,180),
      metrics:{
        runningW:n(metrics.runningW),requiredContinuousW:n(metrics.requiredContinuousW),
        requiredSurgeW:n(metrics.requiredSurgeW),requiredWh:n(metrics.requiredWh),targetHours:n(metrics.targetHours)
      },
      input:{
        pumpType:safeText(input.pumpType,40),phase:safeText(input.phase,20),voltage:n(input.voltage),
        ratedCurrent:n(input.ratedCurrent),startMethod:safeText(input.startMethod,20),
        connection:safeText(input.connection,20),sourceType:safeText(input.sourceType,30)
      }
    };
  }

  function purgeRecords(records,now=new Date()){
    const nowMs=new Date(now).getTime();
    return (Array.isArray(records)?records:[])
      .map(record=>normalizeRecord(record,new Date(record.createdAt||now)))
      .filter(record=>Date.parse(record.expiresAt)>nowMs)
      .sort((a,b)=>Date.parse(b.createdAt)-Date.parse(a.createdAt))
      .slice(0,MAX_RECORDS);
  }

  function loadStoredRecords(storage,now=new Date()){
    if(!storage||typeof storage.getItem!=='function')return [];
    let parsed=[];
    try{parsed=JSON.parse(storage.getItem(STORAGE_KEY)||'[]');}
    catch(error){parsed=[];}
    const records=purgeRecords(parsed,now);
    try{
      if(records.length)storage.setItem(STORAGE_KEY,JSON.stringify(records));
      else storage.removeItem(STORAGE_KEY);
    }catch(error){}
    return records;
  }

  function exportPayload(records,now=new Date()){
    return {
      schemaVersion:1,
      generatedAt:new Date(now).toISOString(),
      route:ROUTE,
      privacy:'Kayıtlar yalnız teknik cihaz ve hesap sonucunu içerir; ad, telefon, e-posta, adres veya konum içermez.',
      records:purgeRecords(records,now)
    };
  }

  function createRecord(result,input,now=new Date()){
    return normalizeRecord({
      createdAt:new Date(now).toISOString(),status:result.status,title:result.title,
      metrics:result.metrics||{},input:{
        pumpType:input.pumpType,phase:input.phase,voltage:input.voltage,ratedCurrent:input.ratedCurrent,
        startMethod:input.startMethod,connection:input.connection,sourceType:input.sourceType
      }
    },now);
  }

  function toIcs(record){
    const start=new Date(record.reviewAt);
    const end=new Date(start.getTime()+30*60*1000);
    const stamp=value=>value.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z');
    const escape=value=>String(value).replace(/\\/g,'\\\\').replace(/\n/g,'\\n').replace(/,/g,'\\,').replace(/;/g,'\\;');
    return [
      'BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Pompa Yedek Güç Kontrolü//TR','CALSCALE:GREGORIAN',
      'BEGIN:VEVENT',`UID:${escape(record.id)}@alo186.com`,`DTSTAMP:${stamp(new Date())}`,
      `DTSTART:${stamp(start)}`,`DTEND:${stamp(end)}`,
      'SUMMARY:Hidrofor ve pompa yedek güç 90 günlük kontrolü',
      'DESCRIPTION:Motor etiketini, kontrollü kalkışı, kablo-priz-RCD durumunu ve mevcut yedek kaynağı yeniden test edin.',
      `URL:https://alo186.com${ROUTE}`,'END:VEVENT','END:VCALENDAR',''
    ].join('\r\n');
  }

  function init(doc){
    const form=doc.getElementById('pumpForm');
    if(!form)return;
    const get=id=>doc.getElementById(id);
    let lastResult=null;
    let lastInput=null;
    let records=[];

    const read=()=>({
      emergency:get('emergency').checked,pumpType:get('pumpType').value,phase:get('phase').value,
      voltage:get('voltage').value,ratedCurrent:get('ratedCurrent').value,powerFactor:get('powerFactor').value,
      startMethod:get('startMethod').value,connection:get('connection').value,otherLoadW:get('otherLoadW').value,
      targetHours:get('targetHours').value,environment:get('environment').value,protection:get('protection').value,
      sourceStatus:get('sourceStatus').value,sourceType:get('sourceType').value,
      sourceContinuousW:get('sourceContinuousW').value,sourceSurgeW:get('sourceSurgeW').value,sourceWh:get('sourceWh').value
    });

    function loadRecords(){
      try{records=loadStoredRecords(globalThis.localStorage);}
      catch(error){records=[];}
    }
    function writeRecords(){
      try{globalThis.localStorage.setItem(STORAGE_KEY,JSON.stringify(records));return true;}
      catch(error){return false;}
    }
    function download(content,type,filename){
      const blob=new Blob([content],{type});
      const url=URL.createObjectURL(blob);
      const link=doc.createElement('a');link.href=url;link.download=filename;link.click();
      setTimeout(()=>URL.revokeObjectURL(url),0);
    }
    function metricHtml(metrics){
      if(!metrics)return'';
      return `<div class="metrics"><article><span>Motor çalışma gücü</span><strong>${metrics.runningW.toLocaleString('tr-TR')} W</strong></article><article><span>Önerilen sürekli güç</span><strong>${metrics.requiredContinuousW.toLocaleString('tr-TR')} W</strong></article><article><span>Kalkış kapasitesi</span><strong>${metrics.requiredSurgeW.toLocaleString('tr-TR')} W</strong></article><article><span>Hedef enerji</span><strong>${metrics.requiredWh.toLocaleString('tr-TR')} Wh</strong></article></div>`;
    }
    function renderRecords(message=''){
      const list=get('recordList');
      if(!list)return;
      list.innerHTML=records.length?records.map(record=>`<article class="record"><div><strong>${safeText(record.title)}</strong><small>${new Date(record.createdAt).toLocaleDateString('tr-TR')} · 90 günlük kontrol ${new Date(record.reviewAt).toLocaleDateString('tr-TR')}</small></div><div><span>${record.metrics.requiredContinuousW??'—'} W sürekli</span><span>${record.metrics.requiredSurgeW??'—'} W kalkış</span><span>${record.metrics.requiredWh??'—'} Wh</span></div><a href="../elektrikci-is-emri-ozeti/">İş emri özetine aktar →</a></article>`).join(''):'<p class="privacy">Bu cihazda kayıt yok. Sonuç oluşturduktan sonra açık onayla saklayabilirsiniz.</p>';
      get('recordStatus').textContent=message;
      get('exportResults').disabled=!records.length;
      get('clearRecords').disabled=!records.length;
    }
    function render(result){
      lastResult=result;lastInput=read();
      get('resultBadge').textContent=result.status.replaceAll('_',' ');
      get('resultTitle').textContent=result.title;
      get('resultSummary').textContent=result.summary;
      get('metricArea').innerHTML=metricHtml(result.metrics);
      get('issueList').innerHTML=result.issues.length?result.issues.map(item=>`<li>${safeText(item)}</li>`).join(''):'<li>Kritik eksik kaydedilmedi.</li>';
      get('stepList').innerHTML=result.steps.map(item=>`<li>${safeText(item)}</li>`).join('');
      get('toolLinks').innerHTML=(result.toolKeys||[]).map(key=>TOOL_LINKS[key]?`<a class="button" href="${TOOL_LINKS[key].href}">${TOOL_LINKS[key].label}</a>`:'').join('');
      get('result').className=`panel result status-${result.status}`;
      get('result').focus();
      get('commerceGate').classList.toggle('hidden',result.commerceClosed);
      get('productLinks').innerHTML='';
      ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>{get(id).checked=false;});
      get('openProducts').disabled=true;
      get('saveResult').disabled=false;
      get('calendarResult').disabled=false;
    }
    function sourceFields(){get('existingFields').classList.toggle('hidden',get('sourceStatus').value!=='existing');}
    function gate(){get('openProducts').disabled=!['actualNeed','technicalCheck','affiliateCheck'].every(id=>get(id).checked);}

    form.addEventListener('submit',event=>{event.preventDefault();render(evaluate(read()));});
    get('resetBtn').addEventListener('click',()=>{
      form.reset();sourceFields();lastResult=null;lastInput=null;
      get('result').className='panel result hidden';get('commerceGate').classList.add('hidden');
      get('saveResult').disabled=true;get('calendarResult').disabled=true;
    });
    get('sourceStatus').addEventListener('change',sourceFields);
    ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>get(id).addEventListener('change',gate));
    get('openProducts').addEventListener('click',()=>{
      if(!lastResult||lastResult.commerceClosed)return;
      get('productLinks').innerHTML=lastResult.commerceCategories.map(key=>CATEGORY_LINKS[key]?`<a class="button primary" href="${CATEGORY_LINKS[key].href}">${CATEGORY_LINKS[key].label}</a>`:'').join('');
      get('productLinks').focus();
    });
    get('saveResult').addEventListener('click',()=>{
      if(!lastResult||!lastInput)return;
      records=purgeRecords([createRecord(lastResult,lastInput),...records]);
      renderRecords(writeRecords()?'Sonuç yalnız bu cihazda saklandı.':'Tarayıcı kaydı kullanılamadı; sonuç saklanmadı.');
    });
    get('calendarResult').addEventListener('click',()=>{
      if(!lastResult||!lastInput)return;
      const record=createRecord(lastResult,lastInput);
      download(toIcs(record),'text/calendar;charset=utf-8','alo186-pompa-90-gun-kontrol.ics');
    });
    get('exportResults').addEventListener('click',()=>download(JSON.stringify(exportPayload(records),null,2),'application/json;charset=utf-8','alo186-pompa-yedek-guc-kayitlari.json'));
    get('clearRecords').addEventListener('click',()=>{
      records=[];
      try{globalThis.localStorage.removeItem(STORAGE_KEY);}catch(error){}
      renderRecords('Bu cihazdaki pompa kayıtları silindi.');
    });

    loadRecords();renderRecords();sourceFields();
  }

  return {
    evaluate,calculations,normalizeRecord,purgeRecords,loadStoredRecords,exportPayload,createRecord,toIcs,init,
    constants:{START_MULTIPLIER,PF_DEFAULT,RESERVE,BATTERY_EFF,USABLE,STORAGE_KEY,MAX_RECORDS,TTL_DAYS,REVIEW_DAYS,CATEGORY_LINKS}
  };
});
