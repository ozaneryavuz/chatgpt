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

  const current=document.currentScript;
  const commonUrl=current&&current.src?current.src:'/hesaplama/common.js';
  if(!window.Alo186OutcomeBridge&&!document.querySelector('script[data-alo186-outcome-bridge]')){
    const script=document.createElement('script');
    script.src=new URL('outcome-bridge.js',commonUrl).href;
    script.dataset.alo186OutcomeBridge='true';
    script.defer=true;
    document.head.appendChild(script);
  }

  if(/\/(akilli-urun-secimi|amazon-elektrik-urunleri)\/?$/.test(location.pathname)&&!document.querySelector('script[data-alo186-outcome-trust-core]')){
    const coreScript=document.createElement('script');
    coreScript.src=new URL('../urun-eslestirme/outcome-trust-circuit-core.js',commonUrl).href;
    coreScript.dataset.alo186OutcomeTrustCore='true';
    coreScript.addEventListener('load',()=>{
      if(document.querySelector('script[data-alo186-outcome-trust-ui]'))return;
      const uiScript=document.createElement('script');
      uiScript.src=new URL('../urun-eslestirme/outcome-trust-circuit.js',commonUrl).href;
      uiScript.dataset.alo186OutcomeTrustUi='true';
      uiScript.defer=true;
      document.head.appendChild(uiScript);
    },{once:true});
    document.head.appendChild(coreScript);
  }
})();
