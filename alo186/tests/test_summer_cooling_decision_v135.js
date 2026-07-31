'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {execFileSync}=require('node:child_process');

const ROOT=path.resolve(__dirname,'..','..');
const choiceDir=path.join(ROOT,'alo186','hesaplama','vantilator-hava-sogutucu-klima-karar');
const portableDir=path.join(ROOT,'alo186','hesaplama','portatif-klima-egzoz-pencere-priz-uygunluk');
const hubDir=path.join(ROOT,'alo186','sektor-rehberi','yaz-serinleme-elektrik-ve-tekrar-test-merkezi');
const choice=require(path.join(choiceDir,'app.js'));
const portable=require(path.join(portableDir,'app.js'));
const hub=require(path.join(hubDir,'app.js'));
const choiceHtml=fs.readFileSync(path.join(choiceDir,'index.html'),'utf8');
const portableHtml=fs.readFileSync(path.join(portableDir,'index.html'),'utf8');
const hubHtml=fs.readFileSync(path.join(hubDir,'index.html'),'utf8');
const overlay=JSON.parse(fs.readFileSync(path.join(ROOT,'alo186','deployment','routing-overlays','135-summer-cooling-decision.json'),'utf8'));

for(const file of [path.join(choiceDir,'app.js'),path.join(portableDir,'app.js'),path.join(hubDir,'app.js'),path.join(choiceDir,'test.js'),path.join(portableDir,'test.js')])execFileSync('node',['--check',file],{cwd:ROOT,stdio:'pipe'});
execFileSync('node',[path.join(choiceDir,'test.js')],{cwd:ROOT,stdio:'pipe'});
execFileSync('node',[path.join(portableDir,'test.js')],{cwd:ROOT,stdio:'pipe'});

const choiceBase={heatEmergency:false,unconscious:false,confusion:false,electricalDanger:false,activeOutage:false,vulnerablePerson:false,indoorTempC:31,humidityPct:45,outdoorAir:'good',strategy:'personal',crossVentilation:true,waterSafe:true,existingSolution:false,realComfortTest:false,noDamage:true,fanW:50,coolerW:100,portableAcW:1200,splitAcW:900,hoursPerDay:8,days:30,confirmNeed:false,confirmLabel:false,confirmAffiliate:false};
assert.equal(choice.decide({...choiceBase,heatEmergency:true}).code,'medical_emergency');
assert.equal(choice.decide({...choiceBase,indoorTempC:40}).code,'extreme_heat');
assert.equal(choice.decide({...choiceBase,strategy:'evaporative',humidityPct:70}).code,'evaporative_unsuitable');
assert.equal(choice.decide({...choiceBase,existingSolution:true,realComfortTest:true}).code,'no_buy');
assert.equal(choice.decide({...choiceBase,strategy:'whole_room'}).code,'ac_assessment');
const fanEligible=choice.decide({...choiceBase,confirmNeed:true,confirmLabel:true,confirmAffiliate:true});assert.equal(fanEligible.commerce,true);assert.equal(fanEligible.category,'fan');
const coolerEligible=choice.decide({...choiceBase,strategy:'evaporative',humidityPct:35,confirmNeed:true,confirmLabel:true,confirmAffiliate:true});assert.equal(coolerEligible.category,'evaporative_cooler');

const portableBase={heatEmergency:false,electricalDanger:false,activeOutage:false,useCase:'single_room',physicalCondition:'good',manualVerified:true,labelVerified:true,exhaustOutside:'yes',windowEgressRisk:false,hoseManufacturerCompatible:true,hoseExtended:false,windowSealVerified:true,connection:'direct_grounded',rcdVerified:true,voltage:230,inputW:1150,ratedA:5.5,outletMaxA:16,breakerA:16,condensateSafe:true,existingUnit:false,realCoolingTest:false,noHeat:true,hoursPerDay:8,days:30,confirmNeed:false,confirmManual:false,confirmAffiliate:false};
assert.equal(portable.decide({...portableBase,exhaustOutside:'no'}).code,'no_exhaust');
assert.equal(portable.decide({...portableBase,connection:'extension'}).code,'electrical_connection');
assert.equal(portable.decide({...portableBase,outletMaxA:5}).code,'overload');
assert.equal(portable.decide({...portableBase,existingUnit:true,realCoolingTest:true}).code,'no_buy');
const accessory=portable.decide({...portableBase,existingUnit:true,windowSealVerified:false,confirmNeed:true,confirmManual:true,confirmAffiliate:true});assert.equal(accessory.code,'eligible_accessory');assert.equal(accessory.commerce,true);
const portableEligible=portable.decide({...portableBase,confirmNeed:true,confirmManual:true,confirmAffiliate:true});assert.equal(portableEligible.code,'eligible_portable_ac');

