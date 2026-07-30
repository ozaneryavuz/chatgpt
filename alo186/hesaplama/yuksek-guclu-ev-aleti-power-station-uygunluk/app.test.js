'use strict';
const assert=require('node:assert/strict');
const {evaluate}=require('./app.js');

function base(overrides={}){
  return {
    scenario:'planning', applianceType:'kettle', condition:'normal', exactModelVerified:'yes',
    powerEvidence:'input_label', ratedInputW:1800, useMinutes:5, sessions:3,
    simultaneousLoads:'one', surgeKnown:'no', directConnection:'direct',
    outletGrounding:'verified', ventilation:'clear', unattendedUse:'no', sourceStatus:'none',
    ...overrides
  };
}

{ const r=evaluate(base({emergency:true})); assert.equal(r.status,'emergency'); assert.equal(r.commercial.allowed,false); }
{ const r=evaluate(base({applianceType:'induction_hob'})); assert.equal(r.status,'professional'); }
{ const r=evaluate(base({unattendedUse:'yes'})); assert.equal(r.status,'unsafe_use'); }
{ const r=evaluate(base({ratedInputW:''})); assert.equal(r.status,'incomplete'); }
{ const r=evaluate(base({applianceType:'microwave',powerEvidence:'output_rating'})); assert.equal(r.status,'needs_evidence'); assert.match(r.warnings.join(' '),/pişirme\/çıkış wattı/); }
{ const r=evaluate(base({applianceType:'coffee_machine',surgeKnown:'no'})); assert.equal(r.status,'needs_evidence'); }
{ const r=evaluate(base({directConnection:'extension'})); assert.equal(r.status,'needs_evidence'); }
{ const r=evaluate(base({sourceStatus:'existing',sourceContinuousW:2400,sourceSurgeW:3000,sourceWh:1000,sourcePureSine:'yes',sourceGroundedOutput:'verified',controlledTest:'success'})); assert.equal(r.status,'no_buy'); assert.equal(r.commercial.allowed,false); }
{ const r=evaluate(base({sourceStatus:'existing',sourceContinuousW:2400,sourceSurgeW:3000,sourceWh:1000,sourcePureSine:'yes',sourceGroundedOutput:'verified',controlledTest:'untested'})); assert.equal(r.status,'test_first'); }
{ const r=evaluate(base({sourceStatus:'existing',sourceContinuousW:1200,sourceSurgeW:1500,sourceWh:300,sourcePureSine:'yes',sourceGroundedOutput:'verified',controlledTest:'failed'})); assert.equal(r.status,'capacity_gap'); assert.equal(r.commercial.allowed,true); assert.match(r.commercial.url,/tasinabilir-guc-istasyonu-secimi/); }
{ const r=evaluate(base({scenario:'active'})); assert.equal(r.status,'active_outage'); assert.equal(r.commercial.allowed,false); }
{ const r=evaluate(base()); assert.equal(r.status,'capacity_gap'); assert.equal(r.metrics.continuousW,2100); assert.equal(r.metrics.energyPerUseWh,150); assert.equal(r.metrics.requiredNominalWh,600); }
{ const r=evaluate(base({applianceType:'microwave',ratedInputW:1400,useMinutes:10,sessions:2,surgeKnown:'yes',surgeW:2200})); assert.equal(r.status,'capacity_gap'); assert.equal(r.metrics.surgeW,2200); }

console.log(JSON.stringify({ok:true,scenarios:12,module:'high-power-appliance-power-station'}));
