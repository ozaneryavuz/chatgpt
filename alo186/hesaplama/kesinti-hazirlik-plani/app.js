(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document)api.mount(root.document,root);
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const STORAGE_KEY='alo186_outage_plan_v3';
  const STORAGE_DAYS=180;
  const PROFILE_NAMES={home:'Ev',site:'Apartman / site',business:'Küçük işletme',hotel:'Otel / tesis'};
  const ROUTES={
    official:{label:'Resmî kesinti kanalını bul',href:'https://alo186.com/elektrik-kesintisi',note:'Yetkili EDAŞ, 186 ve planlı kesinti ekranı.'},
    emergency:{label:'112 / 186 / 187 ayrımını kontrol et',href:'https://alo186.com/acil-numaralar',note:'Can güvenliği, elektrik ve doğal gaz acil kanalları.'},
    modem:{label:'Modem ve ONT yedekleme uygunluğu',href:'https://alo186.com/hesaplama/modem-internet-yedekleme/',note:'Voltaj, akım, jak, polarite, W ve Wh.'},
    cpap:{label:'CPAP / APAP / BiPAP yedek güç testi',href:'https://alo186.com/hesaplama/cpap-bipap-yedek-guc-sure-uygunluk/',note:'Yalnız reçeteli uyku tedavisi cihazı; yaşam destekte profesyonel plan.'},
    cold:{label:'Buzdolabı ve dondurucu kesinti güvenliği',href:'https://alo186.com/hesaplama/buzdolabi-dondurucu-kesinti-guvenligi/',note:'Süre, sıcaklık, kapı ve buz kristali kanıtı.'},
    coldPower:{label:'Buzdolabı yedek güç uygunluğu',href:'https://alo186.com/hesaplama/buzdolabi-dondurucu-yedek-guc-uygunluk/',note:'Kompresör sürekli W, kalkış W ve Wh.'},
    heating:{label:'Kombi yedek güç uygunluğu',href:'https://alo186.com/hesaplama/kombi-elektrik-kesintisi-yedek-guc-uygunluk/',note:'Gaz, arıza kodu, saf sinüs, W ve Wh ayrımı.'},
    aquarium:{label:'Akvaryum kesinti yedek güç planı',href:'https://alo186.com/hesaplama/akvaryum-kesinti-yedek-guc-uygunluk/',note:'Hava, filtre, sirkülasyon, ısıtıcı ve canlı güvenliği.'},
    security:{label:'Kamera, NVR ve PoE yedek güç hesabı',href:'https://alo186.com/hesaplama/kamera-nvr-poe-yedek-guc-uygunluk/',note:'Gece IR, kayıt cihazı, PoE bütçesi ve Wh.'},
    remoteWork:{label:'Evden çalışma yedek güç seti',href:'https://alo186.com/hesaplama/evden-calisma-laptop-modem-yedek-guc-seti/',note:'Laptop, modem/ONT, monitör ve yalnız eksik bileşenler.'},
    lighting:{label:'Acil aydınlatma süre uygunluğu',href:'https://alo186.com/hesaplama/acil-aydinlatma-sure-uygunluk/',note:'Lümen, süre, otomatik yanma ve gerçek test.'},
    phone:{label:'Powerbank ve USB-C uygunluğu',href:'https://alo186.com/hesaplama/powerbank-usb-c-uygunluk/',note:'Wh, USB-C PD, kablo ve gerçek şarj sayısı.'},
    source:{label:'Yedek güç çözüm seçici',href:'https://alo186.com/hesaplama/yedek-guc-cozum-secici/',note:'UPS, power station, inverter veya jeneratör sınıfı.'},
    generator:{label:'Jeneratör gücü ön seçimi',href:'https://alo186.com/hesaplama/jenerator-gucu-secimi/',note:'Sürekli W, motor kalkışı, kVA ve profesyonel sınır.'},
    log:{label:'Kesinti günlüğü ve hak ön kontrolü',href:'https://alo186.com/hesaplama/kesinti-gunlugu/',note:'Gerçek tarih, süre, kayıt numarası ve tekrar sıklığı.'},
    continuity:{label:'Elektrik sürekliliği olgunluk skoru',href:'https://alo186.com/hesaplama/elektrik-surekliligi-olgunluk-skoru/',note:'Site, işletme ve otel için 30/60/90 günlük plan.'}
  };
  const bool=(v)=>v===true||v==='true';
  function unique(items){return [...new Set(items)];}
  function buildPlan(input={}){
    const flags=input.flags||{},ready=input.ready||{},duration=Number(input.duration)||2,profile=input.profile||'home',activeOutage=input.activeOutage==='yes';
    const tasks=[
      'Yetkili EDAŞ’ın planlı kesinti ekranını ve 186 bilgisini doğrulayın.',
      'Kesinti başlangıç ve dönüş saatini kaydedin; üçüncü taraf kesin dönüş tahminine güvenmeyin.',
      'Telefon ve acil aydınlatmayı önceden şarj edin ve gerçek süre testini yapın.',
      'Hassas elektronik cihazları güvenli biçimde kapatın; enerji geri geldiğinde kademeli devreye alın.'
    ];
    const routes=['official','log'];
    const gaps=[];
    if(!ready.officialReady)gaps.push('resmî kesinti kanalı');
    if(!ready.phoneReady){gaps.push('telefon şarj hazırlığı');routes.push('phone');}
    if(!ready.lightingReady){gaps.push('acil aydınlatma testi');routes.push('lighting');}
    if(flags.internet){tasks.push('Modem ve varsa fiber ONT için voltaj, akım, jak, polarite ve gerçek çalışma süresini doğrulayın.');routes.push('modem');}
    if(flags.medical){tasks.unshift('CPAP/APAP/BiPAP için sağlık profesyoneli kesinti planını ve tam model üretici uyumluluğunu doğrulayın; ventilatör ve oksijen cihazında tüketici ürün yolunu kullanmayın.');routes.push('emergency','cpap');}
    if(flags.cold){tasks.push('Buzdolabı/dondurucu kapaklarını gereksiz açmayın; sıcaklık ve kesinti süresi kaydı tutun.');routes.push('cold','coldPower');if(!ready.coldEvidence)gaps.push('soğuk zincir termometresi ve kapı planı');}
    if(flags.heating){tasks.push('Kombi için gaz kokusu, arıza kodu ve üretici haricî kaynak koşulunu yedek güç ihtiyacından ayırın.');routes.push('heating','emergency');}
    if(flags.aquarium){tasks.unshift('Akvaryumda önce oksijenlenme ve sirkülasyon yükünü koruyun; türe, sıcaklığa ve sistem hacmine göre profesyonel plan sınırını değerlendirin.');routes.push('aquarium');}
    if(flags.security){tasks.push('Kamera, NVR/DVR, PoE switch, modem ve gece IR yükünün tamamını aynı güç bütçesine dahil edin.');routes.push('security');}
    if(flags.generator){tasks.push('Jeneratörü bina içinde veya açıklık yakınında kullanmayın; doğrudan bina prizine geri beslemeyin ve transfer düzenini yetkili uzmana doğrulatın.');routes.push('generator','emergency');}
    if(flags.pump)tasks.push('Hidrofor/pompa için kuru çalışma, motor kalkışı, seviye kontrolü ve otomatik yeniden başlama riskini doğrulayın.');
    if(flags.elevator)tasks.unshift('Asansör kullanıcılarını bilgilendirin; kurtarma ve erişilebilirlik prosedürünü hazır tutun.');
    if(input.context==='remote-work'){tasks.push('Laptop bataryası, modem/ONT, monitör ve alternatif mobil bağlantıyı birlikte test edin.');routes.push('remoteWork');}
    if(input.context==='seasonal')tasks.push('Uzun süre kullanılmayan batarya, UPS, powerbank ve şarjlı ekipmanların kapasite ve tarih kontrolünü yapın.');
    if(input.context==='busy')tasks.push('Yoğun dönem öncesinde sorumlu kişilerle kısa bir kesinti tatbikatı yapın ve eksikleri kaydedin.');
    if(['site','business','hotel'].includes(profile)||flags.pump||flags.elevator){tasks.push('Kritik yükleri, sorumluları ve devreye alma sırasını yazılı prosedüre bağlayın.');routes.push('continuity');}
    if(profile==='hotel')tasks.push('Resepsiyon, mutfak/soğuk oda, yangın sistemi, asansör, hidrofor, ağ ve oda operasyonlarını ayrı sorumlularla doğrulayın.');
    const selectedCritical=Object.values(flags).filter(bool).length;
    if(selectedCritical>0&&!ready.sourceReady){gaps.push('kritik yükler için gerçek kesinti testi');routes.push('source');}
    const checks=[ready.officialReady,ready.phoneReady,ready.lightingReady,selectedCritical===0||ready.sourceReady,!flags.cold||ready.coldEvidence];
    const score=Math.round(checks.filter(bool).length/checks.length*100);
    let status='gap',title='Hazırlıkta doğrulanması gereken açıklar var',summary=`Eksik kanıtlar: ${unique(gaps).join(', ')||'seçilen kritik ihtiyaçların ayrıntılı uygunluk testi'}. Önce ücretsiz teknik aracı tamamlayın; doğrudan ürün aramayın.`;
    if(activeOutage){status='active_outage';title='Aktif kesintide ürün teslimatını çözüm saymayın';summary='Can güvenliği, resmî kesinti kanalı, mevcut güvenli ekipman ve önceden hazırlanmış prosedür önceliklidir. Bu planda ve yönlendirme listesinde mağaza bağlantısı bulunmaz.';}
    else if((profile==='business'||profile==='hotel'||profile==='site')&&(flags.generator||flags.pump||flags.elevator)){status='professional';title='Çoklu kritik yük için profesyonel süreklilik planı gerekir';summary='Jeneratör transferi, hidrofor, asansör ve ortak alan yükleri yalnız ürün seçimiyle yönetilmez; yük listesi, seçicilik, bakım, test ve görev sahipliği birlikte tasarlanmalıdır.';}
    else if(gaps.length===0){status='ready';title='Mevcut hazırlık yeterli; yeni ürün aramayın';summary='Resmî kanal, telefon, aydınlatma, seçilen kritik yükler ve soğuk zincir kanıtları hazır. Yalnız periyodik gerçek testi ve kayıt disiplinini sürdürün.';}
    return {status,title,summary,score,priority:(flags.medical||flags.elevator||flags.aquarium||duration>=12)?'Yüksek':(duration>=6||flags.generator||flags.pump||flags.cold)?'Orta–yüksek':'Standart',tasks:unique(tasks),routes:unique(routes).map((key)=>({key,...ROUTES[key]})),gaps:unique(gaps),commercialAllowed:false,affiliateLinks:0};
  }
  function stamp(date){return date.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z');}
  function download(doc,filename,text,type){const blob=new Blob([text],{type});const url=URL.createObjectURL(blob);const link=doc.createElement('a');link.href=url;link.download=filename;link.click();setTimeout(()=>URL.revokeObjectURL(url),0);}
  function mount(doc,win){
    const $=(id)=>doc.getElementById(id);if(!$('generateBtn'))return;
    let last=null;
    const read=()=>({activeOutage:$('activeOutage').value,profile:$('profile').value,duration:$('duration').value,context:$('context').value,reviewCycle:$('reviewCycle').value,flags:{internet:$('internet').checked,medical:$('medical').checked,cold:$('cold').checked,heating:$('heating').checked,aquarium:$('aquarium').checked,security:$('security').checked,pump:$('pump').checked,generator:$('generator').checked,elevator:$('elevator').checked},ready:{officialReady:$('officialReady').checked,phoneReady:$('phoneReady').checked,lightingReady:$('lightingReady').checked,sourceReady:$('sourceReady').checked,coldEvidence:$('coldEvidence').checked}});
    function renderTasks(tasks){$('taskList').innerHTML='';tasks.forEach((text,i)=>{const label=doc.createElement('label');label.className='check-item';const input=doc.createElement('input');input.type='checkbox';input.dataset.task=String(i);input.addEventListener('change',updateProgress);const span=doc.createElement('span');span.textContent=text;label.append(input,span);$('taskList').appendChild(label);});updateProgress();}
    function updateProgress(){const all=[...doc.querySelectorAll('[data-task]')],done=all.filter((x)=>x.checked).length,p=all.length?Math.round(done/all.length*100):0;$('bar').style.width=p+'%';}
    function renderRoutes(routes){$('routeLinks').innerHTML='';routes.forEach((route)=>{const link=doc.createElement('a');link.className='route-card';link.href=route.href;link.innerHTML=`<b>${route.label} →</b><small>${route.note}</small>`;$('routeLinks').appendChild(link);});}
    function dueDate(days){const date=new Date();date.setDate(date.getDate()+Number(days||90));return date;}
    function render(result,input){last={generatedAt:new Date().toISOString(),input,result,personalDataCollected:false};$('rProfile').textContent=PROFILE_NAMES[input.profile]||input.profile;$('rDuration').textContent=$('duration').selectedOptions[0].text;$('rScore').textContent=result.score+'/100';$('rScoreText').textContent=result.gaps.length?`${result.gaps.length} kanıt açığı`:'Satın alma gerektirmeyen hazır plan';$('rPriority').textContent=result.priority;$('rReview').textContent=dueDate(input.reviewCycle).toLocaleDateString('tr-TR');$('statusCard').dataset.status=result.status;$('statusTitle').textContent=result.title;$('statusSummary').textContent=result.summary;renderTasks(result.tasks);renderRoutes(result.routes);$('reviewStatus').textContent='Plan doğrudan affiliate bağlantısı içermez; JSON ve takvim dosyaları kişisel veri içermez.';$('results').classList.remove('hidden');$('results').focus();}
    function generate(){const input=read();render(buildPlan(input),input);}
    function save(){if(!last)return;try{const saved={...last,expiresAt:new Date(Date.now()+STORAGE_DAYS*86400000).toISOString()};win.localStorage.setItem(STORAGE_KEY,JSON.stringify(saved));$('rSaved').textContent='180 gün; ziyaretle uzamaz';$('reviewStatus').textContent=`Bu cihazdaki kayıt ${new Date(saved.expiresAt).toLocaleDateString('tr-TR')} tarihinde sona erer.`;}catch(e){$('reviewStatus').textContent='Tarayıcı depolamasına erişilemedi; JSON veya ICS dışa aktarımını kullanın.';}}
    function load(){let raw=null;try{raw=win.localStorage.getItem(STORAGE_KEY);}catch(e){}if(!raw){win.alert('Bu cihazda geçerli kayıtlı plan bulunamadı.');return;}try{const saved=JSON.parse(raw);if(!saved.expiresAt||new Date(saved.expiresAt)<=new Date()){win.localStorage.removeItem(STORAGE_KEY);win.alert('Kayıt süresi dolmuş. Yeni plan oluşturun.');return;}const input=saved.input||{};$('activeOutage').value=input.activeOutage||'no';$('profile').value=input.profile||'home';$('duration').value=input.duration||'2';$('context').value=input.context||'standard';$('reviewCycle').value=input.reviewCycle||'90';Object.entries(input.flags||{}).forEach(([k,v])=>{if($(k))$(k).checked=Boolean(v);});Object.entries(input.ready||{}).forEach(([k,v])=>{if($(k))$(k).checked=Boolean(v);});render(saved.result||buildPlan(input),input);$('rSaved').textContent=`${new Date(saved.expiresAt).toLocaleDateString('tr-TR')} tarihine kadar`;}catch(e){win.alert('Kayıt okunamadı. Yeni plan oluşturun.');}}
    $('generateBtn').addEventListener('click',generate);$('saveBtn').addEventListener('click',save);$('loadBtn').addEventListener('click',load);
    $('jsonBtn').addEventListener('click',()=>{if(!last)return;download(doc,'alo186-kesinti-hazirlik-plani.json',JSON.stringify(last,null,2),'application/json');});
    $('icsBtn').addEventListener('click',()=>{if(!last)return;const due=dueDate(last.input.reviewCycle);const now=new Date();const ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Kesinti Hazirlik Plani//TR','BEGIN:VEVENT',`UID:alo186-outage-plan-${Date.now()}@alo186.com`,`DTSTAMP:${stamp(now)}`,`DTSTART:${stamp(due)}`,'SUMMARY:ALO186 elektrik kesintisi hazırlık planını yeniden test et','DESCRIPTION:Resmî kesinti kanalı, telefon ve acil aydınlatma, kritik yük yedek kaynağı, soğuk zincir kanıtı ve gerçek kesinti testini yeniden doğrula. Fiyat veya kampanya kontrolü değildir.','END:VEVENT','END:VCALENDAR'].join('\r\n');download(doc,'alo186-kesinti-hazirlik-kontrolu.ics',ics,'text/calendar;charset=utf-8');});
  }
  return {buildPlan,mount,ROUTES,STORAGE_KEY,STORAGE_DAYS};
});
