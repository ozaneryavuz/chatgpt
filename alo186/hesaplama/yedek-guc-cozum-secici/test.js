const assert=require('assert');
const fs=require('fs');
const path=require('path');
const core=require('./core.js');

function run(name,input,expected){
  const result=core.analyze(input);
  assert.strictEqual(result.recommendation,expected,`${name}: ${result.recommendation}`);
  return result;
}
const common={phase:'single',portable:'no',fuel:'no',outdoor:'no',solar:'no',medical:false};
let result=run('mini ups',{...common,continuousW:20,peakW:25,hours:8,transition:'instant',scope:'dc-network'},'mini_ups');
assert.strictEqual(result.commercialAllowed,true);
result=run('ups',{...common,continuousW:300,peakW:500,hours:1,transition:'instant',scope:'plug'},'ups');
assert.strictEqual(result.commercialAllowed,false);
result=run('power station',{...common,continuousW:400,peakW:900,hours:4,transition:'brief',scope:'plug',portable:'yes'},'power_station');
assert.strictEqual(result.commercialAllowed,true);
result=run('generator',{...common,continuousW:1000,peakW:2200,hours:12,transition:'manual',scope:'motor',fuel:'yes',outdoor:'yes'},'generator');
assert.strictEqual(result.commercialAllowed,false);
result=run('fixed three phase',{...common,continuousW:1800,peakW:4000,hours:4,transition:'brief',scope:'fixed',phase:'three',fuel:'yes',outdoor:'yes'},'generator');
assert.strictEqual(result.professionalRequired,true);
result=run('medical',{...common,continuousW:200,peakW:300,hours:4,transition:'instant',scope:'plug',medical:true},'professional');
assert.strictEqual(result.commercialAllowed,false);
assert.strictEqual(core.calculateEnergyWh(100,2),273);
assert.throws(()=>core.analyze({...common,continuousW:500,peakW:400,hours:2,transition:'brief',scope:'plug'}),/Tepe yük/);

const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const app=fs.readFileSync(path.join(__dirname,'app.js'),'utf8');
assert(html.includes('Reklam / satış ortaklığı açıklaması'));
assert(html.includes('Kişisel veri yok'));
assert(html.includes('Ticari ürün yönlendirmesi kapatıldı'));
assert(html.includes('application/ld+json'));
assert(html.includes('https://www.cdc.gov/carbon-monoxide/about/index.html'));
assert(html.includes('id="restoreBtn"'));
assert(html.includes('en fazla 30 gün saklanır'));
assert(html.includes('Tıbbi cihaz seçimi yerel kayda alınmaz'));
assert(html.includes('Sıfırla ve yerel kaydı sil'));
assert(app.includes("const STORAGE_KEY='alo186_backup_selector_v2'"));
assert(app.includes('30*24*60*60*1000'));
assert(app.includes('localStorage.removeItem(STORAGE_KEY)'));
assert(app.includes('backup_solution_selector_restored'));
assert(app.includes('input:sanitizeTechnical(data)'));
assert(!app.includes('clean.medical='));
assert(!app.includes("allowed=['continuousW','peakW','hours','transition','scope','phase','portable','fuel','outdoor','solar','medical']"));
assert(!/amazon\.(com\.tr|com)\//i.test(html));
assert(!/type="(?:email|tel|text)"/i.test(html));
assert(!/name="(?:address|phone|email|subscription|tc|identity)"/i.test(html));
console.log('Yedek güç çözüm seçici testleri başarılı.');