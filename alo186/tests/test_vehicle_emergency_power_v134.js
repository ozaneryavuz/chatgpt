'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {execFileSync}=require('node:child_process');

const ROOT=path.resolve(__dirname,'..','..');
const jumpDir=path.join(ROOT,'alo186','hesaplama','aku-takviye-cihazi-jump-starter-uygunluk');
const inverterDir=path.join(ROOT,'alo186','hesaplama','arac-12v-priz-inverter-yuk-uygunluk');
const hubDir=path.join(ROOT,'alo186','sektor-rehberi','arac-aku-ve-acil-enerji-test-merkezi');
const jump=require(path.join(jumpDir,'app.js'));
const inverter=require(path.join(inverterDir,'app.js'));
const hub=require(path.join(hubDir,'app.js'));
const jumpHtml=fs.readFileSync(path.join(jumpDir,'index.html'),'utf8');
const inverterHtml=fs.readFileSync(path.join(inverterDir,'index.html'),'utf8');
const hubHtml=fs.readFileSync(path.join(hubDir,'index.html'),'utf8');
const overlay=JSON.parse(fs.readFileSync(path.join(ROOT,'alo186','deployment','routing-overlays','134-vehicle-emergency-power.json'),'utf8'));

for(const file of [path.join(jumpDir,'app.js'),path.join(inverterDir,'app.js'),path.join(hubDir,'app.js')])execFileSync('node',['--check',file],{cwd:ROOT,stdio:'pipe'});

const jumpBase={danger:false,batteryDamage:false,frozenBattery:false,activeRoadside:false,vehicleClass:'gasoline',systemVoltage:'12',manualVerified:true,connectionPointsVerified:true,batteryTypeVerified:true,batteryType:'agm',lithiumApproved:false,hasExisting:false,existingTested:false,existingVoltageMatch:false,existingVehicleMatch:false,existingPhysicalSafe:true,existingChargeReady:false,confirmNeed:false,confirmManual:false,confirmAffiliate:false};
assert.equal(jump.decide({...jumpBase,danger:true}).code,'danger');
assert.equal(jump.decide({...jumpBase,activeRoadside:true}).code,'active');
assert.equal(jump.decide({...jumpBase,vehicleClass:'ev'}).code,'special_vehicle');
assert.equal(jump.decide({...jumpBase,systemVoltage:'24'}).code,'voltage');
assert.equal(jump.decide({...jumpBase,manualVerified:false}).code,'evidence');
assert.equal(jump.decide({...jumpBase,batteryType:'lithium'}).code,'lithium');
assert.equal(jump.decide({...jumpBase,hasExisting:true,existingTested:true,existingVoltageMatch:true,existingVehicleMatch:true,existingPhysicalSafe:true,existingChargeReady:true}).code,'no_buy');
const jumpQualified=jump.decide({...jumpBase,confirmNeed:true,confirmManual:true,confirmAffiliate:true});
assert.equal(jumpQualified.code,'eligible');assert.equal(jumpQualified.commerce,true);

const inverterBase={danger:false,socketDamage:false,voltage:12,loadW:65,efficiencyPct:85,socketMaxA:10,inverterInputMaxA:15,inverterOutputW:150,loadClass:'electronics',connection:'accessory',manualVerified:true,socketLabelVerified:true,inverterLabelVerified:true,engineOff:false,runtimeMinutes:30,batteryEnergyVerified:false,existingSuitable:false,realLoadTest:false,noHeat:false,confirmNeed:false,confirmLabel:false,confirmAffiliate:false};
const calc=inverter.calculate(inverterBase);assert.ok(calc.dcA>6.3&&calc.dcA<6.4);assert.ok(calc.plannedA>7.6&&calc.plannedA<7.7);assert.equal(calc.socketW,120);
assert.equal(inverter.decide({...inverterBase,danger:true}).code,'danger');
assert.equal(inverter.decide({...inverterBase,loadClass:'heater'}).code,'unsupported');
assert.equal(inverter.decide({...inverterBase,connection:'direct_battery'}).code,'installation');
assert.equal(inverter.decide({...inverterBase,manualVerified:false}).code,'evidence');
assert.equal(inverter.decide({...inverterBase,loadW:140}).code,'overload');
assert.equal(inverter.decide({...inverterBase,engineOff:true,runtimeMinutes:120}).code,'battery_runtime');
assert.equal(inverter.decide({...inverterBase,existingSuitable:true,realLoadTest:true,noHeat:true}).code,'no_buy');
const inverterQualified=inverter.decide({...inverterBase,confirmNeed:true,confirmLabel:true,confirmAffiliate:true});
assert.equal(inverterQualified.code,'eligible');assert.equal(inverterQualified.commerce,true);

