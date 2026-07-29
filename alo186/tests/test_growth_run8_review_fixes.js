'use strict';

// Regression coverage for all seven actionable Codex review threads on merged PR #236.
const assert = require('node:assert/strict');
const runtime = require('../hesaplama/yedek-guc-runtime-saglik-gunlugu/core.js');
const vpp = require('../hesaplama/vpp-esnek-yuk-hazirlik/core.js');
const ev = require('../hesaplama/apartman-site-ev-sarj-karar-paketi/core.js');

const record = (id, date, minutes, system = 'mini') => ({
  id, date, system, load: 'low', charge: 'full', minutes, outcome: 'normal', hazard: false,
  createdAt: `${date}T12:00:00.000Z`, expiresAt: '2030-01-01T00:00:00.000Z'
});

let entries = [record('r1', '2026-01-01', 100), record('r2', '2026-02-01', 50)];
let result = runtime.assess(entries, entries[1]);
assert.equal(result.state, 'confirmation_needed');
assert.equal(result.showCommercial, false, 'Tek düşüş ticari kategori yolunu açmamalı.');

entries.push(record('r3', '2026-03-01', 48));
result = runtime.assess(entries, entries[2]);
assert.equal(result.state, 'repeated_drop');
assert.equal(result.showCommercial, true, 'İkinci düşük doğrulama sonrası düşük riskli kategori yolu açılabilir.');

const backfilled = [record('july', '2026-07-01', 100), record('june', '2026-06-01', 50)];
result = runtime.assess(backfilled, backfilled[1]);
assert.equal(result.baseline, null, 'Geri tarihli kayıt gelecekteki testi baseline olarak kullanmamalı.');
assert.equal(result.change, null);
assert.equal(result.showCommercial, false);

const now = Date.parse('2026-07-29T00:00:00Z');
const expired = {...record('old', '2025-01-01', 100), expiresAt: '2026-07-28T00:00:00Z'};
const active = {...record('new', '2026-07-01', 90), expiresAt: '2026-12-01T00:00:00Z'};
assert.deepEqual(runtime.pruneEntries([expired, active], now).map(item => item.id), ['new']);
const serialized = runtime.serialize([active], now);
assert.equal(serialized.items[0].expiresAt, active.expiresAt, 'Ziyaret veya kayıt ekleme eski kaydın TTL tarihini uzatmamalı.');
assert.equal(serialized.retentionMode, 'per-record');

const strongest = {history: 'twelve', meter: 'five', telemetry: 'remote', control: 'remote', availability: 'defined', contract: 'identified'};
let vppResult = vpp.assess({assets: [], values: strongest});
assert.equal(vppResult.assetRequired, true);
assert.equal(vppResult.band, 'asset_required');
assert(vppResult.score <= 8, 'Kaynak seçilmeden yeşil hazırlık puanı üretilememeli.');
vppResult = vpp.assess({assets: ['pv'], values: strongest});
assert.equal(vppResult.band, 'ready');

const evResult = ev.assess({facility: 'site', use: 'common', supply: 'common', parking: 'defined', load: 'measured', management: 'dynamic', metering: 'submeter', evidence: 'ready'});
assert.equal(evResult.score, 11);
assert.equal(evResult.maxScore, 11);

console.log('ALO186 PR #236 review fixes: runtime confirmation/chronology/TTL, VPP asset gate and EV score OK.');
