const assert=require('assert');
const c=require('../hesaplama/calc-core.js');

let r=c.upsRuntime({loadW:100,batteryWh:1000,efficiency:.9,usableDepth:.8,aging:.9});
assert(Math.abs(r.runtimeHours-6.48)<1e-9);

r=c.requiredBattery({loadW:100,hours:4,efficiency:.9,usableDepth:.8,aging:.9,reserve:0});
assert(Math.abs(r.requiredNominalWh-617.283950617284)<1e-9);

r=c.evCharge({batteryKWh:60,currentSoc:20,targetSoc:80,chargerKW:7.4,efficiency:.9,unitPrice:3});
assert(Math.abs(r.batteryEnergyKWh-36)<1e-9);
assert(Math.abs(r.gridEnergyKWh-40)<1e-9);
assert(Math.abs(r.hours-(40/7.4))<1e-9);

r=c.voltageDrop({system:'three',material:'copper',lengthM:100,currentA:50,sectionMM2:10,voltageV:400,tempC:20});
assert(Math.abs(r.dropV-(Math.sqrt(3)*50*100*.0175/10))<1e-9);

r=c.requiredSection({system:'three',material:'copper',lengthM:100,currentA:50,voltageV:400,tempC:20,maxDropPercent:3});
assert.strictEqual(r.sectionMM2,16);

console.log('Tüm calc-core testleri başarılı.');
