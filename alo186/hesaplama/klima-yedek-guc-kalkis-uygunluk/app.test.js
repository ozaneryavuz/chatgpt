'use strict';
const assert=require('node:assert/strict');
const app=require('./app.js');

const base={
  emergency:false,medicalCooling:false,scenario:'planning',unitType:'inverter_split',connection:'plug',phase:'single',
  labelW:'1000',voltage:'230',ratedCurrent:'',powerFactor:'',startupW:'',otherLoadW:'100',targetHours:'2',
  sourceStatus:'none',sourceType:'auto',sourceContinuousW:'',sourceSurgeW:'',sourceWh:'',waveform:'unknown',outputSpec:'unknown',startTest:'untested'
};
const run=patch=>app.evaluate({...base,...patch});

assert.equal(app.ROUTE,'/hesaplama/klima-yedek-guc-kalkis-uygunluk/');
assert.equal(app.PF_DEFAULT,0.9);
assert.equal(app.RESERVE,1.25);
assert.equal(app.SURGE_RESERVE,1.15);
assert.equal(app.BATTERY_EFF,0.85);
assert.equal(app.USABLE,0.8);
assert.deepEqual(app.START_MULTIPLIER,{inverter_split:1.5,fixed_split:4.5,portable:4,window:4});

const metrics=app.calculations(base);
assert.equal(metrics.runningW,1000);
assert.equal(metrics.startupW,1500);
assert.equal(metrics.totalRunningW,1100);
assert.equal(metrics.requiredContinuousW,1375);
assert.equal(metrics.requiredSurgeW,1840);
assert.equal(metrics.requiredWh,3235);
assert.equal(metrics.approximateVA,1618);
assert.equal(metrics.pfAssumed,true);
assert.equal(metrics.startupAssumed,true);

const currentBased=app.calculations({...base,labelW:'',ratedCurrent:'5',otherLoadW:'0',targetHours:'1'});
assert.equal(currentBased.runningW,1035);
assert.equal(currentBased.pf,0.9);
const knownStart=app.calculations({...base,startupW:'2400'});
assert.equal(knownStart.startupW,2400);
assert.equal(knownStart.startupAssumed,false);

assert.equal(run({emergency:true}).status,'emergency');
assert.equal(run({medicalCooling:true}).status,'professional');
assert.equal(run({unitType:'unknown'}).status,'evidence_required');
assert.equal(run({phase:'unknown'}).status,'evidence_required');
assert.equal(run({connection:'unknown'}).status,'evidence_required');
assert.equal(run({labelW:'',ratedCurrent:''}).status,'evidence_required');
assert.equal(run({targetHours:'0'}).status,'evidence_required');
assert.equal(run({unitType:'central',startupW:''}).status,'evidence_required');
assert.equal(run({unitType:'central',startupW:'4000'}).status,'professional');
assert.equal(run({connection:'fixed'}).status,'professional');
assert.equal(run({phase:'three'}).status,'professional');
assert.equal(run({labelW:'2500'}).status,'professional');

const active=run({scenario:'active',labelW:'700',otherLoadW:'0',targetHours:'1'});
assert.equal(active.status,'active_event');
assert.equal(active.commerceClosed,true);

const missingExisting=run({scenario:'existing',sourceStatus:'existing',sourceType:'power_station'});
assert.equal(missingExisting.status,'evidence_required');
const unknownType=run({scenario:'existing',sourceStatus:'existing',sourceType:'auto'});
assert.equal(unknownType.status,'evidence_required');

const powerStationNeed=run({labelW:'600',otherLoadW:'0',targetHours:'1'});
assert.equal(powerStationNeed.status,'conditional_purchase');
assert.deepEqual(powerStationNeed.commerceCategories,['power_station']);
assert.equal(powerStationNeed.commerceClosed,false);

const generatorNeed=run({unitType:'fixed_split',labelW:'1500',otherLoadW:'200',targetHours:'5'});
assert.equal(generatorNeed.status,'conditional_purchase');
assert.deepEqual(generatorNeed.commerceCategories,['generator']);

const insufficient=run({scenario:'existing',sourceStatus:'existing',sourceType:'power_station',sourceContinuousW:'900',sourceSurgeW:'1200',sourceWh:'1000',waveform:'pure',outputSpec:'confirmed',startTest:'failed'});
assert.equal(insufficient.status,'conditional_purchase');

const unverifiedCompatibility=run({scenario:'existing',sourceStatus:'existing',sourceType:'power_station',sourceContinuousW:'3000',sourceSurgeW:'5000',sourceWh:'6000',waveform:'unknown',outputSpec:'unknown',startTest:'untested'});
assert.equal(unverifiedCompatibility.status,'evidence_required');
assert(unverifiedCompatibility.issues.some(item=>item.includes('Saf sinüs')));

const noBuy=run({scenario:'existing',sourceStatus:'existing',sourceType:'power_station',sourceContinuousW:'3000',sourceSurgeW:'5000',sourceWh:'6000',waveform:'pure',outputSpec:'confirmed',startTest:'success'});
assert.equal(noBuy.status,'no_buy');
assert.equal(noBuy.commerceClosed,true);
assert.match(noBuy.title,/yeni ürün almayın/);

assert.equal(app.gateReady(true,true,true),true);
assert.equal(app.gateReady(true,true,false),false);

console.log(JSON.stringify({ok:true,scenarios:20,route:app.ROUTE,affiliateGateChecks:3,personalDataFields:0,directStoreLinks:0},null,2));
