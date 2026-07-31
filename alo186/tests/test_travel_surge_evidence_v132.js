'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {execFileSync}=require('node:child_process');

const ROOT=path.resolve(__dirname,'..','..');
const flightDir=path.join(ROOT,'alo186','hesaplama','powerbank-ucak-wh-kabin-bagaji-uygunluk');
const surgeDir=path.join(ROOT,'alo186','hesaplama','akim-korumali-priz-koruma-gostergesi-omur-testi');
const centerDir=path.join(ROOT,'alo186','sektor-rehberi','elektronik-cihaz-guc-seyahat-koruma-merkezi');
const flight=require(path.join(flightDir,'app.js'));
const surge=require(path.join(surgeDir,'app.js'));
const center=require(path.join(centerDir,'app.js'));
const flightHtml=fs.readFileSync(path.join(flightDir,'index.html'),'utf8');
const surgeHtml=fs.readFileSync(path.join(surgeDir,'index.html'),'utf8');
const centerHtml=fs.readFileSync(path.join(centerDir,'index.html'),'utf8');
const sharedCss=fs.readFileSync(path.join(ROOT,'alo186','hesaplama','elektrik-faturasi-kwh-gun-karsilastirma','styles.css'),'utf8');
const overlay=JSON.parse(fs.readFileSync(path.join(ROOT,'alo186','deployment','routing-overlays','132-travel-surge-electronics.json'),'utf8'));

for(const file of [path.join(flightDir,'app.js'),path.join(surgeDir,'app.js'),path.join(centerDir,'app.js')])execFileSync('node',['--check',file],{cwd:ROOT,stdio:'pipe'});

const flightBase={kind:'powerbank',energyMode:'mah',mah:20000,voltage:3.7,wh:'',airlineMaxWh:100,airlineMaxQty:2,quantity:1,requiredWh:90,airlineChecked:true,cabinOnly:true,terminalProtected:true,planUseOnBoard:false,unsafeBattery:false,existingSuitable:false,confirmNeed:false,confirmLabel:false,confirmAffiliate:false};
assert.equal(flight.energyWh(flightBase),74);
assert.equal(flight.decide({...flightBase,unsafeBattery:true}).code,'unsafe');
assert.equal(flight.decide({...flightBase,airlineChecked:false}).code,'verify_airline');
assert.equal(flight.decide({...flightBase,cabinOnly:false}).code,'checked_bag_block');
assert.equal(flight.decide({...flightBase,mah:30000,voltage:3.7}).code,'over_limit');
assert.equal(flight.decide({...flightBase,quantity:3}).code,'quantity_limit');
assert.equal(flight.decide({...flightBase,terminalProtected:false}).code,'terminal_risk');
assert.equal(flight.decide({...flightBase,planUseOnBoard:true}).code,'onboard_rule');
assert.equal(flight.decide({...flightBase,existingSuitable:true}).code,'no_buy');
assert.equal(flight.decide({...flightBase,requiredWh:50}).code,'capacity_ok');
assert.equal(flight.decide(flightBase).code,'need_unconfirmed');
const flightQualified=flight.decide({...flightBase,confirmNeed:true,confirmLabel:true,confirmAffiliate:true});
assert.equal(flightQualified.code,'qualified');
assert.equal(flightQualified.commerce,true);
assert.ok(flight.calendar(7).includes('BEGIN:VCALENDAR'));
assert.equal(flight.report(flightBase).route,flight.ROUTE);

const surgeBase={productType:'surge',protectionIndicator:'on',groundIndicator:'ok',loadW:450,ratedW:3680,longUse:false,manualChecked:true,physicalSafe:true,majorEvent:false,wholeHomeNeed:false,repeatedVoltage:false,existingHealthy:false,existingAlternative:false,higherJouleOnly:false,excludedLoad:false,emergency:false,confirmNeed:false,confirmLowRisk:false,confirmAffiliate:false};
assert.ok(surge.metrics(surgeBase).loadRatio>12&&surge.metrics(surgeBase).loadRatio<13);
assert.equal(surge.decision({...surgeBase,emergency:true}).code,'unsafe');
assert.equal(surge.decision({...surgeBase,excludedLoad:true}).code,'excluded');
assert.equal(surge.decision({...surgeBase,wholeHomeNeed:true}).code,'professional');
assert.equal(surge.decision({...surgeBase,repeatedVoltage:true}).code,'professional');
assert.equal(surge.decision({...surgeBase,loadW:4000}).code,'overload');
assert.equal(surge.decision({...surgeBase,groundIndicator:'fault'}).code,'ground_fault');
assert.equal(surge.decision({...surgeBase,protectionIndicator:'unknown'}).code,'verify_manual');
assert.equal(surge.decision({...surgeBase,majorEvent:true}).code,'post_event');
assert.equal(surge.decision({...surgeBase,higherJouleOnly:true}).code,'no_buy_joule');
assert.equal(surge.decision({...surgeBase,existingHealthy:true}).code,'no_buy');
assert.equal(surge.decision({...surgeBase,productType:'powerstrip'}).code,'not_protected');
assert.equal(surge.decision({...surgeBase,protectionIndicator:'off'}).code,'indicator_off');
const surgeQualified=surge.decision({...surgeBase,protectionIndicator:'off',confirmNeed:true,confirmLowRisk:true,confirmAffiliate:true});
assert.equal(surgeQualified.code,'qualified_failed');
assert.equal(surgeQualified.commerce,true);
assert.ok(surge.calendar(90).includes('BEGIN:VCALENDAR'));
assert.equal(surge.report(surgeBase).route,surge.ROUTE);

