(function(root,factory){
  const api=factory(root.Alo186ProductCatalog||(typeof require==='function'?require('./catalog.js'):null));
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186ProductMatcher=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(catalog){
  if(!catalog)throw new Error('Ürün kataloğu yüklenemedi.');

  function num(value,fallback=0){const n=Number(value);return Number.isFinite(n)?n:fallback;}
  function clamp(value,min,max){return Math.max(min,Math.min(max,value));}
  function totalPorts(attributes){return num(attributes.usbCPorts)+num(attributes.usbAPorts)+num(attributes.ports);}

  function knownRatio(attributes,keys){
    const known=keys.filter(k=>attributes[k]!==null&&attributes[k]!==undefined).length;
    return keys.length?known/keys.length:1;
  }

  function rankLabel(index,total){
    if(total===1)return 'Tek uygun seçenek';
    if(index===0)return 'En güçlü eşleşme';
    if(index===total-1)return 'Alternatif';
    return 'Dengeli seçenek';
  }

  function scorePowerbank(product,requirements){
    const a=product.attributes;
    const minCapacity=num(requirements.minCapacityMah,10000);
    const minOutput=num(requirements.minOutputW,10);
    const needWireless=Boolean(requirements.wireless);
    const reasons=[],unknowns=[],failures=[];

    if(num(a.capacityMah)<minCapacity)failures.push(`Kapasite ${minCapacity} mAh altı.`);
    if(needWireless&&!a.wireless)failures.push('Kablosuz şarj gereksinimini karşılamıyor.');
    if(a.maxOutputW===null||a.maxOutputW===undefined){
      if(minOutput>10)failures.push(`${minOutput} W çıkış gereksinimi, teknik değer bilinmediği için doğrulanamıyor.`);
      else unknowns.push('Maksimum çıkış gücü bilinmiyor.');
    }else if(num(a.maxOutputW)<minOutput)failures.push(`Çıkış gücü ${minOutput} W gereksiniminin altında.`);

    if(failures.length)return {eligible:false,score:0,reasons,unknowns,failures};

    let score=55;
    const reserve=(num(a.capacityMah)-minCapacity)/Math.max(minCapacity,1);
    score+=clamp(reserve*12,0,12);
    if(a.maxOutputW!==null&&a.maxOutputW!==undefined){
      score+=clamp((num(a.maxOutputW)-minOutput)/Math.max(minOutput,1)*10,0,10);
      reasons.push(`${a.maxOutputW} W çıkış, ${minOutput} W minimumu karşılıyor.`);
    }
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
    if(a.joules===null||a.joules===undefined){
      if(minJoules>250)failures.push(`${minJoules} J gereksinimi, joule değeri bilinmediği için doğrulanamıyor.`);
      else unknowns.push('Joule değeri bilinmiyor.');
    }else if(num(a.joules)<minJoules)failures.push(`${minJoules} J minimumunun altında.`);

    if(failures.length)return {eligible:false,score:0,reasons,unknowns,failures};

    let score=55;
    score+=clamp((num(a.outlets)-minOutlets)*3,0,12);
    if(a.joules!==null&&a.joules!==undefined){
      score+=clamp((num(a.joules)-minJoules)/Math.max(minJoules,1)*12,0,12);
      reasons.push(`${a.joules} J değeri, ${minJoules} J minimumu karşılıyor.`);
    }
    reasons.push(`${a.outlets} priz, istenen ${minOutlets} priz sayısını karşılıyor.`);
    if(needUsb&&a.usbPorts)reasons.push(`${a.usbPorts} USB çıkışı bulunuyor.`);
    if(a.maxCurrentA!==null&&a.maxCurrentA!==undefined)reasons.push(`Etikette ${a.maxCurrentA} A nominal akım belirtilmiş.`);
    else unknowns.push('Nominal akım değeri bilinmiyor.');
    score+=knownRatio(a,['outlets','joules','maxCurrentA','usbPorts'])*14;
    score+=product.status==='verified_listing'?5:0;
    return {eligible:true,score:Math.round(clamp(score,0,100)),reasons,unknowns,failures,confidence:unknowns.length>1?'Düşük–orta':unknowns.length?'Orta':'Yüksek'};
  }

  function scoreCharger(product,requirements){
    const a=product.attributes||{};
    const minOutput=num(requirements.minOutputW,25);
    const minUsbC=num(requirements.minUsbCPorts,1);
    const multiPort=Boolean(requirements.multiPort);
    const reasons=[],unknowns=[],failures=[];
    if(a.maxOutputW===null||a.maxOutputW===undefined)failures.push('Maksimum çıkış gücü bilinmiyor.');
    else if(num(a.maxOutputW)<minOutput)failures.push(`${minOutput} W minimum çıkış gereksinimini karşılamıyor.`);
    if(num(a.usbCPorts)<minUsbC)failures.push(`${minUsbC} USB-C port gereksinimini karşılamıyor.`);
    if(multiPort&&totalPorts(a)<2)failures.push('Çoklu cihaz için en az iki port gereksinimini karşılamıyor.');
    if(failures.length)return {eligible:false,score:0,reasons,unknowns,failures};
    let score=58;
    score+=clamp((num(a.maxOutputW)-minOutput)/Math.max(minOutput,1)*12,0,12);
    score+=clamp((totalPorts(a)-1)*3,0,9);
    score+=knownRatio(a,['maxOutputW','usbCPorts','usbAPorts'])*12;
    if(a.pd3||a.pps||a.samsungSfc2)score+=5;
    if(a.gan)score+=3;
    reasons.push(`${a.maxOutputW} W etiket gücü, ${minOutput} W minimumu karşılıyor.`);
    reasons.push(`${num(a.usbCPorts)} USB-C${num(a.usbAPorts)?` + ${num(a.usbAPorts)} USB-A`:''} port bulunuyor.`);
    if(multiPort)reasons.push('Çoklu cihaz kullanımına uygun port sayısı bulunuyor.');
    if(!a.pd3&&!a.pps&&!a.samsungSfc2)unknowns.push('Hızlı şarj protokolü ürün sayfasında yeniden doğrulanmalı.');
    return {eligible:true,score:Math.round(clamp(score,0,100)),reasons,unknowns,failures,confidence:unknowns.length?'Orta':'Yüksek'};
  }

  function scoreUsbCable(product,requirements){
    const a=product.attributes||{};
    const minPower=num(requirements.minPowerW,60);
    const minLength=num(requirements.minLengthM,1);
    const needData=Boolean(requirements.dataTransfer);
    const reasons=[],unknowns=[],failures=[];
    if(a.maxPowerW===null||a.maxPowerW===undefined)failures.push('Kablo güç sınıfı bilinmiyor.');
    else if(num(a.maxPowerW)<minPower)failures.push(`${minPower} W kablo sınıfını karşılamıyor.`);
    if(a.lengthM===null||a.lengthM===undefined)unknowns.push('Kablo uzunluğu bilinmiyor.');
    else if(num(a.lengthM)<minLength)failures.push(`${minLength} m minimum uzunluğu karşılamıyor.`);
    if(needData&&!a.dataTransfer&&!num(a.dataTransferMbps)&&!num(a.dataTransferGbps))failures.push('Veri aktarımı gereksinimi doğrulanamıyor.');
    if(failures.length)return {eligible:false,score:0,reasons,unknowns,failures};
    let score=58;
    score+=clamp((num(a.maxPowerW)-minPower)/Math.max(minPower,1)*10,0,10);
    score+=knownRatio(a,['connectorA','connectorB','maxPowerW','lengthM'])*15;
    if(num(a.maxCurrentA)>=5)score+=4;
    if(a.dataTransfer||num(a.dataTransferMbps)||num(a.dataTransferGbps))score+=4;
    reasons.push(`${a.maxPowerW} W güç sınıfı, ${minPower} W minimumu karşılıyor.`);
    if(a.lengthM!==null&&a.lengthM!==undefined)reasons.push(`${a.lengthM} m uzunluk, seçilen minimumu karşılıyor.`);
    if(needData)reasons.push('Veri aktarımı özelliği ürün kartında belirtilmiş.');
    return {eligible:true,score:Math.round(clamp(score,0,100)),reasons,unknowns,failures,confidence:unknowns.length?'Orta':'Yüksek'};
  }

  function scoreHub(product,requirements){
    const a=product.attributes||{};
    const needHdmi=requirements.needHdmi!==false;
    const needEthernet=Boolean(requirements.needEthernet);
    const minPd=num(requirements.minPdPassThroughW,65);
    const reasons=[],unknowns=[],failures=[];
    if(needHdmi&&!a.hdmiMax)failures.push('HDMI görüntü çıkışı gereksinimi karşılanmıyor.');
    if(needEthernet&&!a.ethernet&&!num(a.ethernetMbps))failures.push('Ethernet gereksinimi karşılanmıyor.');
    if(a.pdPassThroughW===null||a.pdPassThroughW===undefined)unknowns.push('PD geçiş gücü bilinmiyor.');
    else if(num(a.pdPassThroughW)<minPd)failures.push(`${minPd} W PD geçiş sınıfını karşılamıyor.`);
    if(failures.length)return {eligible:false,score:0,reasons,unknowns,failures};
    let score=58;
    score+=knownRatio(a,['hdmiMax','pdPassThroughW','ethernetMbps','dataTransferGbps'])*16;
    score+=clamp((num(a.pdPassThroughW)-minPd)/Math.max(minPd,1)*8,0,8);
    if(a.sdReader)score+=3;
    if(a.microSdReader)score+=3;
    reasons.push(`${a.hdmiMax||'Görüntü'} çıkışı ürün kartında doğrulanmış.`);
    if(a.pdPassThroughW)reasons.push(`${a.pdPassThroughW} W PD geçiş üst sınırı belirtilmiş.`);
    if(needEthernet)reasons.push('Ethernet ihtiyacını karşılıyor.');
    return {eligible:true,score:Math.round(clamp(score,0,100)),reasons,unknowns,failures,confidence:unknowns.length?'Orta':'Yüksek'};
  }

  function scoreDisplay(product,requirements){
    const a=product.attributes||{};
    const minLength=num(requirements.minLengthM,1.8);
    const need4k=requirements.need4k!==false;
    const reasons=[],unknowns=[],failures=[];
    if(a.lengthM===null||a.lengthM===undefined)unknowns.push('Kablo uzunluğu bilinmiyor.');
    else if(num(a.lengthM)<minLength)failures.push(`${minLength} m minimum uzunluğu karşılamıyor.`);
    const displayClaim=String(a.maxResolution||a.hdmiMax||'')+String(a.max4KHz||'')+String(a.maxDataGbps||'');
    if(need4k&&!displayClaim)failures.push('4K görüntü sınıfı teknik kartta doğrulanamıyor.');
    if(failures.length)return {eligible:false,score:0,reasons,unknowns,failures};
    let score=58;
    score+=knownRatio(a,['connectorA','connectorB','lengthM','maxDataGbps'])*15;
    if(num(a.maxDataGbps)>=32.4)score+=8;
    if(a.displayPortVersion==='1.4'||a.hdmiVersion==='2.1')score+=6;
    if(a.vrr||a.earc||a.bidirectional)score+=4;
    if(a.lengthM!==null&&a.lengthM!==undefined)reasons.push(`${a.lengthM} m uzunluk, seçilen minimumu karşılıyor.`);
    if(a.maxResolution)reasons.push(`${a.maxResolution} görüntü sınıfı belirtilmiş.`);
    else if(a.hdmiMax)reasons.push(`${a.hdmiMax} görüntü sınıfı belirtilmiş.`);
    if(a.maxDataGbps)reasons.push(`${a.maxDataGbps} Gbps bant genişliği belirtilmiş.`);
    if(!a.connectorA||!a.connectorB)unknowns.push('Kaynak ve hedef konnektör ürün sayfasında yeniden doğrulanmalı.');
    return {eligible:true,score:Math.round(clamp(score,0,100)),reasons,unknowns,failures,confidence:unknowns.length?'Orta':'Yüksek'};
  }

  function scoreGeneric(product){
    const a=product.attributes||{};
    const known=Object.values(a).filter(value=>value!==null&&value!==undefined).length;
    const reasons=[`${known} doğrulanmış teknik alan katalogda bulunuyor.`];
    const unknowns=known<3?['Teknik alan sayısı sınırlı; ürün sayfasında yeniden doğrulama gerekir.']:[];
    return {eligible:known>0,score:Math.round(clamp(60+known*3+(product.status==='verified_listing'?5:0),0,90)),reasons,unknowns,failures:[],confidence:unknowns.length?'Orta':'Yüksek'};
  }

  function scorerFor(categoryId){
    if(categoryId==='powerbank')return scorePowerbank;
    if(categoryId==='surge_strip')return scoreSurge;
    if(categoryId==='usb_c_charger')return scoreCharger;
    if(categoryId==='usb_c_cable')return scoreUsbCable;
    if(categoryId==='usb_c_hub')return scoreHub;
    if(['display_cable','displayport_cable','hdmi_cable','usb_c_hdmi_cable'].includes(categoryId))return scoreDisplay;
    return scoreGeneric;
  }

  function guideResult(category){
    const professionalSelectionRequired=['compatibility','safety','measurement'].includes(category.risk);
    return {
      category,
      mode:'guide',
      matches:[],
      searchUrl:catalog.searchUrl(category.id),
      professionalSelectionRequired,
      affiliatePolicy:category.affiliatePolicy||'after_checklist',
      nextStep:category.nextStepUrl?{url:category.nextStepUrl,label:category.nextStepLabel||'Ücretsiz ön kontrolü aç'}:null
    };
  }

  function qualifiedGateAllowed(category,options={}){
    return Boolean(options.qualified===true&&category&&category.id==='surge_strip'&&category.mode==='guide'&&category.affiliatePolicy==='after_tool');
  }

  function match(categoryId,requirements={},options={}){
    const category=catalog.getCategory(categoryId);
    if(!category)throw new Error('Ürün kategorisi bulunamadı.');
    const qualifiedGate=qualifiedGateAllowed(category,options);
    if(category.mode!=='direct'&&!qualifiedGate)return guideResult(category);

    const now=options.now||new Date();
    const allProducts=catalog.productsFor(categoryId,{now,freshOnly:false});
    const freshProducts=catalog.productsFor(categoryId,{now,freshOnly:true});
    const staleProductCount=Math.max(0,allProducts.length-freshProducts.length);
    const scorer=scorerFor(categoryId);
    const scored=freshProducts.map(product=>({product,...scorer(product,requirements),freshness:catalog.verificationStatus(product,now)})).filter(x=>x.eligible).sort((a,b)=>b.score-a.score);
    scored.forEach((item,index)=>item.label=rankLabel(index,scored.length));
    return {
      category,
      mode:'direct',
      matches:scored.slice(0,3),
      searchUrl:catalog.searchUrl(categoryId),
      professionalSelectionRequired:false,
      affiliatePolicy:category.affiliatePolicy||'verified_direct',
      staleProductCount,
      freshProductCount:freshProducts.length,
      catalogFresh:staleProductCount===0,
      qualifiedGate
    };
  }

  function requirementsSummary(categoryId,requirements={}){
    if(categoryId==='powerbank')return `${num(requirements.minCapacityMah,10000).toLocaleString('tr-TR')} mAh+, ${num(requirements.minOutputW,10)} W+${requirements.wireless?', kablosuz şarj':''}`;
    if(categoryId==='surge_strip')return `${num(requirements.minOutlets,1)} priz+, ${num(requirements.minJoules,250)} J+${requirements.usb?', USB çıkışı':''}`;
    if(categoryId==='usb_c_charger')return `${num(requirements.minOutputW,25)} W+, ${num(requirements.minUsbCPorts,1)} USB-C port+${requirements.multiPort?', çoklu cihaz':''}`;
    if(categoryId==='usb_c_cable')return `${num(requirements.minPowerW,60)} W+, ${num(requirements.minLengthM,1)} m+${requirements.dataTransfer?', veri':''}`;
    if(categoryId==='usb_c_hub')return `${num(requirements.minPdPassThroughW,65)} W PD+, HDMI${requirements.needEthernet?', Ethernet':''}`;
    if(['display_cable','displayport_cable','hdmi_cable','usb_c_hdmi_cable'].includes(categoryId))return `${num(requirements.minLengthM,1.8)} m+, ${requirements.need4k===false?'temel görüntü':'4K+'}`;
    const category=catalog.getCategory(categoryId);
    return category?category.description:'';
  }

  return {match,scorePowerbank,scoreSurge,scoreCharger,scoreUsbCable,scoreHub,scoreDisplay,scoreGeneric,scorerFor,requirementsSummary,knownRatio,guideResult,qualifiedGateAllowed};
});
