'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '../..');
const portal = fs.readFileSync(path.join(root, 'alo186/index.html'), 'utf8');
const hub = fs.readFileSync(path.join(root, 'alo186/hesaplama/index.html'), 'utf8');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'alo186/deployment/routing-manifest.json'), 'utf8'));

const staleInventory = /\b\d+\s+(?:kişisel veri istemeyen (?:araç|hesaplama ve karar aracı)|kaynak doğrulamalı (?:teknik )?rehber)\b/giu;
assert.equal(
  [...portal.matchAll(staleInventory)].length,
  0,
  'Elektrik Portalı hızlı değişen araç/rehber envanterini sabit sayıyla yayımlamamalı.'
);

assert(portal.includes('kişisel veri istemeyen araçlar'), 'Portal kişisel veri istemeyen araç ailesini görünür anlatmalı.');
assert(portal.includes('kaynak doğrulamalı rehberler'), 'Portal kaynak doğrulamalı rehber ailesini görünür anlatmalı.');
assert(portal.includes('kişisel veri istemeyen hesaplama ve karar araçları'), 'Portal JSON-LD açıklaması araç ailesini çoğul ve sayısız anlatmalı.');
assert(portal.includes('kaynak doğrulamalı teknik rehberler'), 'Portal JSON-LD açıklaması rehber ailesini sayısız anlatmalı.');

const visibleHubCount = Number((hub.match(/<strong>(\d+) çekirdek araç<\/strong>/) || [])[1]);
assert(Number.isInteger(visibleHubCount) && visibleHubCount >= 30, 'Hesaplama merkezi görünür araç sayısı beklenen eşiğin altında.');
assert(manifest.routes.filter((route) => route.type === 'article').length >= 60, 'Routing manifest kaynak doğrulamalı rehber eşiğinin altında.');

console.log('ALO186 portal envanteri: hızla değişen araç ve rehber sayıları sabit pazarlama iddiasından ayrıldı.');
