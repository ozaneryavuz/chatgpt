(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document,root);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const AFFILIATE_TAG='alo186rehber-21';
  const safeNumber=(value)=>{const number=Number(value);return Number.isFinite(number)?number:null;};
  const round=(value,digits=2)=>Number.isFinite(value)?Number(value.toFixed(digits)):null;
  const percentChange=(current,previous)=>previous>0?((current-previous)/previous)*100:null;
  const pctDiff=(a,b)=>a!==null&&b!==null&&Math.max(Math.abs(a),Math.abs(b))>0?Math.abs(a-b)/Math.max(Math.abs(a),Math.abs(b))*100:null;

  function evaluate(raw={}){
    const input={
      emergency:Boolean(raw.emergency),
      meterCondition:raw.meterCondition||'unknown',
      readingType:raw.readingType||'unknown',
      mainSwitchCheck:raw.mainSwitchCheck||'not_done',
      currentDays:safeNumber(raw.currentDays),
      currentKwh:safeNumber(raw.currentKwh),
      previousDays:safeNumber(raw.previousDays),
      previousKwh:safeNumber(raw.previousKwh),
      lastYearKwh:safeNumber(raw.lastYearKwh),
      previousIndex:safeNumber(raw.previousIndex),
      currentIndex:safeNumber(raw.currentIndex),
      multiplier:safeNumber(raw.multiplier)||1,
      occupancyChange:raw.occupancyChange||'same',
      weatherLoad:raw.weatherLoad||'no',
      newLoad:raw.newLoad||'no',
      existingMonitor:raw.existingMonitor||'none',
      intendedLoad:raw.intendedLoad||'unknown',
      directWall:raw.directWall||'unknown',
      earthRequired:raw.earthRequired||'unknown',
      featureNeed:raw.featureNeed||'local_display'
    };

    const actions=[];
    const warnings=[];
    const evidence=[];
    const commercial={allowed:false,category:null,query:null,reason:null};
    const metrics={currentDaily:null,previousDaily:null,changePct:null,indexConsumption:null,indexMismatchPct:null,periodFlag:false};

    if(input.currentDays>0&&input.currentKwh>=0)metrics.currentDaily=input.currentKwh/input.currentDays;
    if(input.previousDays>0&&input.previousKwh>=0)metrics.previousDaily=input.previousKwh/input.previousDays;
    metrics.changePct=percentChange(metrics.currentDaily,metrics.previousDaily);
    if(input.currentIndex!==null&&input.previousIndex!==null&&input.currentIndex>=input.previousIndex){
      metrics.indexConsumption=(input.currentIndex-input.previousIndex)*input.multiplier;
      metrics.indexMismatchPct=pctDiff(metrics.indexConsumption,input.currentKwh);
    }
    metrics.periodFlag=Boolean(input.currentDays&&((input.currentDays<25)||(input.currentDays>35)));

    const dangerousConditions=new Set(['burned','wet','broken','hot','display_error','seal_damage']);
    if(input.emergency||dangerousConditions.has(input.meterCondition)){
      warnings.push('Duman, ark, yanık kokusu, aşırı ısınma, su veya sayaç hasarı alışveriş konusu değildir. Panoya ve sayaca müdahale etmeyin.');
      actions.push('Güvenli mesafeye geçin; aktif elektrik arızası için bölgenizdeki dağıtım şirketi veya 186 ile iletişim kurun.');
      actions.push('Sayaç mühürlerine, bağlantılara ve pano içine dokunmayın; incelemeyi yetkili kuruluş veya yetkin elektrikçi yapsın.');
      return finalize('official_check','Resmî/teknik inceleme gerekli',input,metrics,actions,warnings,evidence,commercial);
    }

    if(!(input.currentDays>0)||!(input.currentKwh>=0)){
      actions.push('Faturadaki tüketim kWh değerini ve ilk–son okuma arasındaki gün sayısını girin.');
      return finalize('incomplete','Karar için temel veri eksik',input,metrics,actions,warnings,evidence,commercial);
    }

    evidence.push(`Bu dönem: ${round(input.currentKwh,1)} kWh / ${input.currentDays} gün = ${round(metrics.currentDaily,2)} kWh/gün.`);
    if(metrics.previousDaily!==null)evidence.push(`Önceki karşılaştırılabilir dönem: ${round(input.previousKwh,1)} kWh / ${input.previousDays} gün = ${round(metrics.previousDaily,2)} kWh/gün.`);
    if(metrics.changePct!==null)evidence.push(`Günlük normalize tüketim değişimi: %${round(metrics.changePct,1)}.`);

    if(metrics.periodFlag){
      warnings.push('Okuma dönemi 25–35 gün aralığının dışında görünüyor. Mücbir sebep, ağır mevsim şartı veya dönemsel kullanım istisnaları olabilir; fatura tarihlerini dağıtım şirketi kaydıyla doğrulayın.');
      actions.push('İlk ve son okuma tarihlerini, fatura üzerindeki okuma türünü ve sayaç endeksini kontrol edin.');
    }

    if(input.readingType==='estimated'){
      warnings.push('Fatura gerçek sayaç okuması yerine kıyas/tahmin içeriyor olabilir. Tahmini tüketimi cihaz satın alarak açıklamaya çalışmayın.');
      actions.push('Güncel sayaç endeksinin fotoğrafını kişisel bilgiler görünmeyecek şekilde kendi kayıtlarınız için saklayın ve görevli tedarik/dağıtım şirketine başvurun.');
    }else if(input.readingType==='unknown'){
      actions.push('Faturada okuma türünün gerçek, tahmini/kıyasen veya düzeltme olup olmadığını doğrulayın.');
    }

    if(metrics.indexConsumption!==null){
      evidence.push(`Girilen endeks farkı × çarpan: ${round(metrics.indexConsumption,1)} kWh.`);
      if(metrics.indexMismatchPct!==null&&metrics.indexMismatchPct>5){
        warnings.push(`Endeks hesabı ile faturadaki kWh arasında yaklaşık %${round(metrics.indexMismatchPct,1)} fark var.`);
        actions.push('Sayaç çarpanını, ilk/son endeksi ve okuma tarihlerini kontrol edin; fark sürüyorsa önce görevli tedarik veya dağıtım şirketine yazılı başvuru yapın.');
      }
    }

    if(input.mainSwitchCheck==='index_continues'){
      warnings.push('Kullanıcı tarafındaki ana şalter kapalıyken sayaç tüketimi artmaya devam ediyor gözlemi; ortak/yanlış bağlantı, sayaç veya tesisat incelemesi gerektirir.');
      actions.push('Sayaca müdahale etmeyin. Zaman damgalı endeks kayıtlarıyla dağıtım şirketine ve yetkin elektrikçiye başvurun.');
      return finalize('official_check','Endeks veya bağlantı incelemesi gerekli',input,metrics,actions,warnings,evidence,commercial);
    }

    const mismatch=metrics.indexMismatchPct!==null&&metrics.indexMismatchPct>5;
    const anomaly=metrics.changePct!==null&&metrics.changePct>=25;
    const strongDrop=metrics.changePct!==null&&metrics.changePct<=-25;
    const expectedChange=input.occupancyChange==='higher'||input.weatherLoad==='yes'||input.newLoad==='yes';
    const riskyLoads=new Set(['heater','motor_compressor','ev_charging','medical','fixed_wiring','unknown']);

    if(input.existingMonitor==='adequate'){
      actions.push('Mevcut ölçüm cihazınız aynı yükü güvenli biçimde ve gerekli kWh çözünürlüğüyle ölçüyorsa yeni ürün almayın.');
      actions.push('Aynı saat aralığında 7 günlük kWh kaydı oluşturup günlük ortalamayı karşılaştırın.');
      return finalize('no_buy','Mevcut ölçüm imkânı yeterli',input,metrics,actions,warnings,evidence,commercial);
    }

    if(!anomaly&&!mismatch){
      if(strongDrop)actions.push('Tüketim düşmüş görünüyor; yalnız daha ayrıntılı veri görmek için yeni cihaz almak zorunlu değildir.');
      else actions.push('Günlük normalize tüketimde belirgin bir artış veya endeks uyuşmazlığı görülmüyor. Yeni ürün almayın; bir sonraki dönemde aynı yöntemi tekrarlayın.');
      actions.push('Karşılaştırmayı tutarlı yapmak için kWh/gün değerini ve kullanım değişikliklerini kaydedin.');
      return finalize('no_buy','Belirgin tüketim anomalisi doğrulanmadı',input,metrics,actions,warnings,evidence,commercial);
    }

    if(mismatch||input.readingType==='estimated'||metrics.periodFlag){
      actions.push('Önce fatura-endeks-okuma dönemi uyuşmazlığını resmî kanaldan açıklığa kavuşturun; ürün ölçümü fatura düzeltmesinin yerine geçmez.');
      return finalize('official_check','Önce fatura ve sayaç verisini doğrulayın',input,metrics,actions,warnings,evidence,commercial);
    }

    if(anomaly&&expectedChange){
      actions.push('Artış; kullanım süresi, kişi sayısı, ısıtma/soğutma veya yeni cihaz değişikliğiyle açıklanabilir. Yeni ürün almadan önce 7 günlük manuel çalışma süresi ve kWh kaydı tutun.');
      actions.push('Yüksek tüketimli cihazların etiket W değeri × çalışma saati ile yaklaşık katkısını ayrı hesaplayın.');
      return finalize('explained','Artış için makul kullanım değişikliği var',input,metrics,actions,warnings,evidence,commercial);
    }

    if(riskyLoads.has(input.intendedLoad)){
      warnings.push('Isıtıcı, motor/kompresör, elektrikli araç, medikal cihaz, sabit tesisat veya yükü bilinmeyen devre basit akıllı priz/fiş tipi ölçer affiliate sonucuna dönüştürülmez.');
      actions.push('Devre ve cihaz tüketimini uygun CAT sınıfı ölçüm yöntemiyle yetkin elektrikçi değerlendirsin.');
      return finalize('professional','Profesyonel ölçüm yöntemi gerekli',input,metrics,actions,warnings,evidence,commercial);
    }

    if(input.directWall!=='yes'){
      warnings.push('Grup priz, uzatma veya zincirleme bağlantı üzerinden ölçüm yapılması toplam yük ve temas ısınması riskini gizleyebilir.');
      actions.push('Önce doğrudan duvar prizi, ürün etiketi, topraklama ihtiyacı ve yük akımını doğrulayın.');
      return finalize('needs_evidence','Güvenli ölçüm bağlantısı doğrulanmadı',input,metrics,actions,warnings,evidence,commercial);
    }

    if(input.earthRequired==='unknown'){
      actions.push('Cihazın koruma sınıfını ve topraklama gereksinimini doğrulayın; bilinmeyen topraklama durumunda ticari bağlantı açılmaz.');
      return finalize('needs_evidence','Topraklama ve yük kanıtı eksik',input,metrics,actions,warnings,evidence,commercial);
    }

    if(input.existingMonitor==='available'){
      actions.push('Elinizdeki ölçüm cihazını önce 7 gün kullanın. Aynı yükü güvenli ve yeterli çözünürlükte ölçebiliyorsa yeni ürün almayın.');
      return finalize('no_buy','Önce mevcut ölçüm cihazını kullanın',input,metrics,actions,warnings,evidence,commercial);
    }

    commercial.allowed=true;
    if(input.featureNeed==='remote_control'){
      commercial.category='energy_monitoring_smart_plug';
      commercial.query='enerji ölçümlü akıllı priz Matter 16A kWh izleme';
      commercial.reason='Düşük riskli fişli yükte kWh ölçümü yanında uzaktan kontrol/zamanlama gereksinimi doğrulandı.';
    }else{
      commercial.category='plug_in_energy_meter';
      commercial.query='priz tipi enerji ölçer watt kWh güç faktörü ekranlı';
      commercial.reason='Düşük riskli fişli yükte yerel W/kWh ölçüm açığı doğrulandı.';
    }
    actions.push('Tek bir düşük riskli fişli yükü 7 gün ölçün; aynı saatlerde W, kWh ve çalışma süresini kaydedin.');
    actions.push('Ölçüm cihazının anma akımı, güç sınırı, topraklama yapısı ve üretici talimatını yük etiketiyle eşleştirin.');
    return finalize('monitoring_gap','Ölçüm açığı doğrulandı; düşük riskli ürün sınıfı değerlendirilebilir',input,metrics,actions,warnings,evidence,commercial);
  }

  function finalize(code,title,input,metrics,actions,warnings,evidence,commercial){
    return {code,title,input,metrics:{
      currentDaily:round(metrics.currentDaily),previousDaily:round(metrics.previousDaily),changePct:round(metrics.changePct,1),
      indexConsumption:round(metrics.indexConsumption,1),indexMismatchPct:round(metrics.indexMismatchPct,1),periodFlag:metrics.periodFlag
    },actions,warnings,evidence,commercial};
  }

  function affiliateUrl(result){
    if(!result?.commercial?.allowed||!result.commercial.query)return null;
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(result.commercial.query)}&tag=${AFFILIATE_TAG}`;
  }

  function report(result){
    return {
      schemaVersion:1,
      generatedAt:new Date().toISOString(),
      tool:'ALO186 Elektrik Faturası kWh Anomali ve Sayaç Kontrolü',
      decision:result.code,
      title:result.title,
      metrics:result.metrics,
      actions:result.actions,
      warnings:result.warnings,
      evidence:result.evidence,
      commercialPolicy:{affiliateAllowed:result.commercial.allowed,category:result.commercial.category,pricePublished:false,stockPublished:false,ratingPublished:false,sellerPublished:false,warrantyPublished:false},
      privacy:{name:false,email:false,phone:false,address:false,subscriberNumber:false,meterSerial:false,storage:false}
    };
  }

  function ics(result,days=30){
    const date=new Date();date.setDate(date.getDate()+days);
    const stamp=(value)=>value.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z');
    const summary='ALO186 aylık kWh ve sayaç endeksi kontrolü';
    const description=[
      'Faturadaki ilk/son okuma tarihini ve kWh değerini kontrol edin.',
      'kWh/gün değerini önceki dönemle karşılaştırın.',
      'Sayaç endeks farkı ve çarpanı doğrulayın.',
      'Isınma, koku, hasar veya şüpheli endeks varsa ürüne yönelmeyin; resmî/teknik inceleme isteyin.',
      `Önceki karar: ${result.title}`
    ].join('\\n');
    return ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//kWh Anomali Kontrolu//TR','BEGIN:VEVENT',`UID:${Date.now()}-kwh@alo186.com`,`DTSTAMP:${stamp(new Date())}`,`DTSTART:${stamp(date)}`,`SUMMARY:${summary}`,`DESCRIPTION:${description}`,'END:VEVENT','END:VCALENDAR'].join('\r\n');
  }

  function mount(document,window){
    const form=document.getElementById('kwhForm');
    if(!form)return;
    const resultBox=document.getElementById('result');
    const title=document.getElementById('resultTitle');
    const metrics=document.getElementById('metrics');
    const warnings=document.getElementById('warnings');
    const evidence=document.getElementById('evidence');
    const actions=document.getElementById('actions');
    const affiliatePanel=document.getElementById('affiliatePanel');
    const affiliateLink=document.getElementById('affiliateLink');
    const affiliateChecks=[...document.querySelectorAll('[data-affiliate-check]')];
    let current=null;

    const read=()=>Object.fromEntries(new FormData(form).entries());
    const list=(host,items)=>{host.replaceChildren();for(const item of items||[]){const li=document.createElement('li');li.textContent=item;host.appendChild(li);}};
    const renderMetrics=(result)=>{
      metrics.replaceChildren();
      const values=[['Bu dönem',result.metrics.currentDaily===null?'—':`${result.metrics.currentDaily} kWh/gün`],['Önceki dönem',result.metrics.previousDaily===null?'—':`${result.metrics.previousDaily} kWh/gün`],['Değişim',result.metrics.changePct===null?'—':`%${result.metrics.changePct}`],['Endeks hesabı',result.metrics.indexConsumption===null?'—':`${result.metrics.indexConsumption} kWh`]];
      for(const[label,value]of values){const item=document.createElement('div');const small=document.createElement('small');small.textContent=label;const strong=document.createElement('strong');strong.textContent=value;item.append(small,strong);metrics.appendChild(item);}
    };
    const syncAffiliate=()=>{
      if(!current?.commercial?.allowed){affiliateLink.removeAttribute('href');affiliateLink.setAttribute('aria-disabled','true');return;}
      const ready=affiliateChecks.every((input)=>input.checked);
      affiliateLink.setAttribute('aria-disabled',ready?'false':'true');affiliateLink.tabIndex=ready?0:-1;
      if(ready)affiliateLink.href=affiliateUrl(current);else affiliateLink.removeAttribute('href');
    };
    const render=(result)=>{
      current=result;resultBox.hidden=false;resultBox.dataset.decision=result.code;title.textContent=result.title;renderMetrics(result);list(warnings,result.warnings);warnings.parentElement.hidden=!result.warnings.length;list(evidence,result.evidence);list(actions,result.actions);
      affiliatePanel.hidden=!result.commercial.allowed;
      document.getElementById('affiliateReason').textContent=result.commercial.reason||'';
      affiliateChecks.forEach((input)=>{input.checked=false;});syncAffiliate();
      resultBox.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
    };
    form.addEventListener('submit',(event)=>{event.preventDefault();render(evaluate(read()));});
    affiliateChecks.forEach((input)=>input.addEventListener('change',syncAffiliate));
    affiliateLink.addEventListener('click',(event)=>{if(affiliateLink.getAttribute('aria-disabled')!=='false')event.preventDefault();});
    document.getElementById('downloadJson').addEventListener('click',()=>{if(!current)return;download(window,JSON.stringify(report(current),null,2),'alo186-kwh-kontrol-fiisi.json','application/json');});
    document.getElementById('downloadIcs').addEventListener('click',()=>{if(!current)return;download(window,ics(current),'alo186-aylik-kwh-kontrolu.ics','text/calendar');});
    document.getElementById('printResult').addEventListener('click',()=>window.print());
  }

  function download(window,content,name,type){const blob=new Blob([content],{type:`${type};charset=utf-8`});const url=URL.createObjectURL(blob);const anchor=window.document.createElement('a');anchor.href=url;anchor.download=name;anchor.click();setTimeout(()=>URL.revokeObjectURL(url),0);}

  return {evaluate,affiliateUrl,report,ics,mount,AFFILIATE_TAG};
});
