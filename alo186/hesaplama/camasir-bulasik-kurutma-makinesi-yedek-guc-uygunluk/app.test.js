'use strict';
const assert=require('node:assert/strict');
const tool=require('./app.js');

const safe={
  emergency:false,scenario:'planning',applianceType:'washer',connection:'dedicated',waterDrain:'secure',supervised:'yes',
  powerEvidence:'nameplate',maxInputW:2200,explicitSurgeW:'',energyFormat:'per_100',energyKWh:52,cycleCount:1,otherW:0,
  sourceStatus:'none',sourceType:'power_station',sourceContinuousW:'',sourceSurgeW:'',sourceWh:'',waveform:'unknown',outputSpec:'unknown',directOutput:'unknown',loadTest:'untested'
};
const run=patch=>tool.evaluate({...safe,...patch});

const metrics=tool.calculations(safe);
assert.equal(metrics.requiredContinuousW,2640);
assert.equal(metrics.requiredSurgeW,4114);
assert.equal(metrics.energyPerCycleKWh,0.52);
assert.equal(metrics.cycleEnergyWh,520);
assert.equal(metrics.requiredWh,765);
assert.equal(metrics.surgeAssumed,true);

assert.equal(run({emergency:true}).status,'emergency');
assert.equal(run({powerEvidence:'energy_label_only'}).status,'evidence_required');
assert.match(run({powerEvidence:'energy_label_only'}).title,/Enerji etiketi/);
assert.equal(run({connection:'extension'}).status,'stop');
assert.equal(run({waterDrain:'risk'}).status,'stop');
assert.equal(run({supervised:'no'}).status,'stop');
assert.equal(run({applianceType:'industrial',connection:'hardwired'}).status,'professional');
assert.equal(run({applianceType:'resistance_dryer',maxInputW:2800,energyFormat:'per_cycle',energyKWh:3}).status,'professional');
assert.equal(run({applianceType:'washer_dryer',maxInputW:2500,energyFormat:'per_cycle',energyKWh:4.5}).status,'professional');
assert.equal(run({scenario:'active'}).status,'active_event');
assert.equal(run({maxInputW:'',energyKWh:''}).status,'evidence_required');

const enough=run({
  scenario:'existing',sourceStatus:'existing',sourceType:'power_station',sourceContinuousW:3000,sourceSurgeW:5000,sourceWh:1200,
  waveform:'pure',outputSpec:'confirmed',directOutput:'yes',loadTest:'success'
});
assert.equal(enough.status,'no_buy');
assert.equal(enough.commerceClosed,true);
assert.match(enough.title,/yeni ürün almayın/i);

const gap=run({
  scenario:'existing',sourceStatus:'existing',sourceType:'power_station',sourceContinuousW:1800,sourceSurgeW:2500,sourceWh:500,
  waveform:'pure',outputSpec:'confirmed',directOutput:'yes',loadTest:'success'
});
assert.equal(gap.status,'conditional');
assert.equal(gap.commerceClosed,false);
assert.deepEqual(gap.commerceCategories,['power_station']);
assert.ok(gap.issues.some(item=>item.includes('Sürekli güç')));

const planning=run({sourceStatus:'none',sourceType:'power_station'});
assert.equal(planning.status,'conditional');
assert.equal(planning.commerceClosed,false);
assert.deepEqual(planning.commerceCategories,['power_station']);

const heatPump=run({applianceType:'heat_pump_dryer',maxInputW:900,energyFormat:'per_cycle',energyKWh:1.5,sourceType:'power_station'});
assert.equal(heatPump.status,'conditional');
assert.equal(heatPump.metrics.requiredContinuousW,1080);
assert.equal(heatPump.metrics.requiredSurgeW,2376);
assert.equal(heatPump.metrics.requiredWh,2206);

const explicit=tool.calculations({...safe,explicitSurgeW:3200});
assert.equal(explicit.requiredSurgeW,3520);
assert.equal(explicit.surgeAssumed,false);

assert.equal(tool.ROUTE,'/hesaplama/camasir-bulasik-kurutma-makinesi-yedek-guc-uygunluk/');
console.log(JSON.stringify({
  ok:true,
  scenarios:16,
  continuousW:metrics.requiredContinuousW,
  surgeW:metrics.requiredSurgeW,
  requiredWh:metrics.requiredWh,
  energyLabelConverted:true,
  noBuy:true,
  emergencyCommerceClosed:true,
  activeOutageCommerceClosed:true
}));
