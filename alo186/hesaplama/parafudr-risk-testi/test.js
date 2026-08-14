'use strict';
const assert = require('node:assert/strict');
const { calculateScore, classify, buildRecommendation } = require('./app.js');

function has(texts, fragment) {
  return texts.some((item) => item.toLocaleLowerCase('tr-TR').includes(fragment.toLocaleLowerCase('tr-TR')));
}

const high = buildRecommendation({
  lps: 'yes', supply: 'overhead', events: 'frequent', sensitive: 'many',
  existing: 'none', distance: 'over10', earthing: 'unknown', damage: 'yes'
});
assert.equal(high.level.key, 'high');
assert.ok(high.score >= 65);
assert.equal(high.type1Need, true);
assert.equal(high.type2Need, true);
assert.equal(high.upstreamAdequate, false);
assert.ok(has(high.layers, 'Tip 1'));
assert.equal(high.affiliateAllowed, false);

const overheadOnly = buildRecommendation({
  lps: 'no', supply: 'overhead', events: 'occasional', sensitive: 'some',
  existing: 'none', distance: 'under10', earthing: 'verified', damage: 'no'
});
assert.equal(overheadOnly.type1Need, false, 'Havai hat tek başına Tip 1 zorunluluğu üretmemeli');
assert.equal(overheadOnly.type2Need, true);
assert.ok(has(overheadOnly.layers, 'Tip 2'));
assert.ok(has(overheadOnly.reasons, 'tek başına Tip 1'));

const noBuy = buildRecommendation({
  lps: 'no', supply: 'underground', events: 'rare', sensitive: 'none',
  existing: 'type2', indicator: 'ok', documentation: 'verified', inspection: 'pass',
  distance: 'under10', earthing: 'verified', damage: 'no'
});
assert.equal(noBuy.level.key, 'review');
assert.ok(noBuy.score < 35);
assert.equal(noBuy.status, 'no-buy');
assert.equal(noBuy.type1Need, false);
assert.equal(noBuy.type3Useful, false);
assert.equal(noBuy.affiliateAllowed, false);

const downstreamWithoutConsent = buildRecommendation({
  lps: 'no', supply: 'underground', events: 'rare', sensitive: 'many',
  existing: 'type2', indicator: 'ok', documentation: 'verified', inspection: 'pass',
  distance: 'under10', earthing: 'verified', damage: 'no'
});
assert.equal(downstreamWithoutConsent.status, 'downstream');
assert.equal(downstreamWithoutConsent.type3Useful, true);
assert.equal(downstreamWithoutConsent.affiliateAllowed, false);

const downstreamWithConsent = buildRecommendation({
  lps: 'no', supply: 'underground', events: 'rare', sensitive: 'many',
  existing: 'type2', indicator: 'ok', documentation: 'verified', inspection: 'pass',
  distance: 'under10', earthing: 'verified', damage: 'no',
  confirmNeed: true, confirmSpecs: true, confirmAffiliate: true
});
assert.equal(downstreamWithConsent.status, 'downstream');
assert.equal(downstreamWithConsent.affiliateAllowed, true);
assert.match(downstreamWithConsent.affiliateHref, /amazon\.com\.tr/);
assert.match(downstreamWithConsent.affiliateHref, /alo186rehber-21/);

const type3Only = buildRecommendation({
  lps: 'no', supply: 'underground', events: 'rare', sensitive: 'some',
  existing: 'type3', distance: 'under10', earthing: 'verified', damage: 'no',
  candidateType: 'type3', candidateStandard: 'verified'
});
assert.equal(type3Only.upstreamAdequate, false);
assert.equal(type3Only.status, 'evidence');
assert.ok(has(type3Only.warnings, 'yerine geçmez'));
assert.ok(has(type3Only.evidence, 'önünde doğrulanmış Tip 2'));
assert.equal(type3Only.affiliateAllowed, false);

const storm = buildRecommendation({activeStorm: 'yes', earthing: 'verified'});
assert.equal(storm.status, 'stop');
assert.equal(storm.affiliateAllowed, false);

const unknown = calculateScore({});
assert.ok(unknown.score > 0 && unknown.score < 100);
assert.equal(classify(100).key, 'high');
assert.equal(classify(50).key, 'medium');
assert.equal(classify(10).key, 'review');

console.log('Parafudr risk testi v346: güvenlik, no-buy, Tip 1/2/3 ve affiliate kapıları başarılı.');
