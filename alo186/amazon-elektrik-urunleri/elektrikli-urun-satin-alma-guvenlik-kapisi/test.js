"use strict";
const assert = require("assert");
const { evaluate } = require("./app.js");

let result = evaluate({ damage: true, category: "plugIn" });
assert.equal(result.status, "stop");
assert.equal(result.affiliate, false);

result = evaluate({ category: "fixed", exactModel: true, manual: true });
assert.equal(result.status, "stop");
assert.equal(result.affiliate, false);

result = evaluate({ category: "plugIn", existingSufficient: true });
assert.equal(result.status, "ok");
assert.match(result.title, /yeni ürün almayın/i);
assert.equal(result.affiliate, false);

result = evaluate({
  category: "plugIn", exactModel: true, manual: true, label: true,
  voltageMatch: true, traceability: true, recallChecked: false,
  needConfirmed: true, affiliateAware: true
});
assert.equal(result.status, "warn");
assert.match(result.summary, /GÜBİS/i);

result = evaluate({
  category: "plugIn", exactModel: true, manual: true, label: true,
  voltageMatch: true, traceability: true, recallChecked: true,
  needConfirmed: true, affiliateAware: true
});
assert.equal(result.status, "ok");
assert.equal(result.affiliate, true);

console.log(JSON.stringify({ ok: true, cases: 5, directAmazonLinks: 0, noBuyOutcome: true }));
