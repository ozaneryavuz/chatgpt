(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186ContinuityGrowth=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const BASE_URL='https://www.alo186.com';
  const DIMENSION_LABELS={
    'critical-loads':'Kritik yük',documentation:'Dokümantasyon',backup:'Yedek güç',testing:'Test ve tatbikat',maintenance:'Bakım',incident:'Olay yönetimi',ownership:'Sahiplik',improvement:'İyileştirme'
  };
  const PROFILE_LABELS={hotel:'Otel / tesis',site:'Apartman / site',business:'Küçük işletme',other:'Diğer tesis'};
  const ROUTES={
    'critical-loads':{href:'#kritik-yukler',label:'Kritik yük envanterini aç',kind:'panel'},
    documentation:{href:'#rapor',label:'Rapor ve yedek bölümünü aç',kind:'panel'},
    backup:{href:`${BASE_URL}/hesaplama/yedek-guc-cozum-secici/`,label:'Yedek güç çözüm seçiciyi aç',kind:'free-tool'},
    testing:{href:'#testler',label:'Jeneratör / UPS testlerini aç',kind:'panel'},
    maintenance:{href:`${BASE_URL}/hesaplama/ekipman-bakim-plani/`,label:'Ekipman bakım planını aç',kind:'free-tool'},
    incident:{href:`${BASE_URL}/hesaplama/kesinti-gunlugu/`,label:'Kesinti günlüğünü aç',kind:'free-tool'},
    ownership:{href:'#kurulum',label:'Rol ve lokasyon kurulumunu aç',kind:'panel'},
    improvement:{href:'#iyilestirme',label:'90 günlük planı aç',kind:'panel'}
  };
  const QUESTION_ROUTES={
    backup_coverage:ROUTES.backup,
    backup_capacity:ROUTES.backup,
    transfer_test:ROUTES.testing,
    generator_test:ROUTES.testing,
    maintenance_calendar:ROUTES.maintenance,
    incident_log:ROUTES.incident,
    incident_cost:ROUTES.incident,
    critical_load_inventory:ROUTES['critical-loads'],
    roles:ROUTES.ownership,
    management_review:ROUTES.improvement
  };

  function number(value,fallback=0){const n=Number(value);return Number.isFinite(n)?n:fallback;}
  function clean(value,max=240){return String(value||'').replace(/[<>]/g,'').replace(/\s+/g,' ').trim().slice(0,max);}
  function date(value,fallback=new Date()){const d=value instanceof Date?new Date(value):new Date(value||fallback);return Number.isNaN(d.getTime())?new Date(fallback):d;}
  function addDays(value,days){const d=date(value);d.setUTCDate(d.getUTCDate()+Math.max(0,number(days)));return d;}
  function safeArray(value){return Array.isArray(value)?value:[];}
  function routeForAction(action){return QUESTION_ROUTES[clean(action&&action.sourceQuestionId,80)]||ROUTES[clean(action&&action.dimension,40)]||ROUTES.improvement;}

  function nextBestActions(state,limit=3){
    const max=Math.max(1,Math.min(6,number(limit,3)));
    const open=safeArray(state&&state.improvementActions)
      .filter(item=>item&&!item.completed&&item.status!=='completed')
      .sort((a,b)=>number(a.horizonDays,90)-number(b.horizonDays,90)||number(b.priority)-number(a.priority)||date(a.createdAt).getTime()-date(b.createdAt).getTime());
    if(!open.length){
      return [{
        id:'maturity-score-start',
        title:'Elektrik sürekliliği olgunluk skorunu tamamlayın.',
        dimension:'improvement',dimensionLabel:DIMENSION_LABELS.improvement,horizonDays:30,
        href:`${BASE_URL}/hesaplama/elektrik-surekliligi-olgunluk-skoru/`,
        linkLabel:'Ücretsiz olgunluk skorunu aç',kind:'free-tool',
        disclosure:'Ücretsiz değerlendirmedir; ürün veya resmî uygunluk önerisi değildir.'
      }];
    }
    const ranked=open.map(item=>{
      const route=routeForAction(item),kind=route.kind;
      return {
        id:clean(item.id,100),title:clean(item.title,240)||'İyileştirme aksiyonunu tamamlayın.',
        dimension:clean(item.dimension,40),dimensionLabel:DIMENSION_LABELS[item.dimension]||'İyileştirme',
        horizonDays:Math.max(0,number(item.horizonDays,90)),href:route.href,linkLabel:route.label,kind,
        disclosure:kind==='free-tool'?'Ücretsiz araçtır. Ürün bağlantısı yalnız düşük riskli sonuçta ve satış ortaklığı etiketiyle açılabilir.':'Panel içi görevdir; satın alma bağlantısı içermez.'
      };
    });
    const result=[],seenRoutes=new Set(),seenIds=new Set();
    ranked.forEach(item=>{if(result.length>=max||seenRoutes.has(item.href))return;result.push(item);seenRoutes.add(item.href);seenIds.add(item.id);});
    ranked.forEach(item=>{if(result.length>=max||seenIds.has(item.id))return;result.push(item);seenIds.add(item.id);});
    return result;
  }

  function activationReadiness(state){
    const actions=safeArray(state&&state.improvementActions),incidents=safeArray(state&&state.incidents);
    const milestones=[
      {id:'location',title:'En az bir lokasyon tanımlandı',done:safeArray(state&&state.locations).length>0},
      {id:'critical-load',title:'Kritik yük envanteri oluşturuldu',done:safeArray(state&&state.criticalLoads).length>0},
      {id:'asset',title:'Jeneratör, UPS veya batarya varlığı eklendi',done:safeArray(state&&state.assets).length>0},
      {id:'test',title:'En az bir test kaydı oluşturuldu',done:safeArray(state&&state.tests).length>0},
      {id:'plan',title:'30/60/90 günlük iyileştirme planı var',done:actions.length>0},
      {id:'evidence',title:'Bir aksiyon veya olay kanıtla kapatıldı',done:actions.some(x=>x&&x.completed)||incidents.some(x=>x&&x.status==='closed')}
    ];
    const completed=milestones.filter(x=>x.done).length,total=milestones.length,percent=Math.round(completed/total*100);
    const level=completed>=5?'Pilot değerlendirmesine hazır':completed>=3?'Pilot verisi oluşuyor':'Ön hazırlık';
    const next=milestones.find(x=>!x.done)||null;
    return {completed,total,percent,level,ready:completed>=4,next,milestones};
  }

  function genericProfile(state){const profile=state&&state.organization&&state.organization.profile;return PROFILE_LABELS[profile]||PROFILE_LABELS.other;}
  function latestMaturity(state){return safeArray(state&&state.maturityImports)[0]||null;}
  function overdueAssetCount(state,at=new Date()){
    const now=date(at);
    return safeArray(state&&state.assets).filter(asset=>{
      if(!asset||!asset.lastTestAt)return true;
      return addDays(asset.lastTestAt,number(asset.testIntervalDays,7))<now;
    }).length;
  }
  function profileCounts(state){
    const assets=safeArray(state&&state.assets),loads=safeArray(state&&state.criticalLoads),incidents=safeArray(state&&state.incidents),actions=safeArray(state&&state.improvementActions);
    return {
      locations:safeArray(state&&state.locations).length,
      criticalLoads:loads.length,
      p1Loads:loads.filter(x=>x&&x.priority==='P1').length,
      assets:assets.length,
      generators:assets.filter(x=>x&&x.type==='generator').length,
      ups:assets.filter(x=>x&&x.type==='ups').length,
      batteries:assets.filter(x=>x&&x.type==='battery').length,
      tests:safeArray(state&&state.tests).length,
      incidents:incidents.length,
      openIncidents:incidents.filter(x=>x&&x.status==='open').length,
      improvementActions:actions.length,
      completedActions:actions.filter(x=>x&&x.completed).length
    };
  }

  function buildPilotBrief(state,at=new Date()){
    const generatedAt=date(at).toISOString(),readiness=activationReadiness(state),counts=profileCounts(state),maturity=latestMaturity(state);
    const requestedCapabilities=['Rol bazlı erişim','Merkezi ve şifreli yedekleme','Bakım/test bildirimleri','Çoklu kullanıcı audit kaydı'];
    if(counts.locations>1)requestedCapabilities.push('Çoklu lokasyon görünümü');
    if(counts.incidents>0)requestedCapabilities.push('Olay yönetimi ve yönetici raporu');
    if(counts.improvementActions>0)requestedCapabilities.push('30/60/90 günlük iyileştirme backlog’u');
    const brief={
      version:1,generatedAt,source:'ALO186 Elektrik Sürekliliği Paneli',profile:genericProfile(state),
      readiness:{completed:readiness.completed,total:readiness.total,percent:readiness.percent,level:readiness.level},
      maturity:maturity?{score:Math.max(0,Math.min(100,Math.round(number(maturity.score)))),band:clean(maturity.band,40),actionCount:Math.max(0,number(maturity.actionCount))}:null,
      inventory:{...counts,overdueAssets:overdueAssetCount(state,at)},
      requestedCapabilities,
      privacy:{containsOrganizationName:false,containsLocationName:false,containsAddress:false,containsContact:false,containsSubscriptionNumber:false,containsFreeText:false,containsMedicalSelection:false},
      disclaimer:'Bu özet fiyat teklifi, teknik proje, bakım belgesi veya resmî uygunluk raporu değildir.'
    };
    const lines=[
      'ALO186 — anonim elektrik sürekliliği pilot kapsamı',
      `Oluşturma: ${generatedAt.slice(0,10)}`,
      `Profil: ${brief.profile}`,
      `Aktivasyon: ${readiness.completed}/${readiness.total} · ${readiness.level}`,
      maturity?`Olgunluk skoru: ${brief.maturity.score}/100${brief.maturity.band?` · ${brief.maturity.band}`:''}`:'Olgunluk skoru: henüz aktarılmadı',
      `Envanter: ${counts.locations} lokasyon, ${counts.criticalLoads} kritik yük (${counts.p1Loads} P1), ${counts.assets} yedek güç varlığı, ${counts.tests} test kaydı`,
      `Takip: ${counts.improvementActions} aksiyon (${counts.completedActions} tamamlandı), ${counts.incidents} olay (${counts.openIncidents} açık), ${brief.inventory.overdueAssets} gecikmiş test`,
      `İstenen SaaS yetenekleri: ${requestedCapabilities.join(', ')}`,
      'Gizlilik: Kuruluş/lokasyon adı, adres, iletişim, abonelik, serbest metin ve tıbbi seçim içermez.',
      brief.disclaimer
    ];
    return {brief,text:lines.join('\n')};
  }

  function actionDueDate(action){return addDays(action&&action.createdAt,number(action&&action.horizonDays,90));}
  function assetDueDate(asset,at){if(asset&&asset.lastTestAt)return addDays(asset.lastTestAt,number(asset.testIntervalDays,7));return date(at);}
  function buildCalendarEvents(state,at=new Date()){
    const now=date(at),events=[];
    safeArray(state&&state.improvementActions).filter(x=>x&&!x.completed).slice(0,18).forEach(action=>{
      const due=actionDueDate(action),dimension=DIMENSION_LABELS[action.dimension]||'İyileştirme';
      events.push({id:`action-${clean(action.id,80)}`,date:due,summary:`ALO186 ${number(action.horizonDays,90)} günlük süreklilik aksiyonu`,description:`${dimension}: ${clean(action.title,220)} Panelde gözden geçirin.`,url:`${BASE_URL}/isletme-surekliligi#iyilestirme`,kind:'improvement'});
    });
    safeArray(state&&state.assets).slice(0,12).forEach((asset,index)=>{
      const type=asset&&asset.type==='generator'?'Jeneratör':asset&&asset.type==='ups'?'UPS':'Batarya / inverter';
      events.push({id:`asset-${index}-${date(asset&&asset.createdAt,now).getTime()}`,date:assetDueDate(asset,now),summary:`ALO186 ${type} test kontrolü`,description:'Panelde kayıtlı yedek güç varlığının test periyodunu ve son test sonucunu gözden geçirin. Varlık veya lokasyon adı takvime aktarılmamıştır.',url:`${BASE_URL}/isletme-surekliligi#testler`,kind:'asset-test'});
    });
    if(events.length){events.push({id:`review-${now.toISOString().slice(0,10)}`,date:addDays(now,30),summary:'ALO186 aylık elektrik sürekliliği gözden geçirmesi',description:'Kritik yükleri, açık aksiyonları, geciken testleri ve olay kayıtlarını panelde gözden geçirin.',url:`${BASE_URL}/isletme-surekliligi#dashboard`,kind:'review'});}
    return events.sort((a,b)=>date(a.date).getTime()-date(b.date).getTime()).slice(0,30);
  }

  function icsEscape(value){return String(value||'').replace(/\\/g,'\\\\').replace(/\r?\n/g,'\\n').replace(/,/g,'\\,').replace(/;/g,'\\;');}
  function ymd(value){return date(value).toISOString().slice(0,10).replace(/-/g,'');}
  function stamp(value){return date(value).toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z');}
  function buildIcs(events,at=new Date()){
    const now=date(at),rows=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Elektrik Surekliligi//TR','CALSCALE:GREGORIAN','METHOD:PUBLISH'];
    safeArray(events).slice(0,30).forEach((event,index)=>{
      rows.push('BEGIN:VEVENT',`UID:${icsEscape(clean(event&&event.id,120)||`alo186-${index}`)}@alo186.com`,`DTSTAMP:${stamp(now)}`,`DTSTART;VALUE=DATE:${ymd(event&&event.date)}`,`SUMMARY:${icsEscape(clean(event&&event.summary,180))}`,`DESCRIPTION:${icsEscape(clean(event&&event.description,500))}`,`URL:${icsEscape(clean(event&&event.url,300)||`${BASE_URL}/isletme-surekliligi`)}`,'TRANSP:TRANSPARENT','END:VEVENT');
    });
    rows.push('END:VCALENDAR');return rows.join('\r\n')+'\r\n';
  }

  return {BASE_URL,DIMENSION_LABELS,ROUTES,nextBestActions,activationReadiness,profileCounts,overdueAssetCount,buildPilotBrief,buildCalendarEvents,buildIcs,clean};
});
