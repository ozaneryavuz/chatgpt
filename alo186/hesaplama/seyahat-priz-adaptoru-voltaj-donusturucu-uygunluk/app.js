'use strict';

function truthy(value){return value===true||value==='true'||value==='on';}
function evaluate(data){
  const destV=Number(data.destV||0),minV=Number(data.minV||0),maxV=Number(data.maxV||0),powerW=Number(data.powerW||0);
  const adapterA=Number(data.adapterA||0),adapterW=Number(data.adapterW||0);
  const confirmations=truthy(data.confirmNeed)&&truthy(data.confirmSpecs)&&truthy(data.confirmAffiliate);
  const currentA=destV&&powerW?powerW/destV:0;
  if(truthy(data.damage)||['hot','loose'].includes(data.test)) return {status:'stop',affiliateAllowed:false,categories:[],reason:'damage'};
  if(data.deviceClass==='medical') return {status:'professional',affiliateAllowed:false,categories:[],reason:'medical'};
  if(!destV||!minV||!maxV||!powerW||minV>maxV||data.destHz==='unknown'||data.deviceHz==='unknown'||data.plugMatch==='unknown'||data.official!=='yes') return {status:'evidence',affiliateAllowed:false,categories:[],reason:'missing-evidence'};
  const voltageOK=destV>=minV&&destV<=maxV;
  const frequencyOK=data.deviceHz==='both'||data.deviceHz===data.destHz;
  if(!voltageOK||!frequencyOK) return {status:'stop',affiliateAllowed:false,categories:[],reason:'voltage-frequency-mismatch',currentA};
  if(data.deviceClass==='earthed'&&data.earth!=='yes') return {status:'stop',affiliateAllowed:false,categories:[],reason:'earth-missing',currentA};
  if(data.plugMatch==='yes') return {status:'no-buy',affiliateAllowed:false,categories:[],reason:'plug-already-matches',currentA};
  const existingRated=(adapterA>0&&adapterA>=currentA)||(adapterW>0&&adapterW>=powerW);
  if(data.existing==='adapter'&&existingRated&&data.test==='pass') return {status:'no-buy',affiliateAllowed:false,categories:[],reason:'existing-pass',currentA};
  if(data.existing==='genericConverter') return {status:'stop',affiliateAllowed:false,categories:[],reason:'generic-converter',currentA};
  return {status:'recommend',affiliateAllowed:confirmations,categories:['travel_adapter'],reason:'plug-only-gap',currentA};
}
module.exports={evaluate};
