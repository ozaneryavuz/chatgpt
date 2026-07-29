(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186RuntimeHealthCore=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const TTL_MS=540*86400000;
  const MAX_RECORDS=12;
  const SIGNIFICANT_DROP=-0.35;
  const TREND_DROP=-0.20;

  function validDate(value){return Number.isFinite(Date.parse(String(value||'')));}
  function iso(value,fallback){return validDate(value)?new Date(value).toISOString():fallback;}
  function compareOrder(a,b){
    const dateCompare=String(a?.date||'').localeCompare(String(b?.date||''));
    if(dateCompare!==0)return dateCompare;
    return String(a?.createdAt||a?.id||'').localeCompare(String(b?.createdAt||b?.id||''));
  }
  function sortEntries(entries){return [...(Array.isArray(entries)?entries:[])].sort(compareOrder);}
  function normalizeEntry(item,fallbackExpiry,now=Date.now()){
    if(!item||typeof item!=='object'||!item.id||!item.date||!(Number(item.minutes)>0))return null;
    const createdFallback=validDate(item.date)?new Date(`${item.date}T12:00:00.000Z`).toISOString():new Date(now).toISOString();
    const createdAt=iso(item.createdAt,createdFallback);
    const derivedExpiry=new Date(Date.parse(createdAt)+TTL_MS).toISOString();
    const expiresAt=iso(item.expiresAt,iso(fallbackExpiry,derivedExpiry));
    return {
      id:String(item.id),date:String(item.date),system:String(item.system),load:String(item.load),
      charge:String(item.charge),minutes:Number(item.minutes),outcome:String(item.outcome||'normal'),
      hazard:Boolean(item.hazard),createdAt,expiresAt
    };
  }
  function pruneEntries(entries,now=Date.now()){
    return sortEntries(entries)
      .filter(item=>validDate(item.expiresAt)&&Date.parse(item.expiresAt)>now)
      .slice(-MAX_RECORDS);
  }
  function createEntry(input,now=Date.now()){
    const createdAt=new Date(now).toISOString();
    return normalizeEntry({
      ...input,
      id:String(input.id||`r${now}`),
      createdAt,
      expiresAt:new Date(now+TTL_MS).toISOString()
    },null,now);
  }
  function serialize(entries,now=Date.now()){
    const active=pruneEntries(entries,now);
    return {
      schema:'alo186.backupRuntimeJournal.v1',version:2,personalData:false,
      retentionMode:'per-record',ttlDays:540,updatedAt:new Date(now).toISOString(),items:active
    };
  }
  function priorComparable(entries,focus){
    return sortEntries(entries).filter(item=>
      item.id!==focus.id&&compareOrder(item,focus)<0&&item.system===focus.system&&
      item.load===focus.load&&item.charge==='full'&&!item.hazard
    );
  }
  function assess(entries,focus){
    const sorted=sortEntries(entries);
    const latest=focus||sorted.at(-1)||null;
    if(!latest)return {state:'empty',showCommercial:false,steps:[],latest:null};
    const safe=!latest.hazard;
    const prior=priorComparable(sorted,latest);
    const baseline=prior.at(-1)||null;
    const reference=prior.at(-2)||null;
    const change=baseline&&baseline.minutes>0?(latest.minutes-baseline.minutes)/baseline.minutes:null;
    const previousDrop=reference&&reference.minutes>0?(baseline.minutes-reference.minutes)/reference.minutes:null;
    const currentVsReference=reference&&reference.minutes>0?(latest.minutes-reference.minutes)/reference.minutes:null;
    const repeatedSignificantDrop=Boolean(
      safe&&latest.charge==='full'&&latest.load!=='high'&&reference&&baseline&&
      previousDrop!==null&&previousDrop<=SIGNIFICANT_DROP&&
      currentVsReference!==null&&currentVsReference<=SIGNIFICANT_DROP
    );

    let result={
      state:'stable',className:'good',label:'Mevcut ürünle devam',
      title:'Güvenlik belirtisi yok; runtime kaydını izlemeyi sürdürün.',
      summary:'Mevcut süre hedefinizi karşılıyorsa yeni ürün satın almayın.',
      steps:['Aynı yük ve tam şarjla 90 gün sonra yeniden test edin.','Çıkış gerilimi, kablo/adaptör ve cihaz yükünü değiştirmeden karşılaştırın.'],
      showCommercial:false
    };
    if(!safe){
      result={state:'hazard',className:'bad',label:'Kullanımı ve şarjı durdur',title:'Fiziksel veya termal güvenlik belirtisi kaydedildi.',summary:'Testi sürdürmeyin, cihazı açmayın ve güvenli üretici/uzman sürecini izleyin.',steps:['Cihazı yanıcı malzemelerden uzak, güvenli koşulda enerjisiz bırakın.','Duman veya yangın riski varsa güvenli alana geçip 112’yi arayın.','Affiliate ve yeni ürün yönlendirmesi bu sonuçta kapalıdır.'],showCommercial:false};
    }else if(latest.charge!=='full'||latest.load==='high'){
      result={state:'not_comparable',className:'warn',label:'Karşılaştırılabilir yeniden test',title:'Şarj veya yük koşulu eğilim kararı için yeterince sabit değil.',summary:'Yeni ürün kararı vermeden tam şarj ve mümkünse sabit yükle kontrollü test yapın.',steps:['Üretici talimatına göre tam şarjı tamamlayın.','Aynı cihazları ve benzer ortam koşullarını kullanın.','Erken kapanma veya alarm tekrarlanırsa teknik inceleme alın.'],showCommercial:false};
    }else if(repeatedSignificantDrop){
      result={state:'repeated_drop',className:'warn',label:'Tekrarlayan belirgin runtime düşüşü',title:'Doğrulama testi de önceki sağlıklı seviyenin belirgin altında kaldı.',summary:'Kablo, adaptör ve yük değişikliği dışlandıysa batarya/cihaz sağlık incelemesine ilerleyin. Mevcut süre ihtiyacı karşılıyorsa satın almama hâlâ geçerli sonuçtur.',steps:['Üretici olay kayıtlarını ve şarj davranışını kontrol edin.','Aynı yükle ölçülen iki düşük sonucu teknik servis veya kategori rehberiyle değerlendirin.','Kritik UPS yüklerinde doğrudan ürün yönlendirmesi yerine profesyonel kabul testi kullanın.'],showCommercial:latest.system==='mini'||latest.system==='station'};
    }else if(change!==null&&change<=SIGNIFICANT_DROP){
      result={state:'confirmation_needed',className:'warn',label:'Belirgin düşüş — doğrulama gerekli',title:'Tek karşılaştırmada çalışma süresi belirgin azaldı.',summary:'Ticari yönlendirme açılmadan önce aynı yük ve tam şarjla bir doğrulama testi daha yapın.',steps:['Tam şarj sonrası aynı yükle bir kez daha kontrollü test yapın.','Kablo, adaptör, yük ve ortam değişikliklerini dışlayın.','Düşüş ikinci karşılaştırılabilir testte de sürerse sağlık incelemesine ilerleyin.'],showCommercial:false};
    }else if(change!==null&&change<=TREND_DROP){
      result={state:'trend',className:'warn',label:'Eğilim izlenmeli',title:'Runtime düşüşü var; tek kayıtla değişim kararı vermeyin.',summary:'30–90 gün içinde aynı koşullarda yeniden test edin; mevcut süre yeterliyse satın almama geçerlidir.',steps:['Tam şarj ve aynı yük koşulunu koruyun.','Alarm ve erken kapanma kayıtlarını takip edin.','İhtiyaç süresi karşılanıyorsa mevcut ürünle devam edin.'],showCommercial:false};
    }
    if(latest.outcome!=='normal'&&safe)result.steps.push('Alarm veya erken kapanma tekrarında üretici kayıtları ve teknik servis sürecini kontrol edin.');
    return {...result,latest,baseline,reference,change,previousDrop,currentVsReference,repeatedSignificantDrop,priorCount:prior.length};
  }

  return {TTL_MS,MAX_RECORDS,SIGNIFICANT_DROP,TREND_DROP,compareOrder,sortEntries,normalizeEntry,pruneEntries,createEntry,serialize,priorComparable,assess};
});
