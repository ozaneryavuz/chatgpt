const assert=require('assert');
const fs=require('fs');
const path=require('path');
const core=require('./core.js');
function run(name,input,expected){const result=core.analyze(input);assert.strictEqual(result.recommendation,expected,`${name}: ${result.recommendation}`);return result;}
const common={duration:'minutes',scope:'whole_home',measurement:'none',loadType:'electronics',powerBand:'under1000',phase:'single',continuity:'none',existing:'none',emergency:false,medical:false};
let result=run('emergency',{...common,symptom:'flicker',emergency:true},'emergency');assert.strictEqual(result.commercialAllowed,false);assert.strictEqual(result.riskLevel,'Kritik');
result=run('medical',{...common,symptom:'outage_restart',medical:true},'medical_plan');assert.strictEqual(result.commercialAllowed,false);
result=run('mixed neutral',{...common,symptom:'mixed',measurement:'fluctuating'},'neutral_risk');assert.strictEqual(result.professionalRequired,true);
result=run('neighbor utility',{...common,symptom:'dim',scope:'neighbors',measurement:'low'},'utility_report');assert.strictEqual(result.distributionReport,true);
result=run('single room',{...common,symptom:'flicker',scope:'one_room'},'installation_check');assert.strictEqual(result.commercialAllowed,false);
result=run('safe transient',{...common,symptom:'surge',duration:'instant',scope:'one_device'},'spd_layers');assert.strictEqual(result.commercialAllowed,true);assert.strictEqual(result.productCategory,'surge_strip');
result=run('transient existing strip',{...common,symptom:'surge',duration:'instant',scope:'one_device',existing:'surge_strip'},'spd_layers');assert.strictEqual(result.commercialAllowed,false);
result=run('ups avr',{...common,symptom:'outage_restart',scope:'one_device',continuity:'must_stay_on'},'ups_avr');assert.strictEqual(result.commercialAllowed,false);
result=run('safe regulator',{...common,symptom:'dim',scope:'one_device',measurement:'low'},'voltage_regulator');assert.strictEqual(result.commercialAllowed,false);
result=run('motor voltage',{...common,symptom:'dim',scope:'one_device',measurement:'low',loadType:'motor'},'voltage_monitoring');assert.strictEqual(result.professionalRequired,true);
result=run('single device normal',{...common,symptom:'single_device',scope:'one_device',measurement:'normal'},'device_service');assert.strictEqual(result.commercialAllowed,false);
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');const app=fs.readFileSync(path.join(__dirname,'app.js'),'utf8');const styles=fs.readFileSync(path.join(__dirname,'styles.css'),'utf8');
assert(html.includes('Belirtiye dayalı ön değerlendirmedir'));assert(html.includes('Reklam / satış ortaklığı açıklaması'));assert(html.includes('Ticari ürün yönlendirmesi kapatıldı'));assert(html.includes('Kişisel veri yok'));assert(html.includes('application/ld+json'));assert(html.includes('https://www.se.com/us/en/faqs/FA158913/'));assert(html.includes('https://electrification.us.abb.com/products/controls-relays/cm-exx-cm-sxx-single-phase-monitoring-relays'));assert(html.includes('https://www.epdk.gov.tr/detay/icerik/18/tuketici-kosesi'));assert(app.includes('voltage_protection_selector_completed'));assert(app.includes('kategori=${encodeURIComponent(result.productCategory)}'));assert(styles.includes('@media(max-width:640px)'));assert(!/amazon\.(com\.tr|com)\//i.test(html));assert(!/type="(?:email|tel|text)"/i.test(html));assert(!/name="(?:address|phone|email|subscription|tc|identity|note)"/i.test(html));console.log('Gerilim koruma çözüm seçici testleri başarılı.');
