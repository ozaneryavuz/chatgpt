(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;root.Alo186CorporateReadiness=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const allowed={facility:['hotel','site','restaurant','office','industrial'],problem:['outage','voltage','backup','energy','ev','audit'],backup:['none','ups','generator','both','solar_storage'],scope:['remote','comparison','site','roadmap'],urgency:['urgent','soon','planning'],evidence:['none','partial','ready']};
  const commonDocs=['Tek hat şeması veya güncel pano/dağıtım özeti','Kritik yük listesi ve yaklaşık çalışma süreleri','Son kesinti/gerilim olaylarının tarih-süre kaydı','Mevcut UPS, jeneratör, GES veya batarya etiket bilgileri'];
  const problemDocs={outage:['Kesinti günlüğü ve jeneratör/UPS test kayıtları'],voltage:['Gerilim ölçüm kayıtları, cihaz hasarı ve servis raporları'],backup:['Sürekli/kalkış güçleri ve mevcut kapasite bilgileri'],energy:['Son 12 aylık tüketim-fatura özeti; abone numarası ve adres kapatılabilir'],ev:['Araç AC/DC sınırı, ana güç ve otopark/hat planı'],audit:['Bakım, topraklama, RCD, termal ve güç kalitesi raporları']};
  const facilityDocs={hotel:['Oda, mutfak, soğuk oda, asansör ve ortak alan kritik yük ayrımı'],site:['Blok, hidrofor, asansör, yangın ve ortak alan kritik yük ayrımı'],restaurant:['Soğuk zincir, mutfak ve satış sistemi kritik yük listesi'],office:['Sunucu, internet, güvenlik ve iş sürekliliği kritik yükleri'],industrial:['Motor, sürücü, kompresör ve proses duruş etkisi']};
  function valid(group,value){return allowed[group].includes(String(value));}
  function unique(items){return [...new Set(items.filter(Boolean))];}
  function assess(input={}){
    const data={};for(const key of Object.keys(allowed)){data[key]=valid(key,input[key])?String(input[key]):allowed[key][0];}
    let score=0;
    score+=data.evidence==='ready'?40:data.evidence==='partial'?24:8;
    score+=data.backup==='none'?5:15;
    score+=data.scope==='site'?25:data.scope==='comparison'?22:data.scope==='roadmap'?18:15;
    score+=data.urgency==='urgent'?15:data.urgency==='soon'?10:5;
    score=Math.min(100,score);
    const band=score>=80?'ready':score>=58?'partial':'prepare';
    const label=band==='ready'?'Ön görüşmeye hazır':band==='partial'?'Kısmen hazır':'Belge hazırlığı gerekli';
    const docs=unique([...commonDocs,...(problemDocs[data.problem]||[]),...(facilityDocs[data.facility]||[])]);
    const next=band==='ready'?'Talebi e-posta ile gönderip kapsam ve ücret teyidi isteyin.':band==='partial'?'Eksik belgeleri tamamlayın veya uzaktan ön incelemeyle başlayın.':'Önce kritik yük, olay kaydı ve mevcut sistem etiketlerini hazırlayın.';
    return {data,score,band,label,docs,next};
  }
  function brief(readable,assessment){
    return ['ALO186 Kurumsal Elektrik Sürekliliği Ön Değerlendirmesi','',`Hazırlık skoru: ${assessment.score}/100 — ${assessment.label}`,`Tesis türü: ${readable.facility}`,`Ana problem: ${readable.problem}`,`Mevcut yedek kaynak: ${readable.backup}`,`İstenen kapsam: ${readable.scope}`,`Karar zamanı: ${readable.urgency}`,`Belge hazırlığı: ${readable.evidence}`,'','İlk inceleme için önerilen belgeler:',...assessment.docs.map((item)=>`- ${item}`),'',`Sonraki adım: ${assessment.next}`,'','Not: Bu özet resmî arıza/şikâyet kaydı, fiyat teklifi veya teknik uygunluk onayı değildir.'].join('\n');
  }
  return {assess,brief,allowed};
});
