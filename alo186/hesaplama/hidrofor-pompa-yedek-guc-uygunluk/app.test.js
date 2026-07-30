'use strict';
const assert=require('node:assert/strict');
const app=require('./app.js');

const base={
  emergency:false,pumpType:'domestic',phase:'single',voltage:230,ratedCurrent:5,
  powerFactor:.8,startMethod:'direct',connection:'plug',otherLoadW:0,targetHours:2,
  environment:'dry',protection:'rated',sourceStatus:'none',sourceType:'auto',
  sourceContinuousW:'',sourceSurgeW:'',sourceWh:''
};

const calc=app.calculations(base);
assert.equal(calc.runningW,920);
assert.equal(calc.requiredContinuousW,1150);
assert.equal(calc.requiredSurgeW,6348);
assert.equal(calc.requiredWh,2705.9);

const defaultPf=app.calculations({...base,powerFactor:''});
assert.equal(defaultPf.pf,.8);
assert.equal(defaultPf.runningW,920);

assert.equal(app.evaluate({...base,emergency:true}).status,'emergency');
assert.equal(app.evaluate({...base,pumpType:'fire'}).status,'professional');
assert.equal(app.evaluate({...base,phase:'three',voltage:400}).status,'professional');
assert.equal(app.evaluate({...base,pumpType:'borehole'}).status,'professional');
assert.equal(app.evaluate({...base,connection:'fixed'}).status,'professional');
assert.equal(app.evaluate({...base,environment:'wet',protection:'not_rated'}).status,'stop');
assert.equal(app.evaluate({...base,environment:'wet',protection:'unknown',connection:'fixed',phase:'three',voltage:400}).status,'stop','Islak ortam durdurma kapısı profesyonel sınıflandırmadan önce çalışmalı.');
assert.equal(app.evaluate({...base,ratedCurrent:''}).status,'evidence_required');

const generatorResult=app.evaluate(base);
assert.equal(generatorResult.status,'conditional_purchase');
assert.deepEqual(generatorResult.commerceCategories,['generator']);

const powerStationResult=app.evaluate({...base,ratedCurrent:2,startMethod:'vfd',sourceType:'auto'});
assert.equal(powerStationResult.status,'conditional_purchase');
assert.deepEqual(powerStationResult.commerceCategories,['power_station']);

const inverterResult=app.evaluate({...base,ratedCurrent:2,startMethod:'soft',sourceType:'inverter'});
assert.deepEqual(inverterResult.commerceCategories,['inverter']);

const missingClass=app.evaluate({...base,sourceStatus:'existing',sourceType:'auto',sourceContinuousW:1500,sourceSurgeW:7000,sourceWh:5000});
assert.equal(missingClass.status,'evidence_required','Mevcut kaynak sınıfı seçilmeden no-buy sonucu üretilemez.');
assert(missingClass.issues.some(item=>item.includes('Mevcut kaynağın sınıfını doğrulayın')));

const blankExisting=app.evaluate({...base,sourceStatus:'existing',sourceType:'generator',sourceContinuousW:'',sourceSurgeW:' '});
assert.equal(blankExisting.status,'evidence_required','Boş sayısal alanlar sıfır kabul edilmemeli.');

const batteryMissingWh=app.evaluate({...base,sourceStatus:'existing',sourceType:'power_station',sourceContinuousW:7000,sourceSurgeW:7000,sourceWh:''});
assert.equal(batteryMissingWh.status,'evidence_required','Bataryalı kaynakta Wh zorunlu olmalı.');

const generatorNoBuy=app.evaluate({...base,sourceStatus:'existing',sourceType:'generator',sourceContinuousW:1500,sourceSurgeW:7000});
assert.equal(generatorNoBuy.status,'no_buy');
assert.equal(generatorNoBuy.commerceClosed,true);
assert.match(generatorNoBuy.summary,/yakıt/);

