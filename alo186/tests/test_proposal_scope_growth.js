'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const exists=p=>fs.existsSync(path.join(root,p));

const route='/hesaplama/teknik-teklif-kapsam-karsilastirma/';
const overlay=JSON.parse(read('alo186/deployment/routing-overlays/growth-proposal-scope-run12.json'));
assert.equal(overlay.version,37);
assert.deepEqual(overlay.routes,[{source:'alo186/hesaplama/teknik-teklif-kapsam-karsilastirma/index.html',canonicalPath:route,type:'business-tool'}]);

for(const file of ['core.js','app.js','index.html','styles.css','test.js'])assert(exists(`alo186/hesaplama/teknik-teklif-kapsam-karsilastirma/${file}`),`${file} eksik`);
const html=read('alo186/hesaplama/teknik-teklif-kapsam-karsilastirma/index.html');
assert(html.includes(`rel="canonical" href="https://www.alo186.com${route}"`));
assert(html.includes('WebApplication'));
assert(html.includes('FAQPage'));
assert(html.includes('Mevcut çözüm yeterli mi?'));
assert(html.includes('satış ortaklığı açıklamasını anladım'));
assert(html.includes('ALO186 EDAŞ, kamu kurumu, yüklenici, satıcı veya kabul kuruluşu değildir'));
assert(!/<textarea\b|type="(?:email|tel|text)"/i.test(html));
assert(!/amazon\.(?:com|com\.tr)/i.test(html));

const inject=read('alo186/deployment/inject_proposal_scope_growth.py');
for(const token of ['36 çekirdek araç','data-alo186-proposal-hub','data-alo186-proposal-card','data-alo186-proposal-section','manifest.webmanifest','offlineCriticalRouteCount','checksums.sha256'])assert(inject.includes(token),`Enjektör sözleşmesi eksik: ${token}`);
assert(inject.includes('teknik-devir-kabul-paketi'));
assert(inject.includes('kurumsal-elektrik-surekliligi-on-degerlendirme'));

const chain=read('alo186/deployment/inject_handoff_growth.py');
assert(chain.includes('from inject_proposal_scope_growth import run as run_proposal_scope'));
assert(chain.includes("result['proposalScope']=run_proposal_scope(site,base_path)"));

console.log('ALO186 teknik teklif kapsamı: v37 rota, görünür güven sınırı, artifact entegrasyonu ve gizlilik sözleşmeleri başarılı.');
