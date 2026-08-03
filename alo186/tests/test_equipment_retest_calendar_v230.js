const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const route = path.join(root, 'hesaplama', 'elektrik-ekipmani-tekrar-test-takvimi');
const html = fs.readFileSync(path.join(route, 'index.html'), 'utf8');
const app = fs.readFileSync(path.join(route, 'app.js'), 'utf8');
const overlay = JSON.parse(fs.readFileSync(path.join(root, 'deployment', 'routing-overlays', '230-equipment-retest-calendar.json'), 'utf8'));

for (const token of [
  'Elektrik Ekipmanı Tekrar Test Takvimi',
  '30 gün',
  '90 gün',
  '365 gün',
  'Kişisel veri yok',
  'Doğrudan mağaza bağlantısı yok',
  'Mevcut ürün yeterliyse yenisini almayın',
  'ALO186 EDAŞ, TEDAŞ, EPDK veya kamu kurumu değildir',
  'WebApplication',
  'FAQPage',
  'BreadcrumbList',
  'id="retestForm"',
  'id="result"'
]) {
  if (!html.includes(token)) throw new Error(`HTML sözleşmesi eksik: ${token}`);
}

for (const token of [
  'BEGIN:VCALENDAR',
  'equipment_retest_calendar_download',
  'equipment_retest_plan_created',
  'equipment_retest_blocked',
  'status === "damaged"',
  'Mevcut güvenli çözüm yeterliyse yeni ürün almayın',
  'URL.createObjectURL',
  'text/calendar;charset=utf-8'
]) {
  if (!app.includes(token)) throw new Error(`Uygulama sözleşmesi eksik: ${token}`);
}

if (/amazon\.com\.tr|amzn\.to/i.test(html + app)) throw new Error('Doğrudan Amazon bağlantısı bulunmamalı');
if (/"@type"\s*:\s*"(?:Product|Offer|AggregateRating)"/i.test(html)) throw new Error('Ticari ürün şeması bulunmamalı');
if (/\b(?:fiyat|stokta|puan|garanti süresi)\b/i.test(html)) throw new Error('Doğrulanmamış ticari alan bulunmamalı');
if (/<input\b[^>]*type=["'](?:text|email|tel|number)["']/i.test(html)) throw new Error('Kişisel veya serbest veri alanı bulunmamalı');
if (overlay.version !== 230) throw new Error('Routing sürümü yanlış');
if (overlay.routes?.length !== 1) throw new Error('Tek rota sözleşmesi bozuk');
if (overlay.routes[0].canonicalPath !== '/hesaplama/elektrik-ekipmani-tekrar-test-takvimi/') throw new Error('Canonical rota yanlış');
if (overlay.routes[0].type !== 'calculator') throw new Error('Rota tipi yanlış');

console.log(JSON.stringify({
  ok: true,
  version: overlay.version,
  route: overlay.routes[0].canonicalPath,
  directAffiliateLinksAdded: 0,
  personalFieldsAdded: 0,
  intervals: [30, 90, 365]
}));
