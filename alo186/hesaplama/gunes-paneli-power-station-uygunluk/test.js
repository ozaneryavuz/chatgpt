'use strict';
const assert=require('assert');
const fs=require('fs');
const path=require('path');
const core=require('./core.js');
const base={panelPower:200,panelVoc:24.3,panelVmp:20.5,panelIsc:10.3,panelImp:9.8,vocTempCoeff:.28,seriesCount:1,parallelCount:1,minTemp:0,mpptMinV:11,mpptMaxV:60,absoluteMaxVoc:60,maxInputCurrent:15,maxShortCircuitCurrent:'',maxInputPower:500,stationCapacity:768,currentSoc:20,targetSoc:80,derating:.8,application:'portable',manualVerified:true,connectorKnown:true,factoryCable:true};
{
  const r=core.analyze(base);
  assert.equal(r.status,'compatible');
  assert.equal(r.panelCount,1);
  assert(r.coldVoc>24.3&&r.coldVoc<27);
  assert.equal(r.commercialAllowed,true);
  assert.equal(r.professionalRequired,false);
  assert(r.idealHours>2&&r.idealHours<4);
}
{
  const r=core.analyze({...base,seriesCount:4,panelPower:400,panelVoc:37.2,panelVmp:31.2,panelIsc:13.8,panelImp:12.9,minTemp:-10,mpptMinV:30,mpptMaxV:150,absoluteMaxVoc:150,maxInputPower:1600,application:'fixed',connectorKnown:false,factoryCable:false});
  assert.equal(r.status,'incompatible');
  assert(r.blockers.some(x=>x.includes('mutlak sınır')));
  assert.equal(r.commercialAllowed,false);
  assert.equal(r.professionalRequired,true);
}
{
  const r=core.analyze({...base,parallelCount:2,maxInputCurrent:15});
  assert.equal(r.status,'conditional');
  assert(r.warnings.some(x=>x.includes('Toplam Imp')));
  assert.equal(r.commercialAllowed,false);
}
{
  const r=core.analyze({...base,seriesCount:2,panelVmp:18,mpptMinV:40});
  assert.equal(r.status,'incompatible');
  assert(r.blockers.some(x=>x.includes('MPPT alt sınırı')));
}
{
  const r=core.analyze({...base,maxShortCircuitCurrent:9});
  assert.equal(r.status,'incompatible');
  assert(r.blockers.some(x=>x.includes('kısa devre akımı')));
}
{
  const r=core.analyze({...base,maxInputPower:100});
  assert.equal(r.status,'conditional');
  assert(r.estimatedAcceptedPower<=100);
  assert.equal(r.commercialAllowed,false);
}
{
  const r=core.analyze({...base,stationCapacity:'',currentSoc:'',targetSoc:''});
  assert.equal(r.energyNeed,null);
  assert.equal(r.idealHours,null);
}
assert.throws(()=>core.analyze({...base,panelVmp:25}),/Vmp değeri Voc/);
assert.throws(()=>core.analyze({...base,targetSoc:10}),/Hedef doluluk/);
assert.throws(()=>core.analyze({...base,stationCapacity:'',currentSoc:20,targetSoc:80}),/birlikte girilmelidir/);
assert.throws(()=>core.analyze({...base,stationCapacity:768,currentSoc:'',targetSoc:''}),/birlikte girilmelidir/);
assert.throws(()=>core.analyze({...base,stationCapacity:768,currentSoc:20,targetSoc:''}),/birlikte girilmelidir/);

const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
assert(html.includes('rel="canonical" href="https://www.alo186.com/hesaplama/gunes-paneli-power-station-uygunluk/"'));
assert(html.includes('Reklam / satış ortaklığı açıklaması'));
assert(html.includes('Kişisel veri yok'));
assert(html.includes('Elektriksel ön kontroldür; kurulum onayı değildir'));
assert(html.includes('https://www.victronenergy.com/'));
assert(html.includes('https://manuals.ecoflow.com/'));
assert(!/amazon\.(com\.tr|com)\//i.test(html));
assert(!/type="(?:email|tel|text)"|name="(?:address|phone|email|subscription|tc|identity|note)"/i.test(html));
const schemaBlocks=[...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
assert(schemaBlocks.length>0);schemaBlocks.forEach(match=>JSON.parse(match[1]));
console.log('Güneş paneli / power station uygunluk testleri başarılı.');
