const $=id=>document.getElementById(id);
const storageKey='alo186_outage_plan';
const profileNames={home:'Ev',site:'Apartman / site',business:'Küçük işletme',hotel:'Otel / tesis'};

function buildTasks(){
  const p=$('profile').value,d=Number($('duration').value),people=Math.max(1,Number($('people').value)||1),tasks=[
    'Yetkili EDAŞ’ın planlı kesinti ekranını kontrol et ve 186 bilgisini hazır tut.',
    'Telefon, powerbank ve şarjlı aydınlatmaları şarj et.',
    'Hassas elektronik cihazları güvenli biçimde kapat; enerji geri geldiğinde kademeli devreye al.',
    'Buzdolabı ve dondurucu kapaklarını gereksiz açma.',
    'Kesinti başlangıç ve dönüş saatini kaydet.'
  ];
  if($('internet').checked)tasks.push('Modem/ONT/POS için yedek güç ve tahmini çalışma süresini kontrol et.');
  if($('medical').checked)tasks.unshift('Tıbbi cihaz için üretici acil planını uygula; yedek güç ve sağlık desteğini önceden hazırla. Tüketici tipi ürün önerisine güvenme.');
  if($('cold').checked&&d>=6)tasks.push('Soğuk zincir sıcaklığını takip et; gıda güvenliği için süre ve sıcaklık kaydı tut.');
  if($('pump').checked)tasks.push('Su deposu/hidrofor durumunu kontrol et; kuru çalışma ve otomatik tekrar devreye girme riskini değerlendir.');
  if($('security').checked)tasks.push('Kamera, alarm ve geçiş sistemlerinin UPS çalışma süresini doğrula.');
  if($('generator').checked)tasks.push('Jeneratör yakıtı, yağ/su seviyesi, otomatik transfer ve test kaydını yetkili prosedüre göre kontrol et.');
  if($('elevator').checked)tasks.unshift('Asansör kullanıcılarını bilgilendir; kurtarma ve erişilebilirlik prosedürünü hazırla.');
  if(p==='site')tasks.push('Bina sakinlerine kesinti ve ortak alan durumu hakkında tek kanaldan bilgi ver.');
  if(p==='business'||p==='hotel')tasks.push('Kritik yükler, sorumlular ve jeneratör/UPS devreye alma görevlerini vardiya bazında ata.');
  if(p==='hotel')tasks.push('Resepsiyon, mutfak, soğuk oda, asansör, hidrofor ve yangın sistemlerini ayrı ayrı kontrol et.');
  if(people>=10)tasks.push('Kullanıcı sayısına uygun el feneri, iletişim ve sorumlu kişi dağılımını doğrula.');
  if($('context').value==='remote-work')tasks.push('Çevrim içi çalışma için modem/ONT, bilgisayar güvenli kapanışı ve alternatif mobil bağlantı planını test et.');
  if($('context').value==='seasonal')tasks.push('Uzun süre kullanılmayan batarya, UPS ve şarjlı ekipmanların kapasite ve tarih kontrolünü yap.');
  if($('context').value==='busy')tasks.push('Yoğun dönem öncesinde sorumlu kişilerle kısa bir kesinti tatbikatı yap ve eksikleri kaydet.');
  return [...new Set(tasks)];
}

function render(tasks,checked=[]){
  $('taskList').innerHTML='';
  tasks.forEach((text,i)=>{
    const label=document.createElement('label');label.className='check-item';
    const input=document.createElement('input');input.type='checkbox';input.dataset.task=String(i);input.checked=checked.includes(i);input.addEventListener('change',updateProgress);
    const span=document.createElement('span');span.textContent=text;
    label.append(input,span);$('taskList').appendChild(label);
  });
  updateProgress();
}

function updateProgress(){
  const all=[...document.querySelectorAll('[data-task]')],done=all.filter(x=>x.checked).length,p=all.length?Math.round(done/all.length*100):0;
  $('rProgress').textContent=p+'%';$('bar').style.width=p+'%';
}

function priority(){
  const high=$('medical').checked||$('elevator').checked||($('profile').value==='hotel'&&Number($('duration').value)>=6);
  return high?'Yüksek':Number($('duration').value)>=6||$('generator').checked||$('pump').checked?'Orta–yüksek':'Standart';
}

function addRoute(container,label,href,eventName){
  const link=document.createElement('a');link.className='btn btn-secondary';link.href=href;link.textContent=label;
  link.addEventListener('click',()=>Alo186Track('outage_plan_route_opened',{route:eventName}));container.appendChild(link);
}

