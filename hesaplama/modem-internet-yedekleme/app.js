'use strict';

const AFFILIATE_URLS={
  mini:'https://www.amazon.com.tr/s?k=modem+mini+ups&tag=alo186rehber-21',
  backup:'https://www.amazon.com.tr/s?k=ta%C5%9F%C4%B1nabilir+g%C3%BC%C3%A7+istasyonu&tag=alo186rehber-21'
};

function numeric(value,name,min,max){
  const parsed=Number(value);
  if(!Number.isFinite(parsed)||parsed<min||parsed>max)throw new Error(`${name} ${min}–${max} aralığında olmalıdır.`);
  return parsed;
}

function evaluateModemBackup(raw){
  const connection=String(raw.connection||'other');
  const modemW=numeric(raw.modemW,'Modem gücü',0.1,150);
  const modemV=numeric(raw.modemV,'Modem voltajı',3,48);
  const separateOnt=connection==='fiber';
  const ontW=separateOnt?numeric(raw.ontW,'ONT gücü',0,100):0;
  const ontV=separateOnt&&ontW>0?numeric(raw.ontV,'ONT voltajı',3,48):0;
  const hours=numeric(raw.hours,'Hedef süre',0.5,48);
  const efficiency=numeric(raw.efficiency,'Verim',60,100)/100;
  const reserve=numeric(raw.reserve,'Rezerv',0,60)/100;
  const totalW=modemW+ontW;
  const minContinuousW=totalW*1.25;
  const requiredWh=totalW*hours/efficiency*(1+reserve);
  const modemA=modemW/modemV*1.25;
  const ontA=ontW>0?ontW/ontV*1.25:0;
  const differentVoltages=ontW>0&&Math.abs(modemV-ontV)>.05;
  const evidenceComplete=['voltageVerified','currentVerified','jackVerified','polarityVerified'].every(key=>raw[key]==='yes');
  const scenario=String(raw.scenario||'planning');
  const sourceStatus=String(raw.sourceStatus||'none');
  const serviceEvidence=String(raw.serviceEvidence||'unknown');
  let existingW=0,existingWh=0;
  if(sourceStatus==='existing'){
    existingW=numeric(raw.existingW,'Mevcut sürekli çıkış',1,1000);
    existingWh=numeric(raw.existingWh,'Mevcut enerji',1,5000);
  }
  const existingCapacityEnough=sourceStatus==='existing'&&existingW>=minContinuousW&&existingWh>=requiredWh;
  const realTest=String(raw.realTest||'unknown');

  let state='commerce';
  let commerceAllowed=true;
  let title='Teknik açık doğrulandı';
  let lead='Uyum kanıtları tamamlandı ve mevcut yeterli çözüm bulunmuyor. Yalnız gereken teknik sınıfı karşılaştırın.';
  let badge='Koşullu ürün yolu';
  let badgeClass='warn';

  if(Boolean(raw.electricalHazard)){
    state='hazard';commerceAllowed=false;badge='Kullanmayı durdurun';badgeClass='bad';
    title='Elektriksel veya batarya tehlikesi';
    lead='Ürünü enerjiden güvenli biçimde ayırabiliyorsanız ayırın; şişmiş veya hasarlı bataryayı şarj etmeyin. Ticari bağlantılar kapatıldı.';
  }else if(Boolean(raw.criticalUse)){
    state='professional';commerceAllowed=false;badge='Profesyonel plan';badgeClass='bad';
    title='Kritik kullanım için tüketici ürünü seçimi yeterli değil';
    lead='Sağlık, güvenlik veya kesintiye tahammülsüz işletme için yedekli erişim, operatör çeşitliliği, izleme ve bakım planı gerekir.';
  }else if(scenario==='active'){
    state='active';commerceAllowed=false;badge='Aktif kesinti';badgeClass='neutral';
    title='Yeni ürün mevcut kesintiyi çözmez';
    lead='Önce güvenli mevcut kaynağı, mobil bağlantı alternatifini ve internet işletmecisinin hizmet durumunu kontrol edin. Satış yolu kapatıldı.';
  }else if(serviceEvidence==='no'){
    state='service_gap';commerceAllowed=false;badge='Hizmet kanıtı yok';badgeClass='neutral';
    title='Ev içi güç tek başına bağlantı sağlamamış';
    lead='Geçmiş testte modem ve ONT açıkken internet hizmeti gelmediyse yeni mini UPS satın almak aynı sorunu çözmeyebilir. Önce işletmeci ve mobil yedek bağlantı planını değerlendirin.';
  }else if(!evidenceComplete||sourceStatus==='unknown'){
    state='evidence';commerceAllowed=false;badge='Kanıt gerekli';badgeClass='warn';
    title='Uyumluluk kanıtı tamamlanmadan ürün seçmeyin';
    lead='Voltaj, gerekli akım, DC jak ölçüsü, merkez polaritesi ve mevcut kaynağın değerleri doğrulanmadan mağaza yolu açılmaz.';
  }else if(sourceStatus==='existing'&&existingCapacityEnough&&realTest==='yes'){
    state='no_buy';commerceAllowed=false;badge='Satın alma yok';badgeClass='ok';
    title='Mevcut çözüm yeterli: yeni ürün almayın';
    lead='Sürekli güç, nominal enerji, çıkış uyumu ve gerçek kesinti testi hedefinizi karşılıyor.';
  }else if(sourceStatus==='existing'&&existingCapacityEnough&&realTest!=='yes'){
    state='test_first';commerceAllowed=false;badge='Önce test';badgeClass='warn';
    title='Kapasite yeterli görünüyor; önce gerçek kesinti testi yapın';
    lead='Etiket değerleri uygun olsa da gerçek süre ve internet hizmeti doğrulanmadan yeni ürün önermek gereksiz olabilir.';
  }else if(totalW>150||requiredWh>1000){
    state='professional';commerceAllowed=false;badge='Profesyonel değerlendirme';badgeClass='bad';
    title='Yük veya süre tüketici tipi mini UPS sınırını aşıyor';
    lead='Ağ dolabı, çoklu erişim cihazı veya uzun süreli kritik kullanım için projelendirilmiş UPS ve ağ sürekliliği planı gerekir.';
  }

  const productClass=requiredWh<=180&&totalW<=50?'mini':'backup';
  const outputs=[
    `Modem çıkışı: ${modemV.toFixed(1)} V DC ve en az ${modemA.toFixed(2)} A.`,
    ontW>0?`ONT çıkışı: ${ontV.toFixed(1)} V DC ve en az ${ontA.toFixed(2)} A.`:'Ayrı ONT yükü hesaba katılmadı.',
    differentVoltages?'Modem ve ONT farklı voltaj kullanıyor; tek sabit voltaj çıkışı yeterli değildir.':'Cihaz voltajları aynı görünse bile jak ve polarite ayrı doğrulanmalıdır.'
  ];
  const summary=[
    `Toplam sürekli yük yaklaşık ${totalW.toFixed(1)} W.`,
    `Ürün sürekli çıkışı en az ${minContinuousW.toFixed(1)} W olmalı.`,
    `Hedef süre için yaklaşık nominal enerji en az ${requiredWh.toFixed(0)} Wh.`,
    serviceEvidence==='unknown'?'İnternet işletmecisinin kesintide hizmet devamlılığı henüz doğrulanmadı.':'Geçmiş hizmet gözlemi gelecekte çalışma garantisi oluşturmaz.',
    sourceStatus==='existing'&&!existingCapacityEnough?`Mevcut kaynak güç veya enerji eşiğinin altında: ${existingW.toFixed(0)} W / ${existingWh.toFixed(0)} Wh.`:'Mevcut kaynak yoksa yalnız gerçek teknik açık için ürün karşılaştırın.'
  ];

  return {
    state,commerceAllowed,title,lead,badge,badgeClass,totalW,minContinuousW,requiredWh,
    modemA,ontA,differentVoltages,outputs,summary,productClass,
    affiliateUrl:AFFILIATE_URLS[productClass],revisitDays:90,
    generatedAt:new Date().toISOString()
  };
}

