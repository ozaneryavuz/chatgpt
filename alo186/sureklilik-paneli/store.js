(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  root.Alo186ContinuityStore=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  const SCHEMA_VERSION=2;
  const HANDOFF_VERSION=1;
  const HANDOFF_MAX_AGE_MS=7*24*60*60*1000;
  const FACILITY_TYPES=new Set(['hotel','site','business','other']);
  const DIMENSIONS=new Set(['critical-loads','documentation','backup','testing','maintenance','incident','ownership','improvement']);
  const HORIZONS={day30:30,day60:60,day90:90};

  function nowIso(){return new Date().toISOString();}
  function id(prefix='id'){
    const random=typeof crypto!=='undefined'&&crypto.randomUUID?crypto.randomUUID():`${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
    return `${prefix}-${random}`;
  }
  function number(value,fallback=0){const n=Number(value);return Number.isFinite(n)?n:fallback;}
  function clone(value){return JSON.parse(JSON.stringify(value));}
  function cleanText(value,max=240){return String(value||'').replace(/[<>]/g,'').replace(/\s+/g,' ').trim().slice(0,max);}

  function createState(){
    return {
      schemaVersion:SCHEMA_VERSION,
      organization:{name:'',profile:'hotel',createdAt:nowIso(),updatedAt:nowIso()},
      locations:[],criticalLoads:[],assets:[],tests:[],incidents:[],improvementActions:[],maturityImports:[],auditLog:[]
    };
  }

  function audit(state,action,entityType,entityId,detail={}){
    state.auditLog.unshift({id:id('audit'),at:nowIso(),action,entityType,entityId,detail});
    state.auditLog=state.auditLog.slice(0,500);
  }

  function configureOrganization(state,{name,profile}){
    const next=clone(state);
    next.organization={...next.organization,name:String(name||'').trim(),profile:profile||'hotel',updatedAt:nowIso()};
    audit(next,'organization_updated','organization','organization',{profile:next.organization.profile});
    return next;
  }

  function addLocation(state,input){
    const next=clone(state);const name=String(input.name||'').trim();
    if(!name)throw new Error('Lokasyon adı zorunludur.');
    const location={id:id('loc'),name,province:String(input.province||'').trim(),district:String(input.district||'').trim(),type:input.type||next.organization.profile||'business',capacity:number(input.capacity),notes:String(input.notes||'').trim(),createdAt:nowIso()};
    next.locations.push(location);audit(next,'location_created','location',location.id,{name:location.name});return {state:next,location};
  }

  function addCriticalLoad(state,input){
    const next=clone(state);if(!next.locations.some(x=>x.id===input.locationId))throw new Error('Geçerli lokasyon seçin.');
    const name=String(input.name||'').trim();if(!name)throw new Error('Kritik yük adı zorunludur.');
    const load={id:id('load'),locationId:input.locationId,name,category:input.category||'other',powerKw:Math.max(0,number(input.powerKw)),priority:input.priority||'P2',requiredAutonomyMin:Math.max(0,number(input.requiredAutonomyMin)),backupSource:input.backupSource||'none',owner:String(input.owner||'').trim(),notes:String(input.notes||'').trim(),createdAt:nowIso()};
    next.criticalLoads.push(load);audit(next,'critical_load_created','critical_load',load.id,{name:load.name,priority:load.priority});return {state:next,load};
  }

  function addAsset(state,input){
    const next=clone(state);if(!next.locations.some(x=>x.id===input.locationId))throw new Error('Geçerli lokasyon seçin.');
    const name=String(input.name||'').trim();if(!name)throw new Error('Varlık adı zorunludur.');
    const asset={id:id('asset'),locationId:input.locationId,type:input.type||'generator',name,ratedPowerKva:Math.max(0,number(input.ratedPowerKva)),fuelCapacityL:Math.max(0,number(input.fuelCapacityL)),autonomyMin:Math.max(0,number(input.autonomyMin)),testIntervalDays:Math.max(1,number(input.testIntervalDays,7)),lastTestAt:null,createdAt:nowIso()};
    next.assets.push(asset);audit(next,'asset_created','asset',asset.id,{name:asset.name,type:asset.type});return {state:next,asset};
  }

  function recordTest(state,input){
    const next=clone(state);const asset=next.assets.find(x=>x.id===input.assetId);if(!asset)throw new Error('Geçerli jeneratör veya UPS seçin.');
    const test={id:id('test'),assetId:asset.id,locationId:asset.locationId,testedAt:input.testedAt||nowIso(),status:input.status||'passed',runtimeMin:Math.max(0,number(input.runtimeMin)),fuelPercent:input.fuelPercent===''||input.fuelPercent===undefined?null:Math.min(100,Math.max(0,number(input.fuelPercent))),transferObserved:input.transferObserved===true||input.transferObserved==='true',notes:String(input.notes||'').trim(),createdAt:nowIso()};
    next.tests.push(test);asset.lastTestAt=test.testedAt;audit(next,'asset_test_recorded','asset_test',test.id,{assetId:asset.id,status:test.status});return {state:next,test};
  }

  function taskTemplates(profile,loads){
    const tasks=[['Yetkili EDAŞ planlı kesinti ekranını kontrol et','before','P2'],['186 arıza kaydı ve kayıt numarasını doğrula','during','P2'],['Hassas cihazları güvenli kapatma planını uygula','during','P1'],['Enerji geri geldiğinde yükleri kademeli devreye al','after','P1'],['Kesinti başlangıç ve dönüş saatini kaydet','during','P2']];
    if(profile==='hotel')tasks.push(['Resepsiyon, mutfak, soğuk oda, asansör ve hidrofor durumunu kontrol et','during','P1'],['Misafir iletişim metnini yayınla','during','P2']);
    if(profile==='site')tasks.push(['Asansör ve hidrofor kullanıcılarını bilgilendir','during','P1'],['Bina sakinlerine ortak duyuru gönder','during','P2']);
    if(profile==='business')tasks.push(['POS, internet ve güvenlik sistemlerinin yedek gücünü kontrol et','during','P1']);
    loads.filter(x=>x.priority==='P1').forEach(load=>tasks.push([`${load.name} kritik yük durumunu doğrula`,'during','P1']));
    return tasks.map(([title,phase,priority])=>({id:id('task'),title,phase,priority,owner:'',completed:false,completedAt:null}));
  }

  function startIncident(state,input){
    const next=clone(state);const location=next.locations.find(x=>x.id===input.locationId);if(!location)throw new Error('Geçerli lokasyon seçin.');
    if(next.incidents.some(x=>x.locationId===location.id&&x.status==='open'))throw new Error('Bu lokasyonda zaten açık bir olay var.');
    const loads=next.criticalLoads.filter(x=>x.locationId===location.id);
    const incident={id:id('incident'),locationId:location.id,type:input.type||'outage',status:'open',startedAt:input.startedAt||nowIso(),endedAt:null,summary:String(input.summary||'').trim(),affectedSystems:Array.isArray(input.affectedSystems)?input.affectedSystems:[],caseNumber:String(input.caseNumber||'').trim(),tasks:taskTemplates(location.type||next.organization.profile,loads),events:[{id:id('event'),at:input.startedAt||nowIso(),type:'incident_started',note:String(input.summary||'Kesinti olayı başlatıldı.').trim()}],costs:[],createdAt:nowIso(),updatedAt:nowIso()};
    next.incidents.unshift(incident);audit(next,'incident_started','incident',incident.id,{locationId:location.id});return {state:next,incident};
  }

  function addIncidentEvent(state,incidentId,input){
    const next=clone(state);const incident=next.incidents.find(x=>x.id===incidentId);if(!incident)throw new Error('Olay bulunamadı.');
    const note=String(input.note||'').trim();if(!note)throw new Error('Olay notu zorunludur.');
    const event={id:id('event'),at:input.at||nowIso(),type:input.type||'note',note};incident.events.push(event);incident.updatedAt=nowIso();audit(next,'incident_event_added','incident',incident.id,{eventType:event.type});return {state:next,event};
  }

  function toggleIncidentTask(state,incidentId,taskId,completed=true){
    const next=clone(state);const incident=next.incidents.find(x=>x.id===incidentId);if(!incident)throw new Error('Olay bulunamadı.');
    const task=incident.tasks.find(x=>x.id===taskId);if(!task)throw new Error('Görev bulunamadı.');
    task.completed=Boolean(completed);task.completedAt=task.completed?nowIso():null;incident.updatedAt=nowIso();audit(next,'incident_task_updated','incident_task',task.id,{completed:task.completed});return {state:next,task};
  }

  function addIncidentCost(state,incidentId,input){
    const next=clone(state);const incident=next.incidents.find(x=>x.id===incidentId);if(!incident)throw new Error('Olay bulunamadı.');
    const amount=Math.max(0,number(input.amount));if(amount<=0)throw new Error('Maliyet sıfırdan büyük olmalıdır.');
    const cost={id:id('cost'),category:input.category||'other',amount,note:String(input.note||'').trim(),createdAt:nowIso()};incident.costs.push(cost);incident.updatedAt=nowIso();audit(next,'incident_cost_added','incident_cost',cost.id,{incidentId,amount});return {state:next,cost};
  }

  function closeIncident(state,incidentId,input={}){
    const next=clone(state);const incident=next.incidents.find(x=>x.id===incidentId);if(!incident)throw new Error('Olay bulunamadı.');
    const incompleteP1=incident.tasks.filter(x=>x.priority==='P1'&&!x.completed);
    incident.status='closed';incident.endedAt=input.endedAt||nowIso();incident.closureNote=String(input.closureNote||'').trim();incident.closedWithIncompleteP1=incompleteP1.length>0;incident.events.push({id:id('event'),at:incident.endedAt,type:'incident_closed',note:incident.closureNote||'Olay kapatıldı.'});incident.updatedAt=nowIso();audit(next,'incident_closed','incident',incident.id,{incompleteP1:incompleteP1.length});return {state:next,incident,incompleteP1};
  }

  function validateMaturityHandoff(raw,at=Date.now()){
    if(!raw||typeof raw!=='object'||raw.version!==HANDOFF_VERSION)return {valid:false,reason:'Sürüm geçersiz.'};
    const generated=Date.parse(raw.generatedAt||''),expires=Date.parse(raw.expiresAt||'');
    if(!Number.isFinite(generated)||!Number.isFinite(expires)||generated>at+300000||expires<=at||expires-generated>HANDOFF_MAX_AGE_MS+300000)return {valid:false,reason:'Aktarım süresi geçersiz veya dolmuş.'};
    const facilityType=FACILITY_TYPES.has(raw.facilityType)?raw.facilityType:'other',score=Math.round(number(raw.score,-1));
    if(score<0||score>100)return {valid:false,reason:'Skor geçersiz.'};
    const actions=[];
    Object.entries(HORIZONS).forEach(([phase,horizonDays])=>{
      const items=raw.plan&&Array.isArray(raw.plan[phase])?raw.plan[phase]:[];
      items.slice(0,9).forEach(item=>{
        const questionId=cleanText(item&&item.questionId,80),dimension=cleanText(item&&item.dimension,40),text=cleanText(item&&item.action,240);
        if(questionId&&DIMENSIONS.has(dimension)&&text)actions.push({questionId,dimension,text,horizonDays,priority:Math.max(0,Math.min(9,number(item.priority,0)))});
      });
    });
    if(!actions.length||actions.length>18)return {valid:false,reason:'Aktarılabilir aksiyon bulunamadı.'};
    const importId=cleanText(raw.importId,100)||`maturity-${generated}-${score}-${facilityType}`;
    return {valid:true,value:{version:HANDOFF_VERSION,importId,generatedAt:new Date(generated).toISOString(),expiresAt:new Date(expires).toISOString(),facilityType,score,band:cleanText(raw.band,40),dimensions:Array.isArray(raw.dimensions)?raw.dimensions.slice(0,8).map(d=>({id:cleanText(d&&d.id,40),title:cleanText(d&&d.title,90),score:Math.max(0,Math.min(100,Math.round(number(d&&d.score,0))))})).filter(d=>DIMENSIONS.has(d.id)):[],actions}};
  }

  function importMaturityHandoff(state,raw,at=Date.now()){
    const checked=validateMaturityHandoff(raw,at);if(!checked.valid)throw new Error(checked.reason);
    const next=hydrate(clone(state)),payload=checked.value;
    if(next.maturityImports.some(x=>x.importId===payload.importId))return {state:next,added:0,duplicate:true,importId:payload.importId};
    const existing=new Set(next.improvementActions.map(x=>`${x.sourceQuestionId}|${x.horizonDays}|${x.title}`));let added=0;
    payload.actions.forEach(item=>{const key=`${item.questionId}|${item.horizonDays}|${item.text}`;if(existing.has(key))return;next.improvementActions.push({id:id('improve'),title:item.text,dimension:item.dimension,horizonDays:item.horizonDays,priority:item.priority,status:'open',completed:false,completedAt:null,source:'maturity-score',sourceQuestionId:item.questionId,sourceImportId:payload.importId,createdAt:nowIso()});existing.add(key);added++;});
    next.maturityImports.unshift({importId:payload.importId,score:payload.score,band:payload.band,facilityType:payload.facilityType,dimensions:payload.dimensions,importedAt:nowIso(),actionCount:added});next.maturityImports=next.maturityImports.slice(0,20);
    if(!next.organization.name&&!next.locations.length&&['hotel','site','business'].includes(payload.facilityType))next.organization.profile=payload.facilityType;
    audit(next,'maturity_plan_imported','maturity_import',payload.importId,{score:payload.score,band:payload.band,facilityType:payload.facilityType,added});
    return {state:next,added,duplicate:false,importId:payload.importId};
  }

  function toggleImprovementAction(state,actionId,completed=true){
    const next=hydrate(clone(state)),action=next.improvementActions.find(x=>x.id===actionId);if(!action)throw new Error('İyileştirme aksiyonu bulunamadı.');
    action.completed=Boolean(completed);action.status=action.completed?'completed':'open';action.completedAt=action.completed?nowIso():null;audit(next,'improvement_action_updated','improvement_action',action.id,{completed:action.completed,horizonDays:action.horizonDays,dimension:action.dimension});return {state:next,action};
  }

  function incidentCostTotal(incident){return (incident&&incident.costs||[]).reduce((sum,x)=>sum+number(x.amount),0);}
  function taskProgress(incident){const tasks=incident&&incident.tasks||[];return tasks.length?Math.round(tasks.filter(x=>x.completed).length/tasks.length*100):0;}
  function improvementProgress(state){const items=state&&Array.isArray(state.improvementActions)?state.improvementActions:[];return items.length?Math.round(items.filter(x=>x.completed).length/items.length*100):0;}

  function metrics(state,at=new Date()){
    const now=at instanceof Date?at:new Date(at),openIncidents=state.incidents.filter(x=>x.status==='open'),p1Loads=state.criticalLoads.filter(x=>x.priority==='P1');
    const overdueAssets=state.assets.filter(asset=>{if(!asset.lastTestAt)return true;const due=new Date(asset.lastTestAt);due.setDate(due.getDate()+number(asset.testIntervalDays,7));return due<now;});
    return {locations:state.locations.length,criticalLoads:state.criticalLoads.length,p1Loads:p1Loads.length,assets:state.assets.length,overdueAssets:overdueAssets.length,openIncidents:openIncidents.length,totalIncidentCost:state.incidents.reduce((sum,x)=>sum+incidentCostTotal(x),0),improvementActions:state.improvementActions.length,improvementProgress:improvementProgress(state)};
  }

  function hydrate(raw){
    const base=createState();if(!raw||typeof raw!=='object')return base;
    return {...base,...raw,schemaVersion:SCHEMA_VERSION,organization:{...base.organization,...(raw.organization||{})},locations:Array.isArray(raw.locations)?raw.locations:[],criticalLoads:Array.isArray(raw.criticalLoads)?raw.criticalLoads:[],assets:Array.isArray(raw.assets)?raw.assets:[],tests:Array.isArray(raw.tests)?raw.tests:[],incidents:Array.isArray(raw.incidents)?raw.incidents:[],improvementActions:Array.isArray(raw.improvementActions)?raw.improvementActions:[],maturityImports:Array.isArray(raw.maturityImports)?raw.maturityImports:[],auditLog:Array.isArray(raw.auditLog)?raw.auditLog:[]};
  }

  return {SCHEMA_VERSION,HANDOFF_VERSION,HANDOFF_MAX_AGE_MS,createState,configureOrganization,addLocation,addCriticalLoad,addAsset,recordTest,startIncident,addIncidentEvent,toggleIncidentTask,addIncidentCost,closeIncident,validateMaturityHandoff,importMaturityHandoff,toggleImprovementAction,improvementProgress,incidentCostTotal,taskProgress,metrics,hydrate,clone};
});
