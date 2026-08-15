(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const AFFILIATE_TAG='alo186rehber-21';
  const OUTPUT_MARGIN=1.25;
  const PLANNING_POWER_FACTOR=0.80;
  const ENERGY_EFFICIENCY=0.85;
  const USABLE_ENERGY_FRACTION=0.80;
  const AGING_RESERVE=0.85;

  const num=(value)=>{
    if(value===null||value===undefined||value==='')return null;
    const parsed=Number(String(value).replace(',','.'));
    return Number.isFinite(parsed)?parsed:null;
  };
  const roundUp=(value,step)=>Math.ceil(value/step)*step;
  const baseResult=(status,title,summary,extra={})=>({
    status,title,summary,commercialAllowed:false,searchUrl:null,
    totalLoadW:null,requiredContinuousW:null,requiredPeakW:null,
    requiredVA:null,requiredNominalWh:null,targetMinutes:null,...extra
  });

  function metrics(input){
    const values=['computerW','monitorW','networkW','nasW','otherW'].map(key=>Math.max(0,num(input[key])||0));
    const totalLoadW=values.reduce((sum,value)=>sum+value,0);
    const targetMinutes=num(input.targetMinutes);
    const enteredPeakW=num(input.peakW);
    const peakFactor=input.useCase==='gaming_pc'?1.35:input.useCase==='small_server'?1.25:1.20;
    const planningPeak=Math.max(totalLoadW,enteredPeakW&&enteredPeakW>0?enteredPeakW:totalLoadW*peakFactor);
    const requiredContinuousW=roundUp(totalLoadW*OUTPUT_MARGIN,50);
    const requiredPeakW=roundUp(planningPeak*1.10,50);
    const requiredVA=roundUp(requiredContinuousW/PLANNING_POWER_FACTOR,50);
    const requiredNominalWh=targetMinutes&&targetMinutes>0
      ?roundUp((totalLoadW*(targetMinutes/60))/(ENERGY_EFFICIENCY*USABLE_ENERGY_FRACTION*AGING_RESERVE),50)
      :null;
    return {totalLoadW,targetMinutes,requiredContinuousW,requiredPeakW,requiredVA,requiredNominalWh};
  }

  function withMetrics(result,m){return {...result,...m};}

  function calculate(input={}){
    if(input.emergency){
      return baseResult('emergency','UPS ve aküye yaklaşmayın','Duman, kıvılcım, tıslama, şişme, erime, keskin koku veya elektrik çarpması riski varsa fişe ya da UPS’e dokunmayın. Güvenli alana çıkın; yangın, yaralanma veya yoğun dumanda 112’yi arayın. Bütün ticari yollar kapalıdır.');
    }
    if(['swollen','hot','leaking','damaged'].includes(input.upsCondition||'')){
      return baseResult('stop_use','UPS’i kullanmayı durdurun','Şişmiş, aşırı ısınan, sızdıran, darbe almış veya erime belirtisi bulunan UPS/akü kullanılmaz ve şarj edilmez. Üretici veya yetkili teknik servis değerlendirmesi gerekir.');
    }
    if(input.upsCondition!=='sound'){
      return baseResult('evidence_required','UPS ve akünün fiziksel durumunu doğrulayın','Kasa, fiş, kablo, priz ve akü bölümünün sağlam, kuru, serin ve olağandışı kokusuz olduğunu doğrulamadan seçim yapmayın.');
    }
    if(input.installation==='wet'){
      return baseResult('stop_use','Islak veya su riski bulunan yerde kullanmayın','UPS kuru, üretici sıcaklık ve havalandırma sınırlarına uygun bir yerde kullanılmalıdır. Su teması veya yoğuşma riski varken cihazı enerjilendirmeyin.');
    }
    if(input.installation==='blocked'){
      return baseResult('stop_use','Havalandırmayı kapatmayın','Kapalı dolap, halı üzeri, ısı kaynağı yakını veya hava girişleri kapalı kullanım; aşırı ısınma ve akü ömrü riski oluşturur. Yerleşimi düzeltmeden ürün seçmeyin.');
    }
    if(input.installation!=='dry'){
      return baseResult('evidence_required','Kurulum yerini doğrulayın','Kuru, serin, çocuklardan uzak ve hava girişleri açık bir yer doğrulanmalıdır.');
    }
    if(['medical','industrial'].includes(input.useCase||'')){
      return baseResult('professional','Bu yük profesyonel süreklilik tasarımı gerektirir','Yaşam destek/medikal yükler ile endüstriyel prosesler, tek bir tüketici UPS hesaplayıcısıyla onaylanamaz. Risk analizi, üretici şartları, seçicilik, bypass, alarm ve bakım planı gerekir; affiliate yönlendirmesi kapalıdır.');
    }
    if(input.hardwired==='yes'){
      return baseResult('professional','Sabit bağlantılı UPS profesyonel projedir','Pano bağlantısı, sabit tesisat, harici akü kabini, bypass veya jeneratör entegrasyonu yetkili elektrik mühendisi/teknik servis tarafından projelendirilmelidir.');
    }
    if(input.hardwired!=='no'){
      return baseResult('evidence_required','Bağlantı biçimini doğrulayın','Bu araç yalnız fişli, tek fazlı, kullanıcı erişimli düşük güçlü UPS ön seçimi içindir.');
    }
    if(!['home_office','gaming_pc','nas_cctv','small_server'].includes(input.useCase||'')){
      return baseResult('evidence_required','Kullanım senaryosunu seçin','Ev/ofis bilgisayarı, gaming PC, NAS-kamera veya küçük sunucu senaryolarından birini seçin.');
    }
    if(input.loadEvidence==='psu_rating'){
      return baseResult('evidence_required','PSU watt etiketi gerçek tüketim değildir','Örneğin 850 W bilgisayar güç kaynağı, bilgisayarın sürekli 850 W çektiği anlamına gelmez. Priz tipi enerji ölçer, UPS yazılımı veya cihaz teknik verisiyle gerçek azami giriş wattını belirleyin.');
    }
    if(!['measured','technical_max'].includes(input.loadEvidence||'')){
      return baseResult('evidence_required','Yük watt değerini kanıtlayın','Toplamı priz tipi enerji ölçer/UPS yazılımı ile ölçün veya cihazların gerçek azami giriş wattlarını teknik belgelerden toplayın.');
    }

    const m=metrics(input);
    if(m.totalLoadW<=0||m.totalLoadW>3000){
      return withMetrics(baseResult(m.totalLoadW>3000?'professional':'evidence_required',m.totalLoadW>3000?'3 kW üzeri yük profesyonel UPS projesidir':'Bağlanacak yükleri watt olarak girin',m.totalLoadW>3000?'Yük paylaşımı, priz-devre kapasitesi, bypass, akü kabini ve ısı yönetimi profesyonel tasarım gerektirir.':'Bilgisayar, monitör, modem/ONT, NAS-kamera ve diğer eşzamanlı yüklerin gerçek azami wattlarını girin.'),m);
    }
    if(m.targetMinutes===null||m.targetMinutes<5||m.targetMinutes>480){
      return withMetrics(baseResult('evidence_required','Hedef süreyi 5–480 dakika arasında girin','UPS’in amacı güvenli kapatma mı, kısa kesinti köprüsü mü, yoksa daha uzun süre mi; hedef süreyi açıkça belirleyin.'),m);
    }
    if(input.activeOutage==='yes'){
      return withMetrics(baseResult('active_outage','Aktif kesintide güvenli kapatma önceliklidir','Yeni ürün teslimatı mevcut kesintiyi çözmez. Bilgisayarda çalışmayı kaydedin, kritik olmayan yükleri kapatın ve mevcut UPS alarm/çalışma süresine göre güvenli kapatma yapın. Hesaplanan değerler sonraki hazırlık içindir.'),m);
    }
    if(input.activeOutage!=='no'){
      return withMetrics(baseResult('evidence_required','Aktif kesinti durumunu belirtin','Önceden planlama ile devam eden elektrik kesintisi birbirinden ayrılmalıdır.'),m);
    }

    const needsPureSine=input.activePfc==='yes'||['gaming_pc','nas_cctv','small_server'].includes(input.useCase);
    const className=input.useCase==='small_server'?'online UPS':needsPureSine?'saf sinüs line-interactive UPS':'line-interactive UPS';
    const searchTerm=`${m.requiredVA}VA ${m.requiredContinuousW}W ${needsPureSine?'saf sinüs ':''}${className} bilgisayar NAS UPS`;
    if(input.existingType==='none'){
      return withMetrics(baseResult('conditional_purchase',`${m.requiredVA} VA / ${m.requiredContinuousW} W sınıfını doğrulayın`,`Toplam ${m.totalLoadW} W yük için en az ${m.requiredContinuousW} W sürekli çıkış, ${m.requiredPeakW} W planlama tepe gücü ve ${m.targetMinutes} dakika hedefte yaklaşık ${m.requiredNominalWh} Wh nominal enerji görünür. Nihai süre için üreticinin tam model yük–süre eğrisini kontrol edin.`,{commercialAllowed:true,productClass:input.useCase==='small_server'?'online_ups':needsPureSine?'pure_sine_line_interactive':'line_interactive',searchTerm}),m);
    }

    const existingVA=num(input.existingVA);
    const existingW=num(input.existingW);
    const observedRuntime=num(input.observedRuntimeMinutes);
    const manufacturerRuntime=num(input.manufacturerRuntimeMinutes);
    const batteryAge=num(input.batteryAgeYears);

    if(existingVA===null||existingW===null||existingVA<=0||existingW<=0){
      return withMetrics(baseResult('evidence_required','Mevcut UPS’in hem VA hem W sınırını doğrulayın','Sadece VA etiketi yeterli değildir. Üretici teknik föyündeki azami çıkış wattı ve VA değeri birlikte girilmelidir.'),m);
    }
    if(existingW<m.requiredContinuousW||existingVA<m.requiredVA){
      return withMetrics(baseResult('replace_candidate','Mevcut UPS güç sınırının altında',`Mevcut ${existingVA} VA / ${existingW} W kaynak; hesaplanan ${m.requiredVA} VA / ${m.requiredContinuousW} W alt sınırını karşılamıyor. Daha büyük sınıfı değerlendirirken üretici yük–süre eğrisini ve priz sayısını doğrulayın.`,{commercialAllowed:true,productClass:needsPureSine?'pure_sine_ups':'ups',searchTerm}),m);
    }
    if(needsPureSine&&input.pureSine!=='yes'){
      return withMetrics(baseResult(input.pureSine==='no'?'replace_candidate':'evidence_required','Saf sinüs çıkışı doğrulayın','Aktif PFC bilgisayar güç kaynakları, gaming PC, NAS ve küçük sunucu yüklerinde üretici tarafından doğrulanmış saf sinüs çıkış tercih edilmelidir. “Simüle edilmiş” veya belirsiz dalga biçimini eşdeğer saymayın.',{commercialAllowed:input.pureSine==='no',productClass:'pure_sine_ups',searchTerm}),m);
    }
    if(input.certification!=='yes'){
      return withMetrics(baseResult('evidence_required','UPS güvenlik ve performans belgesini doğrulayın','Tam üretici-model, kullanım kılavuzu, garanti/servis ve IEC 62040-1 güvenlik ile IEC 62040-3 performans beyanı veya eşdeğer izlenebilir belge aranmalıdır.'),m);
    }
    if(input.existingType==='power_station'&&input.upsModeCertified!=='yes'){
      return withMetrics(baseResult('evidence_required','Power station UPS değildir; EPS/UPS modunu doğrulayın','Transfer süresi, çıkış sürekliliği ve bilgisayar uyumluluğu tam model teknik belgesinde açıkça verilmedikçe power station kesintisiz güç kaynağı kabul edilmez.'),m);
    }
    if(input.transferTest==='no'){
      return withMetrics(baseResult('replace_candidate','Şebeke geçiş testi başarısız','Bilgisayar yeniden başladı, UPS aşırı yüke geçti veya çıkış kesildi. Mevcut cihazı yeterli saymayın; önce yükü azaltın ve üretici desteği alın.',{commercialAllowed:true,productClass:needsPureSine?'pure_sine_ups':'ups',searchTerm}),m);
    }
    if(input.transferTest!=='yes'){
      return withMetrics(baseResult('test_existing','Gözetimli şebeke geçiş testi yapın','Teknik kapasite yeterli görünüyor. Çalışma kaydedilmişken, üretici prosedürüne göre gözetimli test yapmadan yeni ürün almayın veya mevcut UPS’i yeterli saymayın.'),m);
    }
    if(input.batterySelfTest==='no'){
      return withMetrics(baseResult('battery_service','UPS aküsünü servis/test sürecine alın','Akü öz testi başarısızsa tüm UPS’i hemen değiştirmek yerine tam modele uygun akü değişim uygunluğunu, üretici servisini ve atık akü sürecini değerlendirin. Bu araç affiliate bağlantısı açmaz.'),m);
    }
    if(input.batterySelfTest!=='yes'){
      return withMetrics(baseResult('test_existing','Akü öz testini ve alarm geçmişini doğrulayın','Üretici yazılımındaki akü öz testi, alarm ve değişim uyarıları tamamlanmadan çalışma süresine güvenmeyin.'),m);
    }
    if(batteryAge!==null&&batteryAge>=4){
      return withMetrics(baseResult('battery_service','Akü yaşını ve gerçek kapasiteyi ölçün','Dört yıl ve üzeri yaş tek başına arıza kanıtı değildir; ancak sıcaklık ve kullanım geçmişiyle birlikte kapasite kaybı riski yükselir. Gözetimli süre testi veya üretici servisi olmadan yeni UPS satın almayın.'),m);
    }

    const provenRuntime=observedRuntime&&observedRuntime>0?observedRuntime:manufacturerRuntime&&manufacturerRuntime>0?manufacturerRuntime:null;
    if(provenRuntime===null){
      return withMetrics(baseResult('test_existing','Tam yükte çalışma süresini kanıtlayın','Üreticinin bu tam model ve yaklaşık yük için yük–süre eğrisini veya gözetimli gerçek süre testini doğrulayın. Wh hesabı yalnız ön planlamadır.'),m);
    }
    if(provenRuntime<m.targetMinutes){
      return withMetrics(baseResult('replace_candidate','Mevcut çalışma süresi hedefin altında',`Kanıtlanan yaklaşık ${provenRuntime} dakika, ${m.targetMinutes} dakikalık hedefi karşılamıyor. Harici akü yalnız üreticinin bu model için açıkça desteklediği durumda kullanılır; rastgele akü eklemeyin.`,{commercialAllowed:true,productClass:needsPureSine?'long_runtime_pure_sine_ups':'long_runtime_ups',searchTerm}),m);
    }

    return withMetrics(baseResult('no_buy','Mevcut UPS yeterli; yeni ürün almayın',`Mevcut ${existingVA} VA / ${existingW} W UPS; güç, dalga biçimi, belge, akü öz testi, geçiş testi ve yaklaşık ${provenRuntime} dakikalık süreyle hedefi karşılıyor. Üretici bakım planını izleyin ve kritik dosyalar için otomatik güvenli kapatmayı etkinleştirin.`),m);
  }

  function affiliateUrl(result){
    if(!result||!result.commercialAllowed||!result.searchTerm)return null;
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(result.searchTerm)}&tag=${AFFILIATE_TAG}`;
  }

  function mount(doc){
    const form=doc.getElementById('upsForm');
    if(!form)return;
    const ids=['upsCondition','installation','useCase','hardwired','loadEvidence','computerW','monitorW','networkW','nasW','otherW','peakW','targetMinutes','activePfc','activeOutage','existingType','existingVA','existingW','pureSine','certification','upsModeCertified','transferTest','batterySelfTest','batteryAgeYears','manufacturerRuntimeMinutes','observedRuntimeMinutes'];
    const el=Object.fromEntries(ids.map(id=>[id,doc.getElementById(id)]));
    const emergency=doc.getElementById('emergency');
    const resultBox=doc.getElementById('result');
    const status=doc.getElementById('status');
    const title=doc.getElementById('resultTitle');
    const summary=doc.getElementById('summary');
    const totalLoad=doc.getElementById('totalLoad');
    const powerClass=doc.getElementById('powerClass');
    const runtimeNeed=doc.getElementById('runtimeNeed');
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
      emergency:'112 / güvenli alan',stop_use:'Kullanımı durdurun',professional:'UPS uzmanı / elektrik mühendisi',
      evidence_required:'Eksik teknik kanıtı tamamlayın',active_outage:'Güvenli kapatma',
      test_existing:'Mevcut UPS’i gözetimli test edin',battery_service:'Akü testi / üretici servisi',
      no_buy:'Mevcut UPS’i kullanın',conditional_purchase:'Doğrulanmış UPS sınıfı',
      replace_candidate:'Daha uygun UPS sınıfı'
    })[r.status]||'Teknik doğrulama';

    form.addEventListener('submit',(event)=>{
      event.preventDefault();
      latest=calculate(values());
      resultBox.hidden=false;
      resultBox.dataset.status=latest.status;
      status.textContent=latest.status.replaceAll('_',' ').toLocaleUpperCase('tr-TR');
      title.textContent=latest.title;
      summary.textContent=latest.summary;
      totalLoad.textContent=latest.totalLoadW?`${latest.totalLoadW.toLocaleString('tr-TR')} W`:'—';
      powerClass.textContent=latest.requiredVA&&latest.requiredContinuousW?`${latest.requiredVA.toLocaleString('tr-TR')} VA / ${latest.requiredContinuousW.toLocaleString('tr-TR')} W`:'—';
      runtimeNeed.textContent=latest.requiredNominalWh?`${latest.targetMinutes.toLocaleString('tr-TR')} dk · ≈ ${latest.requiredNominalWh.toLocaleString('tr-TR')} Wh`:'—';
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
      const payload={tool:'ALO186 Bilgisayar Gaming PC ve NAS UPS Uygunluk Testi',createdAt:new Date().toISOString(),personalData:false,result:latest,inputs:values(),disclaimer:'Ön seçimdir; üreticinin tam model yük-süre eğrisi ve güvenlik talimatı önceliklidir.'};
      download('alo186-bilgisayar-ups-teknik-fis.json','application/json;charset=utf-8',JSON.stringify(payload,null,2));
    });
    icsButton.addEventListener('click',()=>{
      if(!latest)return;
      const date=new Date();date.setUTCDate(date.getUTCDate()+90);
      const end=new Date(date);end.setUTCDate(end.getUTCDate()+1);
      const stamp=(x)=>`${x.getUTCFullYear()}${String(x.getUTCMonth()+1).padStart(2,'0')}${String(x.getUTCDate()).padStart(2,'0')}`;
      const ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//UPS Kontrolu//TR','BEGIN:VEVENT',`DTSTART;VALUE=DATE:${stamp(date)}`,`DTEND;VALUE=DATE:${stamp(end)}`,'SUMMARY:UPS akü, alarm ve geçiş testi','DESCRIPTION:UPS fiziksel durumu, akü öz testi, alarm geçmişi, bağlı yük, güvenli kapatma yazılımı ve gözetimli şebeke geçişini yeniden doğrulayın.','END:VEVENT','END:VCALENDAR'].join('\r\n');
      download('alo186-ups-90-gun-kontrol.ics','text/calendar;charset=utf-8',ics);
    });
    printButton.addEventListener('click',()=>root.print());
  }

  return {calculate,metrics,affiliateUrl,mount,constants:{AFFILIATE_TAG,OUTPUT_MARGIN,PLANNING_POWER_FACTOR,ENERGY_EFFICIENCY,USABLE_ENERGY_FRACTION,AGING_RESERVE}};
});
