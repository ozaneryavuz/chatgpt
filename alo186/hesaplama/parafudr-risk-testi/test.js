'use strict';
const assert = require('node:assert/strict');
const { calculateScore, classify, buildRecommendation } = require('./app.js');

function has(texts, fragment) {
  return texts.some((item) => item.toLocaleLowerCase('tr-TR').includes(fragment.toLocaleLowerCase('tr-TR')));
}

const critical = buildRecommendation({
  lps: 'yes', supply: 'overhead', events: 'frequent', sensitive: 'many',
  existing: 'none', distance: 'over10', earthing: 'unknown', damage: 'yes'
});
assert.equal(critical.level.key, 'critical');
assert.ok(critical.score >= 66);
assert.equal(critical.type1Need, true);
assert.equal(critical.type2Need, true);
assert.equal(critical.type3Need, true);
assert.ok(has(critical.layers, 'Tip 1'));
assert.ok(has(critical.layers, 'Tip 2'));
assert.ok(has(critical.layers, 'Tip 3'));

const moderate = buildRecommendation({
  lps: 'no', supply: 'underground', events: 'occasional', sensitive: 'many',
  existing: 'none', distance: 'under10', earthing: 'old', damage: 'no'
});
assert.ok(['elevated', 'review'].includes(moderate.level.key));
assert.equal(moderate.type2Need, true);
assert.ok(has(moderate.layers, 'Tip 2'));

const maintained = buildRecommendation({
  lps: 'no', supply: 'underground', events: 'rare', sensitive: 'none',
  existing: 'type12', distance: 'under10', earthing: 'verified', damage: 'no'
});
assert.equal(maintained.level.key, 'review');
assert.ok(maintained.score < 36);
assert.equal(maintained.type1Need, false);
assert.equal(maintained.type3Need, false);
assert.ok(has(maintained.layers, 'bakım'));

const unknown = calculateScore({});
assert.ok(unknown.score > 0 && unknown.score < 100);
assert.equal(classify(100).key, 'critical');
assert.equal(classify(50).key, 'elevated');
assert.equal(classify(10).key, 'review');

const type3Only = buildRecommendation({
  lps: 'no', supply: 'underground', events: 'rare', sensitive: 'some',
  existing: 'type3', distance: 'under10', earthing: 'verified', damage: 'no'
});
assert.ok(has(type3Only.warnings, 'yerine geçmez'));
assert.ok(has(type3Only.layers, 'Tip 2'));

console.log('Parafudr risk testi: 5 senaryo ve sınıflandırma kontrolleri başarılı.');
