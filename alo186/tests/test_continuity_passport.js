const assert = require("assert");
const fs = require("fs");
const path = require("path");
const core = require("../hesaplama/elektrik-surekliligi-pasaportu/core.js");

function statuses(value) {
  return Object.fromEntries(core.EVIDENCE.map((item) => [item.id, value]));
}

const fixedNow = "2026-07-28T07:00:00.000Z";

assert.strictEqual(core.EVIDENCE.length, 10, "Pasaport tam 10 kanıt alanı taşımalı.");
assert.strictEqual(core.EVIDENCE.reduce((sum, item) => sum + item.weight, 0), 100, "Kanıt ağırlıkları 100 olmalı.");
assert.strictEqual(new Set(core.EVIDENCE.map((item) => item.id)).size, 10, "Kanıt kimlikleri benzersiz olmalı.");

const complete = core.evaluatePassport({
  facilityType: "hotel",
  criticalLoadCategories: ["safety", "communications"],
  backupSourceClasses: ["generator", "ups"],
  evidenceStatuses: statuses("current")
}, { now: fixedNow });
assert.strictEqual(complete.valid, true);
assert.strictEqual(complete.emergency, false);
assert.strictEqual(complete.score, 100, "Bütün kanıtlar güncelse skor 100 olmalı.");
assert.strictEqual(complete.classification.id, "complete");
assert.strictEqual(complete.totalGapCount, 0);
assert.strictEqual(complete.gaps.P0.length, 0);
assert.strictEqual(complete.revenueAllowed, true);

const criticalWithoutBackup = core.evaluatePassport({
  facilityType: "business",
  criticalLoadCategories: ["refrigeration"],
  backupSourceClasses: [],
  evidenceStatuses: statuses("current")
}, { now: fixedNow });
assert(criticalWithoutBackup.gaps.P0.some((item) => item.id === "critical-load-without-backup"), "Kritik yük + yedek kaynak yok durumunda P0 oluşmalı.");
assert.strictEqual(criticalWithoutBackup.professionalReviewRequired, true);

const mixedStatuses = statuses("current");
mixedStatuses["critical-load-inventory"] = "missing";
mixedStatuses["grounding-measurement"] = "due";
mixedStatuses["outage-log"] = "planned";
const mixed = core.evaluatePassport({
  facilityType: "site",
  criticalLoadCategories: ["water-pumps", "access"],
  backupSourceClasses: ["generator"],
  evidenceStatuses: mixedStatuses
}, { now: fixedNow });
assert(mixed.score > 0 && mixed.score < 100);
assert.strictEqual(mixed.gaps.P0[0].id, "critical-load-inventory");
assert(mixed.gaps.P1.some((item) => item.id === "grounding-measurement"));
assert(mixed.gaps.P2.some((item) => item.id === "outage-log"));
assert.strictEqual(mixed.nextReviewDate, "2026-08-04", "En yakın P0 hedefi 7 gün olmalı.");

const emergency = core.evaluatePassport({ immediateDanger: true, lifeSupportPresent: true }, { now: fixedNow });
assert.strictEqual(emergency.emergency, true);
assert.strictEqual(emergency.score, null);
assert.strictEqual(emergency.revenueAllowed, false, "Acil durumda gelir CTA'sı yasak olmalı.");

const lifeSupport = core.evaluatePassport({
  facilityType: "other",
  criticalLoadCategories: ["safety"],
  backupSourceClasses: ["ups"],
  evidenceStatuses: statuses("current"),
  lifeSupportPresent: true
}, { now: fixedNow });
assert.strictEqual(lifeSupport.professionalReviewRequired, true);
assert.strictEqual(lifeSupport.lifeSupportPresentAtRuntime, true);

const stored = core.sanitizeStorage({
  facilityType: "hotel",
  criticalLoadCategories: ["communications", "INVALID"],
  backupSourceClasses: ["generator"],
  evidenceStatuses: statuses("current"),
  lifeSupportPresent: true,
  immediateDanger: true,
  name: "Kişisel veri"
}, Date.parse(fixedNow));
assert.strictEqual(stored.lifeSupportPresent, undefined, "Yaşam destek seçimi storage dışında kalmalı.");
assert.strictEqual(stored.immediateDanger, undefined, "Acil tehlike seçimi storage dışında kalmalı.");
assert.strictEqual(stored.name, undefined, "Serbest kişisel veri storage dışında kalmalı.");
assert.deepStrictEqual(stored.criticalLoadCategories, ["communications"]);
assert.strictEqual(core.isStoredPayloadFresh(stored, Date.parse(fixedNow) + 29 * 24 * 60 * 60 * 1000), true);
assert.strictEqual(core.isStoredPayloadFresh(stored, Date.parse(fixedNow) + 31 * 24 * 60 * 60 * 1000), false);

const maturityExport = {
  schemaVersion: 1,
  generatedAt: fixedNow,
  facilityType: "hotel",
  score: 72,
  maturityBand: "Dirençli"
};
const imported = core.parseMaturityImport(maturityExport);
assert.strictEqual(imported.valid, true);
assert.strictEqual(imported.facilityType, "hotel");
assert.strictEqual(imported.maturityReference.score, 72);
assert.strictEqual(imported.sourceType, "export");
assert.strictEqual(core.parseMaturityImport({ score: 80, privacy: { containsPersonalData: true } }).valid, false, "Kişisel veri içerdiği işaretlenen import reddedilmeli.");

const passport = core.createPassportExport(lifeSupport, {
  generatedAt: fixedNow,
  maturityReference: imported.maturityReference
});
assert.strictEqual(passport.schemaVersion, "1.0.0");
assert.strictEqual(passport.score, 100);
assert.strictEqual(passport.privacy.containsPersonalData, false);
assert.strictEqual(passport.privacy.includesLifeSupportFlag, false, "Hassas yük bayrağı export edilmemeli.");
assert.strictEqual(passport.privacy.includesImmediateDangerFlag, false);
assert.strictEqual(passport.privacy.freeTextCollected, false);
assert.strictEqual(passport.maturityReference.score, 72);
assert.strictEqual(passport.evidence.length, 10);
assert(!JSON.stringify(passport).includes("lifeSupportPresentAtRuntime"));

assert.throws(() => core.createPassportExport(emergency), /Geçerli pasaport sonucu/);

const repoRoot = path.resolve(__dirname, "../..");
const schema = JSON.parse(fs.readFileSync(path.join(repoRoot, "alo186/schemas/electric-continuity-passport-v1.schema.json"), "utf8"));
assert.strictEqual(schema.$id, passport.$schema);
assert(schema.required.includes("privacy"));
assert.strictEqual(schema.properties.privacy.properties.containsPersonalData.const, false);
assert.strictEqual(schema.properties.evidence.minItems, 10);
assert.strictEqual(schema.properties.evidence.maxItems, 10);

const analytics = JSON.parse(fs.readFileSync(path.join(repoRoot, "alo186/hesaplama/elektrik-surekliligi-pasaportu/analytics-events.json"), "utf8"));
const eventNames = new Set(analytics.events.map((item) => item.name));
for (const name of [
  "continuity_passport_started",
  "continuity_passport_completed",
  "continuity_passport_emergency_route_shown",
  "continuity_passport_exported",
  "continuity_passport_handoff_created",
  "continuity_passport_panel_clicked"
]) assert(eventNames.has(name), `GA4 sözleşmesinde eksik event: ${name}`);
assert.strictEqual(analytics.privacy.personalDataAllowed, false);

console.log("ALO186 Elektrik Sürekliliği Pasaportu çekirdek, gizlilik, export ve analitik testleri başarılı.");
