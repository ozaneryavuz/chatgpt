(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const AFFILIATE_TAG='alo186rehber-21';
  const AC_EFFICIENCY=0.85;
  const USABLE_FRACTION=0.80;
  const OUTPUT_HEADROOM=1.25;
  const SURGE_HEADROOM=1.15;
  const PF_PLANNING=0.80;
  const num=(value)=>{
    if(value===null||value===undefined||value==='')return null;
    const parsed=Number(String(value).replace(',','.'));
    return Number.isFinite(parsed)?parsed:null;
  };
  const roundUp=(value,step)=>Math.ceil(value/step)*step;
  const result=(status,title,summary,extra={})=>({status,title,summary,commercialAllowed:false,searchUrl:null,...extra});

  function calculate(input={}){
    if(input.gasEmergency){
      return result('emergency','Elektrik ürünü aramayın; gaz acil prosedürünü uygulayın','Gaz kokusu, CO alarmı, baca gazı belirtisi, yangın veya patlama şüphesinde elektrik düğmesi ve fiş kullanmayın; ortamdan güvenle çıkın ve Doğal Gaz Acil 187’yi arayın. Baş ağrısı, bulantı, bilinç değişikliği, nefes darlığı veya yangında 112 önceliklidir. Bütün ticari yollar kapalıdır.');
    }
    if(input.electricalEmergency){
      return result('emergency','Kombiyi ve yedek kaynağı kullanmayın','Duman, kıvılcım, erime, yanık kokusu, elektrik çarpması veya suyla elektrik teması varsa enerjiye yaklaşmayın; güvenli yerde 112 ve yetkili elektrik desteği alın. Bütün ticari yollar kapalıdır.');
    }
    if(input.applianceCondition==='damaged')return result('stop_use','Hasarlı veya su kaçıran cihazı beslemeyin','Kombi, kazan, adaptör, kablo veya priz ıslak, çatlak, erimiş, aşırı sıcak ya da su kaçaklıysa UPS/power station bağlamayın; yetkili servis ve elektrikçi incelemesi gerekir.');
    if(input.applianceCondition!=='sound')return result('evidence_required','Cihaz ve elektrik bağlantısını doğrulayın','Kombi, kablo, priz/şalter ve çevresinin kuru, sağlam ve olağandışı ısı/koku göstermediğini doğrulayın.');

    if(['electric_boiler','central_cascade','shared_boiler'].includes(input.applianceType||'')){
      return result('professional','Bu ısıtma sistemi profesyonel yedeklilik tasarımı gerektirir','Elektrikli kazan, ortak/merkezi kazan veya kaskad sistem; priz tipi UPS seçimiyle yönetilmez. Yük, kontrol, pompa, gaz ve transfer sistemi yetkili servis ve elektrik mühendisi tarafından projelendirilmelidir.');
    }
    if(!['gas_combi','gas_boiler_pump'].includes(input.applianceType||''))return result('evidence_required','Cihaz türünü doğrulayın','Bireysel gazlı kombi veya gazlı kazan + tek sirkülasyon pompası seçin.');
    if(input.criticalHeating==='yes')return result('professional','Kritik ısınma ihtiyacı için çok katmanlı plan gerekir','Donma, sağlık, yaşlı/çocuk veya yaşam güvenliği açısından ısıtmanın kesilmesi kritikse tek bir affiliate ürüne güvenmeyin. Gaz dağıtım, yetkili servis, elektrik ve alternatif barınma/ısıtma planını birlikte kurun.');
    if(input.criticalHeating!=='no')return result('evidence_required','Isıtma bağımlılık düzeyini doğrulayın','Kesintinin sağlık veya donma açısından kritik olup olmadığını belirtin.');
    if(input.connectionType==='fixed_wiring')return result('professional','Sabit elektrik bağlantısına kullanıcı müdahalesi yapılmaz','Sabit şalter, sigorta, pano, nötr-toprak veya transfer düzenine UPS eklemek yetkili elektrikçi ve kombi servisi işi olmalıdır. Ters besleme veya geçici kablo kullanmayın.');
    if(input.connectionType!=='approved_plug')return result('evidence_required','Üretici onaylı fişli bağlantıyı doğrulayın','Bu düşük riskli ön seçim yalnız mevcut, yetkili servisçe kurulmuş fişli bağlantı içindir. Sabit bağlantı profesyonel rotaya gider.');
    if(input.generatorTransfer==='yes')return result('professional','Jeneratör ve transfer sistemi profesyonel tasarım gerektirir','Kombi devresinin jeneratör veya bina transfer sistemine bağlanması; faz-nötr, nötr anahtarlama, topraklama ve geri besleme açısından projelendirilmelidir.');
    if(input.generatorTransfer!=='no')return result('evidence_required','Jeneratör/transfer durumunu doğrulayın','Bina transfer sistemi veya jeneratör bağlantısı bulunup bulunmadığını belirtin.');

    if(input.activeOutage==='yes')return result('active_outage','Aktif kesintide ürün teslimatını çözüm saymayın','Mevcut üretici onaylı kaynağı ve yetkili servis planını kullanın. Yeni ürün teslimatı mevcut kesintiyi çözmez; doğaçlama nötr-toprak köprüsü, ters besleme veya polaritesi belirsiz bağlantı yapmayın.');
    if(input.activeOutage!=='no')return result('evidence_required','Aktif kesinti durumunu belirtin','Geleceğe yönelik hazırlık ile devam eden kesinti ayrılmalıdır.');
    if(input.annualService!=='yes')return result('evidence_required','Yetkili bakım ve gaz güvenliği güncel olmalı','Baca, yanma, gaz ve su devresi güvenliği doğrulanmadan elektrik yedekleme ürünü seçmeyin.');
    if(input.flueVentilation!=='yes')return result('evidence_required','Baca ve havalandırma uygunluğu gerekli','Baca/atık gaz ve havalandırma koşulları yetkili servis veya gaz dağıtım şartlarına göre doğrulanmalıdır.');
    if(input.coAlarm!=='yes')return result('evidence_required','CO alarmı ve yerleşim planını tamamlayın','Yedek güç, karbonmonoksit riskini azaltmaz. Uygun CO alarmı, yerleşim ve düzenli test planı olmadan ticari rota açılmaz.');
    if(input.manufacturerCompatibility!=='yes')return result('evidence_required','Kombi üreticisi yedek güç uyumluluğu gerekli','Tam model için üreticinin/servisin saf sinüs, gerilim-frekans, faz-nötr, topraklama ve kesintisiz geçiş koşullarını doğrulayın. Satıcı beyanı tek başına yeterli değildir.');
    if(input.phaseNeutralVerified!=='yes')return result('evidence_required','Faz-nötr ve nötr-toprak düzeni doğrulanmalı','Bazı kombiler faz-nötr ve iyonizasyon/toprak referansına duyarlıdır. Yetkili servis ve elektrikçi, yedek kaynağın çıkış düzenini tam model için doğrulamalıdır.');
    if(input.recallChecked==='no')return result('stop_use','Aktif geri çağırma veya güvenlik düzeltmesini çözün','Kombi veya yedek güç kaynağında aktif güvenlik uyarısı varsa üretici talimatını uygulayın; affiliate yolu kapalıdır.');
    if(input.recallChecked!=='yes')return result('evidence_required','Geri çağırma ve güvenlik duyurusu kontrolü gerekli','Tam kombi ve yedek kaynak modelini üretici/resmî güvenlik kaynaklarında kontrol edin.');

    const model=String(input.boilerModel||'').trim();
    const boilerW=num(input.boilerMaxW);
    const startW=num(input.boilerStartW);
    const otherW=num(input.otherW)??0;
    const duty=num(input.dutyPercent);
    const hours=num(input.targetHours);
    if(model.length<3)return result('evidence_required','Tam kombi marka-modeli gerekli','Ürün etiketindeki tam model kodunu girin; kullanıcı adı veya adres girmeyin.');
    if(boilerW===null||boilerW<=0||boilerW>1500)return result('evidence_required','Azami elektrik güç çekişi gerekli','Kombi/kazan teknik föyündeki azami elektrik güç çekişini W olarak girin; ısıtma gücü olan 24 kW gibi değerleri kullanmayın.');
    if(startW===null||startW<=0||startW>5000)return result('evidence_required','Başlangıç/tepe elektrik gücü gerekli','Üretici, servis veya ölçümle doğrulanmış toplam başlangıç/tepe W değerini girin. Tahminle ürün seçmeyin.');
    if(otherW<0||otherW>1000)return result('evidence_required','Diğer eşzamanlı yükleri kontrol edin','Termostat, ağ geçidi veya ayrı pompa yükü 0–1000 W arasında olmalıdır.');
    if(duty===null||duty<10||duty>100)return result('evidence_required','Çalışma oranını doğrulayın','Enerji hesabı için %10–100 arasında ölçülmüş veya muhafazakâr çalışma oranı girin; bilinmiyorsa %100 kullanın.');
    if(hours===null||hours<1||hours>72)return result('evidence_required','Hedef süreyi kontrol edin','Hedef çalışma süresi 1–72 saat arasında olmalıdır. Uzun süreli afet planı tek ürüne bağlanmamalıdır.');

    const fullLoadW=boilerW+otherW;
    const averageW=boilerW*duty/100+otherW;
    const requiredContinuousW=roundUp(fullLoadW*OUTPUT_HEADROOM,10);
    const requiredSurgeW=roundUp(Math.max(startW+otherW,fullLoadW)*SURGE_HEADROOM,10);
    const requiredNominalWh=roundUp(averageW*hours/AC_EFFICIENCY/USABLE_FRACTION,10);
    const requiredVA=roundUp(requiredContinuousW/PF_PLANNING,50);
    const metrics={boilerW,averageW:Math.round(averageW),requiredContinuousW,requiredSurgeW,requiredNominalWh,requiredVA,targetHours:hours};

    const existing=input.existingSource;
    if(!['none','ups','power_station'].includes(existing||''))return result('evidence_required','Mevcut yedek kaynak durumunu belirtin','UPS, power station veya kaynak yok seçimini yapın.',{metrics});
    if(existing!=='none'){
      const sourceW=num(input.sourceContinuousW);
      const sourceSurge=num(input.sourceSurgeW);
      const sourceWh=num(input.sourceWh);
      if([sourceW,sourceSurge,sourceWh].some(v=>v===null||v<=0))return result('evidence_required','Mevcut kaynağın W, tepe W ve Wh değerleri gerekli','Tam model teknik föyünden sürekli çıkış, tepe/kalkış çıkışı ve nominal enerji kapasitesini girin.',{metrics});
      const gaps=[];
      if(sourceW<requiredContinuousW)gaps.push(`sürekli güç açığı ${requiredContinuousW-sourceW} W`);
      if(sourceSurge<requiredSurgeW)gaps.push(`tepe güç açığı ${requiredSurgeW-sourceSurge} W`);
      if(sourceWh<requiredNominalWh)gaps.push(`enerji açığı ${requiredNominalWh-sourceWh} Wh`);
      if(input.pureSine!=='yes')gaps.push('saf sinüs doğrulanmadı');
      if(input.output230V50Hz!=='yes')gaps.push('230 V / 50 Hz çıkış doğrulanmadı');
      if(input.transferTest!=='yes')gaps.push('şebeke geçiş testi başarısız/yapılmadı');
      if(input.actualHeatingTest!=='yes')gaps.push('gözetimli gerçek ısıtma testi başarısız/yapılmadı');
      if(!gaps.length)return result('no_buy','Mevcut kaynak yeterliyse yeni ürün almayın','Sürekli W, tepe W, Wh, saf sinüs, 230 V / 50 Hz, faz-nötr/toprak referansı ve gerçek ısıtma testi doğrulandı. Mevcut sistemi koruyun ve 90 gün sonra yeniden test edin.',{metrics});
      metrics.gaps=gaps;
    }

    const vaClass=[650,850,1000,1500,2000,3000,5000].find(v=>v>=requiredVA)||5000;
    const whClass=roundUp(requiredNominalWh,100);
    const query=encodeURIComponent(`${model} kombi uyumlu saf sinüs UPS ${vaClass}VA en az ${requiredContinuousW}W ${whClass}Wh`);
    return result('conditional_purchase','Saf sinüs UPS sınıfı için teknik açık doğrulandı','Bu yalnız güç/enerji ön seçimidir. Tam kombi modelinin faz-nötr, toprak referansı, geçiş süresi ve üretici uyumluluğu; aday UPS’in gerçek W, tepe W ve batarya süresiyle yeniden doğrulanmalıdır.',{metrics,commercialAllowed:true,searchUrl:`https://www.amazon.com.tr/s?k=${query}&tag=${AFFILIATE_TAG}`,vaClass,whClass});
  }

  function mount(doc){
    const form=doc.getElementById('boilerForm');if(!form)return;
    const output=doc.getElementById('result');const commerce=doc.getElementById('commerce');const link=doc.getElementById('affiliateLink');const jsonButton=doc.getElementById('jsonButton');const icsButton=doc.getElementById('icsButton');const gates=[...commerce.querySelectorAll('input[type="checkbox"]')];let last=null;
    const value=(id)=>{const el=doc.getElementById(id);return el&&el.type==='checkbox'?el.checked:el?.value;};
    const collect=()=>({gasEmergency:Boolean(value('gasEmergency')),electricalEmergency:Boolean(value('electricalEmergency')),applianceCondition:value('applianceCondition'),applianceType:value('applianceType'),criticalHeating:value('criticalHeating'),connectionType:value('connectionType'),generatorTransfer:value('generatorTransfer'),activeOutage:value('activeOutage'),annualService:value('annualService'),flueVentilation:value('flueVentilation'),coAlarm:value('coAlarm'),manufacturerCompatibility:value('manufacturerCompatibility'),phaseNeutralVerified:value('phaseNeutralVerified'),recallChecked:value('recallChecked'),boilerModel:value('boilerModel'),boilerMaxW:value('boilerMaxW'),boilerStartW:value('boilerStartW'),otherW:value('otherW'),dutyPercent:value('dutyPercent'),targetHours:value('targetHours'),existingSource:value('existingSource'),sourceContinuousW:value('sourceContinuousW'),sourceSurgeW:value('sourceSurgeW'),sourceWh:value('sourceWh'),pureSine:value('pureSine'),output230V50Hz:value('output230V50Hz'),transferTest:value('transferTest'),actualHeatingTest:value('actualHeatingTest')});
    const render=(data)=>{const m=data.metrics||{};output.hidden=false;output.className=`panel result status-${data.status}`;output.innerHTML=`<span class="status">${data.status.replaceAll('_',' ')}</span><h2>${data.title}</h2><p>${data.summary}</p>${Object.keys(m).length?`<div class="metrics"><div><span>Azami cihaz yükü</span><strong>${m.boilerW??'—'} W</strong></div><div><span>Ortalama plan yükü</span><strong>${m.averageW??'—'} W</strong></div><div><span>Gerekli sürekli çıkış</span><strong>${m.requiredContinuousW??'—'} W</strong></div><div><span>Gerekli tepe çıkış</span><strong>${m.requiredSurgeW??'—'} W</strong></div><div><span>Gerekli nominal enerji</span><strong>${m.requiredNominalWh??'—'} Wh</strong></div><div><span>Yaklaşık alt VA</span><strong>${m.requiredVA??'—'} VA</strong></div></div>${Array.isArray(m.gaps)?`<p><strong>Açıklar:</strong> ${m.gaps.join(', ')}</p>`:''}`:''}`;output.focus();commerce.hidden=!data.commercialAllowed;gates.forEach(g=>g.checked=false);link.hidden=true;link.removeAttribute('href');jsonButton.disabled=false;icsButton.disabled=false;};
    const refresh=()=>{if(!last?.commercialAllowed||!gates.every(g=>g.checked)){link.hidden=true;link.removeAttribute('href');return;}link.href=last.searchUrl;link.rel='sponsored nofollow noopener';link.hidden=false;};
    form.addEventListener('submit',e=>{e.preventDefault();last=calculate(collect());render(last);});gates.forEach(g=>g.addEventListener('change',refresh));
    form.addEventListener('reset',()=>setTimeout(()=>{last=null;output.hidden=true;output.innerHTML='';commerce.hidden=true;gates.forEach(g=>g.checked=false);link.hidden=true;link.removeAttribute('href');jsonButton.disabled=true;icsButton.disabled=true;},0));
    jsonButton.addEventListener('click',()=>{if(!last)return;download(doc,'alo186-kombi-yedek-guc.json',JSON.stringify({createdAt:new Date().toISOString(),tool:'ALO186 kombi yedek güç uygunluğu',result:last.status,metrics:last.metrics||{},personalDataCollected:false,commercialRankingFieldsUsed:[]},null,2),'application/json');});
    icsButton.addEventListener('click',()=>{if(!last)return;const d=new Date();d.setDate(d.getDate()+90);const stamp=d.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}/,'');const ics=`BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//ALO186//Kombi Yedek Guc//TR\r\nBEGIN:VEVENT\r\nDTSTART:${stamp}\r\nDURATION:PT30M\r\nSUMMARY:Kombi yedek güç sistemini yeniden test et\r\nDESCRIPTION:Yetkili bakım, CO alarmı, faz-nötr/toprak, saf sinüs, W, Wh, transfer ve gerçek ısıtma testini doğrula.\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n`;download(doc,'alo186-kombi-90-gun.ics',ics,'text/calendar');});
  }
  function download(doc,name,content,type){const blob=new Blob([content],{type});const url=URL.createObjectURL(blob);const a=doc.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),0);}
  return {calculate,mount};
});
