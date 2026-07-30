'use strict';
const assert=require('assert');
const {calculate,metrics,amazonUrl,ics}=require('./app.js');

const valid=overrides=>({
  emergency:false,condition:'sound',installation:'plug_in_low_voltage',stripMode:'constant_voltage',
  labelVerified:'yes',stripVoltage:'24',wattsPerMeter:'14.4',lengthMeters:'5',reservePercent:'20',
  feedCount:'2',cableLengthM:'2',cableSectionMm2:'1.5',feedPlanVerified:'yes',
  environment:'dry',ipEvidence:'unknown',ventilation:'unknown',thermalMount:'verified',
  recallChecked:'yes',certification:'yes',psuVoltage:'24',psuW:'100',psuA:'4.5',
  controllerType:'none',controllerA:'',connectorA:'3',ownership:'candidate',fieldTest:'not_done',
  ...overrides
});

let r=calculate(valid());
assert.strictEqual(r.status,'qualified');
assert.strictEqual(r.loadW,72);
assert.strictEqual(r.loadA,3);
assert.strictEqual(r.requiredW,86.4);
assert.strictEqual(r.requiredA,3.6);
assert.strictEqual(r.currentPerFeedA,1.5);
assert.ok(r.voltageDropPct<3);

assert.strictEqual(calculate(valid({emergency:true})).status,'emergency');
for(const condition of ['burned','melted','wet','damaged','hot']){
  assert.strictEqual(calculate(valid({condition})).status,'stop_use');
}
assert.strictEqual(calculate(valid({condition:'unknown'})).status,'evidence_required');
for(const installation of ['fixed_mains','open_terminals','commercial','vehicle']){
  assert.strictEqual(calculate(valid({installation})).status,'professional');
}
assert.strictEqual(calculate(valid({installation:'unknown'})).status,'evidence_required');
assert.strictEqual(calculate(valid({stripMode:'constant_current'})).status,'professional');
assert.strictEqual(calculate(valid({stripMode:'unknown'})).status,'evidence_required');
assert.strictEqual(calculate(valid({labelVerified:'no'})).status,'evidence_required');
assert.strictEqual(calculate(valid({stripVoltage:'18'})).status,'evidence_required');
assert.strictEqual(calculate(valid({wattsPerMeter:''})).status,'evidence_required');
assert.strictEqual(calculate(valid({lengthMeters:'0'})).status,'evidence_required');
assert.strictEqual(calculate(valid({reservePercent:'5'})).status,'evidence_required');
assert.strictEqual(calculate(valid({feedCount:'0'})).status,'evidence_required');
assert.strictEqual(calculate(valid({cableSectionMm2:''})).status,'evidence_required');

r=calculate(valid({stripVoltage:'5',wattsPerMeter:'18',lengthMeters:'5',feedCount:'1',cableLengthM:'4',cableSectionMm2:'0.5',psuVoltage:'5',psuW:'120',psuA:'24',connectorA:'30'}));
assert.strictEqual(r.status,'design_gap');
assert.ok(r.voltageDropPct>3);

assert.strictEqual(calculate(valid({feedPlanVerified:'no'})).status,'evidence_required');
assert.strictEqual(calculate(valid({environment:'wet_outdoor',ipEvidence:'no'})).status,'evidence_required');
assert.strictEqual(calculate(valid({environment:'enclosed',ventilation:'no'})).status,'stop_use');
assert.strictEqual(calculate(valid({environment:'unknown'})).status,'evidence_required');
assert.strictEqual(calculate(valid({thermalMount:'no'})).status,'evidence_required');
assert.strictEqual(calculate(valid({recallChecked:'recalled'})).status,'stop_use');
assert.strictEqual(calculate(valid({recallChecked:'unknown'})).status,'evidence_required');
assert.strictEqual(calculate(valid({certification:'no'})).status,'evidence_required');

r=calculate(valid({psuVoltage:'',psuW:'',psuA:''}));
assert.strictEqual(r.status,'replace_candidate');
assert.strictEqual(r.productClass,'power_supply');
assert.strictEqual(r.commercialAllowed,true);

assert.strictEqual(calculate(valid({psuVoltage:'12'})).status,'stop_use');

r=calculate(valid({psuW:'70',psuA:'3'}));
assert.strictEqual(r.status,'replace_candidate');
assert.strictEqual(r.productClass,'power_supply');

r=calculate(valid({controllerType:'rgb',controllerA:''}));
assert.strictEqual(r.status,'replace_candidate');
assert.strictEqual(r.productClass,'controller');

r=calculate(valid({controllerType:'rgb',controllerA:'3'}));
assert.strictEqual(r.status,'replace_candidate');
assert.strictEqual(r.productClass,'controller');

r=calculate(valid({connectorA:'1'}));
assert.strictEqual(r.status,'replace_candidate');
assert.strictEqual(r.productClass,'low_voltage_distribution');

assert.strictEqual(calculate(valid({ownership:'owned',fieldTest:'fail'})).status,'stop_use');
assert.strictEqual(calculate(valid({ownership:'owned',fieldTest:'not_done'})).status,'test_first');
assert.strictEqual(calculate(valid({ownership:'owned',fieldTest:'pass'})).status,'no_buy');

r=metrics(valid());
assert.strictEqual(r.loadW,72);
assert.strictEqual(r.requiredW,86.4);
assert.ok(r.voltageDropV>0);
assert.ok(amazonUrl('24V LED güç kaynağı').includes('alo186rehber-21'));
assert.ok(amazonUrl('test').includes('amazon.com.tr'));
assert.ok(ics({revisitDays:180}).includes('BEGIN:VCALENDAR'));
assert.ok(ics({revisitDays:180}).includes('Şerit LED'));

console.log(JSON.stringify({ok:true,scenarios:43,noBuy:true,affiliateTripleGate:true,revisitDays:180}));
