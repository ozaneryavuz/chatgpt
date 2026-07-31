"use strict";
const assert = require("assert");
const { evaluate } = require("./app.js");

let result = evaluate({ damage: true });
assert.equal(result.status, "stop");
assert.equal(result.commerce, false);

result = evaluate({ match: "exact" });
assert.equal(result.status, "stop");
assert.match(result.title, /Tam model eşleşti/i);

result = evaluate({ match: "possible" });
assert.equal(result.status, "warn");
assert.equal(result.commerce, false);

result = evaluate({ origin: "eu", brandModel: true, serialLot: true, market: true, manufacturer: true, gubis: true, safetyGate: false, match: "none" });
assert.equal(result.status, "warn");
assert.match(result.summary, /Safety Gate/i);

result = evaluate({ origin: "tr", brandModel: true, serialLot: true, market: true, manufacturer: true, gubis: true, match: "none" });
assert.equal(result.status, "ok");
assert.match(result.title, /güvenlik garantisi değildir/i);
assert.equal(result.commerce, false);

console.log(JSON.stringify({ ok: true, cases: 5, commerceClosed: true, noSafetyGuarantee: true }));
