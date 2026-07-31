'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {execFileSync}=require('node:child_process');

const ROOT=path.resolve(__dirname,'..','..');
const extensionDir=path.join(ROOT,'alo186','hesaplama','uzatma-kablosu-kablo-makarasi-yuk-uygunluk');
const lightingDir=path.join(ROOT,'alo186','hesaplama','elektrik-kesintisi-sarjli-ampul-isildak-uygunluk');
const centerDir=path.join(ROOT,'alo186','sektor-rehberi','elektrik-kesintisi-aydinlatma-ve-guvenli-uzatma-merkezi');
const extension=require(path.join(extensionDir,'app.js'));
const lighting=require(path.join(lightingDir,'app.js'));
const center=require(path.join(centerDir,'app.js'));
const extensionHtml=fs.readFileSync(path.join(extensionDir,'index.html'),'utf8');
const lightingHtml=fs.readFileSync(path.join(lightingDir,'index.html'),'utf8');
const centerHtml=fs.readFileSync(path.join(centerDir,'index.html'),'utf8');
const sharedCss=fs.readFileSync(path.join(ROOT,'alo186','hesaplama','elektrik-faturasi-kwh-gun-karsilastirma','styles.css'),'utf8');
const overlay=JSON.parse(fs.readFileSync(path.join(ROOT,'alo186','deployment','routing-overlays','133-portable-safety-lighting.json'),'utf8'));

for(const file of [path.join(extensionDir,'app.js'),path.join(lightingDir,'app.js'),path.join(centerDir,'app.js')])execFileSync('node',['--check',file],{cwd:ROOT,stdio:'pipe'});

const extensionBase={danger:false,maleToMale:false,physicalSafe:true,mode:'planning',useClass:'low_power',connection:'single',reelState:'not_reel',environment:'indoor',outdoorRated:false,ratingVerified:true,voltage:230,loadW:800,ratedA:16,lengthM:20,crossSection:1.5,targetDropPct:3,earthRcdVerified:true,existingSuitable:false,confirmNeed:false,confirmLabel:false,confirmAffiliate:false};
const em=extension.metrics(extensionBase);
assert.ok(em.currentA>3.4&&em.currentA<3.5);
assert.ok(em.ratedW===3680);
assert.ok(em.voltageDropPct>0&&em.voltageDropPct<1);
assert.equal(extension.decide({...extensionBase,danger:true}).code,'danger');
assert.equal(extension.decide({...extensionBase,maleToMale:true}).code,'backfeed');
assert.equal(extension.decide({...extensionBase,physicalSafe:false}).code,'physical');
assert.equal(extension.decide({...extensionBase,mode:'active_outage'}).code,'active');
assert.equal(extension.decide({...extensionBase,useClass:'ev'}).code,'excluded');
assert.equal(extension.decide({...extensionBase,connection:'chain'}).code,'chain');
assert.equal(extension.decide({...extensionBase,connection:'reel',reelState:'coiled'}).code,'coiled');
assert.equal(extension.decide({...extensionBase,environment:'outdoor',outdoorRated:false}).code,'outdoor');
assert.equal(extension.decide({...extensionBase,earthRcdVerified:false}).code,'protection');
assert.equal(extension.decide({...extensionBase,ratingVerified:false}).code,'label');
assert.equal(extension.decide({...extensionBase,loadW:4000}).code,'overload');
assert.equal(extension.decide({...extensionBase,crossSection:''}).code,'drop_unknown');
assert.equal(extension.decide({...extensionBase,lengthM:100,crossSection:.75,targetDropPct:1}).code,'drop');
assert.equal(extension.decide({...extensionBase,existingSuitable:true}).code,'no_buy');
const extensionQualified=extension.decide({...extensionBase,confirmNeed:true,confirmLabel:true,confirmAffiliate:true});
assert.equal(extensionQualified.code,'qualified');
assert.equal(extensionQualified.commerce,true);
assert.ok(extension.calendar(90).includes('BEGIN:VCALENDAR'));
assert.equal(extension.report(extensionBase).route,extension.ROUTE);

