(function(){
  'use strict';

  window.Alo186Track=function(name,params){
    const data=Object.assign({event:name,tool_location:location.pathname},params||{});
    window.dataLayer=window.dataLayer||[];
    window.dataLayer.push(data);
    window.dispatchEvent(new CustomEvent('alo186:event',{detail:data}));
  };

  window.fmt=function(value,digits=1,unit=''){
    return new Intl.NumberFormat('tr-TR',{maximumFractionDigits:digits,minimumFractionDigits:0}).format(value)+(unit?' '+unit:'');
  };

  window.copyText=async function(text,button){
    try{
      await navigator.clipboard.writeText(text);
      if(button){
        const old=button.textContent;
        button.textContent='Kopyalandı';
        setTimeout(()=>button.textContent=old,1600);
      }
    }catch(e){
      alert('Kopyalama başarısız. Metni manuel seçebilirsiniz.');
    }
  };

  document.querySelectorAll('[data-print]').forEach(button=>button.addEventListener('click',()=>window.print()));

  if(!window.Alo186OutcomeBridge&&!document.querySelector('script[data-alo186-outcome-bridge]')){
    const current=document.currentScript;
    const source=current&&current.src?new URL('outcome-bridge.js',current.src).href:'/hesaplama/outcome-bridge.js';
    const script=document.createElement('script');
    script.src=source;
    script.dataset.alo186OutcomeBridge='true';
    script.defer=true;
    document.head.appendChild(script);
  }
})();
