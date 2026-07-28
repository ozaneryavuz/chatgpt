'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const core=require('./core.js');
const now=new Date('2026-07-28T16:00:00.000Z');
const snapshot={
 outcomes:[
  {id:'o1',createdAt:'2026-07-26T12:00:00Z',dueAt:'2026-07-28T12:00:00Z',category:'backup_power',action:'free_tool',outcome:'unresolved',recurrence:'multiple',purchase:'not_applicable',followupRoute:'/hesaplama/yedek-guc-cozum-secici/'},
  {id:'o2',createdAt:'2026-07-20T12:00:00Z',dueAt:'2026-10-20T12:00:00Z',category:'product_selection',action:'existing_equipment',outcome:'resolved',recurrence:'none',purchase:'existing',followupRoute:'/hesaplama/ekipman-bakim-plani/'}
 ],
 pending:[{id:'p1',version:1,source:'calculator',category:'protection',action:'free_tool',originPath:'/hesaplama/parafudr-risk-testi/',recommendedPath:'/akilli-urun-secimi',createdAt:'2026-07-27T00:00:00Z',askAfter:'2026-07-27T12:00:00Z',expiresAt:'2026-09-01T00:00:00Z'}],
 reviews:[{id:'r1',category:'surge_strip',reviewDate:'2026-07-30',createdAt:'2026-07-01'}],
 maintenance:{surge_strip:{checks:[true,false,true]}},
 outageJournal:{entries:[{id:'e1',date:'2026-07-27',durationMinutes:800,deviceDamage:true}]},
 savedDecision:{category:'powerbank',reviewAt:'2026-07-29T00:00:00Z'}
};
const plan=core.buildPlan(snapshot,now);
assert.ok(plan.tasks.length>=6);
assert.equal(plan.tasks[0].priority,'critical');
assert.ok(plan.tasks.some(item=>item.id==='outage-damage'));
assert.ok(plan.tasks.some(item=>item.id==='outage-long'));
assert.ok(plan.tasks.some(item=>item.id==='pending-p1'));
assert.ok(plan.tasks.some(item=>item.id==='maintenance-surge_strip'));
assert.ok(plan.tasks.some(item=>item.id==='saved-decision'));
assert.equal(plan.metrics.unresolved,1);
assert.equal(plan.metrics.repeated,1);
assert.equal(plan.metrics.noPurchase,1);
assert.equal(plan.professionalPack.needed,true);
assert.equal(plan.professionalPack.category,'backup_power');
assert.match(plan.professionalPack.route,/kurumsal-elektrik-surekliligi-on-degerlendirme/);
assert.ok(plan.professionalPack.checklist.some(item=>/kritik yük/i.test(item)));
assert.ok(plan.metrics.health<100);
const payload=core.buildExport(plan);
assert.equal(payload.schema,'alo186-electrical-plan-v1');
assert.doesNotMatch(JSON.stringify(payload),/email|phone|address|subscriber|serial|price|seller/i);
const ics=core.buildCalendar(plan,'https://www.alo186.com');
assert.match(ics,/BEGIN:VCALENDAR/);
assert.match(ics,/ALO186 kişisel veri tutmaz/);
assert.doesNotMatch(ics,/ATTENDEE|ORGANIZER|LOCATION|EMAIL|TEL/i);
assert.equal(core.safePath('https://www.amazon.com.tr/dp/B0SECRET'),'/hesaplama/');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
assert.match(html,/https:\/\/www\.alo186\.com\/hesaplama\/elektrik-planim\//);
assert.match(html,/WebApplication/);
assert.match(html,/FAQPage/);
assert.match(html,/Kişisel veri yok/);
assert.match(html,/Ücretli profesyonel hizmete hazırlık/);
assert.doesNotMatch(html,/type="(?:email|tel|text)"|<textarea/i);
assert.doesNotMatch(html,/amazon\.(?:com|com\.tr)/i);
console.log('Elektrik Planım: birleştirme, öncelik, satın almama, profesyonel paket, JSON, ICS ve gizlilik testleri başarılı.');
