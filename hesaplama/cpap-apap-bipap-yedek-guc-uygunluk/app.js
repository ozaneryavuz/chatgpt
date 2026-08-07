(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document,root);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const safeNumber=(value)=>{const number=Number(value);return Number.isFinite(number)?number:null;};
  const round=(value,digits=1)=>Number.isFinite(value)?Number(value.toFixed(digits)):null;
  const ceilStep=(value,step)=>Number.isFinite(value)?Math.ceil(value/step)*step:null;
  const HIGH_RISK_TYPES=new Set(['ventilator','oxygen_concentrator']);

  function efficiencyFor(path){
    if(path==='manufacturer_battery'||path==='manufacturer_dc')return 0.90;
    if(path==='ac_power_station')return 0.82;
    return null;
  }

  function evaluate(raw={}){
    const input={
      emergency:Boolean(raw.emergency),
      scenario:raw.scenario||'planning',
      deviceType:raw.deviceType||'cpap',
      dependence:raw.dependence||'routine',
      supplementalOxygen:raw.supplementalOxygen||'no',
      exactModelVerified:raw.exactModelVerified||'no',
      manufacturerPowerGuide:raw.manufacturerPowerGuide||'unknown',
      humidifier:raw.humidifier||'off',
      heatedTube:raw.heatedTube||'off',
      accessoriesIncluded:raw.accessoriesIncluded||'unknown',
      maxW:safeNumber(raw.maxW),
      energyMode:raw.energyMode||'average_w',
      averageW:safeNumber(raw.averageW),
      referenceWh:safeNumber(raw.referenceWh),
      referenceHours:safeNumber(raw.referenceHours),
      targetHours:safeNumber(raw.targetHours),
      powerPath:raw.powerPath||'unknown',
      sourceStatus:raw.sourceStatus||'none',
      sourceContinuousW:safeNumber(raw.sourceContinuousW),
      sourceWh:safeNumber(raw.sourceWh),
      sourceOutputVerified:raw.sourceOutputVerified||'unknown',
      daytimeTest:raw.daytimeTest||'untested',
      physicalCondition:raw.physicalCondition||'normal'
    };

    const actions=[];
    const warnings=[];
    const evidence=[];
    const metrics={averageW:null,requiredWh:null,continuousW:null,effectiveSourceWh:null,runtimeHours:null,efficiency:null,usedUpperBound:false};
    const commercial={allowed:false,category:null,url:null,reason:null};

    const dangerConditions=new Set(['swollen','hot','wet','damaged','smell']);
    if(input.emergency||dangerConditions.has(input.physicalCondition)){
      warnings.push('Nefes darlığı, bilinç değişikliği, aktif sağlık riski veya hasarlı enerji ekipmanı alışveriş konusu değildir.');
      actions.push('Acil sağlık riski varsa 112’yi arayın; cihazın klinik kullanımına ilişkin kararı sağlık profesyoneliyle verin.');
      actions.push('Şişmiş, ıslanmış, aşırı ısınan veya hasarlı batarya/kabloyu kullanmayın ve şarj etmeyin.');
      return finalize('emergency','Önce sağlık ve elektrik güvenliği',input,metrics,actions,warnings,evidence,commercial);
    }

    if(HIGH_RISK_TYPES.has(input.deviceType)||input.supplementalOxygen==='yes'||input.dependence==='critical'){
      warnings.push('Ventilatör, oksijen konsantratörü, ek oksijenle kullanılan PAP veya klinik olarak kritik bağımlılık tüketici tipi affiliate sonucuna dönüştürülmez.');
      actions.push('Kesinti planını cihaz sağlayıcısı, hekim/uyku merkezi ve yerel acil sağlık planıyla yazılı olarak doğrulayın.');
      actions.push('Yedek güç, alarm, oksijen güvenliği ve tahliye seçeneklerini profesyonel planın parçası yapın.');
      return finalize('clinical','Klinik süreklilik planı gerekli',input,metrics,actions,warnings,evidence,commercial);
    }

    if(!(input.maxW>0)||!(input.targetHours>0)){
      actions.push('Tam modelin üretici kılavuzundaki azami güç değerini ve hedef çalışma süresini girin.');
      return finalize('incomplete','Temel güç verisi eksik',input,metrics,actions,warnings,evidence,commercial);
    }

    if(input.energyMode==='measured_wh'){
      if(!(input.referenceWh>0)||!(input.referenceHours>0)){
        actions.push('Üretici veya gözetimli testte belirtilen Wh değerini ve bu değerin ait olduğu saat süresini girin.');
        return finalize('incomplete','Enerji referansı eksik',input,metrics,actions,warnings,evidence,commercial);
      }
      metrics.averageW=input.referenceWh/input.referenceHours;
      evidence.push(`${round(input.referenceWh)} Wh / ${round(input.referenceHours,2)} saat = yaklaşık ${round(metrics.averageW)} W ortalama.`);
    }else if(input.energyMode==='average_w'){
      if(!(input.averageW>0)){
        actions.push('Üretici tablosundan veya güvenli gözetimli ölçümden ortalama watt değerini girin.');
        return finalize('incomplete','Ortalama tüketim verisi eksik',input,metrics,actions,warnings,evidence,commercial);
      }
      metrics.averageW=input.averageW;
      evidence.push(`Girilen ortalama tüketim: ${round(metrics.averageW)} W.`);
    }else{
      metrics.averageW=input.maxW;
      metrics.usedUpperBound=true;
      warnings.push('Güç kaynağı etiketi gerçek ortalama tüketim değildir. Hesap azami W üzerinden konservatif yapılmıştır ve kapasiteyi fazla gösterebilir.');
      evidence.push(`Ortalama enerji verisi olmadığı için ${round(input.maxW)} W üst sınırı kullanıldı.`);
    }

    if(metrics.averageW>input.maxW){
      warnings.push('Ortalama W değeri azami W değerinden büyük olamaz. Etiket veya ölçüm birimini yeniden kontrol edin.');
      return finalize('incomplete','Güç değerleri tutarsız',input,metrics,actions,warnings,evidence,commercial);
    }

    if((input.humidifier==='on'||input.heatedTube==='on')&&input.accessoriesIncluded!=='yes'){
      warnings.push('Nemlendirici veya ısıtmalı hortum açıkken enerji referansının bu aksesuarları içerdiği doğrulanmadı.');
      actions.push('Tam model üretici batarya rehberinde nemlendirici ve ısıtmalı hortum senaryosunu ayrı doğrulayın.');
      return finalize('needs_evidence','Aksesuar enerji kanıtı eksik',input,metrics,actions,warnings,evidence,commercial);
    }

    metrics.efficiency=efficiencyFor(input.powerPath);
    if(metrics.efficiency===null){
      actions.push('Üretici bataryası, üretici DC dönüştürücü veya AC power station/inverter yolundan hangisinin kullanılacağını doğrulayın.');
      return finalize('needs_evidence','Güç dönüşüm yolu bilinmiyor',input,metrics,actions,warnings,evidence,commercial);
    }

    metrics.continuousW=ceilStep(input.maxW*1.25,5);
    metrics.requiredWh=ceilStep((metrics.averageW*input.targetHours)/(metrics.efficiency*0.80),10);
    evidence.push(`Sürekli çıkış için görünür ön sınır: ${metrics.continuousW} W (azami cihaz gücü + %25 pay).`);
    evidence.push(`Hedef enerji: yaklaşık ${metrics.requiredWh} Wh (${round(metrics.averageW)} W × ${round(input.targetHours,2)} saat, dönüşüm ve kullanılabilir kapasite payı).`);

    if(input.exactModelVerified!=='yes'||input.manufacturerPowerGuide!=='yes'){
      warnings.push('Tam model ve üreticinin alternatif güç/batarya uyumluluğu doğrulanmadan ticari yol açılmaz.');
      actions.push('Üreticinin kullanıcı kılavuzu, batarya uyumluluk listesi ve doğru DC kablo/dönüştürücü referansını bulun.');
      return finalize('needs_evidence','Tam model ve üretici güç rehberi gerekli',input,metrics,actions,warnings,evidence,commercial);
    }

    if(input.sourceStatus==='existing'){
      if(input.sourceWh>0)metrics.effectiveSourceWh=input.sourceWh*0.80*metrics.efficiency;
      if(metrics.averageW>0&&metrics.effectiveSourceWh!==null)metrics.runtimeHours=metrics.effectiveSourceWh/metrics.averageW;
      const enoughPower=input.sourceContinuousW>=metrics.continuousW;
      const enoughEnergy=input.sourceWh>=metrics.requiredWh;
      const outputOkay=input.sourceOutputVerified==='yes';
      if(enoughPower&&enoughEnergy&&outputOkay&&input.daytimeTest==='success'){
        actions.push('Mevcut üretici uyumlu kaynak, güç ve enerji sınırlarını ve uyanıkken yapılan kontrollü transfer testini karşılıyor. Yeni ürün almayın.');
        actions.push('Batarya durumunu, kabloyu ve aksesuar senaryosunu 90 gün sonra yeniden test edin.');
        return finalize('no_buy','Mevcut yedek güç yeterli',input,metrics,actions,warnings,evidence,commercial);
      }
      if(enoughPower&&enoughEnergy&&outputOkay&&input.daytimeTest==='untested'){
        actions.push('Yeni ürün almadan önce cihazı kullanırken uyanık olduğunuz bir zamanda üretici talimatına uygun kontrollü güç aktarım testi yapın.');
        actions.push('Gece tedavisi sırasında deneme amacıyla enerjiyi kesmeyin.');
        return finalize('test_first','Kapasite yeterli görünüyor; önce güvenli test',input,metrics,actions,warnings,evidence,commercial);
      }
      if(input.daytimeTest==='failed')warnings.push('Mevcut kaynak kontrollü testte cihazı sürdüremedi. Aynı bağlantıyı tedavi sırasında güvenilir kabul etmeyin.');
      if(!enoughPower)warnings.push(`Mevcut sürekli güç ${input.sourceContinuousW||0} W; ön sınır ${metrics.continuousW} W.`);
      if(!enoughEnergy)warnings.push(`Mevcut nominal enerji ${input.sourceWh||0} Wh; hedef yaklaşık ${metrics.requiredWh} Wh.`);
      if(!outputOkay)warnings.push('Çıkış gerilimi, frekans, DC dönüştürücü veya dalga biçimi uyumu doğrulanmadı.');
    }

    if(input.scenario==='active'){
      warnings.push('Aktif kesinti sırasında ürün teslimatı anlık tedavi çözümü değildir; affiliate yolu kapalıdır.');
      actions.push('Elinizde üretici onaylı ve daha önce test edilmiş kaynak varsa talimatına göre kullanın.');
      actions.push('Tedaviyi sürdüremiyorsanız sağlık profesyoneli/cihaz sağlayıcısıyla iletişim kurun; acil belirti varsa 112’yi arayın.');
      return finalize('active_outage','Aktif kesintide sağlık planı öncelikli',input,metrics,actions,warnings,evidence,commercial);
    }

    if(input.deviceType==='bipap'){
      warnings.push('BiPAP/bilevel cihazlarda güç ve klinik bağımlılık modele ve tedavi planına daha duyarlıdır; tüketici ürün rotası açılmaz.');
      actions.push('Tam model batarya rehberini cihaz sağlayıcısı veya uyku merkeziyle doğrulayın.');
      return finalize('clinical','BiPAP için profesyonel doğrulama',input,metrics,actions,warnings,evidence,commercial);
    }

    if(metrics.continuousW>200||metrics.requiredWh>2500||input.targetHours>16){
      warnings.push('Güç veya süre ihtiyacı tüketici tipi kısa liste sınırını aşıyor.');
      actions.push('Batarya kapasitesi, şarj süresi, yedeklilik ve klinik sürekliliği profesyonel planla doğrulayın.');
      return finalize('professional','Yüksek süre/güç için profesyonel plan',input,metrics,actions,warnings,evidence,commercial);
    }

    commercial.allowed=true;
    commercial.category=input.powerPath==='manufacturer_battery'?'manufacturer_battery':'portable_power';
    commercial.url='/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi?from=cpap';
    commercial.reason='Tam model, üretici alternatif güç rehberi, aksesuar kapsamı ve gerçek kapasite açığı doğrulandı.';
    actions.push('Önce tam modele özgü üretici bataryası veya DC dönüştürücü seçeneğini karşılaştırın; genel power station yalnız üretici uyumluluğu açıkça destekliyorsa değerlendirilir.');
    actions.push('Seçilecek kaynakta sürekli W, nominal Wh, doğru çıkış yolu ve kablo/dönüştürücü referansını yeniden doğrulayın.');
    actions.push('İlk denemeyi uyanıkken ve cihaz sağlayıcısının talimatına göre yapın; gece tedavisinde plansız test yapmayın.');
    return finalize('capacity_gap','Yedek güç açığı doğrulandı',input,metrics,actions,warnings,evidence,commercial);
  }

  function finalize(code,title,input,metrics,actions,warnings,evidence,commercial){
    return {code,title,input,metrics:{averageW:round(metrics.averageW),requiredWh:round(metrics.requiredWh),continuousW:round(metrics.continuousW),effectiveSourceWh:round(metrics.effectiveSourceWh),runtimeHours:round(metrics.runtimeHours,2),efficiency:metrics.efficiency,usedUpperBound:metrics.usedUpperBound},actions,warnings,evidence,commercial};
  }

  function technicalReport(result){
    return {
      schemaVersion:1,
      generatedAt:new Date().toISOString(),
      tool:'ALO186 CPAP/APAP/BiPAP Yedek Güç Uygunluğu',
      decision:result.code,
      title:result.title,
      technicalInput:{
        scenario:result.input.scenario,
        deviceType:result.input.deviceType,
        accessories:{humidifier:result.input.humidifier,heatedTube:result.input.heatedTube,included:result.input.accessoriesIncluded},
        maxW:result.input.maxW,
        targetHours:result.input.targetHours,
        powerPath:result.input.powerPath,
        sourceStatus:result.input.sourceStatus
      },
      metrics:result.metrics,
      actions:result.actions,
      warnings:result.warnings,
      commercialAllowed:result.commercial.allowed,
      privacy:'Ad, iletişim, tanı, reçete, tedavi basıncı veya konum içermez. Yalnız kullanıcının cihazında oluşturulur.',
      disclaimer:'Bu çıktı tıbbi öneri, reçete değişikliği, cihaz onayı veya acil sağlık planı değildir.'
    };
  }

  function createIcs(result,now=new Date()){
    const start=new Date(now.getTime()+90*86400000);
    const stamp=(date)=>date.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z');
    const day=start.toISOString().slice(0,10).replace(/-/g,'');
    const description='Tam model batarya rehberini, kablo ve dönüştürücü referansını, batarya durumunu ve uyanıkken kontrollü transfer testini doğrula. Gece tedavisinde deneme amacıyla enerjiyi kesme.';
    return ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//CPAP Backup Check//TR','CALSCALE:GREGORIAN','BEGIN:VEVENT',`UID:alo186-cpap-${stamp(now)}@alo186.com`,`DTSTAMP:${stamp(now)}`,`DTSTART;VALUE=DATE:${day}`,`SUMMARY:CPAP yedek güç 90 günlük kontrolü`,`DESCRIPTION:${description}`,'END:VEVENT','END:VCALENDAR'].join('\r\n');
  }

  function download(win,content,name,type){
    const blob=new win.Blob([content],{type});
    const url=win.URL.createObjectURL(blob);
    const link=win.document.createElement('a');link.href=url;link.download=name;link.click();
    win.setTimeout(()=>win.URL.revokeObjectURL(url),500);
  }

  function mount(doc,win){
    const form=doc.getElementById('cpapForm');
    if(!form)return;
    const resultBox=doc.getElementById('result');
    const commerce=doc.getElementById('commerce');
    const professional=doc.getElementById('professional');
    let lastResult=null;

    const syncFields=()=>{
      const mode=form.elements.energyMode.value;
      doc.querySelectorAll('[data-energy]').forEach((node)=>{node.hidden=node.dataset.energy!==mode;});
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
      if(result.metrics.requiredWh!==null)metrics.append(metric('Nominal enerji hedefi',`${result.metrics.requiredWh} Wh`));
      if(result.metrics.runtimeHours!==null)metrics.append(metric('Mevcut kaynak yaklaşık süresi',`${result.metrics.runtimeHours} saat`));
      fillList('evidence',result.evidence);fillList('resultActions',result.actions);fillList('warnings',result.warnings);
      doc.getElementById('warningBox').hidden=!result.warnings.length;
      commerce.hidden=!result.commercial.allowed;
      professional.hidden=!['clinical','professional'].includes(result.code);
      if(result.commercial.allowed){
        const checks=[...commerce.querySelectorAll('input[type=checkbox]')];
        checks.forEach((input)=>{input.checked=false;});
        const link=doc.getElementById('productLink');
        const sync=()=>{const ready=checks.every((input)=>input.checked);link.classList.toggle('disabled',!ready);link.setAttribute('aria-disabled',String(!ready));if(ready)link.href=result.commercial.url;else link.removeAttribute('href');};
        commerce.addEventListener('change',sync,{once:false});sync();
      }
      resultBox.focus();
    }

    form.addEventListener('submit',(event)=>{
      event.preventDefault();
      const data=Object.fromEntries(new win.FormData(form).entries());
      data.emergency=form.elements.emergency.checked;
      render(evaluate(data));
    });
    form.addEventListener('reset',()=>win.setTimeout(()=>{syncFields();resultBox.hidden=true;commerce.hidden=true;professional.hidden=true;lastResult=null;},0));
    doc.getElementById('downloadJson').addEventListener('click',()=>{if(lastResult)download(win,JSON.stringify(technicalReport(lastResult),null,2),'alo186-cpap-yedek-guc-teknik-fis.json','application/json');});
    doc.getElementById('downloadIcs').addEventListener('click',()=>{if(lastResult)download(win,createIcs(lastResult),'alo186-cpap-90-gun-kontrol.ics','text/calendar');});
    doc.getElementById('printResult').addEventListener('click',()=>win.print());
  }

  return {evaluate,technicalReport,createIcs,mount};
});
