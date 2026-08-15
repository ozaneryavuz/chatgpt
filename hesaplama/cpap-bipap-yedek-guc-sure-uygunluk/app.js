(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const AFFILIATE_TAG='alo186rehber-21';
  const AC_EFFICIENCY=0.85;
  const USABLE_FRACTION=0.80;
  const OUTPUT_HEADROOM=1.25;

  const num=(value)=>{
    if(value===null||value===undefined||value==='')return null;
    const parsed=Number(String(value).replace(',','.'));
    return Number.isFinite(parsed)?parsed:null;
  };
  const roundUp=(value,step)=>Math.ceil(value/step)*step;
  const result=(status,title,summary,extra={})=>({status,title,summary,commercialAllowed:false,searchUrl:null,...extra});

  function calculate(input={}){
    if(input.emergency){
      return result('emergency','Ürün aramayın; acil sağlık planını uygulayın','Nefes darlığı, morarma, bilinç değişikliği veya güç kaybı nedeniyle cihazın hayati desteği kesildiyse 112’yi arayın ve size verilen klinik acil planı uygulayın. Bütün ticari yollar kapalıdır.');
    }
    if(input.lifeSustaining==='yes'||['ventilator','oxygen_concentrator'].includes(input.deviceType)){
      return result('professional','Yaşam destek cihazı için klinik yedeklilik gerekir','Ventilatör, yaşamı sürdürmek için zorunlu solunum desteği veya oksijen konsantratörü; internetten UPS/power station seçimiyle yönetilmez. Hekim, evde bakım sağlayıcısı, cihaz üreticisi ve elektrik dağıtım acil planı birlikte kurulmalıdır.');
    }
    if(input.lifeSustaining!=='no')return result('evidence_required','Cihaz bağımlılık düzeyini doğrulayın','Bu aracın düşük riskli CPAP/APAP/BiPAP ön seçimine geçebilmesi için cihazın yaşamı sürdürmek amacıyla kullanılan ventilatör olmadığını doğrulayın.');
    if(!['cpap','apap','bipap'].includes(input.deviceType||''))return result('evidence_required','Cihaz türünü doğrulayın','CPAP, APAP veya BiPAP seçin. Diğer solunum ve oksijen cihazları profesyonel yedeklilik planına gider.');
    if(input.wetOrDamaged==='yes')return result('stop_use','Islak, hasarlı veya aşırı ısınan cihazı kullanmayın','Cihaz, adaptör, kablo veya batarya ıslak, çatlak, şişmiş, yanık kokulu ya da aşırı sıcaksa prize veya yedek kaynağa bağlamayın; üretici/yetkili servisle görüşün.');
    if(input.wetOrDamaged!=='no')return result('evidence_required','Cihaz ve güç zincirini fiziksel olarak doğrulayın','Cihaz, adaptör, kablo ve bataryanın kuru, sağlam ve olağandışı ısı/koku göstermediğini doğrulayın.');
    if(input.activeOutage==='yes')return result('active_outage','Aktif kesintide teslimatı çözüm saymayın','Mevcut üretici onaylı yedek kaynağı ve sağlık profesyonelinizin kesinti planını kullanın. Yeni ürün teslimatı mevcut geceyi çözmez; doğaçlama adaptör veya polaritesi belirsiz DC kablo kullanmayın.');
    if(input.activeOutage!=='no')return result('evidence_required','Aktif kesinti durumunu belirtin','Geleceğe yönelik hazırlık ile devam eden elektrik kesintisi ayrılmalıdır.');
    if(input.clinicalPlan!=='yes')return result('evidence_required','Sağlık profesyoneli kesinti planı gerekli','Tedavinin kesilmesi, nemlendirici/ısıtmalı hortum kapatılması veya ayar değişikliği yalnız sağlık profesyoneli ve üretici talimatıyla değerlendirilmelidir.');
    if(input.manufacturerCompatibility!=='yes')return result('evidence_required','Üretici güç ve batarya uyumluluğu gerekli','Tam cihaz modeli için üreticinin AC, DC, batarya veya jeneratör kullanım talimatını doğrulayın. Satıcı açıklaması tek başına yeterli değildir.');
    if(input.recallChecked==='no')return result('stop_use','Aktif geri çağırma veya güvenlik uyarısını çözün','Cihaz modelinde aktif güvenlik düzeltmesi/geri çağırma varsa üretici ve sağlık hizmeti sağlayıcısının talimatını uygulayın; affiliate yolu kapalıdır.');
    if(input.recallChecked!=='yes')return result('evidence_required','Geri çağırma ve güvenlik uyarısı kontrolü gerekli','Tam marka-modeli üretici ve resmî tıbbi cihaz güvenlik kaynaklarında kontrol edin.');

    const model=String(input.deviceModel||'').trim();
    const configurationW=num(input.configurationW);
    const targetHours=num(input.targetHours);
    if(model.length<3)return result('evidence_required','Tam cihaz marka-modeli gerekli','Ürün etiketi veya üretici kılavuzundaki tam model kodunu girin. Sağlık bilgisi veya kullanıcı adı girmeyin.');
    if(configurationW===null||configurationW<=0||configurationW>500)return result('evidence_required','Tam kullanım yapılandırmasının watt değeri gerekli','Nemlendirici ve ısıtmalı hortum dahil kullanılacak gerçek yapılandırma için üreticinin azami/planlama watt değerini girin. Etiketin yalnız şebeke INPUT değerini yanlış yorumlamayın.');
    if(targetHours===null||targetHours<1||targetHours>72)return result('evidence_required','Hedef süreyi kontrol edin','Hedef çalışma süresi 1–72 saat arasında olmalıdır. Uzun süreli afet planı sağlık hizmeti sağlayıcısı ve üreticiyle yapılmalıdır.');
    if(input.configurationVerified!=='yes')return result('evidence_required','Nemlendirici ve hortum yapılandırmasını doğrulayın','Girilen watt değerinin kullanacağınız basınç, nemlendirici ve ısıtmalı hortum yapılandırmasını kapsadığını üretici belgesinden doğrulayın.');
    if(input.outputCompatibility==='no')return result('stop_use','Çıkış tipi veya adaptör uyumsuz','Üretici onayı olmayan DC dönüştürücü, ters polarite, farklı voltaj veya uygun olmayan AC dalga biçimi kullanmayın.');
    if(input.outputCompatibility!=='yes')return result('evidence_required','AC/DC çıkış uyumluluğu kanıtı gerekli','Saf sinüs AC veya üretici onaylı DC kablo/dönüştürücü seçimini tam model için doğrulayın.');

    const requiredContinuousW=roundUp(configurationW*OUTPUT_HEADROOM,10);
    const requiredNominalWh=roundUp((configurationW*targetHours)/AC_EFFICIENCY/USABLE_FRACTION,10);
    const metrics={configurationW,requiredContinuousW,requiredNominalWh,targetHours};

    if(input.fixedInstallation==='yes'||input.generatorTransfer==='yes'){
      return result('professional','Sabit tesisat veya jeneratör transferi profesyonel tasarım ister','Tıbbi cihaz için sabit UPS, transfer panosu, jeneratör veya çok kaynaklı besleme; seçicilik, nötr-toprak düzeni, bakım, alarm ve klinik acil planla projelendirilmelidir.',{metrics});
    }
    if(input.fixedInstallation!=='no'||input.generatorTransfer!=='no')return result('evidence_required','Bağlantı yöntemini doğrulayın','Bu araç yalnız üretici onaylı, fişli ve taşınabilir güç yolunu ön değerlendirir. Sabit bağlantı ve jeneratör transferi profesyonel kapsamdadır.',{metrics});

    const existing=input.existingSource||'unknown';
    if(existing==='unknown')return result('evidence_required','Mevcut yedek kaynak durumunu belirtin','Mevcut UPS/power station, üretici bataryası veya kaynak yok seçimini yapın.',{metrics});
    if(existing!=='none'){
      const sourceW=num(input.sourceContinuousW);
      const sourceWh=num(input.sourceWh);
      if(sourceW===null||sourceWh===null||sourceW<=0||sourceWh<=0)return result('evidence_required','Mevcut kaynağın W ve Wh değerleri gerekli','Sürekli çıkış gücü ile kullanılabilir/nominal enerji kapasitesini üretici veri sayfasından girin.',{metrics});
      const estimatedRuntimeHours=Math.round(((sourceWh*AC_EFFICIENCY*USABLE_FRACTION)/configurationW)*10)/10;
      metrics.sourceContinuousW=sourceW;metrics.sourceWh=sourceWh;metrics.estimatedRuntimeHours=estimatedRuntimeHours;
      const gaps=[];
      if(sourceW<requiredContinuousW)gaps.push('sürekli W');
      if(sourceWh<requiredNominalWh)gaps.push('Wh');
      if(input.transferTest!=='yes')gaps.push('şebeke kesilme/geçiş testi');
      if(input.actualNightTest!=='yes')gaps.push('gözetimli gerçek gece testi');
      if(gaps.length===0)return result('no_buy','Mevcut yedek kaynak yeterli; yeni ürün almayın','Güç, enerji, üretici uyumluluğu, geçiş ve gerçek kullanım testi doğrulandı. Batarya sağlığını ve 90 günlük yeniden testi sürdürün.',{metrics});
      return result('gap_found','Mevcut kaynakta doğrulanmış teknik açık var',`Eksik koşullar: ${gaps.join(', ')}. Yalnız bu açığı kapatan kaynağı değerlendirin; tedavi ayarını değiştirmeyin.`,{metrics,gaps});
    }

    const query=`${model} uyumlu saf sinüs power station ${requiredContinuousW}W ${requiredNominalWh}Wh`;
    return result('conditional_purchase','Yalnız üretici onaylı güç sınıfına ilerleyin','Amazon sonucu tıbbi veya teknik onay değildir. Tam model, sürekli W, Wh, saf sinüs/üretici DC uyumu, iade koşulu ve gerçek gözetimli test yeniden doğrulanmalıdır.',{metrics,commercialAllowed:true,searchUrl:`https://www.amazon.com.tr/s?k=${encodeURIComponent(query)}&tag=${AFFILIATE_TAG}`});
  }

  function download(doc,filename,text,type){
    const blob=new Blob([text],{type});
    const url=URL.createObjectURL(blob);
    const link=doc.createElement('a');link.href=url;link.download=filename;link.click();
    setTimeout(()=>URL.revokeObjectURL(url),0);
  }
  function stamp(date){return date.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z');}

  function mount(doc){
    const form=doc.getElementById('cpapForm');if(!form)return;
    const resultBox=doc.getElementById('result');const commerce=doc.getElementById('commerce');const affiliateLink=doc.getElementById('affiliateLink');
    const jsonButton=doc.getElementById('jsonButton');const icsButton=doc.getElementById('icsButton');
    let last=null;
    const value=(id)=>doc.getElementById(id)?.value||'';
    const read=()=>({emergency:doc.getElementById('emergency').checked,lifeSustaining:value('lifeSustaining'),deviceType:value('deviceType'),wetOrDamaged:value('wetOrDamaged'),activeOutage:value('activeOutage'),clinicalPlan:value('clinicalPlan'),manufacturerCompatibility:value('manufacturerCompatibility'),recallChecked:value('recallChecked'),deviceModel:value('deviceModel'),configurationW:value('configurationW'),targetHours:value('targetHours'),configurationVerified:value('configurationVerified'),outputCompatibility:value('outputCompatibility'),fixedInstallation:value('fixedInstallation'),generatorTransfer:value('generatorTransfer'),existingSource:value('existingSource'),sourceContinuousW:value('sourceContinuousW'),sourceWh:value('sourceWh'),transferTest:value('transferTest'),actualNightTest:value('actualNightTest')});
    const gates=()=>[...doc.querySelectorAll('.gate input[type="checkbox"]')];
    const closeCommerce=()=>{commerce.hidden=true;affiliateLink.hidden=true;affiliateLink.removeAttribute('href');gates().forEach((gate)=>{gate.checked=false;});};
    function render(res){
      last=res;resultBox.hidden=false;resultBox.dataset.status=res.status;
      const metrics=res.metrics?`<div class="metrics"><article><span>Yapılandırma yükü</span><strong>${res.metrics.configurationW} W</strong></article><article><span>Gerekli sürekli çıkış</span><strong>${res.metrics.requiredContinuousW} W</strong></article><article><span>Gerekli nominal enerji</span><strong>${res.metrics.requiredNominalWh} Wh</strong></article><article><span>Yaklaşık mevcut süre</span><strong>${res.metrics.estimatedRuntimeHours??'—'} saat</strong></article></div>`:'';
      resultBox.innerHTML=`<span class="badge">${res.status.replaceAll('_',' ')}</span><h2>${res.title}</h2><p>${res.summary}</p>${metrics}`;
      closeCommerce();if(res.commercialAllowed)commerce.hidden=false;jsonButton.disabled=false;icsButton.disabled=false;resultBox.focus();
    }
    form.addEventListener('submit',(event)=>{event.preventDefault();render(calculate(read()));});
    form.addEventListener('reset',()=>setTimeout(()=>{last=null;resultBox.hidden=true;resultBox.innerHTML='';closeCommerce();jsonButton.disabled=true;icsButton.disabled=true;},0));
    gates().forEach((gate)=>gate.addEventListener('change',()=>{const enabled=gates().every((item)=>item.checked)&&last?.commercialAllowed&&last?.searchUrl;if(enabled){affiliateLink.href=last.searchUrl;affiliateLink.rel='sponsored nofollow noopener';affiliateLink.hidden=false;}else{affiliateLink.hidden=true;affiliateLink.removeAttribute('href');}}));
    jsonButton.addEventListener('click',()=>{if(!last)return;download(doc,'alo186-cpap-yedek-guc-sonucu.json',JSON.stringify({generatedAt:new Date().toISOString(),tool:'ALO186 CPAP/BiPAP Yedek Güç Uygunluk Testi',personalDataCollected:false,result:last},null,2),'application/json');});
    icsButton.addEventListener('click',()=>{if(!last)return;const date=new Date();date.setDate(date.getDate()+90);const ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//CPAP Backup Retest//TR','BEGIN:VEVENT',`UID:alo186-cpap-${Date.now()}@alo186.com`,`DTSTAMP:${stamp(new Date())}`,`DTSTART:${stamp(date)}`,'SUMMARY:CPAP/BiPAP yedek güç testini yenile','DESCRIPTION:Üretici uyumluluğu, geri çağırma, W, Wh, geçiş, batarya sağlığı ve gözetimli gerçek kullanım testini yeniden doğrulayın.','END:VEVENT','END:VCALENDAR'].join('\r\n');download(doc,'alo186-cpap-yedek-guc-90-gun.ics',ics,'text/calendar');});
  }
  return{calculate,mount,AFFILIATE_TAG,AC_EFFICIENCY,USABLE_FRACTION,OUTPUT_HEADROOM};
});
