(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.Alo186DecisionShortlistCore=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const schemaVersion=1;
  const limit=3;
  const retentionDays=30;
  const forbiddenKeys=['name','fullName','email','phone','address','subscription','identity','plate','serialNumber','freeText'];
  const attributeLabels={
    capacityMah:'Kapasite (mAh)',energyWh:'Enerji (Wh)',maxOutputW:'Azami çıkış (W)',wireless:'Kablosuz şarj',usbCPorts:'USB-C portu',usbAPorts:'USB-A portu',display:'Ekran',
    outlets:'Priz sayısı',joules:'Enerji sönümleme (J)',maxCurrentA:'Azami akım (A)',maxPowerW:'Azami güç (W)',usbPorts:'USB portu',cableM:'Kablo (m)'
  };

  function nowIso(now=new Date()){return new Date(now).toISOString();}
  function expiresAt(now=new Date()){return new Date(new Date(now).getTime()+retentionDays*86400000).toISOString();}
  function safeText(value,max=280){return String(value??'').replace(/[<>]/g,'').trim().slice(0,max);}
  function safeNumber(value){const n=Number(value);return Number.isFinite(n)?n:null;}
  function safeBoolean(value){return typeof value==='boolean'?value:null;}
  function sanitizeAttributes(attributes={}){
    const result={};
    Object.keys(attributeLabels).forEach(key=>{
      if(!(key in attributes))return;
      const value=attributes[key];
      if(typeof value==='boolean')result[key]=safeBoolean(value);
      else result[key]=safeNumber(value);
    });
    return result;
  }
  function sanitizeSnapshot(input={},now=new Date()){
    const snapshot={
      schemaVersion,
      productId:safeText(input.productId,80),
      asin:safeText(input.asin,24),
      categoryId:safeText(input.categoryId,50),
      productName:safeText(input.productName,160),
      brand:safeText(input.brand,80),
      score:safeNumber(input.score),
      confidence:safeText(input.confidence,30),
      verifiedAt:safeText(input.verifiedAt,20),
      sourceNote:safeText(input.sourceNote,260),
      unknowns:Array.isArray(input.unknowns)?input.unknowns.map(x=>safeText(x,140)).filter(Boolean).slice(0,8):[],
      attributes:sanitizeAttributes(input.attributes),
      savedAt:nowIso(now),
      expiresAt:expiresAt(now)
    };
    if(!snapshot.productId||!snapshot.categoryId||!snapshot.productName)return null;
    return snapshot;
  }
  function hasForbiddenData(value){
    if(!value||typeof value!=='object')return false;
    return Object.keys(value).some(key=>forbiddenKeys.includes(key)||hasForbiddenData(value[key]));
  }
  function normalizeVault(raw,now=new Date()){
    const parsed=Array.isArray(raw)?raw:[];
    const current=new Date(now).getTime();
    const clean=[];
    const seen=new Set();
    for(const item of parsed){
      if(!item||item.schemaVersion!==schemaVersion||!item.productId||!item.categoryId||!item.productName)continue;
      if(hasForbiddenData(item))continue;
      const expiry=new Date(item.expiresAt).getTime();
      if(!Number.isFinite(expiry)||expiry<=current||seen.has(item.productId))continue;
      seen.add(item.productId);
      clean.push(item);
      if(clean.length===limit)break;
    }
    return clean;
  }
  function upsert(vault,snapshot){
    if(!snapshot)return normalizeVault(vault);
    return [snapshot,...normalizeVault(vault).filter(item=>item.productId!==snapshot.productId)].slice(0,limit);
  }
  function remove(vault,productId){return normalizeVault(vault).filter(item=>item.productId!==productId);}
  function gateAllowed(state={}){return Boolean(state.needConfirmed&&state.technicalConfirmed&&state.affiliateConfirmed);}
  function formatValue(key,value){
    if(value===null||value===undefined)return 'Bilinmiyor';
    if(typeof value==='boolean')return value?'Var':'Yok';
    return new Intl.NumberFormat('tr-TR',{maximumFractionDigits:2}).format(value);
  }
  function comparisonRows(vault){
    const items=normalizeVault(vault);
    const keys=[...new Set(items.flatMap(item=>Object.keys(item.attributes||{})))];
    return keys.map(key=>({key,label:attributeLabels[key]||key,values:items.map(item=>formatValue(key,item.attributes?.[key]))}));
  }
  function daysUntilExpiry(item,now=new Date()){
    const diff=new Date(item?.expiresAt).getTime()-new Date(now).getTime();
    return Number.isFinite(diff)?Math.max(0,Math.ceil(diff/86400000)):0;
  }

  return {schemaVersion,limit,retentionDays,attributeLabels,sanitizeSnapshot,normalizeVault,upsert,remove,gateAllowed,comparisonRows,daysUntilExpiry,hasForbiddenData};
});
