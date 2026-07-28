const assert=require('assert');
const store=require('../sureklilik-paneli/store.js');

let state=store.createState();
assert.strictEqual(state.schemaVersion,2);
assert.strictEqual(store.metrics(state).locations,0);
assert(Array.isArray(state.improvementActions));
assert(Array.isArray(state.maturityImports));

state=store.configureOrganization(state,{name:'Test Oteli',profile:'hotel'});
assert.strictEqual(state.organization.name,'Test Oteli');
assert.strictEqual(state.organization.profile,'hotel');

let result=store.addLocation(state,{name:'Ana Otel',province:'Muğla',district:'Marmaris',type:'hotel',capacity:100});
state=result.state;const location=result.location;
assert.strictEqual(state.locations.length,1);
assert.throws(()=>store.addLocation(state,{name:''}),/Lokasyon adı zorunludur/);

result=store.addCriticalLoad(state,{locationId:location.id,name:'Soğuk oda',category:'cold',powerKw:18,priority:'P1',requiredAutonomyMin:15,backupSource:'generator',owner:'Mutfak'});
state=result.state;const load=result.load;
assert.strictEqual(load.priority,'P1');
assert.strictEqual(store.metrics(state).p1Loads,1);
assert.throws(()=>store.addCriticalLoad(state,{locationId:'yok',name:'Test'}),/Geçerli lokasyon/);

result=store.addAsset(state,{locationId:location.id,type:'generator',name:'Ana jeneratör',ratedPowerKva:630,testIntervalDays:7});
state=result.state;const asset=result.asset;
assert.strictEqual(store.metrics(state).overdueAssets,1,'Test yapılmamış varlık gecikmiş sayılmalı.');

result=store.recordTest(state,{assetId:asset.id,status:'passed',runtimeMin:20,fuelPercent:80,transferObserved:true,notes:'Test başarılı'});
state=result.state;const test=result.test;
assert.strictEqual(test.status,'passed');
assert.strictEqual(state.assets[0].lastTestAt,test.testedAt);
assert.strictEqual(store.metrics(state,new Date(test.testedAt)).overdueAssets,0);

result=store.startIncident(state,{locationId:location.id,type:'outage',startedAt:'2026-07-27T18:00:00.000Z',summary:'Bölgesel kesinti',caseNumber:'ABC123',affectedSystems:['cold','internet']});
state=result.state;const incident=result.incident;
assert.strictEqual(incident.status,'open');
assert(incident.tasks.some(x=>x.title.includes('Soğuk oda')),'P1 kritik yük için görev oluşmalı.');
assert(incident.tasks.some(x=>x.title.includes('Resepsiyon')),'Otel profil görevleri oluşmalı.');
assert.throws(()=>store.startIncident(state,{locationId:location.id,type:'outage'}),/zaten açık/);
assert.strictEqual(store.metrics(state).openIncidents,1);

const p1Task=incident.tasks.find(x=>x.priority==='P1');
result=store.toggleIncidentTask(state,incident.id,p1Task.id,true);
state=result.state;
assert.strictEqual(result.task.completed,true);
assert(store.taskProgress(state.incidents[0])>0);

result=store.addIncidentEvent(state,incident.id,{at:'2026-07-27T18:10:00.000Z',note:'Jeneratör devreye girdi',type:'generator_started'});
state=result.state;
assert.strictEqual(state.incidents[0].events.length,2);
assert.throws(()=>store.addIncidentEvent(state,incident.id,{note:''}),/zorunludur/);

result=store.addIncidentCost(state,incident.id,{category:'fuel',amount:2500,note:'Yakıt'});
state=result.state;
assert.strictEqual(store.incidentCostTotal(state.incidents[0]),2500);
assert.throws(()=>store.addIncidentCost(state,incident.id,{amount:0}),/sıfırdan büyük/);

result=store.closeIncident(state,incident.id,{endedAt:'2026-07-27T20:00:00.000Z',closureNote:'Enerji geldi'});
state=result.state;
assert.strictEqual(result.incident.status,'closed');
assert.strictEqual(store.metrics(state).openIncidents,0);
assert.strictEqual(store.metrics(state).totalIncidentCost,2500);
assert.strictEqual(result.incident.closedWithIncompleteP1,true,'Tamamlanmamış P1 görevler uyarı üretmeli.');

const hydrated=store.hydrate(JSON.parse(JSON.stringify(state)));
assert.strictEqual(hydrated.locations.length,1);
assert.strictEqual(hydrated.incidents.length,1);
assert(Array.isArray(hydrated.improvementActions));
assert(hydrated.auditLog.length>=8,'Audit kayıtları oluşmalı.');

const badHydrate=store.hydrate({locations:'bozuk',incidents:null,improvementActions:'bozuk'});
assert(Array.isArray(badHydrate.locations));
assert(Array.isArray(badHydrate.incidents));
assert(Array.isArray(badHydrate.improvementActions));

console.log('İşletme sürekliliği store testleri başarılı.');
