const assert=require('assert');
const companies=require('../turkiye-arama/companies.js');
const search=require('../turkiye-arama/search-core.js');

assert.strictEqual(companies.normalize('Muğla / Marmaris'),'mugla marmaris');
assert.strictEqual(companies.normalize('ÇEDAŞ'),'cedas');

const covered=new Set(companies.companies.flatMap(c=>c.provinceIds));
for(let id=1;id<=81;id++)assert(covered.has(id),`İl kapsamı eksik: ${id}`);

assert.strictEqual(companies.companyForProvince(48).id,'adm');
assert.strictEqual(companies.companyForProvince(35).id,'gdz');
assert.strictEqual(companies.companyForProvince(34,'Ümraniye').id,'ayedas');
assert.strictEqual(companies.companyForProvince(34,'Esenyurt').id,'bedas');
assert.strictEqual(companies.companyForProvince(34,'Bilinmeyen'),null);

const provinces=[{id:48,name:'Muğla'},{id:34,name:'İstanbul'},{id:16,name:'Bursa'}];
const districts=[
  {id:1,name:'Marmaris',provinceId:48},
  {id:2,name:'Ümraniye',provinceId:34},
  {id:3,name:'Esenyurt',provinceId:34},
  {id:4,name:'Nilüfer',provinceId:16}
];
const index=search.buildIndex(provinces,districts);

let result=search.search('marmaris',index,5);
assert.strictEqual(result[0].type,'district');
assert.strictEqual(result[0].company.id,'adm');

result=search.search('mugla',index,5);
assert(result.some(r=>r.type==='province'&&r.provinceId===48));

result=search.search('aydem dagitim',index,5);
assert.strictEqual(result[0].type,'company');
assert.strictEqual(result[0].company.id,'adm');

result=search.search('kablo yere düştü',index,5);
assert.strictEqual(result[0].id,'emergency');

result=search.search('umraniye',index,5);
assert.strictEqual(result[0].company.id,'ayedas');

result=search.search('esenyurt',index,5);
assert.strictEqual(result[0].company.id,'bedas');

assert(search.similarity('marmaris','marmars')>.8);
console.log('Türkiye EDAŞ arama testleri başarılı.');