const centerBase={scenario:'travel',tripDays:7,danger:false,existingWorks:false,newDevice:false,majorEvent:false};
assert.equal(center.makePlan({...centerBase,danger:true}).code,'danger');
assert.equal(center.makePlan({...centerBase,existingWorks:true}).code,'no_buy');
assert.equal(center.makePlan(centerBase).code,'travel');
assert.equal(center.makePlan({...centerBase,scenario:'storm'}).code,'storm');
assert.equal(center.makePlan({...centerBase,scenario:'new-device'}).code,'device');
assert.equal(center.makePlan({...centerBase,scenario:'routine'}).code,'routine');
assert.ok(center.calendar(center.makePlan(centerBase)).includes('BEGIN:VCALENDAR'));
assert.equal(center.report(centerBase).route,center.ROUTE);

for(const [name,html] of [['flight',flightHtml],['surge',surgeHtml],['center',centerHtml]]){
  for(const token of ['rel="canonical"','FAQPage','BreadcrumbList','ALO186'])assert.ok(html.includes(token),`${name}:${token}`);
  assert.ok(html.toLocaleLowerCase('tr-TR').includes('bağımsız'),`${name}:independence`);
  assert.ok(html.toLocaleLowerCase('tr-TR').includes('kişisel veri'),`${name}:personal-data`);
  for(const forbidden of ['https://www.amazon','https://amazon','"@type":"Product"','"@type":"Offer"','priceCurrency','aggregateRating','availability'])assert.ok(!html.includes(forbidden),`${name}:${forbidden}`);
}
assert.ok(flightHtml.includes('rel="sponsored nofollow noopener"'));
assert.ok(surgeHtml.includes('rel="sponsored nofollow noopener"'));
assert.ok(flightHtml.toLocaleLowerCase('tr-TR').includes('satış ortaklığı'));
assert.ok(surgeHtml.toLocaleLowerCase('tr-TR').includes('satış ortaklığı'));
assert.ok(!centerHtml.includes('rel="sponsored nofollow noopener"'));
assert.ok(centerHtml.includes(flight.ROUTE)&&centerHtml.includes(surge.ROUTE));
assert.ok(flightHtml.includes('iATA'.toUpperCase().replace('IATA','IATA'))||flightHtml.includes('IATA'));
assert.ok(surgeHtml.includes('NEMA')&&surgeHtml.includes('Schneider'));
for(const js of [fs.readFileSync(path.join(flightDir,'app.js'),'utf8'),fs.readFileSync(path.join(surgeDir,'app.js'),'utf8'),fs.readFileSync(path.join(centerDir,'app.js'),'utf8')])for(const forbidden of ['fetch(','navigator.geolocation','localStorage','sessionStorage'])assert.ok(!js.includes(forbidden),forbidden);
for(const token of ['@media(max-width:820px)','@media(max-width:560px)','min-height:48px','prefers-reduced-motion','forced-colors','focus-visible'])assert.ok(sharedCss.includes(token),token);
assert.ok(!/outline\s*:\s*(?:0|none)\b/i.test(sharedCss));
assert.equal(overlay.version,132);
assert.deepEqual(overlay.routes.map((route)=>route.canonicalPath),[flight.ROUTE,surge.ROUTE,center.ROUTE]);

const temp=fs.mkdtempSync(path.join(os.tmpdir(),'alo186-travel-surge-v132-'));
const canonical=path.join(temp,'canonical');
execFileSync('python',[path.join(ROOT,'alo186','deployment','build_static_site.py'),'--output',canonical,'--commit','travel-surge-v132-test'],{cwd:ROOT,stdio:'pipe'});
const sitemap=fs.readFileSync(path.join(canonical,'sitemap.xml'),'utf8');
for(const route of [flight.ROUTE,surge.ROUTE,center.ROUTE])assert.ok(sitemap.includes(route),route);
for(const file of [
  path.join(canonical,'hesaplama','powerbank-ucak-wh-kabin-bagaji-uygunluk','index.html'),
  path.join(canonical,'hesaplama','akim-korumali-priz-koruma-gostergesi-omur-testi','index.html'),
  path.join(canonical,'sektor-rehberi','elektronik-cihaz-guc-seyahat-koruma-merkezi','index.html')
])assert.ok(fs.existsSync(file),file);
for(const basePath of ['','/chatgpt']){
  const target=path.join(temp,basePath?'project':'custom');
  fs.cpSync(canonical,target,{recursive:true});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','prepare_github_pages.py'),'--site',target,'--base-path',basePath,'--repository','ozaneryavuz/chatgpt','--commit','travel-surge-v132-test'],{cwd:ROOT,stdio:'pipe'});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','smoke_github_pages.py'),'--site',target,'--base-path',basePath],{cwd:ROOT,stdio:'pipe'});
  const expected=`${basePath}/assets/alo186-ux.js`||'/assets/alo186-ux.js';
  for(const file of [
    path.join(target,'hesaplama','powerbank-ucak-wh-kabin-bagaji-uygunluk','index.html'),
    path.join(target,'hesaplama','akim-korumali-priz-koruma-gostergesi-omur-testi','index.html'),
    path.join(target,'sektor-rehberi','elektronik-cihaz-guc-seyahat-koruma-merkezi','index.html')
  ])assert.ok(fs.readFileSync(file,'utf8').includes(expected),`${basePath}:${file}`);
}
fs.rmSync(temp,{recursive:true,force:true});
console.log(JSON.stringify({ok:true,version:132,routes:[flight.ROUTE,surge.ROUTE,center.ROUTE],flightWh:true,airlineRuleUserVerified:true,surgeIndicator:true,jouleOnlyNoBuy:true,repeatVisitPlan:true,affiliateTransparent:true,unsafeCommerceClosed:true,unverifiedCommercialFields:false,personalData:false,customDomain:true,projectPath:true}));
