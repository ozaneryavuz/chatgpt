(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186FridgeFreezerBackup=api;
  if(root&&root.document)api.init(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const PF_DEFAULT=0.85;
  const RESERVE=1.25;
  const SURGE_RESERVE=1.15;
  const BATTERY_EFF=0.85;
  const USABLE=0.8;
  const START_MULTIPLIER={fridge:3,fridge_freezer:3.5,upright_freezer:3.5,chest_freezer:3};
  const DUTY_CYCLE_DEFAULT={fridge:45,fridge_freezer:50,upright_freezer:50,chest_freezer:40};
  const ROUTE='/hesaplama/buzdolabi-dondurucu-yedek-guc-uygunluk/';

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
    return {status,title,summary,issues:[],steps:[],metrics:null,foodSafety:null,commerceCategories:[],toolKeys:[],commerceClosed:true};
  }

  function foodSafetyWindow(input={}){
    const unknown={hours:null,refrigeratorHours:null,freezerHours:null,label:'Kapı açıldı veya kapalı tutulacağı doğrulanmadı',note:'4/24/48 saatlik resmî süreler yalnız kapı kapalı tutulduğunda kullanılan yaklaşık rehber değerlerdir.'};
    if(input.doorClosed!=='yes')return unknown;

    if(input.applianceType==='fridge'){
      return {hours:4,refrigeratorHours:4,freezerHours:null,label:'Buzdolabı yaklaşık 4 saat',note:'Kapı açılmazsa buzdolabı yaklaşık 4 saat soğuk kalabilir; gerçek sıcaklığı cihaz termometresiyle 4 °C (40 °F) veya altında doğrulayın.'};
    }

    if(input.applianceType==='fridge_freezer'){
      const freezerHours=input.freezerFill==='full'?48:input.freezerFill==='half'?24:null;
      const freezerText=freezerHours?`dondurucu yaklaşık ${freezerHours} saat`:'dondurucu doluluğu doğrulanmalı';
      const freezerNote=freezerHours
        ? `${input.freezerFill==='full'?'Tam':'Yarı'} dolu dondurucu bölümü kapı açılmazsa yaklaşık ${freezerHours} saat sıcaklığı koruyabilir.`
        : 'Dondurucunun tam veya yarı dolu olduğu bilinmeden 24/48 saatlik süre kullanılmaz.';
      return {
        hours:4,
        refrigeratorHours:4,
        freezerHours,
        label:`Buzdolabı yaklaşık 4 saat · ${freezerText}`,
        note:`Buzdolabı bölümü için 4 saatlik sınır her durumda ayrıca korunur. ${freezerNote} Gerçek sıcaklığı termometreyle doğrulayın.`
      };
    }

    if(['upright_freezer','chest_freezer'].includes(input.applianceType)){
      if(input.freezerFill==='full')return {hours:48,refrigeratorHours:null,freezerHours:48,label:'Dondurucu yaklaşık 48 saat',note:'Tam dolu dondurucu kapı açılmazsa yaklaşık 48 saat sıcaklığı koruyabilir.'};
      if(input.freezerFill==='half')return {hours:24,refrigeratorHours:null,freezerHours:24,label:'Dondurucu yaklaşık 24 saat',note:'Yarı dolu dondurucu kapı açılmazsa yaklaşık 24 saat sıcaklığı koruyabilir.'};
      return {hours:null,refrigeratorHours:null,freezerHours:null,label:'Dondurucu doluluğu doğrulanmalı',note:'Dondurucunun tam veya yarı dolu olduğu bilinmeden 24/48 saatlik rehber süre seçilmez.'};
    }

    return {hours:null,refrigeratorHours:null,freezerHours:null,label:'Ticari cihaz için genel süre kullanılmaz',note:'Ticari soğutucuda ürün yükü, kapı kullanımı, sıcaklık kaydı ve işletme prosedürü birlikte değerlendirilmelidir.'};
  }

  function calculations(input={}){
    const labelW=n(input.labelW);
    const voltage=n(input.voltage);
    const current=n(input.ratedCurrent);
    const pf=n(input.powerFactor)??PF_DEFAULT;
    const otherW=n(input.otherLoadW)??0;
    const hours=n(input.targetHours);
    if(!(hours>0))return null;

    const phaseFactor=input.phase==='three'?Math.sqrt(3):1;
    let runningW=labelW;
    let powerFromCurrent=false;
    if(!(runningW>0)&&voltage>0&&current>0){
      runningW=phaseFactor*voltage*current*pf;
      powerFromCurrent=true;
    }
    if(!(runningW>0))return null;

    const explicitStartup=n(input.startupW);
    const multiplier=START_MULTIPLIER[input.applianceType]??null;
    if(!(explicitStartup>0)&&!multiplier)return null;
    const startupW=explicitStartup>0?explicitStartup:runningW*multiplier;

    const explicitDuty=n(input.dutyCyclePct);
    const defaultDuty=DUTY_CYCLE_DEFAULT[input.applianceType]??null;
    const dutyPct=explicitDuty??defaultDuty;
    if(!(dutyPct>0&&dutyPct<=100))return null;

    const compressorAverageW=runningW*(dutyPct/100);
    const averageW=compressorAverageW+otherW;
    const totalRunningW=runningW+otherW;
    const requiredContinuousW=totalRunningW*RESERVE;
    const requiredSurgeW=(startupW+otherW)*SURGE_RESERVE;
    const requiredWh=averageW*hours/BATTERY_EFF/USABLE;
    const approximateVA=requiredContinuousW/0.8;

    return {
      labelW:labelW>0?round(labelW):null,
      voltage:voltage>0?round(voltage):null,
      current:current>0?round(current,2):null,
      phaseFactor:round(phaseFactor,3),
      powerFromCurrent,
      pf:round(pf,2),
      pfAssumed:n(input.powerFactor)===null,
      runningW:round(runningW),
      startupW:round(startupW),
      startupAssumed:!(explicitStartup>0),
      multiplier:explicitStartup>0?null:multiplier,
      dutyPct:round(dutyPct),
      dutyAssumed:explicitDuty===null,
      compressorAverageW:round(compressorAverageW),
      otherW:round(otherW),
      averageW:round(averageW),
      totalRunningW:round(totalRunningW),
      requiredContinuousW:round(requiredContinuousW),
      requiredSurgeW:round(requiredSurgeW),
      requiredWh:round(requiredWh),
      approximateVA:round(approximateVA),
      targetHours:round(hours,2)
    };
  }

  function foodSafetyIssues(input,safety,outageHours){
    return uniq([
      input.doorClosed!=='yes'&&'Kapı açıldıysa resmî 4/24/48 saat rehber süreleri doğrudan kullanılamaz.',
      outageHours!==null&&safety.refrigeratorHours!==null&&outageHours>safety.refrigeratorHours&&`Buzdolabı bölümü için yaklaşık ${safety.refrigeratorHours} saatlik kapalı-kapı rehber penceresi aşıldı.`,
      outageHours!==null&&safety.freezerHours!==null&&outageHours>safety.freezerHours&&`Dondurucu bölümü için yaklaşık ${safety.freezerHours} saatlik kapalı-kapı rehber penceresi aşıldı.`
    ]);
  }

  function chooseCategory(input,metrics){
    if(input.sourceType==='power_station')return 'power_station';
    if(input.sourceType==='inverter')return 'inverter';
    if(input.sourceType==='generator')return 'generator';
    return metrics.requiredContinuousW<=1500&&metrics.requiredSurgeW<=3000&&metrics.requiredWh<=3000&&metrics.targetHours<=12
      ?'power_station':'generator';
  }

  function evaluate(input={}){
    if(input.emergency){
      const result=base('emergency','Acil: cihazı ve yedek kaynağı kullanmayın','Duman, kıvılcım, yanık kokusu, erime, su teması veya elektrik çarpması riski varken hesap ve ticari yönlendirme yapılmaz.');
      result.issues=['Islak yüzeye, hasarlı prize, kabloya veya enerjili metal gövdeye yaklaşmayın.'];
      result.steps=['Güvenliyse enerjiyi ana noktadan kesin.','Yangın, yaralanma veya elektrik çarpması riski varsa 112’yi arayın.'];
      return result;
    }

    if(input.medicalStorage){
      const result=base('professional','İlaç, aşı veya sağlık açısından kritik soğuk zinciri tüketici ürünü seçimine bırakmayın','Kritik sıcaklık aralığı gereken ürünlerde yalnız yaklaşık Wh hesabı yeterli güvence değildir.');
      result.issues=['Üretici saklama sıcaklığı, kalibre sıcaklık kaydı, yedeklilik, alarm ve alternatif güvenli saklama planı birlikte gerekir.'];
      result.steps=['İlgili sağlık profesyoneli ve ürün üreticisinin kesinti talimatını uygulayın.','Yetkili elektrik uzmanıyla yedekli güç ve sıcaklık alarm planı oluşturun.'];
      result.toolKeys=['handoff'];
      return result;
    }

    const evidence=[];
    if(!['planning','active','existing'].includes(input.scenario))evidence.push('Kullanım senaryosu seçilmedi.');
    if(!['fridge','fridge_freezer','upright_freezer','chest_freezer','commercial'].includes(input.applianceType))evidence.push('Cihaz türü doğrulanmadı.');
    if(!['plug','fixed'].includes(input.connection))evidence.push('Bağlantının fişli mi sabit mi olduğu bilinmiyor.');
    if(!['single','three'].includes(input.phase))evidence.push('Faz bilgisi doğrulanmadı.');
    if(!['yes','no'].includes(input.doorClosed))evidence.push('Kapının kapalı tutulup tutulmayacağı doğrulanmadı.');

    const labelW=n(input.labelW);
    const voltage=n(input.voltage);
    const current=n(input.ratedCurrent);
    const pf=n(input.powerFactor);
    const startupW=n(input.startupW);
    const duty=n(input.dutyCyclePct);
    const otherW=n(input.otherLoadW);
    const targetHours=n(input.targetHours);
    const outageHours=n(input.outageHours);
    const hasRunningData=labelW>0||(voltage>0&&current>0);

    if(!hasRunningData)evidence.push('Etiket giriş gücü veya V/A bilgisi doğrulanmadı.');
    if(labelW!==null&&(labelW<20||labelW>10000))evidence.push('Etiket giriş gücü 20–10.000 W aralığında olmalıdır.');
    if(voltage!==null&&(voltage<100||voltage>500))evidence.push('Etiket gerilimi 100–500 V aralığında olmalıdır.');
    if(current!==null&&(current<=0||current>60))evidence.push('Etiket akımı 0–60 A aralığında olmalıdır.');
    if(pf!==null&&(pf<0.4||pf>1))evidence.push('Güç faktörü 0,40–1,00 aralığında olmalıdır.');
    if(startupW!==null&&(startupW<20||startupW>50000))evidence.push('Başlangıç/maksimum güç 20–50.000 W aralığında olmalıdır.');
    if(duty!==null&&(duty<10||duty>100))evidence.push('Çalışma oranı %10–100 aralığında olmalıdır.');
    if(otherW!==null&&(otherW<0||otherW>10000))evidence.push('Diğer eşzamanlı yük 0–10.000 W aralığında olmalıdır.');
    if(!(targetHours>0)||targetHours>48)evidence.push('Hedef çalışma süresi 0–48 saat aralığında doğrulanmadı.');
    if(outageHours!==null&&(outageHours<0||outageHours>168))evidence.push('Kesinti süresi 0–168 saat aralığında olmalıdır.');
    if(input.applianceType==='commercial'&&!(startupW>0))evidence.push('Ticari soğutucu için üretici başlangıç/maksimum güç değeri gerekir.');
    if(['upright_freezer','chest_freezer','fridge_freezer'].includes(input.applianceType)&&!['full','half','unknown'].includes(input.freezerFill))evidence.push('Dondurucu doluluk durumu doğrulanmadı.');
    if(input.sourceStatus==='existing'&&input.sourceType==='auto')evidence.push('Mevcut kaynağın power station, jeneratör veya inverter sınıfı seçilmedi.');

    if(evidence.length){
      const result=base('evidence_required','Önce elektrik etiketini ve soğuk saklama koşulunu doğrulayın','Cihaz hacmi, enerji etiketi sınıfı veya yalnız marka/model adıyla yedek güç seçilmez.');
      result.issues=evidence;
      result.steps=['Etiketteki input power / rated current alanlarını kaydedin.','Üretici teknik sayfasında kompresör başlangıç veya maksimum giriş gücünü doğrulayın.','Buzdolabı/dondurucu termometresiyle gerçek sıcaklığı izleyin.'];
      result.toolKeys=['compare'];
      return result;
    }

    const metrics=calculations(input);
    if(!metrics)return base('evidence_required','Hesap için gerekli veri eksik','Sayısal bilgiler tamamlanmadan ürün yolu açılmaz.');
    const safety=foodSafetyWindow(input);

    const fixed=input.connection==='fixed';
    const three=input.phase==='three';
    const commercial=input.applianceType==='commercial';
    const highPower=metrics.runningW>1500;
    if(fixed||three||commercial||highPower){
      const result=base('professional','Soğutma cihazı ve yedek kaynak koordinasyonu uzman doğrulaması gerektirir','Sabit bağlı, trifaze, ticari veya yüksek güçlü sistemde yalnız watt hesabı yeterli değildir.');
      result.metrics=metrics;
      result.foodSafety=safety;
      result.issues=uniq([
        fixed&&'Sabit tesisat bağlantısı transfer, koruma ve nötr düzeni gerektirir.',
        three&&'Trifaze V/A hesabında √3 katsayısı kullanıldı; faz sırası, dengesizlik ve kaynak regülasyonu ayrıca doğrulanmalıdır.',
        commercial&&'Ticari soğuk zincirde sıcaklık kaydı, alarm ve işletme prosedürü gerekir.',
        highPower&&'Gerçek giriş gücü tüketici tipi taşınabilir kaynak sınırını aşıyor.'
      ]);
      result.steps=['Yetkili elektrik uzmanına etiket, koruma, transfer ve kaynak verilerini doğrulatın.','Soğuk zincir için sıcaklık alarmı ve alternatif saklama prosedürü oluşturun.'];
      result.toolKeys=['generator','inverter','handoff'];
      return result;
    }

    let sourceAssessment=null;
    if(input.sourceStatus==='existing'){
      const continuous=n(input.sourceContinuousW);
      const surge=n(input.sourceSurgeW);
      const wh=n(input.sourceWh);
      const batteryNeeded=['power_station','inverter'].includes(input.sourceType);
      const missing=continuous===null||continuous<=0||surge===null||surge<=0||(batteryNeeded&&(wh===null||wh<=0));
      if(missing){
        const result=base('evidence_required','Mevcut kaynağın sürekli, tepe ve enerji değerini doğrulayın','Sadece model adı, VA veya pazarlama tepe değeri yeterli değildir.');
        result.metrics=metrics;
        result.foodSafety=safety;
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
      const capacityIssues=uniq([
        !continuousOk&&`Mevcut kaynağın ${round(continuous)} W sürekli gücü, gereken yaklaşık ${metrics.requiredContinuousW} W değerinin altında.`,
        !surgeOk&&`Mevcut kaynağın ${round(surge)} W tepe gücü, kompresör için gereken yaklaşık ${metrics.requiredSurgeW} W değerinin altında.`,
        !whOk&&`Mevcut kaynağın ${round(wh)} Wh enerjisi, hedef süre için gereken yaklaşık ${metrics.requiredWh} Wh değerinin altında.`
      ]);
      const compatibilityIssues=uniq([
        !waveformOk&&'Saf sinüs çıkış doğrulanmadı.',
        !outputOk&&'230 V / 50 Hz ve üretici cihaz kullanım uygunluğu doğrulanmadı.',
        !startOk&&(input.startTest==='failed'?'Kontrollü kompresör başlatma testi başarısız oldu.':'Kontrollü kompresör başlatma testi yapılmadı.')
      ]);
      sourceAssessment={continuousOk,surgeOk,whOk,waveformOk,outputOk,startOk,capacityIssues,compatibilityIssues};
    }

    if(input.scenario==='active'){
      const result=base('active_event','Aktif kesintide önce gıda güvenliği ve mevcut kaynak sınırlarını yönetin','Ürün teslimatını anlık çözüm olarak beklemeyin. Kapıları kapalı tutun, sıcaklığı termometreyle izleyin ve yetersiz kaynağı zorlamayın.');
      result.metrics=metrics;
      result.foodSafety=safety;
      result.issues=uniq([
        ...foodSafetyIssues(input,safety,outageHours),
        ...(sourceAssessment?sourceAssessment.capacityIssues:[]),
        ...(sourceAssessment?sourceAssessment.compatibilityIssues:[])
      ]);
      result.steps=['Kapıları mümkün olduğunca kapalı tutun.','Buzdolabında gerçek sıcaklığı 4 °C (40 °F) veya altında termometreyle doğrulayın.','Kaynak kapasitesi veya başlatma testi yetersizse cihazı tekrar tekrar çalıştırmayı denemeyin.','Güvenli süre aşılacaksa buz/soğutucu ve gıda imha kararını resmî gıda güvenliği rehberine göre uygulayın.'];
      result.toolKeys=['compare'];
      return result;
    }

    if(sourceAssessment){
      if(!sourceAssessment.capacityIssues.length&&!sourceAssessment.compatibilityIssues.length){
        const result=base('no_buy','Mevcut kaynak doğrulanmış eşikleri karşılıyorsa yeni ürün almayın','Girilen teknik değerler ve kontrollü kompresör başlatma testine göre mevcut kaynak yeterli görünüyor.');
        result.metrics=metrics;
        result.foodSafety=safety;
        result.steps=['Cihazı en sıcak beklenen ortamda kontrollü süre testiyle doğrulayın.','Gıda termometresini, kabloyu, prizi ve kaynak sıcaklığını periyodik kontrol edin.'];
        result.toolKeys=['compare'];
        return result;
      }
      if(!sourceAssessment.capacityIssues.length&&sourceAssessment.compatibilityIssues.length){
        const result=base('evidence_required','Güç değerleri yeterli görünse de uyumluluk kanıtı eksik','Kompresör ve elektronik kart için dalga biçimi, 230 V / 50 Hz çıkış ve gerçek başlatma testi doğrulanmadan uygunluk sonucu verilmez.');
        result.metrics=metrics;
        result.foodSafety=safety;
        result.issues=sourceAssessment.compatibilityIssues;
        result.steps=['Kaynağı üretici talimatına uygun yük altında test edin; korumaya geçerse daha büyük ürün satın almadan kök nedeni doğrulayın.'];
        result.toolKeys=['compare'];
        return result;
      }
    }

    const category=chooseCategory(input,metrics);
    const result=base('conditional_purchase','Kaynak yetersiz veya eksik; yalnız hesaplanan sınıfa ilerleyin','Bu sonuç belirli marka/model onayı değildir. Sürekli güç, kompresör başlangıcı, saf sinüs, çıkış kararlılığı ve enerji kapasitesi birlikte doğrulanmalıdır.');
    result.metrics=metrics;
    result.foodSafety=safety;
    result.issues=uniq([
      ...(sourceAssessment?sourceAssessment.capacityIssues:[]),
      `En az yaklaşık ${metrics.requiredContinuousW} W sürekli güç gerekir.`,
      `Kompresör başlangıcı için yaklaşık ${metrics.requiredSurgeW} W kısa süreli kapasite gerekir.`,
      ...(['power_station','inverter'].includes(category)?[`Hedef süre için yaklaşık ${metrics.requiredWh} Wh nominal enerji gerekir.`]:[])
    ]);
    result.steps=['Üretici sayfasında sürekli güç ile tepe/X-Boost değerini ayırın.','Saf sinüs, 230 V / 50 Hz çıkış ve kompresör kullanım uygunluğunu doğrulayın.','Cihazı kontrollü gerçek başlatma ve süre testiyle kabul edin.'];
    result.commerceCategories=[category];
    result.toolKeys=[category];
    result.commerceClosed=false;
    return result;
  }

  const gateReady=(actualNeed,technicalCheck,affiliateCheck)=>Boolean(actualNeed&&technicalCheck&&affiliateCheck);

  function init(doc){
    const form=doc.getElementById('fridgeForm');
    if(!form)return;
    const $=id=>doc.getElementById(id);
    const ids=['emergency','medicalStorage','scenario','applianceType','connection','phase','doorClosed','freezerFill','outageHours','labelW','voltage','ratedCurrent','powerFactor','startupW','dutyCyclePct','otherLoadW','targetHours','sourceStatus','sourceType','sourceContinuousW','sourceSurgeW','sourceWh','waveform','outputSpec','startTest'];
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
      const entries=[['Kompresör çalışma yükü',`${metrics.runningW} W`],['Sürekli alt sınır',`${metrics.requiredContinuousW} W`],['Kalkış alt sınırı',`${metrics.requiredSurgeW} W`],['Ortalama planlama yükü',`${metrics.averageW} W`],['Nominal enerji',`${metrics.requiredWh} Wh`]];
      const wrap=doc.createElement('div');wrap.className='metrics';
      entries.forEach(([label,value])=>{const article=doc.createElement('article');const span=doc.createElement('span');span.textContent=label;const strong=doc.createElement('strong');strong.textContent=value;article.append(span,strong);wrap.appendChild(article);});
      area.appendChild(wrap);
      const notes=[];
      if(metrics.pfAssumed)notes.push('Güç faktörü 0,85 varsayıldı.');
      if(metrics.powerFromCurrent&&metrics.phaseFactor>1)notes.push('Trifaze V/A hesabında √3 katsayısı kullanıldı.');
      notes.push(metrics.startupAssumed?`Kalkış gücü cihaz türü için ${metrics.multiplier}× planlama katsayısıyla tahmin edildi.`:'Kalkış gücü üretici değeriyle hesaplandı.');
      notes.push(metrics.dutyAssumed?`Enerji hesabında %${metrics.dutyPct} çalışma oranı varsayıldı; sıcak ortam ve kapı açılması tüketimi artırabilir.`:`Enerji hesabında girilen %${metrics.dutyPct} çalışma oranı kullanıldı.`);
      const note=doc.createElement('p');note.className='privacy';note.textContent=notes.join(' ');area.appendChild(note);
    };
    const renderSafety=safety=>{
      const area=$('foodSafetyArea');area.innerHTML='';
      if(!safety)return;
      const box=doc.createElement('div');box.className='food-safety';
      const strong=doc.createElement('strong');strong.textContent=`Soğuk saklama rehberi: ${safety.label}`;
      const p=doc.createElement('p');p.textContent=safety.note;
      box.append(strong,p);area.appendChild(box);
    };
    const renderTools=keys=>{const area=$('toolLinks');area.innerHTML='';keys.forEach(key=>{const item=TOOL_LINKS[key];if(!item)return;const a=doc.createElement('a');a.className='button';a.href=item.href;a.textContent=item.label;area.appendChild(a);});};
    const updateGate=()=>{$('openProducts').disabled=!gateReady($('actualNeed').checked,$('technicalCheck').checked,$('affiliateCheck').checked);};
    const track=(event,payload)=>{if(typeof globalThis!=='undefined'&&typeof globalThis.Alo186Track==='function')globalThis.Alo186Track(event,payload);};

    function render(result){
      lastResult=result;
      resultBox.className=`panel result status-${result.status}`;
      resultBox.classList.remove('hidden');
      $('resultBadge').textContent=result.status.replaceAll('_',' ');
      $('resultTitle').textContent=result.title;
      $('resultSummary').textContent=result.summary;
      renderMetrics(result.metrics);
      renderSafety(result.foodSafety);
      renderList($('issueList'),result.issues);
      renderList($('stepList'),result.steps);
      renderTools(result.toolKeys);
      commerceGate.classList.toggle('hidden',result.commerceClosed||!result.commerceCategories.length);
      productLinks.innerHTML='';
      ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>{$(id).checked=false;});
      $('openProducts').disabled=true;
      resultBox.focus();
      track('calculator_result',{tool:'fridge_freezer_backup',result_status:result.status});
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
      track('affiliate_category_gate_open',{tool:'fridge_freezer_backup',categories:lastResult.commerceCategories.join(',')});
    });
    showExisting();
  }

  return {ROUTE,PF_DEFAULT,RESERVE,SURGE_RESERVE,BATTERY_EFF,USABLE,START_MULTIPLIER,DUTY_CYCLE_DEFAULT,foodSafetyWindow,calculations,foodSafetyIssues,evaluate,gateReady,init};
});
