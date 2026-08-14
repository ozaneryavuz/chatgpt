'use strict';

const assert = require('assert');
const path = require('path');
const fs = require('fs');
const tool = require(path.join(__dirname, '..', 'hesaplama', 'parafudr-risk-testi', 'app.js'));

const base = {
  emergency: false,
  activeStorm: 'no',
  useCase: 'home',
  specialSystem: 'no',
  phase: 'single',
  lps: 'no',
  supply: 'underground',
  events: 'rare',
  sensitive: 'none',
  existing: 'none',
  indicator: 'na',
  documentation: 'unknown',
  inspection: 'unknown',
  distance: 'under10',
  earthing: 'verified',
  damage: 'no',
  candidateType: 'none',
  candidateStandard: 'unknown',
  candidateSystemMatch: 'unknown',
  candidateCoordination: 'unknown',
  confirmNeed: false,
  confirmSpecs: false,
  confirmAffiliate: false
};
const run = (patch = {}) => tool.buildRecommendation({...base, ...patch});

let r = run({emergency: true});
assert.equal(r.status, 'stop');
assert.equal(r.affiliateAllowed, false);

r = run({activeStorm: 'yes'});
assert.equal(r.status, 'stop');
assert(r.stops.some(x => x.includes('fırtına')));

r = run({earthing: 'failed'});
assert.equal(r.status, 'stop');
assert.equal(r.affiliateAllowed, false);

r = run({lps: 'yes'});
assert.equal(r.type1Need, true);
assert.equal(r.upstreamAdequate, false);
assert(r.layers.some(x => x.includes('Tip 1')));
assert.equal(r.affiliateAllowed, false);

r = run({lps: 'no', supply: 'overhead'});
assert.equal(r.type1Need, false, 'Havai hat tek başına Tip 1 zorunluluğu üretmemeli');
assert(r.reasons.some(x => x.includes('tek başına Tip 1')));

r = run({existing: 'type2', indicator: 'ok', documentation: 'verified', inspection: 'pass'});
assert.equal(r.status, 'no-buy');
assert.equal(r.affiliateAllowed, false);

r = run({lps: 'yes', existing: 'type12', indicator: 'ok', documentation: 'verified', inspection: 'pass'});
assert.equal(r.status, 'no-buy');
assert.equal(r.upstreamAdequate, true);

r = run({existing: 'type3'});
assert.equal(r.upstreamAdequate, false);
assert(r.warnings.some(x => x.includes('yerine geçmez')));
assert.equal(r.affiliateAllowed, false);

r = run({existing: 'type2', indicator: 'ok', documentation: 'verified', inspection: 'pass', sensitive: 'many'});
assert.equal(r.status, 'downstream');
assert.equal(r.affiliateAllowed, false, 'Onaylar olmadan affiliate açılmamalı');

r = run({existing: 'type2', indicator: 'ok', documentation: 'verified', inspection: 'pass', sensitive: 'many', confirmNeed: true, confirmSpecs: true, confirmAffiliate: true});
assert.equal(r.status, 'downstream');
assert.equal(r.affiliateAllowed, true);
assert(r.affiliateHref.includes('amazon.com.tr'));
assert(r.affiliateHref.includes('alo186rehber-21'));

r = run({candidateType: 'type3', candidateStandard: 'verified', candidateSystemMatch: 'verified', candidateCoordination: 'verified'});
assert.equal(r.status, 'evidence');
assert(r.evidence.some(x => x.includes('önünde doğrulanmış Tip 2')));

r = run({lps: 'yes', candidateType: 'type2', candidateStandard: 'verified', candidateSystemMatch: 'verified', candidateCoordination: 'verified'});
assert.equal(r.status, 'evidence');
assert(r.evidence.some(x => x.includes('Tip 1 kapasitesi')));

r = run({specialSystem: 'yes'});
assert.equal(r.status, 'professional');
assert.equal(r.affiliateAllowed, false);

r = run({phase: 'three'});
assert.equal(r.status, 'professional');

r = run({phase: 'unknown'});
assert.equal(r.status, 'evidence');

r = run({existing: 'type2', indicator: 'failed', documentation: 'verified', inspection: 'pass'});
assert.equal(r.status, 'professional');
assert.equal(r.affiliateAllowed, false);

const html = fs.readFileSync(path.join(__dirname, '..', 'hesaplama', 'parafudr-risk-testi', 'index.html'), 'utf8');
const js = fs.readFileSync(path.join(__dirname, '..', 'hesaplama', 'parafudr-risk-testi', 'app.js'), 'utf8');
const css = fs.readFileSync(path.join(__dirname, '..', 'hesaplama', 'parafudr-risk-testi', 'styles.css'), 'utf8');
assert(html.includes('IEC 61643-11:2025'));
assert(html.includes('rel="sponsored nofollow noopener"'));
assert(html.includes('Satış ortaklığı açıklaması'));
assert(html.includes('Kişisel veri yok'));
assert(html.includes('Mevcut parafudr yeterliyse yenisini almak gerekir mi?'));
assert(!/localStorage|sessionStorage|geolocation|fetch\s*\(/.test(js));
assert(css.includes('min-height:48px'));
assert(css.includes('prefers-reduced-motion'));
assert(css.includes('forced-colors'));

const decision = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'deployment', 'affiliate-category-decisions', 'parafudr-risk-v346.json'), 'utf8'));
assert.equal(decision.version, 346);
assert.equal(decision.fixedPanelAffiliateAllowed, false);
assert.equal(decision.allowedAffiliateClass, 'downstream-Type-3-device-near-surge-protection-only');

console.log('ALO186 parafudr risk & suitability v346: PASS');
