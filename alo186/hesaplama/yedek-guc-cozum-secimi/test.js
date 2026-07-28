const assert = require('assert');
const Core = require('./core.js');

function base(overrides) {
  return Object.assign({
    context: 'home',
    loadProfile: 'electronics',
    powerBand: 'p600',
    continuity: 'seconds',
    duration: 'd2',
    installation: 'portable',
    outdoorFuel: 'no',
    threePhase: false
  }, overrides || {});
}

let result = Core.evaluate(base({ loadProfile: 'internet', powerBand: 'p150', continuity: 'zero' }));
assert.strictEqual(result.ok, true);
assert.strictEqual(result.primary.key, 'mini_ups');
assert.strictEqual(result.showCommercial, true);
assert.match(result.productUrl, /category=mini_ups/);

result = Core.evaluate(base({ context: 'homeoffice', continuity: 'zero' }));
assert.strictEqual(result.primary.key, 'online_ups');
assert.strictEqual(result.showCommercial, true);
assert.strictEqual(result.calculatorUrl, '/hesaplama/yedek-guc');

result = Core.evaluate(base({ continuity: 'manual', duration: 'd6' }));
assert.strictEqual(result.primary.key, 'power_station');
assert.strictEqual(result.showCommercial, true);
assert.match(result.productUrl, /power_station/);

result = Core.evaluate(base({ loadProfile: 'refrigeration', powerBand: 'p1500', continuity: 'manual', duration: 'd12', installation: 'selected' }));
assert.strictEqual(result.primary.key, 'inverter_battery');
assert.strictEqual(result.professional, true);
assert.strictEqual(result.showCommercial, false);
assert.strictEqual(result.productUrl, null);

result = Core.evaluate(base({ loadProfile: 'mixed', powerBand: 'p3000', continuity: 'manual', duration: 'long', outdoorFuel: 'yes' }));
assert.strictEqual(result.primary.key, 'generator');
assert.strictEqual(result.professional, true);
assert.strictEqual(result.showCommercial, false);

result = Core.evaluate(base({ context: 'medical', loadProfile: 'electronics', continuity: 'zero' }));
assert.strictEqual(result.primary.key, 'hybrid');
assert.strictEqual(result.professional, true);
assert.strictEqual(result.showCommercial, false);
assert.ok(result.professionalReasons.some((item) => /Tıbbi/.test(item)));

result = Core.evaluate(base({ installation: 'whole', outdoorFuel: 'yes' }));
assert.strictEqual(result.primary.key, 'hybrid');
assert.strictEqual(result.professional, true);
assert.strictEqual(result.showCommercial, false);

result = Core.evaluate(base({ threePhase: true }));
assert.strictEqual(result.primary.key, 'hybrid');
assert.strictEqual(result.professional, true);
assert.strictEqual(result.showCommercial, false);

result = Core.evaluate(base({ powerBand: 'high_unknown' }));
assert.strictEqual(result.primary.key, 'hybrid');
assert.strictEqual(result.professional, true);
assert.strictEqual(result.showCommercial, false);

result = Core.evaluate({});
assert.strictEqual(result.ok, false);
assert.ok(result.errors.length >= 7);

const sanitized = Core.sanitizeInput({ context: 'home', email: 'x@example.com', note: 'özel', threePhase: 1 });
assert.deepStrictEqual(sanitized, { context: 'home', threePhase: true });

console.log('Yedek güç çözüm seçimi testleri başarılı.');