function byId(id){return document.getElementById(id);}
function readForm(){
  return {
    electricalHazard:byId('electricalHazard').checked,
    criticalUse:byId('criticalUse').checked,
    scenario:byId('scenario').value,
    connection:byId('connection').value,
    serviceEvidence:byId('serviceEvidence').value,
    modemW:byId('modemW').value,modemV:byId('modemV').value,
    ontW:byId('ontW').value,ontV:byId('ontV').value,
    hours:byId('hours').value,efficiency:byId('efficiency').value,reserve:byId('reserve').value,
    voltageVerified:byId('voltageVerified').value,currentVerified:byId('currentVerified').value,
    jackVerified:byId('jackVerified').value,polarityVerified:byId('polarityVerified').value,
    sourceStatus:byId('sourceStatus').value,existingW:byId('existingW').value,
    existingWh:byId('existingWh').value,realTest:byId('realTest').value
  };
}

function textList(target,items){
  target.innerHTML='';
  items.forEach(text=>{const li=document.createElement('li');li.textContent=text;target.appendChild(li);});
}
function download(name,type,content){
  const blob=new Blob([content],{type});
  const url=URL.createObjectURL(blob);
  const anchor=document.createElement('a');anchor.href=url;anchor.download=name;document.body.appendChild(anchor);anchor.click();anchor.remove();URL.revokeObjectURL(url);
}
function ymd(date){return date.toISOString().slice(0,10).replaceAll('-','');}
function safeTrack(name,payload){if(typeof Alo186Track==='function')Alo186Track(name,payload);}

