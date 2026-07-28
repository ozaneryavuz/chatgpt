'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const core = require('./core.js');

const now = new Date('2026-07-28T12:00:00.000Z');

const alias = core.sanitizeInput({ source: 'karar-motoru', category: 'panel', action: 'electrician', outcome: 'partial' });
assert.equal(alias.source, 'decision_engine');
assert.equal(alias.category, 'indoor_fault');

const noPurchase = core.deriveDecision({
  source: 'decision_engine',
  category: 'outage_official',
  action: 'official_channel',
  outcome: 'resolved',
  recurrence: 'none',
  purchase: 'no_purchase'
});
assert.equal(noPurchase.key, 'resolved_no_purchase');
assert.equal(noPurchase.revenueAllowed, false);
assert.match(noPurchase.title, /satın alma olmadan/i);
assert.doesNotMatch(JSON.stringify(noPurchase.actions), /amazon/i);

const productWorked = core.deriveDecision({
  source: 'product_center',
  category: 'product_selection',
  action: 'product',
  outcome: 'resolved',
  recurrence: 'none',
  purchase: 'new_product'
});
assert.equal(productWorked.key, 'resolved_product');
assert.match(productWorked.title, /yeni ürün aramayın/i);
assert.ok(productWorked.actions.every((item) => !/akilli-urun-secimi|amazon/i.test(item.href)));

const repeated = core.deriveDecision({
  source: 'calculator',
  category: 'backup_power',
  action: 'free_tool',
  outcome: 'unresolved',
  recurrence: 'multiple',
  purchase: 'not_applicable'
});
assert.equal(repeated.key, 'unresolved_repeated');
assert.match(repeated.actions[0].href, /kurumsal-elektrik-surekliligi-on-degerlendirme/);
assert.equal(repeated.revenueAllowed, false);

const emergency = core.deriveDecision({
  source: 'guide',
  category: 'indoor_fault',
  action: 'maintenance',
  outcome: 'safety',
  recurrence: 'once',
  purchase: 'not_applicable'
});
assert.equal(emergency.key, 'safety_escalation');
assert.equal(emergency.followupDays, 0);
assert.equal(emergency.actions[0].href, 'tel:112');

const record = core.normalizeRecord({
  id: 'safe_record_1',
  source: 'outage_workshop',
  category: 'backup_power',
  action: 'existing_equipment',
  outcome: 'resolved',
  recurrence: 'none',
  purchase: 'existing'
}, now);
assert.equal(record.id, 'safe_record_1');
assert.equal(record.dueAt, '2026-10-26T12:00:00.000Z');
assert.ok(core.isValidRecord(record));

const oldRecord = { ...record, id: 'old', createdAt: '2025-01-01T00:00:00.000Z' };
const many = Array.from({ length: 15 }, (_, index) => ({
  ...record,
  id: `record_${index}`,
  createdAt: new Date(now.getTime() - index * 1000).toISOString()
}));
const pruned = core.pruneRecords([oldRecord, ...many], now);
assert.equal(pruned.length, core.MAX_RECORDS);
assert.equal(pruned[0].id, 'record_0');
assert.ok(!pruned.some((item) => item.id === 'old'));

const unresolvedRecord = core.normalizeRecord({
  id: 'unresolved_1',
  source: 'calculator',
  category: 'protection',
  action: 'free_tool',
  outcome: 'unresolved',
  recurrence: 'multiple',
  purchase: 'not_applicable'
}, now);
const summary = core.summarizeRecords([record, unresolvedRecord], now);
assert.equal(summary.total, 2);
assert.equal(summary.resolved, 1);
assert.equal(summary.resolutionRate, 50);
assert.equal(summary.noPurchaseRate, 50);
assert.equal(summary.recurrenceRate, 50);

const ics = core.buildCalendar(record, 'https://www.alo186.com');
assert.match(ics, /BEGIN:VCALENDAR/);
assert.match(ics, /DTSTART;VALUE=DATE:20261026/);
assert.match(ics, /https:\/\/www\.alo186\.com\/hesaplama\/ekipman-bakim-plani\//);
assert.doesNotMatch(ics, /ATTENDEE|ORGANIZER|LOCATION|EMAIL|TEL/i);

const exported = core.exportPayload([record], now);
assert.equal(exported.schema, 'alo186-solution-outcomes-v1');
assert.equal(exported.records.length, 1);
assert.match(exported.privacy, /Kişisel veri/);
assert.doesNotMatch(JSON.stringify(exported), /address|phone|email|subscriber|serial|price|seller/i);

const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
assert.match(html, /https:\/\/www\.alo186\.com\/hesaplama\/cozum-sonucu\//);
assert.match(html, /WebApplication/);
assert.match(html, /FAQPage/);
assert.match(html, /Satın alma gerekmedi/);
assert.match(html, /180 gün/);
assert.doesNotMatch(html, /type="(?:email|tel|text)"/i);
assert.doesNotMatch(html, /amazon\.(?:com|com\.tr)/i);
assert.doesNotMatch(html, /name="(?:address|phone|email|subscription|tc|identity|serial|note)"/i);

console.log('ALO186 çözüm sonucu: karar, satın almama, tekrar, güvenlik, yerel kayıt, takvim ve gizlilik testleri başarılı.');