const lightingBase={danger:false,openFlame:false,context:'home',mode:'planning',productType:'lantern',runtimeMode:'manufacturer',manufacturerRuntimeH:4,batteryWh:12,lampW:4,usablePct:80,requiredHours:3,requiredAreas:2,availableUnits:2,physicalSafe:true,charged:true,indicatorOk:true,switchDependencyKnown:true,realOutageTest:true,existingSafeLight:true,existingSuitable:false,confirmNeed:false,confirmEvidence:false,confirmAffiliate:false};
assert.equal(lighting.runtimeHours(lightingBase),4);
assert.equal(lighting.runtimeHours({...lightingBase,runtimeMode:'battery'}),2.4);
assert.equal(lighting.decide({...lightingBase,danger:true}).code,'danger');
assert.equal(lighting.decide({...lightingBase,openFlame:true}).code,'flame');
assert.equal(lighting.decide({...lightingBase,context:'commercial_exit'}).code,'regulated');
assert.equal(lighting.decide({...lightingBase,mode:'active_outage',existingSafeLight:false}).code,'active');
assert.equal(lighting.decide({...lightingBase,physicalSafe:false}).code,'physical');
assert.equal(lighting.decide({...lightingBase,charged:false}).code,'charge');
assert.equal(lighting.decide({...lightingBase,productType:'rechargeable_bulb',switchDependencyKnown:false}).code,'switch');
assert.equal(lighting.decide({...lightingBase,realOutageTest:false}).code,'test');
assert.equal(lighting.decide({...lightingBase,manufacturerRuntimeH:''}).code,'evidence');
assert.equal(lighting.decide({...lightingBase,requiredAreas:0}).code,'coverage_unknown');
assert.equal(lighting.decide({...lightingBase,existingSuitable:true}).code,'no_buy');
assert.equal(lighting.decide({...lightingBase,requiredHours:6}).code,'runtime_gap');
assert.equal(lighting.decide({...lightingBase,availableUnits:1}).code,'coverage_gap');
const lightingQualified=lighting.decide({...lightingBase,requiredHours:6,confirmNeed:true,confirmEvidence:true,confirmAffiliate:true});
assert.equal(lightingQualified.code,'qualified');
assert.equal(lightingQualified.commerce,true);
assert.ok(lighting.calendar(90).includes('BEGIN:VCALENDAR'));
assert.equal(lighting.report(lightingBase).route,lighting.ROUTE);

const centerBase={scenario:'routine',danger:false,commercialOrEgress:false,existingPass:false,newLoad:false,outdoorChange:false};
assert.equal(center.makePlan({...centerBase,danger:true}).code,'danger');
assert.equal(center.makePlan({...centerBase,commercialOrEgress:true}).code,'professional');
assert.equal(center.makePlan({...centerBase,existingPass:true}).code,'no_buy');
assert.equal(center.makePlan({...centerBase,scenario:'outage'}).code,'outage');
assert.equal(center.makePlan({...centerBase,scenario:'outdoor'}).code,'outdoor');
assert.equal(center.makePlan({...centerBase,scenario:'new-light'}).code,'new');
assert.equal(center.makePlan(centerBase).code,'routine');
assert.ok(center.calendar(center.makePlan(centerBase)).includes('BEGIN:VCALENDAR'));
assert.equal(center.report(centerBase).route,center.ROUTE);

