(() => {
  'use strict';
  const ROUTE='/sektor-rehberi/kritik-sistemler-yedek-guc-test-merkezi/';
  const SYSTEMS={
    aquarium:{title:'Akvaryum yaşam desteği',route:'/hesaplama/akvaryum-elektrik-kesintisi-yedek-guc-uygunluk/',first:'Elektrik-su temasını ve canlılarda stres belirtisini kontrol edin.',checks:['Hava motoru ve su hareketi','Gerçek W ve hedef süre','Damlama döngüsü ve kuru yerleşim','Transfer ve gerçek süre testi']},
    cctv:{title:'Kamera, NVR ve PoE sistemi',route:'/hesaplama/kamera-nvr-poe-ups-uygunluk/',first:'NVR, PoE switch, kameralar ve ağ cihazlarını tek güç ağacı olarak çıkarın.',checks:['NVR ve disk','PoE switch ve kameralar','Modem/ONT','Gerçek kayıt ve zaman damgası testi']},
    internet:{title:'Modem ve ONT',route:'/hesaplama/modem-internet-yedekleme/',first:'Modem ve ONT adaptör değerlerini ayrı doğrulayın.',checks:['Modem ve ONT voltaj/polarite','Toplam W','DC kablo uyumu','Operatör altyapısı bağımlılığı']},
    cold_chain:{title:'Buzdolabı ve dondurucu',route:'/amazon-elektrik-urunleri/buzdolabi-dondurucu-power-station-secimi/',first:'Aktif kesintide kapıları kapalı tutun ve süre/sıcaklık kaydı alın.',checks:['Sıcaklık ve süre kaydı','Kompresör sürekli/kalkış W','Gerçek başlatma testi','Gıda güvenliği kararı']},
    computer:{title:'Bilgisayar, gaming PC ve NAS',route:'/hesaplama/bilgisayar-gaming-pc-nas-ups-uygunluk/',first:'Veri kaybını önlemek için gerçek yük ve güvenli kapatma süresini ayırın.',checks:['PC/NAS gerçek W','UPS W ve VA sınırı','USB/ağ kapatma iletişimi','Transfer ve güvenli kapanma']},
    entertainment:{title:'TV, oyun konsolu ve modem',route:'/hesaplama/tv-oyun-konsolu-modem-yedek-guc-uygunluk/',first:'Eşzamanlı TV, konsol, modem/ONT ve ses yükünü toplayın.',checks:['Toplam gerçek W','UPS VA','Hedef Wh','Yeniden başlama/transfer testi']},
    medical:{title:'Tıbbi ve yaşam desteği cihazı',route:'/hesaplama/cpap-apap-bipap-yedek-guc-uygunluk/',first:'Üretici, sağlık profesyoneli ve acil durum planını ürün alışverişinden önce doğrulayın.',checks:['Üretici onayı','Klinik/acil plan','Test edilmiş mevcut kaynak','112 ve alternatif bakım rotası']}
  };
  const makePlan=(input)=>{
    const system=SYSTEMS[input.systemType]||SYSTEMS.internet;
    const active=input.scenario==='active';
    const emergency=input.emergency;
    let title=`${system.title} için test planı`;
    let commerce=false;
    let action=system.first;
    if(emergency){title='Önce can güvenliği ve elektrik riskini ayırın';action='Duman, yangın, elektrik çarpması veya su teması varsa yaklaşmayın; güvenli alana geçin ve gerektiğinde 112’yi arayın.';}
    else if(active){title=`${system.title}: aktif kesintide önce mevcut güvenli plan`;action=`${system.first} Henüz satın alınmamış ürün devam eden kesintide anlık çözüm değildir.`;}
    else if(input.systemType!=='medical'){commerce=true;}
    return {systemType:input.systemType,system,scenario:input.scenario,frequencyDays:Number(input.frequencyDays)||90,title,action,checks:system.checks,route:system.route,commerce,emergency};
  };
  if(typeof module!=='undefined' && module.exports){module.exports={ROUTE,SYSTEMS,makePlan};return;}
  const $=(id)=>document.getElementById(id);
  const form=$('planForm');
  const result=$('result');
  const getInput=()=>({emergency:$('emergency').checked,systemType:$('systemType').value,scenario:$('scenario').value,frequencyDays:$('frequencyDays').value});
  const render=(plan)=>{
    const affiliate=plan.commerce?'<p class="hint"><strong>Ticari sınır:</strong> Bağlı hesaplayıcı gerçek teknik açık bulursa satış ortaklığı içeren ürün sınıfı gösterebilir. Fiyat, stok, puan ve garanti ALO186 üzerinde yayımlanmaz; mevcut çözüm yeterliyse yeni ürün önerilmez.</p>':'<p class="hint"><strong>Ticari yol kapalı:</strong> Acil veya tıbbi yaşam desteği bağlamında ürün yönlendirmesi bu planın amacı değildir.</p>';
    result.className=`panel result ${plan.emergency?'stop':'warn'}`;
    result.innerHTML=`<h2>${plan.title}</h2><div class="callout ${plan.emergency?'danger':''}"><strong>İlk adım:</strong> ${plan.action}</div><h3>Kontrol listesi</h3><ol class="steps">${plan.checks.map(item=>`<li>${item}</li>`).join('')}</ol>${affiliate}<div class="actions"><a class="button primary" href="${plan.route}">İlgili aracı aç</a><button id="jsonBtn" class="button" type="button">Planı JSON indir</button><button id="icsBtn" class="button" type="button">${plan.frequencyDays} günlük test takvimi indir</button></div>`;
    result.classList.remove('hidden');result.focus();
    $('jsonBtn')?.addEventListener('click',()=>downloadJson(plan));
    $('icsBtn')?.addEventListener('click',()=>downloadIcs(plan));
  };
  const saveBlob=(content,type,name)=>{const blob=new Blob([content],{type});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();URL.revokeObjectURL(url);};
  const downloadJson=(plan)=>saveBlob(JSON.stringify({schema:'alo186-critical-systems-test-plan-v1',route:ROUTE,createdAt:new Date().toISOString(),personalData:false,plan},null,2),'application/json','alo186-kritik-sistem-test-plani.json');
  const pad=(v)=>String(v).padStart(2,'0');
  const stamp=(date)=>`${date.getUTCFullYear()}${pad(date.getUTCMonth()+1)}${pad(date.getUTCDate())}T${pad(date.getUTCHours())}${pad(date.getUTCMinutes())}00Z`;
  const escapeIcs=(value)=>String(value).replace(/\\/g,'\\\\').replace(/,/g,'\\,').replace(/;/g,'\\;').replace(/\n/g,'\\n');
  const downloadIcs=(plan)=>{const start=new Date();start.setDate(start.getDate()+plan.frequencyDays);start.setHours(10,0,0,0);const end=new Date(start.getTime()+45*60*1000);const description=`${plan.action} Kontroller: ${plan.checks.join('; ')}. Mevcut kaynak yeterliyse yeni ürün almayın.`;const ics=`BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//ALO186//Kritik Sistem Test Plani//TR\r\nBEGIN:VEVENT\r\nUID:critical-${Date.now()}@alo186.com\r\nDTSTAMP:${stamp(new Date())}\r\nDTSTART:${stamp(start)}\r\nDTEND:${stamp(end)}\r\nSUMMARY:${escapeIcs(plan.system.title)} yedek güç testi\r\nDESCRIPTION:${escapeIcs(description)}\r\nURL:https://alo186.com${plan.route}\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n`;saveBlob(ics,'text/calendar',`alo186-${plan.systemType}-${plan.frequencyDays}-gun-test.ics`);};
  form.addEventListener('submit',(event)=>{event.preventDefault();render(makePlan(getInput()));});
  form.addEventListener('reset',()=>setTimeout(()=>{result.className='panel result hidden';result.innerHTML='';},0));
})();
