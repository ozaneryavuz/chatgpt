const assert=require('assert');
const fs=require('fs');
const path=require('path');
const core=require('./journey-retention-core.js');

const categories=['powerbank','surge_strip','mini_ups','emergency_light','smoke_alarm','power_station','generator','inverter','outlet_tester'];
assert.strictEqual(core.schemaVersion,1);
assert.strictEqual(core.maxReviews,5);
assert.deepStrictEqual(core.allowedReviewDays,[7,30,90,180]);

for(const category of categories){
  const journey=core.getJourney(category);
  assert(journey,`Yol haritası eksik: ${category}`);
  assert(journey.label);
  for(const stage of ['learn','calculate','compare']){
    assert(journey[stage]&&journey[stage].url.startsWith('/'),`${category} ${stage} iç rota eksik`);
    assert(!journey[stage].url.includes('amazon.com.tr'),`${category} doğrudan Amazon rotası içermemeli`);
  }
  assert.strictEqual(journey.maintenance.length,3,`${category} üç bakım kontrolü taşımalı`);
  assert(journey.reviewReason.length>20,`${category} tekrar ziyaret nedeni eksik`);
}

assert.strictEqual(core.getJourney('unknown'),null);
assert.strictEqual(core.addDays('2026-07-28',7),'2026-08-04');
assert.strictEqual(core.dueBand('2026-07-27',new Date('2026-07-28T12:00:00Z')),'overdue');
assert.strictEqual(core.dueBand('2026-07-28',new Date('2026-07-28T12:00:00Z')),'today');
assert.strictEqual(core.dueBand('2026-08-02',new Date('2026-07-28T12:00:00Z')),'soon');
assert.strictEqual(core.dueBand('2026-09-01',new Date('2026-07-28T12:00:00Z')),'later');

const review=core.normalizeReview({category:'mini_ups',reviewDays:30,reason:'maintenance_due'},new Date('2026-07-28T12:00:00Z'));
assert.strictEqual(review.createdAt,'2026-07-28');
assert.strictEqual(review.reviewDate,'2026-08-27');
assert.strictEqual(review.reason,'maintenance_due');

let reviews=[];
for(const category of categories.slice(0,7)){
  reviews=core.upsertReview(reviews,{category,reviewDays:30},new Date('2026-07-28T12:00:00Z'));
}
assert.strictEqual(reviews.length,5,'Takvim en fazla beş kayıt tutmalı');
reviews=core.upsertReview(reviews,{category:reviews[0].category,reviewDays:90},new Date('2026-07-28T12:00:00Z'));
assert.strictEqual(reviews.length,5,'Aynı kategoride kayıt güncellenmeli');
assert(reviews.some(item=>item.reviewDays===90));
const removed=core.removeReview(reviews,reviews[0].id,new Date('2026-07-28T12:00:00Z'));
assert.strictEqual(removed.length,4);

const incomplete=core.maintenanceRecord('power_station',[true,false,true],new Date('2026-07-28T12:00:00Z'));
assert.strictEqual(incomplete.completed,false);
const complete=core.maintenanceRecord('power_station',[true,true,true],new Date('2026-07-28T12:00:00Z'));
assert.strictEqual(complete.completed,true);
const maintenance=core.sanitizeMaintenance({power_station:complete,unknown:{checks:[true]}});
assert(maintenance.power_station);
assert(!maintenance.unknown);

const event=core.sanitizeEvent({category:'mini_ups',stage:'learn',review_days:30,due_band:'soon',email:'x@example.com',freeText:'secret'});
assert.deepStrictEqual(event,{category:'mini_ups',stage:'learn',review_days:30,due_band:'soon'});
assert.strictEqual(core.hasForbiddenEventData({category:'mini_ups'}),false);
assert.strictEqual(core.hasForbiddenEventData({nested:{phone:'555'}}),true);

const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const css=fs.readFileSync(path.join(__dirname,'journey-retention.css'),'utf8');
const ui=fs.readFileSync(path.join(__dirname,'journey-retention.js'),'utf8');
const styles=fs.readFileSync(path.join(__dirname,'styles.css'),'utf8');
assert(html.includes('id="journeyRetention"'));
assert(html.includes('id="reviewVault"'));
assert(html.includes('İhtiyaç → öğrenme → hesap → mevcut ürün → güvenli karşılaştırma'));
assert(html.includes('Mevcut ürün yeterliyse satın alma yok'));
assert(html.includes('Eksik teknik veri linki durdurur'));
assert(html.includes('Ad, telefon, e-posta, adres, abonelik, seri numarası, fiyat veya satıcı kaydedilmez'));
assert(html.includes('./journey-retention-core.js'));
assert(html.includes('./journey-retention.js'));
assert(styles.includes('@import url("./journey-retention.css")'));
assert(css.includes('@media(max-width:680px)'));
assert(css.includes('min-height:48px'));
assert(ui.includes('ownership_maintenance_completed'));
assert(ui.includes('decision_review_saved'));
assert(ui.includes('product_journey_stage_opened'));
assert(!html.toLowerCase().includes('amazon.com.tr/dp/'));
assert(!html.match(/<input[^>]+(?:name|email|phone|address|text)/i));

console.log('ALO186 trust-first journey: 9 kategori, öğren-hesapla-karşılaştır rotası, mevcut ürün bakımı, 5 kayıtlı tekrar kontrol ve PII-safe analytics testlerini geçti.');
