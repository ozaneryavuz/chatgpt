'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {execFileSync}=require('node:child_process');

const ROOT=path.resolve(__dirname,'..','..');
const billDir=path.join(ROOT,'alo186','hesaplama','elektrik-faturasi-kwh-gun-karsilastirma');
const meterDir=path.join(ROOT,'alo186','hesaplama','priz-tipi-enerji-olcer-standby-deneyi');
const centerDir=path.join(ROOT,'alo186','sektor-rehberi','ev-elektrik-tuketimi-kanit-ve-tasarruf-merkezi');
const bill=require(path.join(billDir,'app.js'));
const meter=require(path.join(meterDir,'app.js'));
const center=require(path.join(centerDir,'app.js'));
const billHtml=fs.readFileSync(path.join(billDir,'index.html'),'utf8');
const meterHtml=fs.readFileSync(path.join(meterDir,'index.html'),'utf8');
const centerHtml=fs.readFileSync(path.join(centerDir,'index.html'),'utf8');
const billJs=fs.readFileSync(path.join(billDir,'app.js'),'utf8');
const meterJs=fs.readFileSync(path.join(meterDir,'app.js'),'utf8');
const centerJs=fs.readFileSync(path.join(centerDir,'app.js'),'utf8');
const css=fs.readFileSync(path.join(billDir,'styles.css'),'utf8');
const overlay=JSON.parse(fs.readFileSync(path.join(ROOT,'alo186','deployment','routing-overlays','129-home-energy-evidence.json'),'utf8'));

for(const file of [path.join(billDir,'app.js'),path.join(meterDir,'app.js'),path.join(centerDir,'app.js')])execFileSync('node',['--check',file],{cwd:ROOT,stdio:'pipe'});

const billBase={currentKwh:300,currentDays:30,previousKwh:200,previousDays:30,seasonal:false,newDevice:false,occupancy:false,supplierIssue:false,existingMeter:false,lowRiskPlugLoads:true,emergency:false,meterPhysical:false};
const billMetrics=bill.metrics(billBase);
assert.equal(billMetrics.currentDaily,10);
assert.ok(Math.abs(billMetrics.previousDaily-6.6666667)<0.001);
assert.ok(billMetrics.changePct>49&&billMetrics.changePct<51);
assert.equal(bill.decide({...billBase,emergency:true}).code,'emergency');
assert.equal(bill.decide({...billBase,meterPhysical:true}).code,'meter_physical');
assert.equal(bill.decide({...billBase,currentKwh:0}).code,'invalid');
assert.equal(bill.decide({...billBase,currentKwh:205}).code,'stable');
assert.equal(bill.decide({...billBase,seasonal:true}).code,'explained');
assert.equal(bill.decide({...billBase,existingMeter:true}).code,'use_existing');
assert.equal(bill.decide(billBase).code,'measure_plug_loads');
assert.equal(bill.decide({...billBase,lowRiskPlugLoads:false}).code,'professional');
assert.equal(bill.report(billBase).route,bill.ROUTE);

const meterBase={device:'tv',days:7,safePlug:true,excludedLoad:false,existingMeter:false,networkNeeded:false,activeW:100,standbyW:2,activeHours:4,offHours:8,confirmNeed:false,confirmSafe:false,confirmAffiliate:false,emergency:false};
const meterMetrics=meter.calculate(meterBase);
assert.equal(meterMetrics.activeKwhDay,0.4);
assert.ok(Math.abs(meterMetrics.standbyKwhMonth-1.2)<0.001);
assert.ok(meterMetrics.avoidableKwhMonth>0.4);
assert.equal(meter.decide({...meterBase,emergency:true}).code,'emergency');
assert.equal(meter.decide({...meterBase,excludedLoad:true}).code,'excluded');
assert.equal(meter.decide({...meterBase,safePlug:false}).code,'unsafe');
assert.equal(meter.decide({...meterBase,existingMeter:true}).code,'no_buy');
assert.equal(meter.decide({...meterBase,activeW:0,standbyW:0}).code,'measure_first');
const qualified=meter.decide({...meterBase,activeW:0,standbyW:0,confirmNeed:true,confirmSafe:true,confirmAffiliate:true});
assert.equal(qualified.code,'qualified_meter');
assert.equal(qualified.commerce,true);
assert.equal(meter.decide(meterBase).code,'measured');
assert.ok(meter.calendar(7).includes('BEGIN:VCALENDAR'));
assert.equal(meter.report(meterBase).route,meter.ROUTE);

