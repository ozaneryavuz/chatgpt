(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186EvSharedParkingCore=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const MAX_SCORE=11;
  const LABELS={private:'Tahsisli bireysel',common:'Ortak kullanım',mixed:'Karma kullanım',public:'Halka açık/ücretli aday'};
  function assess(v){
    let score=0;
    score+=v.supply==='unknown'?0:1;
    score+=v.parking==='defined'?2:v.parking==='partial'?1:0;
    score+=v.load==='measured'?2:v.load==='bill'?1:0;
    score+=v.management==='dynamic'?2:v.management==='static'?1:0;
    score+=v.metering==='unknown'?0:2;
    score+=v.evidence==='ready'?2:v.evidence==='draft'?1:0;
    const agenda=['Kullanım modelini ve park alanı tahsisini yazılı karara bağlayın.','Besleme gideri, enerji ölçümü, ortak alan kullanımı ve işletme sorumluluğunu ayırın.','Arıza, acil durdurma, erişim, bakım ve hasar bildirim sorumluluklarını belirleyin.'];
    const technical=[];
    if(v.supply==='unknown')technical.push('Mevcut iç tesisat ile ayrı abonelik/bağlantı seçeneklerini tek hat ve kapasiteyle karşılaştırın.');
    if(v.parking!=='defined')technical.push('Park yeri, kablo güzergâhı, mekanik koruma, yangın/kaçış ve erişilebilirlik durumunu keşfedin.');
    if(v.load!=='measured')technical.push('Ana besleme, fazlar ve eşzamanlı yük için ölçüm yapın; yalnız wallbox etiket gücüyle karar vermeyin.');
    if(v.management==='none')technical.push('Araç sayısı ve şarj penceresine göre statik veya dinamik yük yönetimi senaryosu hazırlayın.');
    if(v.metering==='unknown')technical.push('Kullanıcı bazlı tüketim kaydı, gider paylaşımı ve varsa ayrı sayaç/abonelik modelini tanımlayın.');
    if(v.evidence!=='ready')technical.push('Tek hat, kablo/gerilim düşümü, RCD/RDC-DD, PEN/topraklama, kısa devre, devreye alma ve as-built teslimlerini şartnameye ekleyin.');
    if(v.use==='public')agenda.push('Halka açık/ücretli şarj hizmeti ihtimalinde lisanslı şarj ağı ve tüketici süreçlerini ayrıca doğrulayın.');
    if(!technical.length)technical.push('Gerçek araçlarla yük yönetimi, koruma, sayaç, uzaktan durdurma ve tekrar enerjilendirme kabul testini kayda alın.');
    let result={band:'early',className:'bad',label:'Ön karar eksik',title:'Önce park, besleme ve ölçüm modelini netleştirin.',summary:'Bu aşamada ürün teklifi almak kapsam farkı ve gereksiz kapasite riski oluşturabilir.'};
    if(score>=9)result={band:'ready',className:'good',label:'Teknik teklif aşamasına yakın',title:'Temel karar ve teknik girdiler büyük ölçüde tanımlı.',summary:'Marka ve fiyat istemeden önce kabul kriterlerini ve proje sorumluluklarını yazılı hale getirerek karşılaştırılabilir teklif alın.'};
    else if(score>=5)result={band:'prepare',className:'warn',label:'Keşif ve yönetim hazırlığı',title:'Kurulum fikri net; birkaç kritik karar ve kanıt eksik.',summary:'Eksikleri kapatmak, yanlış wallbox gücü ve belirsiz ortak gider modelinden korur.'};
    return {...result,inputs:v,score,maxScore:MAX_SCORE,model:LABELS[v.use],officialApproval:false,managementDecision:false,directAffiliateLinks:false,agenda,technical};
  }
  return {MAX_SCORE,LABELS,assess};
});
