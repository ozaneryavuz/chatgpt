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
assert(overlays.some(item=>item.name==='content-authority-78.json'),'78 rehberlik önceki authority overlay eksik.');
assert(overlays.some(item=>item.name==='growth-technical-handoff-run11.json'),'Teknik devir büyüme overlay eksik.');
const current=overlays.find(item=>item.name==='content-authority-81-run12.json');
assert(current,'Run 12 içerik otoritesi overlay eksik.');
assert.equal(current.version,37,'Run 12 routing sürümü v37 olmalı.');
assert.equal(current.generatedAt,'2026-07-29');
assert.equal(current.routes.length,3,'Run 12 overlay tam üç yeni rota taşımalı.');

function normalizeRoute(route, sourceLabel){
  const hasModern=Boolean(route&&route.canonicalPath&&route.source&&route.type);
  if(hasModern){
    if(route.path!==undefined) assert.equal(route.path,route.canonicalPath,`Dual rota canonical uyumsuz: ${sourceLabel}`);
    if(route.file!==undefined) assert.equal(`alo186/${route.file}`,route.source,`Dual rota source uyumsuz: ${sourceLabel}`);
    if(route.intent!==undefined) assert(String(route.intent).trim(),`Dual rota intent boş: ${sourceLabel}`);
    return {canonicalPath:route.canonicalPath,source:route.source,type:route.type};
  }
  assert(route&&route.path&&route.file&&route.intent,`Rota şeması tanınmıyor: ${sourceLabel}`);
  assert(route.path.startsWith('/haberler/'),`Legacy rota haber olmalı: ${sourceLabel}`);
  assert.equal(route.file,`${route.path.slice(1)}/index.html`,`Legacy rota kaynak uyuşmuyor: ${sourceLabel}`);
  return {canonicalPath:route.path,source:`alo186/${route.file}`,type:'article'};
}

const effective=base.routes.map((route,index)=>normalizeRoute(route,`routing-manifest.json#${index}`));
for(const overlay of overlays){
  overlay.routes.forEach((route,index)=>effective.push(normalizeRoute(route,`${overlay.name}#${index}`)));
}
const canonical=new Set();
const sources=new Set();
for(const route of effective){
  assert(!canonical.has(route.canonicalPath),`Canonical çakışması: ${route.canonicalPath}`);
  assert(!sources.has(route.source),`Kaynak dosya çakışması: ${route.source}`);
  canonical.add(route.canonicalPath);
  sources.add(route.source);
}
assert(Math.max(...overlays.map(item=>item.version))>=37,'En yüksek routing overlay sürümü en az v37 olmalı.');
assert(effective.filter(route=>route.type==='article').length>=81,'Etkili routing en az 81 teknik makale taşımalı.');
assert(effective.length>=123,'Etkili routing en az 123 canonical rota taşımalı.');

const articles=[
  {
    slug:'topraklama-espotansiyel-kusaklama-farki',
    required:['eşpotansiyel kuşaklama','ana topraklama terminali','PE iletkeni','dokunma gerilimi','ek eşpotansiyel kuşaklama'],
    cta:'/hesaplama/teknik-devir-kabul-paketi/'
  },
  {
    slug:'k-faktorlu-trafo-harmonik-yuk-derating',
    required:['K faktörü','K-rated','K4','K13','THDi','TDD','derating','harmonik spektrum'],
    cta:'/haberler/detuned-reaktor-aktif-harmonik-filtre-farki'
  },
  {
    slug:'lifepo4-hucre-dengeleme-aktif-pasif-bms',
    required:['aktif balancing','pasif balancing','0,01 V','1,8 A','hücre voltaj farkı','BMS'],
    cta:'/hesaplama/inverter-uygunluk/'
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

console.log('ALO186 içerik otoritesi run 12 tabanı: en az 81 kaynak doğrulamalı makale ve 123 canonical rota sözleşmesi başarılı.');