function renderRoutes(){
  const container=$('routeLinks');container.innerHTML='';
  addRoute(container,'Resmî kesinti kanalını bul','https://www.alo186.com/elektrik-kesintisi','official-outage');
  if($('internet').checked)addRoute(container,'Modem ve ONT yedekleme hesabı','https://www.alo186.com/hesaplama/modem-internet-yedekleme/','modem-backup');
  if($('cold').checked||$('security').checked)addRoute(container,'UPS çalışma süresini hesapla','https://www.alo186.com/hesaplama/ups-suresi/','ups-runtime');
  if($('generator').checked||$('pump').checked||$('elevator').checked||['site','business','hotel'].includes($('profile').value))addRoute(container,'Süreklilik panelini aç','https://www.alo186.com/sureklilik-paneli/','continuity-panel');
}

function showPlan(tasks,checked=[]){
  render(tasks,checked);$('rProfile').textContent=profileNames[$('profile').value];$('rDuration').textContent=$('duration').selectedOptions[0].text;
  $('rPriority').textContent=priority();renderRoutes();$('results').classList.remove('hidden');$('results').scrollIntoView({behavior:'smooth'});
}

function nextReviewDate(fromIso,cycleDays){
  const date=new Date(fromIso);date.setDate(date.getDate()+Number(cycleDays||90));return date;
}

function setReviewDisplay(reviewedAt,cycleDays){
  if(!reviewedAt){$('rReview').textContent='Kaydedilmedi';$('rSaved').textContent='Bu cihazda saklanabilir';$('reviewStatus').textContent='Planı kaydettiğinizde bir sonraki kontrol tarihi bu cihazda tutulur.';return;}
  const due=nextReviewDate(reviewedAt,cycleDays),now=new Date(),isDue=due<=now;
  $('rReview').textContent=isDue?'Kontrol zamanı':due.toLocaleDateString('tr-TR');
  $('rSaved').textContent='Yalnız bu cihazda';
  $('reviewStatus').textContent=isDue?`Planın son kontrolü ${new Date(reviewedAt).toLocaleDateString('tr-TR')} tarihinde yapıldı. Ekipman, pil ve görev durumlarını yeniden doğrulayın.`:`Son kontrol ${new Date(reviewedAt).toLocaleDateString('tr-TR')}; sonraki kontrol ${due.toLocaleDateString('tr-TR')}.`;
  $('reviewStatus').className=isDue?'warning':'info';
}

function collectPlan(reviewedAt=new Date().toISOString()){
  return {
    version:2,
    profile:$('profile').value,
    duration:$('duration').value,
    people:$('people').value,
    context:$('context').value,
    reviewCycle:$('reviewCycle').value,
    flags:['internet','medical','cold','pump','security','generator','elevator'].reduce((a,k)=>(a[k]=$(k).checked,a),{}),
    tasks:[...document.querySelectorAll('[data-task]')].map(x=>x.parentElement.querySelector('span').textContent),
    checked:[...document.querySelectorAll('[data-task]')].filter(x=>x.checked).map(x=>Number(x.dataset.task)),
    reviewedAt
  };
}

function savePlan(eventName){
  try{
    const data=collectPlan();localStorage.setItem(storageKey,JSON.stringify(data));setReviewDisplay(data.reviewedAt,data.reviewCycle);
    Alo186Track(eventName,{profile:data.profile,review_cycle_days:Number(data.reviewCycle),task_count:data.tasks.length});
  }catch(e){$('reviewStatus').textContent='Tarayıcı depolamasına erişilemedi. Planı PDF olarak kaydedebilirsiniz.';$('reviewStatus').className='warning';}
}

$('generateBtn').addEventListener('click',()=>{
  const tasks=buildTasks();showPlan(tasks);setReviewDisplay(null,$('reviewCycle').value);
  Alo186Track('outage_plan_generated',{profile:$('profile').value,duration:Number($('duration').value),task_count:tasks.length,context:$('context').value});
});

$('saveBtn').addEventListener('click',()=>savePlan('outage_plan_saved'));
$('reviewBtn').addEventListener('click',()=>savePlan('outage_plan_reviewed'));

$('loadBtn').addEventListener('click',()=>{
  let raw;try{raw=localStorage.getItem(storageKey);}catch(e){}
  if(!raw){alert('Bu cihazda kayıtlı plan bulunamadı.');return;}
  try{
    const d=JSON.parse(raw);$('profile').value=d.profile||'home';$('duration').value=d.duration||'2';$('people').value=d.people||3;
    $('context').value=d.context||'standard';$('reviewCycle').value=d.reviewCycle||'90';
    Object.entries(d.flags||{}).forEach(([k,v])=>{if($(k))$(k).checked=v});
    showPlan(Array.isArray(d.tasks)&&d.tasks.length?d.tasks:buildTasks(),d.checked||[]);setReviewDisplay(d.reviewedAt,d.reviewCycle||90);
    Alo186Track('outage_plan_loaded',{profile:d.profile||'home',review_due:d.reviewedAt?nextReviewDate(d.reviewedAt,d.reviewCycle||90)<=new Date():false});
  }catch(e){alert('Kayıtlı plan okunamadı. Yeni bir plan oluşturun.');}
});
