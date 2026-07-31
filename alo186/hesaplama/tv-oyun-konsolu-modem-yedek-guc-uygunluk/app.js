(() => {
  'use strict';
  const ROUTE='/hesaplama/tv-oyun-konsolu-modem-yedek-guc-uygunluk/';
  const PRODUCT_ROUTES={
    ups:'/akilli-urun-secimi?intent=tv-konsol-ups',
    power_station:'/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi'
  };
  const n=(value)=>Number.isFinite(Number(value))?Math.max(0,Number(value)):0;
  const round10=(value)=>Math.ceil(value/10)*10;
  const calculate=(input)=>{
    const totalW=['tvW','consoleW','networkW','audioW','mediaW','otherW'].reduce((sum,key)=>sum+n(input[key]),0);
    const targetHours=n(input.targetHours);
    const requiredW=round10(totalW*1.25);
    const requiredVA=Math.ceil((requiredW/0.7)/50)*50;
    const requiredWh=round10((totalW*targetHours)/0.85/0.8);
    return {totalW,requiredW,requiredVA,requiredWh,targetHours};
  };
  const decide=(input)=>{
    const metrics=calculate(input);
    if(input.emergency)return {code:'emergency',level:'stop',title:'Önce enerjiyi ve tehlikeyi güvenle ayırın',metrics,commerce:false};
    if(input.loadClass==='medical')return {code:'medical',level:'stop',title:'Bu araç tıbbi veya yaşam desteği cihazı için kullanılmamalıdır',metrics,commerce:false};
    if(input.loadClass==='pc_nas')return {code:'pc_nas',level:'warn',title:'Bilgisayar, gaming PC ve NAS için özel UPS aracına geçin',metrics,commerce:false};
    if(input.loadClass==='high_power')return {code:'high_power',level:'stop',title:'Yüksek güçlü cihazları bu ev eğlence kaynağına bağlamayın',metrics,commerce:false};
    if(input.connection==='daisy')return {code:'daisy_chain',level:'stop',title:'Çoklayıcı ve adaptör zincirini kaldırmadan ürün seçmeyin',metrics,commerce:false};
    if(input.ventilation==='blocked')return {code:'ventilation',level:'stop',title:'Kaynağın havalandırmasını düzeltin',metrics,commerce:false};
    if(metrics.totalW<=0 || metrics.targetHours<=0)return {code:'missing_load',level:'warn',title:'Gerçek yük ve hedef süreyi girin',metrics,commerce:false};
    if(input.loadEvidence==='estimated')return {code:'evidence',level:'warn',title:'Yaklaşık değer yerine gerçek giriş wattını doğrulayın',metrics,commerce:false};
    if(input.scenario==='active' && input.sourceStatus!=='existing')return {code:'active_outage',level:'warn',title:'Aktif kesintide ürün teslimatını anlık çözüm saymayın',metrics,commerce:false};

    if(input.sourceStatus==='existing'){
      const enoughW=n(input.sourceW)>=metrics.requiredW;
      const enoughVA=n(input.sourceVA)>=metrics.requiredVA;
      const enoughWh=n(input.sourceWh)>=metrics.requiredWh;
      const compatible=input.waveform==='approved';
      const transferOk=input.continuity==='restart_ok' || input.transferTest==='success';
      const runtimeOk=input.runtimeTest==='success';
      if(enoughW && enoughVA && enoughWh && compatible && transferOk && runtimeOk){
        return {code:'no_buy',level:'good',title:'Mevcut kaynak yeterli — yeni ürün almayın',metrics,commerce:false};
      }
      if(input.transferTest==='restart' && input.continuity==='no_restart'){
        return {code:'transfer_fail',level:'warn',title:'Güç yeterli olsa bile transfer davranışı hedefi karşılamıyor',metrics,commerce:false};
      }
    }

    const productClass=input.continuity==='restart_ok'?'power_station':'ups';
    const title=productClass==='ups'
      ? 'Kesintide yeniden başlamayı önlemek için UPS veya doğrulanmış EPS sınıfını karşılaştırın'
      : 'Uzun çalışma süresi için uygun power station sınıfını karşılaştırın';
    return {code:productClass,level:'warn',title,metrics,commerce:input.scenario!=='active',productClass};
  };

  if(typeof module!=='undefined' && module.exports){module.exports={ROUTE,PRODUCT_ROUTES,calculate,decide};return;}
  const $=(id)=>document.getElementById(id);
  const form=$('entertainmentForm');
  const result=$('result');
  const sourceStatus=$('sourceStatus');
  const existingFields=$('existingFields');
  const getInput=()=>({
    emergency:$('emergency').checked,
    scenario:$('scenario').value,
    loadClass:$('loadClass').value,
    continuity:$('continuity').value,
    connection:$('connection').value,
    ventilation:$('ventilation').value,
    tvW:$('tvW').value,consoleW:$('consoleW').value,networkW:$('networkW').value,
    audioW:$('audioW').value,mediaW:$('mediaW').value,otherW:$('otherW').value,
    targetHours:$('targetHours').value,loadEvidence:$('loadEvidence').value,
    sourceStatus:sourceStatus.value,sourceType:$('sourceType').value,
    sourceW:$('sourceW').value,sourceVA:$('sourceVA').value,sourceWh:$('sourceWh').value,
    waveform:$('waveform').value,transferTest:$('transferTest').value,runtimeTest:$('runtimeTest').value
  });
  const metric=(label,value,small='')=>`<div class="metric"><span>${label}</span><strong>${value}</strong><small>${small}</small></div>`;
  const render=(decision)=>{
    const m=decision.metrics;
    let extra='';
    if(decision.code==='pc_nas')extra='<p><a class="button" href="../bilgisayar-gaming-pc-nas-ups-uygunluk/">Bilgisayar ve NAS UPS aracını aç</a></p>';
    if(decision.commerce){
      extra=`<div class="affiliate"><strong>Şeffaf satış ortaklığı kapısı</strong><p>Ürün sınıfı yalnız gerçek teknik açık bulunduğu için gösteriliyor. Sonraki dış mağaza bağlantılarından ALO186 komisyon kazanabilir; kullanıcıya ek maliyet yansımaz.</p><div class="checks">
        <label class="check"><input id="confirmGap" type="checkbox">Mevcut güvenli kaynağın hedefi karşılamadığını doğruladım.</label>
        <label class="check"><input id="confirmSpecs" type="checkbox">W, VA, Wh, çıkış uyumu ve transfer davranışını tam modelde yeniden kontrol edeceğim.</label>
        <label class="check"><input id="confirmAffiliate" type="checkbox">Sonraki bağlantının satış ortaklığı bağlantısı olabileceğini anlıyorum.</label>
      </div><a id="productLink" class="button primary" href="${PRODUCT_ROUTES[decision.productClass]}" rel="sponsored nofollow noopener" aria-disabled="true">Uygun ürün sınıfını aç</a></div>`;
    }
    result.className=`panel result ${decision.level}`;
    result.innerHTML=`<h2>${decision.title}</h2><div class="metrics">
      ${metric('Toplam gerçek yük',`${Math.round(m.totalW)} W`,'eşzamanlı cihazlar')}
      ${metric('Sürekli güç alt sınırı',`${m.requiredW} W`,'%25 rezerv dahil')}
      ${metric('Yaklaşık UPS alt sınırı',`${m.requiredVA} VA`,'W sınırı ayrıca doğrulanır')}
      ${metric('Nominal enerji ihtiyacı',`${m.requiredWh} Wh`,`${m.targetHours} saat hedef`)}
    </div><div class="callout ${decision.level==='stop'?'danger':decision.level==='good'?'good':''}"><strong>Neden?</strong> ${explain(decision.code)}</div>${extra}
    <div class="actions"><button id="printBtn" class="button" type="button">Yazdır / PDF</button><button id="jsonBtn" class="button" type="button">Teknik sonucu JSON indir</button></div>`;
    result.classList.remove('hidden');
    result.focus();
    const printBtn=$('printBtn'); if(printBtn)printBtn.addEventListener('click',()=>globalThis.print());
    const jsonBtn=$('jsonBtn'); if(jsonBtn)jsonBtn.addEventListener('click',()=>downloadJson(decision));
    ['confirmGap','confirmSpecs','confirmAffiliate'].forEach(id=>{const el=$(id);if(el)el.addEventListener('change',updateAffiliate);});
  };
  const explain=(code)=>({
    emergency:'Can güvenliği ve yangın riski ürün seçiminden önce gelir.',
    medical:'Yaşam desteği ve tıbbi cihazlarda üretici, sağlık profesyoneli ve özel süreklilik planı gerekir.',
    pc_nas:'Bilgisayar güç kaynağı, aktif PFC, veri kaybı ve NAS kapanma gereksinimleri ayrı değerlendirilir.',
    high_power:'Isıtıcı, lazer yazıcı, süpürge ve benzeri yükler UPS çıkışını aşabilir.',
    daisy_chain:'Art arda çoklayıcılar temas, ısınma ve koruma belirsizliği oluşturur.',
    ventilation:'UPS ve bataryalar ısı üretir; kapalı dolap ve tıkalı hava girişi ömrü ve güvenliği etkiler.',
    missing_load:'Sıfır veya eksik yükle yapılan sonuç gerçek ürün seçimi değildir.',
    evidence:'Model adı veya tahmini internet değeri yerine etiket, teknik belge veya ölçüm gerekir.',
    active_outage:'Yeni satın alma, devam eden kesintide anında enerji sağlamaz.',
    no_buy:'Güç, VA, enerji, uyumluluk, transfer ve gerçek süre kanıtları birlikte yeterli.',
    transfer_fail:'Wh kapasitesi yeterli olsa bile transfer sırasında cihaz yeniden başlıyorsa kesintisizlik hedefi sağlanmaz.',
    ups:'Kesintide yeniden başlama kabul edilmiyorsa transfer davranışı ve gerçek yük testi belirleyicidir.',
    power_station:'Kısa kesintide yeniden başlama kabul ediliyorsa daha uzun Wh kapasitesi öncelikli olabilir.'
  }[code]||'Teknik kanıtları tamamlayın.');
  const updateAffiliate=()=>{
    const link=$('productLink'); if(!link)return;
    const enabled=['confirmGap','confirmSpecs','confirmAffiliate'].every(id=>$(id)?.checked);
    link.setAttribute('aria-disabled',String(!enabled));
  };
  const downloadJson=(decision)=>{
    const payload={schema:'alo186-entertainment-backup-v1',route:ROUTE,createdAt:new Date().toISOString(),personalData:false,result:decision};
    const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});
    const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='alo186-tv-konsol-yedek-guc-sonucu.json';a.click();URL.revokeObjectURL(url);
  };
  sourceStatus.addEventListener('change',()=>existingFields.classList.toggle('hidden',sourceStatus.value!=='existing'));
  form.addEventListener('submit',(event)=>{event.preventDefault();render(decide(getInput()));});
  form.addEventListener('reset',()=>{setTimeout(()=>{existingFields.classList.add('hidden');result.className='panel result hidden';result.innerHTML='';},0);});
})();