const urgentPlan=hub.buildPlan({heatSymptoms:true,activeOutage:true,vulnerablePerson:true,unsureDevice:false,portableAC:false,newAC:false,roomChanged:false,backupNeed:false,highBill:false,existingFailure:false});assert.equal(urgentPlan.level,'P0');assert.equal(urgentPlan.repeatDays,7);assert.equal(urgentPlan.commerce,false);
const installPlan=hub.buildPlan({heatSymptoms:false,activeOutage:false,vulnerablePerson:false,unsureDevice:true,portableAC:true,newAC:true,roomChanged:false,backupNeed:false,highBill:true,existingFailure:false});assert.equal(installPlan.repeatDays,30);assert.ok(installPlan.tasks.length>=4);
const routine=hub.buildPlan({heatSymptoms:false,activeOutage:false,vulnerablePerson:false,unsureDevice:false,portableAC:false,newAC:false,roomChanged:false,backupNeed:false,highBill:false,existingFailure:false});assert.equal(routine.repeatDays,90);

for(const [name,html] of [['choice',choiceHtml],['portable',portableHtml],['hub',hubHtml]]){
  for(const token of ['rel="canonical"','FAQPage','BreadcrumbList','ALO186'])assert.ok(html.includes(token),`${name}:${token}`);
  assert.ok(html.toLocaleLowerCase('tr-TR').includes('bağımsız'),`${name}:independence`);
  assert.ok(html.toLocaleLowerCase('tr-TR').includes('kişisel veri'),`${name}:personal-data`);
  for(const forbidden of ['https://www.amazon','https://amazon','"@type":"Product"','"@type":"Offer"','priceCurrency','aggregateRating','availability'])assert.ok(!html.includes(forbidden),`${name}:${forbidden}`);
}
assert.ok(choiceHtml.includes('rel="sponsored nofollow noopener"'));
assert.ok(portableHtml.includes('rel="sponsored nofollow noopener"'));
assert.ok(!hubHtml.includes('rel="sponsored nofollow noopener"'));
assert.ok(hubHtml.includes(choice.ROUTE)&&hubHtml.includes(portable.ROUTE));
assert.ok(choiceHtml.includes('WHO')&&choiceHtml.includes('Department of Energy'));
assert.ok(portableHtml.includes('Portable Air Conditioners')&&portableHtml.includes('ENERGY STAR'));
assert.ok(hubHtml.includes('112')&&hubHtml.includes('7 gün')&&hubHtml.includes('30 gün')&&hubHtml.includes('90 gün'));
for(const js of [fs.readFileSync(path.join(choiceDir,'app.js'),'utf8'),fs.readFileSync(path.join(portableDir,'app.js'),'utf8'),fs.readFileSync(path.join(hubDir,'app.js'),'utf8')])for(const forbidden of ['fetch(','navigator.geolocation','localStorage','sessionStorage'])assert.ok(!js.includes(forbidden),forbidden);
assert.equal(overlay.version,135);
assert.deepEqual(overlay.routes.map((route)=>route.canonicalPath),[choice.ROUTE,portable.ROUTE,hub.ROUTE]);

const temp=fs.mkdtempSync(path.join(os.tmpdir(),'alo186-summer-cooling-v135-'));
const canonical=path.join(temp,'canonical');
execFileSync('python',[path.join(ROOT,'alo186','deployment','build_static_site.py'),'--output',canonical,'--commit','summer-cooling-v135-test'],{cwd:ROOT,stdio:'pipe'});
const sitemap=fs.readFileSync(path.join(canonical,'sitemap.xml'),'utf8');
for(const route of [choice.ROUTE,portable.ROUTE,hub.ROUTE])assert.ok(sitemap.includes(route),route);
for(const file of [path.join(canonical,'hesaplama','vantilator-hava-sogutucu-klima-karar','index.html'),path.join(canonical,'hesaplama','portatif-klima-egzoz-pencere-priz-uygunluk','index.html'),path.join(canonical,'sektor-rehberi','yaz-serinleme-elektrik-ve-tekrar-test-merkezi','index.html')])assert.ok(fs.existsSync(file),file);
for(const basePath of ['','/chatgpt']){
  const target=path.join(temp,basePath?'project':'custom');fs.cpSync(canonical,target,{recursive:true});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','prepare_github_pages.py'),'--site',target,'--base-path',basePath,'--repository','ozaneryavuz/chatgpt','--commit','summer-cooling-v135-test'],{cwd:ROOT,stdio:'pipe'});
  execFileSync('python',[path.join(ROOT,'alo186','deployment','smoke_github_pages.py'),'--site',target,'--base-path',basePath],{cwd:ROOT,stdio:'pipe'});
}
fs.rmSync(temp,{recursive:true,force:true});
console.log(JSON.stringify({ok:true,version:135,routes:[choice.ROUTE,portable.ROUTE,hub.ROUTE],healthFirst:true,fanCoolerAcSeparated:true,portableExhaustAndOutlet:true,noBuy:true,affiliateTransparent:true,repeatVisit:[7,30,90],personalData:false,customDomain:true,projectPath:true}));
