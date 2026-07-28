const assert=require('assert');
const fs=require('fs');
const path=require('path');
const store=require('../sureklilik-paneli/store.js');

const NOW=Date.parse('2026-07-28T09:30:00.000Z');

function handoff(overrides={}){
  return {
    schema:'alo186.continuity-drill-handoff.v1',
    version:1,
    createdAt:'2026-07-28T09:00:00.000Z',
    expiresAt:'2026-08-04T09:00:00.000Z',
    facilityType:'hotel',
    scenarioId:'generator-failure',
    criticalLoads:['life-safety','cold-chain'],
    backupSources:['generator'],
    score:58,
    band:'fragile',
    gaps:[
      {id:'generator-manual-start-boundary',window:'15',priority:'P0',status:'missing'},
      {id:'offline-comms',window:'15',priority:'P1',status:'partial'},
      {id:'closure-owner',window:'60',priority:'P2',status:'missing'}
    ],
    passportEvidenceSuggestions:{recovery_drill:'planned',emergency_contacts:'due'},
    ...overrides
  };
}

assert.strictEqual(store.DRILL_HANDOFF_SCHEMA,'alo186.continuity-drill-handoff.v1');
let state=store.createState();
assert(Array.isArray(state.drillImports));

const checked=store.validateDrillHandoff(handoff(),NOW);
assert.strictEqual(checked.valid,true,checked.reason);
assert.strictEqual(checked.value.actions.length,3);
assert.strictEqual(checked.value.actions[0].dimension,'ownership');
assert.strictEqual(checked.value.actions[0].horizonDays,60);
assert.strictEqual(checked.value.actions[0].priority,9);
assert(!JSON.stringify(checked.value).includes('lifeSupport'));

let result=store.importDrillHandoff(state,handoff(),NOW);
state=result.state;
assert.strictEqual(result.added,3);
assert.strictEqual(result.duplicate,false);
assert.strictEqual(state.drillImports.length,1);
assert.strictEqual(state.drillImports[0].scenarioId,'generator-failure');
assert.strictEqual(state.organization.profile,'hotel');
assert.strictEqual(state.improvementActions.length,3);
assert(state.improvementActions.every(item=>item.source==='outage-drill'));
assert(state.improvementActions.some(item=>item.horizonDays===90&&item.dimension==='improvement'));
assert(state.auditLog.some(item=>item.action==='outage_drill_imported'));

result=store.importDrillHandoff(state,handoff(),NOW);
assert.strictEqual(result.duplicate,true);
assert.strictEqual(result.added,0);
assert.strictEqual(result.state.improvementActions.length,3);

const complete=handoff({score:94,band:'controlled',gaps:[]});
const completeChecked=store.validateDrillHandoff(complete,NOW);
assert.strictEqual(completeChecked.valid,true,completeChecked.reason);
result=store.importDrillHandoff(result.state,complete,NOW);
assert.strictEqual(result.added,0);
assert.strictEqual(result.state.drillImports.length,2,'Boşluksuz başarılı tatbikat da audit kanıtı olarak içe alınmalı.');

assert.strictEqual(store.validateDrillHandoff(handoff({expiresAt:'2026-07-28T09:10:00.000Z'}),NOW).valid,false);
assert.strictEqual(store.validateDrillHandoff(handoff({scenarioId:'unknown'}),NOW).valid,false);
assert.strictEqual(store.validateDrillHandoff(handoff({gaps:[{id:'unknown-gap',window:'5',priority:'P0',status:'missing'}]}),NOW).valid,false);
assert.strictEqual(store.validateDrillHandoff(handoff({gaps:[{id:'scope-check',window:'7',priority:'P0',status:'missing'}]}),NOW).valid,false);
assert.strictEqual(store.validateDrillHandoff(handoff({gaps:[{id:'scope-check',window:'5',priority:'P9',status:'missing'}]}),NOW).valid,false);

const hydrated=store.hydrate(JSON.parse(JSON.stringify(state)));
assert(Array.isArray(hydrated.drillImports));
assert.strictEqual(hydrated.drillImports.length,1);

const root=path.resolve(__dirname,'..');
const panelIndex=fs.readFileSync(path.join(root,'sureklilik-paneli/index.html'),'utf8');
const bridge=fs.readFileSync(path.join(root,'sureklilik-paneli/drill-handoff-bridge.js'),'utf8');
const drillApp=fs.readFileSync(path.join(root,'hesaplama/elektrik-kesintisi-tatbikati/app.js'),'utf8');
assert(panelIndex.includes('./drill-handoff-bridge.js'));
assert(bridge.includes('store.validateDrillHandoff'));
assert(bridge.includes('store.importDrillHandoff'));
assert(bridge.includes('continuity_drill_handoff_detected'));
assert(drillApp.includes('enforceExclusiveNone'));
assert(drillApp.includes('Panele git ve bulguları içe aktar'));
assert(drillApp.includes('https://www.alo186.com/isletme-surekliligi'));

console.log('Tatbikat → Süreklilik Paneli handoff testleri başarılı.');