const batteryNoBuy=app.evaluate({...base,sourceStatus:'existing',sourceType:'power_station',sourceContinuousW:1500,sourceSurgeW:7000,sourceWh:3000});
assert.equal(batteryNoBuy.status,'no_buy');

const weak=app.evaluate({...base,sourceStatus:'existing',sourceType:'generator',sourceContinuousW:500,sourceSurgeW:1000});
assert.equal(weak.status,'conditional_purchase');

const now=new Date('2026-07-30T12:00:00Z');
const record=app.createRecord(generatorResult,base,now);
assert.equal(record.reviewAt,'2026-10-28T12:00:00.000Z');
assert.equal(record.expiresAt,'2027-07-30T12:00:00.000Z');
assert.equal(record.input.pumpType,'domestic');
assert.equal(record.metrics.requiredSurgeW,6348);

const many=[];
for(let index=0;index<10;index+=1){
  many.push(app.normalizeRecord({
    id:`record-${index}`,
    createdAt:new Date(now.getTime()-index*86400000).toISOString(),
    status:'conditional_purchase',title:'Pompa teknik sonucu',metrics:calc,input:base
  },now));
}
many.push(app.normalizeRecord({id:'expired',createdAt:'2025-01-01T00:00:00Z',status:'old',title:'Eski kayıt'},new Date('2025-01-01T00:00:00Z')));
const purged=app.purgeRecords(many,now);
assert.equal(purged.length,8);
assert.equal(purged[0].id,'record-0');
assert(!purged.some(item=>item.id==='expired'));

const storageState=new Map([[app.constants.STORAGE_KEY,JSON.stringify([record,many.at(-1)])]]);
const fakeStorage={
  getItem:key=>storageState.has(key)?storageState.get(key):null,
  setItem:(key,value)=>storageState.set(key,value),
  removeItem:key=>storageState.delete(key)
};
const stored=app.loadStoredRecords(fakeStorage,now);
assert.equal(stored.length,1,'Süresi dolan kayıt yüklemede temizlenmeli.');
assert.equal(stored[0].id,record.id);
assert.equal(JSON.parse(storageState.get(app.constants.STORAGE_KEY)).length,1,'Temizlenmiş dizi persistent storage üzerine yazılmalı.');
app.loadStoredRecords(fakeStorage,new Date('2028-01-01T00:00:00Z'));
assert.equal(storageState.has(app.constants.STORAGE_KEY),false,'Bütün kayıtlar süresi dolduysa storage anahtarı kaldırılmalı.');

const payload=app.exportPayload(purged,now);
assert.equal(payload.schemaVersion,1);
assert.equal(payload.route,'/hesaplama/hidrofor-pompa-yedek-guc-uygunluk/');
assert.equal(payload.records.length,8);
assert(!JSON.stringify(payload).match(/email|phone|address|location/i));

const calendar=app.toIcs(record);
assert.match(calendar,/BEGIN:VCALENDAR/);
assert.match(calendar,/90 günlük kontrolü/);
assert.match(calendar,/hidrofor-pompa-yedek-guc-uygunluk/);

assert.equal(app.constants.START_MULTIPLIER.direct,6);
assert.equal(app.constants.START_MULTIPLIER.soft,3);
assert.equal(app.constants.START_MULTIPLIER.vfd,1.5);
assert.equal(app.constants.MAX_RECORDS,8);
assert.equal(app.constants.TTL_DAYS,365);
assert.equal(app.constants.REVIEW_DAYS,90);
assert(!Object.values(app.constants.CATEGORY_LINKS).some(item=>item.href.includes('amazon.')));

console.log(JSON.stringify({
  ok:true,
  scenarios:25,
  records:app.constants.MAX_RECORDS,
  reviewDays:app.constants.REVIEW_DAYS,
  route:'/hesaplama/hidrofor-pompa-yedek-guc-uygunluk/'
},null,2));
