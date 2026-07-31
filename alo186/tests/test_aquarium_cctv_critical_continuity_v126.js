'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {execFileSync}=require('node:child_process');

const ROOT=path.resolve(__dirname,'..','..');
const routes={
  aquarium:'akvaryum-elektrik-kesintisi-yedek-guc-uygunluk',
  cctv:'kamera-nvr-poe-ups-uygunluk',
  center:'kritik-sistemler-yedek-guc-test-merkezi'
};
const aquariumDir=path.join(ROOT,'alo186','hesaplama',routes.aquarium);
const cctvDir=path.join(ROOT,'alo186','hesaplama',routes.cctv);
const centerDir=path.join(ROOT,'alo186','sektor-rehberi',routes.center);
const aquariumHtml=fs.readFileSync(path.join(aquariumDir,'index.html'),'utf8');
const cctvHtml=fs.readFileSync(path.join(cctvDir,'index.html'),'utf8');
const centerHtml=fs.readFileSync(path.join(centerDir,'index.html'),'utf8');
const aquariumJs=fs.readFileSync(path.join(aquariumDir,'app.js'),'utf8');
const cctvJs=fs.readFileSync(path.join(cctvDir,'app.js'),'utf8');
const centerJs=fs.readFileSync(path.join(centerDir,'app.js'),'utf8');
const css=fs.readFileSync(path.join(ROOT,'alo186','assets','critical-continuity-v126.css'),'utf8');
const overlay=JSON.parse(fs.readFileSync(path.join(ROOT,'alo186','deployment','routing-overlays','126-aquarium-cctv-critical-continuity.json'),'utf8'));
const aquarium=require(path.join(aquariumDir,'app.js'));
const cctv=require(path.join(cctvDir,'app.js'));
const center=require(path.join(centerDir,'app.js'));

for(const file of [path.join(aquariumDir,'app.js'),path.join(cctvDir,'app.js'),path.join(centerDir,'app.js')]){
  execFileSync('node',['--check',file],{cwd:ROOT,stdio:'pipe'});
}

const aquariumBase={
  electricalEmergency:false,livestockDistress:false,scenario:'planning',systemType:'freshwater',backupPlan:'air_flow',continuity:'no_restart',connection:'safe',
  airW:8,circulationW:12,filterW:20,returnPumpW:0,heaterW:0,chillerW:0,lightingW:0,otherW:0,targetHours:6,loadEvidence:'measured',
  sourceStatus:'none',sourceW:0,sourceVA:0,sourceWh:0,waveform:'unknown',transferTest:'untested',runtimeTest:'untested'
};
assert.deepEqual(aquarium.calculate(aquariumBase),{
  loads:{air:8,circulation:12,filter:20,returnPump:0,heater:0,chiller:0,lighting:0,other:0},
  totalW:20,keys:['air','circulation'],targetHours:6,requiredW:30,requiredVA:50,requiredWh:180,thermalW:0
});
assert.equal(aquarium.decide({...aquariumBase,electricalEmergency:true}).commerce,false);
assert.equal(aquarium.decide({...aquariumBase,livestockDistress:true}).code,'livestock_distress');
assert.equal(aquarium.decide({...aquariumBase,scenario:'active'}).commerce,false);
assert.equal(aquarium.decide({...aquariumBase,systemType:'reef',backupPlan:'air_only'}).code,'reef_plan');
assert.equal(aquarium.decide({...aquariumBase,sourceStatus:'existing',sourceW:100,sourceVA:200,sourceWh:500,waveform:'approved',transferTest:'success',runtimeTest:'success'}).code,'no_buy');
assert.equal(aquarium.decide({...aquariumBase,backupPlan:'air_only',airW:8,continuity:'restart_ok'}).productClass,'battery_air_pump');

const cctvBase={
  emergency:false,scenario:'planning',systemScope:'home',continuity:'no_restart',connection:'direct',
  nvrW:45,poeSwitchW:18,cameraCount:8,cameraW:10,routerW:25,monitorW:0,alarmW:0,otherW:0,targetHours:2,loadEvidence:'measured',
  sourceStatus:'none',sourceW:0,sourceVA:0,sourceWh:0,waveform:'unknown',transferTest:'untested',runtimeTest:'untested',recordingTest:'untested'
};
assert.deepEqual(cctv.calculate(cctvBase),{cameraW:80,totalW:168,targetHours:2,requiredW:210,requiredVA:300,requiredWh:500,monitorW:0});
assert.equal(cctv.decide({...cctvBase,systemScope:'life_safety'}).commerce,false);
assert.equal(cctv.decide({...cctvBase,systemScope:'multi_closet'}).commerce,false);
assert.equal(cctv.decide({...cctvBase,scenario:'active'}).commerce,false);
assert.equal(cctv.decide({...cctvBase,sourceStatus:'existing',sourceW:500,sourceVA:1000,sourceWh:1000,waveform:'approved',transferTest:'success',runtimeTest:'success',recordingTest:'success'}).code,'no_buy');
assert.equal(cctv.decide({...cctvBase,sourceStatus:'existing',sourceW:500,sourceVA:1000,sourceWh:1000,waveform:'approved',transferTest:'success',runtimeTest:'success',recordingTest:'failed'}).code,'recording_fail');

