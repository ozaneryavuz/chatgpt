'use strict';
const assert=require('node:assert/strict');
const {evaluate,DISTANCE_MIN_M}=require('./app.js');

const safeBase={
  emergency:false,
  placement:'open_outdoor',
  distanceM:7,
  exhaust:'away',
  weather:'dry',
  connection:'direct',
  cord:'outdoor_good',
  refuel:'cooled_outdoors',
  medical:false,
  coAlarm:'full',
  coShutoff:'yes',
  generatorStatus:'owned_sized',
  sizingCompleted:true
};

assert.equal(DISTANCE_MIN_M,6.1);
assert.equal(evaluate({...safeBase,emergency:true}).status,'emergency');
assert.equal(evaluate({...safeBase,placement:'indoor'}).status,'stop');
assert.equal(evaluate({...safeBase,placement:'garage_shed'}).status,'stop');
assert.equal(evaluate({...safeBase,placement:'porch_carport'}).status,'stop');
assert.equal(evaluate({...safeBase,distanceM:4}).status,'stop');
assert.equal(evaluate({...safeBase,distanceM:6}).status,'stop');
assert.equal(evaluate({...safeBase,exhaust:'toward'}).status,'stop');
assert.equal(evaluate({...safeBase,connection:'backfeed'}).status,'stop');
assert.equal(evaluate({...safeBase,weather:'wet'}).status,'stop');
assert.equal(evaluate({...safeBase,cord:'damaged'}).status,'stop');
assert.equal(evaluate({...safeBase,refuel:'hot_running'}).status,'stop');

const unknown=evaluate({...safeBase,distanceM:'',placement:'unknown'});
assert.equal(unknown.status,'evidence_required');
assert.equal(unknown.commerceClosed,true);

const noAlarm=evaluate({...safeBase,coAlarm:'none'});
assert.equal(noAlarm.status,'prerequisite');
assert.deepEqual(noAlarm.commerceCategories,['co_alarm']);
assert.equal(noAlarm.commerceClosed,false);

const badCord=evaluate({...safeBase,cord:'indoor_light'});
assert.equal(badCord.status,'prerequisite');
assert.deepEqual(badCord.commerceCategories,['extension_cord']);

const transfer=evaluate({...safeBase,connection:'transfer'});
assert.equal(transfer.status,'professional');
assert.equal(transfer.commerceClosed,true);

const medical=evaluate({...safeBase,medical:true});
assert.equal(medical.status,'professional');
assert.equal(medical.commerceClosed,true);

const existing=evaluate(safeBase);
assert.equal(existing.status,'no_buy');
assert.equal(existing.commerceCategories.length,0);
assert.equal(existing.commerceClosed,true);

const noGeneratorNoSizing=evaluate({...safeBase,generatorStatus:'none',sizingCompleted:false});
assert.equal(noGeneratorNoSizing.status,'evidence_required');
assert.deepEqual(noGeneratorNoSizing.toolKeys,['sizing']);

const purchase=evaluate({...safeBase,generatorStatus:'none',sizingCompleted:true});
assert.equal(purchase.status,'conditional_purchase');
assert.deepEqual(purchase.commerceCategories,['generator']);
assert.equal(purchase.commerceClosed,false);

const noCoShutoff=evaluate({...safeBase,coShutoff:'no'});
assert.equal(noCoShutoff.status,'no_buy');
assert(noCoShutoff.steps.some(item=>item.includes('CO otomatik durdurma')));

console.log(JSON.stringify({ok:true,scenarios:20,noBuy:true,emergencyCommerceClosed:true,affiliateRoutes:['generator','co_alarm','extension_cord']},null,2));
