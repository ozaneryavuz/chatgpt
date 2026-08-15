(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186AirConditionerBackup=api;
  if(root&&root.document)api.init(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const SQRT3=Math.sqrt(3);
  const PF_DEFAULT=0.9;
  const RESERVE=1.25;
  const SURGE_RESERVE=1.15;
  const BATTERY_EFF=0.85;
  const USABLE=0.8;
  const START_MULTIPLIER={inverter_split:1.5,fixed_split:4.5,portable:4,window:4};
  const ROUTE='/hesaplama/klima-yedek-guc-kalkis-uygunluk/';

  const CATEGORY_LINKS={
    power_station:{label:'Power station ürün sınıfını aç',href:'../../akilli-urun-secimi?kategori=power_station'},
    generator:{label:'Jeneratör ürün sınıfını aç',href:'../../akilli-urun-secimi?kategori=generator'},
    inverter:{label:'İnverter ürün sınıfını aç',href:'../../akilli-urun-secimi?kategori=inverter'}
  };
  const TOOL_LINKS={
    power_station:{label:'Power station kapasite testini aç',href:'../power-station-kapasite-eps-uygunluk/'},
    generator:{label:'Jeneratör güç hesabını aç',href:'../jenerator-gucu-secimi/'},
    inverter:{label:'İnverter uygunluk testini aç',href:'../inverter-uygunluk/'},
    compare:{label:'Yedek güç çözüm seçiciyi aç',href:'../yedek-guc-cozum-secici/'},
    handoff:{label:'Elektrikçi iş emri özetini aç',href:'../elektrikci-is-emri-ozeti/'}
  };

  const n=value=>{
    const raw=String(value??'').trim().replace(',','.');
    if(!raw)return null;
    const parsed=Number(raw);
    return Number.isFinite(parsed)?parsed:null;
  };
  const round=(value,digits=0)=>Number(value.toFixed(digits));
  const uniq=values=>[...new Set(values.filter(Boolean))];

  function base(status,title,summary){
    return {status,title,summary,issues:[],steps:[],metrics:null,commerceCategories:[],toolKeys:[],commerceClosed:true};
  }

  function calculations(input={}){
    const phase=input.phase==='three'?3:input.phase==='single'?1:null;
    const labelW=n(input.labelW);
    const voltage=n(input.voltage);
    const current=n(input.ratedCurrent);
    const pf=n(input.powerFactor)??PF_DEFAULT;
    const otherW=n(input.otherLoadW)??0;
    const hours=n(input.targetHours);
    if(!phase||!hours||hours<=0)return null;

    let runningW=labelW;
    if(!(runningW>0)&&voltage>0&&current>0){
      runningW=(phase===3?SQRT3:1)*voltage*current*pf;
    }
    if(!(runningW>0))return null;

    const explicitStartup=n(input.startupW);
    const multiplier=START_MULTIPLIER[input.unitType]??null;
    if(!(explicitStartup>0)&&!multiplier)return null;
    const startupW=explicitStartup>0?explicitStartup:runningW*multiplier;
    const totalRunningW=runningW+otherW;
    const requiredContinuousW=totalRunningW*RESERVE;
    const requiredSurgeW=(startupW+otherW)*SURGE_RESERVE;
    const requiredWh=totalRunningW*hours/BATTERY_EFF/USABLE;
    const approximateVA=requiredContinuousW/0.85;

    return {
      phase,labelW:labelW>0?round(labelW):null,voltage:voltage>0?round(voltage):null,current:current>0?round(current,2):null,
      pf:round(pf,2),pfAssumed:n(input.powerFactor)===null,runningW:round(runningW),startupW:round(startupW),
      startupAssumed:!(explicitStartup>0),multiplier:explicitStartup>0?null:multiplier,
      otherW:round(otherW),totalRunningW:round(totalRunningW),requiredContinuousW:round(requiredContinuousW),
      requiredSurgeW:round(requiredSurgeW),requiredWh:round(requiredWh),approximateVA:round(approximateVA),targetHours:round(hours,2)
    };
  }

  function evaluate(input={}){
    if(input.emergency){
      const result=base('emergency','Acil: klimayı ve yedek kaynağı kullanmayın','Duman, kıvılcım, yanık kokusu, su/yoğuşma teması veya elektrik çarpması riski varken hesap ve ticari yönlendirme yapılmaz.');
      result.issues=['Enerjili ekipmana, ıslak yüzeye veya hasarlı kabloya yaklaşmayın.'];
      result.steps=['Güvenliyse enerjiyi ana noktadan kesin.','Yangın, yaralanma veya elektrik çarpması riski varsa 112’yi arayın.'];
      return result;
    }

    if(input.medicalCooling){
      const result=base('professional','Sağlık açısından kritik soğutma için tüketici ürünü seçmeyin','Soğutma kaybı sağlık veya yaşam güvenliği açısından kritikse tek bir power station ya da jeneratör seçimi yeterli güvence değildir.');
      result.issues=['Yedeklilik, çalışma süresi, bakım, yakıt/enerji ikmali ve alternatif güvenli alan planı birlikte hazırlanmalıdır.'];
      result.steps=['Sağlık profesyonelinin ve yetkili elektrik uzmanının yönlendirmesiyle kesinti planı oluşturun.','Acil sağlık riski oluşursa 112’yi arayın.'];
      result.toolKeys=['handoff'];
      return result;
    }

    const evidence=[];
    if(!['planning','active','existing'].includes(input.scenario))evidence.push('Kullanım senaryosu seçilmedi.');
    if(!START_MULTIPLIER[input.unitType]&&input.unitType!=='central')evidence.push('Klima türü doğrulanmadı.');
    if(!['single','three'].includes(input.phase))evidence.push('Faz bilgisi doğrulanmadı.');
    if(!['plug','fixed'].includes(input.connection))evidence.push('Bağlantının fişli mi sabit mi olduğu bilinmiyor.');

    const labelW=n(input.labelW);
    const voltage=n(input.voltage);
    const current=n(input.ratedCurrent);
    const pf=n(input.powerFactor);
    const startupW=n(input.startupW);
    const otherW=n(input.otherLoadW);
    const targetHours=n(input.targetHours);
    const hasRunningData=labelW>0||(voltage>0&&current>0);
    if(!hasRunningData)evidence.push('Etiket giriş gücü veya V/A bilgisi doğrulanmadı.');
    if(labelW!==null&&(labelW<50||labelW>20000))evidence.push('Etiket giriş gücü 50–20.000 W aralığında olmalıdır.');
    if(voltage!==null&&(voltage<100||voltage>500))evidence.push('Etiket gerilimi 100–500 V aralığında olmalıdır.');
    if(current!==null&&(current<=0||current>100))evidence.push('Etiket akımı 0–100 A aralığında olmalıdır.');
    if(pf!==null&&(pf<0.4||pf>1))evidence.push('Güç faktörü 0,40–1,00 aralığında olmalıdır.');
    if(startupW!==null&&(startupW<50||startupW>50000))evidence.push('Başlangıç/maksimum giriş gücü 50–50.000 W aralığında olmalıdır.');
    if(otherW!==null&&(otherW<0||otherW>10000))evidence.push('Diğer eşzamanlı yük 0–10.000 W aralığında olmalıdır.');
    if(!(targetHours>0)||targetHours>24)evidence.push('Hedef çalışma süresi 0–24 saat aralığında doğrulanmadı.');
    if(input.unitType==='central'&&!(startupW>0))evidence.push('Merkezi/VRF sistem için üretici başlangıç veya maksimum giriş gücü gereklidir.');
    if(input.sourceStatus==='existing'&&input.sourceType==='auto')evidence.push('Mevcut kaynağın power station, jeneratör veya inverter sınıfı seçilmedi.');

    if(evidence.length){
      const result=base('evidence_required','Önce klima etiketini ve bağlantıyı doğrulayın','BTU veya yalnız cihaz model adıyla yedek güç seçilmez. Elektrik giriş gücü, faz, bağlantı ve süre kanıtı gerekir.');
      result.issues=evidence;
      result.steps=['Etiketteki input power / rated input / current alanlarını kaydedin.','Üretici teknik sayfasında maksimum giriş veya kompresör başlangıç davranışını doğrulayın.'];
      result.toolKeys=['compare'];
      return result;
    }

    const metrics=calculations(input);
    if(!metrics)return base('evidence_required','Hesap için gerekli veri eksik','Sayısal bilgiler tamamlanmadan ürün yolu açılmaz.');

    const fixed=input.connection==='fixed';
    const three=input.phase==='three';
    const central=input.unitType==='central';
    const highPower=metrics.runningW>2000;
    if(fixed||three||central||highPower){
      const result=base('professional','Klima ve yedek kaynak koordinasyonu uzman doğrulaması gerektirir','Sabit bağlı, trifaze, merkezi veya yüksek güçlü klimada yalnız watt hesabı yeterli değildir.');
      result.metrics=metrics;
      result.issues=uniq([
        fixed&&'Sabit tesisat bağlantısı transfer, koruma ve nötr düzeni gerektirir.',
        three&&'Trifaze sistemde faz sırası, dengesizlik ve kaynak gerilim regülasyonu doğrulanmalıdır.',
        central&&'VRF/multisplit sistem üreticiye özgü sürücü, haberleşme ve maksimum giriş sınırları taşır.',
        highPower&&'Klima giriş gücü tüketici tipi taşınabilir kaynak sınırını aşıyor.'
      ]);
      result.steps=['Yetkili elektrik uzmanına klima etiketi, kablo, koruma, transfer ve kaynak verilerini doğrulatın.','Jeneratör veya inverteri yalnız sürekli güç değil kompresör başlangıcı ve gerilim/frekans kararlılığıyla seçin.'];
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
        const result=base('evidence_required','Mevcut kaynağın sürekli, tepe ve enerji değerini doğrulayın','Sadece model adı, VA veya pazarlama tepe değeri yeterli değildir.');
        result.metrics=metrics;
        result.issues=['Pozitif sürekli W, tepe W ve bataryalıysa Wh değeri eksik.'];
        result.steps=['Üretici teknik sayfasındaki aynı model ve çıkış koşullarını doğrulayın.'];
        return result;
      }

      const continuousOk=continuous>=metrics.requiredContinuousW;
      const surgeOk=surge>=metrics.requiredSurgeW;
      const whOk=!batteryNeeded||wh>=metrics.requiredWh;
      const waveformOk=input.waveform==='pure';
      const outputOk=input.outputSpec==='confirmed';
      const startOk=input.startTest==='success';

      if(continuousOk&&surgeOk&&whOk&&waveformOk&&outputOk&&startOk){
        const result=base('no_buy','Mevcut kaynak doğrulanmış eşikleri karşılıyorsa yeni ürün almayın','Girilen teknik değerler ve kontrollü başlatma testine göre mevcut kaynak yeterli görünüyor.');
        result.metrics=metrics;
        result.steps=['Klimayı gerçek ortam sıcaklığında kontrollü süre testiyle doğrulayın.','Kablo, priz, koruma, havalandırma ve kaynak sıcaklığını periyodik kontrol edin.'];
        result.toolKeys=['compare'];
        return result;
      }

      if(continuousOk&&surgeOk&&whOk&&(!waveformOk||!outputOk||!startOk)){
        const result=base('evidence_required','Güç değerleri yeterli görünse de uyumluluk kanıtı eksik','Klima motoru ve elektronik kartı için dalga biçimi, 230 V / 50 Hz çıkış ve gerçek başlatma testi doğrulanmadan uygunluk sonucu verilmez.');
        result.metrics=metrics;
        result.issues=uniq([
          !waveformOk&&'Saf sinüs çıkış doğrulanmadı.',
          !outputOk&&'230 V / 50 Hz ve üretici klima kullanım uygunluğu doğrulanmadı.',
          !startOk&&(input.startTest==='failed'?'Kontrollü başlatma testi başarısız oldu.':'Kontrollü başlatma testi yapılmadı.')
        ]);
        result.steps=['Kaynağı üretici talimatına uygun yük altında test edin; korumaya geçerse daha büyük ürün satın almadan kök nedeni doğrulayın.'];
        result.toolKeys=['compare'];
        return result;
      }
    }

    if(input.scenario==='active'){
      const result=base('active_event','Aktif kesintide ürün teslimatını çözüm olarak beklemeyin','Hesap yalnız gelecekteki hazırlık sınıfını gösterir; aktif olayda ticari yönlendirme kapalıdır.');
      result.metrics=metrics;
      result.issues=['Mevcut güvenli kaynak yoksa klimayı çalıştırmaya yönelik geçici kablo veya ters besleme çözümü kullanmayın.'];
      result.steps=['Mevcut güvenli serinleme planını uygulayın.','Sağlık riski oluşursa 112’yi arayın; elektriksel tehlikede enerjiyi güvenli biçimde kesin.','Kesinti sonrasında kaynak seçimini kontrollü test planıyla yapın.'];
      result.toolKeys=['compare'];
      return result;
    }

    let category='generator';
    if(input.sourceType==='power_station'||(input.sourceType==='auto'&&metrics.requiredContinuousW<=1800&&metrics.requiredSurgeW<=3600&&metrics.requiredWh<=3000&&metrics.targetHours<=4))category='power_station';
    else if(input.sourceType==='inverter')category='inverter';
    else if(input.sourceType==='generator')category='generator';

    const result=base('conditional_purchase','Kaynak yetersiz veya eksik; yalnız hesaplanan sınıfa ilerleyin','Bu sonuç belirli marka/model onayı değildir. Sürekli güç, kompresör başlangıcı, saf sinüs, çıkış kararlılığı ve enerji kapasitesi birlikte doğrulanmalıdır.');
    result.metrics=metrics;
    result.issues=[
      `En az yaklaşık ${metrics.requiredContinuousW} W sürekli güç gerekir.`,
      `Kompresör başlangıcı için yaklaşık ${metrics.requiredSurgeW} W kısa süreli kapasite gerekir.`,
      ...(['power_station','inverter'].includes(category)?[`Hedef süre için yaklaşık ${metrics.requiredWh} Wh nominal enerji gerekir.`]:[])
    ];
    result.steps=['Üretici sayfasında sürekli güç ile tepe/X-Boost değerini ayırın.','Saf sinüs, 230 V / 50 Hz çıkış ve klima kullanım uygunluğunu doğrulayın.','Klimayı kontrollü gerçek başlatma ve süre testiyle kabul edin.'];
    result.commerceCategories=[category];
    result.toolKeys=[category];
    result.commerceClosed=false;
    return result;
  }

  const gateReady=(actualNeed,technicalCheck,affiliateCheck)=>Boolean(actualNeed&&technicalCheck&&affiliateCheck);

  function init(doc){
    const form=doc.getElementById('acForm');
    if(!form)return;
    const $=id=>doc.getElementById(id);
    const ids=['emergency','medicalCooling','scenario','unitType','connection','phase','labelW','voltage','ratedCurrent','powerFactor','startupW','otherLoadW','targetHours','sourceStatus','sourceType','sourceContinuousW','sourceSurgeW','sourceWh','waveform','outputSpec','startTest'];
    const resultBox=$('result');
    const commerceGate=$('commerceGate');
    const productLinks=$('productLinks');
    let lastResult=null;

    const input=()=>Object.fromEntries(ids.map(id=>[id,$(id).type==='checkbox'?$(id).checked:$(id).value]));
    const showExisting=()=>$('existingFields').classList.toggle('hidden',$('sourceStatus').value!=='existing');
    const renderList=(node,items)=>{node.innerHTML='';(items.length?items:['Yok.']).forEach(item=>{const li=doc.createElement('li');li.textContent=item;node.appendChild(li);});};
    const renderMetrics=metrics=>{
      const area=$('metricArea');area.innerHTML='';
      if(!metrics)return;
      const entries=[['Çalışma yükü',`${metrics.totalRunningW} W`],['Sürekli alt sınır',`${metrics.requiredContinuousW} W`],['Kalkış alt sınırı',`${metrics.requiredSurgeW} W`],['Yaklaşık VA',`${metrics.approximateVA} VA`],['Nominal enerji',`${metrics.requiredWh} Wh`]];
      const wrap=doc.createElement('div');wrap.className='metrics';
      entries.forEach(([label,value])=>{const article=doc.createElement('article');const span=doc.createElement('span');span.textContent=label;const strong=doc.createElement('strong');strong.textContent=value;article.append(span,strong);wrap.appendChild(article);});
      area.appendChild(wrap);
      const note=doc.createElement('p');note.className='privacy';note.textContent=`${metrics.pfAssumed?'Güç faktörü 0,90 varsayıldı. ':''}${metrics.startupAssumed?`Başlangıç gücü klima türü için ${metrics.multiplier}× planlama katsayısıyla tahmin edildi; üretici değeri varsa onu kullanın.`:'Başlangıç gücü kullanıcı tarafından girilen üretici değeriyle hesaplandı.'}`;area.appendChild(note);
    };
    const renderTools=keys=>{const area=$('toolLinks');area.innerHTML='';keys.forEach(key=>{const item=TOOL_LINKS[key];if(!item)return;const a=doc.createElement('a');a.className='button';a.href=item.href;a.textContent=item.label;area.appendChild(a);});};
    const updateGate=()=>{$('openProducts').disabled=!gateReady($('actualNeed').checked,$('technicalCheck').checked,$('affiliateCheck').checked);};

    function render(result){
      lastResult=result;
      resultBox.className=`panel result status-${result.status}`;
      resultBox.classList.remove('hidden');
      $('resultBadge').textContent=result.status.replaceAll('_',' ');
      $('resultTitle').textContent=result.title;
      $('resultSummary').textContent=result.summary;
      renderMetrics(result.metrics);
      renderList($('issueList'),result.issues);
      renderList($('stepList'),result.steps);
      renderTools(result.toolKeys);
      commerceGate.classList.toggle('hidden',result.commerceClosed||!result.commerceCategories.length);
      productLinks.innerHTML='';
      ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>{$(id).checked=false;});
      $('openProducts').disabled=true;
      resultBox.focus();
      if(window.Alo186Track)window.Alo186Track('calculator_result',{tool:'air_conditioner_backup',result_status:result.status});
    }

    form.addEventListener('submit',event=>{event.preventDefault();render(evaluate(input()));});
    $('resetBtn').addEventListener('click',()=>{form.reset();$('voltage').value='230';$('otherLoadW').value='0';showExisting();resultBox.classList.add('hidden');commerceGate.classList.add('hidden');productLinks.innerHTML='';lastResult=null;});
    $('sourceStatus').addEventListener('change',showExisting);
    ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>$(id).addEventListener('change',updateGate));
    $('openProducts').addEventListener('click',()=>{
      productLinks.innerHTML='';
      if(!lastResult||lastResult.commerceClosed||!gateReady($('actualNeed').checked,$('technicalCheck').checked,$('affiliateCheck').checked))return;
      lastResult.commerceCategories.forEach(key=>{const item=CATEGORY_LINKS[key];if(!item)return;const a=doc.createElement('a');a.className='button';a.href=item.href;a.textContent=item.label;productLinks.appendChild(a);});
      productLinks.focus();
      if(window.Alo186Track)window.Alo186Track('affiliate_category_gate_open',{tool:'air_conditioner_backup',categories:lastResult.commerceCategories.join(',')});
    });
    showExisting();
  }

  return {ROUTE,PF_DEFAULT,RESERVE,SURGE_RESERVE,BATTERY_EFF,USABLE,START_MULTIPLIER,calculations,evaluate,gateReady,init};
});
