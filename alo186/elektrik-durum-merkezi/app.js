'use strict';
(() => {
  const form=document.getElementById('status-form');
  const result=document.getElementById('result');
  const save=document.getElementById('save');
  const exportBtn=document.getElementById('export');
  const clear=document.getElementById('clear');
  const list=document.getElementById('record-list');
  if(!form||!result||!save||!exportBtn||!clear||!list)return;

  const key='alo186.electricStatus.v1';
  const ttl=30*24*60*60*1000;
  const fields=[...form.querySelectorAll('fieldset')];
  const submit=form.querySelector('button[type="submit"]');
  let last=null;
  let currentStep=0;

  const labels={outage:'Tam kesinti',voltage:'Gerilim olayı',meter:'Sayaç/şebeke ekipmanı',panel:'İç tesisat',damage:'Cihaz hasarı',backup:'Yedek güç',device:'Tek cihaz/priz',home:'Daire/villa',building:'Bina/site',area:'Sokak/mahalle',business:'İşletme',once:'İlk kez',sometimes:'Ara sıra',frequent:'Sık tekrarlıyor',continuous:'Devam ediyor'};
  const allowedEvents=new Set(['outage','voltage','meter','panel','damage','backup']);
  const allowedScopes=new Set(['device','home','building','area','business']);
  const allowedRepeats=new Set(['once','sometimes','frequent','continuous']);
  const allowedHazards=new Set(['smoke','spark','shock','heat','water']);

  const read=()=>{try{return JSON.parse(localStorage.getItem(key)||'[]').filter(x=>Date.now()-Number(x.createdAt||0)<ttl).slice(0,6)}catch{return[]}};
  const write=items=>{try{localStorage.setItem(key,JSON.stringify(items.slice(0,6)))}catch{}};
  const route=(href,title,text)=>`<a class="route" href="${href}"><b>${title}</b>${text}</a>`;
  const humanDate=value=>new Date(value).toLocaleString('tr-TR',{dateStyle:'medium',timeStyle:'short'});

  function renderRecords(){
    const items=read();
    write(items);
    list.innerHTML=items.length?items.map(x=>`<div class="record-item"><b>${humanDate(x.createdAt)}</b><span>${labels[x.event]||x.event} · ${labels[x.scope]||x.scope} · ${labels[x.repeat]||x.repeat}</span><small>${x.title}</small></div>`).join(''):'<p>Henüz cihazda saklanan kayıt yok.</p>';
  }

  function evaluate(data){
    const hazards=data.hazards;
    const dangerous=hazards.some(x=>['smoke','spark','shock'].includes(x));
    const hot=hazards.includes('heat')||hazards.includes('water');
    if(dangerous){return{level:'danger',title:'Öncelik: can güvenliği ve acil müdahale',summary:'Enerji kaynağına yaklaşmayın, suyla müdahale etmeyin ve güvenli mesafeden 112’yi arayın. Ardından şebeke tarafı şüphesi varsa 186 kaydı oluşturun.',steps:['İnsanları riskli alandan uzaklaştırın.','Güvenli değilse şalter veya cihaza dokunmayın.','Fotoğraf/video için tehlikeli alana girmeyin.'],routes:[route('tel:112','112 Acil','Yangın, elektrik çarpması, duman veya aktif kıvılcım'),route('/karar-motoru','Güvenli yönlendirme','Tehlike sonrası doğru teknik ve resmî kanalı ayırın.')]}};
    if(hot){return{level:'warning',title:'Öncelik: kullanımı durdurun ve enerjili müdahale yapmayın',summary:'Aşırı ısınma, erime veya su teması ürün alışverişiyle çözülmez. Yetkili elektrikçi incelemesi ve şebeke sorumluluğu ayrımı gerekir.',steps:['Ekipmanı yeniden devreye almayın.','Olay saati ve güvenli mesafeden görünür belirtileri kaydedin.','Sayaç önü/servis hattı şüphesinde 186’yı kullanın.'],routes:[route('/karar-motoru','112/186/elektrikçi ayrımı','Sorumluluk ve güvenlik rotasını belirleyin.'),route('/hesaplama/elektrik-kanit-envanteri/','Kanıt envanteri','Olay kayıtlarını kişisel veri vermeden düzenleyin.')]}};
    const common=['Olay saatini ve kapsamını kaydedin.','Aynı anda etkilenen cihaz veya bölgeyi not edin.'];
    if(data.event==='outage'){
      const area=data.scope==='area'||data.scope==='building';
      return{level:'safe',title:area?'Şebeke/EDAŞ rotası öncelikli':'Önce kapsamı ve iç tesisatı ayırın',summary:area?'Komşu alanı da etkileyen kesintide 186 ve ilgili dağıtım şirketinin kesinti kanalı kullanılmalıdır.':'Yalnız daireyi etkileyen kesintide ana koruma, kaçak akım ve bina ortak alanı kontrolü yetkili kişi tarafından ayrılmalıdır.',steps:[...common,'Planlı kesinti bilgisini resmî EDAŞ kanalından doğrulayın.'],routes:[route('/edas-bul','EDAŞ bulucu','İl ve ilçeye göre doğru dağıtım şirketini bulun.'),route('/hesaplama/kesinti-gunlugu/','Kesinti günlüğü','Süre, tekrar ve cihaz etkisini cihazınızda kaydedin.')]};
    }
    if(data.event==='voltage')return{level:'warning',title:'Gerilim olayı için zaman damgalı kanıt oluşturun',summary:'Titreme veya reset, tam kesinti olmayabilir. Kalan gerilim, süre, faz ve eşzamanlı yük değişimi ayrılmadan ürün değiştirmeyin.',steps:[...common,'Tek multimetre fotoğrafını kesin kanıt kabul etmeyin.'],routes:[route('/haberler/gerilim-cukuru-kisa-kesinti-dusuk-gerilim-farki','Gerilim olayı rehberi','Çukur, kısa kesinti ve düşük gerilimi ayırın.'),route('/hesaplama/gerilim-koruma-cozum-secici/','Çözüm seçici','SPD, UPS/AVR, regülatör ve EDAŞ rotasını karşılaştırın.')]};
    if(data.event==='meter')return{level:'warning',title:'Sayaç ve şebeke ekipmanına müdahale etmeyin',summary:'Mühürlü sayaç, servis hattı, direk veya şebeke ekipmanı kullanıcı müdahalesine kapalıdır. 186 ve ilgili dağıtım şirketinin resmî kanalı kullanılmalıdır.',steps:[...common,'Sayaç sonrası iç tesisat bölümünü ayrıca yetkili elektrikçiye kontrol ettirin.'],routes:[route('/edas-bul','EDAŞ bulucu','Doğru şirket ve resmî iletişim kanalını bulun.'),route('/haberler/elektrik-sayaci-isiniyor-yanik-kokusu-cizirti-edas-elektrikci','Sayaç güvenliği rehberi','EDAŞ ve elektrikçi görev ayrımını görün.')]};
    if(data.event==='panel')return{level:'warning',title:'İç tesisat ve koruma cihazı incelemesi gerekir',summary:'Pano, priz, kablo veya kaçak akım sorunu yalnız daha büyük sigorta ya da yeni ürünle çözülmemelidir. Kök neden ve ölçüm gerekir.',steps:[...common,'RCD’yi sürekli kaldırarak kullanıma devam etmeyin.'],routes:[route('/karar-motoru','Güvenli yönlendirme','Pano, nötr, faz, RCD ve kablo sorununu ayırın.'),route('/hesaplama/elektrik-surekliligi-pasaportu/','Teknik pasaport','Kanıt ve eksikleri P0/P1/P2 olarak düzenleyin.')]};
    if(data.event==='damage')return{level:'warning',title:'Cihaz hasarı dosyasını gecikmeden hazırlayın',summary:'Dağıtım şebekesinden kaynaklandığını düşündüğünüz cihaz hasarında güncel başvuru süresini ve dağıtım şirketinin resmî kanalını kontrol edin.',steps:[...common,'Servis raporu, fotoğraf, fatura/cihaz bilgisi ve yazılı kararları saklayın.'],routes:[route('/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu','Başvuru rehberi','Belge, süre ve görev ayrımını görün.'),route('/edas-bul','EDAŞ bulucu','İlgili dağıtım şirketine ulaşın.')]};
    return{level:'warning',title:'Yedek güç olayını kaynak, yük ve transfer olarak ayırın',summary:'UPS, jeneratör veya inverter arızasında yalnız kapasite etiketi yeterli değildir. Gerçek yük, transfer, alarm ve çalışma modu birlikte incelenmelidir.',steps:[...common,'Alarm kodunu ve olay anındaki yükü kaydedin.','Bypass veya manuel transferi yetkisiz uygulamayın.'],routes:[route('/hesaplama/elektrik-surekliligi-pasaportu/','Süreklilik pasaportu','Yedek kaynak ve kanıt durumunu çıkarın.'),route('/kurumsal-elektrik-surekliligi-on-degerlendirme','Profesyonel ön değerlendirme','Otel, site ve işletme için teknik kapsam oluşturun.')]};
  }

  function currentData(){
    const fd=new FormData(form);
    return{event:fd.get('event'),scope:fd.get('scope'),repeat:fd.get('repeat'),hazards:fd.getAll('hazard')};
  }

  function showOutcome(data,scroll=true){
    const outcome=evaluate(data);
    last={...data,...outcome,createdAt:Date.now()};
    result.hidden=false;
    result.className=`result ${outcome.level}`;
    result.innerHTML=`<span class="result-kicker">Önerilen sonraki adım</span><h2>${outcome.title}</h2><p>${outcome.summary}</p><ol class="checklist">${outcome.steps.map(x=>`<li>${x}</li>`).join('')}</ol><div class="route-grid">${outcome.routes.join('')}</div>`;
    save.disabled=false;
    if(scroll)result.scrollIntoView({behavior:'smooth',block:'start'});
  }

  const progress=document.createElement('div');
  progress.className='stepper';
  progress.setAttribute('aria-live','polite');
  progress.innerHTML='<div class="stepper-copy"><b id="step-label">Adım 1 / 4</b><span id="step-title">Olayı seçin</span></div><div class="progress-track" aria-hidden="true"><span id="progress-bar"></span></div>';
  form.insertBefore(progress,fields[0]);

  const feedback=document.createElement('p');
  feedback.className='step-feedback';
  feedback.hidden=true;
  form.insertBefore(feedback,submit);

  const navigation=document.createElement('div');
  navigation.className='step-actions';
  navigation.innerHTML='<button type="button" id="step-back" class="ghost">Geri</button><button type="button" id="step-next">Devam</button>';
  form.insertBefore(navigation,submit);
  const back=navigation.querySelector('#step-back');
  const next=navigation.querySelector('#step-next');
  const stepLabel=progress.querySelector('#step-label');
  const stepTitle=progress.querySelector('#step-title');
  const progressBar=progress.querySelector('#progress-bar');
  const stepNames=['Olayı seçin','Tehlike belirtisini işaretleyin','Kapsamı belirleyin','Tekrar durumunu seçin'];

  function stepComplete(index){
    const data=currentData();
    if(index===0)return Boolean(data.event);
    if(index===2)return Boolean(data.scope);
    if(index===3)return Boolean(data.repeat);
    return true;
  }

  function setStep(index,{focus=true}={}){
    currentStep=Math.max(0,Math.min(fields.length-1,index));
    fields.forEach((field,i)=>{field.hidden=i!==currentStep;field.setAttribute('aria-hidden',String(i!==currentStep))});
    stepLabel.textContent=`Adım ${currentStep+1} / ${fields.length}`;
    stepTitle.textContent=stepNames[currentStep]||'';
    progressBar.style.width=`${((currentStep+1)/fields.length)*100}%`;
    back.hidden=currentStep===0;
    next.hidden=currentStep===fields.length-1;
    submit.hidden=currentStep!==fields.length-1;
    feedback.hidden=true;
    if(focus){const target=fields[currentStep].querySelector('input,select');if(target)target.focus({preventScroll:true})}
  }

  next.addEventListener('click',()=>{
    if(!stepComplete(currentStep)){
      feedback.textContent=currentStep===0?'Önce olay türünü seçin.':'Bu adımı tamamlayın.';
      feedback.hidden=false;
      return;
    }
    setStep(currentStep+1);
  });
  back.addEventListener('click',()=>setStep(currentStep-1));

  function applyRecord(record,{showResult=false}={}){
    if(!record)return;
    if(allowedEvents.has(record.event)){
      const input=form.querySelector(`input[name="event"][value="${record.event}"]`);
      if(input)input.checked=true;
    }
    form.querySelectorAll('input[name="hazard"]').forEach(input=>{input.checked=Array.isArray(record.hazards)&&record.hazards.includes(input.value)});
    if(allowedScopes.has(record.scope))form.elements.scope.value=record.scope;
    if(allowedRepeats.has(record.repeat))form.elements.repeat.value=record.repeat;
    setStep(fields.length-1,{focus:false});
    if(showResult&&record.event&&record.scope&&record.repeat)showOutcome({event:record.event,scope:record.scope,repeat:record.repeat,hazards:(record.hazards||[]).filter(x=>allowedHazards.has(x))},false);
    form.scrollIntoView({behavior:'smooth',block:'start'});
  }

  function renderResume(){
    const latest=read()[0];
    if(!latest)return;
    const banner=document.createElement('section');
    banner.className='resume-card';
    banner.setAttribute('aria-label','Son elektrik durumuna devam et');
    banner.innerHTML=`<div><span class="resume-kicker">Bu cihazdaki son kayıt</span><h2>${labels[latest.event]||'Elektrik olayı'} · ${labels[latest.scope]||''}</h2><p>${humanDate(latest.createdAt)} · ${latest.title}</p></div><div class="resume-actions"><button type="button" data-resume>Kayda devam et</button><button type="button" class="ghost" data-new>Yeni durum başlat</button></div>`;
    form.before(banner);
    banner.querySelector('[data-resume]').addEventListener('click',()=>applyRecord(latest,{showResult:true}));
    banner.querySelector('[data-new]').addEventListener('click',()=>{form.reset();result.hidden=true;save.disabled=true;last=null;setStep(0);banner.remove()});
  }

  function applyQueryIntent(){
    const params=new URLSearchParams(location.search);
    const event=params.get('event');
    const scope=params.get('scope');
    const repeat=params.get('repeat');
    if(allowedEvents.has(event)){
      const input=form.querySelector(`input[name="event"][value="${event}"]`);
      if(input)input.checked=true;
      currentStep=1;
    }
    if(allowedScopes.has(scope)){form.elements.scope.value=scope;currentStep=Math.max(currentStep,3)}
    if(allowedRepeats.has(repeat)){form.elements.repeat.value=repeat;currentStep=3}
    if(params.get('resume')==='1'){
      const latest=read()[0];
      if(latest)applyRecord(latest,{showResult:true});
    }
  }

  form.addEventListener('submit',event=>{
    event.preventDefault();
    const data=currentData();
    if(!data.event||!data.scope||!data.repeat){
      feedback.textContent='Dört adımı da tamamlayın.';
      feedback.hidden=false;
      const missing=!data.event?0:!data.scope?2:3;
      setStep(missing);
      return;
    }
    showOutcome(data);
  });
  save.addEventListener('click',()=>{if(!last)return;write([last,...read()].slice(0,6));renderRecords();save.textContent='Cihazda saklandı';setTimeout(()=>save.textContent='Sonucu cihazda sakla',1400)});
  exportBtn.addEventListener('click',()=>{const blob=new Blob([JSON.stringify({exportedAt:new Date().toISOString(),records:read()},null,2)],{type:'application/json'});const anchor=document.createElement('a');anchor.href=URL.createObjectURL(blob);anchor.download='alo186-elektrik-durum-kayitlari.json';anchor.click();URL.revokeObjectURL(anchor.href)});
  clear.addEventListener('click',()=>{localStorage.removeItem(key);renderRecords();document.querySelector('.resume-card')?.remove()});

  const mobileDock=document.createElement('nav');
  mobileDock.className='mobile-dock';
  mobileDock.setAttribute('aria-label','Hızlı erişim');
  mobileDock.innerHTML='<a aria-current="page" href="/elektrik-durum-merkezi">Durum</a><a href="/edas-bul">EDAŞ</a><a href="/hesaplama/elektrik-planim/">Planım</a>';
  document.body.appendChild(mobileDock);

  renderRecords();
  renderResume();
  applyQueryIntent();
  setStep(currentStep,{focus:false});
})();
