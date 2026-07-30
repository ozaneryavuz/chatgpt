(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const AFFILIATE_TAG='alo186rehber-21';
  const NOMINAL_VOLTAGE=230;
  const PLUG_AFFILIATE_MAX_A=10;
  const ABSOLUTE_PLUG_MAX_A=16;

  const num=(value)=>{
    if(value===null||value===undefined||value==='')return null;
    const parsed=Number(String(value).replace(',','.'));
    return Number.isFinite(parsed)?parsed:null;
  };
  const round=(value,digits=1)=>{
    const p=10**digits;
    return Math.round((value+Number.EPSILON)*p)/p;
  };
  const baseResult=(status,title,summary,extra={})=>({
    status,title,summary,commercialAllowed:false,searchUrl:null,searchTerm:null,
    monthlyKWh:null,monthlyCost:null,annualCost:null,standbyKWh:null,
    activeKWh:null,estimatedCurrentA:null,...extra
  });

  function metrics(input={}){
    const basis=input.measurementBasis||'unknown';
    const days=num(input.daysPerMonth);
    const tariff=num(input.tariff);
    let activeKWh=null;
    let standbyKWh=0;
    let monthlyKWh=null;

    if(basis==='measured_kwh'){
      const measuredKWh=num(input.measuredKWh);
      const measuredDays=num(input.measuredDays);
      if(measuredKWh!==null&&measuredDays&&days){
        monthlyKWh=(measuredKWh/measuredDays)*days;
        activeKWh=monthlyKWh;
      }
    }else{
      const activePowerW=num(input.activePowerW);
      const hours=num(input.hoursPerDay);
      const duty=num(input.dutyCyclePct);
      const standbyW=Math.max(0,num(input.standbyW)||0);
      const standbyHours=Math.max(0,num(input.standbyHoursPerDay)||0);
      if(activePowerW!==null&&hours!==null&&duty!==null&&days){
        activeKWh=(activePowerW*hours*days*(duty/100))/1000;
        standbyKWh=(standbyW*standbyHours*days)/1000;
        monthlyKWh=activeKWh+standbyKWh;
      }
    }

    const current=num(input.deviceCurrentA);
    const activePowerW=num(input.activePowerW);
    const estimatedCurrentA=current!==null?current:(activePowerW!==null?activePowerW/NOMINAL_VOLTAGE:null);
    const monthlyCost=monthlyKWh!==null&&tariff!==null?monthlyKWh*tariff:null;
    const annualCost=monthlyCost!==null?monthlyCost*12:null;

    return {
      activeKWh:activeKWh===null?null:round(activeKWh,2),
      standbyKWh:monthlyKWh===null?null:round(standbyKWh,2),
      monthlyKWh:monthlyKWh===null?null:round(monthlyKWh,2),
      monthlyCost:monthlyCost===null?null:round(monthlyCost,2),
      annualCost:annualCost===null?null:round(annualCost,2),
      estimatedCurrentA:estimatedCurrentA===null?null:round(estimatedCurrentA,2)
    };
  }

  const withMetrics=(result,m)=>({...result,...m});
  const highRiskRemote=(useCase)=>['refrigerator','motor','heater','kettle','air_conditioner'].includes(useCase||'');
  const lowRiskPlug=(input,m)=>{
    const current=num(input.deviceCurrentA);
    const power=num(input.activePowerW);
    return input.connection==='plug'&&input.environment==='dry'&&
      current!==null&&current>0&&current<=PLUG_AFFILIATE_MAX_A&&
      (power===null||power<=2300)&&
      !['ev','medical'].includes(input.useCase||'');
  };

  function calculate(input={}){
    if(input.emergency){
      return baseResult('emergency','Fişe veya cihaza dokunmayın','Duman, kıvılcım, erime, yanık kokusu, yoğun ısı veya elektrik çarpması riski varsa enerjiyi güvenli biçimde kestirin ve alandan uzaklaşın. Yangın, yaralanma veya yoğun dumanda 112 önceliklidir. Bütün ticari yollar kapalıdır.');
    }
    if(['hot','loose','damaged','wet'].includes(input.condition||'')){
      return baseResult('stop_use','Priz ve cihaz kullanılmamalı','Isınan, gevşek, kararmış, kırık, ıslak veya erime belirtisi bulunan priz/fiş üzerine enerji ölçer ya da akıllı priz takmayın. Yetkili elektrikçi kontrolü gerekir.');
    }
    if(input.condition!=='sound'){
      return baseResult('evidence_required','Priz ve fişin fiziksel durumunu doğrulayın','Ölçümden önce priz, fiş ve kablonun sağlam, kuru, sıkı ve olağandışı ısınmasız olduğunu doğrulayın.');
    }
    if(input.environment!=='dry'){
      return baseResult(input.environment==='wet'||input.environment==='outdoor'?'professional':'evidence_required','Islak veya dış ortamda kullanıcı tipi priz ölçeri kullanmayın','Bu araç yalnız kuru iç ortam, doğrudan duvar prizi ve kullanıcı tipi fişli yükler içindir. Dış ortam, ıslak hacim ve su riski profesyonel koruma ve uygun IP tasarımı gerektirir.');
    }
    if(['hardwired','three_phase'].includes(input.connection||'')){
      return baseResult('professional','Sabit veya trifaze ölçüm profesyonel projedir','Pano içi DIN sayaç, akım trafosu, pens ölçümü veya trifaze enerji analizi; uygun kategori, bağlantı, koruma ve yetkili kişi gerektirir. Affiliate yönlendirmesi kapalıdır.');
    }
    if(input.connection!=='plug'){
      return baseResult('evidence_required','Bağlantı biçimini doğrulayın','Bu araç yalnız tek fazlı, fişli ve doğrudan duvar prizine bağlanan cihazların ön değerlendirmesi içindir.');
    }
    if(['ev','medical'].includes(input.useCase||'')){
      return baseResult('professional','Bu yük tüketici tipi enerji ölçerle onaylanamaz',input.useCase==='ev'?'EV şarjı için priz tipi enerji ölçer veya akıllı priz kullanılmaz. EVSE, devre, RCD/DC kaçak koruması ve enerji ölçümü birlikte projelendirilmelidir.':'Medikal ve yaşam destek yüklerinde uzaktan anahtarlama veya genel tüketici tipi ölçer önerilmez; üretici ve profesyonel süreklilik planı gerekir.');
    }
    if(!['electronics','lighting','refrigerator','motor','heater','kettle','air_conditioner'].includes(input.useCase||'')){
      return baseResult('evidence_required','Cihaz sınıfını seçin','Elektronik, aydınlatma, buzdolabı, motorlu cihaz, ısıtıcı, su ısıtıcısı/ütü veya klima sınıfından birini seçin.');
    }

    const m=metrics(input);
    const days=num(input.daysPerMonth);
    const tariff=num(input.tariff);
    if(days===null||days<1||days>31){
      return withMetrics(baseResult('evidence_required','Ay içindeki kullanım gününü girin','Kullanım gününü 1–31 arasında girin.'),m);
    }
    if(tariff===null||tariff<=0||tariff>100){
      return withMetrics(baseResult('evidence_required','Faturanızdaki birim bedeli girin','Hesap güncel tarife varsaymaz. Vergi ve diğer bedeller dahil karşılaştırmak istediğiniz TL/kWh değerini kendi faturanızdan girin.'),m);
    }

    if(input.measurementBasis==='measured_kwh'){
      const measuredKWh=num(input.measuredKWh);
      const measuredDays=num(input.measuredDays);
      if(measuredKWh===null||measuredKWh<0||measuredDays===null||measuredDays<1||measuredDays>365){
        return withMetrics(baseResult('evidence_required','kWh ölçüm süresi ve tüketimini doğrulayın','Enerji ölçerdeki kWh farkını ve kaç gün ölçtüğünüzü girin. Sayaç başlangıç ve bitiş değerlerini aynı çalışma koşulunda karşılaştırın.'),m);
      }
    }else if(['measured_w','nameplate_w'].includes(input.measurementBasis||'')){
      const power=num(input.activePowerW);
      const hours=num(input.hoursPerDay);
      const duty=num(input.dutyCyclePct);
      const standbyHours=num(input.standbyHoursPerDay);
      if(power===null||power<=0||power>3680){
        return withMetrics(baseResult(power>3680?'professional':'evidence_required',power>3680?'3,68 kW üzeri yük profesyonel ölçüm gerektirir':'Aktif güç değerini watt olarak girin',power>3680?'Kullanıcı tipi fişli enerji ölçer sınırının dışında kalan yükleri pano/tesisat seviyesinde değerlendirin.':'Etiket veya ölçüm cihazındaki aktif güç W değerini girin; VA değerini watt yerine kullanmayın.'),m);
      }
      if(hours===null||hours<0||hours>24||duty===null||duty<0||duty>100||standbyHours===null||standbyHours<0||standbyHours>24||hours+standbyHours>24.01){
        return withMetrics(baseResult('evidence_required','Çalışma, görev oranı ve bekleme süresini düzeltin','Aktif ve bekleme saatlerinin toplamı 24 saati aşmamalı; görev oranı yüzde 0–100 arasında olmalıdır.'),m);
      }
    }else{
      return withMetrics(baseResult('evidence_required','Ölçüm temelini seçin','Doğrudan kWh ölçümü, ölçülmüş aktif watt veya yalnız etiket wattı seçeneklerinden birini seçin.'),m);
    }

    const deviceCurrent=num(input.deviceCurrentA);
    if(deviceCurrent===null||deviceCurrent<=0){
      return withMetrics(baseResult('evidence_required','Cihazın azami akımını doğrulayın','Priz tipi ölçer seçiminde yalnız watt yeterli değildir. Cihaz etiketi, kılavuz veya uygun ölçümle azami akımı amper olarak doğrulayın.'),m);
    }
    if(deviceCurrent>ABSOLUTE_PLUG_MAX_A){
      return withMetrics(baseResult('professional','16 A üzeri yük priz tipi ölçere bağlanmaz','Bu yük sabit tesisat veya özel devre ölçümü gerektirir. DIN sayaç/enerji analizörü seçimi yetkili elektrikçi tarafından yapılmalıdır.'),m);
    }
    if(deviceCurrent>PLUG_AFFILIATE_MAX_A){
      return withMetrics(baseResult('professional','Yüksek sürekli akım için profesyonel ölçüm kullanın','10 A üzerindeki sürekli veya uzun süreli yüklerde ara adaptör temasları ısınabilir. Priz, devre ve pano seviyesinde ölçüm değerlendirin; affiliate yolu kapalıdır.'),m);
    }

    const safeForAffiliate=lowRiskPlug(input,m);
    const meterSearch='16A priz tipi enerji ölçer kWh watt güç faktörü';
    const smartSearch='16A enerji ölçümlü akıllı priz kWh güç takibi';

    if(input.goal==='remote_control'&&highRiskRemote(input.useCase)){
      return withMetrics(baseResult('measurement_only','Bu cihazı uzaktan anahtarlamayın','Isıtıcı, ütü/su ısıtıcısı, kompresör veya motorlu yükte genel amaçlı akıllı prizle otomatik açma-kapama önerilmez. Yalnız üreticinin izin verdiği, gözetimli enerji ölçümünü değerlendirin.',{commercialAllowed:safeForAffiliate,productClass:'plug_energy_meter',searchTerm:meterSearch}),m);
    }

    if(input.measurementBasis==='nameplate_w'){
      return withMetrics(baseResult('estimate_only','Etiket wattı yalnız tahmindir','Termostat, kompresör, hız kontrolü, güç faktörü ve çalışma döngüsü gerçek tüketimi değiştirebilir. En az 24 saat; buzdolabı ve klima gibi çevrimli yüklerde tercihen birkaç gün kWh ölçümü yapın.',{commercialAllowed:safeForAffiliate&&input.existingType==='none',productClass:'plug_energy_meter',searchTerm:meterSearch}),m);
    }

    if(input.goal==='estimate_bill'){
      return withMetrics(baseResult('no_buy','Hesap tamamlandı; yeni ürün zorunlu değil',`Yaklaşık aylık tüketim ${m.monthlyKWh} kWh ve girdiğiniz birim bedelle ${m.monthlyCost} TL'dir. Bu sonuç ölçülmüş kWh temeline dayanıyorsa daha güvenilir; yalnız anlık watt temeline dayanıyorsa çalışma döngüsünü düzenli aralıklarla doğrulayın.`),m);
    }

    if(input.existingType==='none'){
      const productClass=input.goal==='remote_control'&&['electronics','lighting'].includes(input.useCase)?'energy_monitoring_smart_plug':'plug_energy_meter';
      const searchTerm=productClass==='energy_monitoring_smart_plug'?smartSearch:meterSearch;
      return withMetrics(baseResult('conditional_purchase','Ölçüm amacına uygun cihaz sınıfını doğrulayın',`Aylık yaklaşık ${m.monthlyKWh} kWh ve ${m.monthlyCost} TL görünür. Satın almadan önce 230 V, en az 16 A etiket sınırı, gerçek kWh/aktif W ölçümü, tam model güvenlik belgesi ve doğrudan duvar prizi kullanımını doğrulayın.`,{commercialAllowed:safeForAffiliate,productClass,searchTerm}),m);
    }

    if(input.existingCondition!=='sound'){
      return withMetrics(baseResult(input.existingCondition==='hot'||input.existingCondition==='damaged'?'stop_use':'evidence_required','Mevcut ölçerin fiziksel durumunu doğrulayın','Isınan, kararan, çatlayan veya gevşeyen enerji ölçeri kullanmayın. Sağlam, kuru ve olağandışı ısınmasız durum kanıtlanmalıdır.'),m);
    }
    const existingMaxA=num(input.existingMaxA);
    if(existingMaxA===null||existingMaxA<=0){
      return withMetrics(baseResult('evidence_required','Mevcut ölçerin azami akımını doğrulayın','Tam model teknik belgesindeki azami akım ve yük türü sınırını girin.'),m);
    }
    if(existingMaxA<deviceCurrent||deviceCurrent>existingMaxA*0.8){
      return withMetrics(baseResult('replace_candidate','Mevcut ölçerde yeterli akım payı yok',`Cihazın ${deviceCurrent} A azami akımına karşı mevcut ölçer ${existingMaxA} A etiketli. Uzun süreli kullanımda en az yüzde 20 akım payı bırakılmadan cihaz yeterli sayılmaz.`,{commercialAllowed:safeForAffiliate,productClass:'plug_energy_meter',searchTerm:meterSearch}),m);
    }
    if(input.existingEnergyKwh!=='yes'){
      return withMetrics(baseResult('evidence_required','Gerçek aktif enerji kWh ölçümünü doğrulayın','Yalnız akım, VA veya anlık watt gösterimi aylık enerji hesabının yerini tutmaz. Cihazın aktif enerji kWh biriktirdiğini teknik belgede doğrulayın.'),m);
    }
    if(input.existingCertificate!=='yes'||input.existingAccuracyClass!=='yes'){
      return withMetrics(baseResult('evidence_required','Güvenlik ve ölçüm belgesini doğrulayın','Tam model için izlenebilir güvenlik belgesi ile aktif enerji doğruluk sınıfını doğrulayın. IEC 62052-31:2024 güvenlik ve IEC 62053-21:2020 aktif enerji ölçüm sınıfları için referans çerçevedir.'),m);
    }
    if(input.temperatureTest==='no'){
      return withMetrics(baseResult('stop_use','Gözetimli sıcaklık testi başarısız','Fiş, priz veya ölçer belirgin ısındıysa kullanımı durdurun. Temas, priz ve ürün uygunluğu yetkili kişi tarafından kontrol edilmelidir.'),m);
    }
    if(input.temperatureTest!=='yes'){
      return withMetrics(baseResult('test_existing','Mevcut ölçeri gözetimli test edin','İlk kullanımda üretici talimatına göre gözetimli test yapın; fiş, priz ve ölçerde olağandışı sıcaklık, koku veya renk değişimi olmadığını doğrulamadan sürekli kullanmayın.'),m);
    }
    if(input.existingType==='smart_plug'&&highRiskRemote(input.useCase)){
      return withMetrics(baseResult('measurement_only','Mevcut akıllı prizi yalnız ölçüm için değerlendirin','Motor, kompresör ve ısıtıcı yüklerde uzaktan otomatik anahtarlama kapalı tutulmalı; cihaz üreticisinin açık izni yoksa röleli akıllı priz kullanımını ölçümle sınırlayın.'),m);
    }

    return withMetrics(baseResult('no_buy','Mevcut enerji ölçer yeterli; yeni ürün almayın',`Mevcut cihaz; akım payı, aktif kWh ölçümü, güvenlik/doğruluk belgesi, fiziksel durum ve gözetimli sıcaklık testiyle bu düşük güçlü fişli yük için yeterli görünüyor. Aylık yaklaşık ${m.monthlyKWh} kWh ve ${m.monthlyCost} TL sonucunu düzenli ölçümle karşılaştırın.`),m);
  }

  function affiliateUrl(result){
    if(!result||!result.commercialAllowed||!result.searchTerm)return null;
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(result.searchTerm)}&tag=${AFFILIATE_TAG}`;
  }

  function mount(doc){
    const form=doc.getElementById('energyForm');
    if(!form)return;
    const ids=['condition','environment','connection','useCase','goal','measurementBasis','activePowerW','hoursPerDay','daysPerMonth','dutyCyclePct','standbyW','standbyHoursPerDay','measuredKWh','measuredDays','tariff','deviceCurrentA','existingType','existingMaxA','existingEnergyKwh','existingCertificate','existingAccuracyClass','existingCondition','temperatureTest'];
    const el=Object.fromEntries(ids.map(id=>[id,doc.getElementById(id)]));
    const emergency=doc.getElementById('emergency');
    const resultBox=doc.getElementById('result');
    const status=doc.getElementById('status');
    const title=doc.getElementById('resultTitle');
    const summary=doc.getElementById('summary');
    const monthlyEnergy=doc.getElementById('monthlyEnergy');
    const monthlyCost=doc.getElementById('monthlyCost');
    const annualCost=doc.getElementById('annualCost');
    const standbyEnergy=doc.getElementById('standbyEnergy');
    const next=doc.getElementById('nextStep');
    const commerce=doc.getElementById('commerce');
    const affiliate=doc.getElementById('affiliate');
    const confirms=[...doc.querySelectorAll('.confirm')];
    const jsonButton=doc.getElementById('downloadJson');
    const icsButton=doc.getElementById('downloadIcs');
    const printButton=doc.getElementById('printResult');
    let latest=null;

    const values=()=>({emergency:emergency.checked,...Object.fromEntries(ids.map(id=>[id,el[id]?el[id].value:null]))});
    const download=(name,type,text)=>{
      const blob=new Blob([text],{type});
      const url=URL.createObjectURL(blob);
      const a=doc.createElement('a');a.href=url;a.download=name;doc.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
    };
    const updateGate=()=>{
      const url=affiliateUrl(latest);
      const open=Boolean(url)&&confirms.every(c=>c.checked);
      affiliate.setAttribute('aria-disabled',String(!open));
      affiliate.tabIndex=open?0:-1;
      if(open)affiliate.href=url;else affiliate.removeAttribute('href');
    };
    const nextLabel=(r)=>({
      emergency:'112 / güvenli alan',stop_use:'Kullanımı durdurun',professional:'Yetkili elektrikçi / enerji ölçümü',
      evidence_required:'Eksik teknik kanıtı tamamlayın',estimate_only:'kWh ile gerçek ölçüm yapın',
      measurement_only:'Uzaktan anahtarlamayı kapatın',test_existing:'Gözetimli sıcaklık testi',
      no_buy:'Mevcut çözümü kullanın',conditional_purchase:'Doğrulanmış ölçer sınıfı',
      replace_candidate:'Daha uygun ölçer sınıfı'
    })[r.status]||'Teknik doğrulama';

    form.addEventListener('submit',(event)=>{
      event.preventDefault();
      latest=calculate(values());
      resultBox.hidden=false;
      resultBox.dataset.status=latest.status;
      status.textContent=latest.status.replaceAll('_',' ').toLocaleUpperCase('tr-TR');
      title.textContent=latest.title;
      summary.textContent=latest.summary;
      monthlyEnergy.textContent=latest.monthlyKWh!==null?`${latest.monthlyKWh.toLocaleString('tr-TR')} kWh`:'—';
      monthlyCost.textContent=latest.monthlyCost!==null?`${latest.monthlyCost.toLocaleString('tr-TR')} TL`:'—';
      annualCost.textContent=latest.annualCost!==null?`${latest.annualCost.toLocaleString('tr-TR')} TL`:'—';
      standbyEnergy.textContent=latest.standbyKWh!==null?`${latest.standbyKWh.toLocaleString('tr-TR')} kWh/ay`:'—';
      next.textContent=nextLabel(latest);
      commerce.hidden=!latest.commercialAllowed;
      confirms.forEach(c=>{c.checked=false;});
      updateGate();
      resultBox.focus();
    });
    confirms.forEach(c=>c.addEventListener('change',updateGate));
    form.addEventListener('reset',()=>setTimeout(()=>{
      latest=null;resultBox.hidden=true;commerce.hidden=true;confirms.forEach(c=>{c.checked=false;});updateGate();
    },0));
    jsonButton.addEventListener('click',()=>{
      if(!latest)return;
      const payload={tool:'ALO186 Cihaz Elektrik Tüketimi ve Enerji Ölçer Uygunluk Testi',createdAt:new Date().toISOString(),personalData:false,result:latest,inputs:values(),disclaimer:'Ön hesaplamadır; faturadaki tarife, tam model kılavuzu ve gerçek kWh ölçümü önceliklidir.'};
      download('alo186-cihaz-enerji-olcum-fisi.json','application/json;charset=utf-8',JSON.stringify(payload,null,2));
    });
    icsButton.addEventListener('click',()=>{
      if(!latest)return;
      const date=new Date();date.setUTCDate(date.getUTCDate()+90);
      const end=new Date(date);end.setUTCDate(end.getUTCDate()+1);
      const stamp=(x)=>`${x.getUTCFullYear()}${String(x.getUTCMonth()+1).padStart(2,'0')}${String(x.getUTCDate()).padStart(2,'0')}`;
      const ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Enerji Olcer Kontrolu//TR','BEGIN:VEVENT',`DTSTART;VALUE=DATE:${stamp(date)}`,`DTEND;VALUE=DATE:${stamp(end)}`,'SUMMARY:Cihaz tüketimi ve enerji ölçer kontrolü','DESCRIPTION:Priz, fiş, ölçer sıcaklığı, cihaz akımı, kWh kaydı, tarife ve bekleme tüketimini yeniden doğrulayın.','END:VEVENT','END:VCALENDAR'].join('\r\n');
      download('alo186-enerji-olcer-90-gun-kontrol.ics','text/calendar;charset=utf-8',ics);
    });
    printButton.addEventListener('click',()=>root.print());
  }

  return {calculate,metrics,affiliateUrl,mount,constants:{AFFILIATE_TAG,NOMINAL_VOLTAGE,PLUG_AFFILIATE_MAX_A,ABSOLUTE_PLUG_MAX_A}};
});
