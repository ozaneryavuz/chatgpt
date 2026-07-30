'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const api=require('./app.js');

const base={
  scenario:'planning',applianceType:'gas_boiler',connection:'plug',gasAvailable:'yes',lockout:'no',
  manufacturerApproval:'yes',transferNeed:'short_break_ok',labelW:150,voltage:230,ratedCurrent:'',powerFactor:'',
  startupW:300,otherLoadW:20,loadFactorPct:70,targetHours:2,sourceStatus:'none',waveform:'unknown',
  outputSpec:'unknown',startTest:'untested'
};

let result=api.calculate({...base,emergencyGas:true});
assert.equal(result.status,'emergency_gas');
assert.equal(result.commerceAllowed,false);
assert.match(result.summary,/187/);
assert.match(result.summary,/112/);

result=api.calculate({...base,electricalHazard:true});
assert.equal(result.status,'emergency_electrical');
assert.equal(result.commerceAllowed,false);

result=api.calculate({...base,gasAvailable:'no'});
assert.equal(result.status,'no_electrical_solution');
assert.equal(result.commerceAllowed,false);
assert.match(result.title,/Gaz beslemesi yoksa/);

result=api.calculate({...base,lockout:'yes'});
assert.equal(result.status,'service_required');
assert.equal(result.commerceAllowed,false);

result=api.calculate({...base,applianceType:'electric_boiler'});
assert.equal(result.status,'professional');
assert.equal(result.commerceAllowed,false);

result=api.calculate({...base,manufacturerApproval:'unknown'});
assert.equal(result.status,'needs_evidence');
assert.equal(result.commerceAllowed,false);
assert.ok(result.reasons.some((item)=>/Üretici/.test(item)));

result=api.calculate({...base,connection:'fixed'});
assert.equal(result.status,'professional');
assert.equal(result.commerceAllowed,false);

result=api.calculate({...base,sourceStatus:'existing',sourceContinuousW:300,sourceSurgeW:500,sourceWh:1000,waveform:'pure',outputSpec:'confirmed',startTest:'success'});
assert.equal(result.status,'no_buy');
assert.equal(result.commerceAllowed,false);
assert.match(result.title,/yeni ürün almayın/i);
assert.equal(result.requirements.continuousW,220);
assert.equal(result.requirements.surgeW,370);
assert.equal(result.requirements.energyWh,430);

result=api.calculate({...base,scenario:'active'});
assert.equal(result.status,'active_event');
assert.equal(result.commerceAllowed,false);
assert.match(result.title,/Aktif kesintide/);

result=api.calculate({...base,transferNeed:'no_break'});
assert.equal(result.status,'qualified_gap');
assert.equal(result.commerceAllowed,true);
assert.equal(result.productCategory,'ups');
assert.match(result.affiliateDisclosure,/Amazon satış ortaklığı/);

result=api.calculate({...base,transferNeed:'short_break_ok'});
assert.equal(result.status,'qualified_gap');
assert.equal(result.productCategory,'power_station');

result=api.calculate({...base,targetHours:6});
assert.equal(result.status,'professional');
assert.equal(result.commerceAllowed,false);

result=api.calculate({...base,labelW:'',ratedCurrent:1,powerFactor:0.8,voltage:230});
assert.equal(result.requirements.baseW,184);
assert.equal(result.status,'qualified_gap');

const ics=api.buildIcs(result,new Date('2026-07-30T07:00:00Z'));
assert.match(ics,/BEGIN:VCALENDAR/);
assert.match(ics,/Kombi yedek güç ve güvenlik yeniden testi/);
assert.match(ics,/Fiyat veya kampanya kontrolü değildir/);

const source=fs.readFileSync(path.join(__dirname,'app.js'),'utf8');
for(const forbidden of ['amazon.com.tr/','localStorage','sessionStorage','fetch(','XMLHttpRequest','navigator.geolocation']){
  assert.equal(source.includes(forbidden),false,`Yasak ifade: ${forbidden}`);
}
console.log('Kombi elektrik kesintisi yedek güç karar motoru testleri başarılı.');
