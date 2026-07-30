'use strict';
(() => {
  const form=document.getElementById('status-form');
  const result=document.getElementById('result');
  const save=document.getElementById('save');
  const exportBtn=document.getElementById('export');
  const clear=document.getElementById('clear');
  const list=document.getElementById('record-list');
  const key='alo186.electricStatus.v1';
  const ttl=30*24*60*60*1000;
  let last=null;

  const labels={outage:'Tam kesinti',voltage:'Gerilim olayı',meter:'Sayaç/şebeke ekipmanı',panel:'İç tesisat',damage:'Cihaz hasarı',backup:'Yedek güç',device:'Tek cihaz/priz',home:'Daire/villa',building:'Bina/site',area:'Sokak/mahalle',business:'İşletme'};
  const read=()=>{try{return JSON.parse(localStorage.getItem(key)||'[]').filter(x=>Date.now()-x.createdAt<ttl).slice(0,6)}catch{return[]}};
  const write=x=>localStorage.setItem(key,JSON.stringify(x.slice(0,6)));
  const route=(href,title,text)=>`<a class="route" href="${href}"><b>${title}</b>${text}</a>`;
  const renderRecords=()=>{const items=read();write(items);list.innerHTML=items.length?items.map(x=>`<div class="record-item"><b>${new Date(x.createdAt).toLocaleString('tr-TR')}</b> · ${labels[x.event]||x.event} · ${labels[x.scope]||x.scope}<br>${x.title}</div>`).join(''):'<p>Henüz cihazda saklanan kayıt yok.</p>'};

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

  form.addEventListener('submit',e=>{
    e.preventDefault();
    const fd=new FormData(form);const event=fd.get('event'),scope=fd.get('scope'),repeat=fd.get('repeat');
    if(!event||!scope||!repeat){result.hidden=false;result.className='result warning';result.innerHTML='<h2>Eksik seçim var</h2><p>Dört adımı da tamamlayın.</p>';return}
    const data={event,scope,repeat,hazards:fd.getAll('hazard')};const outcome=evaluate(data);last={...data,...outcome,createdAt:Date.now()};
    result.hidden=false;result.className=`result ${outcome.level}`;result.innerHTML=`<h2>${outcome.title}</h2><p>${outcome.summary}</p><ol class="checklist">${outcome.steps.map(x=>`<li>${x}</li>`).join('')}</ol><div class="route-grid">${outcome.routes.join('')}</div>`;save.disabled=false;result.scrollIntoView({behavior:'smooth',block:'start'});
  });
  save.addEventListener('click',()=>{if(!last)return;write([last,...read()].slice(0,6));renderRecords();save.textContent='Cihazda saklandı';setTimeout(()=>save.textContent='Sonucu cihazda sakla',1400)});
  exportBtn.addEventListener('click',()=>{const blob=new Blob([JSON.stringify({exportedAt:new Date().toISOString(),records:read()},null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='alo186-elektrik-durum-kayitlari.json';a.click();URL.revokeObjectURL(a.href)});
  clear.addEventListener('click',()=>{localStorage.removeItem(key);renderRecords()});
  renderRecords();
})();