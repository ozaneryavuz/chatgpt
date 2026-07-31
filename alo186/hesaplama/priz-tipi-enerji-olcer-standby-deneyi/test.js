'use strict';
const assert=require('node:assert/strict');
const app=require('./app.js');

const base={device:'tv',days:7,safePlug:true,excludedLoad:false,existingMeter:false,networkNeeded:false,activeW:100,standbyW:2,activeHours:4,offHours:8,confirmNeed:false,confirmSafe:false,confirmAffiliate:false,emergency:false};
const metrics=app.calculate(base);
assert.equal(metrics.activeKwhDay,0.4);
assert.ok(Math.abs(metrics.standbyKwhMonth-1.2)<0.001);
assert.equal(app.decide({...base,emergency:true}).code,'emergency');
assert.equal(app.decide({...base,excludedLoad:true}).code,'excluded');
assert.equal(app.decide({...base,existingMeter:true}).code,'no_buy');
assert.equal(app.decide({...base,activeW:0,standbyW:0}).code,'measure_first');
const qualified=app.decide({...base,activeW:0,standbyW:0,confirmNeed:true,confirmSafe:true,confirmAffiliate:true});
assert.equal(qualified.code,'qualified_meter');
assert.equal(qualified.commerce,true);
assert.ok(app.calendar(7).includes('BEGIN:VCALENDAR'));
console.log(JSON.stringify({ok:true,route:app.ROUTE,standby:true,noBuy:true,affiliateGate:true}));