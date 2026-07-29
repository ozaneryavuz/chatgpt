'use strict';

const assert = require('node:assert/strict');
const core = require('./conversion-growth-core.js');

assert.equal(core.gateStatus('generator', {}).reason, 'professional_only');
assert.equal(core.gateStatus('inverter', {}).reason, 'professional_only');
assert.equal(core.gateStatus('outlet_tester', {}).reason, 'professional_only');
assert.equal(core.gateStatus('ups_battery', {}).reason, 'professional_only');

assert.deepEqual(
  core.gateStatus('ev_cable', {
    toolConfirmed: true,
    existingInsufficient: false,
    affiliateAccepted: true,
  }),
  { allowed: false, reason: 'existing_may_be_sufficient' }
);

assert.deepEqual(
  core.gateStatus('ev_cable', {
    toolConfirmed: true,
    existingInsufficient: true,
    affiliateAccepted: false,
  }),
  { allowed: false, reason: 'affiliate_not_accepted' }
);

assert.deepEqual(
  core.gateStatus('ev_cable', {
    toolConfirmed: true,
    existingInsufficient: true,
    affiliateAccepted: true,
  }),
  { allowed: true, reason: 'qualified_search' }
);

const url = core.buildAffiliateUrl('ev_cable', { current: '32', phase: 'three', length: '7_5' });
assert.match(url, /^https:\/\/www\.amazon\.com\.tr\/s\?k=/);
assert.match(url, /(?:\?|&)tag=alo186hazirlik-21/);
assert.match(url, /32A/);

console.log(JSON.stringify({ ok: true, professionalOnly: 4, qualifiedAffiliateGate: true }));
