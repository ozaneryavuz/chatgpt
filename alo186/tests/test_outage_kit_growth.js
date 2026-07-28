'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const repoRoot=path.resolve(__dirname,'../..');
const read=relative=>fs.readFileSync(path.join(repoRoot,relative),'utf8');
const planCore=require('../hesaplama/elektrik-planim/core.js');

const kitHtml=read('alo186/hesaplama/elektrik-kesintisi-kiti/index.html');
const kitApp=read('alo186/hesaplama/elektrik-kesintisi-kiti/app.js');
const pwa=read('alo186/hesaplama/pwa-install.js');
const planHtml=read('alo186/hesaplama/elektrik-planim/index.html');
const planApp=read('alo186/hesaplama/elektrik-planim/app.js');
const planGrowth=read('alo186/hesaplama/elektrik-planim/growth.js');
const injector=read('alo186/deployment/inject_outcome_runtime.py');

assert.match(kitHtml,/https:\/\/www\.alo186\.com\/hesaplama\/elektrik-kesintisi-kiti\//);
assert.match(kitHtml,/Envanter önce · eksik sonra · satış en son/);
assert.match(kitHtml,/Reklam \/ satış ortaklığı açıklaması/);
assert.match(kitHtml,/id="installBtn"/);
assert.match(kitHtml,/pwa-install\.js/);
assert.doesNotMatch(kitHtml,/type="(?:email|tel|text)"|<textarea/i);
assert.doesNotMatch(kitHtml,/amazon\.(?:com|com\.tr)\//i);

assert.match(kitApp,/data-tool-confirm/);
assert.match(kitApp,/Teknik aracı tamamladım/);
assert.match(kitApp,/affiliate-link/);
assert.match(kitApp,/warmOffline/);
assert.match(kitApp,/alo186-emergency-/);
assert.doesNotMatch(kitApp,/amazon\.(?:com|com\.tr)\/dp\//i);

assert.match(pwa,/beforeinstallprompt/);
assert.match(pwa,/appinstalled/);
assert.match(pwa,/Ana Ekrana Ekle/);
assert.doesNotMatch(pwa,/Notification\.requestPermission|geolocation|getUserMedia|\b(?:email|phone|address)\b/i);

assert.match(planHtml,/\/hesaplama\/elektrik-kesintisi-kiti\//);
assert.match(planHtml,/id="installBtnPlan"/);
assert.match(planHtml,/Offline ana ekran dönüşü/);
assert.match(planApp,/outageKit:'alo186:outage-kit:v1'/);
assert.match(planApp,/Kesinti kiti envanteri/);
assert.match(planGrowth,/Alo186PwaInstall\.bind/);

const now=new Date('2026-07-28T12:00:00.000Z');
const kitRecord={version:1,createdAt:'2026-07-28T12:00:00.000Z',reviewAt:'2026-10-26T12:00:00.000Z',profile:'home',status:'gaps',score:55,metrics:{required:4,covered:2,verify:1,missing:1,professional:0,noBuy:2},missingCategories:['mini_ups'],verifyCategories:['emergency_light'],professionalCategories:[]};
const plan=planCore.buildPlan({outageKit:kitRecord},now);
assert.equal(plan.sourceCounts.outageKit,1);
assert.equal(plan.metrics.noPurchase,2);
assert.ok(plan.tasks.some(item=>item.id==='outage-kit-missing'));
assert.match(plan.tasks.find(item=>item.id==='outage-kit-missing').route,/elektrik-kesintisi-kiti/);

const professionalPlan=planCore.buildPlan({outageKit:{...kitRecord,status:'professional',metrics:{...kitRecord.metrics,professional:1,missing:0},missingCategories:[],verifyCategories:[],professionalCategories:['power_station']}},now);
assert.ok(professionalPlan.tasks.some(item=>item.id==='outage-kit-professional'));
assert.equal(professionalPlan.professionalPack.needed,true);

assert.match(injector,/KIT_CANONICAL/);
assert.match(injector,/KIT_HUB_MARKER/);
assert.match(injector,/offlineOutageKitRoute/);
assert.match(injector,/pwaInstallHelper/);
assert.match(injector,/manifest\.setdefault\("shortcuts"/);
assert.match(injector,/Elektrik Kesintisi Kiti/);

console.log('ALO186 kesinti kiti büyümesi: envanter, satın almama, affiliate kapısı, Elektrik Planım ve PWA entegrasyonu başarılı.');
