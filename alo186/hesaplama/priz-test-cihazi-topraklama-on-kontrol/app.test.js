"use strict";
const assert = require("node:assert/strict");
const { evaluate, affiliateUrl, voltageMetric, requiredType, hasProfessionalTask } = require("./app.js");

let scenarios = 0;
function check(name, input, expectedStatus, extra) {
  const decision = evaluate(input);
  assert.equal(decision.status, expectedStatus, name);
  if (extra) extra(decision);
  scenarios += 1;
  return decision;
}

const base = {
  emergency: false,
  condition: "sound",
  issue: "precheck",
  outageScope: "none",
  role: "general",
  installation: "home230",
  plugStandard: "type_ef",
  commonFaults: true,
  voltageDisplay: false,
  rcdFunctional: false,
  earthQuality: false,
  loopImpedance: false,
  rcdTripTime: false,
  measuredVoltage: "230",
  ownership: "none",
  testerType: "unknown",
  plugCompatibility: "na",
  voltageRating: "na",
  safetyEvidence: "na",
  recall: "na",
  knownGood: "na"
};
const withBase = (patch) => Object.assign({}, base, patch || {});

check("basic recommendation", base, "recommend", (d) => {
  assert.equal(d.productType, "basic");
  assert.equal(d.commerceEligible, true);
  assert.match(d.limitation, /çevrim empedansı/i);
});
check("voltage display recommendation", withBase({ voltageDisplay: true }), "recommend", (d) => assert.equal(d.productType, "display"));
check("rcd recommendation", withBase({ rcdFunctional: true }), "recommend", (d) => {
  assert.equal(d.productType, "rcd");
  assert.match(d.limitation, /açma akımı/i);
});

for (const issue of ["tingling"]) check(`danger issue ${issue}`, withBase({ issue }), "danger");
for (const condition of ["loose", "burnt", "wet", "cracked"]) check(`unsafe condition ${condition}`, withBase({ condition }), "danger");
check("emergency checkbox", withBase({ emergency: true }), "danger");
check("recalled tester", withBase({ ownership: "owned", testerType: "basic", recall: "recalled" }), "danger");
check("failed known-good check", withBase({ ownership: "owned", testerType: "basic", knownGood: "failed" }), "danger");

check("neighborhood outage", withBase({ outageScope: "neighborhood" }), "official", (d) => assert.match(d.next, /186/));
for (const scope of ["room", "property"]) check(`circuit scope ${scope}`, withBase({ outageScope: scope }), "professional");
check("single dead outlet", withBase({ issue: "no_power", outageScope: "single" }), "professional");
check("repeated rcd trip", withBase({ issue: "repeated_rcd" }), "professional");
check("intermittent outlet", withBase({ issue: "intermittent" }), "professional");
for (const installation of ["outdoor", "industrial", "ev", "threephase"]) check(`professional installation ${installation}`, withBase({ installation }), "professional");
for (const task of ["earthQuality", "loopImpedance", "rcdTripTime"]) check(`professional task ${task}`, withBase({ [task]: true }), "professional");

check("unknown installation", withBase({ installation: "unknown" }), "evidence");
check("unknown plug standard", withBase({ plugStandard: "unknown" }), "evidence");
check("other plug standard", withBase({ plugStandard: "other" }), "evidence");
check("no consumer task", withBase({ commonFaults: false }), "evidence");

const ownedVerified = {
  ownership: "owned",
  testerType: "rcd",
  plugCompatibility: "yes",
  voltageRating: "yes",
  safetyEvidence: "yes",
  recall: "yes",
  knownGood: "passed"
};
check("owned suitable no-buy", withBase(Object.assign({ rcdFunctional: true }, ownedVerified)), "no-buy", (d) => {
  assert.equal(d.commerceEligible, false);
  assert.match(d.title, /yeni ürün almayın/i);
});
check("owned display suitable", withBase(Object.assign({ voltageDisplay: true, testerType: "display" }, ownedVerified)), "no-buy");
check("owned basic suitable", withBase(Object.assign({ testerType: "basic" }, ownedVerified)), "no-buy");
check("owned class too low", withBase(Object.assign({ rcdFunctional: true, testerType: "basic" }, ownedVerified)), "replace", (d) => assert.equal(d.commerceEligible, true));
check("owned display too low", withBase(Object.assign({ voltageDisplay: true, testerType: "basic" }, ownedVerified)), "replace");
check("candidate compatible", withBase(Object.assign({ ownership: "candidate", rcdFunctional: true }, ownedVerified)), "candidate", (d) => assert.equal(d.commerceEligible, true));

check("unknown tester type", withBase({ ownership: "owned" }), "evidence");
check("plug mismatch", withBase(Object.assign({}, ownedVerified, { plugCompatibility: "no" })), "replace");
check("voltage mismatch", withBase(Object.assign({}, ownedVerified, { voltageRating: "no" })), "replace");
check("missing safety evidence", withBase(Object.assign({}, ownedVerified, { safetyEvidence: "no" })), "replace");
check("unknown safety evidence", withBase(Object.assign({}, ownedVerified, { safetyEvidence: "unknown" })), "evidence");
check("unknown recall", withBase(Object.assign({}, ownedVerified, { recall: "unknown" })), "evidence");
check("known-good not done", withBase(Object.assign({}, ownedVerified, { knownGood: "unknown" })), "evidence");

const recommended = evaluate(withBase({ rcdFunctional: true }));
const url = affiliateUrl(recommended);
assert.match(url, /^https:\/\/www\.amazon\.com\.tr\/s\?k=/);
assert.match(url, /tag=alo186rehber-21$/);
assert.match(decodeURIComponent(url), /RCD test/);
scenarios += 3;
assert.equal(affiliateUrl(evaluate(withBase(Object.assign({ rcdFunctional: true }, ownedVerified)))), "");
scenarios += 1;

assert.equal(requiredType(withBase({ rcdFunctional: true })), "rcd");
assert.equal(requiredType(withBase({ voltageDisplay: true })), "display");
assert.equal(requiredType(withBase()), "basic");
assert.equal(requiredType(withBase({ commonFaults: false })), null);
scenarios += 4;
assert.equal(hasProfessionalTask(withBase({ earthQuality: true })), true);
assert.equal(hasProfessionalTask(withBase()), false);
scenarios += 2;

const nominal = voltageMetric("230");
assert.equal(nominal.voltage, 230);
assert.equal(nominal.deviationPercent, 0);
const low = voltageMetric("207");
assert.equal(low.deviationPercent, -10);
assert.match(low.text, /207 V/);
const none = voltageMetric("");
assert.equal(none.voltage, null);
scenarios += 5;

assert.equal(evaluate(base).personalData, false);
assert.equal(evaluate(base).reviewDays, 180);
scenarios += 2;

console.log(JSON.stringify({ ok: true, scenarios }));
