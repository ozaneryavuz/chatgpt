(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const core=window.Alo186PowerbankUsbC;
  const valueIds=['deviceType','deviceEnergyMode','deviceWh','deviceMah','deviceVoltage','targetCharges','deviceMinW','devicePreferredW','bankEnergyMode','bankWh','bankMah','cellVoltage','transferEfficiency','singlePortW','totalOutputW','simultaneousDevices','cableW','ownership'];
  const checkIds=['capacityLabelVerified','usbPdConfirmed','cableRated','sharedOutputConfirmed','manufacturerInstructionsChecked','damageFree','recallChecked','medicalDevice'];
  const presets={
    phone:{deviceType:'phone',deviceEnergyMode:'wh',deviceWh:18,deviceMah:'',deviceVoltage:'',targetCharges:2,deviceMinW:10,devicePreferredW:25,bankEnergyMode:'mah',bankWh:'',bankMah:20000,cellVoltage:3.7,transferEfficiency:70,singlePortW:25,totalOutputW:25,simultaneousDevices:1,cableW:60,ownership:'candidate',capacityLabelVerified:true,usbPdConfirmed:true,cableRated:true,sharedOutputConfirmed:true,manufacturerInstructionsChecked:true,damageFree:true,recallChecked:true,medicalDevice:false},
    laptop:{deviceType:'laptop',deviceEnergyMode:'wh',deviceWh:60,deviceMah:'',deviceVoltage:'',targetCharges:1,deviceMinW:45,devicePreferredW:65,bankEnergyMode:'mah',bankWh:'',bankMah:27000,cellVoltage:3.7,transferEfficiency:70,singlePortW:65,totalOutputW:65,simultaneousDevices:1,cableW:100,ownership:'candidate',capacityLabelVerified:true,usbPdConfirmed:true,cableRated:true,sharedOutputConfirmed:true,manufacturerInstructionsChecked:true,damageFree:true,recallChecked:true,medicalDevice:false},
    shared:{deviceType:'tablet',deviceEnergyMode:'wh',deviceWh:30,deviceMah:'',deviceVoltage:'',targetCharges:1,deviceMinW:18,devicePreferredW:30,bankEnergyMode:'mah',bankWh:'',bankMah:20000,cellVoltage:3.7,transferEfficiency:70,singlePortW:30,totalOutputW:30,simultaneousDevices:2,cableW:60,ownership:'owned',capacityLabelVerified:true,usbPdConfirmed:true,cableRated:true,sharedOutputConfirmed:false,manufacturerInstructionsChecked:true,damageFree:true,recallChecked:true,medicalDevice:false}
  };
  function emit(name,params={}){if(typeof window.Alo186Track==='function')window.Alo186Track(name,params);}
  function values(){const data={};valueIds.forEach(id=>data[id]=$(id).value);checkIds.forEach(id=>data[id]=$(id).checked);return data;}
  function setValues(data){valueIds.forEach(id=>{if(data[id]!=null)$(id).value=String(data[id]);});checkIds.forEach(id=>{$(id).checked=Boolean(data[id]);});updateModeFields();}
  const escapeHtml=value=>String(value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const list=items=>items.map(item=>`<li>${escapeHtml(item)}</li>`).join('');
  const fmt=(value,digits=1)=>Number(value).toLocaleString('tr-TR',{maximumFractionDigits:digits});
  function updateModeFields(){
    const deviceWh=$('deviceEnergyMode').value==='wh';
    $('deviceWhField').classList.toggle('hidden',!deviceWh);$('deviceMahField').classList.toggle('hidden',deviceWh);$('deviceVoltageField').classList.toggle('hidden',deviceWh);
    const bankWh=$('bankEnergyMode').value==='wh';
    $('bankWhField').classList.toggle('hidden',!bankWh);$('bankMahField').classList.toggle('hidden',bankWh);$('cellVoltageField').classList.toggle('hidden',bankWh);
  }
  function updateAffiliate(){const enabled=$('affiliateAck').checked;const link=$('productCenterLink');link.classList.toggle('disabled-link',!enabled);link.setAttribute('aria-disabled',enabled?'false':'true');link.tabIndex=enabled?0:-1;}
  function render(result){
    $('results').classList.remove('hidden');
    const labels={compatible:'Hedef ve güç sınırları içinde',conditional:'Koşullu / daha yavaş veya doğrulama gerekli',incompatible:'Hedefi karşılamıyor veya güvenlik engeli var'};
    $('resultStatus').textContent=labels[result.status];$('resultStatus').className=`status ${result.status==='compatible'?'ok':result.status==='conditional'?'warn':'bad'}`;
    $('storedMetric').textContent=`${fmt(result.bankStoredWh)} Wh`;
    $('usableMetric').textContent=`${fmt(result.usableWh)} Wh`;
    $('chargesMetric').textContent=`${fmt(result.estimatedCharges,2)} kez`;
    $('powerMetric').textContent=`${fmt(result.negotiatedW)} W`;
    $('timeMetric').textContent=`${fmt(result.approximateChargeHours,2)} saat`;
    $('requiredMetric').textContent=`${fmt(result.requiredStoredWh)} Wh · ${fmt(result.requiredMah,0)} mAh`;
    $('resultSummary').textContent=`Cihaz ${fmt(result.deviceWh)} Wh · hedef ${fmt(result.input.targetCharges,2)} tam şarj · toplam aktarım verimi %${fmt(result.input.transferEfficiency*100,0)}`;
    $('blockerCard').classList.toggle('hidden',!result.blockers.length);$('blockerList').innerHTML=list(result.blockers);
    $('warningList').innerHTML=list(result.warnings.length?result.warnings:['Belirgin kapasite veya güç sınırı görülmedi; tam model etiketi ve üretici kılavuzu yine doğrulanmalıdır.']);
    $('checkList').innerHTML=list(result.checks);
    $('noPurchasePanel').classList.toggle('hidden',!result.noPurchaseNeeded);
    $('affiliatePanel').classList.toggle('hidden',!result.commercialAllowed);$('affiliateAck').checked=false;updateAffiliate();
    $('results').focus({preventScroll:true});$('results').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
    emit('powerbank_usb_c_completed',{status:result.status,commercial_allowed:result.commercialAllowed,no_purchase_needed:result.noPurchaseNeeded,device_type:result.input.deviceType,capacity_band:result.bankStoredWh<=40?'small':result.bankStoredWh<=80?'medium':'large',power_band:result.negotiatedW<30?'low':result.negotiatedW<65?'medium':'high'});
  }
  document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>{setValues(presets[button.dataset.preset]);emit('powerbank_usb_c_preset_selected',{preset:button.dataset.preset});}));
  $('deviceEnergyMode').addEventListener('change',updateModeFields);$('bankEnergyMode').addEventListener('change',updateModeFields);
  $('powerbankForm').addEventListener('submit',event=>{event.preventDefault();try{$('validation').textContent='';render(core.analyze(values()));}catch(error){$('validation').textContent=error.message;$('validation').focus();}});
  $('resetBtn').addEventListener('click',()=>{$('powerbankForm').reset();setValues(presets.phone);$('results').classList.add('hidden');$('validation').textContent='';emit('powerbank_usb_c_reset');});
  $('affiliateAck').addEventListener('change',updateAffiliate);
  $('productCenterLink').addEventListener('click',event=>{if(event.currentTarget.getAttribute('aria-disabled')==='true'){event.preventDefault();return;}emit('powerbank_product_center_opened',{category:'powerbank'});});
  setValues(presets.phone);
})();