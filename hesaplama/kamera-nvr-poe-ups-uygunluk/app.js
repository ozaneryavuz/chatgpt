(() => {
  'use strict';
  const ROUTE='/hesaplama/kamera-nvr-poe-ups-uygunluk/';
  const PRODUCT_ROUTES={
    ups:'/akilli-urun-secimi?intent=kamera-nvr-poe-ups',
    power_station:'/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi'
  };
  const n=(value)=>Number.isFinite(Number(value))?Math.max(0,Number(value)):0;
  const round10=(value)=>Math.ceil(value/10)*10;
  const round50=(value)=>Math.ceil(value/50)*50;
  const calculate=(input)=>{
    const cameraW=n(input.cameraCount)*n(input.cameraW);
    const totalW=n(input.nvrW)+n(input.poeSwitchW)+cameraW+n(input.routerW)+n(input.monitorW)+n(input.alarmW)+n(input.otherW);
    const targetHours=n(input.targetHours);
    const requiredW=round10(totalW*1.25);
    const requiredVA=round50(requiredW/0.7);
    const requiredWh=round10((totalW*targetHours)/0.85/0.8);
    return {cameraW,totalW,targetHours,requiredW,requiredVA,requiredWh,monitorW:n(input.monitorW)};
  };
  const decide=(input)=>{
    const metrics=calculate(input);
    if(input.emergency)return {code:'emergency',level:'stop',title:'Önce elektrik, yangın ve su temas riskini güvenle ayırın',metrics,commerce:false};
    if(input.systemScope==='life_safety')return {code:'life_safety',level:'stop',title:'Yangın algılama, acil çıkış ve kritik erişim sistemleri tüketici tipi ürün seçimine bırakılamaz',metrics,commerce:false};
    if(input.systemScope==='multi_closet')return {code:'multi_closet',level:'warn',title:'Birden fazla kabinet veya bina için her güç ağacını ayrı projelendirin',metrics,commerce:false};
    if(input.connection==='daisy')return {code:'daisy_chain',level:'stop',title:'Çoklayıcı ve adaptör zincirini kaldırmadan yedek güç kullanmayın',metrics,commerce:false};
    if(metrics.totalW<=0 || metrics.targetHours<=0)return {code:'missing_load',level:'warn',title:'Kamera, kayıt, ağ ve hedef süre yüklerini girin',metrics,commerce:false};
    if(input.loadEvidence==='estimated')return {code:'evidence',level:'warn',title:'PoE bütçesi ve cihaz wattlarını teknik belge veya ölçümle doğrulayın',metrics,commerce:false};
    if(input.scenario==='active' && input.sourceStatus!=='existing')return {code:'active_outage',level:'warn',title:'Aktif kesintide henüz satın alınmamış ürün kayıt sürekliliği sağlamaz',metrics,commerce:false};
    if(metrics.requiredW>1500 || metrics.requiredWh>5000)return {code:'professional',level:'warn',title:'Bu yük ve süre küçük tüketici sistemi sınırını aşıyor',metrics,commerce:false};

    if(input.sourceStatus==='existing'){
      const enoughW=n(input.sourceW)>=metrics.requiredW;
      const enoughVA=n(input.sourceVA)>=metrics.requiredVA;
      const enoughWh=n(input.sourceWh)>=metrics.requiredWh;
      const compatible=input.waveform==='approved';
      const transferOk=input.continuity==='restart_ok' || input.transferTest==='success';
      const runtimeOk=input.runtimeTest==='success';
      const recordingOk=input.recordingTest==='success';
      if(enoughW && enoughVA && enoughWh && compatible && transferOk && runtimeOk && recordingOk){
        return {code:'no_buy',level:'good',title:'Mevcut kaynak yeterli — yeni ürün almayın',metrics,commerce:false};
      }
      if(input.recordingTest==='failed')return {code:'recording_fail',level:'warn',title:'Güç devam etse de kayıt veya kamera ağacı kesintide korunmuyor',metrics,commerce:false};
      if(input.transferTest==='restart' && input.continuity==='no_restart')return {code:'transfer_fail',level:'warn',title:'Transfer davranışı kesintisiz kayıt hedefini karşılamıyor',metrics,commerce:false};
      if(input.runtimeTest==='failed')return {code:'runtime_fail',level:'warn',title:'Gerçek süre testi hedefi karşılamıyor',metrics,commerce:false};
    }

    const productClass=input.continuity==='restart_ok'?'power_station':'ups';
    const title=productClass==='ups'
      ? 'NVR, PoE switch ve ağ cihazları için UPS sınıfını karşılaştırın'
      : 'Yeniden başlama kabul ediliyorsa yeterli Wh değerine sahip güç istasyonu sınıfını karşılaştırın';
    return {code:productClass,level:'warn',title,metrics,commerce:input.scenario!=='active',productClass};
  };

  if(typeof module!=='undefined' && module.exports){module.exports={ROUTE,PRODUCT_ROUTES,calculate,decide};return;}
  const $=(id)=>document.getElementById(id);
  const form=$('cctvForm');
  const result=$('result');
  const sourceStatus=$('sourceStatus');
  const existingFields=$('existingFields');
  const getInput=()=>({
    emergency:$('emergency').checked,scenario:$('scenario').value,systemScope:$('systemScope').value,
    continuity:$('continuity').value,connection:$('connection').value,
    nvrW:$('nvrW').value,poeSwitchW:$('poeSwitchW').value,cameraCount:$('cameraCount').value,cameraW:$('cameraW').value,
    routerW:$('routerW').value,monitorW:$('monitorW').value,alarmW:$('alarmW').value,otherW:$('otherW').value,
    targetHours:$('targetHours').value,loadEvidence:$('loadEvidence').value,sourceStatus:sourceStatus.value,
    sourceW:$('sourceW').value,sourceVA:$('sourceVA').value,sourceWh:$('sourceWh').value,waveform:$('waveform').value,
    transferTest:$('transferTest').value,runtimeTest:$('runtimeTest').value,recordingTest:$('recordingTest').value
  });
  const metric=(label,value,small='')=>`<div class="metric"><span>${label}</span><strong>${value}</strong><small>${small}</small></div>`;
  const explain=(code)=>({
    emergency:'Duman, erime, su teması veya elektrik çarpması riski ürün seçiminden önce gelir.',
    life_safety:'Yangın alarmı, acil çıkış kilidi ve yaşam güvenliği sistemleri ilgili standart, proje ve bakım sorumluluğuyla ele alınmalıdır.',
    multi_closet:'Her kabinetin PoE yükü, uplink cihazları, kayıt yolu ve batarya süresi ayrı hesaplanmalıdır.',
    daisy_chain:'Art arda çoklayıcılar temas, ısınma ve koruma belirsizliği oluşturur.',
    missing_load:'NVR, PoE switch, kameralar ve ağ cihazları birlikte hesaba katılmalıdır.',
    evidence:"Port sayısı güç bütçesi değildir. Switch'in kendi tüketimi ile kameraların gerçek veya azami PoE yükü ayrılmalıdır.",
    active_outage:'Yeni satın alma devam eden kesintide kaydı geri getirmez; mevcut kaynak ve güvenli kapatma planı önceliklidir.',
    professional:'Yüksek güç, uzun süre veya dağıtık kabinet yapısı proje, seçicilik, batarya kabini ve bakım planı gerektirir.',
    no_buy:'W, VA, Wh, transfer, gerçek süre ve kayıt kanıtları birlikte yeterli.',
    recording_fail:'NVR açık kalsa bile PoE switch, kamera, disk veya ağ bağlantısı düşüyorsa gerçek kayıt sürekliliği yoktur.',
    transfer_fail:'Wh yeterli olsa da transfer anında NVR yeniden başlıyorsa kayıt boşluğu oluşabilir.',
    runtime_fail:'Akü yaşı, disk yükü, gece IR modu ve gerçek PoE tüketimi pratik süreyi kısaltabilir.',
    ups:'Kesintisiz kayıt için hem aktif W/VA sınırı hem gerçek transfer testi gerekir.',
    power_station:'Yeniden başlama kabul edilse bile EPS davranışı, nominal Wh ve gerçek yük testi doğrulanmalıdır.'
  }[code]||'Teknik kanıtları tamamlayın.');
  const render=(decision)=>{
    const m=decision.metrics;
    let extra='';
    if(decision.commerce){
      extra=`<div class="affiliate"><strong>Şeffaf satış ortaklığı kapısı</strong><p>Ürün sınıfı yalnız gerçek teknik açık bulunduğu için gösteriliyor. Sonraki dış mağaza bağlantılarından ALO186 komisyon kazanabilir; kullanıcıya ek maliyet yansımaz.</p><div class="checks">
        <label class="check"><input id="confirmGap" type="checkbox">Mevcut güvenli kaynağın kayıt hedefini karşılamadığını doğruladım.</label>
        <label class="check"><input id="confirmSpecs" type="checkbox">NVR, PoE, W, VA, Wh, transfer ve gerçek kayıt testini tam modelde yeniden kontrol edeceğim.</label>
        <label class="check"><input id="confirmAffiliate" type="checkbox">Sonraki bağlantının satış ortaklığı bağlantısı olabileceğini anlıyorum.</label>
      </div><a id="productLink" class="button primary" href="${PRODUCT_ROUTES[decision.productClass]}" rel="sponsored nofollow noopener" aria-disabled="true">Uygun ürün sınıfını aç</a></div>`;
    }
    const monitorNote=m.monitorW>0?'<p class="hint"><strong>İpucu:</strong> Monitörü batarya çıkışından ayırmak kayıt sisteminin çalışma süresini uzatabilir; uzaktan görüntüleme için modem/ONT ve operatör altyapısı ayrıca çalışmalıdır.</p>':'';
    result.className=`panel result ${decision.level}`;
    result.innerHTML=`<h2>${decision.title}</h2><div class="metrics">
      ${metric('Toplam kamera PoE yükü',`${Math.round(m.cameraW)} W`,'adet × kamera W')}
      ${metric('Toplam kritik yük',`${Math.round(m.totalW)} W`,'NVR + PoE + ağ')}
      ${metric('UPS alt sınırı',`${m.requiredW} W / ${m.requiredVA} VA`,'%25 rezerv dahil')}
      ${metric('Nominal enerji ihtiyacı',`${m.requiredWh} Wh`,`${m.targetHours} saat hedef`)}
    </div>${monitorNote}<div class="callout ${decision.level==='stop'?'danger':decision.level==='good'?'good':''}"><strong>Neden?</strong> ${explain(decision.code)}</div>${extra}
    <div class="actions"><button id="printBtn" class="button" type="button">Yazdır / PDF</button><button id="jsonBtn" class="button" type="button">Teknik sonucu JSON indir</button><button id="icsBtn" class="button" type="button">90 günlük kayıt testi indir</button></div>`;
    result.classList.remove('hidden');result.focus();
    $('printBtn')?.addEventListener('click',()=>globalThis.print());
    $('jsonBtn')?.addEventListener('click',()=>downloadJson(decision));
    $('icsBtn')?.addEventListener('click',downloadIcs);
    ['confirmGap','confirmSpecs','confirmAffiliate'].forEach(id=>$(id)?.addEventListener('change',updateAffiliate));
  };
  const updateAffiliate=()=>{const link=$('productLink');if(!link)return;const enabled=['confirmGap','confirmSpecs','confirmAffiliate'].every(id=>$(id)?.checked);link.setAttribute('aria-disabled',String(!enabled));};
  const saveBlob=(content,type,name)=>{const blob=new Blob([content],{type});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();URL.revokeObjectURL(url);};
  const downloadJson=(decision)=>saveBlob(JSON.stringify({schema:'alo186-cctv-continuity-v1',route:ROUTE,createdAt:new Date().toISOString(),personalData:false,result:decision},null,2),'application/json','alo186-kamera-nvr-poe-ups-sonucu.json');
  const pad=(v)=>String(v).padStart(2,'0');
  const stamp=(date)=>`${date.getUTCFullYear()}${pad(date.getUTCMonth()+1)}${pad(date.getUTCDate())}T${pad(date.getUTCHours())}${pad(date.getUTCMinutes())}00Z`;
  const downloadIcs=()=>{const start=new Date();start.setDate(start.getDate()+90);start.setHours(10,0,0,0);const end=new Date(start.getTime()+45*60*1000);const ics=`BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//ALO186//Kamera Sistemi Yedek Güç Testi//TR\r\nBEGIN:VEVENT\r\nUID:cctv-${Date.now()}@alo186.com\r\nDTSTAMP:${stamp(new Date())}\r\nDTSTART:${stamp(start)}\r\nDTEND:${stamp(end)}\r\nSUMMARY:Kamera NVR PoE yedek güç ve kayıt testi\r\nDESCRIPTION:NVR, disk, PoE switch, bütün kameralar, modem/ONT, zaman damgası, uzaktan erişim, transfer ve gerçek süreyi kontrollü test edin.\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n`;saveBlob(ics,'text/calendar','alo186-kamera-nvr-poe-90-gunluk-test.ics');};
  sourceStatus.addEventListener('change',()=>existingFields.classList.toggle('hidden',sourceStatus.value!=='existing'));
  form.addEventListener('submit',(event)=>{event.preventDefault();render(decide(getInput()));});
  form.addEventListener('reset',()=>setTimeout(()=>{existingFields.classList.add('hidden');result.className='panel result hidden';result.innerHTML='';},0));
})();
