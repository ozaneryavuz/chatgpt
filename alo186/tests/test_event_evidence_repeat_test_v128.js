'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {execFileSync}=require('node:child_process');

const ROOT=path.resolve(__dirname,'..','..');
const outageDir=path.join(ROOT,'alo186','hesaplama','elektrik-kesintisi-sure-siklik-gunlugu');
const voltageDir=path.join(ROOT,'alo186','hesaplama','gerilim-dalgalanmasi-cihaz-reset-kanit-gunlugu');
const centerDir=path.join(ROOT,'alo186','sektor-rehberi','elektrik-olay-kanit-ve-tekrar-test-merkezi');
const outage=require(path.join(outageDir,'app.js'));
const voltage=require(path.join(voltageDir,'app.js'));
const center=require(path.join(centerDir,'app.js'));
const outageHtml=fs.readFileSync(path.join(outageDir,'index.html'),'utf8');
const voltageHtml=fs.readFileSync(path.join(voltageDir,'index.html'),'utf8');
const centerHtml=fs.readFileSync(path.join(centerDir,'index.html'),'utf8');
const outageJs=fs.readFileSync(path.join(outageDir,'app.js'),'utf8');
const voltageJs=fs.readFileSync(path.join(voltageDir,'app.js'),'utf8');
const centerJs=fs.readFileSync(path.join(centerDir,'app.js'),'utf8');
const css=fs.readFileSync(path.join(outageDir,'styles.css'),'utf8');
const overlay=JSON.parse(fs.readFileSync(path.join(ROOT,'alo186','deployment','routing-overlays','128-event-evidence-repeat-test.json'),'utf8'));

for(const file of [path.join(outageDir,'app.js'),path.join(voltageDir,'app.js'),path.join(centerDir,'app.js')])execFileSync('node',['--check',file],{cwd:ROOT,stdio:'pipe'});

const recent=(minutesAgo)=>new Date(Date.now()-minutesAgo*60000).toISOString();
const outageBase={start:recent(180),end:recent(120),scope:'home',officialRecord:'yes',active:false,restoration:'normal',impacts:['internet'],criticalGap:true,emergency:false,createdAt:Date.now()};
assert.equal(outage.durationMinutes(outageBase.start,outageBase.end),60);
assert.equal(outage.decide({...outageBase,emergency:true},[]).code,'emergency');
assert.equal(outage.decide({...outageBase,active:true},[]).code,'active_outage');
assert.equal(outage.decide({...outageBase,impacts:['medical']},[]).code,'medical');
assert.equal(outage.decide(outageBase,[]).code,'single_event');
const priorOutage={...outageBase,start:recent(3000),end:recent(2940),createdAt:Date.now()-1000};
const qualifiedOutage=outage.decide(outageBase,[priorOutage]);
assert.equal(qualifiedOutage.code,'qualified_gap');
assert.equal(qualifiedOutage.commerce,true);
assert.equal(qualifiedOutage.productClass,'internet_backup');
assert.ok(outage.csv([outage.cleanRecord(outageBase)]).includes('duration_minutes'));
assert.ok(outage.calendar(30).includes('BEGIN:VCALENDAR'));

const voltageBase={eventAt:recent(60),scope:'single_device',symptoms:['reset'],measurementSource:'none',minV:0,maxV:0,repeated:true,officialRecord:false,lowRiskPlugLoad:true,existingMonitor:false,emergency:false,createdAt:Date.now()};
assert.equal(voltage.decide({...voltageBase,emergency:true},[]).code,'emergency');
assert.equal(voltage.decide({...voltageBase,symptoms:['bright','dim'],scope:'home'},[]).code,'network_or_neutral');
assert.equal(voltage.decide({...voltageBase,symptoms:['damage']},[]).code,'damage');
assert.equal(voltage.decide({...voltageBase,existingMonitor:true},[{...voltageBase,eventAt:recent(3000),createdAt:Date.now()-1000}]).code,'no_buy');
assert.equal(voltage.decide({...voltageBase,lowRiskPlugLoad:false},[{...voltageBase,eventAt:recent(3000),createdAt:Date.now()-1000}]).code,'professional');
const qualifiedVoltage=voltage.decide(voltageBase,[{...voltageBase,eventAt:recent(3000),createdAt:Date.now()-1000}]);
assert.equal(qualifiedVoltage.code,'qualified_monitor');
assert.equal(qualifiedVoltage.commerce,true);
assert.ok(voltage.csv([voltage.clean(voltageBase)]).includes('measurement_source'));
assert.ok(voltage.calendar(30).includes('BEGIN:VCALENDAR'));

