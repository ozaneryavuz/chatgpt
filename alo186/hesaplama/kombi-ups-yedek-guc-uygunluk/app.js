(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document,root);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const safeNumber=(value)=>{const number=Number(value);return Number.isFinite(number)?number:null;};
  const round=(value,digits=1)=>Number.isFinite(value)?Number(value.toFixed(digits)):null;
  const ceilStep=(value,step)=>Number.isFinite(value)?Math.ceil(value/step)*step:null;
  const DANGER_CONDITIONS=new Set(['hot','wet','damaged','smell','burned']);
  const PROFESSIONAL_TYPES=new Set(['electric_boiler','central_boiler','heat_pump']);

  function evaluate(raw={}){
    const input={
      emergency:Boolean(raw.emergency),
      scenario:raw.scenario||'planning',
      applianceType:raw.applianceType||'gas_combi',
      exactModelVerified:raw.exactModelVerified||'no',
      manufacturerPowerGuide:raw.manufacturerPowerGuide||'unknown',
      connectionType:raw.connectionType||'unknown',
      physicalCondition:raw.physicalCondition||'normal',
      maxW:safeNumber(raw.maxW),
      energyMode:raw.energyMode||'average_w',
      averageW:safeNumber(raw.averageW),
      referenceWh:safeNumber(raw.referenceWh),
      referenceHours:safeNumber(raw.referenceHours),
      targetHours:safeNumber(raw.targetHours),
      startupKnown:raw.startupKnown||'no',
      startupW:safeNumber(raw.startupW),
      outputPf:safeNumber(raw.outputPf),
      pureSineRequirement:raw.pureSineRequirement||'unknown',
      groundingRequirement:raw.groundingRequirement||'unknown',
      continuityNeed:raw.continuityNeed||'unknown',
      freezeRisk:raw.freezeRisk||'no',
      sourceStatus:raw.sourceStatus||'none',
      sourceContinuousW:safeNumber(raw.sourceContinuousW),
      sourceSurgeW:safeNumber(raw.sourceSurgeW),
      sourceWh:safeNumber(raw.sourceWh),
      sourceVa:safeNumber(raw.sourceVa),
      sourcePureSine:raw.sourcePureSine||'unknown',
      sourceGroundingVerified:raw.sourceGroundingVerified||'unknown',
      daytimeTest:raw.daytimeTest||'untested'
    };

    const actions=[];
    const warnings=[];
    const evidence=[];
    const metrics={averageW:null,continuousW:null,surgeW:null,requiredWh:null,referenceVa:null,effectiveSourceWh:null,runtimeHours:null,usedUpperBound:false};
    const commercial={allowed:false,category:null,url:null,reason:null};

    if(input.emergency||DANGER_CONDITIONS.has(input.physicalCondition)){
      warnings.push('Gaz kokusu, karbonmonoksit alarmı/belirtisi, duman, yanık kokusu, su teması veya aşırı ısınma alışveriş konusu değildir.');
      actions.push('Gaz kokusunda elektrik anahtarlarına dokunmadan güvenli alana çıkın ve 187 Doğal Gaz Acil hattını arayın.');
      actions.push('Baş ağrısı, baş dönmesi, bulantı, bilinç değişikliği veya nefes darlığında temiz havaya çıkın ve 112’yi arayın.');
      actions.push('Islanan, yanan veya aşırı ısınan kombi, UPS, kablo ya da prizi yeniden enerjilendirmeyin; yetkili servis ve elektrik uzmanı çağırın.');
      return finalize('emergency','Önce can, gaz ve elektrik güvenliği',input,metrics,actions,warnings,evidence,commercial);
    }

    if(PROFESSIONAL_TYPES.has(input.applianceType)||input.connectionType==='fixed'){
      warnings.push('Elektrikli kazan, ısı pompası, merkezi kazan dairesi veya sabit bağlı cihaz tüketici tipi UPS/power station affiliate sonucuna dönüştürülmez.');
      actions.push('Gerçek güç, kalkış, koruma, topraklama, nötr düzeni, transfer ve jeneratör/UPS koordinasyonunu yetkili proje ve servis ekibiyle doğrulayın.');
      return finalize('professional','Sabit veya yüksek güçlü sistem için profesyonel proje',input,metrics,actions,warnings,evidence,commercial);
    }

    if(!(input.maxW>0)||!(input.targetHours>0)){
      actions.push('Tam modelin üretici teknik sayfasındaki azami elektrik gücünü ve hedef çalışma süresini girin. Isıl kapasiteyi (kW) elektrik tüketimi sanmayın.');
      return finalize('incomplete','Temel elektrik verisi eksik',input,metrics,actions,warnings,evidence,commercial);
    }

    if(input.energyMode==='measured_wh'){
      if(!(input.referenceWh>0)||!(input.referenceHours>0)){
        actions.push('Üretici verisi veya uyanıkken yapılan kontrollü ölçümdeki Wh değerini ve ait olduğu saat süresini girin.');
        return finalize('incomplete','Enerji referansı eksik',input,metrics,actions,warnings,evidence,commercial);
      }
      metrics.averageW=input.referenceWh/input.referenceHours;
      evidence.push(`${round(input.referenceWh)} Wh / ${round(input.referenceHours,2)} saat = yaklaşık ${round(metrics.averageW)} W ortalama.`);
    }else if(input.energyMode==='average_w'){
      if(!(input.averageW>0)){
        actions.push('Üretici verisindeki veya güvenli ölçümdeki ortalama elektrik tüketimini girin.');
        return finalize('incomplete','Ortalama tüketim verisi eksik',input,metrics,actions,warnings,evidence,commercial);
      }
      metrics.averageW=input.averageW;
      evidence.push(`Girilen ortalama elektrik tüketimi: ${round(metrics.averageW)} W.`);
    }else{
      metrics.averageW=input.maxW;
      metrics.usedUpperBound=true;
      warnings.push('Azami elektrik gücü gerçek ortalama tüketim değildir. Enerji hesabı konservatif üst sınırla yapılmıştır ve gerekli Wh değerini fazla gösterebilir.');
      evidence.push(`Ortalama veri bulunmadığı için ${round(input.maxW)} W azami değer üst sınır olarak kullanıldı.`);
    }

    if(metrics.averageW>input.maxW){
      warnings.push('Ortalama W, azami W değerinden büyük olamaz. Isıl kW, elektrik W ve ölçüm sürelerini yeniden kontrol edin.');
      return finalize('incomplete','Güç değerleri tutarsız',input,metrics,actions,warnings,evidence,commercial);
    }

    metrics.continuousW=ceilStep(input.maxW*1.25,10);
    if(input.startupKnown==='yes'&&input.startupW>0){
      metrics.surgeW=ceilStep(Math.max(input.startupW,metrics.continuousW),10);
      evidence.push(`Üretici/ölçüm kalkış verisine göre tepe güç alt sınırı: ${metrics.surgeW} W.`);
    }
    metrics.requiredWh=ceilStep((metrics.averageW*input.targetHours)/(0.82*0.80),10);
    if(input.outputPf>0&&input.outputPf<=1)metrics.referenceVa=ceilStep(metrics.continuousW/input.outputPf,50);
    evidence.push(`Sürekli çıkış alt sınırı: ${metrics.continuousW} W (azami elektrik gücü + %25 görünür pay).`);
    evidence.push(`Nominal enerji hedefi: yaklaşık ${metrics.requiredWh} Wh (${round(metrics.averageW)} W × ${round(input.targetHours,2)} saat; AC dönüşüm ve kullanılabilir kapasite payı dahil).`);
    if(metrics.referenceVa!==null)evidence.push(`Girilen UPS W/VA oranına göre yalnız ön karşılaştırma için yaklaşık ${metrics.referenceVa} VA. Ürünün gerçek W sınırı ayrıca zorunludur.`);

    if(input.exactModelVerified!=='yes'||input.manufacturerPowerGuide!=='yes'){
      warnings.push('Tam model ve üreticinin elektrik bağlantısı/alternatif güç talimatı doğrulanmadan ticari yol açılmaz.');
      actions.push('Model etiketini, kullanım-montaj kılavuzunu, azami elektrik gücünü, topraklama ve yeniden başlatma davranışını yetkili servisle doğrulayın.');
      return finalize('needs_evidence','Tam model ve üretici güç rehberi gerekli',input,metrics,actions,warnings,evidence,commercial);
    }

    if(input.startupKnown!=='yes'||!(input.startupW>0)){
      warnings.push('Pompa, fan ve ateşleme çevriminin kalkış/tepe gücü doğrulanmadı. Yalnız sürekli watt ile UPS seçmeyin.');
      actions.push('Üretici teknik verisini veya yetkili elektrikçinin güvenli ölçümünü kullanarak tepe gücü belirleyin.');
      return finalize('needs_evidence','Kalkış gücü kanıtı gerekli',input,metrics,actions,warnings,evidence,commercial);
    }

    if(input.pureSineRequirement==='unknown'||input.groundingRequirement!=='verified'||input.connectionType!=='grounded_plug'){
      warnings.push('Dalga biçimi, koruyucu topraklama ve cihazın bağlantı biçimi doğrulanmadan UPS/power station uygunluğu kabul edilmez.');
      actions.push('Priz, PE sürekliliği ve üreticinin saf sinüs/nötr-toprak beklentisini yetkili servis ve elektrik uzmanıyla doğrulayın; adaptör, uzatma veya nötr-toprak köprüsü doğaçlamayın.');
      return finalize('needs_evidence','Çıkış ve topraklama kanıtı eksik',input,metrics,actions,warnings,evidence,commercial);
    }

    if(input.continuityNeed==='unknown'){
      actions.push('Kombinin kısa kesintide otomatik yeniden başlamasının kabul edilip edilmediğini ve kesintisiz transfer gereksinimini üretici/servisle doğrulayın.');
      return finalize('needs_evidence','Transfer davranışı bilinmiyor',input,metrics,actions,warnings,evidence,commercial);
    }

    if(input.sourceStatus==='existing'){
      metrics.effectiveSourceWh=input.sourceWh>0?input.sourceWh*0.82*0.80:null;
      metrics.runtimeHours=metrics.effectiveSourceWh!==null&&metrics.averageW>0?metrics.effectiveSourceWh/metrics.averageW:null;
      const enoughContinuous=input.sourceContinuousW>=metrics.continuousW;
      const enoughSurge=input.sourceSurgeW>=metrics.surgeW;
      const enoughEnergy=input.sourceWh>=metrics.requiredWh;
      const sineOkay=input.pureSineRequirement==='no'||input.sourcePureSine==='yes';
      const groundOkay=input.sourceGroundingVerified==='yes';
      const vaOkay=metrics.referenceVa===null||!(input.sourceVa>0)||input.sourceVa>=metrics.referenceVa;
      if(enoughContinuous&&enoughSurge&&enoughEnergy&&sineOkay&&groundOkay&&vaOkay&&input.daytimeTest==='success'){
        actions.push('Mevcut kaynak sürekli W, tepe W, Wh, dalga biçimi, topraklama ve uyanıkken kontrollü transfer testini karşılıyor. Yeni ürün almayın.');
        actions.push('Batarya durumunu, kabloları, priz ısınmasını ve yeniden başlatmayı 90 gün sonra yeniden test edin.');
        return finalize('no_buy','Mevcut yedek güç yeterli',input,metrics,actions,warnings,evidence,commercial);
      }
      if(enoughContinuous&&enoughSurge&&enoughEnergy&&sineOkay&&groundOkay&&vaOkay&&input.daytimeTest==='untested'){
        actions.push('Yeni ürün almadan önce üretici talimatına uygun, uyanıkken ve yetkili servis sınırları içinde kontrollü transfer/yeniden başlatma testi yapın.');
        actions.push('Aşırı soğukta veya ev boşken ilk kez denemeyin.');
        return finalize('test_first','Kapasite yeterli görünüyor; önce kontrollü test',input,metrics,actions,warnings,evidence,commercial);
      }
      if(!enoughContinuous)warnings.push(`Mevcut sürekli çıkış ${input.sourceContinuousW||0} W; görünür alt sınır ${metrics.continuousW} W.`);
      if(!enoughSurge)warnings.push(`Mevcut tepe çıkış ${input.sourceSurgeW||0} W; doğrulanan tepe alt sınırı ${metrics.surgeW} W.`);
      if(!enoughEnergy)warnings.push(`Mevcut nominal enerji ${input.sourceWh||0} Wh; hedef yaklaşık ${metrics.requiredWh} Wh.`);
      if(!sineOkay)warnings.push('Üreticinin saf sinüs gereksinimi karşılanmıyor veya doğrulanmadı.');
      if(!groundOkay)warnings.push('Kaynağın koruyucu topraklama/çıkış düzeni doğrulanmadı.');
      if(input.daytimeTest==='failed')warnings.push('Mevcut kaynak kontrollü testte kombiyi güvenilir biçimde sürdüremedi veya yeniden başlatamadı.');
    }

    if(input.scenario==='active'){
      warnings.push('Aktif kesintide yeni ürün teslimatı anlık ısınma veya donma koruması çözümü değildir; affiliate yolu kapalıdır.');
      actions.push('Yalnız daha önce doğrulanmış ve test edilmiş kaynağı üretici talimatına göre kullanın. Jeneratörü kapalı, yarı kapalı alan, balkon veya pencere yakınına koymayın.');
      actions.push(input.freezeRisk==='yes'?'Donma riski için kombi üreticisi/yetkili servis ve bina yönetiminin tahliye-su tesisatı planını uygulayın.':'Kesinti ve yeniden enerjilendirme davranışını yetkili servis talimatına göre yönetin.');
      return finalize('active_outage','Aktif kesintide güvenli süreklilik planı öncelikli',input,metrics,actions,warnings,evidence,commercial);
    }

    if(metrics.continuousW>500||metrics.surgeW>1500||metrics.requiredWh>3000||input.targetHours>24){
      warnings.push('Güç, tepe veya süre ihtiyacı tüketici tipi kısa liste sınırını aşıyor.');
      actions.push('Akü kapasitesi, şarj süresi, yedeklilik, donma riski, jeneratör ve tesisat koordinasyonunu profesyonel proje olarak ele alın.');
      return finalize('professional','Yüksek güç veya uzun süre için profesyonel plan',input,metrics,actions,warnings,evidence,commercial);
    }

    commercial.allowed=true;
    commercial.category=input.continuityNeed==='no_restart'?'pure_sine_ups':'portable_power';
    commercial.url=input.continuityNeed==='no_restart'
      ?'/amazon-elektrik-urunleri/kesintisiz-guc-kaynagi-secimi?from=kombi'
      :'/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi?from=kombi';
    commercial.reason='Tam model, üretici elektrik rehberi, kalkış gücü, dalga biçimi, topraklama ve gerçek kapasite açığı doğrulandı.';
    actions.push(input.continuityNeed==='no_restart'?'Gerçek W ve VA sınırı, saf sinüs, transfer süresi ve batarya süresi doğrulanmış UPS sınıfını karşılaştırın.':'Kombinin kontrollü yeniden başlamasına izin veriliyorsa sürekli/tepe W ve Wh sınırı doğrulanmış power station sınıfını karşılaştırın.');
    actions.push('Ürünü satın almadan önce tam kombi modeliyle yetkili servisten yazılı uyumluluk doğrulaması alın; ilk testi uyanıkken yapın.');
    actions.push('Uzatma kablosu, çoklayıcı, ters besleme veya nötr-toprak köprüsü kullanmayın.');
    return finalize('capacity_gap','Yedek güç açığı doğrulandı',input,metrics,actions,warnings,evidence,commercial);
  }

  function finalize(code,title,input,metrics,actions,warnings,evidence,commercial){
    return {code,title,input,metrics:{averageW:round(metrics.averageW),continuousW:round(metrics.continuousW),surgeW:round(metrics.surgeW),requiredWh:round(metrics.requiredWh),referenceVa:round(metrics.referenceVa),effectiveSourceWh:round(metrics.effectiveSourceWh),runtimeHours:round(metrics.runtimeHours,2),usedUpperBound:metrics.usedUpperBound},actions,warnings,evidence,commercial};
  }

  function technicalReport(result){
    return {
      schemaVersion:1,
      generatedAt:new Date().toISOString(),
      tool:'ALO186 Kombi UPS ve Yedek Güç Uygunluğu',
      decision:result.code,
      title:result.title,
      technicalInput:{applianceType:result.input.applianceType,scenario:result.input.scenario,maxW:result.input.maxW,targetHours:result.input.targetHours,continuityNeed:result.input.continuityNeed,sourceStatus:result.input.sourceStatus},
      metrics:result.metrics,
      actions:result.actions,
      warnings:result.warnings,
      commercialAllowed:result.commercial.allowed,
      privacy:'Ad, telefon, e-posta, adres, doğalgaz aboneliği, cihaz seri numarası veya konum içermez. Yalnız kullanıcının cihazında oluşturulur.',
      disclaimer:'Bu çıktı kombi, gaz tesisatı, elektrik tesisatı, UPS veya jeneratör için montaj/onay belgesi değildir.'
    };
  }

  function createIcs(result,now=new Date()){
    const start=new Date(now.getTime()+90*86400000);
    const stamp=(date)=>date.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z');
    const day=start.toISOString().slice(0,10).replace(/-/g,'');
    const description='Tam model üretici elektrik verisini, UPS/power station sürekli ve tepe W sınırını, Wh kapasitesini, saf sinüsü, topraklamayı, priz ısınmasını ve uyanıkken transfer/yeniden başlatma testini doğrula. Gaz kokusunda 187, sağlık belirtisinde 112.';
    return ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Combi Backup Check//TR','CALSCALE:GREGORIAN','BEGIN:VEVENT',`UID:alo186-kombi-${stamp(now)}@alo186.com`,`DTSTAMP:${stamp(now)}`,`DTSTART;VALUE=DATE:${day}`,'SUMMARY:Kombi yedek güç 90 günlük kontrolü',`DESCRIPTION:${description}`,'END:VEVENT','END:VCALENDAR'].join('\r\n');
  }

  function download(win,content,name,type){
    const blob=new win.Blob([content],{type});
    const url=win.URL.createObjectURL(blob);
    const link=win.document.createElement('a');link.href=url;link.download=name;link.click();
    win.setTimeout(()=>win.URL.revokeObjectURL(url),500);
  }

  function mount(doc,win){
    const form=doc.getElementById('combiForm');
    if(!form)return;
    const resultBox=doc.getElementById('result');
    const commerce=doc.getElementById('commerce');
    const professional=doc.getElementById('professional');
    let lastResult=null;

    const syncFields=()=>{
      const mode=form.elements.energyMode.value;
      doc.querySelectorAll('[data-energy]').forEach((node)=>{node.hidden=node.dataset.energy!==mode;});
      const startup=form.elements.startupKnown.value==='yes';
      doc.querySelectorAll('[data-startup]').forEach((node)=>{node.hidden=!startup;});
      const existing=form.elements.sourceStatus.value==='existing';
      doc.querySelectorAll('[data-source]').forEach((node)=>{node.hidden=!existing;});
    };
    form.addEventListener('change',syncFields);syncFields();

    const fillList=(id,items)=>{const host=doc.getElementById(id);host.replaceChildren();for(const text of items||[]){const li=doc.createElement('li');li.textContent=text;host.appendChild(li);}};
    const metric=(label,value)=>{const box=doc.createElement('div');const small=doc.createElement('small');small.textContent=label;const strong=doc.createElement('strong');strong.textContent=value;box.append(small,strong);return box;};

    function render(result){
      lastResult=result;
      resultBox.hidden=false;
      resultBox.className=`panel result ${result.code}`;
      doc.getElementById('resultBadge').textContent=result.code.replaceAll('_',' ');
      doc.getElementById('resultTitle').textContent=result.title;
      doc.getElementById('resultSummary').textContent=result.commercial.allowed?result.commercial.reason:(result.actions[0]||'Teknik kanıtları tamamlayın.');
      const metrics=doc.getElementById('metrics');metrics.replaceChildren();
      if(result.metrics.averageW!==null)metrics.append(metric('Ortalama tüketim',`${result.metrics.averageW} W`));
      if(result.metrics.continuousW!==null)metrics.append(metric('Sürekli çıkış alt sınırı',`${result.metrics.continuousW} W`));
      if(result.metrics.surgeW!==null)metrics.append(metric('Tepe güç alt sınırı',`${result.metrics.surgeW} W`));
      if(result.metrics.requiredWh!==null)metrics.append(metric('Nominal enerji hedefi',`${result.metrics.requiredWh} Wh`));
      if(result.metrics.referenceVa!==null)metrics.append(metric('Referans VA',`${result.metrics.referenceVa} VA`));
      if(result.metrics.runtimeHours!==null)metrics.append(metric('Mevcut kaynak yaklaşık süresi',`${result.metrics.runtimeHours} saat`));
      fillList('evidence',result.evidence);fillList('resultActions',result.actions);fillList('warnings',result.warnings);
      doc.getElementById('warningBox').hidden=!result.warnings.length;
      commerce.hidden=!result.commercial.allowed;
      professional.hidden=!['professional'].includes(result.code);
      if(result.commercial.allowed){
        const checks=[...commerce.querySelectorAll('input[type=checkbox]')];checks.forEach((input)=>{input.checked=false;});
        const link=doc.getElementById('productLink');link.textContent=result.commercial.category==='pure_sine_ups'?'Saf sinüs UPS sınıfını aç':'Power station sınıfını aç';
        const sync=()=>{const ready=checks.every((input)=>input.checked);link.classList.toggle('disabled',!ready);link.setAttribute('aria-disabled',String(!ready));if(ready)link.href=result.commercial.url;else link.removeAttribute('href');};
        commerce.addEventListener('change',sync,{once:false});sync();
      }
      resultBox.focus();
    }

    form.addEventListener('submit',(event)=>{event.preventDefault();const data=Object.fromEntries(new win.FormData(form).entries());data.emergency=form.elements.emergency.checked;render(evaluate(data));});
    form.addEventListener('reset',()=>win.setTimeout(()=>{syncFields();resultBox.hidden=true;commerce.hidden=true;professional.hidden=true;lastResult=null;},0));
    doc.getElementById('downloadJson').addEventListener('click',()=>{if(lastResult)download(win,JSON.stringify(technicalReport(lastResult),null,2),'alo186-kombi-ups-yedek-guc-teknik-fis.json','application/json');});
    doc.getElementById('downloadIcs').addEventListener('click',()=>{if(lastResult)download(win,createIcs(lastResult),'alo186-kombi-90-gun-kontrol.ics','text/calendar');});
    doc.getElementById('printResult').addEventListener('click',()=>win.print());
  }

  return {evaluate,technicalReport,createIcs,mount};
});
