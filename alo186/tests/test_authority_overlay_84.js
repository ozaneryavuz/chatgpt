'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const repoRoot=path.resolve(__dirname,'../..');
const routingRoot=path.join(repoRoot,'alo186/deployment/routing-overlays');
const base=JSON.parse(fs.readFileSync(path.join(repoRoot,'alo186/deployment/routing-manifest.json'),'utf8'));
const overlays=fs.readdirSync(routingRoot)
  .filter(name=>name.endsWith('.json'))
  .sort()
  .map(name=>({name,...JSON.parse(fs.readFileSync(path.join(routingRoot,name),'utf8'))}));

assert.equal(base.version,34,'Base routing manifest beklenen v34 olmalı.');
assert(overlays.some(item=>item.name==='content-authority-81-run12.json'),'81 rehberlik önceki authority overlay eksik.');
assert(overlays.some(item=>item.name==='growth-proposal-scope-run12.json'),'Teknik teklif kapsamı büyüme overlay eksik.');
const current=overlays.find(item=>item.name==='content-authority-84-run13.json');
assert(current,'Run 13 içerik otoritesi overlay eksik.');
assert.equal(current.version,38,'Run 13 routing sürümü v38 olmalı.');
assert.equal(current.generatedAt,'2026-07-29');
assert.equal(current.routes.length,3,'Run 13 overlay tam üç yeni rota taşımalı.');

// This is a historical run-13 contract. Later independent overlays must not make
// the old snapshot fail merely because the site has continued to grow.
const historicalOverlays=overlays.filter(item=>item.version<=current.version);
const effective=[...base.routes];
for(const overlay of historicalOverlays) effective.push(...overlay.routes);
const canonical=new Set();
const sources=new Set();
for(const route of effective){
  assert(!canonical.has(route.canonicalPath),`Canonical çakışması: ${route.canonicalPath}`);
  assert(!sources.has(route.source),`Kaynak dosya çakışması: ${route.source}`);
  canonical.add(route.canonicalPath);
  sources.add(route.source);
}
assert.equal(Math.max(...historicalOverlays.map(item=>item.version)),38,'Run 13 tarihsel routing tepe sürümü v38 olmalı.');
assert.equal(effective.filter(route=>route.type==='article').length,84,'Run 13 tarihsel routing 84 teknik makale taşımalı.');
assert(effective.length>=127,'Run 13 ve önceki düşük sürümlü overlayler en az 127 canonical rota taşımalı.');

const articles=[
  {
    slug:'rcd-rccb-rcbo-farki',
    required:['RCCB','RCBO','MCB','IΔn','kesme kapasitesi','nötr bağlantısı'],
    cta:'/hesaplama/teknik-devir-kabul-paketi/'
  },
  {
    slug:'dusuk-yuksek-voltaj-edas-teknik-kalite-olcumu',
    required:['teknik kalite','bir haftalık ölçüm','15 iş günü','başvuru numarası','EPDK','186'],
    cta:'/edas-bul'
  },
  {
    slug:'lifepo4-dusuk-sicaklikta-sarj-edilir-mi',
    required:['LiFePO₄','lityum kaplama','Allowed-To-Charge','+5°C','BMS','ısıtıcı'],
    cta:'/hesaplama/teknik-devir-kabul-paketi/'
  }
];

for(const article of articles){
  const file=path.join(repoRoot,'alo186/haberler',article.slug,'index.html');
  assert(fs.existsSync(file),`Makale bulunamadı: ${article.slug}`);
  const html=fs.readFileSync(file,'utf8');
  const canonicalUrl=`https://www.alo186.com/haberler/${article.slug}`;
  assert(html.toLowerCase().includes('<!doctype html>'));
  assert(html.includes(`rel="canonical" href="${canonicalUrl}"`),`Canonical eksik: ${article.slug}`);
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
    assert(graph.some(item=>item['@type']==='BreadcrumbList'),`BreadcrumbList schema eksik: ${article.slug}`);
    const articleNode=graph.find(item=>item['@type']==='Article');
    assert(Array.isArray(articleNode.about)&&articleNode.about.some(item=>item['@type']==='DefinedTerm'),`DefinedTerm eksik: ${article.slug}`);
  }

  assert(!/<form\b/i.test(html),`Makale form istememeli: ${article.slug}`);
  assert(!/amazon\.(?:com|com\.tr)/i.test(html),`Doğrudan Amazon URL'si olmamalı: ${article.slug}`);
  assert(!/fiyatı\s+\d|stokta|puanı\s+\d/i.test(html),`Doğrulanmamış ticari bilgi riski: ${article.slug}`);
  assert(!/kesinlikle güvenlidir|her durumda güvenlidir|sonucu garanti eder/i.test(html),`Aşırı kesin güvenlik iddiası: ${article.slug}`);
  assert((html.match(/rel="external noopener"/g)||[]).length>=3,`En az üç görünür birincil kaynak gerekli: ${article.slug}`);
  for(const text of article.required){
    assert(html.toLocaleLowerCase('tr').includes(text.toLocaleLowerCase('tr')),`Zorunlu ifade eksik (${text}): ${article.slug}`);
  }
}

console.log('ALO186 içerik otoritesi run 13: 84 kaynak doğrulamalı makale ve en az 127 canonical rota sözleşmesi başarılı.');
