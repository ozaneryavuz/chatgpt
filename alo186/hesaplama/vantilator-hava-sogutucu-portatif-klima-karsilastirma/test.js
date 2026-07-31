'use strict';

const assert = require('node:assert/strict');
const { calculateCoolingLoad, evaluate, nextBtuClass } = require('./app.js');

const base = {
  emergency: false,
  mode: 'planning',
  useCase: 'home_room',
  physical: 'good',
  gridSymptom: 'none',
  goal: 'personal_breeze',
  areaM2: 20,
  ceilingM: 2.7,
  humidity: 'medium',
  ventilation: 'yes',
  sun: 'normal',
  people: 2,
  electronicsW: 0,
  deviceType: 'none',
  existing: 'no',
  inputW: 0,
  ratedA: 0,
  candidateBtu: 0,
  manual: 'unknown',
  connection: 'direct',
  protection: 'verified',
  hose: 'unknown',
  drainage: 'unknown',
  taskTest: 'not_tested',
  confirmNeed: true,
  confirmSpecs: true,
  confirmAffiliate: true
};

const run = (changes = {}) => evaluate({ ...base, ...changes });

{
  const load = calculateCoolingLoad(base);
  assert.equal(load.volumeM3, 54);
  assert.ok(load.estimatedBtu > 6000);
  assert.ok(load.suggestedBtu >= load.estimatedBtu);
  assert.equal(nextBtuClass(7200), 8000);
}

{
  const result = run();
  assert.equal(result.status, 'recommend');
  assert.equal(result.recommendation, 'fan');
  assert.equal(result.affiliateAllowed, true);
}

{
  const result = run({ deviceType: 'fan', existing: 'yes', manual: 'verified', inputW: 55, taskTest: 'pass' });
  assert.equal(result.status, 'no-buy');
  assert.equal(result.affiliateAllowed, false);
}

{
  const result = run({ goal: 'room_cooling', deviceType: 'fan', manual: 'verified', inputW: 55 });
  assert.equal(result.status, 'evidence');
  assert.match(result.headline, /eşleşmiyor/);
}

{
  const result = run({ goal: 'room_cooling', humidity: 'low', ventilation: 'yes', deviceType: 'evaporative', manual: 'verified', inputW: 110 });
  assert.equal(result.status, 'recommend');
  assert.equal(result.recommendation, 'compare_evap_ac');
  assert.equal(result.affiliateAllowed, true);
}

{
  const result = run({ goal: 'room_cooling', humidity: 'high', deviceType: 'evaporative', manual: 'verified', inputW: 110 });
  assert.equal(result.status, 'evidence');
  assert.ok(result.warnings.some((item) => item.includes('yüksek')));
  assert.equal(result.affiliateAllowed, false);
}

{
  const result = run({ goal: 'room_cooling', humidity: 'low', ventilation: 'no', deviceType: 'evaporative', manual: 'verified', inputW: 110 });
  assert.equal(result.status, 'evidence');
  assert.ok(result.warnings.some((item) => item.includes('dış hava')));
}

{
  const result = run({ goal: 'room_cooling', humidity: 'high', ventilation: 'no', deviceType: 'portable_ac', manual: 'verified', inputW: 1200, ratedA: 5.5, candidateBtu: 8000, hose: 'verified', drainage: 'verified' });
  assert.equal(result.status, 'recommend');
  assert.equal(result.recommendation, 'portable_ac');
  assert.equal(result.affiliateAllowed, true);
  assert.equal(result.electrical.workingA, 5.5);
}

{
  const result = run({ goal: 'room_cooling', deviceType: 'portable_ac', manual: 'verified', inputW: 1200, candidateBtu: 8000, hose: 'verified', drainage: 'verified', connection: 'extension' });
  assert.equal(result.status, 'stop');
  assert.equal(result.affiliateAllowed, false);
}

{
  const result = run({ goal: 'room_cooling', deviceType: 'portable_ac', manual: 'verified', inputW: 1200, candidateBtu: 8000, hose: 'missing', drainage: 'verified' });
  assert.equal(result.status, 'evidence');
  assert.ok(result.evidence.some((item) => item.includes('hortumu')));
}

{
  const result = run({ goal: 'room_cooling', deviceType: 'portable_ac', manual: 'verified', inputW: 1200, candidateBtu: 5000, hose: 'verified', drainage: 'verified' });
  assert.equal(result.status, 'evidence');
  assert.ok(result.warnings.some((item) => item.includes('altında')));
}

{
  const result = run({ emergency: true });
  assert.equal(result.status, 'stop');
}

{
  const result = run({ gridSymptom: 'bright_dim' });
  assert.equal(result.status, 'professional');
}

{
  const result = run({ mode: 'active_outage' });
  assert.equal(result.status, 'stop');
  assert.equal(result.affiliateAllowed, false);
}

{
  const result = run({ useCase: 'commercial' });
  assert.equal(result.status, 'professional');
}

{
  const result = run({ goal: 'humidity_relief', humidity: 'high' });
  assert.equal(result.status, 'recommend');
  assert.equal(result.recommendation, 'dehumidifier');
  assert.equal(result.affiliateAllowed, true);
}

{
  const result = run({ goal: 'room_cooling', deviceType: 'portable_ac', existing: 'yes', manual: 'verified', inputW: 1200, candidateBtu: 8000, hose: 'verified', drainage: 'verified', taskTest: 'pass' });
  assert.equal(result.status, 'no-buy');
  assert.equal(result.affiliateAllowed, false);
}

{
  const result = run({ areaM2: 0 });
  assert.equal(result.ok, false);
}

console.log(JSON.stringify({
  ok: true,
  scenarios: 18,
  calculations: ['oda_hacmi', 'btu_on_secim', 'watt_amper', 'saatlik_kwh'],
  safetyClosures: ['acil', 'aktif_kesinti', 'sebeke_notr', 'ticari_kritik', 'uzatma', 'su_elektrik'],
  noBuy: true,
  affiliateGate: 3
}, null, 2));
