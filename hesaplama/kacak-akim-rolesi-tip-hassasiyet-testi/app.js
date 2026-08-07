(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.ALO186RcdDecision=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const OPTIONS=Object.freeze({
    hazard:['none','shock','smoke','exposed'],
    application:['unknown','general','electronic','single_inverter','three_drive','ev_mode3','pv_storage_ups'],
    supply:['unknown','single','three'],
    manufacturer:['unknown','none','A','F','B','A_F_RDC'],
    existingType:['unknown','none','AC','A','F','B'],
    residual:['unknown','30','100','300'],
    deviceForm:['unknown','rccb_shared','rcbo_dedicated','rccb_dedicated'],
    tripPattern:['none','start','random','moisture','after_upgrade','test_fails'],
    testButton:['unknown','works','fails'],
    circuits:['unknown','one','multiple'],
    recentWork:['unknown','no','yes'],
    ratingCoordination:['unknown','verified']
  });

  const KNOWN_FIELDS=['application','supply','manufacturer','existingType','residual','deviceForm','testButton','circuits','recentWork','ratingCoordination'];
  const TYPE_RANK={AC:0,A:1,F:2,B:3};

  function valid(field,value,fallback){return OPTIONS[field].includes(value)?value:fallback;}
  function normalize(raw){const source=raw||{};return{
    hazard:valid('hazard',source.hazard,'none'),application:valid('application',source.application,'unknown'),supply:valid('supply',source.supply,'unknown'),manufacturer:valid('manufacturer',source.manufacturer,'unknown'),existingType:valid('existingType',source.existingType,'unknown'),residual:valid('residual',source.residual,'unknown'),deviceForm:valid('deviceForm',source.deviceForm,'unknown'),tripPattern:valid('tripPattern',source.tripPattern,'none'),testButton:valid('testButton',source.testButton,'unknown'),circuits:valid('circuits',source.circuits,'unknown'),recentWork:valid('recentWork',source.recentWork,'unknown'),ratingCoordination:valid('ratingCoordination',source.ratingCoordination,'unknown')};}
  function dedupe(items){return[...new Set(items.filter(Boolean))];}
  function evidenceScore(a){let known=0;for(const field of KNOWN_FIELDS){const value=a[field];if(value!=='unknown'&&value!=='none')known+=1;}return Math.round(known/KNOWN_FIELDS.length*100);}
  function requiredType(a){
    if(['A','F','B','A_F_RDC'].includes(a.manufacturer))return a.manufacturer;
    if(a.application==='ev_mode3')return'A_F_RDC_OR_B';
    if(a.application==='three_drive'||a.application==='pv_storage_ups')return'B_REVIEW';
    if(a.application==='single_inverter')return'F_REVIEW';
    if(a.application==='electronic'||a.application==='general')return'A_REVIEW';
    return'UNKNOWN';
  }
  function typeMismatch(a,required){
    if(!['AC','A','F','B'].includes(a.existingType))return false;
    const target={A:1,F:2,B:3,A_REVIEW:1,F_REVIEW:2,B_REVIEW:3}[required];
    if(Number.isInteger(target))return TYPE_RANK[a.existingType]<target;
    if(required==='A_F_RDC')return!['A','F'].includes(a.existingType);
    if(required==='A_F_RDC_OR_B')return a.existingType!=='B';
    return false;
  }
  function classify(a,context){
    if(a.hazard!=='none')return{key:'emergency',label:'Acil güvenlik',css:'bad'};
    if(a.testButton==='fails'||a.tripPattern==='test_fails')return{key:'urgent',label:'Acil profesyonel test',css:'bad'};
    if(context.mismatch||a.tripPattern!=='none'||a.residual==='100'||a.residual==='300')return{key:'measure',label:'Ölçüm ve tip doğrulama',css:'warn'};
    if(context.score<60)return{key:'evidence',label:'Kanıt eksik',css:'warn'};
    return{key:'review',label:'Mevcut tasarımı doğrula',css:'ok'};
  }

  function buildDecision(raw){
    const a=normalize(raw);const score=evidenceScore(a);const required=requiredType(a);const mismatch=typeMismatch(a,required);const selection=[];const causes=[];const tests=[];const architecture=[];const warnings=[];

    if(a.hazard!=='none'){
      selection.push('Ürün veya tip seçimi durduruldu; önce enerjinin güvenli biçimde kesilmesi ve yetkili inceleme gerekir.');
      causes.push(a.hazard==='shock'?'Elektrik çarpması veya metal gövdede gerilim hissi gerçek kaçak, koruyucu iletken kopukluğu ya da bağlantı arızası göstergesi olabilir.':'Duman, kıvılcım, su veya fiziksel hasar can ve yangın riski oluşturabilir.');
    }else{
      if(required==='A')selection.push('Tam model üretici talimatı Tip A istiyor; bu şart diğer genel varsayımlardan daha güçlüdür.');
      else if(required==='F')selection.push('Tam model üretici talimatı Tip F istiyor; tek fazlı dönüştürücü kaynaklı bileşik frekanslar dikkate alınmalıdır.');
      else if(required==='B')selection.push('Tam model üretici talimatı Tip B istiyor; düzgün DC artık akım ve geniş frekans kapsamı doğrulanmalıdır.');
      else if(required==='A_F_RDC')selection.push('Üretici talimatındaki Tip A/F + 6 mA DC algılamalı RDC-DD kombinasyonu aynen doğrulanmalıdır.');
      else if(required==='A_F_RDC_OR_B')selection.push('Mode 3 EV şarj için Tip B veya EVSE üreticisinin açıkça doğruladığı Tip A/F + IEC 62955 kapsamındaki 6 mA RDC-DD çözümü değerlendirilmelidir.');
      else if(required==='B_REVIEW')selection.push('Trifaze sürücü, GES, depolama veya UPS topolojisinde düzgün DC artık akım ihtimali nedeniyle Tip B incelemesi gerekir; genel isimle değil tam cihaz kılavuzuyla karar verin.');
      else if(required==='F_REVIEW')selection.push('Tek fazlı inverterli yükte Tip F veya üreticinin açıkça izin verdiği Tip A değerlendirilebilir; her inverterli cihaz otomatik olarak Tip B gerektirmez.');
      else if(required==='A_REVIEW')selection.push('Elektronik yüklerin bulunduğu genel devrede Tip A başlangıç incelemesidir; yerel proje ve üretici şartı doğrulanmalıdır.');
      else selection.push('Yük topolojisi ve üretici talimatı bilinmeden Tip AC/A/F/B seçimi yapılmamalıdır.');

      if(mismatch)selection.push(`Mevcut Tip ${a.existingType}, seçilen yük/üretici şartının algılama kapsamının altında veya gerekli 6 mA DC kanıtından yoksun olabilir; ölçüm ve tam model dokümanıyla doğrulayın.`);
      if(a.application==='ev_mode3'&&required==='A_F_RDC_OR_B'&&a.existingType!=='B')selection.push('Mevcut Tip A/F tek başına yeterli kanıt değildir; EVSE içinde IEC 62955 kapsamındaki 6 mA RDC-DD açıkça doğrulanana kadar uygun kabul etmeyin.');
      if(a.existingType==='AC'&&(a.application==='electronic'||a.application==='single_inverter'))selection.push('Tip AC, elektronik doğrultucu ve inverterli yüklerde otomatik uygun kabul edilmemelidir.');
      if(a.residual==='30')selection.push('30 mA hassasiyet seçilmiş; istenmeyen açmayı azaltmak için değeri büyütmek yerine kök nedeni ölçün.');
      else if(a.residual==='100'||a.residual==='300')selection.push(`${a.residual} mA değer, gerekli olduğu yerlerde aşağı devredeki 30 mA ek korumanın yerine otomatik olarak geçmez; seçicilik ve koruma amacı projeyle doğrulanmalıdır.`);
      else selection.push('IΔn hassasiyeti okunmamış; 30/100/300 mA ile 40/63 A nominal akım değerlerini karıştırmayın.');
      if(a.ratingCoordination!=='verified')selection.push('RCD nominal akımı In, kutup sayısı, kısa devre dayanımı ve üst aşırı akım koruması ayrıca koordine edilmelidir.');
    }

    if(a.tripPattern==='start')causes.push('Cihaz başlangıcındaki EMC filtre akımı, dönüştürücü dalga biçimi, motor kalkışıyla eşzamanlı izolasyon zayıflığı veya yanlış RCD tipi.');
    if(a.tripPattern==='random')causes.push('Birden fazla yükün toplam koruyucu iletken akımı, aralıklı izolasyon arızası, ortak nötr veya nötr-PE bağlantısı.');
    if(a.tripPattern==='moisture')causes.push('Nem, yoğuşma, dış ortam kutusu, kablo eki veya cihaz içi izolasyon bozulması.');
    if(a.tripPattern==='after_upgrade')causes.push('Yeni elektronik yükün artık akım spektrumu, tadilat sonrası ortak nötr/nötr-PE hatası veya yanlış devre eşleşmesi.');
    if(a.tripPattern==='test_fails'||a.testButton==='fails')causes.push('Test düğmesinin açtırmaması cihazın iç test devresi, besleme/bağlantı veya mekanizma sorunu olabilir; gerçek test cihazıyla gecikmeden doğrulanmalıdır.');
    if(a.circuits==='multiple'||a.deviceForm==='rccb_shared')causes.push('Ortak RCD altında çok sayıda elektronik yükün normal PE akımları toplanarak istenmeyen açma eşiğine yaklaşabilir.');
    if(a.recentWork==='yes')causes.push('Yakın tarihli bağlantı değişikliğinde ortak nötr, yanlış nötr barası veya nötr-PE teması kontrol edilmelidir.');
    if(a.tripPattern==='none'&&!mismatch)causes.push('Belirgin istenmeyen açma örüntüsü seçilmedi; mevcut cihazın etiket ve test kayıtları yine de doğrulanmalıdır.');

    tests.push('Kaçak akım pensiyle devre ve yük bazında gerçek koruyucu iletken/artık akım trendini ölçün.');
    tests.push('RCD test cihazıyla açma akımı ve açma süresini, üretici ve proje kriterlerine göre kaydedin.');
    tests.push('Elektronik cihazları üretici prosedürüne göre ayırarak izolasyon direnci ve nötr-PE bağlantısını kontrol edin.');
    tests.push('Tam cihaz modelinin kullanım kılavuzunda RCD tipi, DC algılama ve özel seçicilik şartını doğrulayın.');
    if(a.application==='ev_mode3')tests.push('Wallbox içinde IEC 62955 kapsamındaki RDC-DD bulunup bulunmadığını ve 6 mA DC algılama davranışını tam model belgesinden doğrulayın.');
    if(a.application==='three_drive'||a.application==='pv_storage_ups')tests.push('Sürücü/inverter topolojisi, DC ara devre ve üreticinin düzgün DC artık akım uyarısını kontrol edin.');
    if(a.supply==='three')tests.push('Trifaze devrede faz/nötr kutup düzeni, tüm aktif iletkenlerin birlikte açılması ve üst-alt koruma koordinasyonunu kontrol edin.');

    if(a.deviceForm==='rccb_shared'||a.circuits==='multiple')architecture.push('Devre bazlı RCBO veya seçici kademelendirme, tek arızanın bütün alanı enerjisiz bırakmasını azaltabilir; gerçek kaçak dağılımı ölçülmeden parça değişimi yapılmamalıdır.');
    if(a.deviceForm==='rcbo_dedicated'||a.circuits==='one')architecture.push('Devre bazlı koruma mevcut görünüyor; yine de tip, IΔn, In ve kısa devre koordinasyonu doğrulanmalıdır.');
    if(a.deviceForm==='unknown')architecture.push('Cihazın RCCB mi RCBO mu olduğu ve aşağısındaki devre sayısı pano etiketinden/tek hattan belirlenmelidir.');
    architecture.push('Yukarı ve aşağı RCD’ler arasında zaman/akım seçiciliği üretici tabloları ve proje ile doğrulanmalıdır.');
    architecture.push('RCCB aşırı akım koruması içermez; uygun sigorta/şalter koordinasyonu ayrı kontrol edilir.');

    warnings.push('Bu sonuç, enerjili pano çalışması veya cihaz değişimi talimatı değildir.');
    warnings.push('RCD, uygun topraklama, aşırı akım koruması, SPD, ark ve yangın algılama katmanlarının yerine geçmez.');
    const context={score,mismatch};const state=classify(a,context);
    const summary=state.key==='emergency'?'Can/yangın riski seçildiği için ürün ve ticari yönlendirme kapatıldı.':state.key==='urgent'?'RCD test davranışı başarısız; gecikmeden yetkili ölçüm gerekir.':state.key==='measure'?'Tip, hassasiyet veya açma örüntüsü ölçüm ve tam model doğrulaması gerektiriyor.':state.key==='evidence'?'Karar için kritik etiket ve üretici bilgileri eksik.':'Belirgin arıza sinyali yok; mevcut tasarımın kayıtla doğrulanması yeterli olabilir.';
    return{schema:'alo186.rcdDecision.v1',personalData:false,createdAt:new Date().toISOString(),answers:a,evidenceScore:score,requiredType:required,typeMismatch:mismatch,state,summary,selection:dedupe(selection),causes:dedupe(causes),tests:dedupe(tests),architecture:dedupe(architecture),warnings:dedupe(warnings),directAffiliateLinks:false,commercialCtasAllowed:state.key!=='emergency',noBuyOutcomePreserved:true,officialApproval:false};
  }

  function readForm(form){return Object.fromEntries(new FormData(form).entries());}
  function clear(target){while(target.firstChild)target.removeChild(target.firstChild);}
  function renderList(target,items){clear(target);for(const item of items){const li=document.createElement('li');li.textContent=item;target.appendChild(li);}}
  function download(name,text){const url=URL.createObjectURL(new Blob([text],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),500);}
  function init(){
    const form=document.getElementById('rcdForm');if(!form)return;const results=document.getElementById('results');const reset=document.getElementById('resetBtn');const downloadBtn=document.getElementById('downloadBtn');const printBtn=document.getElementById('printBtn');const commercial=document.querySelector('.commercial-panel');let receipt=null;
    form.addEventListener('submit',(event)=>{event.preventDefault();receipt=buildDecision(readForm(form));document.getElementById('evidenceScore').textContent=`${receipt.evidenceScore}/100`;const state=document.getElementById('resultState');state.textContent=receipt.state.label;state.className=`status ${receipt.state.css}`;document.getElementById('evidenceBar').style.width=`${receipt.evidenceScore}%`;document.getElementById('resultSummary').textContent=receipt.summary;renderList(document.getElementById('selection'),receipt.selection);renderList(document.getElementById('causes'),receipt.causes);renderList(document.getElementById('tests'),receipt.tests);renderList(document.getElementById('architecture'),receipt.architecture);const emergency=document.getElementById('emergencyPanel');emergency.classList.toggle('hidden',receipt.state.key!=='emergency');if(commercial)commercial.classList.toggle('hidden',!receipt.commercialCtasAllowed);document.getElementById('downloadBtn').disabled=!receipt.commercialCtasAllowed;document.getElementById('printBtn').disabled=!receipt.commercialCtasAllowed;document.getElementById('emergencyText').textContent=receipt.state.key==='emergency'?receipt.summary:'';results.classList.remove('hidden');results.focus();results.scrollIntoView({behavior:'smooth',block:'start'});});
    reset.addEventListener('click',()=>{form.reset();receipt=null;results.classList.add('hidden');if(commercial)commercial.classList.remove('hidden');downloadBtn.disabled=false;printBtn.disabled=false;document.getElementById('arac').scrollIntoView({behavior:'smooth',block:'start'});});
    downloadBtn.addEventListener('click',()=>{if(receipt&&receipt.commercialCtasAllowed)download('alo186-kacak-akim-rolesi-karar-fisi.json',JSON.stringify(receipt,null,2));});
    printBtn.addEventListener('click',()=>{if(!receipt||receipt.commercialCtasAllowed)window.print();});
  }
  if(typeof document!=='undefined'){if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();}
  return{OPTIONS,normalize,evidenceScore,requiredType,typeMismatch,classify,buildDecision};
});
