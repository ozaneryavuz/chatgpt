'use strict';
const fs=require('fs');const path=require('path');const assert=require('assert');
const ROOT=path.resolve(__dirname,'..');
const ROUTE=path.join(ROOT,'amazon-elektrik-urunleri','monitor-goruntu-kablosu-secimi');
const HTML=fs.readFileSync(path.join(ROUTE,'index.html'),'utf8');
const APP=fs.readFileSync(path.join(ROUTE,'app-v229.js'),'utf8');
const catalog=require(path.join(ROUTE,'catalog-v229.js'));
const EXPECTED=new Map([['B088GQM9CV','80392'],['B0CFF9T3PS','25911'],['B0C4DB8MLL','25158']]);
function walk(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);}
assert.strictEqual(catalog.version,229);assert.strictEqual(catalog.affiliateTag,'alo186rehber-21');
assert.strictEqual(catalog.verificationMaxAgeDays,45);assert.strictEqual(catalog.category.risk,'consumer-medium');
assert.strictEqual(catalog.category.affiliatePolicy,'after_tool');assert.strictEqual(catalog.category.professionalOnly,false);
assert.strictEqual(catalog.category.requiredTool,'embedded-display-cable-compatibility-v229');
assert.strictEqual(catalog.products.length,3);assert.strictEqual(new Set(catalog.products.map(p=>p.asin)).size,3);
for(const p of catalog.products){assert.strictEqual(EXPECTED.get(p.asin),p.mpn);for(const f of ['need','strengths','limits','nobuy','source','verifiedAt'])assert.ok(p[f]);assert.ok(p.strengths.length>=3);assert.ok(p.limits.length>=3);const u=catalog.amazonProductUrl(p.asin);assert.ok(u.includes('/dp/'+p.asin+'?'));assert.ok(u.includes('tag=alo186rehber-21'));}
assert.strictEqual(catalog.verificationStatus(new Date('2026-09-17T12:00:00Z')).fresh,true);
assert.strictEqual(catalog.verificationStatus(new Date('2026-09-18T12:00:00Z')).fresh,false);
const canonical='https://alo186.com/amazon-elektrik-urunleri/monitor-goruntu-kablosu-secimi/';
assert.strictEqual((HTML.match(new RegExp('<link rel="canonical" href="'+canonical+'">','g'))||[]).length,1);
for(const s of ['data-commercial-scope="after-tool"','data-risk="consumer-medium"','Reklam / satış ortaklığı açıklaması','Satın almama koşulu','rel="sponsored nofollow noopener"'])assert.ok(HTML.includes(s),s);
assert.ok(!/href="https:\/\/www\.amazon\.com\.tr\/(?:dp|s\?k=)/i.test(HTML));
for(const s of ["affiliatePolicy === 'after_tool'","professionalOnly === false",'verificationStatus(new Date())',"link.removeAttribute('href')"])assert.ok(APP.includes(s),s);
const matches=[...HTML.matchAll(/<script type="application\/ld\+json">\s*(.*?)\s*<\/script>/gs)];assert.strictEqual(matches.length,1);
const nodes=JSON.parse(matches[0][1])['@graph'];const ps=nodes.filter(n=>n['@type']==='Product');const lists=nodes.filter(n=>n['@type']==='ItemList');
assert.strictEqual(ps.length,3);assert.strictEqual(lists.length,1);assert.strictEqual(lists[0].numberOfItems,3);
for(const p of ps){assert.strictEqual(p.brand['@type'],'Brand');assert.ok(p.identifier.length>=2);assert.ok(p.additionalProperty.length>=3);assert.ok(!('offers'in p));}
const serialized=JSON.stringify(nodes);for(const f of ['"Offer"','aggregateRating','priceCurrency','availability','seller','review','warranty'])assert.ok(!serialized.includes(f),f);
const duplicate=[];for(const file of walk(ROOT)){if(!['.html','.js','.json'].includes(path.extname(file)))continue;if(file.startsWith(path.join(ROOT,'tests'))||file.startsWith(ROUTE))continue;const txt=fs.readFileSync(file,'utf8');for(const asin of EXPECTED.keys())if(txt.includes(asin))duplicate.push(asin+':'+path.relative(ROOT,file));}
assert.deepStrictEqual(duplicate,[]);
console.log(JSON.stringify({ok:true,route:'/amazon-elektrik-urunleri/monitor-goruntu-kablosu-secimi/',products:[...EXPECTED.keys()],knowledgeGraph:['Product','Brand','ItemList','identifier','additionalProperty'],affiliatePolicy:'after_tool',professionalOnlyBypass:false,staleBoundary:'45-open-46-closed',duplicateAsin:false}));
