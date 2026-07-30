(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const n=value=>{
    if(value===null||value===undefined||value==='')return null;
    const parsed=Number(String(value).replace(',','.'));
    return Number.isFinite(parsed)?parsed:null;
  };
  const roundUp=(value,step=50)=>Math.ceil(value/step)*step;
  const unique=values=>[...new Set(values.filter(Boolean))];
  const result=(status,title,summary,extra={})=>({status,title,summary,commercialAllowed:false,categories:[],...extra});

  const CATEGORY_LABELS={
    power_station:'Power station sınıfı',
    generator:'İnverter jeneratör sınıfı',
    inverter:'Saf sinüs inverter + batarya sınıfı'
  };

  const TOOL_LABELS={
    drill:'Matkap / kırıcı-delici',
    grinder:'Taşlama',
    circular_saw:'Daire testere',
    compressor:'Hava kompresörü',
    shop_vac:'Sanayi tipi süpürge',
    welder:'İnverter kaynak makinesi',
    resistive:'Rezistif / elektronik yük',
    other_motor:'Diğer motorlu el aleti'
  };

  const START_MULTIPLIERS={
    electronic:1.8,
    normal:3,
    heavy:5,
    resistive:1.2
  };

  function architectureLabel(value){
    return ({power_station:'Taşınabilir power station',generator:'İnverter jeneratör',inverter:'Saf sinüs inverter + batarya'})[value]||value;
  }

  function calculate(input={}){
    if(input.emergency){
      return result('emergency','Kullanmayı bırakın ve enerjiyi kesin','Duman, kıvılcım, yanık kokusu, erime, hasarlı kablo, su teması veya elektrik çarpması riski varsa ekipmanı çalıştırmayın. Güvenli biçimde enerjisiz bırakın; yangın veya yaralanma riski varsa 112’yi arayın.');
    }
    if(input.criticalUse){
      return result('professional','İş güvenliği ve süreklilik tasarımı gerekli','Can güvenliği, kurtarma, yangın, tıbbi veya durması kabul edilemeyen işlerde tüketici tipi güç kaynağı tek başına yeterlilik kanıtı değildir. Devre, kaynak, yedeklilik ve çalışma prosedürü birlikte projelendirilmelidir.');
    }

    const scenario=input.scenario||'planning';
    const toolType=input.toolType||'unknown';
    const supply=input.supply||'unknown';
    const connection=input.connection||'unknown';
    const labelMethod=input.labelMethod||'watts';
    const environment=input.environment||'dry';
    const extensionStatus=input.extensionStatus||'unknown';
    const groundingVerified=input.groundingVerified||'unknown';
    const startClass=input.startClass||'unknown';
    const dutyCyclePct=n(input.dutyCyclePct);
    const otherW=n(input.otherW)??0;
    const targetHours=n(input.targetHours);

    if(!Object.hasOwn(TOOL_LABELS,toolType)){
      return result('evidence_required','Ekipman türünü doğrulayın','Matkap, taşlama, testere, kompresör, sanayi tipi süpürge, kaynak makinesi veya diğer yük sınıflarından birini seçin.');
    }
    if(supply!=='230v'){
      return result('professional','Trifaze veya belirsiz besleme için profesyonel seçim gerekli','400 V trifaze veya besleme türü bilinmeyen ekipman, tüketici tipi power station ya da portatif inverter üzerinden seçilmemelidir. Faz, koruma, kalkış ve bağlantı düzenini yetkili uzman doğrulamalıdır.');
    }
    if(connection!=='plug'){
      return result('professional','Sabit bağlantılı ekipman için proje doğrulaması gerekli','Sabit bağlı ekipman; devre kesiti, koruma, ayırma, topraklama ve kaynak koordinasyonuyla birlikte değerlendirilmelidir.');
    }
    if(toolType==='welder'){
      return result('professional','Kaynak makinesi için üretici giriş verisi ve profesyonel doğrulama gerekli','Kaynak akımı, görev çevrimi ve çıkış amperi şebekeden çekilen gerçek giriş gücü değildir. Tam modelin azami giriş akımı, güç faktörü, jeneratör önerisi ve koruma düzeni doğrulanmadan ürün seçmeyin.');
    }
    if(environment==='wet'){
      return result('unsafe','Islak ortamda çalıştırmayın','Su, ıslak zemin, yağmur veya kondenzasyon bulunan ortamda taşınabilir kaynak ve uzatma kablosu kullanmayın. IP sınıfı, RCD, bağlantılar ve iş güvenliği yetkili kişi tarafından doğrulanmalıdır.');
    }
    if(extensionStatus==='unsafe'){
      return result('unsafe','Hasarlı veya uygunsuz uzatma kablosunu kullanmayın','Ezilmiş, ekli, ısınan, sarılı makara hâlindeki veya etiket akımı yetersiz kablo güç kaynağı seçimiyle güvenli hâle gelmez. Önce kablo uygunluk testine ilerleyin.',{nextTool:'/hesaplama/uzatma-kablosu-uygunluk/'});
    }
    if(extensionStatus!=='verified'){
      return result('evidence_required','Uzatma kablosu ve makara koşulu doğrulanmalı','Kablo kesiti, uzunluğu, etiket akımı, dış ortam/IP koşulu ve makaranın tamamen açıldığı doğrulanmadan kaynak gücü seçmeyin.',{nextTool:'/hesaplama/uzatma-kablosu-uygunluk/'});
    }
    if(groundingVerified==='no'){
      return result('unsafe','Koruma iletkeni olmadan çalıştırmayın','Topraklama gerektiren el aleti, kompresör veya metal gövdeli ekipmanı PE sürekliliği doğrulanmamış kaynakta kullanmayın. Adaptör veya dönüştürücü bu eksikliği gidermez.');
    }
    if(groundingVerified!=='yes'){
      return result('evidence_required','PE ve çıkış topraklama koşulu doğrulanmalı','Kaynağın koruma iletkeni, priz yapısı ve ekipmanın Class I/Class II durumu üretici belgeleriyle doğrulanmalıdır.');
    }
    if(!Object.hasOwn(START_MULTIPLIERS,startClass)){
      return result('evidence_required','Kalkış sınıfını doğrulayın','Elektronik yumuşak kalkış, normal motor, ağır kompresör veya rezistif/elektronik yük seçeneklerinden uygun olanı seçin.');
    }
    if(dutyCyclePct===null||dutyCyclePct<5||dutyCyclePct>100){
      return result('evidence_required','Görev çevrimini doğrulayın','Ekipmanın hedef süre içinde yaklaşık çalışma oranını %5–100 aralığında girin.');
    }
    if(targetHours===null||targetHours<0.25||targetHours>12){
      return result('evidence_required','Hedef süreyi doğrulayın','Toplam çalışma penceresini 0,25–12 saat aralığında girin.');
    }
    if(otherW<0||otherW>5000){
      return result('evidence_required','Eşzamanlı yükleri yeniden kontrol edin','Diğer yüklerin toplamı negatif olamaz ve bu tüketici aracı için 5 kW sınırını aşamaz.');
    }

    let runningW;
    if(labelMethod==='watts'){
      runningW=n(input.ratedW);
      if(runningW===null||runningW<=0||runningW>10000){
        return result('evidence_required','Etiket giriş wattı gerekli','Ekipmanın motor çıkış gücünü değil, şebekeden çektiği azami giriş wattını doğrulayın.');
      }
    }else if(labelMethod==='volts_amps'){
      const voltageV=n(input.voltageV);
      const currentA=n(input.currentA);
      const powerFactor=n(input.powerFactor);
      if(voltageV===null||voltageV<200||voltageV>250||currentA===null||currentA<=0||currentA>50||powerFactor===null||powerFactor<0.5||powerFactor>1){
        return result('evidence_required','V, A ve güç faktörü gerekli','Etiket wattı yoksa 200–250 V, giriş amperi ve 0,50–1,00 arası güç faktörünü üretici verisinden doğrulayın.');
      }
      runningW=voltageV*currentA*powerFactor;
    }else{
      return result('evidence_required','Etiket yöntemini seçin','Giriş wattı veya V × A × güç faktörü yönteminden birini seçin.');
    }

    const manufacturerPeakW=n(input.manufacturerPeakW);
    if(manufacturerPeakW!==null&&manufacturerPeakW<runningW){
      return result('evidence_required','Tepe güç çalışma gücünden düşük olamaz','Üretici başlangıç/tepe gücü değerini ve birimini yeniden kontrol edin.');
    }
    const multiplier=START_MULTIPLIERS[startClass];
    const estimatedStartW=manufacturerPeakW??runningW*multiplier;
    const totalRunningW=runningW+otherW;
    const requiredContinuousW=roundUp(totalRunningW*1.25,50);
    const requiredSurgeW=roundUp((estimatedStartW+otherW)*1.15,50);
    const averageW=runningW*(dutyCyclePct/100)+otherW;
    const requiredWh=roundUp(averageW*targetHours/(0.85*0.80),50);
    const metrics={
      toolLabel:TOOL_LABELS[toolType],
      runningW:Math.round(runningW),
      estimatedStartW:Math.round(estimatedStartW),
      totalRunningW:Math.round(totalRunningW),
      requiredContinuousW,
      requiredSurgeW,
      requiredWh,
      dutyCyclePct,
      targetHours,
      startMultiplier:manufacturerPeakW!==null?'Üretici tepe değeri':`${multiplier}× planlama katsayısı`
    };

    if(runningW>2500||requiredContinuousW>3500||requiredSurgeW>7000){
      return result('professional','Yüksek güçlü ekipman için profesyonel kaynak seçimi gerekli','Bu güç ve kalkış sınıfı; devre, kısa devre kapasitesi, koruma, kablo, jeneratör regülasyonu ve gerçek saha testiyle değerlendirilmelidir.',{metrics});
    }

    let architecture=input.preferredSource||'unsure';
    if(architecture==='unsure'){
      architecture=(requiredContinuousW<=1800&&requiredSurgeW<=3500&&targetHours<=4)?'power_station':'generator';
    }
    if(!['power_station','generator','inverter'].includes(architecture)){
      return result('evidence_required','Kaynak mimarisini doğrulayın','Taşınabilir power station, açık alanda jeneratör veya mevcut batarya bankı için inverter seçeneklerinden birini seçin.');
    }
    metrics.architecture=architecture;
    metrics.architectureLabel=architectureLabel(architecture);

    if(scenario==='active'){
      return result('active_event','Aktif kesintide geçici bağlantı kurmayın',`${requiredContinuousW} W sürekli, ${requiredSurgeW} W tepe ve bataryalı kaynakta yaklaşık ${requiredWh} Wh sınıfı hesaplandı. Ürün teslimatı anlık çözüm değildir; ters besleme, çoklayıcı, sarılı makara veya ıslak bağlantı kullanmayın.`,{metrics});
    }

    const sourceStatus=input.sourceStatus||'none';
    if(sourceStatus!=='none'){
      const sourceArchitecture=sourceStatus.replace('_existing','');
      if(!['power_station','generator','inverter'].includes(sourceArchitecture)){
        return result('evidence_required','Mevcut kaynak türünü doğrulayın','Power station, jeneratör veya inverter seçeneklerinden birini seçin.',{metrics});
      }
      metrics.architecture=sourceArchitecture;
      metrics.architectureLabel=architectureLabel(sourceArchitecture);
      const existingContinuousW=n(input.existingContinuousW);
      const existingSurgeW=n(input.existingSurgeW);
      if(existingContinuousW===null||existingSurgeW===null){
        return result('evidence_required','Mevcut kaynağın sürekli ve tepe gücü gerekli',`En az ${requiredContinuousW} W sürekli ve ${requiredSurgeW} W kısa süreli tepe gücünü üretici etiketinden doğrulayın.`,{metrics});
      }
      if(input.existingOutputVerified!=='yes'||input.existingGroundingVerified!=='yes'){
        return result('evidence_required','Çıkış ve koruma koşulları eksik','230 V / 50 Hz çıkış, priz akım sınırı, koruma iletkeni ve üreticinin motorlu yük kullanım koşulu birlikte doğrulanmalıdır.',{metrics});
      }
      if(sourceArchitecture==='generator'&&input.generatorSafetyVerified!=='yes'){
        return result('evidence_required','Jeneratör güvenli kullanım koşulları gerekli','Jeneratör yalnız açık alanda, egzoz ve karbonmonoksit güvenliği doğrulanarak kullanılmalıdır. Güvenlik testini tamamlamadan ürün kararı vermeyin.',{metrics,nextTool:'/hesaplama/jenerator-guvenli-kullanim-testi/'});
      }
      if(sourceArchitecture!=='generator'){
        const existingWh=n(input.existingWh);
        if(existingWh===null||input.existingPureSine!=='yes'){
          return result('evidence_required','Batarya enerjisi ve saf sinüs kanıtı gerekli',`Bataryalı kaynakta en az ${requiredWh} Wh nominal enerji ve saf sinüs 230 V / 50 Hz çıkış birlikte doğrulanmalıdır.`,{metrics});
        }
      }
      const gaps=[];
      if(existingContinuousW<requiredContinuousW)gaps.push(`${requiredContinuousW-existingContinuousW} W sürekli güç`);
      if(existingSurgeW<requiredSurgeW)gaps.push(`${requiredSurgeW-existingSurgeW} W tepe güç`);
      if(sourceArchitecture!=='generator'){
        const existingWh=n(input.existingWh);
        if(existingWh<requiredWh)gaps.push(`${requiredWh-existingWh} Wh enerji`);
      }
      if(input.startTest==='failed'){
        return result('professional','Gerçek başlatma testi başarısız — daha büyük ürün satın almadan kök nedeni bulun','Kaynak etiketleri yeterli görünse bile gerilim çökmesi, koruma açması, kablo düşümü veya motor davranışı başlatmayı engelliyor olabilir. Kablo ve kaynak ölçümü yapılmalıdır.',{metrics});
      }
      if(input.startTest!=='success'){
        return result('evidence_required','Kontrollü gerçek başlatma testi gerekli','Etiket değerleri uygun görünse bile ekipman, uygun kablo ve güvenli ortamda kontrollü olarak başlatılmadan yeterlilik sonucu verilmez.',{metrics});
      }
      if(gaps.length===0){
        return result('no_buy','Mevcut kaynak yeterli — yeni ürün almayın',`Mevcut ${architectureLabel(sourceArchitecture)}; ${requiredContinuousW} W sürekli, ${requiredSurgeW} W tepe${sourceArchitecture==='generator'?'':` ve ${requiredWh} Wh`} ihtiyacını, çıkış/topraklama kanıtını ve gerçek başlatma testini karşılıyor.`,{metrics});
      }
      return result('conditional_purchase','Mevcut kaynakta doğrulanmış kapasite açığı var',`${gaps.join(', ')} eksiği bulundu. Yalnız bu eşikleri karşılayan ${architectureLabel(sourceArchitecture)} sınıfına ilerleyin.`,{metrics,categories:[sourceArchitecture],commercialAllowed:true});
    }

    const category=architecture;
    const generatorNote=architecture==='generator'?' Jeneratör için açık alan, egzoz ve CO güvenlik testini ayrıca tamamlayın.':'';
    return result('conditional_purchase','Yedek güç sınıfı hesaplandı',`${architectureLabel(architecture)} için en az ${requiredContinuousW} W sürekli ve ${requiredSurgeW} W tepe güç${architecture==='generator'?'':`, yaklaşık ${requiredWh} Wh nominal enerji`} gerekir.${generatorNote} Üretici motorlu yük koşulunu ve gerçek başlatma testini doğrulayın.`,{metrics,categories:[category],commercialAllowed:true,nextTool:architecture==='generator'?'/hesaplama/jenerator-guvenli-kullanim-testi/':null});
  }

  const STATUS_LABELS={
    emergency:'Acil',unsafe:'Kullanmayın',professional:'Profesyonel',evidence_required:'Kanıt gerekli',
    active_event:'Aktif kesinti',no_buy:'Satın alma yok',conditional_purchase:'Koşullu ürün'
  };

  function readForm(doc){
    const id=name=>doc.getElementById(name);
    const value=name=>id(name)?.value;
    const checked=name=>Boolean(id(name)?.checked);
    return{
      emergency:checked('emergency'),criticalUse:checked('criticalUse'),scenario:value('scenario'),
      toolType:value('toolType'),supply:value('supply'),connection:value('connection'),
      labelMethod:value('labelMethod'),ratedW:value('ratedW'),voltageV:value('voltageV'),
      currentA:value('currentA'),powerFactor:value('powerFactor'),manufacturerPeakW:value('manufacturerPeakW'),
      startClass:value('startClass'),dutyCyclePct:value('dutyCyclePct'),otherW:value('otherW'),
      targetHours:value('targetHours'),environment:value('environment'),extensionStatus:value('extensionStatus'),
      groundingVerified:value('groundingVerified'),preferredSource:value('preferredSource'),sourceStatus:value('sourceStatus'),
      existingContinuousW:value('existingContinuousW'),existingSurgeW:value('existingSurgeW'),existingWh:value('existingWh'),
      existingPureSine:value('existingPureSine'),existingOutputVerified:value('existingOutputVerified'),
      existingGroundingVerified:value('existingGroundingVerified'),generatorSafetyVerified:value('generatorSafetyVerified'),
      startTest:value('startTest')
    };
  }

  function mount(doc){
    const form=doc.getElementById('toolPowerForm');
    if(!form)return;
    const $=id=>doc.getElementById(id);
    const toggle=()=>{
      const byWatts=$('labelMethod').value==='watts';
      $('wattsFields').classList.toggle('hidden',!byWatts);
      $('vaFields').classList.toggle('hidden',byWatts);
      const existing=$('sourceStatus').value;
      $('existingFields').classList.toggle('hidden',existing==='none');
      $('batteryFields').classList.toggle('hidden',!['power_station_existing','inverter_existing'].includes(existing));
      $('generatorFields').classList.toggle('hidden',existing!=='generator_existing');
    };
    ['labelMethod','sourceStatus'].forEach(id=>$(id)?.addEventListener('change',toggle));
    toggle();

    form.addEventListener('submit',event=>{
      event.preventDefault();
      const out=calculate(readForm(doc));
      const box=$('result');
      box.className=`panel result status-${out.status}`;
      box.hidden=false;
      $('resultBadge').textContent=STATUS_LABELS[out.status]||out.status;
      $('resultTitle').textContent=out.title;
      $('resultSummary').textContent=out.summary;
      const m=out.metrics;
      $('metrics').innerHTML=m?[
        ['Ekipman',m.toolLabel],['Çalışma gücü',`${m.runningW} W`],['Tahmini kalkış',`${m.estimatedStartW} W`],
        ['Sürekli kaynak alt sınırı',`${m.requiredContinuousW} W`],['Tepe kaynak alt sınırı',`${m.requiredSurgeW} W`],
        ['Bataryalı kaynak enerjisi',`${m.requiredWh} Wh`],['Hesap yönü',m.architectureLabel||'—'],['Kalkış verisi',m.startMultiplier]
      ].map(([label,value])=>`<article><span>${label}</span><strong>${value}</strong></article>`).join(''):'';
      const next=$('nextTool');
      if(out.nextTool){next.href=out.nextTool;next.classList.remove('hidden');}else{next.removeAttribute('href');next.classList.add('hidden');}
      const commerce=$('commerce');
      commerce.classList.toggle('hidden',!out.commercialAllowed);
      commerce.dataset.categories=JSON.stringify(out.categories||[]);
      ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>{$(id).checked=false;});
      $('productLinks').innerHTML='';
      box.scrollIntoView({behavior:'smooth',block:'start'});
      box.focus({preventScroll:true});
      if(root.Alo186Track)root.Alo186Track('power_tool_backup_result',{status:out.status,architecture:m?.architecture||'none',categories:(out.categories||[]).join(',')});
    });

    const refreshGate=()=>{
      const commerce=$('commerce');
      const enabled=!commerce.classList.contains('hidden')&&['actualNeed','technicalCheck','affiliateCheck'].every(id=>$(id).checked);
      const target=$('productLinks');
      target.innerHTML='';
      if(!enabled)return;
      const categories=JSON.parse(commerce.dataset.categories||'[]');
      categories.forEach(category=>{
        const link=doc.createElement('a');
        link.className='button primary';
        link.href=`../../akilli-urun-secimi?kategori=${encodeURIComponent(category)}&kaynak=el-aleti-yedek-guc`;
        link.textContent=`${CATEGORY_LABELS[category]||category} seçeneklerini aç`;
        target.appendChild(link);
      });
    };
    ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>$(id)?.addEventListener('change',refreshGate));
  }

  return{calculate,mount,CATEGORY_LABELS,TOOL_LABELS,START_MULTIPLIERS,architectureLabel};
});
