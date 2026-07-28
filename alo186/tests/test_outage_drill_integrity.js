const assert = require("assert");
const fs = require("fs");
const path = require("path");
const core = require("../hesaplama/elektrik-kesintisi-tatbikati/core.js");

function readyStatuses(scenarioId = "grid-outage") {
  return Object.fromEntries(core.activeTasks(scenarioId).map((task) => [task.id, "ready"]));
}

function payload(overrides = {}) {
  return {
    facilityType: "hotel",
    scenarioId: "grid-outage",
    immediateDanger: false,
    confirmTabletop: true,
    rolesAssigned: true,
    offlineContacts: true,
    recordTemplate: true,
    criticalLoads: ["life-safety"],
    backupSources: ["generator"],
    taskStatuses: readyStatuses(),
    ...overrides
  };
}

const now = new Date("2026-07-28T09:00:00Z");

{
  const result = core.evaluate(payload({ criticalLoads: ["none", "communications"] }), { now });
  assert.strictEqual(result.valid, false);
  assert(result.errors.some((item) => item.includes("Kritik yük yok")));
}

{
  const result = core.evaluate(payload({ backupSources: ["none", "generator"] }), { now });
  assert.strictEqual(result.valid, false);
  assert(result.errors.some((item) => item.includes("Yedek kaynak yok")));
}

{
  const result = core.evaluate(payload(), { now });
  assert.strictEqual(result.valid, true);
  assert.strictEqual(result.passportEvidenceSuggestions.recovery_drill, "current");
  assert.deepStrictEqual(result.handoff.passportEvidenceSuggestions, result.passportEvidenceSuggestions);
}

{
  const app = fs.readFileSync(path.join(__dirname, "../hesaplama/elektrik-kesintisi-tatbikati/app.js"), "utf8");
  assert(app.includes("enforceExclusiveNone"));
  assert(app.includes("invalidateResult"));
  assert(app.includes('form.addEventListener("change"'));
  assert(app.includes("latestResult = null"));
}

console.log("Elektrik kesintisi tatbikatı bütünlük korumaları: 4 regresyon grubu başarılı.");
