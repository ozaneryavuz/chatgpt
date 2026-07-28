const assert=require('assert');
const fs=require('fs');
const path=require('path');
const core=require('./trust-growth-core.js');

const now=new Date('2026-07-28T09:00:00Z');

const adequatePowerbank=core.assessExistingProduct('powerbank',{minCapacityMah:20000,minOutputW:25,wireless:false},{owned:true,capacityMah:20000,maxOutputW:45,wireless:false});
assert.strictEqual(adequatePowerbank.status,'adequate');
assert.strictEqual(adequatePowerbank.purchaseNeeded,false);

const insufficientPowerbank=core.assessExistingProduct('powerbank',{minCapacityMah:20000,minOutputW:65,wireless:false},{owned:true,capacityMah:10000,maxOutputW:25,wireless:false});
assert.strictEqual(insufficientPowerbank.status,'insufficient');
assert.strictEqual(insufficientPowerbank.purchaseNeeded,true);
assert(insufficientPowerbank.reasons.some(item=>item.includes('karşılamıyor')));

const unknownPowerbank=core.assessExistingProduct('powerbank',{minCapacityMah:20000,minOutputW:25,wireless:true},{owned:true,capacityMah:null,maxOutputW:null,wireless:null});
assert.strictEqual(unknownPowerbank.status,'unknown');
assert.strictEqual(unknownPowerbank.purchaseNeeded,null);
assert(unknownPowerbank.missing.length>=2);

const adequateStrip=core.assessExistingProduct('surge_strip',{minOutlets:5,minJoules:900,usb:false},{owned:true,outlets:6,joules:1050,usb:false});
assert.strictEqual(adequateStrip.status,'adequate');

const inadequateStrip=core.assessExistingProduct('surge_strip',{minOutlets:6,minJoules:900,usb:true},{owned:true,outlets:5,joules:500,usb:false});
assert.strictEqual(inadequateStrip.status,'insufficient');

const noExisting=core.assessExistingProduct('powerbank',{minCapacityMah:20000,minOutputW:25},{owned:false});
assert.strictEqual(noExisting.status,'none');
assert.strictEqual(noExisting.purchaseNeeded,true);

assert.strictEqual(core.affiliateEligibility({existingStatus:'adequate',confidence:'Yüksek',unknowns:[],score:95,verifiedAt:'2026-07-27'},now).allowed,false);
assert.strictEqual(core.affiliateEligibility({existingStatus:'unknown',confidence:'Yüksek',unknowns:[],score:95,verifiedAt:'2026-07-27'},now).reason,'existing_equipment_unknown');
assert.strictEqual(core.affiliateEligibility({existingStatus:'none',confidence:'Orta',unknowns:[],score:90,verifiedAt:'2026-07-27'},now).reason,'confidence_below_high');
assert.strictEqual(core.affiliateEligibility({existingStatus:'insufficient',confidence:'Yüksek',unknowns:['Nominal akım bilinmiyor'],score:90,verifiedAt:'2026-07-27'},now).reason,'technical_data_incomplete');
assert.strictEqual(core.affiliateEligibility({existingStatus:'none',confidence:'Yüksek',unknowns:[],score:90,verifiedAt:'2026-05-01'},now).reason,'verification_stale');
assert.strictEqual(core.affiliateEligibility({existingStatus:'none',confidence:'Yüksek',unknowns:[],score:69,verifiedAt:'2026-07-27'},now).reason,'match_score_low');
assert.strictEqual(core.affiliateEligibility({existingStatus:'insufficient',confidence:'Yüksek',unknowns:[],score:90,verifiedAt:'2026-07-27'},now).allowed,true);

const noPurchaseQuality=core.decisionQuality({existingStatus:'adequate',matchCount:2,highConfidenceCount:2,staleCount:0});
assert.strictEqual(noPurchaseQuality.band,'satın_alma_gerekmiyor');
assert.strictEqual(noPurchaseQuality.score,100);

const lowConfidenceQuality=core.decisionQuality({existingStatus:'none',matchCount:2,highConfidenceCount:0,lowConfidenceCount:2,staleCount:0});
assert.strictEqual(lowConfidenceQuality.band,'eksik_teknik_veri');

const staleQuality=core.decisionQuality({existingStatus:'none',matchCount:0,highConfidenceCount:0,staleCount:2});
assert.strictEqual(staleQuality.band,'katalog_yenileme_bekleniyor');

const readyQuality=core.decisionQuality({existingStatus:'insufficient',matchCount:2,highConfidenceCount:2,staleCount:0});
assert.strictEqual(readyQuality.band,'yuksek_guvenli_karsilastirma');

const event=core.sanitizeEvent({category:'powerbank',status:'adequate',match_count:2,email:'x@example.com',requirements:{minOutputW:65},raw:'secret'});
assert.deepStrictEqual(event,{category:'powerbank',status:'adequate',match_count:2});
assert.strictEqual(core.hasForbiddenEventData(event),false);
assert.strictEqual(core.hasForbiddenEventData({phone:'555'}),true);
assert.strictEqual(core.ageDays('2026-07-27',now),1);

const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const ui=fs.readFileSync(path.join(__dirname,'trust-growth.js'),'utf8');
const gate=fs.readFileSync(path.join(__dirname,'decision-shortlist.js'),'utf8');
const css=fs.readFileSync(path.join(__dirname,'trust-growth.css'),'utf8');
const mainCss=fs.readFileSync(path.join(__dirname,'styles.css'),'utf8');

assert(html.includes('trust-growth-core.js'));
assert(html.includes('trust-growth.js'));
assert(html.includes('Mevcut ürün yeterliyse satın alma yok'));
assert(html.includes('Karar kalite skoru'));
assert(ui.includes('existingEquipmentCheck'));
assert(ui.includes('product_decision_quality_rendered'));
assert(ui.includes('product_requirement_gap_detected'));
assert(ui.includes('existing_equipment_assessed'));
assert(gate.includes('affiliate_confidence_blocked'));
assert(gate.includes('existing_need_confidence_technical_disclosure'));
assert(gate.includes('rel="sponsored nofollow noopener"'));
assert(css.includes('.decision-quality'));
assert(css.includes('.trust-confidence-note'));
assert(css.includes('@media(max-width:680px)'));
assert(mainCss.includes('@import url("./trust-growth.css")'));
for(const forbidden of ['name="name"','name="email"','name="phone"','name="address"','name="plate"','name="subscription"'])assert(!html.includes(forbidden),`PII alanı bulunmamalı: ${forbidden}`);
assert(!ui.toLowerCase().includes('amazon.com.tr'));

console.log('ALO186 güven odaklı büyüme: mevcut ürün yeterliliği, yüksek güven affiliate kapısı, karar kalite paneli ve PII-safe talep olayları testleri geçti.');
