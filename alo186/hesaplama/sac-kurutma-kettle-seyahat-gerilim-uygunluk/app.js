'use strict';

function truthy(value){return value===true||value==='true'||value==='on';}
function evaluate(data){
  const powerW=Number(data.powerW||0),minV=Number(data.minV||0),maxV=Number(data.maxV||0),destV=Number(data.destV||0);
  const adapterA=Number(data.adapterA||0),adapterW=Number(data.adapterW||0);
  const currentA=destV&&powerW?powerW/destV:0;
  const highHeat=['dryer','kettle','iron'].includes(data.device);
  const confirmations=truthy(data.confirmNeed)&&truthy(data.confirmSpecs)&&truthy(data.confirmAffiliate);
  if(truthy(data.damage)||['hot','trip'].includes(data.test)) return {status:'stop',affiliateAllowed:false,categories:[],reason:'damage'};
  if(data.place==='bathroom'||(data.place==='shaverSocket'&&data.device!=='shaver')) return {status:'stop',affiliateAllowed:false,categories:[],reason:'place'};
  if(!powerW||!minV||!maxV||!destV||minV>maxV||data.deviceHz==='unknown'||data.destHz==='unknown'||data.plugMatch==='unknown'||data.official!=='yes'||data.selector==='unknown') return {status:'evidence',affiliateAllowed:false,categories:[],reason:'missing-evidence'};
  if(data.selector==='wrong') return {status:'stop',affiliateAllowed:false,categories:[],reason:'selector'};
  const voltageOK=destV>=minV&&destV<=maxV;
  const frequencyOK=data.deviceHz==='both'||data.deviceHz===data.destHz;
  if(!voltageOK||!frequencyOK) return {status:'stop',affiliateAllowed:false,categories:[],reason:'voltage-frequency-mismatch',currentA};
  if(data.plugMatch==='yes') return {status:'no-buy',affiliateAllowed:false,categories:[],reason:'plug-already-matches',currentA};
  if(highHeat&&powerW>1000) return {status:'professional',affiliateAllowed:false,categories:[],reason:'high-power',currentA};
  const rated=data.adapter==='rated'&&((adapterA>0&&adapterA>=currentA)||(adapterW>0&&adapterW>=powerW));
  if(rated&&data.test==='pass') return {status:'no-buy',affiliateAllowed:false,categories:[],reason:'existing-pass',currentA};
  if(data.adapter==='unknown') return {status:'stop',affiliateAllowed:false,categories:[],reason:'unknown-adapter',currentA};
  return {status:'recommend',affiliateAllowed:confirmations,categories:['travel_adapter'],reason:'plug-only-gap',currentA};
}
module.exports={evaluate};
