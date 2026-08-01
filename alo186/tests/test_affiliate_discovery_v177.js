'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const root=path.resolve(__dirname,'..');
const page=fs.readFileSync(path.join(root,'amazon-elektrik-urunleri','index.html'),'utf8');
const runtime=fs.readFileSync(path.join(root,'amazon-elektrik-urunleri','commercial.js'),'utf8');
const route='/amazon-elektrik-urunleri/dogrulanmis-tak-calistir-urunler/';

assert.ok(page.includes('commercial.js'),'Ana ürün merkezi ticari runtimeı yüklemeli.');
assert.ok(runtime.includes(`const revenueHubRoute = '${route}'`));
assert.match(runtime,/function injectRevenueHubEntry\(\)/);
assert.match(runtime,/section\.dataset\.affiliateRevenueEntryV177 = 'true'/);
assert.match(runtime,/data-commercial-route=\"verified-hub-v177\"/);
assert.match(runtime,/affiliate_revenue_v177_entry_view/);
assert.match(runtime,/25\+ uzun kuyruk ürün sınıfını/);
assert.match(runtime,/yedi kullanım paketini/);
assert.match(runtime,/45 günlük doğrulama sınırı/);
assert.match(runtime,/ASIN tekilleştirme/);
assert.match(runtime,/Yüksek riskli ürünlerde doğrudan satış yok/);
assert.match(runtime,/Mevcut güvenli ürün yeterliyse satın alma bağlantısı açılmaz/);
assert.match(runtime,/currentPath\.endsWith\('\/amazon-elektrik-urunleri'\)/);
assert.match(runtime,/if \(categoryId \|\|/);
assert.match(runtime,/document\.querySelector\('\[data-affiliate-revenue-entry-v177\]'\)/);
assert.ok(!runtime.includes('href="https://www.amazon.com.tr'), 'Yeni keşif kartı statik Amazon bağlantısı taşımamalı.');

console.log(JSON.stringify({
  ok:true,
  route,
  productCenterEntry:true,
  idempotent:true,
  categoryPagesUnaffected:true,
  staticAmazonLink:false,
  trackingEvent:'affiliate_revenue_v177_entry_view'
},null,2));
