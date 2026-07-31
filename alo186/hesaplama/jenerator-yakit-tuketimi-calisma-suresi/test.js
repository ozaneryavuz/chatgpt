const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const directory = __dirname;
const source = fs.readFileSync(path.join(directory, 'app.js'), 'utf8');
const sandbox = { console, globalThis: {}, setTimeout, clearTimeout };
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(source, sandbox);
const api = sandbox.Alo186GeneratorFuel;
assert(api, 'Karar motoru yüklenemedi');

const safe = {
  emergency: '', coStatus: 'none', location: 'outdoors_clear', mode: 'planning',
  generatorType: 'portable', fuelType: 'diesel', connection: 'individual',
  continuousKW: 5, loadKW: 2.5, tankLiters: 20, usablePct: 90, targetHours: 6,
  fuel25: 0.8, fuel50: 1.2, fuel75: 1.7, fuel100: 2.3,
  curveEvidence: 'manufacturer', existing: 'yes', maintenance: 'yes',
  transferTest: 'yes', coAlarm: 'yes', fuelStorage: 'safe'
};

const metrics = api.calculate(safe);
assert.strictEqual(metrics.loadPct, 50);
assert.strictEqual(metrics.fuelRate, 1.2);
assert.strictEqual(metrics.runtimeHours, 15);
assert.strictEqual(api.decide(safe).code, 'no_buy');
assert.strictEqual(api.decide({ ...safe, coStatus: 'alarm' }).code, 'emergency');
assert.strictEqual(api.decide({ ...safe, connection: 'backfeed' }).code, 'backfeed');
assert.strictEqual(api.decide({ ...safe, existing: 'no' }).code, 'portable_planning');
console.log(JSON.stringify({ ok: true, module: 'generator-fuel-runtime', scenarios: 4 }));
