const $=id=>document.getElementById(id);
const storageKey='alo186_modem_backup_v1';

function numberValue(id){
  const value=Number($(id).value);
  if(!Number.isFinite(value))throw new Error('Lütfen tüm sayısal alanları kontrol edin.');
  return value;
}

function readInputs(){
  const connection=$('connection').value;
  const modemW=numberValue('modemW'),modemV=numberValue('modemV');
  const ontW=connection==='dsl'?0:numberValue('ontW');
  const ontV=numberValue('ontV'),hours=numberValue('hours');
  const efficiency=numberValue('efficiency')/100,reserve=numberValue('reserve')/100;
  if(modemW<=0||modemV<=0||ontW<0||ontV<=0||hours<=0)throw new Error('Güç, voltaj ve süre değerleri geçerli olmalıdır.');
  if(efficiency<.6||efficiency>1)throw new Error('Verim %60 ile %100 arasında olmalıdır.');
  if(reserve<0||reserve>.6)throw new Error('Rezerv %0 ile %60 arasında olmalıdır.');
  return {connection,modemW,modemV,ontW,ontV,hours,efficiency,reserve};
}

function saveCalculation(data){
  try{localStorage.setItem(storageKey,JSON.stringify({...data,savedAt:new Date().toISOString()}));$('restoreBtn').classList.remove('hidden');}
  catch(e){/* Hesap cihazda çalışmaya devam eder; depolama zorunlu değildir. */}
}

function restoreCalculation(){
  try{
    const raw=localStorage.getItem(storageKey);if(!raw)return;
    const data=JSON.parse(raw);
    ['modemW','modemV','ontW','ontV','hours'].forEach(id=>{if(data[id]!=null)$(id).value=data[id]});
    if(data.efficiency!=null)$('efficiency').value=Math.round(data.efficiency*100);
    if(data.reserve!=null)$('reserve').value=Math.round(data.reserve*100);
    if(data.connection)$('connection').value=data.connection;
    Alo186Track('modem_backup_restored',{connection:data.connection||'unknown'});
    calculate(false);
  }catch(e){localStorage.removeItem(storageKey);$('restoreBtn').classList.add('hidden');}
}

function calculate(track=true){
  $('validation').textContent='';
  try{
    const data=readInputs();
    const totalW=data.modemW+data.ontW;
    const requiredWh=totalW*data.hours/data.efficiency*(1+data.reserve);
    const modemA=data.modemW/data.modemV*1.25;
    const ontA=data.ontW>0?data.ontW/data.ontV*1.25:0;
    const differentVoltages=data.ontW>0&&Math.abs(data.modemV-data.ontV)>.05;
    const outputLabel=data.ontW===0?'Tek çıkış':differentVoltages?'Çoklu çıkış':'Ortak voltaj';
    const outputNote=data.ontW===0?`${fmt(data.modemV,1,'V')} modem çıkışı`:differentVoltages?`${fmt(data.modemV,1,'V')} + ${fmt(data.ontV,1,'V')} ayrı çıkış`:`${fmt(data.modemV,1,'V')} uyumlu iki çıkış`;

    $('rLoad').textContent=fmt(totalW,0,'W');
    $('rHours').textContent=fmt(data.hours,1,'saat');
    $('rWh').textContent=fmt(requiredWh,0,'Wh');
    $('rOutput').textContent=outputLabel;
    $('rOutputNote').textContent=outputNote;

    const lines=[
      `Modem çıkışı: ${fmt(data.modemV,1,'V')} ve en az ${fmt(modemA,2,'A')}.`,
      data.ontW>0?`ONT çıkışı: ${fmt(data.ontV,1,'V')} ve en az ${fmt(ontA,2,'A')}.`:'ONT yükü hesaba katılmadı.',
      `Hedef için yaklaşık nominal enerji: en az ${fmt(requiredWh,0,'Wh')}.`,
      `Ürünün sürekli çıkış gücü ${fmt(totalW*1.25,0,'W')} değerinin altında olmamalı.`,
      differentVoltages?'Cihazlar farklı voltaj kullanıyor; tek sabit çıkışlı ürün uygun değildir.':'Jak ölçüsü ve merkez polaritesi ayrıca doğrulanmalıdır.'
    ];
    $('summaryList').innerHTML='';
    lines.forEach(text=>{const li=document.createElement('li');li.textContent=text;$('summaryList').appendChild(li)});

    const compact=requiredWh<=200&&totalW<=50;
    const link=$('productLink');
    link.href=compact?'https://www.alo186.com/amazon-elektrik-urunleri?from=modem-calculator&plan=bilgisayar-modem':'https://www.alo186.com/amazon-elektrik-urunleri?from=modem-calculator&plan=temel-kesinti';
    link.textContent=compact?'Mini UPS seçim merkezini aç':'Yedek enerji seçim merkezini aç';
    link.dataset.plan=compact?'bilgisayar-modem':'temel-kesinti';

    const summary=`ALO186 modem yedekleme özeti\nToplam yük: ${fmt(totalW,0,'W')}\nHedef süre: ${fmt(data.hours,1,'saat')}\nGerekli nominal enerji: ${fmt(requiredWh,0,'Wh')}\nModem: ${fmt(data.modemV,1,'V')} / en az ${fmt(modemA,2,'A')}${data.ontW>0?`\nONT: ${fmt(data.ontV,1,'V')} / en az ${fmt(ontA,2,'A')}`:''}\nVoltaj, akım, jak ve polarite üretici sayfasından doğrulanmalıdır.`;
    $('copyBtn').onclick=()=>copyText(summary,$('copyBtn'));
    $('results').classList.remove('hidden');$('results').scrollIntoView({behavior:'smooth',block:'start'});
    saveCalculation(data);
    if(track)Alo186Track('modem_backup_calculated',{connection:data.connection,total_w:Math.round(totalW),target_hours:data.hours,required_wh:Math.round(requiredWh),different_voltages:differentVoltages});
  }catch(err){$('validation').textContent=err.message;}
}

$('calcBtn').addEventListener('click',()=>calculate(true));
$('clearBtn').addEventListener('click',()=>{document.querySelector('form')?.reset();location.reload();});
$('restoreBtn').addEventListener('click',restoreCalculation);
$('productLink').addEventListener('click',()=>Alo186Track('modem_product_route_opened',{plan:$('productLink').dataset.plan||'unknown'}));
try{if(localStorage.getItem(storageKey))$('restoreBtn').classList.remove('hidden');}catch(e){}