assert.equal(center.makePlan({emergency:false,systemType:'aquarium',scenario:'planning',frequencyDays:90}).route,aquarium.ROUTE);
assert.equal(center.makePlan({emergency:false,systemType:'medical',scenario:'planning',frequencyDays:30}).commerce,false);
assert.equal(center.makePlan({emergency:false,systemType:'cctv',scenario:'active',frequencyDays:90}).commerce,false);
assert.equal(center.makePlan({emergency:true,systemType:'internet',scenario:'planning',frequencyDays:90}).emergency,true);

for(const [name,html] of [['aquarium',aquariumHtml],['cctv',cctvHtml],['center',centerHtml]]){
  for(const token of ['rel="canonical"','FAQPage','BreadcrumbList','Kişisel veri'])assert.ok(html.includes(token),`${name}:${token}`);
  for(const forbidden of ['amazon.com','amazon.com.tr','"@type":"Product"','"@type":"Offer"','priceCurrency','aggregateRating','availability'])assert.ok(!html.includes(forbidden),`${name}:${forbidden}`);
}
for(const [name,js] of [['aquarium',aquariumJs],['cctv',cctvJs],['center',centerJs]]){
  for(const forbidden of ['localStorage','sessionStorage','navigator.geolocation','fetch('])assert.ok(!js.includes(forbidden),`${name}:${forbidden}`);
  assert.ok(js.includes('.ics')||js.includes('text/calendar'),`${name}:calendar`);
}
for(const js of [aquariumJs,cctvJs]){
  for(const token of ['sponsored nofollow noopener','confirmGap','confirmSpecs','confirmAffiliate','no_buy','active_outage'])assert.ok(js.includes(token),token);
}
for(const token of ['@media(max-width:820px)','@media(max-width:560px)','min-height:48px','prefers-reduced-motion','forced-colors','focus-visible'])assert.ok(css.includes(token),token);
assert.ok(!/outline\s*:\s*(?:0|none)\b/i.test(css));

assert.deepEqual(overlay,{
  version:126,
  generatedAt:'2026-07-31',
  routes:[
    {source:`alo186/hesaplama/${routes.aquarium}/index.html`,canonicalPath:aquarium.ROUTE,type:'calculator'},
    {source:`alo186/hesaplama/${routes.cctv}/index.html`,canonicalPath:cctv.ROUTE,type:'calculator'},
    {source:`alo186/sektor-rehberi/${routes.center}/index.html`,canonicalPath:center.ROUTE,type:'guide'}
  ]
});

const temp=fs.mkdtempSync(path.join(os.tmpdir(),'alo186-critical-continuity-v126-'));
const canonical=path.join(temp,'canonical');
execFileSync('python',[path.join(ROOT,'alo186','deployment','build_static_site.py'),'--output',canonical,'--commit','critical-continuity-v126-test'],{cwd:ROOT,stdio:'pipe'});
const sitemap=fs.readFileSync(path.join(canonical,'sitemap.xml'),'utf8');
for(const route of [aquarium.ROUTE,cctv.ROUTE,center.ROUTE])assert.ok(sitemap.includes(route),route);
for(const file of [
  path.join(canonical,'hesaplama',routes.aquarium,'index.html'),
  path.join(canonical,'hesaplama',routes.cctv,'index.html'),
  path.join(canonical,'sektor-rehberi',routes.center,'index.html'),
  path.join(canonical,'assets','critical-continuity-v126.css')
])assert.ok(fs.existsSync(file),file);

for(const basePath of ['','/chatgpt']){
  const target=path.join(temp,basePath?'project':'custom');
  fs.cpSync(canonical,target,{recursive:true});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','prepare_github_pages.py'),'--site',target,'--base-path',basePath,'--repository','ozaneryavuz/chatgpt','--commit','critical-continuity-v126-test'],{cwd:ROOT,stdio:'pipe'});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','smoke_github_pages.py'),'--site',target,'--base-path',basePath],{cwd:ROOT,stdio:'pipe'});
  const expectedAsset=`${basePath}/assets/alo186-ux.js`||'/assets/alo186-ux.js';
  for(const file of [
    path.join(target,'hesaplama',routes.aquarium,'index.html'),
    path.join(target,'hesaplama',routes.cctv,'index.html'),
    path.join(target,'sektor-rehberi',routes.center,'index.html')
  ]){
    const page=fs.readFileSync(file,'utf8');
    assert.ok(page.includes(expectedAsset),`${basePath}:${file}`);
  }
}
fs.rmSync(temp,{recursive:true,force:true});

console.log(JSON.stringify({
  ok:true,version:126,routes:[aquarium.ROUTE,cctv.ROUTE,center.ROUTE],
  aquariumIntent:true,cctvIntent:true,repeatVisitPlanner:true,
  noBuyOutcome:true,activeOutageCommerceClosed:true,medicalCommerceClosed:true,
  affiliateTransparent:true,priceStockRatingWarranty:false,personalData:false,
  customDomain:true,projectPath:true
}));
