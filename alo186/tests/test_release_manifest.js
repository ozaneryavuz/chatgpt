const assert=require('assert');
const fs=require('fs');
const path=require('path');

const repoRoot=path.resolve(__dirname,'../..');
const manifestPath=path.join(repoRoot,'alo186/deployment/routing-manifest.json');
const manifest=JSON.parse(fs.readFileSync(manifestPath,'utf8'));
const sitemap=fs.readFileSync(path.join(repoRoot,'alo186/sitemap.xml'),'utf8');
const hub=fs.readFileSync(path.join(repoRoot,'alo186/index.html'),'utf8');
const canonicalHost='https://alo186.com';
const legacyHost='https://www.alo186.com';
const aliasMarker='data-alo186-content-alias="true"';

function canonicalValues(html){
  const values=[];
  const patterns=[
    /<link\b[^>]*rel=["'][^"']*canonical[^"']*["'][^>]*href=["']([^"']+)["'][^>]*>/gi,
    /<link\b[^>]*href=["']([^"']+)["'][^>]*rel=["'][^"']*canonical[^"']*["'][^>]*>/gi,
  ];
  for(const pattern of patterns){
    for(const match of html.matchAll(pattern))values.push(match[1]);
  }
  return [...new Set(values)];
}

function normalizedPath(value){
  const parsed=new URL(value,canonicalHost);
  const pathname=decodeURIComponent(parsed.pathname||'/').replace(/\/{2,}/g,'/');
  return pathname==='/'?'/':pathname.replace(/\/$/,'');
}

assert.strictEqual(manifest.canonicalHost,canonicalHost);
assert(manifest.routes.length>=13,'Yayın manifestinde beklenen çekirdek rotalar bulunmalı.');

const paths=manifest.routes.map(x=>x.canonicalPath);
assert.strictEqual(new Set(paths).size,paths.length,'Canonical rotalar benzersiz olmalı.');
let aliasCount=0;

for(const route of manifest.routes){
  const sourcePath=path.join(repoRoot,route.source);
  assert(fs.existsSync(sourcePath),`Kaynak dosya bulunamadı: ${route.source}`);
  const html=fs.readFileSync(sourcePath,'utf8');
  const aliases=html.includes(aliasMarker);
  const values=canonicalValues(html);
  const canonical=route.canonicalUrl||`${manifest.canonicalHost}${route.canonicalPath}`;
  const legacyCanonical=canonical.replace(canonicalHost,legacyHost);

  if(aliases){
    aliasCount+=1;
    assert.strictEqual(values.length,1,`Alias tam bir canonical hedef taşımalı: ${route.source}`);
    const target=new URL(values[0]);
    assert.strictEqual(target.protocol,'https:',`Alias canonical HTTPS olmalı: ${route.source}`);
    assert.strictEqual(target.hostname,'alo186.com',`Alias canonical apex origin kullanmalı: ${route.source}`);
    assert.notStrictEqual(normalizedPath(values[0]),normalizedPath(canonical),`Alias kendi eski URL’sini canonical göstermemeli: ${route.source}`);
    assert(/<meta\b[^>]*name=["']robots["'][^>]*content=["'][^"']*noindex[^"']*follow[^"']*["']/i.test(html),`Alias noindex,follow taşımalı: ${route.source}`);
    assert(html.includes(target.pathname),`Alias görünür veya istemci yönlendirmesinde canonical hedefi taşımalı: ${route.source}`);
    continue;
  }

  const sourceCanonicalMatches=[canonical,legacyCanonical].some(value=>values.includes(value));
  assert(sourceCanonicalMatches,`Canonical eşleşmiyor: ${route.source} → ${canonical} veya ${legacyCanonical}`);
  if(route.includeInSitemap!==false){
    assert(sitemap.includes(`<loc>${canonical}</loc>`),`Sitemap rotası eksik: ${canonical}`);
    assert(canonical.startsWith(manifest.canonicalHost),`Sitemap rotası canonicalHost altında olmalı: ${canonical}`);
  }else{
    assert(route.normalizationPending===true,`Sitemap dışındaki rota geçiş durumu içermeli: ${route.source}`);
  }
}

assert(aliasCount>=2,'Bilinen legacy içerik aliasları açık sözleşmeyle korunmalı.');

for(const required of ['/edas-bul','/karar-motoru','/hesaplama/','/akilli-urun-secimi','/isletme-surekliligi']){
  assert(hub.includes(`href="${required}"`),`Yayın merkezinde canonical bağlantı eksik: ${required}`);
}
for(const stale of ['./turkiye-arama/','./karar-motoru/','./urun-eslestirme/','./sureklilik-paneli/']){
  assert(!hub.includes(`href="${stale}"`),`Kaynak klasör adı production rotası olarak kalmış: ${stale}`);
}

const robots=fs.readFileSync(path.join(repoRoot,'alo186/robots.txt'),'utf8');
assert(robots.includes(`Sitemap: ${canonicalHost}/sitemap.xml`));
assert(!robots.includes(`Sitemap: ${legacyHost}/sitemap.xml`));
assert(robots.includes('Allow: /'));

console.log(`ALO186 yayın manifesti, apex canonical sözleşmesi, ${aliasCount} alias köprüsü, portal bağlantıları ve sitemap testleri başarılı.`);