const plan=hub.buildPlan({danger:false,failedStart:true,longTrip:true,accessoryPower:true,vehicleChanged:false,storedVehicle:false});
assert.equal(plan.repeatDays,30);assert.equal(plan.commerce,false);assert.equal(plan.personalData,false);assert.ok(plan.tasks.length>=4);
const routine=hub.buildPlan({danger:false,failedStart:false,longTrip:false,accessoryPower:false,vehicleChanged:false,storedVehicle:false});assert.equal(routine.repeatDays,90);

for(const [name,html] of [['jump',jumpHtml],['inverter',inverterHtml],['hub',hubHtml]]){
  for(const token of ['rel="canonical"','FAQPage','BreadcrumbList','ALO186'])assert.ok(html.includes(token),`${name}:${token}`);
  assert.ok(html.toLocaleLowerCase('tr-TR').includes('bağımsız'),`${name}:independence`);
  assert.ok(html.toLocaleLowerCase('tr-TR').includes('kişisel veri'),`${name}:personal-data`);
  for(const forbidden of ['https://www.amazon','https://amazon','"@type":"Product"','"@type":"Offer"','priceCurrency','aggregateRating','availability'])assert.ok(!html.includes(forbidden),`${name}:${forbidden}`);
}
assert.ok(jumpHtml.includes('rel="sponsored nofollow noopener"'));
assert.ok(inverterHtml.includes('rel="sponsored nofollow noopener"'));
assert.ok(!hubHtml.includes('rel="sponsored nofollow noopener"'));
assert.ok(hubHtml.includes(jump.ROUTE)&&hubHtml.includes(inverter.ROUTE));
assert.ok(jumpHtml.includes('UL 2743')&&jumpHtml.includes('SAE J1494'));
assert.ok(inverterHtml.includes('SAE J2185:2026'));
for(const js of [fs.readFileSync(path.join(jumpDir,'app.js'),'utf8'),fs.readFileSync(path.join(inverterDir,'app.js'),'utf8'),fs.readFileSync(path.join(hubDir,'app.js'),'utf8')])for(const forbidden of ['fetch(','navigator.geolocation','localStorage','sessionStorage'])assert.ok(!js.includes(forbidden),forbidden);
assert.equal(overlay.version,134);
assert.deepEqual(overlay.routes.map((route)=>route.canonicalPath),[jump.ROUTE,inverter.ROUTE,hub.ROUTE]);

const temp=fs.mkdtempSync(path.join(os.tmpdir(),'alo186-vehicle-v134-'));
const canonical=path.join(temp,'canonical');
execFileSync('python',[path.join(ROOT,'alo186','deployment','build_static_site.py'),'--output',canonical,'--commit','vehicle-v134-test'],{cwd:ROOT,stdio:'pipe'});
const sitemap=fs.readFileSync(path.join(canonical,'sitemap.xml'),'utf8');
for(const route of [jump.ROUTE,inverter.ROUTE,hub.ROUTE])assert.ok(sitemap.includes(route),route);
for(const file of [path.join(canonical,'hesaplama','aku-takviye-cihazi-jump-starter-uygunluk','index.html'),path.join(canonical,'hesaplama','arac-12v-priz-inverter-yuk-uygunluk','index.html'),path.join(canonical,'sektor-rehberi','arac-aku-ve-acil-enerji-test-merkezi','index.html')])assert.ok(fs.existsSync(file),file);
for(const basePath of ['','/chatgpt']){
  const target=path.join(temp,basePath?'project':'custom');fs.cpSync(canonical,target,{recursive:true});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','prepare_github_pages.py'),'--site',target,'--base-path',basePath,'--repository','ozaneryavuz/chatgpt','--commit','vehicle-v134-test'],{cwd:ROOT,stdio:'pipe'});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','smoke_github_pages.py'),'--site',target,'--base-path',basePath],{cwd:ROOT,stdio:'pipe'});
}
fs.rmSync(temp,{recursive:true,force:true});
console.log(JSON.stringify({ok:true,version:134,routes:[jump.ROUTE,inverter.ROUTE,hub.ROUTE],jumpStarterManualFirst:true,peakAmpNotSufficient:true,inverterDcCurrent:true,noBuy:true,sensitiveLoadsClosed:true,repeatVisitPlan:true,affiliateTransparent:true,personalData:false,customDomain:true,projectPath:true}));