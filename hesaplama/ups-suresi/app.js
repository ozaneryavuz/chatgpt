const $=id=>document.getElementById(id);
const mode=$('mode'),capacityField=$('capacityField'),hoursField=$('hoursField'),reserveField=$('reserveField');
const storageKey='alo186_ups_calculation_v1';

function syncMode(){
  const c=mode.value==='capacity';
  capacityField.classList.toggle('hidden',c);hoursField.classList.toggle('hidden',!c);reserveField.classList.toggle('hidden',!c);
}
mode.addEventListener('change',syncMode);

document.querySelectorAll('.preset').forEach(b=>b.addEventListener('click',()=>{
  $('loadW').value=b.dataset.w;
  $('surgeFactor').value=b.dataset.motor?'3':'1.2';
  Alo186Track('ups_preset_selected',{preset_w:Number(b.dataset.w),motor:Boolean(b.dataset.motor)});
}));

function readInputs(){
  const data={
    mode:mode.value,
    load:Number($('loadW').value),
    surgeFactor:Number($('surgeFactor').value),
    batteryWh:Number($('batteryWh').value),
    hours:Number($('hours').value),
    efficiency:Number($('efficiency').value)/100,
    dod:Number($('dod').value)/100,
    aging:Number($('aging').value)/100,
    reserve:Number($('reserve').value)/100
  };
  if(!Number.isFinite(data.load)||data.load<=0)throw new Error('Toplam yük 0 W değerinden büyük olmalıdır.');
  if(!Number.isFinite(data.surgeFactor)||data.surgeFactor<1||data.surgeFactor>8)throw new Error('Kalkış katsayısı 1 ile 8 arasında olmalıdır.');
  if(data.mode==='runtime'&&(!Number.isFinite(data.batteryWh)||data.batteryWh<=0))throw new Error('Nominal enerji kapasitesini kontrol edin.');
  if(data.mode==='capacity'&&(!Number.isFinite(data.hours)||data.hours<=0))throw new Error('Hedef çalışma süresini kontrol edin.');
  return data;
}

function saveCalculation(data){
  try{
    localStorage.setItem(storageKey,JSON.stringify({...data,savedAt:new Date().toISOString()}));
    $('restoreBtn').classList.remove('hidden');
  }catch(e){/* Depolama engellense bile hesap çalışır. */}
}

function restoreCalculation(){
  try{
    const raw=localStorage.getItem(storageKey);if(!raw)return;
    const data=JSON.parse(raw);
    mode.value=data.mode||'runtime';syncMode();
    $('loadW').value=data.load;$('surgeFactor').value=data.surgeFactor;
    $('batteryWh').value=data.batteryWh;$('hours').value=data.hours;
    $('efficiency').value=Math.round(data.efficiency*100);$('dod').value=Math.round(data.dod*100);
    $('aging').value=Math.round(data.aging*100);$('reserve').value=Math.round(data.reserve*100);
    Alo186Track('ups_calculation_restored',{mode:mode.value});
    calculate(false);
  }catch(e){
    localStorage.removeItem(storageKey);$('restoreBtn').classList.add('hidden');
  }
}

function configureProductRoute({load,surgeFactor,nominalWh,cls}){
  const route=$('productRoute'),link=$('productLink');
  const safeForConsumerRoute=load<=300&&surgeFactor<=1.5&&nominalWh<=2000&&!cls.includes('Profesyonel');
  route.classList.toggle('hidden',!safeForConsumerRoute);
  if(!safeForConsumerRoute)return;
  const compact=load<=75&&nominalWh<=600;
  const plan=compact?'bilgisayar-modem':'temel-kesinti';
  link.href=`https://alo186.com/amazon-elektrik-urunleri?from=ups-calculator&plan=${plan}`;
  link.dataset.plan=plan;
  link.textContent=compact?'Düşük güçlü UPS planını aç':'Yedek enerji seçim merkezini aç';
  $('productTitle').textContent=compact?'Modem, ağ cihazı ve küçük elektronikler için seçim planını açın.':'UPS ve taşınabilir güç seçeneklerini teknik ölçütlerle karşılaştırın.';
}

