'use strict';
const assert=require('node:assert/strict');
const app=require('./app.js');

const base={currentKwh:300,currentDays:30,previousKwh:200,previousDays:30,seasonal:false,newDevice:false,occupancy:false,supplierIssue:false,existingMeter:false,lowRiskPlugLoads:true,emergency:false,meterPhysical:false};
const metrics=app.metrics(base);
assert.equal(metrics.currentDaily,10);
assert.ok(metrics.changePct>49&&metrics.changePct<51);
assert.equal(app.decide({...base,emergency:true}).code,'emergency');
assert.equal(app.decide({...base,meterPhysical:true}).code,'meter_physical');
assert.equal(app.decide({...base,currentKwh:205}).code,'stable');
assert.equal(app.decide({...base,existingMeter:true}).code,'use_existing');
assert.equal(app.decide(base).code,'measure_plug_loads');
assert.equal(app.report(base).route,app.ROUTE);
console.log(JSON.stringify({ok:true,route:app.ROUTE,kwhPerDay:true,noBuy:true}));