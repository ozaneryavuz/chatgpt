const assert=require('assert');
const {
  calculate,requiredClass,affiliateUrl,buildIcs,AFFILIATE_TAG
}=require('./app.js');

const base={
  emergency:false,competence:'general',exposure:'ordinary',siteType:'home',activeWork:'no',
  task:'spot',outputNeed:'single_temp',surface:'matte',trendNeed:'no',
  existingType:'none',condition:'unknown',resolution:'unknown',radiometric:'unknown',
  emissivity:'yes',measurementParams:'limited',focus:'fixed',reporting:'unknown',
  verification:'unknown',fieldTest:'unknown',recallChecked:'unknown'
};

const run=(patch)=>calculate({...base,...patch});

assert.equal(run({emergency:true}).status,'emergency');
assert.equal(run({condition:'damaged'}).status,'stop_use');
assert.equal(run({recallChecked:'recalled'}).status,'stop_use');
assert.equal(run({competence:'unknown'}).status,'evidence_required');
assert.equal(run({exposure:'energized_exposed',competence:'qualified'}).status,'professional');
assert.equal(run({activeWork:'yes',competence:'qualified'}).status,'professional');
assert.equal(run({task:'electrical',competence:'general',exposure:'closed'}).status,'professional');
assert.equal(run({task:'electrical',competence:'maintenance',exposure:'ir_window'}).status,'professional');
assert.equal(run({siteType:'industrial',task:'mechanical',competence:'maintenance'}).status,'professional');
assert.equal(run({task:'unknown'}).status,'evidence_required');
assert.equal(run({surface:'through_glass'}).status,'evidence_required');

const spot=run({});
assert.equal(spot.status,'conditional_purchase');
assert.equal(spot.productClass,'ir_thermometer');
assert.equal(spot.commercialAllowed,true);
assert.equal(requiredClass(base),'ir_thermometer');

const building=run({
  task:'building',outputNeed:'pattern',trendNeed:'yes',surface:'mixed',
  radiometric:'yes',emissivity:'yes',measurementParams:'yes',focus:'fixed',reporting:'yes'
});
assert.equal(building.status,'conditional_purchase');
assert.equal(building.productClass,'phone_thermal_camera');
assert.equal(building.commercialAllowed,true);

const electrical=run({
  competence:'qualified',exposure:'ir_window',siteType:'workshop',task:'electrical',
  outputNeed:'report',surface:'ir_window',trendNeed:'yes',radiometric:'yes',
  emissivity:'yes',measurementParams:'yes',focus:'manual',reporting:'yes'
});
assert.equal(electrical.status,'conditional_purchase');
assert.equal(electrical.productClass,'handheld_thermal_camera');
assert.equal(electrical.commercialAllowed,true);

const reflectiveGap=run({
  task:'building',outputNeed:'quantitative',trendNeed:'yes',surface:'reflective',
  radiometric:'yes',emissivity:'fixed',measurementParams:'yes',focus:'fixed'
});
assert.equal(reflectiveGap.status,'evidence_required');
assert.equal(reflectiveGap.commercialAllowed,false);

const noBuyIr=run({
  existingType:'ir_thermometer',condition:'sound',verification:'yes',fieldTest:'pass',
  recallChecked:'yes'
});
assert.equal(noBuyIr.status,'no_buy');
assert.equal(noBuyIr.commercialAllowed,false);

const noBuyCamera=run({
  task:'building',outputNeed:'report',trendNeed:'yes',surface:'mixed',
  existingType:'phone_camera',condition:'sound',resolution:'medium',
  radiometric:'yes',emissivity:'yes',measurementParams:'yes',focus:'fixed',
  reporting:'yes',verification:'yes',fieldTest:'pass',recallChecked:'yes'
});
assert.equal(noBuyCamera.status,'no_buy');

const verifyFirst=run({
  existingType:'ir_thermometer',condition:'sound',verification:'unknown',
  fieldTest:'unknown',recallChecked:'yes'
});
assert.equal(verifyFirst.status,'evidence_required');

const testFirst=run({
  existingType:'ir_thermometer',condition:'sound',verification:'yes',
  fieldTest:'unknown',recallChecked:'yes'
});
assert.equal(testFirst.status,'test_existing');

const failedCurrent=run({
  existingType:'ir_thermometer',condition:'sound',verification:'yes',
  fieldTest:'fail',recallChecked:'yes'
});
assert.equal(failedCurrent.status,'conditional_purchase');
assert.equal(failedCurrent.commercialAllowed,true);

const failedVerification=run({
  existingType:'ir_thermometer',condition:'sound',verification:'fail',
  fieldTest:'fail',recallChecked:'yes'
});
assert.equal(failedVerification.status,'stop_use');

const missingRecall=run({
  existingType:'ir_thermometer',condition:'sound',verification:'yes',
  fieldTest:'pass',recallChecked:'unknown'
});
assert.equal(missingRecall.status,'evidence_required');

const reportGap=run({
  task:'reporting',competence:'qualified',exposure:'closed',outputNeed:'report',
  trendNeed:'yes',surface:'matte',radiometric:'yes',emissivity:'yes',
  measurementParams:'yes',focus:'manual',reporting:'no'
});
assert.equal(reportGap.status,'evidence_required');

const url=affiliateUrl('radyometrik termal kamera');
assert(url.includes('amazon.com.tr'));
assert(url.includes(`tag=${AFFILIATE_TAG}`));
assert.equal(AFFILIATE_TAG,'alo186rehber-21');

const ics=buildIcs({revisitDays:90});
assert(ics.includes('BEGIN:VCALENDAR'));
assert(ics.includes('Fiyat veya kampanya takibi değildir'));
assert(ics.includes('Termal ölçüm güvenlik ve trend kontrolü'));

console.log(JSON.stringify({
  ok:true,scenarios:24,emergencyCommerceBlocked:true,
  professionalBoundary:true,noBuy:true,affiliateTripleGate:true,revisitDays:90
}));