assert.equal(center.makePlan({eventType:'outage',system:'internet',frequency:0,evidence:'single',active:false,emergency:false,existingPlan:'none'}).days,90);
assert.equal(center.makePlan({eventType:'voltage',system:'security',frequency:3,evidence:'repeated',active:false,emergency:false,existingPlan:'failed'}).days,30);
assert.equal(center.makePlan({eventType:'outage',system:'medical',frequency:1,evidence:'repeated',active:false,emergency:false,existingPlan:'failed'}).code,'sensitive');
assert.equal(center.makePlan({eventType:'outage',system:'internet',frequency:1,evidence:'repeated',active:true,emergency:false,existingPlan:'none'}).code,'active');
assert.equal(center.makePlan({eventType:'outage',system:'internet',frequency:1,evidence:'single',active:false,emergency:true,existingPlan:'none'}).code,'emergency');
assert.ok(center.calendar(center.makePlan({eventType:'outage',system:'internet',frequency:1,evidence:'single',active:false,emergency:false,existingPlan:'none'})).includes('BEGIN:VCALENDAR'));

for(const [name,html] of [['outage',outageHtml],['voltage',voltageHtml],['center',centerHtml]]){
  for(const token of ['rel="canonical"','FAQPage','BreadcrumbList'])assert.ok(html.includes(token),`${name}:${token}`);
  assert.ok(html.toLocaleLowerCase('tr-TR').includes('kişisel veri'),`${name}:kişisel veri`);
  for(const forbidden of ['amazon.com','amazon.com.tr','"@type":"Product"','"@type":"Offer"','priceCurrency','aggregateRating','availability'])assert.ok(!html.includes(forbidden),`${name}:${forbidden}`);
  assert.ok(html.includes('ALO186')&&html.includes('bağımsız'),`${name}:independence`);
}
for(const js of [outageJs,voltageJs]){
  for(const token of ['sponsored nofollow noopener','localStorage','MAX_RECORDS','TTL_DAYS','text/calendar'])assert.ok(js.includes(token),token);
  for(const forbidden of ['navigator.geolocation','fetch('])assert.ok(!js.includes(forbidden),forbidden);
}
for(const token of ['text/calendar','commerce:false','P0','P1','P2'])assert.ok(centerJs.includes(token),token);
for(const token of ['@media(max-width:820px)','@media(max-width:560px)','min-height:48px','prefers-reduced-motion','forced-colors','focus-visible'])assert.ok(css.includes(token),token);
assert.ok(!/outline\s*:\s*(?:0|none)\b/i.test(css));

assert.equal(overlay.version,128);
assert.deepEqual(overlay.routes.map(r=>r.canonicalPath),[outage.ROUTE,voltage.ROUTE,center.ROUTE]);

const temp=fs.mkdtempSync(path.join(os.tmpdir(),'alo186-event-evidence-v128-'));
const canonical=path.join(temp,'canonical');
execFileSync('python',[path.join(ROOT,'alo186','deployment','build_static_site.py'),'--output',canonical,'--commit','event-evidence-v128-test'],{cwd:ROOT,stdio:'pipe'});
const sitemap=fs.readFileSync(path.join(canonical,'sitemap.xml'),'utf8');
for(const route of [outage.ROUTE,voltage.ROUTE,center.ROUTE])assert.ok(sitemap.includes(route),route);
for(const file of [
  path.join(canonical,'hesaplama','elektrik-kesintisi-sure-siklik-gunlugu','index.html'),
  path.join(canonical,'hesaplama','elektrik-kesintisi-sure-siklik-gunlugu','styles.css'),
  path.join(canonical,'hesaplama','gerilim-dalgalanmasi-cihaz-reset-kanit-gunlugu','index.html'),
  path.join(canonical,'sektor-rehberi','elektrik-olay-kanit-ve-tekrar-test-merkezi','index.html')
])assert.ok(fs.existsSync(file),file);

for(const basePath of ['','/chatgpt']){
  const target=path.join(temp,basePath?'project':'custom');
  fs.cpSync(canonical,target,{recursive:true});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','prepare_github_pages.py'),'--site',target,'--base-path',basePath,'--repository','ozaneryavuz/chatgpt','--commit','event-evidence-v128-test'],{cwd:ROOT,stdio:'pipe'});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','smoke_github_pages.py'),'--site',target,'--base-path',basePath],{cwd:ROOT,stdio:'pipe'});
  const expected=`${basePath}/assets/alo186-ux.js`||'/assets/alo186-ux.js';
  for(const file of [
    path.join(target,'hesaplama','elektrik-kesintisi-sure-siklik-gunlugu','index.html'),
    path.join(target,'hesaplama','gerilim-dalgalanmasi-cihaz-reset-kanit-gunlugu','index.html'),
    path.join(target,'sektor-rehberi','elektrik-olay-kanit-ve-tekrar-test-merkezi','index.html')
  ])assert.ok(fs.readFileSync(file,'utf8').includes(expected),`${basePath}:${file}`);
}
fs.rmSync(temp,{recursive:true,force:true});
console.log(JSON.stringify({ok:true,version:128,routes:[outage.ROUTE,voltage.ROUTE,center.ROUTE],outageEvidence:true,voltageEvidence:true,repeatVisitPlanner:true,noBuyOutcome:true,activeEventCommerceClosed:true,medicalCommerceClosed:true,affiliateTransparent:true,unverifiedCommercialFields:false,personalData:false,customDomain:true,projectPath:true}));