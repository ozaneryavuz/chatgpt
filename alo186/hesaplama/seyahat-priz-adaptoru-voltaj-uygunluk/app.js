(() => {
  'use strict';

  const $=(id)=>document.getElementById(id);
  const api=window.Alo186TravelAdapter;
  let lastResult=null;
  const amazonSearch=(query)=>`https://www.amazon.com.tr/s?k=${encodeURIComponent(query)}&tag=alo186rehber-21`;
  const escapeHtml=(value)=>String(value??'').replace(/[&<>"']/g,(char)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

  function read(){
    return {
      destination:$('destination').value,
      deviceType:$('deviceType').value,
      minV:$('minV').value,
      maxV:$('maxV').value,
      frequency:$('frequency').value,
      deviceW:$('deviceW').value,
      earthClass:$('earthClass').value,
      existingAdapter:$('existingAdapter').value,
      adapterMaxV:$('adapterMaxV').value,
      adapterMaxA:$('adapterMaxA').value,
      adapterMaxW:$('adapterMaxW').value,
      adapterEarth:$('adapterEarth').value,
      safetyEvidence:$('safetyEvidence').value,
      recallChecked:$('recallChecked').value,
      hazard:$('hazard').checked,
      adapterDamaged:$('adapterDamaged').checked,
      tripDate:$('tripDate').value
    };
  }

  function toggleExisting(){
    $('existingFields').classList.toggle('hidden',$('existingAdapter').value!=='yes');
  }

  function setGate(){
    const gate=$('affiliateGate');
    const link=$('affiliateLink');
    const checked=[...gate.querySelectorAll('input[type="checkbox"]')].every((item)=>item.checked);
    link.setAttribute('aria-disabled',checked?'false':'true');
    link.tabIndex=checked?0:-1;
    link.classList.toggle('disabled',!checked);
  }

  function statusClass(status){
    if(status==='no_buy')return 'good';
    if(status==='conditional_purchase')return 'ready';
    if(status==='emergency'||status==='voltage_mismatch'||status==='frequency_mismatch')return 'danger';
    return 'warn';
  }

  function render(result){
    lastResult=result;
    const out=$('result');
    out.classList.remove('hidden');
    $('affiliatePanel').classList.add('hidden');
    $('downloadPanel').classList.remove('hidden');
    $('resultState').className=`state ${statusClass(result.status)}`;
    $('resultState').textContent={
      no_buy:'Satın alma yok',conditional_purchase:'Koşullu ürün yolu',emergency:'Kullanmayı durdurun',
      evidence:'Kanıt gerekli',professional:'Uzman/üretici doğrulaması',voltage_mismatch:'Voltaj uyumsuz',
      frequency_mismatch:'Frekans uyumsuz',invalid:'Girdi hatası'
    }[result.status]||'Teknik sonuç';
    $('resultTitle').textContent=result.title||'Sonuç';
    $('resultSummary').textContent=result.summary||(result.errors||[]).join(' ');
    const frequencyLabel=result.destination&&(result.destination.frequencyLabel||(`${result.destination.frequency} Hz`));
    $('destinationMetric').textContent=result.destination&&result.destination.voltage?`${result.destination.voltage} V · ${frequencyLabel} · Tip ${result.destination.plug}`:'Doğrulanmalı';
    $('requiredMetric').textContent=result.requiredW?`${result.requiredW} W${result.requiredA?` · ${result.requiredA} A`:''}`:'—';
    $('voltageMetric').textContent=result.input?`${result.input.minV}–${result.input.maxV} V · ${result.input.frequency==='50_60'?'50/60':result.input.frequency} Hz`:'—';
    const items=result.actions||result.errors||[];
    $('actions').innerHTML=items.map((item)=>`<li>${escapeHtml(item)}</li>`).join('');
    $('reasonBlock').classList.toggle('hidden',!(result.reasons&&result.reasons.length));
    $('reasons').innerHTML=(result.reasons||[]).map((item)=>`<li>${escapeHtml(item)}</li>`).join('');

    if(result.commerceAllowed&&result.affiliateQuery){
      $('affiliatePanel').classList.remove('hidden');
      $('affiliateLink').href=amazonSearch(result.affiliateQuery);
      $('affiliateQuery').textContent=result.affiliateQuery;
      $('affiliateGate').querySelectorAll('input').forEach((item)=>{item.checked=false;});
      setGate();
    }
    out.focus();
  }

  function slugDate(date){return date.toISOString().slice(0,10).replace(/-/g,'');}
  function download(name,type,content){
    const blob=new Blob([content],{type});
    const url=URL.createObjectURL(blob);
    const link=document.createElement('a');
    link.href=url;link.download=name;document.body.appendChild(link);link.click();link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }

  function exportJson(){
    if(!lastResult)return;
    const payload={
      schemaVersion:1,
      generatedAt:new Date().toISOString(),
      tool:'ALO186 Seyahat Priz Adaptörü ve Voltaj Uygunluğu',
      officialStatus:'ALO186 bağımsız bilgi platformudur; kamu kurumu, EDAŞ, ürün satıcısı veya yetkili servis değildir.',
      result:lastResult,
      commercialDisclosure:'Koşullu mağaza bağlantısı Amazon satış ortaklığı bağlantısıdır. Fiyat, stok, satıcı, puan ve garanti mağazada yeniden doğrulanır.',
      reminder:'Seyahatten önce cihaz etiketi, priz tipi, topraklama, adaptör V/A/W değeri ve ürün güvenliği duyurusu yeniden kontrol edilmelidir.'
    };
    download('alo186-seyahat-elektrik-kontrolu.json','application/json;charset=utf-8',`${JSON.stringify(payload,null,2)}\n`);
  }

  function exportIcs(){
    if(!lastResult||!lastResult.input||!lastResult.input.tripDate){
      alert('Takvim dosyası için seyahat tarihini girin.');
      return;
    }
    const trip=new Date(`${lastResult.input.tripDate}T12:00:00`);
    if(Number.isNaN(trip.getTime())){alert('Seyahat tarihi geçerli değil.');return;}
    const reminder=new Date(trip);reminder.setDate(reminder.getDate()-7);
    const start=slugDate(reminder);
    const endDate=new Date(reminder);endDate.setDate(endDate.getDate()+1);
    const end=slugDate(endDate);
    const uid=`alo186-travel-${Date.now()}@alo186.com`;
    const description='Cihaz INPUT etiketi (V/Hz/W), hedef priz tipi, topraklama, adaptör azami V/A/W, fiziksel hasar ve geri çağırma durumunu kontrol edin. Adaptör voltaj veya frekans dönüştürmez. ALO186 bağımsız bilgi platformudur.';
    const ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//ALO186//Travel Electrical Check//TR','CALSCALE:GREGORIAN','BEGIN:VEVENT',`UID:${uid}`,`DTSTART;VALUE=DATE:${start}`,`DTEND;VALUE=DATE:${end}`,'SUMMARY:Seyahat priz adaptörü ve cihaz etiketi kontrolü',`DESCRIPTION:${description.replace(/,/g,'\\,')}`,'END:VEVENT','END:VCALENDAR',''].join('\r\n');
    download('alo186-seyahat-elektrik-kontrolu.ics','text/calendar;charset=utf-8',ics);
  }

  $('travelForm').addEventListener('submit',(event)=>{event.preventDefault();render(api.evaluate(read()));});
  $('existingAdapter').addEventListener('change',toggleExisting);
  $('affiliateGate').addEventListener('change',setGate);
  $('affiliateLink').addEventListener('click',(event)=>{
    if($('affiliateLink').getAttribute('aria-disabled')!=='false')event.preventDefault();
  });
  $('downloadJson').addEventListener('click',exportJson);
  $('downloadIcs').addEventListener('click',exportIcs);
  $('printResult').addEventListener('click',()=>window.print());
  toggleExisting();
})();
