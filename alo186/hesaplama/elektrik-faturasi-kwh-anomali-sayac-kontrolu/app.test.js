'use strict';
const assert=require('node:assert/strict');
const tool=require('./app.js');

function base(overrides={}){
  return {
    emergency:false,meterCondition:'normal',readingType:'actual',mainSwitchCheck:'index_stopped',
    currentDays:30,currentKwh:300,previousDays:30,previousKwh:200,
    occupancyChange:'same',weatherLoad:'no',newLoad:'no',existingMonitor:'none',
    intendedLoad:'electronic',directWall:'yes',earthRequired:'verified',featureNeed:'local_display',
    ...overrides
  };
}

let result=tool.evaluate(base({emergency:true}));
assert.equal(result.code,'official_check');
assert.equal(result.commercial.allowed,false);

result=tool.evaluate(base({meterCondition:'burned'}));
assert.equal(result.code,'official_check');
assert.match(result.warnings.join(' '),/alışveriş konusu değildir/);

result=tool.evaluate(base({currentDays:35,currentKwh:350,previousDays:25,previousKwh:250}));
assert.equal(result.metrics.currentDaily,10);
assert.equal(result.metrics.previousDaily,10);
assert.equal(result.code,'no_buy');

result=tool.evaluate(base({currentDays:40,currentKwh:400,previousDays:30,previousKwh:300}));
assert.equal(result.metrics.periodFlag,true);
assert.equal(result.code,'official_check');

result=tool.evaluate(base({currentKwh:300,previousIndex:1000,currentIndex:1250,multiplier:1}));
assert.equal(result.metrics.indexConsumption,250);
assert.ok(result.metrics.indexMismatchPct>5);
assert.equal(result.code,'official_check');

result=tool.evaluate(base({mainSwitchCheck:'index_continues'}));
assert.equal(result.code,'official_check');
assert.equal(result.commercial.allowed,false);

result=tool.evaluate(base({existingMonitor:'adequate'}));
assert.equal(result.code,'no_buy');
assert.match(result.actions.join(' '),/yeni ürün almayın/);

result=tool.evaluate(base({occupancyChange:'higher'}));
assert.equal(result.code,'explained');
assert.equal(result.commercial.allowed,false);

result=tool.evaluate(base({weatherLoad:'yes'}));
assert.equal(result.code,'explained');

result=tool.evaluate(base({intendedLoad:'motor_compressor'}));
assert.equal(result.code,'professional');
assert.equal(result.commercial.allowed,false);

result=tool.evaluate(base({intendedLoad:'ev_charging'}));
assert.equal(result.code,'professional');

result=tool.evaluate(base({directWall:'no'}));
assert.equal(result.code,'needs_evidence');
assert.equal(result.commercial.allowed,false);

result=tool.evaluate(base({earthRequired:'unknown'}));
assert.equal(result.code,'needs_evidence');

result=tool.evaluate(base({existingMonitor:'available'}));
assert.equal(result.code,'no_buy');

result=tool.evaluate(base());
assert.equal(result.code,'monitoring_gap');
assert.equal(result.commercial.allowed,true);
assert.equal(result.commercial.category,'plug_in_energy_meter');
assert.match(tool.affiliateUrl(result),/amazon\.com\.tr\/s\?k=/);
assert.match(tool.affiliateUrl(result),/tag=alo186rehber-21/);

result=tool.evaluate(base({featureNeed:'remote_control'}));
assert.equal(result.commercial.category,'energy_monitoring_smart_plug');

const report=tool.report(result);
assert.equal(report.commercialPolicy.pricePublished,false);
assert.equal(report.commercialPolicy.stockPublished,false);
assert.equal(report.commercialPolicy.ratingPublished,false);
assert.equal(report.commercialPolicy.sellerPublished,false);
assert.equal(report.commercialPolicy.warrantyPublished,false);
assert.equal(report.privacy.storage,false);
for(const forbidden of ['price','stock','rating','seller','warranty','address','subscriberNumber','meterSerial']){
  assert.ok(!JSON.stringify(result).toLowerCase().includes(`"${forbidden.toLowerCase()}":`));
}

const calendar=tool.ics(result,30);
assert.match(calendar,/BEGIN:VCALENDAR/);
assert.match(calendar,/kWh ve sayaç endeksi kontrolü/);
assert.match(calendar,/END:VCALENDAR/);

console.log(JSON.stringify({ok:true,scenarios:16,affiliateTag:tool.AFFILIATE_TAG,noBuy:true,officialFirst:true,priceStockRatingPublished:false}));