function calculate(track=true){
  $('validation').textContent='';
  try{
    const data=readInputs();
    const surge=data.load*data.surgeFactor;
    let primary,small,cls,lines=[],nominalWh;
    if(data.mode==='runtime'){
      const r=AloCalc.upsRuntime({loadW:data.load,batteryWh:data.batteryWh,efficiency:data.efficiency,usableDepth:data.dod,aging:data.aging});
      primary=fmt(r.runtimeHours,2,'saat');small='Yaklaşık '+fmt(r.runtimeHours*60,0,'dakika');nominalWh=data.batteryWh;
      lines=[`Kullanılabilir tahmini enerji: ${fmt(r.usableWh,0,'Wh')}`,`En az sürekli çıkış: ${fmt(data.load*1.2,0,'W')}`,`Tahmini tepe çıkış: ${fmt(surge,0,'W')}`];
    }else{
      const r=AloCalc.requiredBattery({loadW:data.load,hours:data.hours,efficiency:data.efficiency,usableDepth:data.dod,aging:data.aging,reserve:data.reserve});
      primary=fmt(r.requiredNominalWh,0,'Wh');small='Rezerv dahil önerilen nominal enerji';nominalWh=r.requiredNominalWh;
      lines=[`Rezervsiz hesap: ${fmt(r.baseNominalWh,0,'Wh')}`,`En az sürekli çıkış: ${fmt(data.load*1.2,0,'W')}`,`Tahmini tepe çıkış: ${fmt(surge,0,'W')}`];
    }
    if(data.load<=150&&nominalWh<=500)cls='Mini UPS / küçük güç';
    else if(data.load<=1000&&nominalWh<=1800)cls='UPS veya power station';
    else if(data.load<=2000&&nominalWh<=3500)cls='Yüksek kapasiteli güç istasyonu';
    else cls='Profesyonel yedek güç tasarımı';

    $('rLoad').textContent=fmt(data.load,0,'W');$('rSurge').textContent=fmt(surge,0,'W');$('rPrimary').textContent=primary;$('rPrimarySmall').textContent=small;$('rClass').textContent=cls;
    $('rConfidence').textContent=data.surgeFactor>1.2?'Kalkış gücü varsayımı kontrol edilmeli':'Etiket watt değeri girildiyse güven artar';
    $('summaryList').innerHTML='';lines.forEach(text=>{const li=document.createElement('li');li.textContent=text;$('summaryList').appendChild(li)});
    const professional=cls.includes('Profesyonel')||data.surgeFactor>1.5||data.load>300;
    $('nextStep').textContent=professional?'Motorlu yük, yüksek güç veya sabit tesisat riski nedeniyle ürün seçimine geçmeden yetkili elektrik mühendisi/servis ile proje doğrulaması gerekir.':'Çözüm seçerken Wh kadar sürekli ve tepe çıkış gücünü, dalga biçimini, bağlantı uyumunu ve üretici garanti koşullarını doğrulayın.';
    $('primaryLabel').textContent=data.mode==='runtime'?'Tahmini çalışma süresi':'Önerilen nominal kapasite';
    configureProductRoute({load:data.load,surgeFactor:data.surgeFactor,nominalWh,cls});
    $('results').classList.remove('hidden');$('results').scrollIntoView({behavior:'smooth',block:'start'});
    const text=`ALO186 yedek güç özeti\nSürekli yük: ${fmt(data.load,0,'W')}\nTepe güç: ${fmt(surge,0,'W')}\n${$('primaryLabel').textContent}: ${primary}\nÇözüm: ${cls}`;
    $('copyBtn').onclick=()=>copyText(text,$('copyBtn'));
    saveCalculation(data);
    if(track)Alo186Track('ups_calculation_completed',{mode:data.mode,load_w:data.load,solution_class:cls,product_route_shown:!$('productRoute').classList.contains('hidden')});
  }catch(err){$('validation').textContent=err.message;}
}

$('calcBtn').addEventListener('click',()=>calculate(true));
$('clearBtn').addEventListener('click',()=>location.reload());
$('restoreBtn').addEventListener('click',restoreCalculation);
$('productLink').addEventListener('click',()=>Alo186Track('ups_product_route_opened',{plan:$('productLink').dataset.plan||'unknown'}));
try{if(localStorage.getItem(storageKey))$('restoreBtn').classList.remove('hidden');}catch(e){}
