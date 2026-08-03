(()=>{
  'use strict';
  const catalog=globalThis.Alo186UsbEthernetAdapterCatalogV237;
  const ids=['toolNeed','toolUsb','toolCable','toolSpeed','toolNoPoe','toolScope'];
  const result=document.getElementById('toolResult'); const panel=document.getElementById('gatePanel');
  const need=document.getElementById('gateNeed'); const affiliate=document.getElementById('gateAffiliate');
  const status=document.getElementById('gateStatus'); const links=[...document.querySelectorAll('[data-affiliate-asin]')];
  let toolPassed=false;
  function lock(message='Mağaza bağlantıları kapalı.'){
    links.forEach((link)=>{link.removeAttribute('href');link.removeAttribute('target');link.classList.add('locked');link.setAttribute('aria-disabled','true');link.setAttribute('tabindex','-1');});
    panel.dataset.open='false'; status.textContent=message;
  }
  function sync(){
    const contract=catalog&&catalog.category.affiliatePolicy === 'after_tool'&&catalog.category.professionalOnly === false;
    const fresh=catalog&&catalog.verificationStatus(new Date()).fresh;
    const open=Boolean(contract&&fresh&&toolPassed&&need.checked&&affiliate.checked);
    if(!open){lock(fresh?'Ön kontrol ve açık onay tamamlanmadan bağlantılar kapalı.':'Ürün kimliği doğrulaması 45 günü aştı; bağlantılar kapalı.');return;}
    links.forEach((link)=>{link.href=catalog.amazonProductUrl(link.dataset.affiliateAsin);link.target='_blank';link.rel='sponsored nofollow noopener';link.classList.remove('locked');link.setAttribute('aria-disabled','false');link.removeAttribute('tabindex');});
    panel.dataset.open='true'; status.textContent='Bağlantılar açıldı. Amazon kaydında ASIN, MPN, port ve link hızını yeniden doğrulayın.';
  }
  document.getElementById('runCompatibilityTool').addEventListener('click',()=>{
    toolPassed=ids.every((id)=>document.getElementById(id).checked);
    result.dataset.passed=String(toolPassed);
    result.textContent=toolPassed?'Ön kontrol geçti. Ürün sınırlamalarını okuyup satış ortaklığı onaylarını tamamlayın.':'Tüm teknik ve kapsam kontrolleri tamamlanmadı. Mevcut çözüm yeterliyse yeni ürün almayın.';
    sync();
  });
  [need,affiliate].forEach((control)=>control.addEventListener('change',sync));
  document.getElementById('resetGate').addEventListener('click',()=>{toolPassed=false;ids.forEach((id)=>document.getElementById(id).checked=false);need.checked=false;affiliate.checked=false;result.dataset.passed='false';result.textContent='Kontroller sıfırlandı.';lock();});
  const revisitDate=new Date(Date.now()+90 * 24 * 60 * 60 * 1000);
  const pad=(value)=>String(value).padStart(2,'0');
  const stamp=`${revisitDate.getUTCFullYear()}${pad(revisitDate.getUTCMonth()+1)}${pad(revisitDate.getUTCDate())}T090000Z`;
  const calendar=`BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//ALO186//USB Ethernet yeniden test//TR\r\nBEGIN:VEVENT\r\nDTSTART:${stamp}\r\nSUMMARY:USB Ethernet link hızını yeniden ölç\r\nDESCRIPTION:Port kablo modem switch ve gerçek link hızını yeniden doğrula. Ad, e-posta, adres veya seri numarası istenmez.\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n`;
  const blob=new Blob([calendar],{type:'text/calendar;charset=utf-8'}); URL.revokeObjectURL(URL.createObjectURL(blob));
  lock();
})();
