'use strict';
const assert=require('node:assert/strict');
const app=require('./app.js');
const base={danger:false,socketDamage:false,voltage:12,loadW:65,efficiencyPct:85,socketMaxA:10,inverterInputMaxA:15,inverterOutputW:150,loadClass:'electronics',connection:'accessory',manualVerified:true,socketLabelVerified:true,inverterLabelVerified:true,engineOff:false,runtimeMinutes:30,batteryEnergyVerified:false,existingSuitable:false,realLoadTest:false,noHeat:false,confirmNeed:false,confirmLabel:false,confirmAffiliate:false};
assert.ok(app.calculate(base).dcA>6.3);
assert.equal(app.decide({...base,loadClass:'heater'}).commerce,false);
assert.equal(app.decide({...base,existingSuitable:true,realLoadTest:true,noHeat:true}).code,'no_buy');
assert.equal(app.decide({...base,confirmNeed:true,confirmLabel:true,confirmAffiliate:true}).code,'eligible');
console.log(JSON.stringify({ok:true,route:app.ROUTE,noBuy:true,highPowerCommerce:false}));