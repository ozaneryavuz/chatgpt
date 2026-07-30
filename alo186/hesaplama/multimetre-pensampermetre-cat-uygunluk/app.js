(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const AFFILIATE_TAG='alo186rehber-21';
  const CURRENT_MARGIN=1.25;
  const CATEGORY_RANK={none:0,cat2:2,cat3:3,cat4:4};
  const num=(value)=>{
    if(value===null||value===undefined||value==='')return null;
    const parsed=Number(String(value).replace(',','.'));
    return Number.isFinite(parsed)?parsed:null;
  };
  const roundUp=(value,step)=>Math.ceil(value/step)*step;
  const baseResult=(status,title,summary,extra={})=>({
    status,title,summary,commercialAllowed:false,searchTerm:null,
    requiredCategory:null,requiredVoltage:null,requiredCurrent:null,
    productClass:null,trueRmsRequired:false,inrushRequired:false,...extra
  });

  function requirements(input={}){
    const location=input.location||'unknown';
    const task=input.task||'unknown';
    const systemVoltage=num(input.systemVoltage);
    const expectedCurrent=num(input.expectedCurrent);
    const map={
      electronics:{category:'cat2',voltage:300,label:'CAT II 300 V'},
      battery:{category:'cat2',voltage:300,label:'CAT II 300 V'},
      appliance:{category:'cat2',voltage:600,label:'CAT II 600 V'},
      socket:{category:'cat2',voltage:600,label:'CAT II 600 V'},
      panel:{category:'cat3',voltage:600,label:'CAT III 600 V'},
      service:{category:'cat4',voltage:600,label:'CAT IV 600 V'}
    };
    const base=map[location]||null;
    if(!base)return null;
    const currentTask=['current_ac','current_dc','inrush'].includes(task);
    const productClass=currentTask?'clamp_meter':'digital_multimeter';
    const requiredCurrent=currentTask&&expectedCurrent&&expectedCurrent>0?roundUp(expectedCurrent*CURRENT_MARGIN,10):null;
    const voltageFromSystem=systemVoltage&&systemVoltage>0?roundUp(systemVoltage*1.25,50):0;
    const requiredVoltage=Math.max(base.voltage,voltageFromSystem);
    const trueRmsRequired=['voltage_ac','current_ac','inrush'].includes(task)&&['socket','panel','service','appliance'].includes(location);
    return {
      requiredCategory:base.category,
      requiredCategoryLabel:base.label,
      requiredVoltage,
      requiredCurrent,
      productClass,
      trueRmsRequired,
      inrushRequired:task==='inrush',
      acDcClampRequired:task==='current_dc'
    };
  }

  function withReq(result,req){return req?{...result,...req}:result;}

  function calculate(input={}){
    if(input.emergency){
      return baseResult('emergency','Ölçümü durdurun ve güvenli alana geçin','Kıvılcım, elektrik çarpması, ark, duman, erime, yanık kokusu veya açıkta enerjili iletken varsa cihaza ve ölçü aletine dokunmayın. Yaralanma, yangın veya yoğun dumanda 112 önceliklidir; ticari yollar kapalıdır.');
    }
    if(['damaged','burned','wet'].includes(input.meterCondition||'')||['damaged','exposed'].includes(input.leadCondition||'')){
      return baseResult('stop_use','Ölçü aletini ve probları kullanmayın','Çatlak kasa, erime, gevşek terminal, açığa çıkmış prob iletkeni, ıslaklık veya yanık izi bulunan ekipman enerjili devrede kullanılmaz. Üretici servisi veya güvenli bertaraf gerekir.');
    }
    if(input.meterCondition!=='sound'||input.leadCondition!=='sound'){
      return baseResult('evidence_required','Cihaz ve prob durumunu doğrulayın','Kasa, ekran, giriş terminalleri, sigortalar, prob uçları ve kablolar sağlam ve kuru olmadan seçim yapmayın.');
    }
    if(!['consumer','trained','qualified'].includes(input.competence||'')){
      return baseResult('evidence_required','Kullanıcı yetkinliğini belirtin','Ev kullanıcısı, eğitimli teknik personel veya yetkili/kalifiye elektrik personeli ayrımı ölçüm sınırını değiştirir.');
    }
    if(['pv','ev'].includes(input.location||'')){
      return baseResult('professional','Bu ölçüm özel eğitim ve ekipman gerektirir','PV dizi DC ölçümleri ile elektrikli araç yüksek gerilim sistemleri genel tüketici multimetresi seçimiyle onaylanamaz. Üretici prosedürü, uygun KKD, izolasyon ve yetkili personel gerekir; affiliate kapalıdır.');
    }
    if(input.location==='service'){
      return baseResult('professional','Servis girişi CAT IV ve profesyonel çalışma alanıdır','Sayaç önü, bina servis girişi, havai hat veya ana besleme tarafında ölçüm yalnız kalifiye personel, iş izin sistemi, ark tehlikesi değerlendirmesi ve CAT IV ekipmanla yapılır. Bu araç ürün yönlendirmesi açmaz.');
    }
    if(input.location==='unknown'||!input.location){
      return baseResult('evidence_required','Ölçüm yerini seçin','Elektronik kart, batarya, fişli cihaz, priz, dağıtım panosu, servis girişi, PV veya EV bağlamı bilinmeden CAT seviyesi belirlenemez.');
    }
    if(input.task==='unknown'||!input.task){
      return baseResult('evidence_required','Ölçülecek büyüklüğü seçin','Gerilim, akım, kalkış akımı, direnç, süreklilik veya enerjisizlik doğrulaması farklı araç ve güvenlik adımları gerektirir.');
    }
    if(input.task==='absence_voltage'){
      return baseResult('professional','Enerjisizlik doğrulaması multimetre veya temassız kalemle tek başına yapılmaz','Enerjisiz çalışma kararı için uygun iki kutuplu gerilim test cihazı, bilinen canlı kaynakta önce-sonra çalışma doğrulaması, kilitleme/etiketleme ve kalifiye personel prosedürü gerekir. Affiliate kapalıdır.');
    }
    if(input.task==='leakage'){
      return baseResult('professional','Kaçak akım ölçümü özel pens ve yorum gerektirir','mA çözünürlüklü kaçak akım pensi, iletkenlerin doğru birlikte kavranması ve RCD/topraklama yorumlaması profesyonel ölçümdür. Genel pensampermetre yönlendirmesi yapılmaz.');
    }
    const deenergizedTasks=['resistance','continuity','capacitance'];
    if(deenergizedTasks.includes(input.task)&&input.liveCircuit==='yes'){
      return baseResult('stop_use','Direnç, süreklilik veya kapasiteyi enerjili devrede ölçmeyin','Devre enerjisiz bırakılmalı, depolanmış enerji boşaltılmalı ve uygun prosedürle enerjisizlik doğrulanmalıdır. Ölçüm modunu değiştirmeden önce probları devreden çıkarın.');
    }
    if(input.location==='panel'&&input.competence!=='qualified'){
      return baseResult('professional','Dağıtım panosu ölçümü kalifiye personel işidir','Pano içinde CAT III geçici aşırı gerilim, kısa devre ve ark riski bulunur. Ev kullanıcısı veya yalnız temel eğitimli kişi kapağı açmamalı ve canlı ölçüm yapmamalıdır.');
    }
    if(['socket','appliance'].includes(input.location)&&input.liveCircuit==='yes'&&input.competence==='consumer'){
      return baseResult('professional','Canlı şebeke ölçümünü kullanıcı düzeyinde yapmayın','230 V priz veya cihaz girişinde canlı ölçüm elektrik çarpması ve kısa devre riski taşır. Yetkin teknik personel ve uygun kategori ekipmanı gerekir.');
    }
    if(input.liveCircuit==='unknown'){
      return baseResult('evidence_required','Devrenin enerjili olup olmadığını belirtin','Canlı şebeke ölçümü ile enerjisiz bakım ölçümü aynı seçim değildir.');
    }
    const req=requirements(input);
    if(!req)return baseResult('evidence_required','Ölçüm kategorisi belirlenemedi','Ölçüm yeri ve görevi yeniden kontrol edin.');
    const systemVoltage=num(input.systemVoltage);
    if(systemVoltage===null||systemVoltage<=0||systemVoltage>1000){
      return withReq(baseResult(systemVoltage&&systemVoltage>1000?'professional':'evidence_required',systemVoltage&&systemVoltage>1000?'1000 V üzeri ölçüm bu aracın dışındadır':'Sistem gerilimini girin',systemVoltage&&systemVoltage>1000?'Yüksek gerilim ölçümü özel prosedür, ekipman ve yetki gerektirir.':'Etiket veya tek hat bilgisindeki nominal AC/DC gerilimi girin.'),req);
    }
    const currentTask=['current_ac','current_dc','inrush'].includes(input.task);
    if(currentTask){
      const expectedCurrent=num(input.expectedCurrent);
      if(expectedCurrent===null||expectedCurrent<=0){
        return withReq(baseResult('evidence_required','Beklenen akım aralığını girin','Pens çene kapasitesi ve ölçüm aralığı için üretici etiketi, devre koruma değeri veya önceki güvenilir kayıt kullanılmalıdır.'),req);
      }
      if(expectedCurrent>1000){
        return withReq(baseResult('professional','1000 A üzeri ölçüm özel sensör ve çalışma planı gerektirir','Esnek akım probu, CT oranı, ark tehlikesi ve erişim planı profesyonelce doğrulanmalıdır.'),req);
      }
    }
    if(input.ncvOnly==='yes'){
      return withReq(baseResult('evidence_required','Temassız gerilim kalemi tek başına karar aracı değildir','NCV göstergesi hızlı tarama içindir; gerilim değerini, polariteyi veya güvenli enerjisizlik durumunu tek başına kanıtlamaz. Uygun temaslı test yöntemi gerekir.'),req);
    }
    const searchTerm=`${req.requiredCategoryLabel} ${req.requiredVoltage}V ${req.productClass==='clamp_meter'?'pensampermetre':'dijital multimetre'} ${req.trueRmsRequired?'True RMS ':''}${req.inrushRequired?'inrush ':''}${req.acDcClampRequired?'AC DC ':''}IEC 61010`;
    if(input.existingType==='none'){
      return withReq(baseResult('conditional_purchase',`${req.requiredCategoryLabel} sınıfını doğrulayın`,`Bu görev için en az ${req.requiredCategoryLabel}, ${req.requiredVoltage} V ölçüm sınırı${req.requiredCurrent?` ve yaklaşık ${req.requiredCurrent} A pens aralığı`:''} gerekir. CAT işareti cihazda ve problarda izlenebilir belgeyle eşleşmelidir; yüksek kategori daha düşük kategoride kullanılabilir, tersi kullanılamaz.`,{commercialAllowed:true,searchTerm,productClass:req.productClass}),req);
    }
    const typeOk=req.productClass==='clamp_meter'?input.existingType==='clamp':input.existingType==='multimeter';
    if(!typeOk){
      return withReq(baseResult('replace_candidate',req.productClass==='clamp_meter'?'Akım için uygun pensampermetre gerekir':'Bu görev için dijital multimetre gerekir','Mevcut cihazın temel ölçüm yöntemi göreve uygun değil. Akım devresini açıp multimetrenin A girişinden ölçmek yerine uygun akım aralıklı pens kullanın; gerilim/direnç görevinde ise uygun multimetre kullanın.',{commercialAllowed:true,searchTerm,productClass:req.productClass}),req);
    }
    if((CATEGORY_RANK[input.existingCategory]||0)<CATEGORY_RANK[req.requiredCategory]){
      return withReq(baseResult('replace_candidate','Mevcut CAT seviyesi ölçüm yerine uygun değil',`Gerekli ${req.requiredCategoryLabel}; mevcut işaret ${String(input.existingCategory||'belirsiz').toUpperCase()}. Ölçüm kategorileri yalnız voltaj sayısı değildir; daha düşük CAT seviyesini adaptör veya farklı probla yükseltemezsiniz.`,{commercialAllowed:true,searchTerm,productClass:req.productClass}),req);
    }
    const existingVoltage=num(input.existingVoltage);
    if(existingVoltage===null||existingVoltage<req.requiredVoltage){
      return withReq(baseResult(existingVoltage===null?'evidence_required':'replace_candidate','Gerilim sınırı yetersiz veya belirsiz',`Cihaz ve prob takımının en az ${req.requiredVoltage} V sınırı doğrulanmalıdır. Takımın güvenlik seviyesi en düşük dereceli parçayla sınırlıdır.`,{commercialAllowed:existingVoltage!==null,searchTerm,productClass:req.productClass}),req);
    }
    if(currentTask){
      const existingCurrent=num(input.existingCurrent);
      if(existingCurrent===null||existingCurrent<req.requiredCurrent){
        return withReq(baseResult(existingCurrent===null?'evidence_required':'replace_candidate','Pens akım aralığını doğrulayın',`Yaklaşık ${req.requiredCurrent} A ölçüm payı gerekir. Çene açıklığı, iletken çapı ve AC/DC yeteneği tam model föyünden kontrol edilmelidir.`,{commercialAllowed:existingCurrent!==null,searchTerm,productClass:'clamp_meter'}),req);
      }
      if(req.acDcClampRequired&&input.clampMode!=='acdc'){
        return withReq(baseResult(input.clampMode==='ac'?'replace_candidate':'evidence_required','DC akım için AC/DC pens gerekir','Yalnız AC pens, batarya veya DC hat akımını ölçemez. Hall etkili AC/DC pens ve sıfırlama prosedürü doğrulanmalıdır.',{commercialAllowed:input.clampMode==='ac',searchTerm,productClass:'acdc_clamp_meter'}),req);
      }
    }
    if(req.trueRmsRequired&&input.trueRms!=='yes'){
      return withReq(baseResult(input.trueRms==='no'?'replace_candidate':'evidence_required','True RMS özelliğini doğrulayın','Elektronik yükler, inverterler ve bozulmuş dalga biçimlerinde ortalama yanıtlı cihaz hatalı akım/gerilim gösterebilir. Tam model teknik föyünde True RMS doğrulanmalıdır.',{commercialAllowed:input.trueRms==='no',searchTerm,productClass:req.productClass}),req);
    }
    if(req.inrushRequired&&input.inrush!=='yes'){
      return withReq(baseResult(input.inrush==='no'?'replace_candidate':'evidence_required','Kalkış akımı kayıt özelliği gerekir','Normal MIN/MAX işlevi her zaman kısa motor kalkış darbesini yakalayamaz. Üreticinin özel inrush modu ve ölçüm aralığı doğrulanmalıdır.',{commercialAllowed:input.inrush==='no',searchTerm,productClass:'inrush_clamp_meter'}),req);
    }
    if(input.probeRating!=='yes'){
      return withReq(baseResult('evidence_required','Prob ve aksesuar CAT derecesini doğrulayın','Prob takımı, koruyucu parmak bariyeri, uç kılıfı ve aksesuarlar cihazla aynı veya daha yüksek CAT/voltaj seviyesinde olmalıdır.'),req);
    }
    if(input.inputProtection!=='yes'){
      return withReq(baseResult('evidence_required','Giriş koruması ve sigortaları doğrulayın','Akım girişlerinde uygun yüksek kesme kapasiteli sigorta, giriş uyarıları ve yanlış bağlantıya karşı koruma tam model belgelerinde doğrulanmalıdır. Rastgele sigorta kullanılmaz.'),req);
    }
    if(input.certification!=='yes'){
      return withReq(baseResult('evidence_required','Tam model IEC 61010 uygunluk belgesini doğrulayın','Yalnız kasa üzerindeki CAT baskısı yeterli değildir. Üretici, tam model, kullanım kılavuzu ve izlenebilir IEC 61010-2-033 / -2-032 / -031 uygunluk kanıtı aranmalıdır.'),req);
    }
    if(input.recallChecked==='recalled'){
      return withReq(baseResult('stop_use','Geri çağrılmış ürünü kullanmayın','Üreticinin veya yetkili ürün güvenliği otoritesinin kullanım durdurma/geri çağırma talimatını izleyin. Ticari yönlendirme kapalıdır.'),req);
    }
    if(input.recallChecked!=='yes'){
      return withReq(baseResult('evidence_required','Geri çağırma ve güvenlik duyurusunu kontrol edin','Tam marka-model için üretici ve resmî ürün güvenliği duyuruları kontrol edilmeden cihaz yeterli sayılmaz.'),req);
    }
    if(input.selfCheck!=='yes'){
      return withReq(baseResult(input.selfCheck==='no'?'stop_use':'test_existing','Cihazın çalışma kontrolünü tamamlayın',input.selfCheck==='no'?'Ekran, pil, sigorta, fonksiyon anahtarı veya bilinen kaynak kontrolü başarısızsa cihazı kullanmayın.':'Üretici prosedürüne göre görsel kontrolü, pil/ekranı, sigortayı ve bilinen kaynakta çalışma kontrolünü tamamlayın.'),req);
    }
    return withReq(baseResult('no_buy','Mevcut ölçü aleti yeterli; yeni ürün almayın',`Mevcut cihaz; ${req.requiredCategoryLabel}, ${req.requiredVoltage} V, gerekli ölçüm işlevi, prob, giriş koruması, belge ve çalışma kontrolünü karşılıyor. Üretici bakım/kalibrasyon planını izleyin ve her kullanımdan önce görsel kontrol yapın.`),req);
  }

  function affiliateUrl(result){
    if(!result||!result.commercialAllowed||!result.searchTerm)return null;
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(result.searchTerm)}&tag=${AFFILIATE_TAG}`;
  }

  function mount(doc){
    const form=doc.getElementById('meterForm');
    if(!form)return;
    const ids=['meterCondition','leadCondition','competence','location','task','liveCircuit','systemVoltage','expectedCurrent','ncvOnly','existingType','existingCategory','existingVoltage','existingCurrent','clampMode','trueRms','inrush','probeRating','inputProtection','certification','recallChecked','selfCheck'];
    const el=Object.fromEntries(ids.map(id=>[id,doc.getElementById(id)]));
    const emergency=doc.getElementById('emergency');
    const resultBox=doc.getElementById('result');
    const status=doc.getElementById('status');
    const title=doc.getElementById('resultTitle');
    const summary=doc.getElementById('summary');
    const catMetric=doc.getElementById('catMetric');
    const rangeMetric=doc.getElementById('rangeMetric');
    const productMetric=doc.getElementById('productMetric');
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
      emergency:'112 / güvenli alan',stop_use:'Kullanımı durdurun',professional:'Kalifiye elektrik personeli',
      evidence_required:'Eksik teknik kanıtı tamamlayın',test_existing:'Mevcut cihazı doğrulayın',
      no_buy:'Mevcut cihazı kullanın',conditional_purchase:'Doğrulanmış ölçü aleti sınıfı',replace_candidate:'Uygun kategori ve işlev'
    })[r.status]||'Teknik doğrulama';
    form.addEventListener('submit',(event)=>{
      event.preventDefault();latest=calculate(values());resultBox.hidden=false;resultBox.dataset.status=latest.status;
      status.textContent=latest.status.replaceAll('_',' ').toLocaleUpperCase('tr-TR');title.textContent=latest.title;summary.textContent=latest.summary;
      catMetric.textContent=latest.requiredCategoryLabel||'—';
      rangeMetric.textContent=latest.requiredVoltage?`${latest.requiredVoltage.toLocaleString('tr-TR')} V${latest.requiredCurrent?` · ${latest.requiredCurrent.toLocaleString('tr-TR')} A`:''}`:'—';
      productMetric.textContent=latest.productClass==='clamp_meter'?'Pensampermetre':latest.productClass==='digital_multimeter'?'Dijital multimetre':'—';
      next.textContent=nextLabel(latest);commerce.hidden=!latest.commercialAllowed;confirms.forEach(c=>{c.checked=false;});updateGate();resultBox.focus();
    });
    confirms.forEach(c=>c.addEventListener('change',updateGate));
    form.addEventListener('reset',()=>setTimeout(()=>{latest=null;resultBox.hidden=true;commerce.hidden=true;confirms.forEach(c=>{c.checked=false;});updateGate();},0));
    jsonButton.addEventListener('click',()=>{
      if(!latest)return;
      const payload={tool:'ALO186 Multimetre ve Pensampermetre CAT Uygunluk Testi',createdAt:new Date().toISOString(),personalData:false,result:latest,inputs:values(),disclaimer:'Ön seçimdir; canlı çalışma yetkisi vermez. Üretici ve iş güvenliği prosedürleri önceliklidir.'};
      download('alo186-multimetre-cat-teknik-fis.json','application/json;charset=utf-8',JSON.stringify(payload,null,2));
    });
    icsButton.addEventListener('click',()=>{
      if(!latest)return;
      const date=new Date();date.setUTCDate(date.getUTCDate()+180);const end=new Date(date);end.setUTCDate(end.getUTCDate()+1);
      const stamp=(x)=>`${x.getUTCFullYear()}${String(x.getUTCMonth()+1).padStart(2,'0')}${String(x.getUTCDate()).padStart(2,'0')}`;
      const ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Olcu Aleti Kontrolu//TR','BEGIN:VEVENT',`DTSTART;VALUE=DATE:${stamp(date)}`,`DTEND;VALUE=DATE:${stamp(end)}`,'SUMMARY:Multimetre ve prob guvenlik kontrolu','DESCRIPTION:Kasa, terminaller, prob kablolari, sigortalar, CAT/voltaj isaretleri, pil, kalibrasyon durumu ve geri cagirma duyurularini yeniden kontrol edin.','END:VEVENT','END:VCALENDAR'].join('\r\n');
      download('alo186-multimetre-180-gun-kontrol.ics','text/calendar;charset=utf-8',ics);
    });
    printButton.addEventListener('click',()=>root.print());
  }

  return {calculate,requirements,affiliateUrl,mount,constants:{AFFILIATE_TAG,CURRENT_MARGIN,CATEGORY_RANK}};
});
