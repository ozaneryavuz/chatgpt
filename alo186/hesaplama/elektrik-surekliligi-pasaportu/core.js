(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports) module.exports=api;
  else root.AloContinuityPassport=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const FACILITY_TYPES=['hotel','site','business','other'];
  const CRITICAL_LOADS=['communications','refrigeration','safety-lighting','access-security','pumps','production'];
  const BACKUP_SYSTEMS=['generator','ups','battery-inverter','power-station'];
  const STATUS_VALUES=['current','due','planned','missing'];
  const STATUS_FACTOR={current:1,due:.6,planned:.35,missing:0};
  const EVIDENCE_ITEMS=[
    {id:'critical-load-inventory',title:'Kritik yük envanteri',weight:15,critical:true,action:'Kritik yükleri P1/P2/P3 olarak sınıflandırın; güç, süre ve sorumlu bilgisini kayda bağlayın.'},
    {id:'single-line-diagram',title:'Güncel tek hat şeması',weight:10,critical:false,action:'Ana dağıtım, yedek kaynak ve transfer noktalarını gösteren tek hat şemasını güncelleyin.'},
    {id:'emergency-contacts',title:'Acil iletişim ve görev sahipliği',weight:8,critical:true,action:'EDAŞ, 112, teknik ekip, yönetim ve kritik tedarikçi iletişimlerini görev sahipleriyle doğrulayın.'},
    {id:'backup-capacity-record',title:'Yedek kaynak kapasite kaydı',weight:12,critical:true,action:'Jeneratör, UPS veya batarya kapasitesini gerçek kritik yük ve hedef süreyle eşleştirin.'},
    {id:'backup-test-record',title:'Jeneratör / UPS test kaydı',weight:15,critical:true,action:'Yük altında test sonucu, tarih, süre, arıza ve düzeltici faaliyeti kayıt altına alın.'},
    {id:'transfer-test',title:'Transfer ve geçiş testi',weight:10,critical:true,action:'ATS/transfer ve kesintisiz geçiş davranışını kontrollü tatbikatta doğrulayın.'},
    {id:'protection-test',title:'RCD, sigorta ve koruma testleri',weight:10,critical:true,action:'Kaçak akım, koruma cihazı ve açma sürelerini yetkili ölçümle doğrulayın.'},
    {id:'grounding-measurement',title:'Topraklama ve süreklilik ölçümü',weight:8,critical:false,action:'Topraklama direnci, PE sürekliliği ve bağlantı durumunu tarihli raporla doğrulayın.'},
    {id:'outage-log',title:'Kesinti ve olay günlüğü',weight:7,critical:false,action:'Başlangıç/bitiş, etkilenen yük, maliyet, 186 kayıt no ve alınan aksiyonları kaydedin.'},
    {id:'recovery-drill',title:'Kurtarma tatbikatı ve yönetim gözden geçirmesi',weight:5,critical:false,action:'En az yıllık tatbikatla görevleri, kurtarma süresini ve açık aksiyonları test edin.'}
  ];

  const uniqueAllowed=(values,allowed)=>[...new Set((Array.isArray(values)?values:[]).filter(value=>allowed.includes(value)))];
  const clamp=(value,min,max)=>Math.max(min,Math.min(max,Number(value)||0));

  function sanitizeInput(input){
    const evidence={};
    EVIDENCE_ITEMS.forEach(item=>{
      const value=input&&input.evidence?input.evidence[item.id]:null;
      evidence[item.id]=STATUS_VALUES.includes(value)?value:'missing';
    });
    return {
      facilityType:FACILITY_TYPES.includes(input&&input.facilityType)?input.facilityType:'other',
      criticalLoads:uniqueAllowed(input&&input.criticalLoads,CRITICAL_LOADS),
      backupSystems:uniqueAllowed(input&&input.backupSystems,BACKUP_SYSTEMS),
      evidence,
      maturityScore:Number.isFinite(Number(input&&input.maturityScore))?Math.round(clamp(input.maturityScore,0,100)):null,
      maturityBand:typeof (input&&input.maturityBand)==='string'?input.maturityBand.slice(0,80):null
    };
  }

  function classification(score){
    if(score>=85) return {id:'controlled',label:'A · Kontrollü',tone:'ok',summary:'Kanıt disiplini güçlü; güncellik ve tatbikat ritmini koruyun.'};
    if(score>=70) return {id:'developing',label:'B · Gelişen',tone:'ok',summary:'Temel yapı var; kritik test ve kayıt boşluklarını kapatın.'};
    if(score>=50) return {id:'fragile',label:'C · Kırılgan',tone:'warn',summary:'Süreklilik kişilere veya doğrulanmamış kabullere bağlı olabilir.'};
    if(score>=30) return {id:'high-risk',label:'D · Yüksek risk',tone:'bad',summary:'Kritik kayıt ve test eksikleri kesinti etkisini büyütebilir.'};
    return {id:'critical-gaps',label:'E · Kritik boşluk',tone:'bad',summary:'Önce kritik yük, sorumluluk, yedekleme ve test temelini kurun.'};
  }

  function evaluatePassport(rawInput){
    const input=sanitizeInput(rawInput||{});
    let weighted=0;
    const priorities={p0:[],p1:[],p2:[]};
    const evidenceRows=EVIDENCE_ITEMS.map(item=>{
      const status=input.evidence[item.id];
      const earned=Math.round(item.weight*STATUS_FACTOR[status]*10)/10;
      weighted+=earned;
      if(status==='missing') priorities[item.critical?'p0':'p1'].push({id:item.id,title:item.title,action:item.action,status});
      else if(status==='planned') priorities.p1.push({id:item.id,title:item.title,action:item.action,status});
      else if(status==='due') priorities[item.critical?'p1':'p2'].push({id:item.id,title:item.title,action:item.action,status});
      return {...item,status,earned};
    });

    let penalty=0;
    if(!input.criticalLoads.length){
      penalty+=5;
      priorities.p1.unshift({id:'critical-load-map',title:'Kritik yük haritası eksik',action:'İşlev kaybı yaratacak yükleri belirleyip güç ve hedef süreyle sınıflandırın.',status:'missing'});
    }
    if(input.criticalLoads.length&&!input.backupSystems.length){
      penalty+=15;
      priorities.p0.unshift({id:'backup-system-gap',title:'Kritik yük için yedek kaynak seçilmedi',action:'Kritik yük ve hedef süreye göre uygun UPS, jeneratör veya batarya mimarisini saha verisiyle belirleyin.',status:'missing'});
    }
    const score=Math.max(0,Math.round(weighted-penalty));
    const reviewDays=score>=85?365:score>=70?180:90;
    return {
      valid:true,
      input,
      score,
      evidenceScore:Math.round(weighted),
      penalty,
      classification:classification(score),
      evidence:evidenceRows,
      priorities,
      reviewDays,
      professionalReviewRecommended:score<70||priorities.p0.length>0,
      panelRecommended:score<85||priorities.p0.length+priorities.p1.length>0
    };
  }

  function parseMaturityImport(value){
    const payload=typeof value==='string'?JSON.parse(value):value;
    if(!payload||typeof payload!=='object') throw new Error('Geçerli bir JSON nesnesi bulunamadı.');
    const candidates=[payload.score,payload.result&&payload.result.score,payload.assessment&&payload.assessment.score,payload.summary&&payload.summary.score];
    const score=candidates.map(Number).find(Number.isFinite);
    if(!Number.isFinite(score)||score<0||score>100) throw new Error('Olgunluk skoru 0–100 arasında bulunamadı.');
    const facilityCandidate=payload.facilityType||(payload.assessment&&payload.assessment.facilityType)||(payload.summary&&payload.summary.facilityType);
    const facilityType=FACILITY_TYPES.includes(facilityCandidate)?facilityCandidate:null;
    const band=payload.band||(payload.classification&&payload.classification.label)||(payload.result&&payload.result.classification&&payload.result.classification.label)||null;
    return {score:Math.round(score),facilityType,maturityBand:typeof band==='string'?band.slice(0,80):null};
  }

  function createPassport(rawInput,result,nowValue){
    const evaluation=result&&result.valid?result:evaluatePassport(rawInput);
    const input=evaluation.input;
    const now=nowValue instanceof Date?nowValue:new Date(nowValue||Date.now());
    if(Number.isNaN(now.getTime())) throw new Error('Geçersiz oluşturma tarihi.');
    const validUntil=new Date(now.getTime()+evaluation.reviewDays*86400000);
    return {
      schema:'https://www.alo186.com/schemas/electrical-continuity-passport-v1.schema.json',
      schemaVersion:'1.0.0',
      documentType:'ElectricalContinuityPassport',
      generatedAt:now.toISOString(),
      validUntil:validUntil.toISOString(),
      facilityType:input.facilityType,
      criticalLoadCategories:input.criticalLoads,
      backupSystems:input.backupSystems,
      scores:{passport:evaluation.score,evidence:evaluation.evidenceScore,maturity:input.maturityScore},
      maturity:{band:input.maturityBand},
      classification:{id:evaluation.classification.id,label:evaluation.classification.label},
      evidence:evaluation.evidence.map(item=>({id:item.id,status:item.status,weight:item.weight,earned:item.earned})),
      actions:{p0:evaluation.priorities.p0,p1:evaluation.priorities.p1,p2:evaluation.priorities.p2},
      limitations:{isCertification:false,isElectricalProject:false,isOfficialInspection:false,requiresFieldVerification:true},
      privacy:{containsPersonalData:false,containsFreeText:false,medicalOrLifeSupportFlagIncluded:false,immediateDangerFlagIncluded:false},
      source:{publisher:'ALO186',url:'https://www.alo186.com/hesaplama/elektrik-surekliligi-pasaportu/'}
    };
  }

  function validatePassport(passport){
    const errors=[];
    if(!passport||typeof passport!=='object') return {valid:false,errors:['Pasaport nesnesi bulunamadı.']};
    if(passport.schemaVersion!=='1.0.0') errors.push('schemaVersion 1.0.0 olmalıdır.');
    if(passport.documentType!=='ElectricalContinuityPassport') errors.push('documentType geçersiz.');
    if(!FACILITY_TYPES.includes(passport.facilityType)) errors.push('facilityType geçersiz.');
    if(!passport.privacy||passport.privacy.containsPersonalData!==false) errors.push('Kişisel veri bayrağı false olmalıdır.');
    if(!passport.scores||!Number.isFinite(Number(passport.scores.passport))||passport.scores.passport<0||passport.scores.passport>100) errors.push('Pasaport skoru geçersiz.');
    if(!Array.isArray(passport.evidence)||passport.evidence.length!==EVIDENCE_ITEMS.length) errors.push('Kanıt listesi eksik.');
    return {valid:errors.length===0,errors};
  }

  return {FACILITY_TYPES,CRITICAL_LOADS,BACKUP_SYSTEMS,STATUS_VALUES,STATUS_FACTOR,EVIDENCE_ITEMS,sanitizeInput,evaluatePassport,parseMaturityImport,createPassport,validatePassport,classification};
});