const centerBase={goal:'bill',system:'electronics',emergency:false,twoBills:true,existingMeter:false,fixedLoad:false,officialIssue:false,newDevice:false};
assert.equal(center.makePlan({...centerBase,emergency:true}).code,'emergency');
assert.equal(center.makePlan({...centerBase,officialIssue:true}).code,'official');
assert.equal(center.makePlan({...centerBase,fixedLoad:true}).code,'professional');
assert.equal(center.makePlan({...centerBase,existingMeter:true}).code,'use_existing');
const plan=center.makePlan(centerBase);
assert.equal(plan.days,30);
assert.ok(plan.tasks.length>=4);
assert.ok(center.calendar(plan).includes('BEGIN:VCALENDAR'));
assert.equal(center.report(centerBase).route,center.ROUTE);

for(const [name,html] of [['bill',billHtml],['meter',meterHtml],['center',centerHtml]]){
  for(const token of ['rel="canonical"','FAQPage','BreadcrumbList'])assert.ok(html.includes(token),`${name}:${token}`);
  assert.ok(html.toLocaleLowerCase('tr-TR').includes('kişisel veri'),`${name}:personal-data`);
  assert.ok(html.includes('ALO186')&&html.toLocaleLowerCase('tr-TR').includes('bağımsız'),`${name}:independence`);
  for(const forbidden of ['amazon.com','amazon.com.tr','"@type":"Product"','"@type":"Offer"','priceCurrency','aggregateRating','availability'])assert.ok(!html.includes(forbidden),`${name}:${forbidden}`);
}
assert.ok(meterHtml.includes('rel="sponsored nofollow noopener"'));
assert.ok(meterHtml.includes('satış ortaklığı'));
assert.ok(billHtml.includes('/hesaplama/priz-tipi-enerji-olcer-standby-deneyi/'));
assert.ok(centerHtml.includes(bill.ROUTE)&&centerHtml.includes(meter.ROUTE));
for(const js of [billJs,meterJs,centerJs])for(const forbidden of ['fetch(','navigator.geolocation','localStorage','sessionStorage'])assert.ok(!js.includes(forbidden),forbidden);
for(const token of ['@media(max-width:820px)','@media(max-width:560px)','min-height:48px','prefers-reduced-motion','forced-colors','focus-visible'])assert.ok(css.includes(token),token);
assert.ok(!/outline\s*:\s*(?:0|none)\b/i.test(css));

assert.equal(overlay.version,131);
assert.deepEqual(overlay.routes.map(r=>r.canonicalPath),[bill.ROUTE,meter.ROUTE,center.ROUTE]);

const temp=fs.mkdtempSync(path.join(os.tmpdir(),'alo186-home-energy-v131-'));
const canonical=path.join(temp,'canonical');
execFileSync('python',[path.join(ROOT,'alo186','deployment','build_static_site.py'),'--output',canonical,'--commit','home-energy-v131-test'],{cwd:ROOT,stdio:'pipe'});
const sitemap=fs.readFileSync(path.join(canonical,'sitemap.xml'),'utf8');
for(const route of [bill.ROUTE,meter.ROUTE,center.ROUTE])assert.ok(sitemap.includes(route),route);
for(const file of [
  path.join(canonical,'hesaplama','elektrik-faturasi-kwh-gun-karsilastirma','index.html'),
  path.join(canonical,'hesaplama','elektrik-faturasi-kwh-gun-karsilastirma','styles.css'),
  path.join(canonical,'hesaplama','priz-tipi-enerji-olcer-standby-deneyi','index.html'),
  path.join(canonical,'sektor-rehberi','ev-elektrik-tuketimi-kanit-ve-tasarruf-merkezi','index.html')
])assert.ok(fs.existsSync(file),file);

for(const basePath of ['','/chatgpt']){
  const target=path.join(temp,basePath?'project':'custom');
  fs.cpSync(canonical,target,{recursive:true});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','prepare_github_pages.py'),'--site',target,'--base-path',basePath,'--repository','ozaneryavuz/chatgpt','--commit','home-energy-v131-test'],{cwd:ROOT,stdio:'pipe'});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','smoke_github_pages.py'),'--site',target,'--base-path',basePath],{cwd:ROOT,stdio:'pipe'});
  const expected=`${basePath}/assets/alo186-ux.js`||'/assets/alo186-ux.js';
  for(const file of [
    path.join(target,'hesaplama','elektrik-faturasi-kwh-gun-karsilastirma','index.html'),
    path.join(target,'hesaplama','priz-tipi-enerji-olcer-standby-deneyi','index.html'),
    path.join(target,'sektor-rehberi','ev-elektrik-tuketimi-kanit-ve-tasarruf-merkezi','index.html')
  ])assert.ok(fs.readFileSync(file,'utf8').includes(expected),`${basePath}:${file}`);
}
fs.rmSync(temp,{recursive:true,force:true});
console.log(JSON.stringify({ok:true,version:131,routes:[bill.ROUTE,meter.ROUTE,center.ROUTE],billKwhPerDay:true,standbyMeasurement:true,repeatVisitPlan:true,noBuyOutcome:true,affiliateTransparent:true,activeRiskCommerceClosed:true,unverifiedCommercialFields:false,personalData:false,customDomain:true,projectPath:true}));