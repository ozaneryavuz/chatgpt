(function(root,factory){const api=factory(root);if(typeof module==='object'&&module.exports)module.exports=api;root.Alo186PwaInstall=api;})(typeof globalThis!=='undefined'?globalThis:this,function(root){
'use strict';
let deferred=null;
let installed=false;
const listeners=[];
function isStandalone(){return Boolean(root.matchMedia&&root.matchMedia('(display-mode: standalone)').matches)||Boolean(root.navigator&&root.navigator.standalone);}
function isIos(){const ua=String(root.navigator&&root.navigator.userAgent||'');return /iphone|ipad|ipod/i.test(ua);}
function notify(){listeners.forEach(listener=>listener(state()));}
function state(){return{supported:Boolean(deferred),installed:installed||isStandalone(),ios:isIos()};}
function track(name,value){if(typeof root.Alo186Track==='function')root.Alo186Track(name,{status:String(value||'')});}
if(root.addEventListener){root.addEventListener('beforeinstallprompt',event=>{event.preventDefault();deferred=event;notify();track('pwa_install_available','true');});root.addEventListener('appinstalled',()=>{installed=true;deferred=null;notify();track('pwa_install_completed','installed');});}
async function prompt(){if(isStandalone())return{outcome:'installed'};if(!deferred)return{outcome:'unavailable'};const event=deferred;deferred=null;try{await event.prompt();const choice=event.userChoice?await event.userChoice:{outcome:'dismissed'};track('pwa_install_choice',choice.outcome);notify();return choice;}catch(_){notify();return{outcome:'error'};}}
function subscribe(listener){if(typeof listener!=='function')return()=>{};listeners.push(listener);listener(state());return()=>{const index=listeners.indexOf(listener);if(index>=0)listeners.splice(index,1);};}
function bind(options={}){const button=typeof options.button==='string'?root.document&&root.document.getElementById(options.button):options.button;const status=typeof options.status==='string'?root.document&&root.document.getElementById(options.status):options.status;const help=typeof options.help==='string'?root.document&&root.document.getElementById(options.help):options.help;if(!button)return()=>{};
 const render=current=>{if(current.installed){button.hidden=true;if(status)status.textContent='ALO186 bu cihazda uygulama gibi açılabilir.';return;}if(current.supported){button.hidden=false;button.textContent=options.label||'ALO186’i yükle';if(status)status.textContent='Kurulum yalnız açık düğme tıklamanızla başlar; bildirim veya kişisel veri izni istemez.';return;}if(current.ios){button.hidden=false;button.textContent='Ana ekrana ekleme adımları';if(status)status.textContent='iPhone/iPad: Paylaş simgesi → Ana Ekrana Ekle.';return;}button.hidden=true;if(status)status.textContent='Tarayıcınız kurulum düğmesi sunmuyor; tarayıcı menüsündeki “Uygulamayı yükle” veya “Ana ekrana ekle” seçeneğini kullanabilirsiniz.';};
 const unsubscribe=subscribe(render);button.addEventListener('click',async()=>{const current=state();if(current.ios&&!current.supported){if(help)help.textContent='Safari’de Paylaş simgesine dokunun, aşağı kaydırın ve “Ana Ekrana Ekle” seçeneğini kullanın.';track('pwa_install_help_opened','ios');return;}const choice=await prompt();if(status){status.textContent=choice.outcome==='accepted'?'Kurulum kabul edildi.':choice.outcome==='dismissed'?'Kurulum şimdilik ertelendi.':choice.outcome==='installed'?'ALO186 zaten kurulu.':'Kurulum bu tarayıcıda kullanılamıyor.';}});return unsubscribe;}
return{state,prompt,subscribe,bind,isStandalone,isIos};
});
