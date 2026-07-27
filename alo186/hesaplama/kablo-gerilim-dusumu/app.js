const $=id=>document.getElementById(id);
$('system').addEventListener('change',()=>{$('voltage').value=$('system').value==='three'?'400':'230';});
$('calcBtn').addEventListener('click',()=>{
  $('validation').textContent='';
  try{
    const p={system:$('system').value,material:$('material').value,lengthM:Number($('length').value),currentA:Number($('current').value),sectionMM2:Number($('section').value),voltageV:Number($('voltage').value),tempC:Number($('temp').value)};
    const r=AloCalc.voltageDrop(p), req=AloCalc.requiredSection({...p,maxDropPercent:Number($('maxDrop').value)});
    const ok=r.dropPercent<=Number($('maxDrop').value);
    $('rDropV').textContent=fmt(r.dropV,2,'V');$('rDropPercent').textContent=fmt(r.dropPercent,2,'%');
    $('rStatus').textContent=ok?'Girilen düşüm sınırının altında':'Girilen düşüm sınırının üzerinde';
    $('rEndVoltage').textContent=fmt(p.voltageV-r.dropV,1,'V');$('rSection').textContent=req.sectionMM2?fmt(req.sectionMM2,1,'mm²'):'300 mm² üzeri / detaylı hesap';
    const lines=[`Malzeme ve sıcaklıkla düzeltilmiş özdirenç: ${fmt(r.rho,5,'Ω·mm²/m')}`,`Mevcut kesit: ${fmt(p.sectionMM2,1,'mm²')}`,`Yalnız gerilim düşümüne göre önerilen standart kesit: ${req.sectionMM2?fmt(req.sectionMM2,1,'mm²'):'hesap aralığı dışında'}`,`Bu sonuç akım taşıma kapasitesi uygunluğu anlamına gelmez.`];
    $('summaryList').innerHTML=lines.map(x=>`<li>${x}</li>`).join('');
    $('results').classList.remove('hidden');$('results').scrollIntoView({behavior:'smooth'});
    const text=`ALO186 gerilim düşümü özeti\nDüşüm: ${fmt(r.dropV,2,'V')} / ${fmt(r.dropPercent,2,'%')}\nHat sonu: ${fmt(p.voltageV-r.dropV,1,'V')}\nDüşüme göre kesit: ${req.sectionMM2?fmt(req.sectionMM2,1,'mm²'):'detaylı hesap gerekli'}`;
    $('copyBtn').onclick=()=>copyText(text,$('copyBtn'));
    Alo186Track('voltage_drop_completed',{system:p.system,material:p.material,drop_percent:AloCalc.round(r.dropPercent,2),section_mm2:p.sectionMM2});
  }catch(err){$('validation').textContent=err.message;}
});
