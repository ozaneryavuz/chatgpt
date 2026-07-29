'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const repoRoot = path.resolve(__dirname, '../..');
const productRoot = path.join(repoRoot, 'alo186', 'urun-eslestirme');
const catalog = require(path.join(productRoot, 'catalog.js'));
const conversion = require(path.join(productRoot, 'conversion-growth-core.js'));
const retention = require(path.join(productRoot, 'journey-retention-core.js'));

assert.equal(catalog.categories.length, 18, 'Ürün merkezi 18 kullanıcı niyetini korumalı.');
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
const hubCategory = catalog.getCategory('usb_c_hub');
const displayCategory = catalog.getCategory('display_cable');
assert(chargerCategory&&cableCategory&&hubCategory&&displayCategory, 'USB-C şarj, kablo, hub ve görüntü niyetleri katalogda bulunmalı.');
for(const category of [chargerCategory,cableCategory,hubCategory,displayCategory])assert.equal(category.affiliatePolicy, 'verified_direct');

const evQuery = conversion.buildQuery('ev_cable', { current: '32', phase: 'three', length: '7_5' });
assert.match(evQuery, /Type 2/i);
assert.match(evQuery, /32A/);
assert.match(evQuery, /trifaze 22kW/);
assert.match(evQuery, /7\.5 metre/);

const evUrl = conversion.buildAffiliateUrl('ev_cable', { current: '32', phase: 'three', length: '7_5' });
assert.match(evUrl, /^https:\/\/www\.amazon\.com\.tr\/s\?k=/);
assert.equal(new URL(evUrl).searchParams.get('tag'), catalog.affiliateTag);

assert.deepEqual(conversion.gateStatus('ev_cable', { toolConfirmed: false, existingInsufficient: true, affiliateAccepted: true }),{ allowed: false, reason: 'tool_not_confirmed' });
assert.deepEqual(conversion.gateStatus('ev_cable', { toolConfirmed: true, existingInsufficient: false, affiliateAccepted: true }),{ allowed: false, reason: 'existing_may_be_sufficient' });
assert.deepEqual(conversion.gateStatus('ev_cable', { toolConfirmed: true, existingInsufficient: true, affiliateAccepted: false }),{ allowed: false, reason: 'affiliate_not_accepted' });
assert.deepEqual(conversion.gateStatus('ev_cable', { toolConfirmed: true, existingInsufficient: true, affiliateAccepted: true }),{ allowed: true, reason: 'qualified_search' });
assert.equal(conversion.gateStatus('generator', {}).reason, 'professional_only');
assert.equal(conversion.getProfile('outlet_tester'), null);
assert.equal(conversion.getProfile('co_alarm'), null, 'CO alarmı yalnız özel güvenlik aracı sonrasında değerlendirilmelidir.');
assert.equal(conversion.getProfile('extension_cord'), null, 'Uzatma kablosu yalnız özel uygunluk aracı sonrasında değerlendirilmelidir.');

const professionalRoute = conversion.professionalRoute('generator');
assert.match(professionalRoute, /^\/kurumsal-elektrik-surekliligi-on-degerlendirme\?/);
assert.match(professionalRoute, /source=product_center/);
assert.match(professionalRoute, /category=generator/);
assert.match(professionalRoute, /problem=backup/);
assert.match(professionalRoute, /backup=generator/);
assert.match(professionalRoute, /scope=comparison/);

const review = retention.normalizeReview({ category: 'surge_strip', reason: 'catalog_refresh', reviewDays: 30, createdAt: '2026-07-28' },new Date('2026-07-28T12:00:00Z'));
assert.equal(review.reviewDate, '2026-08-27');
const ics = retention.buildReviewIcs(review, { origin: 'https://www.alo186.com' });
assert.match(ics, /BEGIN:VCALENDAR/);
assert.match(ics, /DTSTART;VALUE=DATE:20260827/);
assert.match(ics, /SUMMARY:ALO186 yeniden kontrol/);
assert.match(ics, /URL:https:\/\/www\.alo186\.com\/akilli-urun-secimi\?kategori=surge_strip/);
assert.match(ics, /Mevcut ürün yeterliyse yeni satın alma gerekli değildir/);
assert.doesNotMatch(ics, /ATTENDEE|ORGANIZER|mailto:|Fiyat|Stok|Garanti/i);
assert.equal(retention.calendarFilename(review), 'alo186-surge_strip-2026-08-27.ics');

const app = fs.readFileSync(path.join(productRoot, 'app.js'), 'utf8');
const conversionUi = fs.readFileSync(path.join(productRoot, 'conversion-growth.js'), 'utf8');
const conversionCore = fs.readFileSync(path.join(productRoot, 'conversion-growth-core.js'), 'utf8');
const retentionUi = fs.readFileSync(path.join(productRoot, 'journey-retention.js'), 'utf8');
const styles = fs.readFileSync(path.join(productRoot, 'conversion-growth.css'), 'utf8');
const corporate = fs.readFileSync(path.join(repoRoot, 'alo186', 'kurumsal-on-degerlendirme', 'app.js'), 'utf8');

assert.doesNotMatch(app, /data-filtered-search/);
assert.doesNotMatch(app, /data-guide-amazon/);
assert.doesNotMatch(app, /\/iletisim\?konu=urun-teknik-secim/);
assert.match(app, /Ücretli teknik ön değerlendirme/);
assert.match(app, /co_alarm/);
assert.match(conversionUi, /qualifiedAffiliateAccepted/);
assert.match(conversionUi, /qualifiedExistingInsufficient/);
assert.match(conversionUi, /rel="sponsored nofollow noopener"/);
assert.match(conversionUi, /Şimdilik satın alma/);
assert.match(conversionUi, /ALO186 resmî kurum, EDAŞ veya ürün satıcısı değildir/);
assert.match(conversionCore, /after_tool/);
assert.match(conversionCore, /professionalProfiles/);
assert.match(retentionUi, /Takvime ekle \(\.ics\)/);
assert.match(retentionUi, /conversion-growth-core\.js/);
assert.match(retentionUi, /conversion-growth\.js/);
assert.match(corporate, /sourceProfiles/);
assert.match(corporate, /paid_assessment_source_prefilled/);
assert.match(corporate, /source_category/);
assert.match(styles, /min-height:48px/);
assert.match(styles, /@media\(max-width:760px\)/);

for (const text of [conversionUi, conversionCore, retentionUi]) {
  assert.doesNotMatch(text, /type="(?:email|tel|text)"/i);
  assert.doesNotMatch(text, /priceCurrency|availability|aggregateRating/i);
}

const cleanEvent = conversion.sanitizeEvent({category: 'ev_cable',status: 'opened',placement: 'qualified_search',email: 'blocked@example.com'});
assert.deepEqual(cleanEvent, { category: 'ev_cable', status: 'opened', placement: 'qualified_search' });
assert.equal(conversion.hasForbiddenEventData({ category: 'ev_cable', email: 'blocked@example.com' }), true);
assert.equal(conversion.hasForbiddenEventData({ category: 'ev_cable', status: 'opened' }), false);

console.log('ALO186 güvenli gelir dönüşümü: 18 niyet, USB-C hub/görüntü doğrudan ürünleri, uzatma kablosu/CO güvenlik kapıları, teknik arama, satın almama, profesyonel rota, ICS ve PII korumaları başarılı.');