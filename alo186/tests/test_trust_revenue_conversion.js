'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const repoRoot = path.resolve(__dirname, '../..');
const productRoot = path.join(repoRoot, 'alo186', 'urun-eslestirme');
const catalog = require(path.join(productRoot, 'catalog.js'));
const conversion = require(path.join(productRoot, 'conversion-growth-core.js'));
const retention = require(path.join(productRoot, 'journey-retention-core.js'));

assert.equal(catalog.categories.length, 16, 'Ürün merkezi 16 kullanıcı niyetini korumalı.');
const coCategory = catalog.getCategory('co_alarm');
assert(coCategory, 'CO alarmı güvenlik niyeti katalogda bulunmalı.');
assert.equal(coCategory.affiliatePolicy, 'after_tool');
assert.equal(catalog.productsFor('co_alarm').length, 0, 'CO alarmında doğrulanmış ürün olmadan doğrudan kart açılamaz.');
const extensionCategory = catalog.getCategory('extension_cord');
assert(extensionCategory, 'Uzatma kablosu güvenlik niyeti katalogda bulunmalı.');
assert.equal(extensionCategory.affiliatePolicy, 'after_tool');
assert.match(extensionCategory.nextStepUrl, /uzatma-kablosu-kablo-makarasi-uygunluk/);
assert.equal(catalog.productsFor('extension_cord').length, 0, 'Uzatma kablosunda doğrulanmış ürün olmadan doğrudan kart açılamaz.');
const chargerCategory = catalog.getCategory('usb_c_charger');
const cableCategory = catalog.getCategory('usb_c_cable');
assert(chargerCategory&&cableCategory, 'USB-C şarj cihazı ve kablo niyetleri katalogda bulunmalı.');
assert.equal(chargerCategory.affiliatePolicy, 'verified_direct');
assert.equal(cableCategory.affiliatePolicy, 'verified_direct');

const evQuery = conversion.buildQuery('ev_cable', { current: '32', phase: 'three', length: '7_5' });
assert.match(evQuery, /Type 2/i);
assert.match(evQuery, /32A/);
assert.match(evQuery, /trifaze 22kW/);
assert.match(evQuery, /7\.5 metre/);

const evUrl = conversion.buildAffiliateUrl('ev_cable', { current: '32', phase: 'three', length: '7_5' });
assert.match(evUrl, /amazon\.com\.tr/);
assert.match(evUrl, /tag=alo186rehber-21/);
assert.match(evUrl, /Type%202/);

const smartQuery = conversion.buildQuery('smart_plug', { current: '16', motor: 'yes', history: 'yes' });
assert.match(smartQuery, /16A/);
assert.match(smartQuery, /motor/);
assert.match(smartQuery, /kWh geçmiş kayıt/);

const allowedKeys = new Set(['category', 'status', 'placement', 'timestamp', 'sessionId']);
assert.deepEqual(
  new Set(conversion.sanitizeEvent({ category: 'ev_cable', status: 'opened', placement: 'tool', email: 'blocked@example.com', phone: 'blocked' }).keys || []),
  new Set(),
);
const cleanEvent = conversion.sanitizeEvent({ category: 'ev_cable', status: 'opened', placement: 'tool' });
assert.deepEqual(Object.keys(cleanEvent).every(key => allowedKeys.has(key)), true);

assert.equal(conversion.gateStatus('generator', {}).reason, 'professional_only');
assert.equal(conversion.getProfile('outlet_tester'), null);
assert.equal(conversion.getProfile('co_alarm'), null, 'CO alarmı yalnız özel güvenlik aracı sonrasında değerlendirilmelidir.');
assert.equal(conversion.getProfile('extension_cord'), null, 'Uzatma kablosu yalnız özel uygunluk aracı sonrasında değerlendirilmelidir.');

const professionalRoute = conversion.professionalRoute('generator');
assert.match(professionalRoute, /^\/kurumsal-elektrik-surekliligi-on-degerlendirme\?/);

const noBuy = conversion.noBuyOutcome('surge_strip', { existingAdequate: true });
assert.equal(noBuy.shouldBuy, false);
assert.match(noBuy.message, /satın almayın/i);

const retentionRecord = retention.createRecord('surge_strip', { outcome: 'no_buy', reviewDays: 90 });
assert.equal(retentionRecord.category, 'surge_strip');
assert.equal(retentionRecord.reviewDays, 90);
assert.match(retention.createIcs(retentionRecord), /BEGIN:VCALENDAR/);

const files = [
  path.join(repoRoot, 'alo186', 'akilli-urun-secimi', 'index.html'),
  path.join(productRoot, 'catalog.js'),
  path.join(productRoot, 'conversion-growth-core.js'),
  path.join(productRoot, 'journey-retention-core.js'),
];
for (const file of files) assert(fs.existsSync(file), file);

assert.equal(conversion.hasForbiddenEventData({ category: 'ev_cable', email: 'blocked@example.com' }), true);
assert.equal(conversion.hasForbiddenEventData({ category: 'ev_cable', status: 'opened' }), false);

console.log('ALO186 güvenli gelir dönüşümü: 16 niyet, USB-C doğrudan ürünleri, uzatma kablosu/CO güvenlik kapıları, teknik arama, satın almama, profesyonel rota, ICS ve PII korumaları başarılı.');
