'use strict';

const assert=require('node:assert/strict');
const tool=require('./app.js');

function input(overrides={}){
  return {stage:'preparedness',appliance:'fridge',hours:0,doorsClosed:true,thermometer:true,cooler:true,gelPacks:true,fridgeTemp:'',freezerTemp:'',iceCrystals:'unknown',electricalHazard:false,floodContact:false,...overrides};
}

let result=tool.classify(input());
assert.equal(result.noBuy,true);
assert.equal(result.commerceAllowed,false);
assert.deepEqual(result.productNeeds,[]);

result=tool.classify(input({thermometer:false,cooler:false,gelPacks:false}));
assert.equal(result.commerceAllowed,true);
assert.deepEqual(result.productNeeds,['thermometer','cooler']);

result=tool.classify(input({stage:'active',hours:3,thermometer:false,cooler:false,gelPacks:false}));
assert.equal(result.fridgeStatus,'within_time_guide');
assert.equal(result.commerceAllowed,false);
assert.equal(result.commerceDeferred,true);
assert.equal(result.noBuy,true);

result=tool.classify(input({stage:'active',hours:5}));
assert.equal(result.fridgeStatus,'evidence_needed');
assert.equal(result.severity,'warn');

result=tool.classify(input({stage:'active',appliance:'freezer_full',hours:36}));
assert.equal(result.freezerStatus,'within_time_guide');

result=tool.classify(input({stage:'active',appliance:'freezer_half',hours:30}));
assert.equal(result.freezerStatus,'evidence_needed');
assert.equal(result.severity,'warn');

result=tool.classify(input({stage:'active',appliance:'both',hours:30}));
assert.equal(result.fridgeStatus,'evidence_needed');
assert.equal(result.freezerStatus,'evidence_needed');
assert.equal(result.severity,'warn');

result=tool.classify(input({stage:'restored',appliance:'freezer_full',hours:20,freezerTemp:3.5}));
assert.equal(result.freezerStatus,'cold_evidence_present');

result=tool.classify(input({stage:'restored',appliance:'freezer_full',hours:20,iceCrystals:'yes'}));
assert.equal(result.freezerStatus,'cold_evidence_present');

result=tool.classify(input({stage:'active',hours:1,electricalHazard:true,thermometer:false}));
assert.equal(result.severity,'bad');
assert.equal(result.commerceAllowed,false);
assert.deepEqual(result.productNeeds,[]);

result=tool.classify(input({stage:'restored',floodContact:true,cooler:false}));
assert.equal(result.severity,'bad');
assert.equal(result.commerceAllowed,false);

assert.match(tool.amazonSearchUrl('termometre'),/amazon\.com\.tr\/s\?k=/);
assert.match(tool.amazonSearchUrl('termometre'),/tag=alo186rehber-21/);

const start=new Date('2026-08-06T06:00:00.000Z');
const calendar=tool.calendarText(start);
assert.match(calendar,/RRULE:FREQ=WEEKLY;COUNT=12/);
assert.match(calendar,/SUMMARY:Buzdolabı ve dondurucu sıcaklık kontrolü/);

const now=Date.parse('2026-07-30T03:00:00.000Z');
const records=Array.from({length:12},(_,index)=>({createdAt:now-index*1000,id:index}));
assert.equal(tool.prune(records,now).length,8);
assert.equal(tool.prune([{createdAt:now-tool.TTL-1}],now).length,0);
assert.equal(tool.LIMIT,8);
assert.equal(tool.TTL,365*86400000);

console.log(JSON.stringify({ok:true,scenarios:11,affiliateTag:tool.AFFILIATE_TAG,recordLimit:tool.LIMIT,ttlDays:365,combinedFreezerThresholdHours:24},null,2));
