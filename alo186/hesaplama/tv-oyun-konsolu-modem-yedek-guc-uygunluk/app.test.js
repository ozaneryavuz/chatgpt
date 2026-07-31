'use strict';
const assert=require('node:assert/strict');
const {calculate,decide,ROUTE,PRODUCT_ROUTES}=require('./app.js');

assert.equal(ROUTE,'/hesaplama/tv-oyun-konsolu-modem-yedek-guc-uygunluk/');
assert.equal(PRODUCT_ROUTES.ups,'/akilli-urun-secimi?intent=tv-konsol-ups');

const base={
  emergency:false,scenario:'planning',loadClass:'living_room',continuity:'no_restart',
  connection:'direct',ventilation:'open',tvW:120,consoleW:220,networkW:25,audioW:60,mediaW:20,otherW:0,
  targetHours:2,loadEvidence:'measured',sourceStatus:'none',sourceType:'ups',
  sourceW:0,sourceVA:0,sourceWh:0,waveform:'unknown',transferTest:'untested',runtimeTest:'untested'
};
assert.deepEqual(calculate(base),{totalW:445,requiredW:560,requiredVA:800,requiredWh:1310,targetHours:2});
assert.equal(decide({...base,emergency:true}).code,'emergency');
assert.equal(decide({...base,loadClass:'medical'}).code,'medical');
assert.equal(decide({...base,loadClass:'pc_nas'}).code,'pc_nas');
assert.equal(decide({...base,loadClass:'high_power'}).code,'high_power');
assert.equal(decide({...base,connection:'daisy'}).code,'daisy_chain');
assert.equal(decide({...base,ventilation:'blocked'}).code,'ventilation');
assert.equal(decide({...base,tvW:0,consoleW:0,networkW:0,audioW:0,mediaW:0,targetHours:0}).code,'missing_load');
assert.equal(decide({...base,loadEvidence:'estimated'}).code,'evidence');
assert.equal(decide({...base,scenario:'active'}).code,'active_outage');
assert.equal(decide({...base,continuity:'restart_ok'}).code,'power_station');
assert.equal(decide(base).code,'ups');
const existing={...base,sourceStatus:'existing',sourceW:600,sourceVA:1000,sourceWh:1500,waveform:'approved',transferTest:'success',runtimeTest:'success'};
assert.equal(decide(existing).code,'no_buy');
assert.equal(decide({...existing,transferTest:'restart'}).code,'transfer_fail');
assert.equal(decide({...existing,sourceWh:500}).code,'ups');
console.log(JSON.stringify({ok:true,scenarios:14,calculation:true,noBuy:true,activeOutageClosed:true}));
