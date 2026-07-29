(function(root,factory){
  const api=factory(root.Alo186ProductCatalog||(typeof require==='function'?require('./catalog.js'):null));
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186ProductMatcher=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(catalog){
  if(!catalog)throw new Error('Ürün kataloğu yüklenemedi.');

  function num(value,fallback=0){const n=Number(value);return Number.isFinite(n)?n:fallback;}
  function clamp(value,min,max){return Math.max(min,Math.min(max,value));}

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
    const scorer=categoryId==='powerbank'?scorePowerbank:scoreSurge;
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
    const category=catalog.getCategory(categoryId);
    return category?category.description:'';
  }

  return {match,scorePowerbank,scoreSurge,requirementsSummary,knownRatio,guideResult,qualifiedGateAllowed};
});
