'use strict';
const assert=require('node:assert/strict');
const app=require('./app.js');

const base={
  emergency:false,medicalStorage:false,scenario:'planning',applianceType:'fridge_freezer',connection:'plug',phase:'single',
  doorClosed:'yes',freezerFill:'half',outageHours:'',labelW:'180',voltage:'230',ratedCurrent:'',powerFactor:'',
  startupW:'',dutyCyclePct:'',otherLoadW:'20',targetHours:'8',sourceStatus:'none',sourceType:'auto',
  sourceContinuousW:'',sourceSurgeW:'',sourceWh:'',waveform:'unknown',outputSpec:'unknown',startTest:'untested'
};
const run=patch=>app.evaluate({...base,...patch});

assert.equal(app.ROUTE,'/hesaplama/buzdolabi-dondurucu-yedek-guc-uygunluk/');
assert.equal(app.PF_DEFAULT,0.85);
assert.equal(app.RESERVE,1.25);
assert.equal(app.SURGE_RESERVE,1.15);
assert.equal(app.BATTERY_EFF,0.85);
assert.equal(app.USABLE,0.8);
assert.deepEqual(app.START_MULTIPLIER,{fridge:3,fridge_freezer:3.5,upright_freezer:3.5,chest_freezer:3});
assert.deepEqual(app.DUTY_CYCLE_DEFAULT,{fridge:45,fridge_freezer:50,upright_freezer:50,chest_freezer:40});

const metrics=app.calculations(base);
assert.equal(metrics.runningW,180);
assert.equal(metrics.startupW,630);
assert.equal(metrics.dutyPct,50);
assert.equal(metrics.averageW,110);
assert.equal(metrics.totalRunningW,200);
assert.equal(metrics.requiredContinuousW,250);
assert.equal(metrics.requiredSurgeW,747);
assert.equal(metrics.requiredWh,1294);
assert.equal(metrics.approximateVA,313);
assert.equal(metrics.pfAssumed,true);
assert.equal(metrics.startupAssumed,true);
assert.equal(metrics.dutyAssumed,true);

const currentBased=app.calculations({...base,labelW:'',ratedCurrent:'1',otherLoadW:'0',targetHours:'4'});
assert.equal(currentBased.runningW,196);
assert.equal(currentBased.pf,0.85);
const known=app.calculations({...base,startupW:'900',dutyCyclePct:'60'});
assert.equal(known.startupW,900);
assert.equal(known.startupAssumed,false);
assert.equal(known.dutyPct,60);
assert.equal(known.dutyAssumed,false);

assert.equal(app.foodSafetyWindow({applianceType:'fridge',doorClosed:'yes'}).hours,4);
assert.equal(app.foodSafetyWindow({applianceType:'chest_freezer',doorClosed:'yes',freezerFill:'full'}).hours,48);
assert.equal(app.foodSafetyWindow({applianceType:'upright_freezer',doorClosed:'yes',freezerFill:'half'}).hours,24);
assert.equal(app.foodSafetyWindow({applianceType:'fridge',doorClosed:'no'}).hours,null);

assert.equal(run({emergency:true}).status,'emergency');
assert.equal(run({medicalStorage:true}).status,'professional');
assert.equal(run({applianceType:'unknown'}).status,'evidence_required');
assert.equal(run({phase:'unknown'}).status,'evidence_required');
assert.equal(run({connection:'unknown'}).status,'evidence_required');
assert.equal(run({doorClosed:'unknown'}).status,'evidence_required');
assert.equal(run({labelW:'',ratedCurrent:''}).status,'evidence_required');
assert.equal(run({targetHours:'0'}).status,'evidence_required');
assert.equal(run({applianceType:'commercial',startupW:''}).status,'evidence_required');
assert.equal(run({applianceType:'commercial',startupW:'2500',dutyCyclePct:'70'}).status,'professional');
assert.equal(run({connection:'fixed'}).status,'professional');
assert.equal(run({phase:'three'}).status,'professional');
assert.equal(run({labelW:'1800'}).status,'professional');

const active=run({scenario:'active',outageHours:'6'});
assert.equal(active.status,'active_event');
assert.equal(active.commerceClosed,true);
assert.equal(active.foodSafety.hours,24);

const missingExisting=run({scenario:'existing',sourceStatus:'existing',sourceType:'power_station'});
assert.equal(missingExisting.status,'evidence_required');
const unknownType=run({scenario:'existing',sourceStatus:'existing',sourceType:'auto'});
assert.equal(unknownType.status,'evidence_required');

const powerStationNeed=run({});
assert.equal(powerStationNeed.status,'conditional_purchase');
assert.deepEqual(powerStationNeed.commerceCategories,['power_station']);
assert.equal(powerStationNeed.commerceClosed,false);

const generatorNeed=run({labelW:'900',startupW:'4000',targetHours:'24'});
assert.equal(generatorNeed.status,'conditional_purchase');
assert.deepEqual(generatorNeed.commerceCategories,['generator']);

const unverifiedCompatibility=run({scenario:'existing',sourceStatus:'existing',sourceType:'power_station',sourceContinuousW:'1000',sourceSurgeW:'2000',sourceWh:'3000',waveform:'unknown',outputSpec:'unknown',startTest:'untested'});
assert.equal(unverifiedCompatibility.status,'evidence_required');
assert(unverifiedCompatibility.issues.some(item=>item.includes('Saf sinüs')));

const noBuy=run({scenario:'existing',sourceStatus:'existing',sourceType:'power_station',sourceContinuousW:'1000',sourceSurgeW:'2000',sourceWh:'3000',waveform:'pure',outputSpec:'confirmed',startTest:'success'});
assert.equal(noBuy.status,'no_buy');
assert.equal(noBuy.commerceClosed,true);
assert.match(noBuy.title,/yeni ürün almayın/);

assert.equal(app.gateReady(true,true,true),true);
assert.equal(app.gateReady(true,true,false),false);

console.log(JSON.stringify({ok:true,scenarios:25,route:app.ROUTE,affiliateGateChecks:3,personalDataFields:0,directStoreLinks:0,foodSafetyWindows:[4,24,48]},null,2));
