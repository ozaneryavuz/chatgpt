'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {execFileSync}=require('node:child_process');

const ROOT=path.resolve(__dirname,'..','..');
const routes={
  pump:'/hesaplama/hidrofor-su-pompasi-yedek-guc-uygunluk/',
  gate:'/hesaplama/otomatik-kapi-kepenk-bariyer-yedek-guc-uygunluk/',
  center:'/sektor-rehberi/apartman-site-ortak-alan-elektrik-surekliligi-merkezi/',
  service:'/tesis-elektrik-risk-on-degerlendirme/'
};
const sourceFiles={
  pump:path.join(ROOT,'alo186','hesaplama','hidrofor-su-pompasi-yedek-guc-uygunluk','index.html'),
  gate:path.join(ROOT,'alo186','hesaplama','otomatik-kapi-kepenk-bariyer-yedek-guc-uygunluk','index.html'),
  center:path.join(ROOT,'alo186','sektor-rehberi','apartman-site-ortak-alan-elektrik-surekliligi-merkezi','index.html'),
  service:path.join(ROOT,'alo186','tesis-elektrik-risk-on-degerlendirme','index.html')
};
const html=Object.fromEntries(Object.entries(sourceFiles).map(([key,file])=>[key,fs.readFileSync(file,'utf8')]));
const css=fs.readFileSync(path.join(ROOT,'alo186','assets','critical-continuity-v126.css'),'utf8');
const overlay=JSON.parse(fs.readFileSync(path.join(ROOT,'alo186','deployment','routing-overlays','127-property-continuity.json'),'utf8'));

