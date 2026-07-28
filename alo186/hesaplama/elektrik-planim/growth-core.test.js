'use strict';
const assert=require('node:assert/strict');
const core=require('./growth-core.js');

assert.equal(core.seasonKey(new Date('2026-07-28T12:00:00Z')),'summer');
assert.equal(core.seasonKey(new Date('2026-01-15T12:00:00Z')),'winter');
assert.equal(core.seasonKey(new Date('2026-10-01T12:00:00Z')),'storm');
assert.equal(core.seasonKey(new Date('2026-04-01T12:00:00Z')),'spring');

const summer=core.seasonalActions(new Date('2026-07-28T12:00:00Z'));
assert.equal(summer.actions.length,3);
assert.ok(summer.actions.some(item=>item.category==='ev_cable'));
assert.ok(summer.actions.every(item=>!item.route.includes('amazon')));

const ready=core.procurementBrief({savedDecision:{category:'power_station',reviewAt:'2026-08-28T00:00:00Z'},outcomes:[]},new Date('2026-07-28T12:00:00Z'));
assert.equal(ready.status,'ready');
assert.equal(ready.affiliateAllowed,true);
assert.equal(ready.requirements.length,4);
assert.match(ready.route,/akilli-urun-secimi/);

const noBuy=core.procurementBrief({savedDecision:{category:'powerbank'},outcomes:[{createdAt:'2026-07-27T00:00:00Z',category:'product_selection',outcome:'resolved',purchase:'existing',action:'existing_equipment',recurrence:'none'}]},new Date('2026-07-28T12:00:00Z'));
assert.equal(noBuy.status,'no_buy');
assert.equal(noBuy.affiliateAllowed,false);
assert.match(noBuy.disclosure,/ticari ürün yönlendirmesi açmaz/);

const professional=core.procurementBrief({savedDecision:{category:'generator'},outcomes:[]},new Date('2026-07-28T12:00:00Z'));
assert.equal(professional.status,'professional');
assert.equal(professional.affiliateAllowed,false);
assert.match(professional.route,/kurumsal-elektrik-surekliligi-on-degerlendirme/);

const repeated=core.procurementBrief({savedDecision:{category:'ev_cable'},outcomes:[{createdAt:'2026-07-27T00:00:00Z',category:'ev_charging',outcome:'unresolved',purchase:'not_applicable',action:'free_tool',recurrence:'multiple'}]},new Date('2026-07-28T12:00:00Z'));
assert.equal(repeated.status,'professional');

const payload=core.sharePayload({tasks:[{title:'Kesinti günlüğünü tamamla'},{title:'UPS runtime testini yap'}]},summer,ready);
assert.match(payload.text,/Kesinti günlüğünü tamamla/);
assert.match(payload.text,/Mevsimsel hazırlık/);
assert.equal(payload.url,'https://www.alo186.com/hesaplama/elektrik-planim/');
assert.doesNotMatch(JSON.stringify(payload),/email|phone|address|subscriber|serial|price|seller|asin/i);

const review=core.reviewRecord(summer.actions[0],30,new Date('2026-07-28T12:00:00Z'));
assert.equal(review.reviewAt,'2026-08-27T12:00:00.000Z');
assert.equal(core.sanitizeReviews([review],new Date('2026-07-28T12:00:00Z')).length,1);
assert.equal(core.sanitizeReviews([{...review,createdAt:'2025-01-01T00:00:00Z'}],new Date('2026-07-28T12:00:00Z')).length,0);

console.log('Elektrik Planım büyüme çekirdeği: mevsimsel hazırlık, satın almama, profesyonel sınır, paylaşım ve tekrar ziyaret testleri başarılı.');
