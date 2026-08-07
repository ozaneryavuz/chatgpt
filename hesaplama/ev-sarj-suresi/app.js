const $=id=>document.getElementById(id);
$('charger').addEventListener('change',()=>{const kw=Number($('charger').value);$('phase').value=kw>=11?'three':'single';});
$('calcBtn').addEventListener('click',()=>{
  $('validation').textContent='';
  try{
    const kw=Number($('charger').value), phase=$('phase').value;
    const r=AloCalc.evCharge({batteryKWh:Number($('battery').value),currentSoc:Number($('currentSoc').value),targetSoc:Number($('targetSoc').value),chargerKW:kw,efficiency:Number($('eff').value)/100,unitPrice:Number($('price').value)});
    const amps=AloCalc.chargerCurrent({chargerKW:kw,phase});
    const range=r.batteryEnergyKWh/Number($('consumption').value)*100;
    $('rBattery').textContent=fmt(r.batteryEnergyKWh,1,'kWh');$('rGrid').textContent=fmt(r.gridEnergyKWh,1,'kWh');
    $('rTime').textContent=fmt(r.hours,2,'saat');$('rCost').textContent=fmt(r.cost,2,'TL');
    $('electricalList').innerHTML=[`Yaklaşık hat akımı: ${fmt(amps,1,'A')}`,`Bağlantı varsayımı: ${phase==='three'?'Trifaze 400 V':'Monofaze 230 V'}`,`Şarj gücü: ${fmt(kw,1,'kW')}`,kw>7.4?'Profesyonel kapasite ve yük yönetimi kontrolü önerilir.':'Mevcut priz/hat uygunluğu yine de yetkili uzman tarafından doğrulanmalıdır.'].map(x=>`<li>${x}</li>`).join('');
    $('rangeText').textContent=`Hedef SOC artışı teorik olarak yaklaşık ${fmt(range,0,'km')} sürüş enerjisine karşılık gelir. Gerçek menzil; hız, sıcaklık, klima ve sürüşe göre değişir.`;
    $('results').classList.remove('hidden');$('results').scrollIntoView({behavior:'smooth'});
    const text=`ALO186 EV şarj özeti\nEnerji: ${fmt(r.gridEnergyKWh,1,'kWh')}\nSüre: ${fmt(r.hours,2,'saat')}\nMaliyet: ${fmt(r.cost,2,'TL')}\nAkım: ${fmt(amps,1,'A')}`;
    $('copyBtn').onclick=()=>copyText(text,$('copyBtn'));
    Alo186Track('ev_calculation_completed',{charger_kw:kw,phase,charge_hours:AloCalc.round(r.hours,2)});
  }catch(err){$('validation').textContent=err.message;}
});
