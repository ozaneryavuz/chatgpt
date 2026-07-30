'use strict';

const assert=require('node:assert/strict');
const api=require('./app.js');

const base={
  stage:'preparedness',boilerType:'gas',connectionType:'plug',labelW:105,peakW:0,targetHours:2,
  manualChecked:true,grounded:true,neutralEarthVerified:true,pressureOk:true,flueOk:true,coAlarm:true,
  existingType:'none',existingW:0,existingWh:0,existingTested:false,
  gasSmell:false,coSymptoms:false,electricalHazard:false,waterLeak:false
};

function run(overrides={}){return api.classify({...base,...overrides});}

let result=run({gasSmell:true});
assert.equal(result.state,'emergency');
assert.equal(result.commerceAllowed,false);
assert.equal(result.noBuy,true);
assert.equal(result.productNeeds.length,0);

result=run({coSymptoms:true});
assert.equal(result.state,'emergency');

result=run({electricalHazard:true});
assert.equal(result.state,'stop');
assert.equal(result.commerceAllowed,false);

result=run({boilerType:'electric',labelW:9000});
assert.equal(result.state,'professional');
assert.equal(result.commerceAllowed,false);

result=run({boilerType:'heat_pump',labelW:2500});
assert.equal(result.state,'professional');

result=run({boilerType:'unknown'});
assert.equal(result.state,'evidence');

result=run({labelW:0});
assert.equal(result.state,'evidence');

result=run({manualChecked:false});
assert.equal(result.state,'evidence');

result=run({connectionType:'fixed'});
assert.equal(result.state,'professional');
assert.equal(result.commerceAllowed,false);

result=run({neutralEarthVerified:false});
assert.equal(result.state,'professional');

result=run({existingType:'ups',existingW:500,existingWh:500,existingTested:false});
assert.equal(result.state,'test_first');
assert.equal(result.noBuy,true);

result=run({existingType:'ups',existingW:500,existingWh:500,existingTested:true});
assert.equal(result.state,'no_buy');
assert.equal(result.noBuy,true);
assert.equal(result.commerceAllowed,false);

result=run({stage:'active'});
assert.equal(result.state,'deferred');
assert.equal(result.commerceAllowed,false);
assert.equal(result.commerceDeferred,true);

result=run({targetHours:1});
assert.equal(result.state,'qualified');
assert.deepEqual(result.productNeeds,['ups']);
assert.equal(result.commerceAllowed,true);
assert.equal(result.metrics.designW,300);
assert.equal(result.metrics.designVA,500);
assert.equal(result.metrics.energyWh,170);

result=run({targetHours:2,coAlarm:false});
assert.equal(result.state,'qualified');
assert.deepEqual(result.productNeeds,['powerStation','coAlarm']);

result=run({targetHours:6});
assert.equal(result.state,'professional');
assert.equal(result.commerceAllowed,true);
assert.ok(result.productNeeds.includes('inverter'));

result=run({labelW:600,targetHours:2});
assert.equal(result.state,'professional');

const calendar=api.calendarText(new Date('2026-07-30T06:00:00Z'));
assert.match(calendar,/RRULE:FREQ=MONTHLY;COUNT=12/);
assert.match(calendar,/SUMMARY:Kombi yedek güç/);

const now=Date.parse('2026-07-30T06:00:00Z');
const records=[];
for(let i=0;i<15;i++)records.push({createdAt:now-i*1000,state:'qualified'});
assert.equal(api.prune(records,now).length,10);
assert.equal(api.prune([{createdAt:now-api.TTL-1}],now).length,0);

const source=require('node:fs').readFileSync(__filename.replace('app.test.js','app.js'),'utf8');
assert.doesNotMatch(source,/amazon\.(com|com\.tr)|priceCurrency|aggregateRating|availability|"@type"\s*:\s*"Offer"/i);

console.log(JSON.stringify({ok:true,scenarios:18,route:'/hesaplama/kombi-kesinti-yedek-guc-uygunluk/'},null,2));
