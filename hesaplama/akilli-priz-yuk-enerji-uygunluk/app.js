(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const AFFILIATE_TAG='alo186rehber-21';
  const SUPPLY_VOLTAGE=230;
  const LOAD_MARGIN=1.25;
  const LOW_RISK_CASES=['lighting','router','charger','tv','computer','small_appliance'];
  const HIGH_RISK_CASES=['heater','kettle','fridge','ac_motor','medical','ev','fixed'];

  const num=(value)=>{
    if(value===null||value===undefined||value==='')return null;
    const parsed=Number(String(value).replace(',','.'));
    return Number.isFinite(parsed)?parsed:null;
  };
  const roundUp=(value,step)=>Math.ceil(value/step)*step;
  const baseResult=(status,title,summary,extra={})=>({
    status,title,summary,commercialAllowed:false,searchTerm:null,searchUrl:null,
    loadW:null,loadA:null,requiredW:null,requiredA:null,monthlyKwh:null,productClass:null,...extra
  });

  function metrics(input){
    const loadW=Math.max(0,num(input.loadW)||0);
    const enteredA=Math.max(0,num(input.loadA)||0);
    const calculatedA=loadW>0?loadW/SUPPLY_VOLTAGE:0;
    const loadA=Math.max(enteredA,calculatedA);
    const hoursPerDay=num(input.hoursPerDay);
    const requiredW=loadW>0?roundUp(loadW*LOAD_MARGIN,50):null;
    const requiredA=loadA>0?Math.ceil(loadA*LOAD_MARGIN*10)/10:null;
    const monthlyKwh=loadW>0&&hoursPerDay&&hoursPerDay>0
      ?Math.round((loadW*hoursPerDay*30/1000)*10)/10
      :null;
    return {loadW,loadA,requiredW,requiredA,monthlyKwh,hoursPerDay};
  }
  const withMetrics=(result,m)=>({...result,...m});

  function calculate(input={}){
    if(input.emergency){
      return baseResult('emergency','Fişe ve prize dokunmayın','Yanık kokusu, erime, kıvılcım, kararma, yoğun ısı, gevşeklik veya elektrik çarpması riski varsa enerjili bölüme yaklaşmayın. Güvenli alana geçin; yangın, yaralanma veya yoğun dumanda 112’yi arayın. Bütün ticari yollar kapalıdır.');
    }
    if(input.activeProblem==='yes'){
      return baseResult('stop_use','Aktif arızayı ürünle gizlemeyin','Isınan, gevşek, kararmış veya kesinti yapan fiş-priz bağlantısında akıllı priz eklemek çözüm değildir. Kullanımı durdurun; sorun yalnız ev içindeyse yetkili elektrikçi, çevrede de gerilim/kesinti sorunu varsa 186 ve yetkili dağıtım şirketi kanalı kullanılmalıdır.');
    }
    if(input.activeProblem!=='no'){
      return baseResult('evidence_required','Aktif sorun durumunu belirtin','Önceden planlama ile devam eden fiş-priz veya şebeke arızası birbirinden ayrılmalıdır.');
    }
    if(HIGH_RISK_CASES.includes(input.useCase||'')){
      const messages={
        heater:'Isıtıcılar yüksek ve uzun süreli akım çeker; uzaktan enerjilendirme yangın riskini artırabilir.',
        kettle:'Su ısıtıcısı, kahve makinesi ve ütü gibi ısıtıcı yükler gözetimsiz uzaktan anahtarlamaya uygun değildir.',
        fridge:'Buzdolabı ve dondurucuda kompresör başlangıç akımı, yeniden başlatma gecikmesi ve üretici şartları gerekir.',
        ac_motor:'Klima, pompa ve motorlu yüklerde kontaktör, koruma, başlangıç akımı ve kontrol senaryosu profesyonel değerlendirilmelidir.',
        medical:'Medikal veya yaşam destek cihazı tüketici akıllı prizine bağlanmamalıdır.',
        ev:'Elektrikli araç ve yüksek güçlü şarj için akıllı priz değil, projelendirilmiş şarj ekipmanı ve koruma düzeni gerekir.',
        fixed:'Sabit tesisat veya pano kumandası yetkili elektrik mühendisi/elektrikçi tarafından tasarlanmalıdır.'
      };
      return baseResult('professional','Bu yük tüketici akıllı prizi için uygun değil',`${messages[input.useCase]} Affiliate yönlendirmesi kapalıdır.`);
    }
    if(!LOW_RISK_CASES.includes(input.useCase||'')){
      return baseResult('evidence_required','Bağlanacak yükü seçin','Aydınlatma, modem/ağ cihazı, şarj adaptörü, TV, bilgisayar veya düşük güçlü küçük cihaz seçeneklerinden birini seçin.');
    }
    if(input.connection==='extension'||input.connection==='stacked'){
      return baseResult('stop_use','Zincirleme bağlantı kullanmayın','Akıllı prizi uzatma kablosu, grup priz, çoklayıcı veya başka bir akıllı priz üzerinde kullanmak temas direnci, aşırı yük ve ısınma riskini artırır. Sağlam ve uygun topraklı duvar prizi doğrulanmadan ürün yolu açılmaz.');
    }
    if(input.connection!=='wall'){
      return baseResult('evidence_required','Bağlantı biçimini doğrulayın','Bu araç yalnız akıllı prizin doğrudan sağlam duvar prizine bağlandığı düşük riskli senaryolar içindir.');
    }
    if(input.grounded==='no'){
      return baseResult('stop_use','Gerekli topraklama yok','Topraklama gerektiren cihazı topraksız bağlantıda kullanmayın. Akıllı priz koruma iletkeni eksikliğini gidermez.');
    }
    if(!['yes','double'].includes(input.grounded||'')){
      return baseResult('evidence_required','Topraklama sınıfını doğrulayın','Cihazın koruma sınıfını ve duvar prizindeki toprak sürekliliğini doğrulayın.');
    }
    if(input.manufacturerPermission==='no'){
      return baseResult('no_buy','Üretici doğrudan duvar prizi istiyor','Cihaz kılavuzu akıllı priz, zamanlayıcı veya ara bağlantıya izin vermiyorsa yeni ürün almayın ve doğrudan üretici talimatını izleyin.');
    }
    if(input.manufacturerPermission!=='yes'){
      return baseResult('evidence_required','Cihaz üreticisinin kullanım koşulunu kontrol edin','Tam model kullanım kılavuzunda akıllı priz veya zamanlayıcı kullanımına engel bulunmadığını doğrulayın.');
    }
    if(input.loadEvidence==='guess'){
      return baseResult('evidence_required','Tahmini watt satın alma kanıtı değildir','Cihazın teknik etiketi veya güvenilir ölçümde görülen azami W/A değerini kullanın. İnternet yorumu ya da yaklaşık tahminle ürün seçmeyin.');
    }
    if(!['measured','label'].includes(input.loadEvidence||'')){
      return baseResult('evidence_required','Gerçek yük verisini doğrulayın','Cihaz teknik etiketi/üretici föyü veya güvenilir ölçümde görülen azami W/A değerini girin.');
    }

    const m=metrics(input);
    if(m.loadW<=0||m.loadW>4000){
      return withMetrics(baseResult(m.loadW>4000?'professional':'evidence_required',m.loadW>4000?'Bu güç seviyesi profesyonel değerlendirme gerektirir':'Cihaz watt değerini girin',m.loadW>4000?'Yüksek güçlü bağlantı, devre kapasitesi ve kumanda sistemi tüketici akıllı priziyle onaylanamaz.':'Etiket veya ölçümdeki azami gerçek watt değerini girin.'),m);
    }
    if(m.loadW>1500||m.loadA>6.5){
      return withMetrics(baseResult('professional','Yükü akıllı priz üzerinden anahtarlamayın',`Gerçek yük yaklaşık ${m.loadW} W / ${m.loadA.toFixed(2)} A. Uzun süreli yüksek akım, kontak ısınması ve üretici sınırları nedeniyle genel tüketici ürünü önerilmez; devre ve kumanda çözümünü profesyonel değerlendirin.`),m);
    }
    if(m.hoursPerDay===null||m.hoursPerDay<=0||m.hoursPerDay>24){
      return withMetrics(baseResult('evidence_required','Günlük çalışma süresini girin','30 günlük enerji görünürlüğü için cihazın yaklaşık günlük çalışma süresini 0,1–24 saat arasında belirtin.'),m);
    }
    if(!['remote','schedule','energy','both'].includes(input.purpose||'')){
      return withMetrics(baseResult('evidence_required','Asıl kullanım amacını seçin','Uzaktan kontrol, zamanlama, enerji ölçümü veya ikisini birlikte kullanma amacını belirtin.'),m);
    }
    if(!['yes','no'].includes(input.energyFeature||'')){
      return withMetrics(baseResult('evidence_required','Enerji ölçümü gereksinimini belirtin','Yalnız anahtarlama mı yoksa W/kWh ölçümü mü gerektiğini ayırın.'),m);
    }

    const needsEnergy=input.energyFeature==='yes'||['energy','both'].includes(input.purpose);
    const needsControl=['remote','schedule','both'].includes(input.purpose);
    const searchTerm=needsEnergy?'enerji ölçümlü 16A topraklı akıllı priz güvenlik belgeli':'16A topraklı akıllı priz zamanlayıcı güvenlik belgeli';
    const baseExtra={productClass:needsEnergy?'energy_monitoring_smart_plug':'smart_plug',searchTerm};

    if(input.existingType==='none'){
      return withMetrics(baseResult('conditional_purchase',needsEnergy?'Enerji ölçümlü düşük riskli sınıfı doğrulayın':'Düşük riskli akıllı priz sınıfını doğrulayın',`Yaklaşık ${m.loadW} W / ${m.loadA.toFixed(2)} A yük için en az ${m.requiredW} W ve ${m.requiredA.toFixed(1)} A sürekli kapasite payı görünür. Bu değer ürün onayı değildir; tam modelin sürekli yük, topraklama, belge, yazılım desteği ve üretici kullanım sınırını yeniden kontrol edin.`,{commercialAllowed:true,...baseExtra}),m);
    }
    if(['hot','damaged'].includes(input.existingCondition||'')){
      return withMetrics(baseResult('stop_use','Mevcut ürünü kullanmayı durdurun','Isınan, kararan, kokan, gevşek, kırık veya erime belirtisi bulunan akıllı priz/ölçer kullanılmaz. Fişi güvenle ayırmak mümkün değilse enerjili bölüme dokunmayın ve uzman desteği alın.'),m);
    }
    if(input.existingCondition!=='sound'){
      return withMetrics(baseResult('evidence_required','Mevcut ürünün fiziksel durumunu kontrol edin','Kasa, fiş pimleri, priz teması ve yük altında sıcaklık sağlam ve olağandışı kokusuz olmalıdır.'),m);
    }
    const existingA=num(input.existingA);
    const existingW=num(input.existingW);
    if(existingA===null||existingW===null||existingA<=0||existingW<=0){
      return withMetrics(baseResult('evidence_required','Mevcut ürünün hem A hem W sınırını doğrulayın','Tam model teknik föyündeki sürekli amper ve watt sınırlarını birlikte girin. Yalnız “16 A” pazarlama ifadesi yeterli değildir.'),m);
    }
    if(input.recallChecked==='recalled'){
      return withMetrics(baseResult('stop_use','Geri çağırılmış ürünü kullanmayın','Tam marka-model için geri çağırma veya kullanım durdurma duyurusu varsa ürünü enerjilendirmeyin; resmî üretici/ürün güvenliği sürecini izleyin. Affiliate yönlendirmesi kapalıdır.'),m);
    }
    if(input.recallChecked!=='yes'){
      return withMetrics(baseResult('evidence_required','Geri çağırma kontrolünü tamamlayın','Tam marka-model için üretici ve resmî ürün güvenliği duyurularını kontrol edin.'),m);
    }
    if(existingA<m.requiredA||existingW<m.requiredW){
      return withMetrics(baseResult('replace_candidate','Mevcut ürün kapasite payını karşılamıyor',`Mevcut ${existingW} W / ${existingA} A ürün, hesaplanan en az ${m.requiredW} W / ${m.requiredA.toFixed(1)} A planlama sınırının altında. Yükü azaltın veya yalnız doğrulanmış düşük riskli teknik sınıfı değerlendirin.`,{commercialAllowed:true,...baseExtra}),m);
    }
    if(input.certification!=='yes'){
      return withMetrics(baseResult('evidence_required','Tam model güvenlik belgesini doğrulayın','Üretici adı, model numarası, kullanım kılavuzu ve izlenebilir güvenlik/uygunluk belgesi doğrulanmadan mevcut ürünü yeterli saymayın.'),m);
    }
    if(input.softwareSupport==='no'){
      return withMetrics(baseResult('planned_replace','Desteği bitmiş IoT ürününü planlı değiştirin','Güvenlik güncellemesi veya üretici desteği sona ermiş bağlı cihaz, hesap ve ağ riski oluşturabilir. Elektriksel yük düşük riskli olsa bile bulut erişimini sınırlayın; acele satın alma yerine desteklenen ve belgeli bir sınıfı planlı değerlendirin.',{commercialAllowed:true,...baseExtra}),m);
    }
    if(input.softwareSupport!=='yes'){
      return withMetrics(baseResult('evidence_required','Yazılım desteğini doğrulayın','Üreticinin güvenlik güncellemesi, destek süresi, hesap güvenliği ve açık bildirim kanalını kontrol edin.'),m);
    }
    if(needsEnergy&&input.existingEnergy==='unknown'){
      return withMetrics(baseResult('evidence_required','Mevcut ürünün enerji ölçüm özelliğini doğrulayın','W ve kWh ölçümü gerektiğinde bu özelliğin tam modelde bulunduğunu ve yerel/bulut davranışını doğrulayın. Yanıt bilinmeden ürün açığı kabul edilmez.'),m);
    }
    if(needsEnergy&&input.existingEnergy==='no'){
      return withMetrics(baseResult('feature_gap','Gerçek ihtiyaç enerji ölçümü','Mevcut ürün elektriksel olarak yeterli olabilir ancak gerekli W/kWh ölçümünü sağlamıyor. Önce haricî güvenilir ölçer veya desteklenen enerji ölçümlü düşük riskli sınıfın gerçekten gerekli olduğunu doğrulayın.',{commercialAllowed:true,...baseExtra}),m);
    }
    if(needsControl&&input.existingControl==='unknown'){
      return withMetrics(baseResult('evidence_required','Mevcut ürünün kontrol özelliğini doğrulayın','Seçilen amaç için uzaktan anahtarlama veya yerel zamanlama desteğinin tam modelde bulunduğunu doğrulayın. Düz enerji ölçer veya yalnız aç-kapa yapan ürün amacı karşılamayabilir.'),m);
    }
    if(needsControl&&input.existingControl==='no'){
      return withMetrics(baseResult('feature_gap','Seçilen kontrol işlevi mevcut üründe yok','Mevcut ürün elektriksel olarak yeterli olsa da seçilen uzaktan kontrol veya zamanlama işlevini sağlamıyor. Önce bu işlevin gerçekten gerekli olduğunu doğrulayın; yalnız düşük riskli desteklenen sınıf değerlendirilebilir.',{commercialAllowed:true,...baseExtra}),m);
    }
    if(input.loadTest==='no'){
      return withMetrics(baseResult('stop_use','Gerçek yük testi başarısız','Isınma, koku, gevşeklik, kararma veya bağlantı kesilmesi görüldüyse mevcut ürünü kullanmayın. Sorun ürün, duvar prizi veya fiş temasından kaynaklanabilir; uzman değerlendirmesi gerekir.'),m);
    }
    if(input.loadTest!=='yes'){
      return withMetrics(baseResult('test_existing','Önce mevcut ürünü gözetimli test edin','Kapasite ve belgeler yeterli görünüyor. Yeni ürün almadan önce üretici prosedürüne göre 30 dakikalık gözetimli gerçek yük testi yapın; fiş-priz sıcaklığını, gevşekliği ve bağlantı kararlılığını kontrol edin.'),m);
    }
    return withMetrics(baseResult('no_buy','Mevcut ürün yeterli — yeni ürün almayın',`Mevcut ürün düşük riskli ${m.loadW} W / ${m.loadA.toFixed(2)} A yük için kapasite, fiziksel durum, topraklama, belge, destek, gerekli işlevler, geri çağırma ve gözetimli test eşiklerini karşılıyor. Yaklaşık 30 günlük tüketim ${m.monthlyKwh} kWh; değişiklik ancak yük, amaç veya destek durumu değişirse değerlendirilmelidir.`),m);
  }

  function statusLabel(status){
    const map={emergency:'Acil güvenlik',stop_use:'Kullanımı durdur',professional:'Profesyonel değerlendirme',evidence_required:'Kanıt gerekli',conditional_purchase:'Koşullu ürün yolu',replace_candidate:'Kapasite açığı',planned_replace:'Planlı değişim',feature_gap:'Özellik açığı',test_existing:'Önce test',no_buy:'Satın alma yok'};
    return map[status]||'Sonuç';
  }
  function nextStep(result){
    const map={emergency:'Güvenli alana geçin',stop_use:'Enerjiyi güvenle ayırın',professional:'Uzman değerlendirmesi',evidence_required:'Etiket ve belge kontrolü',conditional_purchase:'Teknik sınıf doğrulaması',replace_candidate:'Yük azalt / doğru sınıf',planned_replace:'Acele etmeden planla',feature_gap:'İhtiyacı yeniden doğrula',test_existing:'30 dakika gözetimli test',no_buy:'Mevcut ürünü koru'};
    return map[result.status]||'Kanıtları kontrol edin';
  }
  function buildSearchUrl(term){
    const q=encodeURIComponent(term);
    return `https://www.amazon.com.tr/s?k=${q}&tag=${AFFILIATE_TAG}`;
  }
  function download(filename,text,type){
    const blob=new Blob([text],{type});
    const url=URL.createObjectURL(blob);
    const a=document.createElement('a');
    a.href=url;a.download=filename;document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
  }
  function icsDate(date){return date.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}/,'');}

  function mount(doc){
    const form=doc.getElementById('smartForm');
    if(!form)return;
    const resultBox=doc.getElementById('result');
    const commerce=doc.getElementById('commerce');
    const affiliate=doc.getElementById('affiliate');
    let lastResult=null;

    const read=()=>{
      const ids=['activeProblem','useCase','connection','grounded','loadEvidence','loadW','loadA','hoursPerDay','purpose','manufacturerPermission','existingType','existingCondition','existingA','existingW','certification','softwareSupport','recallChecked','loadTest','energyFeature','existingEnergy','existingControl'];
      const data={emergency:doc.getElementById('emergency').checked};
      ids.forEach(id=>{data[id]=doc.getElementById(id).value;});
      return data;
    };
    const render=(r)=>{
      lastResult=r;
      doc.getElementById('status').textContent=statusLabel(r.status);
      doc.getElementById('resultTitle').textContent=r.title;
      doc.getElementById('summary').textContent=r.summary;
      doc.getElementById('loadMetric').textContent=r.loadW?`${r.loadW} W · ${r.loadA.toFixed(2)} A`:'—';
      doc.getElementById('classMetric').textContent=r.requiredW?`${r.requiredW} W · ${r.requiredA.toFixed(1)} A`:'—';
      doc.getElementById('energyMetric').textContent=r.monthlyKwh!==null?`${r.monthlyKwh} kWh`:'—';
      doc.getElementById('nextMetric').textContent=nextStep(r);
      resultBox.hidden=false;
      commerce.hidden=!r.commercialAllowed;
      affiliate.removeAttribute('href');affiliate.setAttribute('aria-disabled','true');affiliate.setAttribute('tabindex','-1');
      doc.querySelectorAll('.confirm').forEach(box=>{box.checked=false;});
      if(r.commercialAllowed&&r.searchTerm)r.searchUrl=buildSearchUrl(r.searchTerm);
      resultBox.focus();
    };
    form.addEventListener('submit',(event)=>{event.preventDefault();render(calculate(read()));});
    form.addEventListener('reset',()=>{setTimeout(()=>{resultBox.hidden=true;commerce.hidden=true;lastResult=null;},0);});
    doc.querySelectorAll('.confirm').forEach(box=>box.addEventListener('change',()=>{
      const ok=[...doc.querySelectorAll('.confirm')].every(item=>item.checked);
      if(ok&&lastResult&&lastResult.searchUrl){affiliate.href=lastResult.searchUrl;affiliate.removeAttribute('aria-disabled');affiliate.setAttribute('tabindex','0');}
      else{affiliate.removeAttribute('href');affiliate.setAttribute('aria-disabled','true');affiliate.setAttribute('tabindex','-1');}
    }));
    doc.getElementById('downloadJson').addEventListener('click',()=>{
      if(!lastResult)return;
      const payload={generatedAt:new Date().toISOString(),platform:'ALO186 bağımsız bilgi platformu',result:lastResult,notice:'Fiyat, stok, puan, satıcı, teslimat ve garanti verisi içermez.'};
      download('alo186-akilli-priz-teknik-fis.json',JSON.stringify(payload,null,2),'application/json');
    });
    doc.getElementById('downloadIcs').addEventListener('click',()=>{
      if(!lastResult)return;
      const start=new Date();start.setDate(start.getDate()+30);start.setHours(10,0,0,0);
      const end=new Date(start.getTime()+30*60*1000);
      const body=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Akilli Priz Kontrolu//TR','BEGIN:VEVENT',`UID:alo186-smart-plug-${Date.now()}@alo186.com`,`DTSTAMP:${icsDate(new Date())}`,`DTSTART:${icsDate(start)}`,`DTEND:${icsDate(end)}`,'SUMMARY:Akıllı priz güvenlik ve enerji yeniden ölçümü','DESCRIPTION:Fiş-priz ısınması, gevşeklik, tam model geri çağırma, yazılım desteği, gerçek W ve 30 günlük kWh değerini yeniden kontrol edin. Fiyat veya kampanya takibi değildir.','END:VEVENT','END:VCALENDAR'].join('\r\n');
      download('alo186-akilli-priz-30-gun-kontrol.ics',body,'text/calendar');
    });
    doc.getElementById('printResult').addEventListener('click',()=>window.print());
  }

  return {calculate,metrics,mount,buildSearchUrl};
});
