(function(root,factory){
  const api=factory(root.Alo186ProductCatalog||(typeof require==='function'?require('./catalog.js'):null),root);
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186ProductMatcher=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(catalog,root){
  'use strict';
  if(!catalog)throw new Error('Ürün kataloğu yüklenemedi.');

  const directIntentCategories=new Set(['usb_c_charger','usb_c_cable','usb_c_hub']);
  const uiRequirements=new Map();
  let uiCategory=null;

  function num(value,fallback=0){const n=Number(value);return Number.isFinite(n)?n:fallback;}
  function clamp(value,min,max){return Math.max(min,Math.min(max,value));}
  function totalPorts(attributes){return num(attributes.usbCPorts)+num(attributes.usbAPorts)+num(attributes.ports);}
  function knownRatio(attributes,keys){const known=keys.filter(k=>attributes[k]!==null&&attributes[k]!==undefined).length;return keys.length?known/keys.length:1;}
  function rankLabel(index,total){if(total===1)return 'Tek uygun seçenek';if(index===0)return 'En güçlü eşleşme';if(index===total-1)return 'Alternatif';return 'Dengeli seçenek';}
  function mergedRequirements(categoryId,requirements={}){return {...(uiRequirements.get(categoryId)||{}),...(requirements||{})};}

  function scorePowerbank(product,requirements){
    const a=product.attributes;
    const minCapacity=num(requirements.minCapacityMah,10000);
    const minOutput=num(requirements.minOutputW,10);
    const needWireless=Boolean(requirements.wireless);
    const reasons=[],unknowns=[],failures=[];
    if(num(a.capacityMah)<minCapacity)failures.push(`Kapasite ${minCapacity} mAh altı.`);
    if(needWireless&&!a.wireless)failures.push('Kablosuz şarj gereksinimini karşılamıyor.');
    if(a.maxOutputW===null||a.maxOutputW===undefined){if(minOutput>10)failures.push(`${minOutput} W çıkış gereksinimi, teknik değer bilinmediği için doğrulanamıyor.`);else unknowns.push('Maksimum çıkış gücü bilinmiyor.');}
    else if(num(a.maxOutputW)<minOutput)failures.push(`Çıkış gücü ${minOutput} W gereksiniminin altında.`);
    if(failures.length)return {eligible:false,score:0,reasons,unknowns,failures};
    let score=55;
    score+=clamp((num(a.capacityMah)-minCapacity)/Math.max(minCapacity,1)*12,0,12);
    if(a.maxOutputW!==null&&a.maxOutputW!==undefined){score+=clamp((num(a.maxOutputW)-minOutput)/Math.max(minOutput,1)*10,0,10);reasons.push(`${a.maxOutputW} W çıkış, ${minOutput} W minimumu karşılıyor.`);}
    if(a.capacityMah>=minCapacity)reasons.push(`${a.capacityMah.toLocaleString('tr-TR')} mAh kapasite minimumu karşılıyor.`);
    if(needWireless&&a.wireless)reasons.push('Kablosuz şarj ihtiyacını karşılıyor.');
    if(a.display)score+=4;
    score+=knownRatio(a,['capacityMah','maxOutputW','wireless','usbCPorts'])*14;
    score+=product.status==='verified_listing'?5:0;
    return {eligible:true,score:Math.round(clamp(score,0,100)),reasons,unknowns,failures,confidence:unknowns.length?'Orta':'Yüksek'};
  }

  function scoreSurge(product,requirements){
    const a=product.attributes;
    const minOutlets=num(requirements.minOutlets,1);
    const minJoules=num(requirements.minJoules,250);
    const needUsb=Boolean(requirements.usb);
    const reasons=[],unknowns=[],failures=[];
    if(num(a.outlets)<minOutlets)failures.push(`${minOutlets} priz gereksinimini karşılamıyor.`);
    if(needUsb&&num(a.usbPorts)<1)failures.push('USB çıkışı gereksinimini karşılamıyor.');
    if(a.joules===null||a.joules===undefined){if(minJoules>250)failures.push(`${minJoules} J gereksinimi, joule değeri bilinmediği için doğrulanamıyor.`);else unknowns.push('Joule değeri bilinmiyor.');}
    else if(num(a.joules)<minJoules)failures.push(`${minJoules} J minimumunun altında.`);
    if(failures.length)return {eligible:false,score:0,reasons,unknowns,failures};
    let score=55;
    score+=clamp((num(a.outlets)-minOutlets)*3,0,12);
    if(a.joules!==null&&a.joules!==undefined){score+=clamp((num(a.joules)-minJoules)/Math.max(minJoules,1)*12,0,12);reasons.push(`${a.joules} J değeri, ${minJoules} J minimumu karşılıyor.`);}
    reasons.push(`${a.outlets} priz, istenen ${minOutlets} priz sayısını karşılıyor.`);
    if(needUsb&&a.usbPorts)reasons.push(`${a.usbPorts} USB çıkışı bulunuyor.`);
    if(a.maxCurrentA!==null&&a.maxCurrentA!==undefined)reasons.push(`Etikette ${a.maxCurrentA} A nominal akım belirtilmiş.`);else unknowns.push('Nominal akım değeri bilinmiyor.');
    score+=knownRatio(a,['outlets','joules','maxCurrentA','usbPorts'])*14;
    score+=product.status==='verified_listing'?5:0;
    return {eligible:true,score:Math.round(clamp(score,0,100)),reasons,unknowns,failures,confidence:unknowns.length>1?'Düşük–orta':unknowns.length?'Orta':'Yüksek'};
  }

  function scoreCharger(product,requirements){
    const a=product.attributes||{};
    const minOutput=num(requirements.minOutputW,25);
    const minUsbC=num(requirements.minUsbCPorts,1);
    const multiPort=Boolean(requirements.multiPort);
    const requirePps=Boolean(requirements.requirePps);
    const requirePd31=Boolean(requirements.requirePd31);
    const reasons=[],unknowns=[],failures=[];
    if(a.maxOutputW===null||a.maxOutputW===undefined)failures.push('Maksimum çıkış gücü bilinmiyor.');
    else if(num(a.maxOutputW)<minOutput)failures.push(`${minOutput} W minimum çıkış gereksinimini karşılamıyor.`);
    if(num(a.usbCPorts)<minUsbC)failures.push(`${minUsbC} USB-C port gereksinimini karşılamıyor.`);
    if(multiPort&&totalPorts(a)<2)failures.push('Çoklu cihaz için en az iki port gereksinimini karşılamıyor.');
    if(requirePps&&!a.pps)failures.push('PPS desteği teknik kayıtta doğrulanmıyor.');
    if(requirePd31&&!a.pd31)failures.push('USB PD 3.1 desteği teknik kayıtta doğrulanmıyor.');
    if(failures.length)return {eligible:false,score:0,reasons,unknowns,failures};
    let score=58;
    score+=clamp((num(a.maxOutputW)-minOutput)/Math.max(minOutput,1)*12,0,12);
    score+=clamp((totalPorts(a)-1)*3,0,9);
    score+=knownRatio(a,['maxOutputW','usbCPorts','usbAPorts'])*12;
    if(a.pd3||a.pd31||a.pps||a.samsungSfc2)score+=5;
    if(a.gan)score+=3;
    reasons.push(`${a.maxOutputW} W etiket gücü, ${minOutput} W minimumu karşılıyor.`);
    reasons.push(`${num(a.usbCPorts)} USB-C${num(a.usbAPorts)?` + ${num(a.usbAPorts)} USB-A`:''} port bulunuyor.`);
    if(multiPort)reasons.push('Çoklu cihaz kullanımına uygun port sayısı bulunuyor.');
    if(requirePps)reasons.push('PPS desteği doğrulanmış.');
    if(requirePd31)reasons.push('USB PD 3.1 desteği doğrulanmış.');
    if(!a.pd3&&!a.pd31&&!a.pps&&!a.samsungSfc2)unknowns.push('Hızlı şarj protokolü ürün sayfasında yeniden doğrulanmalı.');
    return {eligible:true,score:Math.round(clamp(score,0,100)),reasons,unknowns,failures,confidence:unknowns.length?'Orta':'Yüksek'};
  }

  function scoreUsbCable(product,requirements){
    const a=product.attributes||{};
    const minPower=num(requirements.minPowerW,60);
    const minLength=num(requirements.minLengthM,1);
    const minDataGbps=num(requirements.minDataGbps,0);
    const needData=Boolean(requirements.dataTransfer)||minDataGbps>0;
    const requireEpr=Boolean(requirements.requireEpr)||minPower>100;
    const reasons=[],unknowns=[],failures=[];
    if(a.maxPowerW===null||a.maxPowerW===undefined)failures.push('Kablo güç sınıfı bilinmiyor.');
    else if(num(a.maxPowerW)<minPower)failures.push(`${minPower} W kablo sınıfını karşılamıyor.`);
    if(a.lengthM===null||a.lengthM===undefined)unknowns.push('Kablo uzunluğu bilinmiyor.');
    else if(num(a.lengthM)<minLength)failures.push(`${minLength} m minimum uzunluğu karşılamıyor.`);
    const numericDataGbps=num(a.dataTransferGbps,num(a.dataTransferMbps)/1000);
    if(needData&&!a.dataTransfer&&!numericDataGbps)failures.push('Veri aktarımı gereksinimi doğrulanamıyor.');
    if(minDataGbps>0&&numericDataGbps<minDataGbps)failures.push(`${minDataGbps} Gbps veri gereksinimi doğrulanamıyor.`);
    if(requireEpr&&!a.pdEpr&&!a.epr)failures.push('240 W USB PD EPR ve 5 A E-marker sınıfı doğrulanmıyor.');
    if(failures.length)return {eligible:false,score:0,reasons,unknowns,failures};
    let score=58;
    score+=clamp((num(a.maxPowerW)-minPower)/Math.max(minPower,1)*10,0,10);
    score+=knownRatio(a,['connectorA','connectorB','maxPowerW','lengthM'])*15;
    if(num(a.maxCurrentA)>=5)score+=4;
    if(a.dataTransfer||numericDataGbps)score+=4;
    reasons.push(`${a.maxPowerW} W güç sınıfı, ${minPower} W minimumu karşılıyor.`);
    if(a.lengthM!==null&&a.lengthM!==undefined)reasons.push(`${a.lengthM} m uzunluk, seçilen minimumu karşılıyor.`);
    if(needData)reasons.push(minDataGbps?`${numericDataGbps} Gbps veri sınıfı minimumu karşılıyor.`:'Veri aktarımı özelliği ürün kartında belirtilmiş.');
    if(requireEpr)reasons.push('USB PD EPR sınıfı doğrulanmış.');
    return {eligible:true,score:Math.round(clamp(score,0,100)),reasons,unknowns,failures,confidence:unknowns.length?'Orta':'Yüksek'};
  }

  function scoreHub(product,requirements){
    const a=product.attributes||{};
    const needHdmi=requirements.needHdmi!==false;
    const needEthernet=Boolean(requirements.needEthernet);
    const needCardReader=Boolean(requirements.needCardReader);
    const minPd=num(requirements.minPdPassThroughW,65);
    const minDataGbps=num(requirements.minDataGbps,0);
    const reasons=[],unknowns=[],failures=[];
    if(needHdmi&&!a.hdmiMax)failures.push('HDMI görüntü çıkışı gereksinimi karşılanmıyor.');
    if(needEthernet&&!a.ethernet&&!num(a.ethernetMbps))failures.push('Ethernet gereksinimi karşılanmıyor.');
    if(needCardReader&&!a.sdReader&&!a.microSdReader)failures.push('Kart okuyucu gereksinimi karşılanmıyor.');
    if(a.pdPassThroughW===null||a.pdPassThroughW===undefined){if(minPd>0)failures.push('PD geçiş gücü bilinmediği için minimum doğrulanamıyor.');else unknowns.push('PD geçiş gücü bilinmiyor.');}
    else if(num(a.pdPassThroughW)<minPd)failures.push(`${minPd} W PD geçiş sınıfını karşılamıyor.`);
    if(minDataGbps>0&&num(a.dataTransferGbps)<minDataGbps)failures.push(`${minDataGbps} Gbps veri gereksinimi teknik kartta doğrulanmıyor.`);
    if(failures.length)return {eligible:false,score:0,reasons,unknowns,failures};
    let score=58;
    score+=knownRatio(a,['hdmiMax','pdPassThroughW','ethernetMbps','dataTransferGbps'])*16;
    score+=clamp((num(a.pdPassThroughW)-minPd)/Math.max(minPd,1)*8,0,8);
    if(a.sdReader)score+=3;if(a.microSdReader)score+=3;
    reasons.push(`${a.hdmiMax||'Görüntü'} çıkışı ürün kartında doğrulanmış.`);
    if(a.pdPassThroughW)reasons.push(`${a.pdPassThroughW} W PD geçiş üst sınırı belirtilmiş.`);
    if(needEthernet)reasons.push('Ethernet ihtiyacını karşılıyor.');
    if(needCardReader)reasons.push('Kart okuyucu ihtiyacını karşılıyor.');
    if(minDataGbps)reasons.push(`${a.dataTransferGbps} Gbps veri sınıfı minimumu karşılıyor.`);
    return {eligible:true,score:Math.round(clamp(score,0,100)),reasons,unknowns,failures,confidence:unknowns.length?'Orta':'Yüksek'};
  }

  function scoreDisplay(product,requirements){
    const a=product.attributes||{};
    const minLength=num(requirements.minLengthM,1.8);
    const need4k=requirements.need4k!==false;
    const reasons=[],unknowns=[],failures=[];
    if(a.lengthM===null||a.lengthM===undefined)unknowns.push('Kablo uzunluğu bilinmiyor.');else if(num(a.lengthM)<minLength)failures.push(`${minLength} m minimum uzunluğu karşılamıyor.`);
    const displayClaim=String(a.maxResolution||a.hdmiMax||'')+String(a.max4KHz||'')+String(a.maxDataGbps||'');
    if(need4k&&!displayClaim)failures.push('4K görüntü sınıfı teknik kartta doğrulanamıyor.');
    if(failures.length)return {eligible:false,score:0,reasons,unknowns,failures};
    let score=58;
    score+=knownRatio(a,['connectorA','connectorB','lengthM','maxDataGbps'])*15;
    if(num(a.maxDataGbps)>=32.4)score+=8;if(a.displayPortVersion==='1.4'||a.hdmiVersion==='2.1')score+=6;if(a.vrr||a.earc||a.bidirectional)score+=4;
    if(a.lengthM!==null&&a.lengthM!==undefined)reasons.push(`${a.lengthM} m uzunluk, seçilen minimumu karşılıyor.`);
    if(a.maxResolution)reasons.push(`${a.maxResolution} görüntü sınıfı belirtilmiş.`);else if(a.hdmiMax)reasons.push(`${a.hdmiMax} görüntü sınıfı belirtilmiş.`);
    if(a.maxDataGbps)reasons.push(`${a.maxDataGbps} Gbps bant genişliği belirtilmiş.`);
    if(!a.connectorA||!a.connectorB)unknowns.push('Kaynak ve hedef konnektör ürün sayfasında yeniden doğrulanmalı.');
    return {eligible:true,score:Math.round(clamp(score,0,100)),reasons,unknowns,failures,confidence:unknowns.length?'Orta':'Yüksek'};
  }

  function scoreGeneric(product){const a=product.attributes||{};const known=Object.values(a).filter(value=>value!==null&&value!==undefined).length;const reasons=[`${known} doğrulanmış teknik alan katalogda bulunuyor.`];const unknowns=known<3?['Teknik alan sayısı sınırlı; ürün sayfasında yeniden doğrulama gerekir.']:[];return {eligible:known>0,score:Math.round(clamp(60+known*3+(product.status==='verified_listing'?5:0),0,90)),reasons,unknowns,failures:[],confidence:unknowns.length?'Orta':'Yüksek'};}
  function scorerFor(categoryId){if(categoryId==='powerbank')return scorePowerbank;if(categoryId==='surge_strip')return scoreSurge;if(categoryId==='usb_c_charger')return scoreCharger;if(categoryId==='usb_c_cable')return scoreUsbCable;if(categoryId==='usb_c_hub')return scoreHub;if(['display_cable','displayport_cable','hdmi_cable','usb_c_hdmi_cable'].includes(categoryId))return scoreDisplay;return scoreGeneric;}
  function guideResult(category){const professionalSelectionRequired=['compatibility','safety','measurement'].includes(category.risk);return {category,mode:'guide',matches:[],searchUrl:catalog.searchUrl(category.id),professionalSelectionRequired,affiliatePolicy:category.affiliatePolicy||'after_checklist',nextStep:category.nextStepUrl?{url:category.nextStepUrl,label:category.nextStepLabel||'Ücretsiz ön kontrolü aç'}:null};}
  function qualifiedGateAllowed(category,options={}){return Boolean(options.qualified===true&&category&&category.id==='surge_strip'&&category.mode==='guide'&&category.affiliatePolicy==='after_tool');}
  function blockedDirectResult(category,reason){return {category,mode:'direct',matches:[],searchUrl:catalog.searchUrl(category.id),professionalSelectionRequired:false,affiliatePolicy:category.affiliatePolicy||'verified_direct',staleProductCount:0,freshProductCount:catalog.productsFor(category.id,{freshOnly:true}).length,catalogFresh:true,qualifiedGate:false,blockReason:reason};}

  function match(categoryId,requirements={},options={}){
    const category=catalog.getCategory(categoryId);if(!category)throw new Error('Ürün kategorisi bulunamadı.');
    const req=mergedRequirements(categoryId,requirements);
    const qualifiedGate=qualifiedGateAllowed(category,options);
    if(category.mode!=='direct'&&!qualifiedGate)return guideResult(category);
    if(req.hazard)return blockedDirectResult(category,'hazard');
    if(req.existingSufficient)return blockedDirectResult(category,'no_buy');
    const now=options.now||new Date();
    const allProducts=catalog.productsFor(categoryId,{now,freshOnly:false});
    const freshProducts=catalog.productsFor(categoryId,{now,freshOnly:true});
    const staleProductCount=Math.max(0,allProducts.length-freshProducts.length);
    const scorer=scorerFor(categoryId);
    const scored=freshProducts.map(product=>({product,...scorer(product,req),freshness:catalog.verificationStatus(product,now)})).filter(x=>x.eligible).sort((a,b)=>b.score-a.score);
    scored.forEach((item,index)=>item.label=rankLabel(index,scored.length));
    return {category,mode:'direct',matches:scored.slice(0,3),searchUrl:catalog.searchUrl(categoryId),professionalSelectionRequired:false,affiliatePolicy:category.affiliatePolicy||'verified_direct',staleProductCount,freshProductCount:freshProducts.length,catalogFresh:staleProductCount===0,qualifiedGate};
  }

  function requirementsSummary(categoryId,requirements={}){
    const req=mergedRequirements(categoryId,requirements);
    if(req.hazard)return 'Güvenlik riski — ticari yol kapalı';
    if(req.existingSufficient)return 'Mevcut ürün yeterli — satın alma yok';
    if(categoryId==='powerbank')return `${num(req.minCapacityMah,10000).toLocaleString('tr-TR')} mAh+, ${num(req.minOutputW,10)} W+${req.wireless?', kablosuz şarj':''}`;
    if(categoryId==='surge_strip')return `${num(req.minOutlets,1)} priz+, ${num(req.minJoules,250)} J+${req.usb?', USB çıkışı':''}`;
    if(categoryId==='usb_c_charger')return `${num(req.minOutputW,25)} W+, ${num(req.minUsbCPorts,1)} USB-C port+${req.multiPort?', çoklu cihaz':''}${req.requirePps?', PPS':''}${req.requirePd31?', PD 3.1':''}`;
    if(categoryId==='usb_c_cable')return `${num(req.minPowerW,60)} W+, ${num(req.minLengthM,1)} m+${num(req.minDataGbps)>0?`, ${num(req.minDataGbps)} Gbps+`:req.dataTransfer?', veri':''}${req.requireEpr?', EPR':''}`;
    if(categoryId==='usb_c_hub')return `${num(req.minPdPassThroughW,65)} W PD+${req.needHdmi===false?'':', HDMI'}${req.needEthernet?', Ethernet':''}${req.needCardReader?', kart okuyucu':''}${num(req.minDataGbps)>0?`, ${num(req.minDataGbps)} Gbps+`:''}`;
    if(['display_cable','displayport_cable','hdmi_cable','usb_c_hdmi_cable'].includes(categoryId))return `${num(req.minLengthM,1.8)} m+, ${req.need4k===false?'temel görüntü':'4K+'}`;
    return categoryId&&catalog.getCategory(categoryId)?catalog.getCategory(categoryId).description:'';
  }

  function commonGateMarkup(){return `<div class="guide-list full"><label class="check-item"><input data-intent-field="existingSufficient" type="checkbox"><span><b>Mevcut ürünüm güvenli ve ihtiyacı karşılıyor</b><br><small>Bu durumda yeni ürün gösterilmez.</small></span></label><label class="check-item"><input data-intent-field="hazard" type="checkbox"><span><b>Isınma, erime, şişme, yanık kokusu, kıvılcım veya açık iletken var</b><br><small>Ticari yol kapanır; ürünü kullanmayı bırakın.</small></span></label></div>`;}
  function intentMarkup(categoryId){
    if(categoryId==='usb_c_charger')return `<div class="form-grid"><label class="field"><span>Cihazın kabul ettiği minimum güç</span><select data-intent-field="minOutputW"><option value="25">25 W</option><option value="45" selected>45 W</option><option value="65">65 W</option><option value="100">100 W</option><option value="140">140 W</option></select></label><label class="field"><span>Minimum USB-C portu</span><select data-intent-field="minUsbCPorts"><option value="1" selected>1</option><option value="2">2</option></select></label><label class="check-item field full"><input data-intent-field="multiPort" type="checkbox"><span><b>Aynı anda birden fazla cihaz</b><br><small>Toplam güç ile tek port gücünü ayrı doğrulayın.</small></span></label><label class="check-item field full"><input data-intent-field="requirePps" type="checkbox"><span><b>PPS zorunlu</b><br><small>Yalnız teknik kayıtta PPS doğrulanan ürünler gösterilir.</small></span></label><label class="check-item field full"><input data-intent-field="requirePd31" type="checkbox"><span><b>USB PD 3.1 zorunlu</b><br><small>100–140 W sınıfında cihaz ve kablo desteğini de doğrulayın.</small></span></label>${commonGateMarkup()}</div>`;
    if(categoryId==='usb_c_cable')return `<div class="form-grid"><label class="field"><span>Minimum şarj gücü</span><select data-intent-field="minPowerW"><option value="60">60 W</option><option value="100" selected>100 W</option><option value="240">240 W EPR</option></select></label><label class="field"><span>Minimum uzunluk</span><select data-intent-field="minLengthM"><option value="1">1 m</option><option value="2" selected>2 m</option><option value="3">3 m</option></select></label><label class="field"><span>Veri ihtiyacı</span><select data-intent-field="minDataGbps"><option value="0">Yalnız şarj / hız önemsiz</option><option value="0.48">Temel veri — 480 Mbps+</option><option value="10">Yüksek hızlı veri — 10 Gbps+</option></select></label><label class="check-item field full"><input data-intent-field="requireEpr" type="checkbox"><span><b>240 W USB PD EPR gerekli</b><br><small>Güç etiketi veri veya görüntü desteği anlamına gelmez.</small></span></label>${commonGateMarkup()}</div>`;
    if(categoryId==='usb_c_hub')return `<div class="form-grid"><label class="field"><span>Minimum PD geçiş gücü</span><select data-intent-field="minPdPassThroughW"><option value="0">PD geçişi gerekmiyor</option><option value="65" selected>65 W</option><option value="100">100 W</option></select></label><label class="field"><span>Minimum USB veri hızı</span><select data-intent-field="minDataGbps"><option value="0" selected>Hız şartı yok</option><option value="5">5 Gbps</option><option value="10">10 Gbps</option></select></label><label class="check-item field full"><input data-intent-field="needHdmi" type="checkbox" checked><span><b>HDMI görüntü gerekli</b><br><small>Kaynak USB-C portunda görüntü çıkışı ayrıca bulunmalıdır.</small></span></label><label class="check-item field full"><input data-intent-field="needEthernet" type="checkbox"><span><b>Gigabit Ethernet gerekli</b></span></label><label class="check-item field full"><input data-intent-field="needCardReader" type="checkbox"><span><b>SD veya microSD kart okuyucu gerekli</b></span></label>${commonGateMarkup()}</div>`;
    return '';
  }
  function readIntentFields(categoryId){
    if(!root.document)return {};
    const container=root.document.getElementById('requirementFields');if(!container)return {};
    const value=name=>{const el=container.querySelector(`[data-intent-field="${name}"]`);if(!el)return undefined;return el.type==='checkbox'?el.checked:Number(el.value);};
    const base={existingSufficient:Boolean(value('existingSufficient')),hazard:Boolean(value('hazard'))};
    if(categoryId==='usb_c_charger')return {...base,minOutputW:value('minOutputW'),minUsbCPorts:value('minUsbCPorts'),multiPort:Boolean(value('multiPort')),requirePps:Boolean(value('requirePps')),requirePd31:Boolean(value('requirePd31'))};
    if(categoryId==='usb_c_cable')return {...base,minPowerW:value('minPowerW'),minLengthM:value('minLengthM'),minDataGbps:value('minDataGbps'),requireEpr:Boolean(value('requireEpr'))};
    if(categoryId==='usb_c_hub')return {...base,minPdPassThroughW:value('minPdPassThroughW'),minDataGbps:value('minDataGbps'),needHdmi:Boolean(value('needHdmi')),needEthernet:Boolean(value('needEthernet')),needCardReader:Boolean(value('needCardReader'))};
    return base;
  }
  function installIntentFields(categoryId){if(!root.document||!directIntentCategories.has(categoryId))return;const container=root.document.getElementById('requirementFields');if(container)container.innerHTML=intentMarkup(categoryId);}
  function renderBlockedDecision(){
    if(!root.document||!uiCategory)return;
    const req=uiRequirements.get(uiCategory)||{};if(!req.hazard&&!req.existingSufficient)return;
    const resultText=root.document.getElementById('resultText');const direct=root.document.getElementById('directResult');const guide=root.document.getElementById('guideResult');
    if(guide)guide.classList.add('hidden');if(direct)direct.classList.remove('hidden');
    if(req.hazard){if(resultText)resultText.textContent='Fiziksel veya elektriksel risk seçildi. Affiliate ve ürün yolları kapatıldı.';if(direct)direct.innerHTML='<div class="empty-products stale-note"><h3>Ürünü kullanmayı bırakın.</h3><p>Isınan, eriyen, şişen, kıvılcım çıkaran veya açık iletkenli ekipmanı enerjisiz bırakın. Güvenli inceleme tamamlanmadan yeni ürün bağlantısı açılmaz.</p></div>';}
    else{if(resultText)resultText.textContent='Mevcut ürün güvenli ve ihtiyacı karşılıyor. Yeni ürün satın almak gerekli değildir.';if(direct)direct.innerHTML='<div class="empty-products"><h3>Satın alma yok</h3><p>Mevcut adaptör, kablo veya hub teknik ihtiyacı karşılıyorsa değiştirmeyin. İhtiyaç ya da cihaz etiketi değiştiğinde yeniden kontrol edin.</p></div>';}
  }
  function installUiGates(){
    if(!root.document)return;
    const grid=root.document.getElementById('categoryGrid');
    if(grid)grid.addEventListener('click',event=>{const button=event.target.closest&&event.target.closest('[data-category]');if(!button)return;uiCategory=button.dataset.category;if(directIntentCategories.has(uiCategory))installIntentFields(uiCategory);});
    const matchButton=root.document.getElementById('matchBtn');
    if(matchButton)matchButton.addEventListener('click',()=>{if(uiCategory&&directIntentCategories.has(uiCategory))uiRequirements.set(uiCategory,readIntentFields(uiCategory));setTimeout(renderBlockedDecision,0);},true);
    const params=new URLSearchParams(root.location&&root.location.search||'');const query=params.get('kategori');if(query&&directIntentCategories.has(query)){uiCategory=query;setTimeout(()=>installIntentFields(query),0);}
  }
  if(root&&root.document)root.document.addEventListener('DOMContentLoaded',installUiGates);

  return {match,scorePowerbank,scoreSurge,scoreCharger,scoreUsbCable,scoreHub,scoreDisplay,scoreGeneric,scorerFor,requirementsSummary,knownRatio,guideResult,qualifiedGateAllowed,directIntentCategories,intentMarkup,readIntentFields};
});
