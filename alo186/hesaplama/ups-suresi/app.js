const $=id=>document.getElementById(id);
const mode=$('mode'), capacityField=$('capacityField'), hoursField=$('hoursField'), reserveField=$('reserveField');
mode.addEventListener('change',()=>{const c=mode.value==='capacity';capacityField.classList.toggle('hidden',c);hoursField.classList.toggle('hidden',!c);reserveField.classList.toggle('hidden',!c);});
document.querySelectorAll('.preset').forEach(b=>b.addEventListener('click',()=>{$('loadW').value=b.dataset.w;if(b.dataset.motor)$('surgeFactor').value='3';Alo186Track('ups_preset_selected',{preset_w:Number(b.dataset.w)});}));
$('clearBtn').addEventListener('click',()=>location.reload());
$('calcBtn').addEventListener('click',()=>{
  $('validation').textContent='';
  try{
    const load=Number($('loadW').value), surge=load*Number($('surgeFactor').value);
    const e=Number($('efficiency').value)/100,d=Number($('dod').value)/100,a=Number($('aging').value)/100;
    let primary, small, cls, lines=[];
    if(mode.value==='runtime'){
      const r=AloCalc.upsRuntime({loadW:load,batteryWh:Number($('batteryWh').value),efficiency:e,usableDepth:d,aging:a});
      primary=fmt(r.runtimeHours,2,'saat');small='Yaklaşık '+fmt(r.runtimeHours*60,0,'dakika');
      lines=[`Kullanılabilir tahmini enerji: ${fmt(r.usableWh,0,'Wh')}`,`En az sürekli çıkış: ${fmt(load*1.2,0,'W')}`,`Tahmini tepe çıkış: ${fmt(surge,0,'W')}`];
    }else{
      const r=AloCalc.requiredBattery({loadW:load,hours:Number($('hours').value),efficiency:e,usableDepth:d,aging:a,reserve:Number($('reserve').value)/100});
      primary=fmt(r.requiredNominalWh,0,'Wh');small='Rezerv dahil önerilen nominal enerji';
      lines=[`Rezervsiz hesap: ${fmt(r.baseNominalWh,0,'Wh')}`,`En az sürekli çıkış: ${fmt(load*1.2,0,'W')}`,`Tahmini tepe çıkış: ${fmt(surge,0,'W')}`];
    }
    const refWh=mode.value==='runtime'?Number($('batteryWh').value):Number(primary.replace(/[^\d]/g,''))||0;
    if(load<=150&&refWh<=500)cls='Mini UPS / küçük güç';
    else if(load<=1000&&refWh<=1800)cls='UPS veya power station';
    else if(load<=2000&&refWh<=3500)cls='Yüksek kapasiteli güç istasyonu';
    else cls='Profesyonel yedek güç tasarımı';
    $('rLoad').textContent=fmt(load,0,'W');$('rSurge').textContent=fmt(surge,0,'W');$('rPrimary').textContent=primary;$('rPrimarySmall').textContent=small;$('rClass').textContent=cls;
    $('rConfidence').textContent=Number($('surgeFactor').value)>1.2?'Kalkış gücü varsayımı kontrol edilmeli':'Etiket watt değeri girildiyse güven artar';
    $('summaryList').innerHTML=lines.map(x=>`<li>${x}</li>`).join('');
    $('nextStep').textContent=cls.includes('Profesyonel')?'Sabit tesisat ve yüksek güç nedeniyle yetkili elektrik mühendisi/servis ile proje doğrulaması gerekir.':'Çözüm seçerken Wh kadar sürekli ve tepe çıkış gücünü, dalga biçimini ve garanti koşullarını da doğrulayın.';
    $('primaryLabel').textContent=mode.value==='runtime'?'Tahmini çalışma süresi':'Önerilen nominal kapasite';
    $('results').classList.remove('hidden');$('results').scrollIntoView({behavior:'smooth',block:'start'});
    const text=`ALO186 yedek güç özeti\nSürekli yük: ${fmt(load,0,'W')}\nTepe güç: ${fmt(surge,0,'W')}\n${$('primaryLabel').textContent}: ${primary}\nÇözüm: ${cls}`;
    $('copyBtn').onclick=()=>copyText(text,$('copyBtn'));
    Alo186Track('ups_calculation_completed',{mode:mode.value,load_w:load,solution_class:cls});
  }catch(err){$('validation').textContent=err.message;}
});
