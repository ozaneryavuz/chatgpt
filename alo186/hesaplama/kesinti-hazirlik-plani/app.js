const $=id=>document.getElementById(id);
const profileNames={home:'Ev',site:'Apartman / site',business:'Küçük işletme',hotel:'Otel / tesis'};
function buildTasks(){
  const p=$('profile').value,d=Number($('duration').value),tasks=[
    'Yetkili EDAŞ’ın planlı kesinti ekranını kontrol et ve 186 bilgisini hazır tut.',
    'Telefon, powerbank ve şarjlı aydınlatmaları şarj et.',
    'Hassas elektronik cihazları güvenli biçimde kapat; enerji geri geldiğinde kademeli devreye al.',
    'Buzdolabı ve dondurucu kapaklarını gereksiz açma.',
    'Kesinti başlangıç ve dönüş saatini kaydet.'
  ];
  if($('internet').checked)tasks.push('Modem/ONT/POS için yedek güç ve tahmini çalışma süresini kontrol et.');
  if($('medical').checked)tasks.unshift('Tıbbi cihaz için üretici acil planını uygula; yedek güç ve sağlık desteğini önceden hazırla.');
  if($('cold').checked&&d>=6)tasks.push('Soğuk zincir sıcaklığını takip et; gıda güvenliği için süre ve sıcaklık kaydı tut.');
  if($('pump').checked)tasks.push('Su deposu/hidrofor durumunu kontrol et; kuru çalışma ve otomatik tekrar devreye girme riskini değerlendir.');
  if($('security').checked)tasks.push('Kamera, alarm ve geçiş sistemlerinin UPS çalışma süresini doğrula.');
  if($('generator').checked)tasks.push('Jeneratör yakıtı, yağ/su seviyesi, otomatik transfer ve test kaydını kontrol et.');
  if($('elevator').checked)tasks.unshift('Asansör kullanıcılarını bilgilendir; kurtarma ve erişilebilirlik prosedürünü hazırla.');
  if(p==='site')tasks.push('Bina sakinlerine kesinti ve ortak alan durumu hakkında tek kanaldan bilgi ver.');
  if(p==='business'||p==='hotel')tasks.push('Kritik yükler, sorumlular ve jeneratör/UPS devreye alma görevlerini vardiya bazında ata.');
  if(p==='hotel')tasks.push('Resepsiyon, mutfak, soğuk oda, asansör, hidrofor ve yangın sistemlerini ayrı ayrı kontrol et.');
  return tasks;
}
function render(tasks,checked=[]){
  $('taskList').innerHTML=tasks.map((t,i)=>`<label class="check-item"><input type="checkbox" data-task="${i}" ${checked.includes(i)?'checked':''}><span>${t}</span></label>`).join('');
  document.querySelectorAll('[data-task]').forEach(c=>c.addEventListener('change',updateProgress));updateProgress();
}
function updateProgress(){const all=[...document.querySelectorAll('[data-task]')],done=all.filter(x=>x.checked).length,p=all.length?Math.round(done/all.length*100):0;$('rProgress').textContent=p+'%';$('bar').style.width=p+'%';}
$('generateBtn').addEventListener('click',()=>{
  const tasks=buildTasks();render(tasks);$('rProfile').textContent=profileNames[$('profile').value];$('rDuration').textContent=$('duration').selectedOptions[0].text;
  const critical=$('medical').checked||$('elevator').checked||($('profile').value==='hotel'&&Number($('duration').value)>=6);
  $('rPriority').textContent=critical?'Yüksek':Number($('duration').value)>=6?'Orta–yüksek':'Standart';
  $('results').classList.remove('hidden');$('results').scrollIntoView({behavior:'smooth'});Alo186Track('outage_plan_generated',{profile:$('profile').value,duration:Number($('duration').value),task_count:tasks.length});
});
$('saveBtn').addEventListener('click',()=>{const data={profile:$('profile').value,duration:$('duration').value,people:$('people').value,note:$('note').value,flags:['internet','medical','cold','pump','security','generator','elevator'].reduce((a,k)=>(a[k]=$(k).checked,a),{}),tasks:buildTasks(),checked:[...document.querySelectorAll('[data-task]')].filter(x=>x.checked).map(x=>Number(x.dataset.task))};localStorage.setItem('alo186_outage_plan',JSON.stringify(data));$('rSaved').textContent='Kaydedildi';Alo186Track('outage_plan_saved',{profile:data.profile});});
$('loadBtn').addEventListener('click',()=>{const raw=localStorage.getItem('alo186_outage_plan');if(!raw){alert('Bu cihazda kayıtlı plan bulunamadı.');return;}const d=JSON.parse(raw);$('profile').value=d.profile;$('duration').value=d.duration;$('people').value=d.people;$('note').value=d.note||'';Object.entries(d.flags||{}).forEach(([k,v])=>{if($(k))$(k).checked=v});render(d.tasks||buildTasks(),d.checked||[]);$('rProfile').textContent=profileNames[d.profile];$('rDuration').textContent=$('duration').selectedOptions[0].text;$('rSaved').textContent='Kayıtlı plan';$('rPriority').textContent=(d.flags.medical||d.flags.elevator)?'Yüksek':'Standart';$('results').classList.remove('hidden');$('results').scrollIntoView({behavior:'smooth'});});
