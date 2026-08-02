'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const repoRoot = path.resolve(__dirname, '../..');
const read = (relative) => fs.readFileSync(path.join(repoRoot, relative), 'utf8');

const route = '/hesaplama/cozum-sonucu/';
const sourceCanonical = `https://www.alo186.com${route}`;
const toolHtml = read('alo186/hesaplama/cozum-sonucu/index.html');
const toolCore = read('alo186/hesaplama/cozum-sonucu/core.js');
const toolApp = read('alo186/hesaplama/cozum-sonucu/app.js');
const calculatorHub = read('alo186/hesaplama/index.html');
const decisionHtml = read('alo186/karar-motoru/index.html');
const decisionApp = read('alo186/karar-motoru/app.js');
const workshopApp = read('alo186/kesinti-hazirlik-atolyesi/app.js');
const productJourney = read('alo186/urun-eslestirme/journey-retention.js');
const manifest = JSON.parse(read('alo186/deployment/routing-manifest.json'));
const sitemap = read('alo186/sitemap.xml');
const sitemapCanonical = `${manifest.canonicalHost}${route}`;

assert(manifest.version >= 28, 'Routing manifest closed-loop sürümü v28 veya üzeri olmalı.');
assert(manifest.routes.some((item) => item.source === 'alo186/hesaplama/cozum-sonucu/index.html' && item.canonicalPath === route && item.type === 'tool'), 'Çözüm sonucu rotası routing manifestte eksik.');
assert(sitemap.includes(`<loc>${sitemapCanonical}</loc>`), 'Çözüm sonucu rotası sitemapte eksik.');

assert(toolHtml.includes(`rel="canonical" href="${sourceCanonical}"`), 'Çözüm sonucu canonical eksik.');
assert(toolHtml.includes('WebApplication'), 'WebApplication schema eksik.');
assert(toolHtml.includes('FAQPage'), 'FAQPage schema eksik.');
assert(toolHtml.includes('Satın alma gerekmedi'), 'Satın almama kapalı uçlu seçeneği eksik.');
assert(toolHtml.includes('En fazla 12 kayıt'), 'Kayıt üst sınırı görünür değil.');
assert(toolHtml.includes('180 gün'), 'Saklama süresi görünür değil.');
assert(!/<textarea\b/i.test(toolHtml), 'Serbest metin alanı bulunmamalı.');
assert(!/type="(?:email|tel|text)"/i.test(toolHtml), 'Kişisel veri veya serbest metin inputu bulunmamalı.');
assert(!/amazon\.(?:com|com\.tr)/i.test(toolHtml), 'Doğrudan Amazon URL’si bulunmamalı.');

assert(toolCore.includes('MAX_RECORDS = 12'), 'Kayıt üst sınırı core sözleşmesinde eksik.');
assert(toolCore.includes('TTL_DAYS = 180'), 'TTL sözleşmesi eksik.');
assert(toolCore.includes("key: 'resolved_no_purchase'"), 'Satın almasız çözüm kararı eksik.');
assert(toolCore.includes("'unresolved_repeated'"), 'Tekrar eden çözülmemiş karar eksik.');
assert(toolCore.includes("key: 'safety_escalation'"), 'Güvenlik yükseltme kararı eksik.');
assert(!/freeText|notes|address|phone|email|serialNumber|seller|price/i.test(toolCore), 'Core PII veya ticari değişken tutmamalı.');
assert(toolApp.includes("const STORE_KEY = 'alo186:solution-outcomes:v1'"), 'Yerel kayıt anahtarı eksik.');
assert(toolApp.includes('solution_outcome_recorded'), 'Kişisel verisiz sonuç olayı eksik.');
assert(toolApp.includes('localStorage'), 'Local-first kayıt bulunmalı.');

assert(/[3-9][0-9]+ çekirdek araç/.test(calculatorHub), 'Hesaplama merkezi araç sayısı 30 veya üzeri görünmeli.');
assert(calculatorHub.includes('href="./cozum-sonucu/"'), 'Hesaplama merkezi yeni aracı göstermiyor.');
assert(calculatorHub.includes('Satın almama başarı metriği'), 'Kapalı döngü güven ilkesi görünür değil.');

assert(decisionHtml.includes('id="outcomeBtn"'), 'Karar motoru sonuç handoff bağlantısı eksik.');
assert(decisionHtml.includes('/hesaplama/cozum-sonucu/?kaynak=karar-motoru'), 'Karar motoru temel outcome URL’si eksik.');
assert(decisionApp.includes('updateOutcomeLink(result)'), 'Karar motoru dinamik outcome prefili eksik.');
assert(decisionApp.includes("params.set('guvenlik', 'true')"), 'Karar motoru güvenlik sonucunu outcome aracına aktarmıyor.');

assert(workshopApp.includes("kaynak: 'kesinti-atolyesi'"), 'Kesinti atölyesi outcome kaynağını aktarmıyor.');
assert(workshopApp.includes("outcomeAction(selection, 'buy_nothing')"), 'Satın almama sonucu handoff eksik.');
assert(workshopApp.includes("outcomeAction(selection, 'paid_b2b')"), 'Profesyonel rota sonucu handoff eksik.');
assert(workshopApp.includes("outcomeAction(selection, 'affiliate_product_center')"), 'Ürün merkezi sonucu handoff eksik.');

assert(productJourney.includes("id='productOutcomeLoop'") || productJourney.includes("section.id='productOutcomeLoop'"), 'Ürün merkezinde outcome bölümü dinamik olarak oluşturulmuyor.');
assert(productJourney.includes('/hesaplama/cozum-sonucu/?kaynak=urun-secimi&kategori=product_selection'), 'Ürün merkezi outcome rotası eksik.');
assert(productJourney.includes('Sonucu kaydet ve tekrar riskini izle'), 'Ürün merkezi outcome CTA’sı eksik.');

console.log('ALO186 kapalı döngü çözüm sistemi: rota, sitemap, hesap merkezi, karar motoru, atölye, ürün merkezi ve gizlilik sözleşmeleri başarılı.');
