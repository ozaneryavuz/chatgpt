'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '../..');
const portal = fs.readFileSync(path.join(root, 'alo186/index.html'), 'utf8');
const hub = fs.readFileSync(path.join(root, 'alo186/hesaplama/index.html'), 'utf8');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'alo186/deployment/routing-manifest.json'), 'utf8'));

const staleInventory = /\b\d+\s+(?:kişisel veri istemeyen (?:araç|hesaplama ve karar aracı)|kaynak doğrulamalı (?:teknik )?rehber)\b/giu;
const head = (portal.match(/<head>[\s\S]*?<\/head>/i) || [''])[0];
const jsonLdMatch = head.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/i);
assert(jsonLdMatch, 'Portal CollectionPage JSON-LD taşımalı.');
const jsonLd = JSON.parse(jsonLdMatch[1]);
const jsonLdDescription = String(jsonLd.description || '').toLocaleLowerCase('tr-TR');

assert.equal(
  [...portal.matchAll(staleInventory)].length,
  0,
  'Elektrik Portalı hızlı değişen araç/rehber envanterini sabit sayıyla yayımlamamalı.'
);
assert.equal(
  [...head.matchAll(staleInventory)].length,
  0,
  'Meta açıklaması ve JSON-LD hızlı değişen envanteri sabit sayıyla yayımlamamalı.'
);

assert(portal.includes('kişisel veri istemeyen araçlar'), 'Portal kişisel veri istemeyen araç ailesini görünür anlatmalı.');
assert(portal.includes('kaynak doğrulamalı rehberler'), 'Portal kaynak doğrulamalı rehber ailesini görünür anlatmalı.');
assert(jsonLdDescription.includes('kişisel veri istemeyen') && jsonLdDescription.includes('araçlar'), 'Portal JSON-LD açıklaması kişisel veri istemeyen araç ailesini semantik olarak anlatmalı.');
assert(jsonLdDescription.includes('kaynak doğrulamalı') && jsonLdDescription.includes('rehberler'), 'Portal JSON-LD açıklaması kaynak doğrulamalı rehber ailesini semantik olarak anlatmalı.');
assert.equal(jsonLd['@type'], 'CollectionPage', 'Portal JSON-LD türü CollectionPage olmalı.');

const visibleHubCount = Number((hub.match(/<strong>(\d+) çekirdek araç<\/strong>/) || [])[1]);
assert(Number.isInteger(visibleHubCount) && visibleHubCount >= 30, 'Hesaplama merkezi görünür araç sayısı beklenen eşiğin altında.');
assert(manifest.routes.filter((route) => route.type === 'article').length >= 60, 'Routing manifest kaynak doğrulamalı rehber eşiğinin altında.');

console.log('ALO186 portal envanteri: değişken sayılar sabit pazarlama iddiasından ayrıldı ve JSON-LD semantik olarak doğrulandı.');
