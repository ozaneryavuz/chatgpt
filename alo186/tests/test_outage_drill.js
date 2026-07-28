const assert = require("assert");
const fs = require("fs");
const path = require("path");
const core = require("../hesaplama/elektrik-kesintisi-tatbikati/core.js");

function readyStatuses(scenarioId) {
  return Object.fromEntries(core.activeTasks(scenarioId).map((task) => [task.id, "ready"]));
}

function base(overrides = {}) {
  return {
    facilityType: "hotel",
    scenarioId: "grid-outage",
    immediateDanger: false,
    lifeSupport: false,
    confirmTabletop: true,
    rolesAssigned: true,
    offlineContacts: true,
    recordTemplate: true,
    criticalLoads: ["life-safety", "communications"],
    backupSources: ["generator", "ups"],
    taskStatuses: readyStatuses("grid-outage"),
    ...overrides
  };
}

const fixedNow = new Date("2026-07-28T09:00:00.000Z");

{
  const result = core.evaluate(base({ immediateDanger: true }), { now: fixedNow });
  assert.strictEqual(result.valid, false);
  assert.strictEqual(result.emergency, true);
  assert.strictEqual(result.route, "112");
  assert.strictEqual(result.revenueAllowed, false);
}

{
  const result = core.evaluate(base({ confirmTabletop: false }), { now: fixedNow });
  assert.strictEqual(result.valid, false);
  assert(result.errors.some((item) => item.includes("kontrollü tatbikat")));
}

{
  const result = core.evaluate(base({ criticalLoads: [] }), { now: fixedNow });
  assert.strictEqual(result.valid, false);
  assert(result.errors.some((item) => item.includes("Kritik yük")));
}

{
  const result = core.evaluate(base({ backupSources: [] }), { now: fixedNow });
  assert.strictEqual(result.valid, false);
  assert(result.errors.some((item) => item.includes("Yedek kaynak")));
}

{
  const result = core.evaluate(base(), { now: fixedNow });
  assert.strictEqual(result.valid, true);
  assert.strictEqual(result.score, 100);
  assert.strictEqual(result.classification.id, "controlled");
  assert.strictEqual(result.p0Count, 0);
  assert.strictEqual(result.timeline.length, 3);
  assert.strictEqual(result.nextDrillDate.toISOString(), "2027-01-24T09:00:00.000Z");
}

{
  const result = core.evaluate(base(), { now: fixedNow });
  assert.strictEqual(result.passportEvidenceSuggestions.recovery_drill, "current");
  assert.deepStrictEqual(result.handoff.passportEvidenceSuggestions, result.passportEvidenceSuggestions);
}

{
  const result = core.evaluate(base({ criticalLoads: ["none", "communications"] }), { now: fixedNow });
  assert.strictEqual(result.valid, false);
  assert(result.errors.some((item) => item.includes("Kritik yük yok")));
}

{
  const result = core.evaluate(base({ backupSources: ["none", "generator"] }), { now: fixedNow });
  assert.strictEqual(result.valid, false);
  assert(result.errors.some((item) => item.includes("Yedek kaynak yok")));
}

{
  const statuses = readyStatuses("grid-outage");
  statuses["hazard-check"] = "missing";
  const result = core.evaluate(base({ taskStatuses: statuses }), { now: fixedNow });
  assert(result.score < 100);
  assert(result.gaps.some((item) => item.id === "hazard-check" && item.priority === "P0"));
  assert.strictEqual(result.gaps[0].priority, "P0");
}

{
  const statuses = readyStatuses("grid-outage");
  statuses["hazard-check"] = "partial";
  const result = core.evaluate(base({ taskStatuses: statuses }), { now: fixedNow });
  const gap = result.gaps.find((item) => item.id === "hazard-check");
  assert.strictEqual(gap.priority, "P1");
  assert.strictEqual(gap.status, "partial");
}

{
  const result = core.evaluate(base({ backupSources: ["none"] }), { now: fixedNow });
  assert(result.score <= 49);
  assert(result.gaps.some((item) => item.id === "critical-without-backup" && item.priority === "P0"));
}

{
  const result = core.evaluate(base({ criticalLoads: ["none"], backupSources: ["none"] }), { now: fixedNow });
  assert(!result.gaps.some((item) => item.id === "critical-without-backup"));
  assert.strictEqual(result.score, 100);
}

{
  const result = core.evaluate(base({ rolesAssigned: false }), { now: fixedNow });
  assert(result.score <= 64);
  assert(result.gaps.some((item) => item.id === "roles-not-assigned"));
}

{
  const result = core.evaluate(base({ offlineContacts: false, recordTemplate: false }), { now: fixedNow });
  assert(result.gaps.some((item) => item.id === "offline-contacts-missing" && item.priority === "P1"));
  assert(result.gaps.some((item) => item.id === "record-template-missing"));
}

