(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const POWERBANK_NOMINAL_LIMIT_WH=100;
  const n=value=>{
    if(value===null||value===undefined||value==='')return null;
    const parsed=Number(String(value).replace(',','.'));
    return Number.isFinite(parsed)?parsed:null;
  };
  const roundUp=(value,step=10)=>Math.ceil(value/step)*step;
  const unique=values=>[...new Set(values.filter(Boolean))];
  const makeResult=(status,title,summary,extra={})=>({status,title,summary,commercialAllowed:false,categories:[],...extra});

  const CATEGORY_LABELS={
    powerbank:'USB-C PD powerbank sınıfı',
    mini_ups:'Modem / ONT mini UPS sınıfı',
    usb_c_charger:'USB-C PD şarj adaptörü',
    usb_c_cable:'5 A E-marker USB-C kablo',
    power_station:'Power station sınıfı'
  };

  function architectureLabel(value){
    return ({
      no_external:'Haricî kaynak gerekmiyor',
      network_only:'Modem / ONT mini UPS',
      powerbank_only:'USB-C powerbank',
      split_dc:'Ayrık DC set: powerbank + mini UPS',
      power_station:'Tek AC kaynak: power station',
      ups_path:'UPS topolojisi'
    })[value]||value;
  }

  function calculate(input={}){
    if(input.emergency){
      return makeResult('emergency','Kullanmayı bırakın ve enerjiyi kesin','Şişmiş veya sızdıran batarya, yanık kokusu, kıvılcım, aşırı ısınma, hasarlı kablo, su teması ya da elektrik çarpması riski varsa ekipmanı şarj etmeyin. Güvenli biçimde enerjisiz bırakın; yangın veya yaralanma riski varsa 112’yi arayın.');
    }
    if(input.criticalUse){
      return makeResult('professional','Kritik süreklilik tasarımı gerekli','Sağlık, güvenlik, sunucu, çağrı merkezi veya hizmet kesintisinin kabul edilemediği işlerde tüketici tipi bir set tek başına yeterlilik kanıtı değildir. UPS topolojisi, yedeklilik, akü testi, ağ ve bakım planı birlikte projelendirilmelidir.');
    }

    const scenario=input.scenario||'planning';
    const computerType=input.computerType||'unknown';
    const transferTolerance=input.transferTolerance||'seconds_ok';
    const targetHours=n(input.targetHours);
    const laptopW=n(input.laptopW);
    const laptopInternalHours=n(input.laptopInternalHours)??0;
    const modemW=n(input.modemW)??0;
    const ontW=n(input.ontW)??0;
    const routerW=n(input.routerW)??0;
    const monitorW=n(input.monitorW)??0;
    const dockW=n(input.dockW)??0;
    const otherW=n(input.otherW)??0;

    if(targetHours===null||targetHours<0.5||targetHours>24){
      return makeResult('evidence_required','Hedef çalışma süresini doğrulayın','Kesinti sırasında çalışmak istediğiniz süreyi 0,5–24 saat aralığında girin.');
    }
    if(!['usb_c_laptop','barrel_laptop','desktop','none'].includes(computerType)){
      return makeResult('evidence_required','Bilgisayar besleme türü gerekli','USB-C PD dizüstü, klasik adaptörlü dizüstü, masaüstü bilgisayar veya yalnız ağ cihazı seçeneğinden birini doğrulayın.');
    }
    if([modemW,ontW,routerW,monitorW,dockW,otherW].some(value=>value<0)){
      return makeResult('evidence_required','Negatif güç değeri kullanılamaz','Cihaz etiketlerini yeniden kontrol edin; kullanılmayan yükleri 0 W olarak bırakabilirsiniz.');
    }
    if(computerType!=='none'&&(laptopW===null||laptopW<=0||laptopW>1500)){
      return makeResult('evidence_required','Bilgisayar giriş gücü gerekli','Adaptör veya güç kaynağı etiketindeki azami giriş/çıkış watt değerini doğrulayın.');
    }
    if(laptopInternalHours<0||laptopInternalHours>24){
      return makeResult('evidence_required','Dahili batarya süresini doğrulayın','Dizüstü bilgisayarın mevcut batarya süresini 0–24 saat aralığında girin.');
    }

    const networkW=modemW+ontW+routerW;
    const acAccessoryW=monitorW+dockW+otherW;
    const hasComputer=computerType!=='none';
    const externalLaptopHours=hasComputer?Math.max(0,targetHours-Math.min(laptopInternalHours,targetHours)):0;
    const activeLaptopW=externalLaptopHours>0?(laptopW||0):0;
    const totalActiveW=activeLaptopW+networkW+acAccessoryW;

    if(totalActiveW<=0){
      const metrics={
        targetHours,laptopExternalHours:0,networkW:0,acAccessoryW:0,totalActiveW:0,
        requiredPdW:0,requiredPowerbankWh:0,requiredMiniUpsW:0,requiredMiniUpsWh:0,
        requiredPowerStationW:0,requiredPowerStationWh:0,powerbankNominalLimitWh:POWERBANK_NOMINAL_LIMIT_WH,
        powerbankLimitExceeded:false,architecture:'no_external',architectureLabel:architectureLabel('no_external')
      };
      return makeResult('no_buy','Haricî enerji kaynağı gerekmiyor — yeni ürün almayın','Dizüstü bilgisayarın mevcut bataryası hedef süreyi karşılıyor ve kesintide çalışacak başka cihaz seçilmedi. Batarya sağlığını ve gerçek süreyi kontrollü olarak yeniden test edin.',{metrics});
    }

    if(totalActiveW>1500||acAccessoryW>1200){
      return makeResult('professional','Yüksek güçlü çalışma alanı için profesyonel tasarım gerekli','Toplam aktif yük 1,5 kW sınırını veya yardımcı AC yükler 1,2 kW sınırını aşıyor. Devre, UPS, akü, soğutma, kablo ve seçicilik birlikte değerlendirilmelidir.');
    }

    const rawPowerStationEnergy=(activeLaptopW*externalLaptopHours)+(networkW+acAccessoryW)*targetHours;
    const requiredPdW=computerType==='usb_c_laptop'&&activeLaptopW>0?roundUp(activeLaptopW*1.15,5):0;
    const requiredPowerbankWh=computerType==='usb_c_laptop'&&externalLaptopHours>0?roundUp((activeLaptopW*externalLaptopHours)/(0.90*0.80),10):0;
    const requiredMiniUpsW=networkW>0?roundUp(networkW*1.25,1):0;
    const requiredMiniUpsWh=networkW>0?roundUp((networkW*targetHours)/(0.90*0.80),5):0;
    const requiredPowerStationW=roundUp(totalActiveW*1.25,10);
    const requiredPowerStationWh=roundUp(rawPowerStationEnergy/(0.85*0.80),10);
    const powerbankLimitExceeded=requiredPowerbankWh>POWERBANK_NOMINAL_LIMIT_WH;

    const requiresZeroTransfer=transferTolerance==='zero';
    if(computerType==='desktop'||requiresZeroTransfer){
      const metrics={
        targetHours,laptopExternalHours:externalLaptopHours,networkW,acAccessoryW,totalActiveW,
        requiredPdW:0,requiredPowerbankWh:0,requiredMiniUpsW:0,requiredMiniUpsWh:0,
        requiredPowerStationW,requiredPowerStationWh,powerbankNominalLimitWh:POWERBANK_NOMINAL_LIMIT_WH,
        powerbankLimitExceeded:false,architecture:'ups_path',architectureLabel:architectureLabel('ups_path')
      };
      return makeResult('ups_path','UPS VA ve topoloji testiyle devam edin','Masaüstü bilgisayar veya sıfıra yakın transfer süresi isteyen kullanım, yalnız power station watt değeriyle doğrulanamaz. Gerçek W, VA, güç faktörü, transfer süresi ve batarya süresini UPS uygunluk aracında değerlendirin.',{metrics,nextTool:'/hesaplama/ups-va-topoloji-uygunluk/'});
    }

    if(computerType==='usb_c_laptop'&&externalLaptopHours>0){
      if(input.laptopPdVerified!=='yes'){
        return makeResult('evidence_required','USB-C şarj kabulü doğrulanmalı','Bilgisayardaki USB-C portun gerçekten şarj girişi olduğunu ve kabul ettiği watt değerini üretici kılavuzu veya adaptör etiketiyle doğrulayın. Yalnız USB-C konnektörü bulunması PD şarj desteği anlamına gelmez.');
      }
      if(!['yes','no'].includes(input.chargerAdequate)||!['yes','no'].includes(input.cableAdequate)){
        return makeResult('evidence_required','Adaptör ve kablo sınıfını doğrulayın','Mevcut USB-C adaptörün gerekli PD wattını ve kablonun 3 A/5 A ile E-marker sınıfını karşılayıp karşılamadığını belirleyin.');
      }
    }

    const splitEligible=computerType==='usb_c_laptop'&&activeLaptopW>0&&activeLaptopW<=140&&acAccessoryW===0&&!powerbankLimitExceeded;
    const networkOnly=activeLaptopW===0&&networkW>0&&acAccessoryW===0;
    if((splitEligible||networkOnly)&&networkW>0){
      if(input.networkVoltageVerified!=='yes'||input.networkPolarityVerified!=='yes'||input.networkJackVerified!=='yes'){
        return makeResult('evidence_required','Modem ve ONT çıkış uyumu gerekli','Mini UPS seçmeden önce her cihazın voltajı, polaritesi ve DC jak ölçüsü ayrı ayrı doğrulanmalıdır. Yanlış voltaj veya polarite cihaz hasarına neden olabilir.');
      }
    }

    let architecture='power_station';
    if(networkOnly)architecture='network_only';
    else if(splitEligible&&networkW===0)architecture='powerbank_only';
    else if(splitEligible&&networkW>0)architecture='split_dc';

    const metrics={
      targetHours,
      laptopExternalHours:Math.round(externalLaptopHours*100)/100,
      networkW:Math.round(networkW*10)/10,
      acAccessoryW:Math.round(acAccessoryW*10)/10,
      totalActiveW:Math.round(totalActiveW*10)/10,
      requiredPdW,
      requiredPowerbankWh,
      requiredMiniUpsW,
      requiredMiniUpsWh,
      requiredPowerStationW,
      requiredPowerStationWh,
      splitNominalWh:requiredPowerbankWh+requiredMiniUpsWh,
      powerbankNominalLimitWh:POWERBANK_NOMINAL_LIMIT_WH,
      powerbankLimitExceeded,
      architecture,
      architectureLabel:architectureLabel(architecture)
    };

    let baseCategories=[];
    if(architecture==='network_only')baseCategories=['mini_ups'];
    if(architecture==='powerbank_only'||architecture==='split_dc'){
      if(requiredPowerbankWh>0)baseCategories.push('powerbank');
      if(networkW>0)baseCategories.push('mini_ups');
      if(input.chargerAdequate==='no')baseCategories.push('usb_c_charger');
      if(input.cableAdequate==='no')baseCategories.push('usb_c_cable');
    }
    if(architecture==='power_station')baseCategories=['power_station'];
    baseCategories=unique(baseCategories);

    if(scenario==='active'){
      return makeResult('active_event','Aktif kesintide güvenli çalışma süresini yönetin',`Hedef için ${architectureLabel(architecture)} yönü hesaplandı. Ürün teslimatı anlık çözüm değildir; mevcut batarya yüzdesini, modem/ONT çalışma süresini ve dosya yedeklemeyi önceliklendirin. Geçici ters besleme, hasarlı çoklayıcı veya aşırı yük kullanmayın.`,{metrics});
    }

    const sourceStatus=input.sourceStatus||'none';
    if(sourceStatus==='split_existing'){
      if(!['network_only','powerbank_only','split_dc'].includes(architecture)){
        const reason=powerbankLimitExceeded
          ? `Laptop için hesaplanan ${requiredPowerbankWh} Wh nominal enerji, tek powerbank ön seçim sınırı olan ${POWERBANK_NOMINAL_LIMIT_WH} Wh değerini aşıyor.`
          : 'Monitör, klasik adaptörlü dizüstü veya diğer AC yükleri ayrık DC set kapsamının dışında.';
        return makeResult('conditional_purchase','Ayrık DC set bu senaryoya uygun değil',`${reason} Yalnız hesaplanan power station sınıfına ilerleyin.`,{metrics,categories:['power_station'],commercialAllowed:true});
      }
      const gaps=[];
      const categories=[];
      if(requiredPowerbankWh>0){
        const existingPowerbankPDW=n(input.existingPowerbankPDW);
        const existingPowerbankWh=n(input.existingPowerbankWh);
        if(existingPowerbankPDW===null||existingPowerbankWh===null){
          return makeResult('evidence_required','Mevcut powerbank etiketi gerekli',`En az ${requiredPdW} W tek cihaz USB-C çıkışı ve yaklaşık ${requiredPowerbankWh} Wh nominal kapasiteyi doğrulayın.`,{metrics});
        }
        if(existingPowerbankPDW<requiredPdW){gaps.push(`${requiredPdW-existingPowerbankPDW} W USB-C çıkış`);categories.push('powerbank');}
        if(existingPowerbankWh<requiredPowerbankWh){gaps.push(`${requiredPowerbankWh-existingPowerbankWh} Wh powerbank kapasitesi`);categories.push('powerbank');}
      }
      if(requiredMiniUpsWh>0){
        const existingMiniUpsW=n(input.existingMiniUpsW);
        const existingMiniUpsWh=n(input.existingMiniUpsWh);
        if(existingMiniUpsW===null||existingMiniUpsWh===null||input.networkOutputVerified!=='yes'||input.blackoutTest!=='success'){
          return makeResult('evidence_required','Mevcut mini UPS kanıtı eksik',`En az ${requiredMiniUpsW} W çıkış, yaklaşık ${requiredMiniUpsWh} Wh kapasite, doğru voltaj/polarite/jak ve kontrollü kesinti testi birlikte doğrulanmalıdır.`,{metrics});
        }
        if(existingMiniUpsW<requiredMiniUpsW){gaps.push(`${requiredMiniUpsW-existingMiniUpsW} W mini UPS çıkışı`);categories.push('mini_ups');}
        if(existingMiniUpsWh<requiredMiniUpsWh){gaps.push(`${requiredMiniUpsWh-existingMiniUpsWh} Wh mini UPS kapasitesi`);categories.push('mini_ups');}
      }
      if(input.chargerAdequate==='no'){gaps.push('uygun PD adaptör');categories.push('usb_c_charger');}
      if(input.cableAdequate==='no'){gaps.push('uygun 5 A/E-marker kablo');categories.push('usb_c_cable');}
      if(gaps.length===0){
        return makeResult('no_buy','Mevcut ayrık set yeterli — yeni ürün almayın',`Mevcut powerbank ve mini UPS; ${requiredPdW||'—'} W PD, ${requiredPowerbankWh||'—'} Wh laptop enerjisi ve ${requiredMiniUpsW||'—'} W / ${requiredMiniUpsWh||'—'} Wh ağ ihtiyacını, çıkış doğrulamasını ve gerçek kesinti testini karşılıyor.`,{metrics});
      }
      return makeResult('conditional_purchase','Mevcut sette doğrulanmış açık var',`${gaps.join(', ')} eksiği bulundu. Yalnız eksik bileşen sınıflarına ilerleyin; yeterli parçaları yeniden satın almayın.`,{metrics,categories:unique(categories),commercialAllowed:true});
    }

    if(sourceStatus==='power_station_existing'){
      const sourceW=n(input.existingPowerStationW);
      const sourceWh=n(input.existingPowerStationWh);
      if(sourceW===null||sourceWh===null||input.existingOutputVerified!=='yes'||input.existingPureSine!=='yes'||input.blackoutTest!=='success'){
        return makeResult('evidence_required','Mevcut power station kanıtı eksik',`En az ${requiredPowerStationW} W sürekli çıkış, yaklaşık ${requiredPowerStationWh} Wh nominal enerji, saf sinüs 230 V / 50 Hz ve kontrollü gerçek kesinti testi birlikte doğrulanmalıdır.`,{metrics});
      }
      const gaps=[];
      if(sourceW<requiredPowerStationW)gaps.push(`${requiredPowerStationW-sourceW} W sürekli güç`);
      if(sourceWh<requiredPowerStationWh)gaps.push(`${requiredPowerStationWh-sourceWh} Wh enerji`);
      if(gaps.length===0){
        return makeResult('no_buy','Mevcut power station yeterli — yeni ürün almayın',`Mevcut kaynak ${requiredPowerStationW} W sürekli güç ve ${requiredPowerStationWh} Wh nominal enerji eşiğini, saf sinüs çıkışı ve gerçek kesinti testini karşılıyor. Düzenli batarya ve kablo kontrolü yapın.`,{metrics});
      }
      return makeResult('conditional_purchase','Mevcut power station kapasitesi yetersiz',`${gaps.join(' ve ')} açığı var. Yalnız bu eşikleri karşılayan power station sınıfına ilerleyin.`,{metrics,categories:['power_station'],commercialAllowed:true});
    }

    let summary;
    if(architecture==='split_dc'){
      summary=`Dizüstü için yaklaşık ${requiredPdW} W PD ve ${requiredPowerbankWh} Wh powerbank; modem/ONT için ${requiredMiniUpsW} W ve ${requiredMiniUpsWh} Wh mini UPS gerekir. Ayrık DC set yalnız gerçek eksik bileşenlerle kurulmalıdır.`;
    }else if(architecture==='powerbank_only'){
      summary=`Dizüstü için yaklaşık ${requiredPdW} W tek cihaz USB-C çıkışı ve ${requiredPowerbankWh} Wh nominal powerbank kapasitesi gerekir.`;
    }else if(architecture==='network_only'){
      summary=`Modem/ONT ağı için yaklaşık ${requiredMiniUpsW} W çıkış ve ${requiredMiniUpsWh} Wh nominal mini UPS kapasitesi gerekir.`;
    }else if(powerbankLimitExceeded&&computerType==='usb_c_laptop'&&acAccessoryW===0){
      summary=`Laptop için hesaplanan ${requiredPowerbankWh} Wh nominal enerji, tek powerbank ön seçim sınırı olan ${POWERBANK_NOMINAL_LIMIT_WH} Wh değerini aşıyor. Bu nedenle yaklaşık ${requiredPowerStationW} W / ${requiredPowerStationWh} Wh power station sınıfına ilerleyin.`;
    }else{
      summary=`Tek AC kaynak için yaklaşık ${requiredPowerStationW} W sürekli çıkış ve ${requiredPowerStationWh} Wh nominal enerji gerekir.`;
    }
    return makeResult('conditional_purchase','Yedek çalışma seti hesaplandı',summary,{metrics,categories:baseCategories,commercialAllowed:baseCategories.length>0});
  }

  const statusLabels={
    emergency:'Acil',professional:'Profesyonel',evidence_required:'Kanıt gerekli',
    ups_path:'UPS yolu',active_event:'Aktif kesinti',no_buy:'Satın alma yok',
    conditional_purchase:'Koşullu ürün'
  };

  function readForm(doc){
    const id=name=>doc.getElementById(name);
    const value=name=>id(name)?.value;
    const checked=name=>Boolean(id(name)?.checked);
    return{
      emergency:checked('emergency'),criticalUse:checked('criticalUse'),scenario:value('scenario'),
      computerType:value('computerType'),transferTolerance:value('transferTolerance'),laptopW:value('laptopW'),
      laptopInternalHours:value('laptopInternalHours'),laptopPdVerified:value('laptopPdVerified'),
      chargerAdequate:value('chargerAdequate'),cableAdequate:value('cableAdequate'),
      modemW:value('modemW'),ontW:value('ontW'),routerW:value('routerW'),monitorW:value('monitorW'),
      dockW:value('dockW'),otherW:value('otherW'),targetHours:value('targetHours'),
      networkVoltageVerified:value('networkVoltageVerified'),networkPolarityVerified:value('networkPolarityVerified'),
      networkJackVerified:value('networkJackVerified'),sourceStatus:value('sourceStatus'),
      existingPowerbankPDW:value('existingPowerbankPDW'),existingPowerbankWh:value('existingPowerbankWh'),
      existingMiniUpsW:value('existingMiniUpsW'),existingMiniUpsWh:value('existingMiniUpsWh'),
      networkOutputVerified:value('networkOutputVerified'),existingPowerStationW:value('existingPowerStationW'),
      existingPowerStationWh:value('existingPowerStationWh'),existingPureSine:value('existingPureSine'),
      existingOutputVerified:value('existingOutputVerified'),blackoutTest:value('blackoutTest')
    };
  }

  function mount(doc){
    const form=doc.getElementById('homeOfficeForm');
    if(!form)return;
    const $=id=>doc.getElementById(id);

    const toggle=()=>{
      const computerType=$('computerType').value;
      $('computerFields').classList.toggle('hidden',computerType==='none');
      $('usbCFields').classList.toggle('hidden',computerType!=='usb_c_laptop');
      const networkLoad=[Number($('modemW').value)||0,Number($('ontW').value)||0,Number($('routerW').value)||0].some(value=>value>0);
      $('networkCompatibility').classList.toggle('hidden',!networkLoad);
      const source=$('sourceStatus').value;
      $('splitExistingFields').classList.toggle('hidden',source!=='split_existing');
      $('powerStationExistingFields').classList.toggle('hidden',source!=='power_station_existing');
    };
    ['computerType','sourceStatus','modemW','ontW','routerW'].forEach(id=>$(id)?.addEventListener('change',toggle));
    toggle();

    form.addEventListener('submit',event=>{
      event.preventDefault();
      const out=calculate(readForm(doc));
      const box=$('result');
      box.className=`panel result status-${out.status}`;
      box.hidden=false;
      $('resultBadge').textContent=statusLabels[out.status]||out.status;
      $('resultTitle').textContent=out.title;
      $('resultSummary').textContent=out.summary;
      const m=out.metrics;
      $('metrics').innerHTML=m?[
        ['Önerilen mimari',m.architectureLabel],
        ['Aktif yük',`${m.totalActiveW} W`],
        ['Laptop haricî süre',`${m.laptopExternalHours} saat`],
        ['Powerbank alt sınırı',m.requiredPowerbankWh?`${m.requiredPdW} W / ${m.requiredPowerbankWh} Wh`:'—'],
        ['Mini UPS alt sınırı',m.requiredMiniUpsWh?`${m.requiredMiniUpsW} W / ${m.requiredMiniUpsWh} Wh`:'—'],
        ['Power station alt sınırı',m.requiredPowerStationWh?`${m.requiredPowerStationW} W / ${m.requiredPowerStationWh} Wh`:'—']
      ].map(([label,value])=>`<article><span>${label}</span><strong>${value}</strong></article>`).join(''):'';
      const next=$('nextTool');
      if(out.nextTool){next.href=out.nextTool;next.classList.remove('hidden');}else{next.removeAttribute('href');next.classList.add('hidden');}
      const commerce=$('commerce');
      commerce.classList.toggle('hidden',!out.commercialAllowed);
      commerce.dataset.categories=JSON.stringify(out.categories||[]);
      ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>{$(id).checked=false;});
      $('bundleLinks').innerHTML='';
      box.scrollIntoView({behavior:'smooth',block:'start'});
      box.focus({preventScroll:true});
      if(root.Alo186Track)root.Alo186Track('home_office_backup_result',{status:out.status,architecture:m?.architecture||'none',categories:(out.categories||[]).join(',')});
    });

    const refreshGate=()=>{
      const commerce=$('commerce');
      const enabled=!commerce.classList.contains('hidden')&&['actualNeed','technicalCheck','affiliateCheck'].every(id=>$(id).checked);
      const categories=JSON.parse(commerce.dataset.categories||'[]');
      const target=$('bundleLinks');
      target.innerHTML='';
      if(!enabled)return;
      categories.forEach(category=>{
        const link=doc.createElement('a');
        link.className='button primary';
        link.href=`../../akilli-urun-secimi?kategori=${encodeURIComponent(category)}&kaynak=evden-calisma-seti`;
        link.textContent=`${CATEGORY_LABELS[category]||category} aç`;
        link.dataset.category=category;
        target.appendChild(link);
      });
    };
    ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>$(id)?.addEventListener('change',refreshGate));
  }

  return{calculate,mount,architectureLabel,CATEGORY_LABELS,POWERBANK_NOMINAL_LIMIT_WH};
});
