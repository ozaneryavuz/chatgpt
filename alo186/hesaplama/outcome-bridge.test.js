'use strict';

const assert = require('node:assert/strict');
const bridge = require('./outcome-bridge.js');

const now = new Date('2026-07-28T12:00:00.000Z');
bridge.clear();

assert.equal(bridge.sanitizePath('/hesaplama/ups-suresi/?w=900#sonuc'), '/hesaplama/ups-suresi/');
assert.equal(bridge.sanitizePath('https://www.alo186.com/karar-motoru?x=1'), '/karar-motoru');
assert.equal(bridge.sanitizePath('https://www.amazon.com.tr/dp/B0SECRET?tag=affiliate'), '', 'Haricî ürün yolu veya ASIN yerel kayda alınmamalı.');
assert.equal(bridge.sanitizePath('mailto:test@example.com'), '');

assert.equal(bridge.inferSourceFromPath('/karar-motoru'), 'decision_engine');
assert.equal(bridge.inferSourceFromPath('/haberler/ups-surekli-otuyor-bip-sesi-ne-anlama-gelir'), 'guide');
assert.equal(bridge.inferCategoryFromPath('/hesaplama/ev-sarj-kablosu-uygunluk/'), 'ev_charging');
assert.equal(bridge.inferCategoryFromPath('/hesaplama/power-station-kapasite-eps-uygunluk/'), 'backup_power');
assert.equal(bridge.inferCategoryFromPath('/haberler/ges-inverter-afci-dc-ark-hatasi'), 'solar_storage');
assert.equal(bridge.inferActionFromTarget('tel:112'), null);
assert.equal(bridge.inferActionFromTarget('tel:186'), 'official_channel');
assert.equal(bridge.inferActionFromTarget('/kurumsal-elektrik-surekliligi-on-degerlendirme'), 'professional_service');
assert.equal(bridge.inferActionFromTarget('https://www.amazon.com.tr/s?k=ups', 'sponsored nofollow'), 'product');

const calculator = bridge.sanitizeContext({
  id: 'calc_1',
  source: 'hesaplayici',
  category: 'power_station',
  action: 'free_tool',
  originPath: '/hesaplama/power-station-kapasite-eps-uygunluk/?capacity=1000',
  recommendedPath: '/akilli-urun-secimi?kategori=power_station'
}, now);
assert.equal(calculator.source, 'calculator');
assert.equal(calculator.category, 'backup_power');
assert.equal(calculator.originPath, '/hesaplama/power-station-kapasite-eps-uygunluk/');
assert.equal(calculator.recommendedPath, '/akilli-urun-secimi');
assert.equal(calculator.askAfter, '2026-07-29T00:00:00.000Z');
assert.equal(calculator.expiresAt, '2026-09-11T12:00:00.000Z');

const first = bridge.start(calculator, now);
const duplicate = bridge.start(calculator, now);
assert.equal(first.id, duplicate.id, 'Aynı çözüm yolculuğu tekrar tekrar bekleyen kayıt üretmemeli.');
assert.equal(bridge.eligible(new Date('2026-07-28T23:59:59.000Z')).length, 0);
assert.equal(bridge.eligible(new Date('2026-07-29T00:00:01.000Z')).length, 1);

const url = bridge.buildOutcomeUrl(first, 'resolved');
assert.match(url, /^\/hesaplama\/cozum-sonucu\/\?/);
assert.match(url, /pending=calc_1/);
assert.match(url, /kaynak=calculator/);
assert.match(url, /kategori=backup_power/);
assert.match(url, /sonuc=resolved/);
assert.doesNotMatch(url, /capacity|ASIN|amazon/i);

assert.equal(bridge.dismiss(first.id, new Date('2026-07-29T01:00:00.000Z')), true);
assert.equal(bridge.eligible(new Date('2026-07-30T01:00:00.000Z')).length, 0);
assert.equal(bridge.eligible(new Date('2026-08-05T01:00:01.000Z')).length, 1);
assert.equal(bridge.complete(first.id), true);
assert.equal(bridge.get(first.id), null);

assert.equal(bridge.start({ safety: true, source: 'decision_engine', category: 'indoor_fault' }, now), null);

const product = bridge.start({
  id: 'product_1',
  source: 'product_center',
  category: 'powerbank',
  action: 'product',
  originPath: '/akilli-urun-secimi?kategori=powerbank',
  recommendedPath: 'https://www.amazon.com.tr/dp/B0SECRET?tag=affiliate'
}, now);
assert.equal(product.category, 'product_selection');
assert.equal(product.recommendedPath, '');
assert.doesNotMatch(JSON.stringify(product), /B0SECRET|tag=|amazon/i);
assert.equal(product.askAfter, '2026-07-31T12:00:00.000Z');

bridge.clear();
assert.equal(bridge.eligible(new Date('2026-08-10T00:00:00.000Z')).length, 0);

console.log('ALO186 akıllı outcome bridge: gizlilik, enum, gecikme, tekilleştirme, prompt ve sonuç URL testleri başarılı.');
