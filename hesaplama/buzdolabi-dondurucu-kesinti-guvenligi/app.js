(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.Alo186ColdChain=api;
  if(root&&root.document)api.mount(root.document);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const KEY='alo186-cold-chain-v1';
  const TTL=365*86400000;
  const LIMIT=8;
  const AFFILIATE_TAG='alo186rehber-21';
  const PRODUCT_CATEGORIES={
    thermometer:{
      id:'thermometer',
      title:'Buzdolabı ve dondurucu cihaz termometresi',
      description:'Gelecekteki kesintilerde kapıyı uzun süre açmadan sıcaklık kanıtı oluşturmak için; mevcut çalışan termometreniz varsa yenisi gerekli değildir.',
      query:'buzdolabı dondurucu cihaz termometresi 4 derece'
    },
    cooler:{
      id:'cooler',
      title:'Yalıtımlı soğutucu ve jel buz paketi',
      description:'Uzun kesintide bozulabilir gıdayı 4 °C ve altında tutmaya yönelik hazırlık ekipmanıdır; aktif olayda güvenli buz kaynağı yoksa ürün gelmesini beklemek çözüm değildir.',
      query:'yalıtımlı soğutucu çanta jel buz paketi'
    }
  };

  function amazonSearchUrl(query){
    return `https://www.amazon.com.tr/s?k=${encodeURIComponent(query)}&tag=${encodeURIComponent(AFFILIATE_TAG)}`;
  }

  function finiteOrNull(value){
    if(value===null||value===undefined||value==='')return null;
    const number=Number(value);
    return Number.isFinite(number)?number:null;
  }

  function thresholdFor(appliance){
    if(appliance==='freezer_full')return 48;
    if(appliance==='freezer_half'||appliance==='both')return 24;
    return 4;
  }

  function includesFridge(appliance){return appliance==='fridge'||appliance==='both';}
  function includesFreezer(appliance){return appliance==='freezer_full'||appliance==='freezer_half'||appliance==='both';}

  function normalize(input){
    const stage=['preparedness','active','restored'].includes(input.stage)?input.stage:'preparedness';
    const appliance=['fridge','freezer_full','freezer_half','both'].includes(input.appliance)?input.appliance:'fridge';
    return {
      stage,
      appliance,
      hours:Math.max(0,Math.min(168,finiteOrNull(input.hours)??0)),
      doorsClosed:Boolean(input.doorsClosed),
      thermometer:Boolean(input.thermometer),
      cooler:Boolean(input.cooler),
      gelPacks:Boolean(input.gelPacks),
      fridgeTemp:finiteOrNull(input.fridgeTemp),
      freezerTemp:finiteOrNull(input.freezerTemp),
      iceCrystals:['yes','no','unknown'].includes(input.iceCrystals)?input.iceCrystals:'unknown',
      electricalHazard:Boolean(input.electricalHazard),
      floodContact:Boolean(input.floodContact)
    };
  }

  function classify(raw){
    const input=normalize(raw);
    const hazard=input.electricalHazard||input.floodContact;
    const productNeeds=[];
    if(!input.thermometer)productNeeds.push('thermometer');
    if(!input.cooler||!input.gelPacks)productNeeds.push('cooler');
    const allPrepared=productNeeds.length===0;
    const steps=[];
    let severity='ok';
    let title='Hazırlık durumunuz değerlendirildi.';
    let summary='';
    let fridgeStatus=null;
    let freezerStatus=null;

    if(hazard){
      return {
        input,severity:'bad',title:'Elektriksel veya su teması riski var; ticari yol kapalı.',
        summary:'Cihaza, fişe veya prize dokunmayın. Güvenle yapılabiliyorsa enerjiyi yetkili kişiyle kestirin; duman, yangın veya elektrik çarpması riski varsa güvenli alana geçip 112’yi arayın.',
        steps:['Gıdayı kurtarmaya çalışırken elektriksel tehlikeye yaklaşmayın.','Su temaslı cihazı elektrik gelince kendiniz çalıştırmayın.','Uygun teknik inceleme olmadan cihazı tekrar enerjilendirmeyin.'],
        productNeeds:[],noBuy:true,commerceAllowed:false,commerceDeferred:false,fridgeStatus,freezerStatus
      };
    }

    if(input.stage==='preparedness'){
      title=allPrepared?'Mevcut hazırlığınız temel kanıt ihtiyacını karşılıyor.':'Gelecekteki kesinti için ölçülebilir hazırlık açığı var.';
      summary=allPrepared
        ?'Çalışan termometre, yalıtımlı soğutucu ve jel paketleriniz varsa yeni ürün satın almak gerekli değildir. Haftalık sıcaklık ve ekipman kontrolü yeterlidir.'
        :'Eksik ekipman yalnız gelecekteki kesintiye hazırlık için değerlendirilebilir. Ürün kategorisi açılması gıdanın güvenli olduğunu veya belirli bir çalışma süresini garanti etmez.';
      steps.push('Termometreyi cihaz çalışırken görünür ve temsilî bir noktaya yerleştirin.');
      steps.push('Buzdolabını yaklaşık 4 °C veya altında, dondurucuyu üretici hedefinde tuttuğunuzu düzenli kontrol edin.');
      steps.push('Kesinti başlangıç saatini kaydetme ve kapıları kapalı tutma planını hane halkıyla paylaşın.');
    }else if(input.stage==='active'){
      title='Kesinti devam ederken kapı yönetimi ve süre kaydı önceliklidir.';
      summary='Aktif kesintide ürün gelmesini beklemek veya termometre yerleştirmek için kapıyı açmak güvenli çözüm değildir. Kapıları kapalı tutun, başlangıç saatini kaydedin ve mevcut kanıtla karar verin.';
      steps.push('Buzdolabı ve dondurucu kapılarını gereksiz yere açmayın.');
      steps.push('Şüpheli gıdayı tatmayın; görünüş ve koku tek başına güvenlik kanıtı değildir.');
      if(!input.doorsClosed){severity='warn';steps.push('Kapı açıldığı için rehber süre daha kısa olabilir; ölçülen sıcaklık olmadan güvenli kabul etmeyin.');}
      if(includesFridge(input.appliance)){
        if(input.fridgeTemp!==null){
          fridgeStatus=input.fridgeTemp<=4?'measured_safe_reference':'above_reference';
          if(input.fridgeTemp<=4){steps.push(`Buzdolabı ${input.fridgeTemp.toLocaleString('tr-TR')} °C ölçüldü; kapıyı kapalı tutup izlemeye devam edin.`);}
          else{severity='warn';steps.push(`Buzdolabı ${input.fridgeTemp.toLocaleString('tr-TR')} °C ölçüldü; bozulabilir gıdanın 4 °C üzerinde kaldığı süreyi değerlendirin.`);}
        }else if(input.hours<=4&&input.doorsClosed){
          fridgeStatus='within_time_guide';
          steps.push('Buzdolabı kapısı kapalı ve kesinti 4 saati aşmadı; kapıyı kapalı tutup süreyi izleyin.');
        }else{
          fridgeStatus='evidence_needed';severity='warn';
          steps.push('Buzdolabı için 4 saat rehberi aşıldı veya kapı açıldı; sıcaklık/süre kanıtı olmadan bozulabilir gıdayı güvenli saymayın.');
          if(input.cooler&&input.gelPacks)steps.push('Mevcut soğutucu ve donmuş jel paketlerle bozulabilir gıdayı 4 °C ve altında tutma planını güvenli biçimde uygulayın.');
        }
      }
      if(includesFreezer(input.appliance)){
        const threshold=thresholdFor(input.appliance);
        if(input.freezerTemp!==null||input.iceCrystals==='yes'){
          const safeRef=(input.freezerTemp!==null&&input.freezerTemp<=4)||input.iceCrystals==='yes';
          freezerStatus=safeRef?'cold_evidence_present':'above_reference';
          steps.push(safeRef?'Dondurulmuş gıdada 4 °C ve altı ya da buz kristali kanıtı var; kapıyı kapalı tutup izleyin.':'Dondurucuda güvenli soğukluk kanıtı yok; elektrik geldikten sonra ürün bazlı resmî tabloyla değerlendirin.');
          if(!safeRef)severity='warn';
        }else if(input.hours<=threshold&&input.doorsClosed){
          freezerStatus='within_time_guide';
          const fullness=input.appliance==='freezer_full'?'Tam dolu':'Yarı dolu veya doluluğu bilinmeyen';
          steps.push(`${fullness} dondurucu için ${threshold} saat rehberi aşılmadı; kapıyı kapalı tutun.`);
        }else{
          freezerStatus='evidence_needed';severity='warn';
          steps.push(`Dondurucu için ${threshold} saat rehberi aşıldı veya kapı açıldı; sıcaklık ya da buz kristali kanıtı olmadan güvenli kabul etmeyin.`);
        }
      }
    }else{
      title='Elektrik geri geldi; süre yerine sıcaklık ve ürün kanıtını esas alın.';
      summary='Cihazı çalıştırmadan önce su/elektrik tehlikesi olmadığını doğrulayın. Gıda için ölçülen sıcaklık, 4 °C üzerinde kalma süresi ve buz kristali kanıtını kullanın; şüphede tatmayın.';
      if(includesFridge(input.appliance)){
        if(input.fridgeTemp!==null&&input.fridgeTemp<=4){
          fridgeStatus='measured_safe_reference';steps.push(`Buzdolabı ${input.fridgeTemp.toLocaleString('tr-TR')} °C: ölçüm 4 °C referansını karşılıyor; ürün bazlı süreyi yine kontrol edin.`);
        }else if(input.hours<=4&&input.doorsClosed){
          fridgeStatus='within_time_guide';steps.push('Kapı kapalı kaldı ve kesinti 4 saati aşmadı; cihaz sıcaklığını doğrulayarak normal kullanıma dönün.');
        }else{
          fridgeStatus='evidence_needed';severity='warn';steps.push('Buzdolabı 4 saat rehberini aştı veya sıcaklık kanıtı yok; bozulabilir gıdayı resmî ürün tablosuna göre değerlendirin.');
        }
      }
      if(includesFreezer(input.appliance)){
        const coldEvidence=(input.freezerTemp!==null&&input.freezerTemp<=4)||input.iceCrystals==='yes';
        if(coldEvidence){
          freezerStatus='cold_evidence_present';steps.push('Dondurulmuş gıda 4 °C ve altında veya buz kristalli: yeniden dondurma/pişirme mümkün olabilir; kalite kaybı olabilir.');
        }else{
          const threshold=thresholdFor(input.appliance);
          freezerStatus='evidence_needed';
          if(input.hours>threshold||!input.doorsClosed||input.iceCrystals==='no'){severity='warn';}
          steps.push('Dondurulmuş gıdada güvenli soğukluk kanıtı yok; yalnız koku/görünüşe güvenmeden resmî ürün tablosunu kullanın.');
        }
      }
      steps.push('Cihazın tekrar devreye girmesinde olağandışı ses, koku veya ısınma varsa fişe/prize müdahale etmeyin.');
    }

    const commerceAllowed=input.stage!=='active'&&!hazard&&productNeeds.length>0;
    const commerceDeferred=input.stage==='active'&&productNeeds.length>0;
    const noBuy=allPrepared||input.stage==='active';
    if(commerceDeferred)steps.push('Eksik termometre veya soğutucu ekipmanı mevcut olayın çözümü olarak değil, sonraki kesinti hazırlığı olarak değerlendirin.');

    return {input,severity,title,summary,steps,productNeeds,noBuy,commerceAllowed,commerceDeferred,fridgeStatus,freezerStatus};
  }

  function prune(records,now=Date.now()){
    return (Array.isArray(records)?records:[])
      .filter(record=>record&&Number.isFinite(record.createdAt)&&now-record.createdAt<TTL)
      .sort((a,b)=>b.createdAt-a.createdAt)
      .slice(0,LIMIT);
  }

  function readRecords(storage,now=Date.now()){
    try{return prune(JSON.parse(storage.getItem(KEY)||'[]'),now);}catch{return [];}
  }

  function writeRecord(storage,result,now=Date.now()){
    const record={createdAt:now,stage:result.input.stage,appliance:result.input.appliance,hours:result.input.hours,severity:result.severity,title:result.title,fridgeStatus:result.fridgeStatus,freezerStatus:result.freezerStatus,productNeeds:result.productNeeds,noBuy:result.noBuy};
    const records=prune([record,...readRecords(storage,now)],now);
    storage.setItem(KEY,JSON.stringify(records));
    return records;
  }

  function calendarText(start=new Date()){
    const pad=(value)=>String(value).padStart(2,'0');
    const stamp=(date)=>`${date.getUTCFullYear()}${pad(date.getUTCMonth()+1)}${pad(date.getUTCDate())}T${pad(date.getUTCHours())}${pad(date.getUTCMinutes())}00Z`;
    const end=new Date(start.getTime()+30*60000);
    return ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Soğuk Zincir Kontrolü//TR','BEGIN:VEVENT',`UID:alo186-cold-chain-${start.getTime()}@alo186.com`,`DTSTAMP:${stamp(new Date())}`,`DTSTART:${stamp(start)}`,`DTEND:${stamp(end)}`,'RRULE:FREQ=WEEKLY;COUNT=12','SUMMARY:Buzdolabı ve dondurucu sıcaklık kontrolü','DESCRIPTION:Termometreyi, cihaz sıcaklığını, soğutucu kutuyu ve jel paketleri kontrol edin. Mevcut ekipman yeterliyse yeni ürün almayın.','END:VEVENT','END:VCALENDAR',''].join('\r\n');
  }

  function download(documentRef,name,type,text){
    const blob=new Blob([text],{type});
    const url=URL.createObjectURL(blob);
    const anchor=documentRef.createElement('a');
    anchor.href=url;anchor.download=name;anchor.click();
    setTimeout(()=>URL.revokeObjectURL(url),0);
  }

  function mount(documentRef){
    const form=documentRef.getElementById('cold-form');
    if(!form)return;
    const resultEl=documentRef.getElementById('result');
    const commerce=documentRef.getElementById('commerce');
    const productNeedsEl=documentRef.getElementById('productNeeds');
    const recordsEl=documentRef.getElementById('records');
    const gateInputs=['actualMissing','futurePreparedness','affiliateAccepted'].map(id=>documentRef.getElementById(id));
    let lastResult=null;

    function collect(){
      const value=(id)=>documentRef.getElementById(id).value;
      const checked=(id)=>documentRef.getElementById(id).checked;
      return {stage:value('stage'),appliance:value('appliance'),hours:value('hours'),doorsClosed:checked('doorsClosed'),thermometer:checked('thermometer'),cooler:checked('cooler'),gelPacks:checked('gelPacks'),fridgeTemp:value('fridgeTemp'),freezerTemp:value('freezerTemp'),iceCrystals:value('iceCrystals'),electricalHazard:checked('electricalHazard'),floodContact:checked('floodContact')};
    }

    function gateOpen(){return gateInputs.every(input=>input.checked);}
    function syncGate(){
      productNeedsEl.querySelectorAll('a[data-affiliate]').forEach(link=>{const open=gateOpen();link.setAttribute('aria-disabled',open?'false':'true');link.tabIndex=open?0:-1;});
    }

    function renderRecords(){
      const records=readRecords(localStorage);
      recordsEl.innerHTML=records.length?records.map(record=>`<article class="record"><strong>${new Date(record.createdAt).toLocaleDateString('tr-TR')} · ${record.title}</strong><p>${record.appliance} · ${record.hours.toLocaleString('tr-TR')} saat · ${record.noBuy?'satın alma yok':'hazırlık eksiği'}</p></article>`).join(''):'<p class="muted">Henüz kayıt yok.</p>';
    }

    function render(result){
      lastResult=result;
      resultEl.className='panel result';
      resultEl.innerHTML=`<span class="status ${result.severity}">${result.severity==='bad'?'Güvenlik önceliği':result.severity==='warn'?'Kanıt gerekli':'Güvenli sonraki adım'}</span><h2>${result.title}</h2><p>${result.summary}</p><ol>${result.steps.map(step=>`<li>${step}</li>`).join('')}</ol>${result.noBuy?'<div class="no-buy"><strong>Satın alma sonucu kapalı.</strong> Mevcut ekipman yeterli veya aktif olayda alışveriş doğru çözüm değil.</div>':''}`;
      commerce.classList.toggle('hidden',!result.commerceAllowed);
      gateInputs.forEach(input=>{input.checked=false;});
      if(result.commerceAllowed){
        productNeedsEl.innerHTML=result.productNeeds.map(id=>{const item=PRODUCT_CATEGORIES[id];return `<article class="card"><span class="tag">Gelecek hazırlığı · gerçek eksik</span><h3>${item.title}</h3><p>${item.description}</p><a class="button affiliate" data-affiliate href="${amazonSearchUrl(item.query)}" target="_blank" rel="sponsored nofollow noopener" aria-disabled="true" tabindex="-1">Amazon satış ortaklığı seçeneklerini karşılaştır</a></article>`;}).join('');
        syncGate();
      }else{productNeedsEl.innerHTML='';}
      resultEl.focus();
    }

    form.addEventListener('submit',event=>{event.preventDefault();render(classify(collect()));});
    gateInputs.forEach(input=>input.addEventListener('change',syncGate));
    productNeedsEl.addEventListener('click',event=>{const link=event.target.closest('a[data-affiliate]');if(link&&link.getAttribute('aria-disabled')!=='false')event.preventDefault();});
    documentRef.getElementById('save').addEventListener('click',()=>{if(!lastResult)return;writeRecord(localStorage,lastResult);renderRecords();});
    documentRef.getElementById('export').addEventListener('click',()=>download(documentRef,'alo186-soguk-zincir-kararlari.json','application/json',JSON.stringify({exportedAt:new Date().toISOString(),records:readRecords(localStorage)},null,2)));
    documentRef.getElementById('calendar').addEventListener('click',()=>{const start=new Date(Date.now()+7*86400000);start.setHours(9,0,0,0);download(documentRef,'alo186-soguk-zincir-kontrolu.ics','text/calendar',calendarText(start));});
    renderRecords();
  }

  return {KEY,TTL,LIMIT,AFFILIATE_TAG,PRODUCT_CATEGORIES,amazonSearchUrl,normalize,classify,prune,calendarText,mount};
});
