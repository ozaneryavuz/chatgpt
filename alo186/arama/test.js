'use strict';

const assert = require('node:assert/strict');
const core = require('./core.js');

assert.equal(core.normalize('Kaçak Akım Rölesi'), 'kacak akim rolesi');
assert.deepEqual(core.tokens('UPS UPS akü'), ['ups', 'aku']);
assert(core.compactTokens('elektrik çarpması').includes('elektrikcarpmasi'));

const safety = core.detectIntents('panoda duman ve elektrik çarpması');
assert.equal(safety.safety, true);
assert.equal(safety.official, false);

const official = core.detectIntents('EDAŞ düşük voltaj teknik kalite ölçümü');
assert.equal(official.official, true);
assert.equal(official.safety, false);

const product = core.detectIntents('hangi power station uygun hesapla');
assert.equal(product.product, true);
assert.equal(product.tool, true);

const entries = [
  {
    canonicalPath: '/karar-motoru',
    bucket: 'tool',
    title: '186 mı, 112 mi, elektrikçi mi?',
    h1: 'Elektrik sorunu karar motoru',
    description: 'Duman, yangın, elektrik çarpması ve şebeke sorununda doğru kanalı bulun.',
    excerpt: '',
    topics: ['Elektrik çarpması', '112', '186'],
    priority: 120,
    featured: true
  },
  {
    canonicalPath: '/haberler/elektrik-panosunda-termal-kamera-kontrolu',
    bucket: 'article',
    title: 'Elektrik panosunda termal kamera kontrolü',
    h1: 'Termal kamera pano arızasını gösterir mi?',
    description: 'Sıcak nokta ve bağlantı problemleri.',
    excerpt: 'Pano sıcaklık kontrolü.',
    topics: ['Pano', 'Termografi'],
    priority: 50,
    featured: false
  },
  {
    canonicalPath: '/hesaplama/power-station-kapasite-eps-uygunluk/',
    bucket: 'tool',
    title: 'Power Station Kapasite ve EPS Uygunluğu',
    h1: 'Power station kaç Wh ve W olmalı?',
    description: 'Sürekli güç, tepe güç, çalışma süresi ve EPS geçişini hesaplayın.',
    excerpt: '',
    topics: ['Power station', 'Wh', 'EPS'],
    priority: 78,
    featured: true
  },
  {
    canonicalPath: '/akilli-urun-secimi',
    bucket: 'tool',
    title: 'Akıllı Ürün Merkezi',
    h1: 'Teknik ürün sınıfını belirleyin',
    description: 'Teknik araçtan sonra şeffaf ürün karşılaştırması.',
    excerpt: '',
    topics: ['Ürün seçimi'],
    priority: 65,
    featured: false
  },
  {
    canonicalPath: '/edas-bul',
    bucket: 'tool',
    title: 'Türkiye EDAŞ Bulucu',
    h1: 'Doğru dağıtım şirketini bulun',
    description: 'Kesinti, sayaç ve teknik kalite için resmî dağıtım kanalına ilerleyin.',
    excerpt: '',
    topics: ['EDAŞ', '186', 'Teknik kalite'],
    priority: 115,
    featured: true
  }
];

const emergencyResults = core.searchEntries(entries, 'panoda duman elektrik çarpması');
assert.equal(emergencyResults[0].canonicalPath, '/karar-motoru', 'Acil sorguda karar motoru ilk sırada olmalı.');

const voltageResults = core.searchEntries(entries, 'EDAŞ teknik kalite ölçümü');
assert.equal(voltageResults[0].canonicalPath, '/edas-bul', 'Resmî teknik kalite sorgusunda EDAŞ bulucu ilk sırada olmalı.');

const powerResults = core.searchEntries(entries, 'power station kaç Wh uygun');
assert.equal(powerResults[0].canonicalPath, '/hesaplama/power-station-kapasite-eps-uygunluk/');
assert.notEqual(powerResults[0].canonicalPath, '/akilli-urun-secimi', 'Ürün sorgusunda önce uygunluk aracı gelmeli.');

const toolsOnly = core.searchEntries(entries, 'power station', 'tool');
assert(toolsOnly.every((entry) => entry.bucket === 'tool'));

const featured = core.searchEntries(entries, '', 'all', 12);
assert(featured.every((entry) => entry.featured));
assert.equal(featured[0].canonicalPath, '/karar-motoru');

console.log('ALO186 teknik arama: Türkçe normalizasyon, acil/resmî/ürün niyeti, filtre ve güvenli sıralama testleri başarılı.');
