(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.Alo186TrustGrowthCore=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const schemaVersion=1;
  const confidenceMinimumScore=70;
  const verificationMaxAgeDays=45;
  const allowedEventKeys=['category','status','reason','readiness_band','match_count','stale_count','confidence','product_id','purchase_needed','existing_status'];
  const forbiddenEventKeys=['name','fullName','email','phone','address','subscription','identity','plate','serialNumber','freeText','requirements','existing','raw','value'];

  function num(value){
    if(value===null||value===undefined||value==='')return null;
    const parsed=Number(value);
    return Number.isFinite(parsed)?parsed:null;
  }

  function bool(value){return typeof value==='boolean'?value:null;}

  function normalizeExisting(input={}){
    return {
      owned:Boolean(input.owned),
      capacityMah:num(input.capacityMah),
      maxOutputW:num(input.maxOutputW),
      wireless:bool(input.wireless),
      outlets:num(input.outlets),
      joules:num(input.joules),
      usb:bool(input.usb)
    };
  }

  function assessExistingProduct(categoryId,requirements={},input={}){
    const existing=normalizeExisting(input);
    if(!existing.owned)return {status:'none',purchaseNeeded:true,reasons:['Mevcut ürün beyan edilmedi.'],missing:[]};

    const reasons=[];
    const missing=[];
    const failures=[];

    if(categoryId==='powerbank'){
      const minCapacity=Math.max(0,num(requirements.minCapacityMah)||0);
      const minOutput=Math.max(0,num(requirements.minOutputW)||0);
      const needWireless=Boolean(requirements.wireless);
      if(existing.capacityMah===null)missing.push('Mevcut powerbank kapasitesi bilinmiyor.');
      else if(existing.capacityMah<minCapacity)failures.push(`Mevcut kapasite ${minCapacity} mAh minimumunu karşılamıyor.`);
      else reasons.push('Mevcut kapasite seçilen minimumu karşılıyor.');
      if(existing.maxOutputW===null)missing.push('Mevcut powerbank çıkış gücü bilinmiyor.');
      else if(existing.maxOutputW<minOutput)failures.push(`Mevcut çıkış gücü ${minOutput} W minimumunu karşılamıyor.`);
      else reasons.push('Mevcut çıkış gücü seçilen minimumu karşılıyor.');
      if(needWireless){
        if(existing.wireless===null)missing.push('Mevcut üründe kablosuz şarj bilgisi bilinmiyor.');
        else if(!existing.wireless)failures.push('Mevcut ürün kablosuz şarj ihtiyacını karşılamıyor.');
        else reasons.push('Mevcut ürün kablosuz şarj ihtiyacını karşılıyor.');
      }
    }else if(categoryId==='surge_strip'){
      const minOutlets=Math.max(0,num(requirements.minOutlets)||0);
      const minJoules=Math.max(0,num(requirements.minJoules)||0);
      const needUsb=Boolean(requirements.usb);
      if(existing.outlets===null)missing.push('Mevcut grup prizin priz sayısı bilinmiyor.');
      else if(existing.outlets<minOutlets)failures.push(`Mevcut ürün ${minOutlets} priz minimumunu karşılamıyor.`);
      else reasons.push('Mevcut priz sayısı seçilen minimumu karşılıyor.');
      if(existing.joules===null)missing.push('Mevcut ürünün joule değeri bilinmiyor.');
      else if(existing.joules<minJoules)failures.push(`Mevcut ürün ${minJoules} J minimumunu karşılamıyor.`);
      else reasons.push('Mevcut joule değeri seçilen minimumu karşılıyor.');
      if(needUsb){
        if(existing.usb===null)missing.push('Mevcut üründe USB çıkışı bilgisi bilinmiyor.');
        else if(!existing.usb)failures.push('Mevcut ürün USB çıkışı ihtiyacını karşılamıyor.');
        else reasons.push('Mevcut ürün USB ihtiyacını karşılıyor.');
      }
    }else{
      return {status:'unsupported',purchaseNeeded:null,reasons:['Bu kategori için mevcut ürün yeterlilik hesabı uygulanmıyor.'],missing:[]};
    }

    if(failures.length)return {status:'insufficient',purchaseNeeded:true,reasons:[...reasons,...failures],missing};
    if(missing.length)return {status:'unknown',purchaseNeeded:null,reasons,missing};
    return {status:'adequate',purchaseNeeded:false,reasons,missing:[]};
  }

  function ageDays(verifiedAt,now=new Date()){
    const checked=new Date(verifiedAt);
    const current=new Date(now);
    if(!Number.isFinite(checked.getTime())||!Number.isFinite(current.getTime()))return null;
    const start=Date.UTC(checked.getUTCFullYear(),checked.getUTCMonth(),checked.getUTCDate());
    const end=Date.UTC(current.getUTCFullYear(),current.getUTCMonth(),current.getUTCDate());
    return Math.max(0,Math.floor((end-start)/86400000));
  }

  function affiliateEligibility(input={},now=new Date()){
    const existingStatus=String(input.existingStatus||'none');
    const confidence=String(input.confidence||'').toLocaleLowerCase('tr');
    const unknowns=Array.isArray(input.unknowns)?input.unknowns.filter(Boolean):[];
    const score=num(input.score);
    const verifiedAge=ageDays(input.verifiedAt,now);

    if(existingStatus==='adequate')return {allowed:false,reason:'existing_equipment_adequate',message:'Mevcut ürün seçilen teknik minimumu karşılıyor. Yeni ürün satın almak gerekmeyebilir.'};
    if(existingStatus==='unknown')return {allowed:false,reason:'existing_equipment_unknown',message:'Mevcut ürünün etiket bilgileri tamamlanmadan yeni ürün bağlantısı açılmaz.'};
    if(existingStatus==='unsupported')return {allowed:false,reason:'existing_equipment_not_assessed',message:'Bu kategoride ürün kararı teknik araç veya uzman kontrolünden sonra verilmelidir.'};
    if(verifiedAge===null||verifiedAge>verificationMaxAgeDays)return {allowed:false,reason:'verification_stale',message:'Ürün teknik doğrulaması güncel değil. Katalog yenilenene kadar doğrudan ürün bağlantısı açılmaz.'};
    if(unknowns.length)return {allowed:false,reason:'technical_data_incomplete',message:'Ürün kartında bilinmeyen teknik alanlar var. Doğrudan ürün yerine teknik ihtiyacı kaydedin veya kategoriye dönün.'};
    if(!confidence.includes('yüksek'))return {allowed:false,reason:'confidence_below_high',message:'Teknik güven düzeyi yüksek değil. Ürün bağlantısı yerine yeniden doğrulama gerekir.'};
    if(score===null||score<confidenceMinimumScore)return {allowed:false,reason:'match_score_low',message:'Uygunluk puanı doğrudan ürün bağlantısı için yeterli değil.'};
    return {allowed:true,reason:'high_confidence_verified_match',message:'Mevcut ihtiyaç doğrulandı ve ürün kartındaki temel teknik alanlar yüksek güvenle eşleşiyor.'};
  }

  function decisionQuality(input={}){
    const existingStatus=String(input.existingStatus||'none');
    const matchCount=Math.max(0,Number(input.matchCount)||0);
    const staleCount=Math.max(0,Number(input.staleCount)||0);
    const highConfidenceCount=Math.max(0,Number(input.highConfidenceCount)||0);
    const lowConfidenceCount=Math.max(0,Number(input.lowConfidenceCount)||0);
    const noMatch=matchCount===0;

    if(existingStatus==='adequate')return {score:100,band:'satın_alma_gerekmiyor',title:'Mevcut ürün yeterli görünüyor',nextAction:'Yeni ürün yerine mevcut ekipmanı kullanın; teknik etiket değişirse yeniden kontrol edin.'};

    let score=25;
    if(existingStatus==='none'||existingStatus==='insufficient')score+=25;
    else if(existingStatus==='unknown')score+=5;
    if(matchCount>0)score+=20;
    if(highConfidenceCount>0)score+=30;
    else if(lowConfidenceCount>0)score+=10;
    if(staleCount>0)score-=10;
    score=Math.max(0,Math.min(100,score));

    if(noMatch&&staleCount>0)return {score,band:'katalog_yenileme_bekleniyor',title:'Güncel doğrulanmış ürün yok',nextAction:'Teknik ihtiyaç dosyasını kaydedin ve katalog yenilendiğinde yeniden kontrol edin.'};
    if(noMatch)return {score,band:'dogrulanmis_eslesme_yok',title:'Doğrulanmış eşleşme bulunamadı',nextAction:'Minimumları düşürmeden teknik ihtiyacı kaydedin veya üretici etiketlerini karşılaştırın.'};
    if(highConfidenceCount===0)return {score,band:'eksik_teknik_veri',title:'Eşleşme var, teknik veri eksik',nextAction:'Bilinmeyen alanlar tamamlanmadan doğrudan ürün bağlantısına ilerlemeyin.'};
    if(existingStatus==='unknown')return {score,band:'mevcut_urun_bilinmiyor',title:'Önce mevcut ürünün etiketini okuyun',nextAction:'Yeni ürün almadan kapasite, güç ve gerekli teknik alanları tamamlayın.'};
    return {score,band:'yuksek_guvenli_karsilastirma',title:'Karşılaştırmaya hazır',nextAction:'Kısa listeyi karşılaştırın; satın alma kapısında ihtiyacı ve teknik sınırları yeniden onaylayın.'};
  }

  function sanitizeEvent(input={}){
    if(!input||typeof input!=='object')return {};
    const clean={};
    for(const key of allowedEventKeys){
      if(!(key in input))continue;
      const value=input[key];
      if(typeof value==='string')clean[key]=value.replace(/[<>]/g,'').slice(0,80);
      else if(typeof value==='number'&&Number.isFinite(value))clean[key]=value;
      else if(typeof value==='boolean')clean[key]=value;
    }
    return clean;
  }

  function hasForbiddenEventData(input={}){
    if(!input||typeof input!=='object')return false;
    return Object.keys(input).some(key=>forbiddenEventKeys.includes(key)||hasForbiddenEventData(input[key]));
  }

  return {
    schemaVersion,
    confidenceMinimumScore,
    verificationMaxAgeDays,
    assessExistingProduct,
    affiliateEligibility,
    decisionQuality,
    sanitizeEvent,
    hasForbiddenEventData,
    ageDays,
    normalizeExisting
  };
});