for(const [name,html] of [['extension',extensionHtml],['lighting',lightingHtml],['center',centerHtml]]){
  for(const token of ['rel="canonical"','FAQPage','BreadcrumbList','ALO186'])assert.ok(html.includes(token),`${name}:${token}`);
  assert.ok(html.toLocaleLowerCase('tr-TR').includes('bağımsız'),`${name}:independence`);
  assert.ok(html.toLocaleLowerCase('tr-TR').includes('kişisel veri'),`${name}:personal-data`);
  for(const forbidden of ['https://www.amazon','https://amazon','"@type":"Product"','"@type":"Offer"','priceCurrency','aggregateRating','availability'])assert.ok(!html.includes(forbidden),`${name}:${forbidden}`);
}
assert.ok(extensionHtml.includes('rel="sponsored nofollow noopener"'));
assert.ok(lightingHtml.includes('rel="sponsored nofollow noopener"'));
assert.ok(extensionHtml.toLocaleLowerCase('tr-TR').includes('satış ortaklığı'));
assert.ok(lightingHtml.toLocaleLowerCase('tr-TR').includes('satış ortaklığı'));
assert.ok(!centerHtml.includes('rel="sponsored nofollow noopener"'));
assert.ok(centerHtml.includes(extension.ROUTE)&&centerHtml.includes(lighting.ROUTE));
assert.ok(extensionHtml.includes('CPSC')&&extensionHtml.includes('31 Mart 2026'));
assert.ok(lightingHtml.includes('IEC 60598-2-22:2021')&&lightingHtml.includes('OSHA'));
for(const js of [fs.readFileSync(path.join(extensionDir,'app.js'),'utf8'),fs.readFileSync(path.join(lightingDir,'app.js'),'utf8'),fs.readFileSync(path.join(centerDir,'app.js'),'utf8')])for(const forbidden of ['fetch(','navigator.geolocation','localStorage','sessionStorage'])assert.ok(!js.includes(forbidden),forbidden);
for(const token of ['@media(max-width:820px)','@media(max-width:560px)','min-height:48px','prefers-reduced-motion','forced-colors','focus-visible'])assert.ok(sharedCss.includes(token),token);
assert.ok(!/outline\s*:\s*(?:0|none)\b/i.test(sharedCss));
assert.equal(overlay.version,133);
assert.deepEqual(overlay.routes.map((route)=>route.canonicalPath),[extension.ROUTE,lighting.ROUTE,center.ROUTE]);

const temp=fs.mkdtempSync(path.join(os.tmpdir(),'alo186-portable-safety-v133-'));
const canonical=path.join(temp,'canonical');
execFileSync('python',[path.join(ROOT,'alo186','deployment','build_static_site.py'),'--output',canonical,'--commit','portable-safety-v133-test'],{cwd:ROOT,stdio:'pipe'});
const sitemap=fs.readFileSync(path.join(canonical,'sitemap.xml'),'utf8');
for(const route of [extension.ROUTE,lighting.ROUTE,center.ROUTE])assert.ok(sitemap.includes(route),route);
for(const file of [
  path.join(canonical,'hesaplama','uzatma-kablosu-kablo-makarasi-yuk-uygunluk','index.html'),
  path.join(canonical,'hesaplama','elektrik-kesintisi-sarjli-ampul-isildak-uygunluk','index.html'),
  path.join(canonical,'sektor-rehberi','elektrik-kesintisi-aydinlatma-ve-guvenli-uzatma-merkezi','index.html')
])assert.ok(fs.existsSync(file),file);
for(const basePath of ['','/chatgpt']){
  const target=path.join(temp,basePath?'project':'custom');
  fs.cpSync(canonical,target,{recursive:true});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','prepare_github_pages.py'),'--site',target,'--base-path',basePath,'--repository','ozaneryavuz/chatgpt','--commit','portable-safety-v133-test'],{cwd:ROOT,stdio:'pipe'});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','smoke_github_pages.py'),'--site',target,'--base-path',basePath],{cwd:ROOT,stdio:'pipe'});
  const expected=`${basePath}/assets/alo186-ux.js`||'/assets/alo186-ux.js';
  for(const file of [
    path.join(target,'hesaplama','uzatma-kablosu-kablo-makarasi-yuk-uygunluk','index.html'),
    path.join(target,'hesaplama','elektrik-kesintisi-sarjli-ampul-isildak-uygunluk','index.html'),
    path.join(target,'sektor-rehberi','elektrik-kesintisi-aydinlatma-ve-guvenli-uzatma-merkezi','index.html')
  ])assert.ok(fs.readFileSync(file,'utf8').includes(expected),`${basePath}:${file}`);
}
fs.rmSync(temp,{recursive:true,force:true});
console.log(JSON.stringify({ok:true,version:133,routes:[extension.ROUTE,lighting.ROUTE,center.ROUTE],extensionLabelFirst:true,maleToMaleBlocked:true,reelUnwindRequired:true,lightingRuntime:true,regulatedEmergencyLightingClosed:true,noBuy:true,repeatVisitPlan:true,affiliateTransparent:true,unverifiedCommercialFields:false,personalData:false,customDomain:true,projectPath:true}));