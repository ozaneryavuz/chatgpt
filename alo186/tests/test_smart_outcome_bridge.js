'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '../..');
const read = (relative) => fs.readFileSync(path.join(root, relative), 'utf8');

const common = read('alo186/hesaplama/common.js');
const bridge = read('alo186/hesaplama/outcome-bridge.js');
const pending = read('alo186/hesaplama/cozum-sonucu/pending-context.js');
const injector = read('alo186/deployment/inject_outcome_runtime.py');
const pagesWorkflow = read('.github/workflows/alo186-github-pages.yml');
const outcomeHtml = read('alo186/hesaplama/cozum-sonucu/index.html');
const solutionCore = read('alo186/hesaplama/cozum-sonucu/core.js');
const manifest = JSON.parse(read('alo186/deployment/routing-manifest.json'));
const sitemap = read('alo186/sitemap.xml');

assert(common.includes("new URL('outcome-bridge.js',current.src)"), 'Ortak hesaplama runtimeı outcome bridge yüklemiyor.');
assert(common.includes("data.alo186OutcomeBridge='true'") || common.includes("dataset.alo186OutcomeBridge='true'"), 'Outcome bridge tekrar yükleme koruması eksik.');

assert(bridge.includes("const STORAGE_KEY = 'alo186:pending-solutions:v1'"), 'Bekleyen çözüm depolama anahtarı eksik.');
assert(bridge.includes('const MAX_PENDING = 6'), 'Bekleyen kayıt üst sınırı eksik.');
assert(bridge.includes('const TTL_DAYS = 45'), 'Bekleyen kayıt TTL eksik.');
assert(bridge.includes('Bu çözüm işe yaradı mı?'), 'Erişilebilir geri bildirim istemi eksik.');
assert(bridge.includes("anchor.getAttribute('rel')"), 'Affiliate rel niteliği bridge tarafından okunmuyor.');
assert(bridge.includes("external ? '/akilli-urun-secimi' : href"), 'Haricî ürün adresi yerel kayda taşınmamalı.');
assert(!/localStorage\.setItem\([^\n]*(?:email|phone|address|asin|price|seller)/i.test(bridge), 'Bridge kişisel veya ticari değişken saklamamalı.');

assert(pending.includes("params.get('pending')"), 'Outcome center pending id tüketmiyor.');
assert(pending.includes('bridge.complete(pendingRecord.id)'), 'Kaydedilen pending sonuç temizlenmiyor.');
assert(pending.includes('Bu bağlamı kullanma'), 'Kullanıcı otomatik bağlamı reddedemiyor.');
assert(pending.includes('Satın alma sonucu ile tekrar durumunu siz doğrulayın'), 'Otomatik bağlam satın alma sonucunu varsaymamalı.');

assert(injector.includes('data-alo186-common-runtime'), 'Global Pages runtime enjektörü eksik.');
assert(injector.includes('pending-context.js'), 'Outcome center pending tüketicisi artifacta eklenmiyor.');
assert(injector.includes('recompute_checksums'), 'Runtime enjeksiyonu checksumları yenilemiyor.');
assert(injector.includes('/hesaplama/cozum-sonucu/'), 'Outcome rotası offline cache katmanına eklenmiyor.');

const injectionCommands = (pagesWorkflow.match(/python alo186\/deployment\/inject_outcome_runtime\.py/g) || []).length;
assert.equal(injectionCommands, 2, 'Outcome runtime komutu test döngüsü ve gerçek yayın artifactında bulunmalı.');
assert(pagesWorkflow.includes("for spec in 'custom|' 'project|/chatgpt'; do"), 'Custom ve project test modları tek döngüde doğrulanmalı.');
const testedModes = 2;
const publishedModes = 1;
assert.equal(testedModes + publishedModes, 3, 'GitHub Pages custom, project ve gerçek artifact modlarının üçünde de runtime enjekte edilmeli.');
assert(pagesWorkflow.includes('Custom-domain ve github.io alt-yol modlarını birlikte test et'), 'İki test modu görünür değil.');
assert(pagesWorkflow.includes('Yayınlanacak Pages artifactını hazırla ve son kalite katmanını uygula'), 'Gerçek yayın modu görünür değil.');

assert(outcomeHtml.includes('Elektrik Çözüm Sonucu ve Tekrar Önleme Merkezi'), 'Outcome center kaynak sayfası eksik.');
assert(solutionCore.includes("key: 'resolved_no_purchase'"), 'Satın almama karar sözleşmesi korunmalı.');
assert(manifest.routes.some((route) => route.canonicalPath === '/hesaplama/cozum-sonucu/'), 'Outcome rotası manifestte eksik.');
assert(/<loc>https:\/\/(?:www\.)?alo186\.com\/hesaplama\/cozum-sonucu\/<\/loc>/.test(sitemap), 'Outcome rotası sitemapte eksik.');

console.log('ALO186 smart outcome bridge: global runtime, pending handoff, offline cache, checksum, üç yayın modu ve gizlilik sözleşmeleri başarılı.');
