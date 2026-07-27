const assert=require('assert');
const rules=require('../karar-motoru/rules.js');

assert.strictEqual(rules.categories.length,4,'Dört ana problem kategorisi bulunmalı.');
assert.strictEqual(rules.problems.length,25,'Karar motorunda tam 25 problem bulunmalı.');

const ids=rules.problems.map(p=>p.id);
assert.strictEqual(new Set(ids).size,ids.length,'Problem kimlikleri benzersiz olmalı.');

for(const category of rules.categories){
  const items=rules.listByCategory(category.id);
  assert(items.length>0,`${category.id} kategorisi boş olamaz.`);
}

for(const problem of rules.problems){
  assert(problem.label&&problem.note,`${problem.id} açıklama alanları eksik.`);
  assert(Array.isArray(problem.steps)&&problem.steps.length>0,`${problem.id} güvenli adım içermeli.`);
  assert(Array.isArray(problem.prep)&&problem.prep.length>0,`${problem.id} başvuru hazırlığı içermeli.`);
  const result=rules.resolve(problem.id,'unknown');
  assert(result.level&&result.title&&result.summary,`${problem.id} geçerli sonuç üretmeli.`);
  assert(Array.isArray(result.actions)&&result.actions.length>0,`${problem.id} aksiyon üretmeli.`);
}

const dangerous=['touch_voltage','pole_spark','fallen_conductor','damaged_pole','meter_burned'];
for(const id of dangerous){
  const result=rules.resolve(id,'unknown');
  assert.strictEqual(result.level,'danger',`${id} acil güvenlik rotasına gitmeli.`);
  assert.strictEqual(result.revenueAllowed,false,`${id} gelir CTA'sına izin vermemeli.`);
  assert(result.actions.some(a=>a.href==='tel:112'),`${id} 112 aksiyonu içermeli.`);
}

let result=rules.resolve('flicker','area');
assert.strictEqual(result.level,'official');
result=rules.resolve('flicker','unit');
assert.strictEqual(result.level,'electrician');
result=rules.resolve('flicker','building');
assert.strictEqual(result.level,'mixed');

result=rules.resolve('burning_smell','unknown');
assert.strictEqual(result.revenueAllowed,false,'Yanık kokusunda gelir CTA kapalı olmalı.');
assert(result.warningText,'Yanık kokusu güvenlik uyarısı içermeli.');

result=rules.resolve('subscription','unknown');
assert.strictEqual(result.eyebrow,'Bağlantı / abonelik işlemi');
assert(result.actions.some(a=>a.href.includes('edas-bul')),'Abonelik sonucu EDAŞ bulucuya bağlanmalı.');

assert.throws(()=>rules.resolve('olmayan-problem','unknown'),/Problem bulunamadı/);

console.log('25 sorun karar kuralı testleri başarılı.');