function inlineScript(text){
  const scripts=[...text.matchAll(/<script(?![^>]*type=["']application\/ld\+json["'])[^>]*>([\s\S]*?)<\/script>/gi)];
  return scripts.length?scripts.at(-1)[1]:'';
}
const scripts=Object.fromEntries(Object.entries(html).map(([key,text])=>[key,inlineScript(text)]));
const syntaxDir=fs.mkdtempSync(path.join(os.tmpdir(),'alo186-property-v127-syntax-'));
for(const name of ['pump','gate','center']){
  assert.ok(scripts[name],`${name}:inline script missing`);
  const file=path.join(syntaxDir,`${name}.js`);
  fs.writeFileSync(file,scripts[name]);
  execFileSync('node',['--check',file],{cwd:ROOT,stdio:'pipe'});
}
fs.rmSync(syntaxDir,{recursive:true,force:true});

for(const [name,text] of Object.entries(html)){
  for(const token of ['rel="canonical"','BreadcrumbList','ALO186 bağımsız'])assert.ok(text.includes(token),`${name}:${token}`);
  for(const forbidden of ['amazon.com','amazon.com.tr','"@type":"Product"','"@type":"Offer"','priceCurrency','aggregateRating','availability'])assert.ok(!text.includes(forbidden),`${name}:${forbidden}`);
}
for(const name of ['pump','gate','center']){
  const script=scripts[name];
  for(const forbidden of ['localStorage','sessionStorage','navigator.geolocation','fetch('])assert.ok(!script.includes(forbidden),`${name}:${forbidden}`);
  assert.ok(script.includes('application/json'),`${name}:json`);
  assert.ok(script.includes('text/calendar'),`${name}:calendar`);
}
for(const name of ['pump','gate']){
  const combined=html[name]+scripts[name];
  for(const token of ['rel="sponsored nofollow noopener"','Satış ortaklığı','yeni ürün almayın','commerce-consent','existingEnough','evidenceMissing'])assert.ok(combined.includes(token),`${name}:${token}`);
  assert.ok(/scenario\s*===\s*'active'/.test(scripts[name]),`${name}:active-event-close`);
  assert.ok(scripts[name].includes('commerce = false'),`${name}:commerce-default-closed`);
}
for(const token of ['Yangın pompası','trifaze','Sabit veya yüksek riskli pompa için profesyonel rota','unsafeGenerator'])assert.ok((html.pump+scripts.pump).includes(token),`pump:${token}`);
for(const token of ['Yangın ve tahliye sistemi tüketici ürünüyle seçilemez','manualRelease','safetyDevices','approvalMissing'])assert.ok((html.gate+scripts.gate).includes(token),`gate:${token}`);
for(const token of ['commercialPath: false','Bu merkez doğrudan ürün bağlantısı göstermez','P0','P1','P2','professionalSystemCount'])assert.ok((html.center+scripts.center).includes(token),`center:${token}`);
assert.ok(!html.center.includes('rel="sponsored'),'center must not expose commerce link');
for(const token of ['Ürün satışı yok','ölçüm ve görev kanıtıyla','İletişim sayfasına geçiş satış ortaklığı bağlantısı değildir'])assert.ok(html.service.includes(token),`service:${token}`);
assert.ok(!html.service.includes('rel="sponsored'),'service must not expose affiliate link');
for(const token of ['@media(max-width:820px)','@media(max-width:560px)','min-height:48px','prefers-reduced-motion','forced-colors','focus-visible'])assert.ok(css.includes(token),token);
assert.ok(!/outline\s*:\s*(?:0|none)\b/i.test(css));

// Bu iki relative bağlantı canlıdaki kararlı /sektor-rehberi koleksiyonuna gider.
// Genel validator yalnız exact public aliası kabul etmeli ve diğer kırık relative
// hedeflerde fail-closed kalmalıdır.
assert.ok(html.center.includes('<a href="../">Sektör rehberi</a>'),'center:stable-sector-hub');
assert.ok(html.service.includes('<a href="../sektor-rehberi/">Sektör rehberi</a>'),'service:stable-sector-hub');
execFileSync('python',[path.join(ROOT,'.github','scripts','validate_alo186.py')],{cwd:ROOT,stdio:'pipe'});

assert.deepEqual(overlay,{
  version:127,
  generatedAt:'2026-07-31',
  routes:[
    {source:'alo186/hesaplama/hidrofor-su-pompasi-yedek-guc-uygunluk/index.html',canonicalPath:routes.pump,type:'calculator'},
    {source:'alo186/hesaplama/otomatik-kapi-kepenk-bariyer-yedek-guc-uygunluk/index.html',canonicalPath:routes.gate,type:'calculator'},
    {source:'alo186/sektor-rehberi/apartman-site-ortak-alan-elektrik-surekliligi-merkezi/index.html',canonicalPath:routes.center,type:'guide'},
    {source:'alo186/tesis-elektrik-risk-on-degerlendirme/index.html',canonicalPath:routes.service,type:'service'}
  ]
});

const temp=fs.mkdtempSync(path.join(os.tmpdir(),'alo186-property-continuity-v127-'));
const canonical=path.join(temp,'canonical');
execFileSync('python',[path.join(ROOT,'alo186','deployment','build_static_site.py'),'--output',canonical,'--commit','property-continuity-v127-test'],{cwd:ROOT,stdio:'pipe'});
const sitemap=fs.readFileSync(path.join(canonical,'sitemap.xml'),'utf8');
for(const route of Object.values(routes)){
  assert.ok(sitemap.includes(route),route);
  assert.ok(fs.existsSync(path.join(canonical,route,'index.html')),route);
}
assert.ok(fs.existsSync(path.join(canonical,'assets','critical-continuity-v126.css')));

for(const basePath of ['','/chatgpt']){
  const target=path.join(temp,basePath?'project':'custom');
  fs.cpSync(canonical,target,{recursive:true});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','prepare_github_pages.py'),'--site',target,'--base-path',basePath,'--repository','ozaneryavuz/chatgpt','--commit','property-continuity-v127-test'],{cwd:ROOT,stdio:'pipe'});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','smoke_github_pages.py'),'--site',target,'--base-path',basePath],{cwd:ROOT,stdio:'pipe'});
  const expectedAsset=`${basePath}/assets/alo186-ux.js`||'/assets/alo186-ux.js';
  for(const route of Object.values(routes)){
    const page=fs.readFileSync(path.join(target,route,'index.html'),'utf8');
    assert.ok(page.includes(expectedAsset),`${basePath}:${route}`);
    assert.ok(page.includes('ALO186 bağımsız'),`${basePath}:${route}:independent`);
  }
}
fs.rmSync(temp,{recursive:true,force:true});

console.log(JSON.stringify({
  ok:true,version:127,routes:Object.values(routes),
  searchIntent:['hidrofor jeneratör kVA','otomatik kapı kesintide açma','apartman site ortak alan sürekliliği'],
  noBuyOutcome:true,activeEventCommerceClosed:true,lifeSafetyCommerceClosed:true,
  affiliateTransparent:true,directAmazon:false,priceStockRatingWarranty:false,
  professionalLeadPath:true,repeatVisitCalendar:true,personalData:false,
  officialAffiliation:false,customDomain:true,projectPath:true,
  stableSectorHubValidated:true
}));
