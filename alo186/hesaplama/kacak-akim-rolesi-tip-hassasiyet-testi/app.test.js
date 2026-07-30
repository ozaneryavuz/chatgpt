'use strict';
const assert=require('node:assert/strict');
const rcd=require('./app.js');

const base={hazard:'none',application:'electronic',supply:'single',manufacturer:'unknown',existingType:'A',residual:'30',deviceForm:'rcbo_dedicated',tripPattern:'none',testButton:'works',circuits:'one',recentWork:'no',ratingCoordination:'verified'};

const general=rcd.buildDecision(base);
assert.equal(general.requiredType,'A_REVIEW');
assert.equal(general.state.key,'review');
assert.equal(general.directAffiliateLinks,false);
assert.equal(general.commercialCtasAllowed,true);
assert.equal(general.noBuyOutcomePreserved,true);
assert(general.selection.some(item=>item.includes('30 mA')));
assert.equal(general.evidenceScore,90);

const acMismatch=rcd.buildDecision({...base,existingType:'AC'});
assert.equal(acMismatch.typeMismatch,true);
assert.equal(acMismatch.state.key,'measure');
assert(acMismatch.selection.some(item=>item.includes('algılama kapsamının altında')));

const singleInverter=rcd.buildDecision({...base,application:'single_inverter',existingType:'A'});
assert.equal(singleInverter.requiredType,'F_REVIEW');
assert.equal(singleInverter.typeMismatch,true);
assert(singleInverter.selection.some(item=>item.includes('her inverterli cihaz otomatik olarak Tip B gerektirmez')));

const drive=rcd.buildDecision({...base,application:'three_drive',supply:'three',existingType:'F'});
assert.equal(drive.requiredType,'B_REVIEW');
assert.equal(drive.typeMismatch,true);
assert(drive.tests.some(item=>item.includes('DC ara devre')));

const evWithoutRdc=rcd.buildDecision({...base,application:'ev_mode3',manufacturer:'unknown',existingType:'A'});
assert.equal(evWithoutRdc.requiredType,'A_F_RDC_OR_B');
assert.equal(evWithoutRdc.typeMismatch,true);
assert.equal(evWithoutRdc.state.key,'measure');
assert(evWithoutRdc.selection.some(item=>item.includes('6 mA RDC-DD')));
assert(evWithoutRdc.tests.some(item=>item.includes('6 mA DC')));

const evTypeB=rcd.buildDecision({...base,application:'ev_mode3',manufacturer:'unknown',existingType:'B'});
assert.equal(evTypeB.typeMismatch,false);
assert.notEqual(evTypeB.state.key,'measure');

const evWithRdc=rcd.buildDecision({...base,application:'ev_mode3',manufacturer:'A_F_RDC',existingType:'A'});
assert.equal(evWithRdc.requiredType,'A_F_RDC');
assert.equal(evWithRdc.typeMismatch,false);
assert(evWithRdc.selection.some(item=>item.includes('kombinasyonu aynen doğrulanmalıdır')));

const manufacturerOverride=rcd.buildDecision({...base,application:'general',manufacturer:'B',existingType:'B'});
assert.equal(manufacturerOverride.requiredType,'B');
assert(manufacturerOverride.selection.some(item=>item.includes('üretici talimatı Tip B')));

const highSensitivity=rcd.buildDecision({...base,residual:'300'});
assert.equal(highSensitivity.state.key,'measure');
assert(highSensitivity.selection.some(item=>item.includes('30 mA ek korumanın yerine otomatik olarak geçmez')));

const nuisance=rcd.buildDecision({...base,deviceForm:'rccb_shared',circuits:'multiple',tripPattern:'random'});
assert(nuisance.causes.some(item=>item.includes('toplam koruyucu iletken akımı')));
assert(nuisance.architecture.some(item=>item.includes('Devre bazlı RCBO')));

const failed=rcd.buildDecision({...base,testButton:'fails'});
assert.equal(failed.state.key,'urgent');
assert(failed.causes.some(item=>item.includes('Test düğmesinin açtırmaması')));

const emergency=rcd.buildDecision({...base,hazard:'smoke'});
assert.equal(emergency.state.key,'emergency');
assert.equal(emergency.commercialCtasAllowed,false);
assert(emergency.summary.includes('ticari yönlendirme kapatıldı'));
assert(emergency.selection.some(item=>item.includes('Ürün veya tip seçimi durduruldu')));

const complete=rcd.buildDecision({...base,manufacturer:'A'});
assert.equal(complete.evidenceScore,100);
assert.equal(complete.typeMismatch,false);

const invalid=rcd.normalize({hazard:'bad',application:'bad',residual:'999'});
assert.equal(invalid.hazard,'none');
assert.equal(invalid.application,'unknown');
assert.equal(invalid.residual,'unknown');

console.log(JSON.stringify({ok:true,module:'RCD type and sensitivity decision',scenarios:14,directAffiliateLinks:false,emergencyCommercialCtas:false,noBuyOutcomePreserved:true},null,2));
