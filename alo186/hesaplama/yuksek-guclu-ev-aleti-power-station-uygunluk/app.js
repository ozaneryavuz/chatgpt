(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186HighPowerAppliance=api;
  if(root&&root.document)api.init(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const ROUTE='/hesaplama/yuksek-guclu-ev-aleti-power-station-uygunluk/';
  const CONTINUOUS_RESERVE=1.15;
  const SURGE_RESERVE=1.10;
  const INVERTER_EFFICIENCY=0.85;
  const USABLE_ENERGY=0.80;
  const SURGE_MULTIPLIER={kettle:1.15,airfryer:1.15,coffee:1.5,microwave:1.6,hairdryer:1.15,toaster:1.15,vacuum:2.5,other:1.5};
  const CATEGORY_LINKS={
    power_station:{label:'Power station ürün sınıfını aç',href:'../../akilli-urun-secimi?kategori=power_station'},
    generator:{label:'Jeneratör ürün sınıfını aç',href:'../../akilli-urun-secimi?kategori=generator'},
    inverter:{label:'İnverter ürün sınıfını aç',href:'../../akilli-urun-secimi?kategori=inverter'}
  };
  const TOOL_LINKS={
    power_station:{label:'Power station kapasite testini aç',href:'../power-station-kapasite-eps-uygunluk/'},
    generator:{label:'Jeneratör güç hesabını aç',href:'../jenerator-gucu-secimi/'},
    inverter:{label:'İnverter uygunluk testini aç',href:'../inverter-uygunluk/'},
    extension:{label:'Uzatma kablosu uygunluğunu kontrol et',href:'../uzatma-kablosu-uygunluk/'},
    outlet:{label:'Grup priz ve yük uygunluğunu kontrol et',href:'../akim-korumali-grup-priz-uygunluk/'},
    compare:{label:'Yedek güç çözüm seçiciyi aç',href:'../yedek-guc-cozum-secici/'}
  };

  const n=value=>{
    const raw=String(value??'').trim().replace(',','.');
    if(!raw)return null;
    const parsed=Number(raw);
    return Number.isFinite(parsed)?parsed:null;
  };
  const round=(value,digits=0)=>Number(value.toFixed(digits));
  const uniq=values=>[...new Set(values.filter(Boolean))];
  const base=(status,title,summary)=>({status,title,summary,issues:[],steps:[],metrics:null,commerceCategories:[],toolKeys:[],commerceClosed:true});

  function calculations(input={}){
    const labelW=n(input.labelW);
    const otherW=n(input.otherW)??0;
    const minutes=n(input.cycleMinutes);
    const count=n(input.cycleCount);
    if(!(labelW>0)||!(minutes>0)||!(count>0)||!SURGE_MULTIPLIER[input.applianceType])return null;
    const totalRunningW=labelW+otherW;
    const explicitSurge=n(input.explicitSurgeW);
    const surgeMultiplier=SURGE_MULTIPLIER[input.applianceType];
    const applianceSurge=explicitSurge>0?explicitSurge:labelW*surgeMultiplier;
    const requiredContinuousW=totalRunningW*CONTINUOUS_RESERVE;
    const requiredSurgeW=(applianceSurge+otherW)*SURGE_RESERVE;
    const totalMinutes=minutes*count;
    const loadEnergyWh=totalRunningW*totalMinutes/60;
    const requiredWh=loadEnergyWh/INVERTER_EFFICIENCY/USABLE_ENERGY;
    return {
      labelW:round(labelW),otherW:round(otherW),totalRunningW:round(totalRunningW),
      requiredContinuousW:round(requiredContinuousW),requiredSurgeW:round(requiredSurgeW),
      requiredWh:round(requiredWh),loadEnergyWh:round(loadEnergyWh),totalMinutes:round(totalMinutes,1),
      surgeAssumed:!(explicitSurge>0),surgeMultiplier:explicitSurge>0?null:surgeMultiplier
    };
  }

  function evaluate(input={}){
    if(input.emergency){
      const result=base('emergency','Acil: cihazı ve enerji kaynağını kullanmayın','Duman, erime, şişme, su, yanık kokusu, aşırı ısı veya elektrik çarpması riski varken hesap ve ticari yönlendirme yapılmaz.');
      result.issues=['Enerjili ekipmana, ıslak yüzeye veya hasarlı kabloya yaklaşmayın.'];
      result.steps=['Güvenliyse enerjiyi ana noktadan kesin.','Yangın, yaralanma veya elektrik çarpması riski varsa 112’yi arayın.'];
      return result;
    }

    const evidence=[];
    if(!['planning','active','existing'].includes(input.scenario))evidence.push('Kullanım senaryosu seçilmedi.');
    if(!SURGE_MULTIPLIER[input.applianceType]&&input.applianceType!=='fixed_high_power')evidence.push('Cihaz sınıfı seçilmedi.');
    if(!['direct','extension','fixed'].includes(input.connection))evidence.push('Bağlantı biçimi doğrulanmadı.');
    if(!['yes','no'].includes(input.supervised))evidence.push('Kullanımın gözetimli olup olmadığı belirtilmedi.');
    if(!['input','measured','microwave_output'].includes(input.powerEvidence))evidence.push('Watt verisinin kaynağı doğrulanmadı.');

    const labelW=n(input.labelW);
    const explicitSurgeW=n(input.explicitSurgeW);
    const cycleMinutes=n(input.cycleMinutes);
    const cycleCount=n(input.cycleCount);
    const otherW=n(input.otherW);
    if(!(labelW>0)||labelW<100||labelW>4000)evidence.push('Cihaz giriş gücü 100–4.000 W aralığında doğrulanmadı.');
    if(explicitSurgeW!==null&&(explicitSurgeW<100||explicitSurgeW>10000))evidence.push('Tepe güç 100–10.000 W aralığında olmalıdır.');
    if(!(cycleMinutes>0)||cycleMinutes>180)evidence.push('Bir kullanım süresi 0–180 dakika aralığında doğrulanmadı.');
    if(!(cycleCount>=1)||cycleCount>30)evidence.push('Kullanım adedi 1–30 aralığında olmalıdır.');
    if(otherW!==null&&(otherW<0||otherW>1500))evidence.push('Diğer yük 0–1.500 W aralığında olmalıdır.');

    if(input.powerEvidence==='microwave_output'){
      const result=base('evidence_required','Mikrodalganın giriş wattını bulun','Pişirme veya output wattı, cihazın şebekeden çektiği güç değildir ve power station boyutlandırmasında kullanılamaz.');
      result.issues=['Etiketteki INPUT, rated input veya power consumption değeri eksik.'];
      result.steps=['Cihazın arka/yan etiketini veya üretici teknik sayfasını kontrol edin.','Giriş wattını bulduktan sonra hesabı yeniden yapın.'];
      result.toolKeys=['power_station'];
      return result;
    }

    if(evidence.length){
      const result=base('evidence_required','Önce cihaz etiketini ve kullanım koşulunu doğrulayın','Yalnız ürün adı veya ön yüzdeki watt bilgisiyle güvenli ürün seçimi yapılmaz.');
      result.issues=evidence;
      result.steps=['Etiketteki giriş/tüketim wattını kaydedin.','Kullanımın doğrudan ve gözetimli olacağını doğrulayın.'];
      result.toolKeys=['power_station'];
      return result;
    }

    if(input.applianceType==='fixed_high_power'||input.connection==='fixed'){
      const result=base('professional','Sabit ve yüksek güçlü cihaz için taşınabilir ürün seçmeyin','Ankastre fırın, indüksiyon ocak, sabit ısıtıcı ve sabit tesisata bağlı yüklerde kablo, koruma, transfer ve eşzamanlılık birlikte projelendirilmelidir.');
      result.issues=['Tüketici tipi power station bağlantısı sabit tesisat uygunluğu anlamına gelmez.'];
      result.steps=['Yetkili elektrik uzmanına yük, devre, koruma ve kaynak bağlantısını doğrulatın.','Ters besleme veya geçici adaptör kullanmayın.'];
      result.toolKeys=['generator','inverter','compare'];
      return result;
    }

    if(input.connection==='extension'){
      const result=base('stop','Uzatma, çoklayıcı veya adaptör üzerinden kullanmayın','Yüksek güçlü ısıtıcı ve motorlu cihazlar, kaynak üreticisi açıkça izin vermedikçe kendi AC çıkışına doğrudan bağlanmalıdır.');
      result.issues=['Ek bağlantı noktaları temas direnci, ısınma ve aşırı yük riskini artırır.'];
      result.steps=['Doğrudan bağlantı mümkün değilse bu kullanım planını durdurun.','Uzatma gerekiyorsa ürün almadan önce kablo, akım ve ortam uygunluğunu uzmanla doğrulayın.'];
      result.toolKeys=['extension','outlet'];
      return result;
    }

    if(input.supervised==='no'){
      const result=base('stop','Gözetimsiz yüksek güçlü kullanım uygun değildir','Kettle, airfryer, kahve makinesi, saç kurutma ve benzeri yüksek güçlü cihazlar kesinti kaynağında gözetimsiz veya zamanlayıcılı kullanılmamalıdır.');
      result.issues=['Kaynak, fiş, priz veya cihaz aşırı ısınması fark edilmeyebilir.'];
      result.steps=['Yalnız uyanıkken ve cihazın yanında kullanın.','Havalandırmayı ve kablo sıcaklığını takip edin.'];
      return result;
    }

    const metrics=calculations(input);
    if(!metrics)return base('evidence_required','Hesap için gerekli veri eksik','Sayısal bilgiler tamamlanmadan ürün yolu açılmaz.');

    if(metrics.totalRunningW>2800||metrics.requiredContinuousW>3300){
      const result=base('professional','Eşzamanlı güç taşınabilir tüketici senaryosunu aşıyor','Bu yük düzeyinde yalnız cihaz wattı değil priz devresi, kablo, koruma, havalandırma ve kaynak işletmesi birlikte değerlendirilmelidir.');
      result.metrics=metrics;
      result.issues=['Birden fazla yüksek güçlü cihazı aynı anda çalıştırmayın.'];
      result.steps=['Yükleri sıraya alın veya profesyonel jeneratör/inverter çözümü değerlendirin.','Yetkili elektrik uzmanına devre ve kaynak koordinasyonunu doğrulatın.'];
      result.toolKeys=['generator','inverter','compare'];
      return result;
    }

    if(input.scenario==='active'){
      const result=base('active_event','Aktif kesintide ürün teslimatını çözüm olarak beklemeyin','Hesap gelecekteki hazırlık sınıfını gösterir; aktif olayda ticari yönlendirme kapalıdır.');
      result.metrics=metrics;
      result.issues=['Geçici kablo, ters besleme veya kapalı alanda jeneratör kullanmayın.'];
      result.steps=['Mevcut ve önceden test edilmiş güvenli kaynak yoksa yüksek güçlü cihazı çalıştırmayın.','Kesinti sonrası planlama ve kontrollü kabul testi yapın.'];
      result.toolKeys=['compare'];
      return result;
    }

    if(input.sourceStatus==='existing'){
      const continuous=n(input.sourceContinuousW);
      const surge=n(input.sourceSurgeW);
      const wh=n(input.sourceWh);
      const batteryNeeded=['power_station','inverter','auto'].includes(input.sourceType);
      const missing=!(continuous>0)||!(surge>0)||(batteryNeeded&&!(wh>0));
      if(missing){
        const result=base('evidence_required','Mevcut kaynağın sürekli, tepe ve enerji değerini doğrulayın','Model adı veya pazarlama tepe değeri tek başına yeterli değildir.');
        result.metrics=metrics;
        result.issues=['Pozitif sürekli W, tepe W ve bataryalıysa nominal Wh değeri eksik.'];
        result.steps=['Üretici teknik sayfasındaki aynı model ve AC çıkış koşullarını doğrulayın.'];
        return result;
      }
      const continuousOk=continuous>=metrics.requiredContinuousW;
      const surgeOk=surge>=metrics.requiredSurgeW;
      const whOk=!batteryNeeded||wh>=metrics.requiredWh;
      const waveformOk=input.waveform==='pure';
      const outputOk=input.outputSpec==='confirmed';
      const directOk=input.directOutput==='yes';
      const testOk=input.loadTest==='success';

      if(continuousOk&&surgeOk&&whOk&&waveformOk&&outputOk&&directOk&&testOk){
        const result=base('no_buy','Mevcut kaynak doğrulanmış eşikleri karşılıyorsa yeni ürün almayın','Girilen teknik değerler ve gözetimli gerçek yük testine göre mevcut kaynak yeterli görünüyor.');
        result.metrics=metrics;
        result.steps=['Fiş, priz ve kaynak sıcaklığını her kullanımda kontrol edin.','Kaynak kapasitesini yeni yük eklendiğinde yeniden değerlendirin.'];
        result.toolKeys=['power_station'];
        return result;
      }

      if(continuousOk&&surgeOk&&whOk&&(!waveformOk||!outputOk||!directOk||!testOk)){
        const result=base('evidence_required','Güç değerleri yeterli görünse de kullanım kanıtı eksik','Saf sinüs, 230 V / 50 Hz çıkış, doğrudan bağlantı ve gerçek yük testi doğrulanmadan uygunluk sonucu verilmez.');
        result.metrics=metrics;
        result.issues=uniq([
          !waveformOk&&'Saf sinüs çıkış doğrulanmadı.',
          !outputOk&&'230 V / 50 Hz ve yük sınıfı uygunluğu doğrulanmadı.',
          !directOk&&'Kaynağın kendi AC çıkışına doğrudan bağlantı doğrulanmadı.',
          !testOk&&(input.loadTest==='failed'?'Gerçek yük testi başarısız oldu veya ısınma oluştu.':'Gözetimli gerçek yük testi yapılmadı.')
        ]);
        result.steps=['Yeni ürün almadan önce üretici talimatına uygun kontrollü test yapın.'];
        result.toolKeys=['power_station'];
        return result;
      }
    }

    let category='generator';
    if(input.sourceType==='power_station'||(input.sourceType==='auto'&&metrics.requiredContinuousW<=2400&&metrics.requiredSurgeW<=4800&&metrics.requiredWh<=3500))category='power_station';
    else if(input.sourceType==='inverter')category='inverter';
    else if(input.sourceType==='generator')category='generator';

    const result=base('conditional_purchase','Kapasite açığı var; yalnız hesaplanan kaynak sınıfına ilerleyin','Bu sonuç belirli marka/model onayı değildir. Giriş wattı, sürekli güç, tepe güç, enerji, saf sinüs, çıkış akımı ve gerçek yük testi birlikte doğrulanmalıdır.');
    result.metrics=metrics;
    result.issues=[
      `En az yaklaşık ${metrics.requiredContinuousW} W sürekli AC güç gerekir.`,
      `Kısa süreli tepe için yaklaşık ${metrics.requiredSurgeW} W kapasite gerekir.`,
      ...(['power_station','inverter'].includes(category)?[`Planlanan kullanım için yaklaşık ${metrics.requiredWh} Wh nominal enerji gerekir.`]:[])
    ];
    result.steps=['Üretici sayfasında sürekli AC güç ile boost/tepe değerini ayırın.','Saf sinüs, 230 V / 50 Hz, priz akımı ve bu cihaz sınıfına izin verildiğini doğrulayın.','Cihazı doğrudan bağlayıp uyanıkken kontrollü gerçek yük testi yapın.'];
    result.commerceCategories=[category];
    result.toolKeys=[category,'compare'];
    result.commerceClosed=false;
    return result;
  }

  const gateReady=(actualNeed,technicalCheck,affiliateCheck)=>Boolean(actualNeed&&technicalCheck&&affiliateCheck);

  function init(doc){
    const form=doc.getElementById('applianceForm');
    if(!form)return;
    const $=id=>doc.getElementById(id);
    const ids=['emergency','scenario','applianceType','connection','supervised','powerEvidence','labelW','explicitSurgeW','cycleMinutes','cycleCount','otherW','sourceStatus','sourceType','sourceContinuousW','sourceSurgeW','sourceWh','waveform','outputSpec','directOutput','loadTest'];
    const resultBox=$('result');
    const commerceGate=$('commerceGate');
    const productLinks=$('productLinks');
    let lastResult=null;
    const input=()=>Object.fromEntries(ids.map(id=>[id,$(id).type==='checkbox'?$(id).checked:$(id).value]));
    const showExisting=()=>$('existingFields').classList.toggle('hidden',$('sourceStatus').value!=='existing');
    const renderList=(node,items)=>{node.innerHTML='';(items.length?items:['Yok.']).forEach(item=>{const li=doc.createElement('li');li.textContent=item;node.appendChild(li);});};
    const renderMetrics=metrics=>{
      const area=$('metricArea');area.innerHTML='';if(!metrics)return;
      const entries=[['Çalışma yükü',`${metrics.totalRunningW} W`],['Sürekli alt sınır',`${metrics.requiredContinuousW} W`],['Tepe alt sınırı',`${metrics.requiredSurgeW} W`],['Toplam kullanım',`${metrics.totalMinutes} dk`],['Nominal enerji',`${metrics.requiredWh} Wh`]];
      const wrap=doc.createElement('div');wrap.className='metrics';
      entries.forEach(([label,value])=>{const article=doc.createElement('article');const span=doc.createElement('span');span.textContent=label;const strong=doc.createElement('strong');strong.textContent=value;article.append(span,strong);wrap.appendChild(article);});
      area.appendChild(wrap);
      const note=doc.createElement('p');note.className='privacy';note.textContent=metrics.surgeAssumed?`Tepe güç cihaz sınıfı için ${metrics.surgeMultiplier}× planlama katsayısıyla tahmin edildi; üretici değeri varsa onu kullanın.`:'Tepe güç kullanıcı tarafından girilen üretici değeriyle hesaplandı.';area.appendChild(note);
    };
    const renderTools=keys=>{const area=$('toolLinks');area.innerHTML='';keys.forEach(key=>{const item=TOOL_LINKS[key];if(!item)return;const a=doc.createElement('a');a.className='button';a.href=item.href;a.textContent=item.label;area.appendChild(a);});};
    const updateGate=()=>{$('openProducts').disabled=!gateReady($('actualNeed').checked,$('technicalCheck').checked,$('affiliateCheck').checked);};
    function render(result){
      lastResult=result;resultBox.className=`panel result status-${result.status}`;resultBox.classList.remove('hidden');
      $('resultBadge').textContent=result.status.replaceAll('_',' ');$('resultTitle').textContent=result.title;$('resultSummary').textContent=result.summary;
      renderMetrics(result.metrics);renderList($('issueList'),result.issues);renderList($('stepList'),result.steps);renderTools(result.toolKeys);
      commerceGate.classList.toggle('hidden',result.commerceClosed||!result.commerceCategories.length);productLinks.innerHTML='';
      ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>{$(id).checked=false;});$('openProducts').disabled=true;resultBox.focus();
      if(window.Alo186Track)window.Alo186Track('calculator_result',{tool:'high_power_appliance',result_status:result.status});
    }
    form.addEventListener('submit',event=>{event.preventDefault();render(evaluate(input()));});
    $('resetBtn').addEventListener('click',()=>{form.reset();$('cycleCount').value='1';$('otherW').value='0';showExisting();resultBox.classList.add('hidden');commerceGate.classList.add('hidden');productLinks.innerHTML='';lastResult=null;});
    $('sourceStatus').addEventListener('change',showExisting);
    ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>$(id).addEventListener('change',updateGate));
    $('openProducts').addEventListener('click',()=>{
      productLinks.innerHTML='';
      if(!lastResult||lastResult.commerceClosed||!gateReady($('actualNeed').checked,$('technicalCheck').checked,$('affiliateCheck').checked))return;
      lastResult.commerceCategories.forEach(key=>{const item=CATEGORY_LINKS[key];if(!item)return;const a=doc.createElement('a');a.className='button';a.href=item.href;a.textContent=item.label;a.rel='sponsored nofollow noopener';productLinks.appendChild(a);});
      productLinks.focus();
      if(window.Alo186Track)window.Alo186Track('affiliate_category_gate_open',{tool:'high_power_appliance',categories:lastResult.commerceCategories.join(',')});
    });
    showExisting();
  }

  return {ROUTE,CONTINUOUS_RESERVE,SURGE_RESERVE,INVERTER_EFFICIENCY,USABLE_ENERGY,SURGE_MULTIPLIER,calculations,evaluate,gateReady,init};
});
