const assert=require('assert');
const fs=require('fs');
const path=require('path');

const repoRoot=path.resolve(__dirname,'../..');
const manifestPath=path.join(repoRoot,'alo186/deployment/routing-manifest.json');
const manifest=JSON.parse(fs.readFileSync(manifestPath,'utf8'));
const sitemap=fs.readFileSync(path.join(repoRoot,'alo186/sitemap.xml'),'utf8');
const hub=fs.readFileSync(path.join(repoRoot,'alo186/index.html'),'utf8');

assert.strictEqual(manifest.canonicalHost,'https://www.alo186.com');
assert(manifest.routes.length>=13,'Yayın manifestinde beklenen çekirdek rotalar bulunmalı.');

const paths=manifest.routes.map(x=>x.canonicalPath);
assert.strictEqual(new Set(paths).size,paths.length,'Canonical rotalar benzersiz olmalı.');

for(const route of manifest.routes){
  const sourcePath=path.join(repoRoot,route.source);
  assert(fs.existsSync(sourcePath),`Kaynak dosya bulunamadı: ${route.source}`);
  const html=fs.readFileSync(sourcePath,'utf8');
  const canonical=route.canonicalUrl||`${manifest.canonicalHost}${route.canonicalPath}`;
  assert(html.includes(`rel="canonical" href="${canonical}"`)||html.includes(`href="${canonical}" rel="canonical"`),`Canonical eşleşmiyor: ${route.source} → ${canonical}`);
  if(route.includeInSitemap!==false){
    assert(sitemap.includes(`<loc>${canonical}</loc>`),`Sitemap rotası eksik: ${canonical}`);
    assert(canonical.startsWith(manifest.canonicalHost),`Sitemap rotası canonicalHost altında olmalı: ${canonical}`);
  }else{
    assert(route.normalizationPending===true,`Sitemap dışındaki rota geçiş durumu içermeli: ${route.source}`);
  }
}

for(const required of ['./turkiye-arama/','./karar-motoru/','./hesaplama/','./urun-eslestirme/','./sureklilik-paneli/']){
  assert(hub.includes(`href="${required}"`),`Yayın merkezinde bağlantı eksik: ${required}`);
}

const robots=fs.readFileSync(path.join(repoRoot,'alo186/robots.txt'),'utf8');
assert(robots.includes('Sitemap: https://www.alo186.com/sitemap.xml'));
assert(robots.includes('Allow: /'));

console.log('ALO186 yayın manifesti, canonical ve sitemap testleri başarılı.');