function initBrowser(){
  const form=byId('modemForm');
  const sourceStatus=byId('sourceStatus');
  const existingFields=[...document.querySelectorAll('.existing-field')];
  let latest=null;

  function syncExisting(){existingFields.forEach(node=>node.classList.toggle('hidden',sourceStatus.value!=='existing'));}
  function syncGate(){
    const enabled=['actualNeed','technicalCheck','affiliateCheck'].every(id=>byId(id).checked);
    const link=byId('affiliateLink');
    link.classList.toggle('disabled',!enabled);
    link.setAttribute('aria-disabled',String(!enabled));
    link.textContent=enabled?'Amazon satış ortaklığı seçeneklerini aç':'Üç kontrolü tamamlayın';
    link.href=enabled&&latest?latest.affiliateUrl:'#';
  }
  function render(result){
    latest=result;
    byId('rLoad').textContent=`${result.totalW.toFixed(1)} W`;
    byId('rContinuous').textContent=`${result.minContinuousW.toFixed(1)} W`;
    byId('rWh').textContent=`${result.requiredWh.toFixed(0)} Wh`;
    byId('rState').textContent=result.state==='no_buy'?'Almayın':result.commerceAllowed?'Koşullu':'Bekleyin';
    byId('rStateNote').textContent=result.badge;
    const badge=byId('statusBadge');badge.textContent=result.badge;badge.className=`status ${result.badgeClass}`;
    byId('resultTitle').textContent=result.title;byId('resultLead').textContent=result.lead;
    textList(byId('summaryList'),result.summary);textList(byId('outputList'),result.outputs);
    byId('commerceGate').classList.toggle('hidden',!result.commerceAllowed);
    ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>{byId(id).checked=false;});syncGate();
    byId('results').classList.remove('hidden');byId('results').scrollIntoView({behavior:'smooth',block:'start'});
    safeTrack('modem_ont_backup_evaluated',{state:result.state,total_w:Math.round(result.totalW),required_wh:Math.round(result.requiredWh),commerce_allowed:result.commerceAllowed});
  }

  form.addEventListener('submit',event=>{
    event.preventDefault();byId('validation').textContent='';
    try{render(evaluateModemBackup(readForm()));}catch(error){byId('validation').textContent=error.message;}
  });
  form.addEventListener('reset',()=>setTimeout(()=>{byId('results').classList.add('hidden');byId('validation').textContent='';latest=null;syncExisting();},0));
  sourceStatus.addEventListener('change',syncExisting);
  ['actualNeed','technicalCheck','affiliateCheck'].forEach(id=>byId(id).addEventListener('change',syncGate));
  byId('affiliateLink').addEventListener('click',event=>{
    if(event.currentTarget.getAttribute('aria-disabled')==='true'){event.preventDefault();return;}
    safeTrack('modem_ont_affiliate_opened',{product_class:latest?.productClass||'unknown'});
  });
  byId('jsonBtn').addEventListener('click',()=>{if(latest)download('alo186-modem-ont-teknik-fis.json','application/json;charset=utf-8',JSON.stringify(latest,null,2));});
  byId('calendarBtn').addEventListener('click',()=>{
    if(!latest)return;
    const date=new Date();date.setDate(date.getDate()+latest.revisitDays);
    const body=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Modem ONT Kontrol//TR','BEGIN:VEVENT',`UID:alo186-modem-${Date.now()}@alo186.com`,`DTSTART;VALUE=DATE:${ymd(date)}`,`DTEND;VALUE=DATE:${ymd(new Date(date.getTime()+86400000))}`,'SUMMARY:Modem ve ONT yedek güç testini yenile','DESCRIPTION:Voltaj, akım, jak, polarite, batarya durumu, gerçek çalışma süresi ve internet işletmecisi hizmetini yeniden doğrulayın. Fiyat veya kampanya hatırlatması değildir.','END:VEVENT','END:VCALENDAR'].join('\r\n');
    download('alo186-modem-ont-90-gun-kontrol.ics','text/calendar;charset=utf-8',body);
  });
  syncExisting();syncGate();
}

if(typeof document!=='undefined')document.addEventListener('DOMContentLoaded',initBrowser);
if(typeof module!=='undefined'&&module.exports)module.exports={evaluateModemBackup,AFFILIATE_URLS};