{
  const scenarios = core.SCENARIOS.map((item) => item.id);
  assert.deepStrictEqual(scenarios, ["grid-outage", "generator-failure", "short-autonomy", "voltage-anomaly", "critical-load-loss"]);
  scenarios.forEach((scenarioId) => {
    const tasks = core.activeTasks(scenarioId);
    assert.strictEqual(tasks.length, 16);
    assert(tasks.some((task) => task.id === core.SCENARIO_TASKS[core.SCENARIOS.find((item) => item.id === scenarioId).extraTask].id));
  });
}

{
  const scenarioId = "generator-failure";
  const result = core.evaluate(base({ scenarioId, taskStatuses: readyStatuses(scenarioId) }), { now: fixedNow });
  assert.strictEqual(result.scenario.id, scenarioId);
  assert(result.timeline.flatMap((group) => group.tasks).some((task) => task.id === "generator-manual-start-boundary"));
}

{
  const scenarioId = "short-autonomy";
  const statuses = readyStatuses(scenarioId);
  statuses["autonomy-recheck"] = "missing";
  const result = core.evaluate(base({ scenarioId, taskStatuses: statuses }), { now: fixedNow });
  assert(result.gaps.some((item) => item.id === "autonomy-recheck" && item.window === "15"));
}

{
  const statuses = Object.fromEntries(core.activeTasks("grid-outage").map((task) => [task.id, "missing"]));
  const result = core.evaluate(base({ taskStatuses: statuses }), { now: fixedNow });
  assert.strictEqual(result.classification.id, "uncontrolled");
  assert(result.score < 40);
  assert.strictEqual(result.nextDrillDate.toISOString(), "2026-08-27T09:00:00.000Z");
}

{
  const statuses = readyStatuses("grid-outage");
  statuses["stakeholder-update"] = "missing";
  statuses["closure-owner"] = "missing";
  const result = core.evaluate(base({ taskStatuses: statuses }), { now: fixedNow });
  assert(result.gaps.filter((item) => item.priority === "P2").length >= 2);
}

{
  const statuses = readyStatuses("grid-outage");
  statuses["backup-status"] = "missing";
  statuses["transfer-observation"] = "missing";
  const result = core.evaluate(base({ taskStatuses: statuses }), { now: fixedNow });
  assert.strictEqual(result.passportEvidenceSuggestions.generator_ups_test, "due");
  assert.strictEqual(result.passportEvidenceSuggestions.transfer_test, "due");
}

{
  const result = core.evaluate(base(), { now: fixedNow });
  const payload = core.exportPayload(result);
  assert.strictEqual(payload.schema, "alo186.electric-outage-drill.v1");
  assert.strictEqual(payload.version, 1);
  assert.strictEqual(payload.handoff.schema, "alo186.continuity-drill-handoff.v1");
  assert.strictEqual(payload.handoff.expiresAt, "2026-08-04T09:00:00.000Z");
  assert(!JSON.stringify(payload).match(/lifeSupport|email|phone|address|name/i));
}

{
  assert.throws(() => core.exportPayload({ valid: false }), /Geçerli tatbikat/);
}

{
  const result = core.evaluate(base({ facilityType: "invalid" }), { now: fixedNow });
  assert.strictEqual(result.facilityType, "other");
}

{
  const result = core.evaluate(base({ criticalLoads: ["life-safety", "life-safety", "unknown"], backupSources: ["ups", "ups", "unknown"] }), { now: fixedNow });
  assert.deepStrictEqual(result.criticalLoads, ["life-safety"]);
  assert.deepStrictEqual(result.backupSources, ["ups"]);
}

{
  const html = fs.readFileSync(path.join(__dirname, "../hesaplama/elektrik-kesintisi-tatbikati/index.html"), "utf8");
  assert(html.includes('rel="canonical" href="https://www.alo186.com/hesaplama/elektrik-kesintisi-tatbikati/"'));
  assert(html.includes('"@type":"WebApplication"'));
  assert(html.includes('"@type":"FAQPage"'));
  assert(html.includes("112’yi ara"));
  assert(!/<input[^>]+type=["'](?:text|email|tel)["']/i.test(html));
  assert(!/<textarea/i.test(html));
  assert(!/amazon\.|amzn\./i.test(html));
}

{
  const app = fs.readFileSync(path.join(__dirname, "../hesaplama/elektrik-kesintisi-tatbikati/app.js"), "utf8");
  assert(app.includes("enforceExclusiveNone"));
  assert(app.includes("invalidateResult"));
  assert(app.includes('form.addEventListener("change"'));
}

{
  const schema = JSON.parse(fs.readFileSync(path.join(__dirname, "../hesaplama/elektrik-kesintisi-tatbikati/drill.schema.json"), "utf8"));
  assert.strictEqual(schema.$schema, "https://json-schema.org/draft/2020-12/schema");
  assert.strictEqual(schema.properties.schema.const, "alo186.electric-outage-drill.v1");
  assert(schema.required.includes("handoff"));
}

console.log("Elektrik kesintisi tatbikatı: 28 regresyon grubu başarılı.");
