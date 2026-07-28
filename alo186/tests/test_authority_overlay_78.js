'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const repoRoot=path.resolve(__dirname,'../..');
const base=JSON.parse(fs.readFileSync(path.join(repoRoot,'alo186/deployment/routing-manifest.json'),'utf8'));
const overlayPath=path.join(repoRoot,'alo186/deployment/routing-overlays/content-authority-78.json');
assert(fs.existsSync(overlayPath),'İçerik otoritesi routing overlay dosyası eksik.');
const overlay=JSON.parse(fs.readFileSync(overlayPath,'utf8'));

assert.equal(base.version,34,'Base routing manifest beklenen v34 olmalı.');
assert.equal(overlay.version,35,'Etkili routing sürümü v35 olmalı.');
assert.equal(overlay.generatedAt,'2026-07-29');
assert.equal(overlay.routes.length,3,'Overlay tam üç yeni rota taşımalı.');

const basePaths=new Set(base.routes.map(route=>route.canonicalPath));
const effectiveRoutes=[...base.routes,...overlay.routes];
assert.equal(effectiveRoutes.filter(route=>route.type==='article').length,78,'Etkili routing 78 teknik makale taşımalı.');
for(const route of overlay.routes){
  assert(!basePaths.has(route.canonicalPath),`Yeni rota mevcut manifestle çakışıyor: ${route.canonicalPath}`);
  assert.equal(route.type,'article');
}

const articles=[
  {
    slug:'ups-eco-modu-acik-olmali-mi',
    required:['ECO modu','online çift dönüşüm','statik bypass','10 ms','eConversion','kararsız şebeke'],
    cta:'/hesaplama/ups-suresi/'
  },
  {
    slug:'ges-inverter-mppt-giris-akimi-isc-nasil-kontrol-edilir',
    required:['MPPT','Imp','Isc','maksimum kısa devre akımı','paralel string','soğuk hava'],
    cta:'/hesaplama/gunes-paneli-power-station-uygunluk/'
  },
  {
    slug:'jenerator-start-akusu-neden-bosalir-sarj-olmaz',
    required:['T1','ATS','Charger Missing AC','nötr','yük testi','yetkili servis'],
    cta:'/hesaplama/ekipman-bakim-plani/'
  }
];

for(const article of articles){
  const file=path.join(repoRoot,'alo186/haberler',article.slug,'index.html');
  assert(fs.existsSync(file),`Makale bulunamadı: ${article.slug}`);
  const html=fs.readFileSync(file,'utf8');
  const canonical=`https://www.alo186.com/haberler/${article.slug}`;
  assert(html.toLowerCase().includes('<!doctype html>'));
  assert(html.includes(`rel="canonical" href="${canonical}"`),`Canonical eksik: ${article.slug}`);
  assert(html.includes('meta name="description"'),`Description eksik: ${article.slug}`);
  assert(html.includes('../alo186-article.css'),`Ortak CSS eksik: ${article.slug}`);
  assert(html.includes(article.cta),`İç CTA eksik: ${article.slug}`);
  assert(html.includes('Bağımsız bilgi'),`Bağımsızlık ifadesi eksik: ${article.slug}`);
  assert(html.includes('Son doğrulama: 29 Temmuz 2026'),`Doğrulama tarihi eksik: ${article.slug}`);
  assert(html.includes('Kaynaklar ve doğrulama'),`Görünür kaynak bölümü eksik: ${article.slug}`);
  assert.strictEqual((html.match(/<h1\b/g)||[]).length,1,`Tek H1 olmalı: ${article.slug}`);

  const jsonLd=[...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
  assert(jsonLd.length>0,`JSON-LD bulunamadı: ${article.slug}`);
  for(const match of jsonLd){
    const parsed=JSON.parse(match[1]);
    const graph=parsed['@graph']||[parsed];
    assert(graph.some(item=>item['@type']==='Article'),`Article schema eksik: ${article.slug}`);
    assert(graph.some(item=>item['@type']==='FAQPage'),`FAQPage schema eksik: ${article.slug}`);
    const articleNode=graph.find(item=>item['@type']==='Article');
    assert(Array.isArray(articleNode.about)&&articleNode.about.some(item=>item['@type']==='DefinedTerm'),`DefinedTerm eksik: ${article.slug}`);
  }

  assert(!/<form\b/i.test(html),`Makale form istememeli: ${article.slug}`);
  assert(!/amazon\.(?:com|com\.tr)/i.test(html),`Doğrudan Amazon URL'si olmamalı: ${article.slug}`);
  assert(!/fiyatı\s+\d|stokta|puanı\s+\d/i.test(html),`Doğrulanmamış ticari bilgi riski: ${article.slug}`);
  assert(!/kesinlikle güvenlidir|her durumda güvenlidir|sonucu garanti eder/i.test(html),`Aşırı kesin güvenlik iddiası: ${article.slug}`);
  for(const text of article.required){
    assert(html.toLocaleLowerCase('tr').includes(text.toLocaleLowerCase('tr')),`Zorunlu ifade eksik (${text}): ${article.slug}`);
  }
}

const buildScript=fs.readFileSync(path.join(repoRoot,'alo186/deployment/build_static_site.py'),'utf8');
assert(buildScript.includes('load_effective_manifest'), 'Production builder routing overlay birleştirmiyor.');
assert(buildScript.includes('write_effective_sitemap'), 'Production builder etkili sitemap üretmiyor.');
assert(buildScript.includes('routingOverlays'), 'Release metadata overlay envanteri taşımıyor.');
assert(buildScript.includes('articleCount'), 'Release metadata etkili makale sayısını taşımıyor.');

console.log('ALO186 içerik otoritesi overlay: 75 temel + 3 yeni = 78 kaynak doğrulamalı makale sözleşmesi başarılı.');
