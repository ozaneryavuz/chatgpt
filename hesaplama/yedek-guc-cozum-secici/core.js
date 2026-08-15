(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186BackupSelector=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const solutions={
    mini_ups:{label:'Modem / ONT Mini UPS',note:'Düşük güçlü DC ağ cihazları için kesintisiz ve sade çözüm.',nextStepUrl:'https://alo186.com/hesaplama/modem-internet-yedekleme/',nextStepLabel:'Modem ve ONT hesabını aç',productCategory:'mini_ups'},
    ups:{label:'UPS',note:'Kısa süre ve çok hızlı geçiş isteyen elektronik yükler için.',nextStepUrl:'https://alo186.com/hesaplama/ups-suresi/',nextStepLabel:'UPS süre hesabını aç',productCategory:null},
    power_station:{label:'Taşınabilir Power Station',note:'Egzozsuz, taşınabilir ve orta süreli fişli yükler için.',nextStepUrl:'https://alo186.com/hesaplama/ups-suresi/',nextStepLabel:'Wh ve çalışma süresi hesabını aç',productCategory:'power_station'},
    inverter_battery:{label:'Saf Sinüs İnverter + Batarya',note:'Batarya altyapısı ve yeniden şarj planı bulunan sistemler için.',nextStepUrl:'https://alo186.com/hesaplama/inverter-uygunluk/',nextStepLabel:'İnverter ve batarya testini aç',productCategory:'inverter'},
    generator:{label:'Jeneratör',note:'Uzun süreli veya yüksek enerjili yüklerde, güvenli dış ortam sağlanırsa.',nextStepUrl:'https://alo186.com/hesaplama/jenerator-gucu-secimi/',nextStepLabel:'Jeneratör gücü hesabını aç',productCategory:'generator'},
    hybrid:{label:'Hibrit Batarya + Jeneratör / GES',note:'Uzun süre, sessizlik ve sabit tesisatın birlikte istendiği profesyonel mimari.',nextStepUrl:'https://alo186.com/haberler/ges-elektrik-kesintisinde-calisir-mi',nextStepLabel:'Hibrit yedekleme rehberini aç',productCategory:null},
    professional:{label:'Profesyonel Yedek Güç Tasarımı',note:'Ürün sınıfından önce tesisat, transfer, faz ve güvenlik tasarımı gerekir.',nextStepUrl:'https://alo186.com/hesaplama/jenerator-gucu-secimi/',nextStepLabel:'Ön güç hesabını aç',productCategory:null}
  };

  function number(value,name,min,max){
    const n=Number(value);
    if(!Number.isFinite(n)||n<min||n>max)throw new Error(`${name} ${min} ile ${max} arasında olmalıdır.`);
    return n;
  }

  function calculateEnergyWh(continuousW,hours,options={}){
    const efficiency=number(options.efficiency==null?0.88:options.efficiency,'Verim',0.5,0.99);
    const reserve=number(options.reserve==null?0.2:options.reserve,'Rezerv',0,0.8);
    return Math.ceil((continuousW*hours/efficiency)*(1+reserve));
  }

  function analyze(raw){
    const input={
      continuousW:number(raw.continuousW,'Sürekli yük',1,50000),
      peakW:number(raw.peakW,'Tepe yük',1,100000),
      hours:number(raw.hours,'Çalışma süresi',0.1,168),
      transition:['instant','brief','manual'].includes(raw.transition)?raw.transition:'brief',
      scope:['dc-network','plug','motor','fixed'].includes(raw.scope)?raw.scope:'plug',
      phase:['single','three','unknown'].includes(raw.phase)?raw.phase:'unknown',
      portable:raw.portable==='yes',
      fuel:raw.fuel==='yes',
      outdoor:raw.outdoor==='yes',
      solar:raw.solar==='yes',
      medical:Boolean(raw.medical)
    };
    if(input.peakW<input.continuousW)throw new Error('Tepe yük, sürekli yükten küçük olamaz.');

    const energyWh=calculateEnergyWh(input.continuousW,input.hours);
    const fixedOrComplex=input.scope==='fixed'||input.phase!=='single';
    const highPower=input.continuousW>2500||input.peakW>5000;
    const longEnergy=energyWh>3500||input.hours>8;
    const reasons=[];
    const alternatives=[];
    let recommendation='power_station';

    if(input.medical){
      recommendation='professional';
      reasons.push('Tıbbi ve yaşam destek yüklerinde genel ürün önerisi güvenli değildir.');
      reasons.push('Cihaz üreticisinin güç kalitesi, çalışma süresi ve alarm planı doğrulanmalıdır.');
    }else if(fixedOrComplex||highPower){
      if(input.solar&&!input.fuel)recommendation='hybrid';
      else if(input.fuel&&input.outdoor)recommendation='generator';
      else recommendation='professional';
      reasons.push(input.scope==='fixed'?'Bina devreleri veya tüm yapı için transfer ve koruma tasarımı gerekir.':'Faz veya güç seviyesi tüketici tipi tak-çalıştır seçimin dışındadır.');
      if(input.phase!=='single')reasons.push('Trifaze veya belirsiz faz yapısında faz dengesi ve koruma koordinasyonu doğrulanmalıdır.');
    }else if(input.scope==='dc-network'&&input.continuousW<=60&&input.hours<=12){
      recommendation='mini_ups';
      reasons.push('Yük düşük güçlü modem/ONT sınıfında ve hedef süre mini UPS aralığındadır.');
      reasons.push('Voltaj, jak ve polarite eşleşmesi ürün kapasitesinden önce gelir.');
      alternatives.push('USB-C PD powerbank yalnız uyumlu DC dönüştürücü ve kesintisiz geçiş doğrulanırsa değerlendirilebilir.');
    }else if(input.transition==='instant'&&input.hours<=2&&input.peakW<=1800){
      recommendation='ups';
      reasons.push('Yük kesinti anında kapanmamalı ve hedef süre görece kısadır.');
      reasons.push('UPS seçiminde W, VA, güç faktörü ve gerçek çalışma süresi birlikte kontrol edilmelidir.');
      alternatives.push('Power station ancak modelin EPS/UPS geçiş süresi bağlı cihaz tarafından kabul ediliyorsa alternatif olabilir.');
    }else if(input.fuel&&input.outdoor&&longEnergy){
      recommendation='generator';
      reasons.push('Hedef enerji veya süre taşınabilir batarya sınıfını büyütmektedir.');
      reasons.push('Güvenli dış ortam ve yakıt/bakım koşulu sağlanabildiği belirtilmiştir.');
      alternatives.push(input.solar?'Gündüz üretimi ve kritik yük panosu bulunan hibrit batarya sistemi yakıt süresini azaltabilir.':'Kritik yükleri azaltmak daha küçük jeneratör veya batarya çözümünü mümkün kılabilir.');
    }else if(input.solar&&!input.portable&&energyWh>1800){
      recommendation='inverter_battery';
      reasons.push('Mevcut veya planlanan güneş/batarya altyapısı sessiz yedekleme için avantaj sağlar.');
      reasons.push('İnverter sürekli/tepe gücü ile batarya kWh kapasitesi ayrı boyutlandırılmalıdır.');
      alternatives.push('Çok uzun kesintilerde profesyonel jeneratör desteği hibrit mimaride değerlendirilebilir.');
    }else if(!input.fuel&&(input.portable||energyWh<=3000)&&input.peakW<=3000){
      recommendation='power_station';
      reasons.push('Egzozsuz ve taşınabilir/fişli kullanım şartları power station sınıfını öne çıkarır.');
      reasons.push('Wh kapasitesi kadar sürekli/tepe W ve saf sinüs uyumu da doğrulanmalıdır.');
      if(input.transition==='instant')alternatives.push('Kesintisiz geçiş kritikse bağımsız UPS daha güvenli bir ilk seçenek olabilir.');
      else alternatives.push('Kısa süreli bilgisayar ve ağ yüklerinde UPS daha ekonomik olabilir.');
    }else if(input.fuel&&input.outdoor){
      recommendation='generator';
      reasons.push('Yakıtlı çözüm ve güvenli dış ortam kabul edilmiştir.');
      reasons.push('Motor kalkış gücü ve hedef süre jeneratör hesabıyla doğrulanmalıdır.');
    }else{
      recommendation='inverter_battery';
      reasons.push('Yakıtlı jeneratör koşulu sağlanmadığı için batarya tabanlı çözüm öne çıkar.');
      reasons.push('DC akımı, BMS, kablo, sigorta ve yeniden şarj süresi profesyonel olarak doğrulanmalıdır.');
    }

    const professionalRequired=input.medical||fixedOrComplex||highPower||['hybrid','professional'].includes(recommendation);
    const commercialAllowed=!professionalRequired&&['mini_ups','power_station'].includes(recommendation);
    if(!alternatives.length){
      if(recommendation!=='ups')alternatives.push('Geçişin milisaniye düzeyinde kritik olduğu yüklerde UPS sınıfını ayrıca değerlendirin.');
      if(recommendation!=='generator')alternatives.push('Kesinti süresi uzadıkça yakıt, dış ortam ve bakım koşulları sağlanan jeneratör ekonomik olabilir.');
    }

    const checks=[
      'Cihaz etiketlerindeki gerçek sürekli ve kalkış watt değerlerini doğrulayın.',
      'Önerilen ürünün sürekli ve tepe çıkış sınırını ayrı kontrol edin.',
      'Hedef süre için kullanılabilir Wh kapasitesini, verim ve yaşlanma payıyla doğrulayın.'
    ];
    if(recommendation==='mini_ups')checks.push('DC voltaj, jak ölçüsü, polarite ve kesintisiz geçiş davranışını doğrulayın.');
    if(recommendation==='ups')checks.push('W ve VA sınırlarını, güç faktörünü ve transfer topolojisini doğrulayın.');
    if(recommendation==='power_station')checks.push('Saf sinüs, EPS geçiş süresi, batarya kimyası ve şarj girişlerini doğrulayın.');
    if(recommendation==='inverter_battery'||recommendation==='hybrid')checks.push('BMS, DC sigorta/ayırma, kablo, nötr-toprak düzeni ve transferi projelendirin.');
    if(recommendation==='generator')checks.push('Jeneratörü kapalı alanda kullanmayın; bina bağlantısını transfer sistemi olmadan yapmayın.');

    return {input,energyWh,recommendation,solution:solutions[recommendation],reasons,alternatives,checks,professionalRequired,commercialAllowed};
  }

  return {solutions,calculateEnergyWh,analyze};
});
