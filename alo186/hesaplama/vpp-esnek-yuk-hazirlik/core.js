(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&typeof root==='object')root.Alo186VppReadinessCore=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const MAX_SCORE=14;
  const POINTS={history:{none:0,three:1,twelve:2},meter:{invoice:0,fifteen:1,five:2},telemetry:{none:0,local:1,remote:2},control:{manual:0,scheduled:1,remote:2},availability:{unknown:0,partial:1,defined:2},contract:{none:0,research:1,identified:2}};
  function assess(input){
    const assets=Array.isArray(input?.assets)?input.assets:[];
    const values=input?.values||{};
    let rawScore=assets.length?Math.min(2,assets.length):0;
    for(const [key,options] of Object.entries(POINTS))rawScore+=Number(options[values[key]]||0);
    const assetRequired=assets.length===0;
    const score=assetRequired?Math.min(rawScore,8):rawScore;
    const steps=[];
    if(assetRequired)steps.push('Kontrol edilebilir veya ölçülebilir en az bir kaynağı envantere alın; yalnız isim değil güç, enerji ve işletme sınırını kaydedin.');
    if(values.history==='none')steps.push('En az birkaç aylık zaman serisi oluşturarak normal tüketim/üretim bazını görünür kılın.');
    if(values.meter==='invoice')steps.push('Aylık toplam yerine hedef ürünün gerektirdiği zaman çözünürlüğünde sayaç/veri kaynağını doğrulayın.');
    if(values.telemetry==='none')steps.push('Verinin güvenli, zaman damgalı ve kesinti durumunu gösterecek biçimde aktarılma yöntemini tasarlayın.');
    if(values.control==='manual')steps.push('Yetki, fail-safe, yerel öncelik ve siber güvenlik sınırlarıyla programlanabilir/uzak kontrol ihtiyacını değerlendirin.');
    if(values.availability==='unknown')steps.push('Güç, süre, konfor, üretim, SoC ve geri dönüş sınırlarını tanımlayın; teorik kapasiteyi tamamen satılabilir saymayın.');
    if(values.contract==='none')steps.push('Yalnız lisans ve resmî sözleşme kapsamı doğrulanmış toplayıcı/piyasa ürünüyle görüşün; gelir garantisi kabul etmeyin.');
    if(!steps.length)steps.push('Tek hat, sayaç eşlemesi, veri sözlüğü, kontrol senaryosu ve kabul testini bağımsız teknik incelemeyle doğrulayın.');
    let result={band:'discovery',className:'bad',label:'Ön keşif',title:'Önce veri ve kaynak envanteri oluşturun.',summary:'Mevcut bilgiler VPP/toplayıcılık görüşmesinde performans taahhüdü vermek için yeterli görünmüyor.'};
    if(assetRequired){
      result={band:'asset_required',className:'bad',label:'Kaynak envanteri gerekli',title:'Puan ne olursa olsun önce en az bir ölçülebilir veya kontrol edilebilir kaynak tanımlayın.',summary:'Sayaç, telemetri ve kontrol altyapısı hazır olsa bile portföyde hangi kaynağın hangi güç ve süre sınırıyla kullanılacağı bilinmeden teknik görüşmeye hazır sonucu verilemez.'};
    }else if(score>=9){
      result={band:'ready',className:'good',label:'Teknik görüşmeye hazırlanabilir',title:'Temel veri ve kontrol bileşenleri büyük ölçüde tanımlı.',summary:'Bu sonuç piyasa uygunluğu veya gelir onayı değildir. Teknik arayüz, bağlantı, test, siber güvenlik ve sözleşme koşullarını doğrulayarak ilerleyin.'};
    }else if(score>=5){
      result={band:'prepare',className:'warn',label:'Hazırlık geliştirilmeli',title:'Kaynak var; ölçüm, telemetri veya kontrol boşlukları kapanmalı.',summary:'Önce eksik kanıtları tamamlamak, gereksiz donanım alımından ve gerçekçi olmayan kapasite taahhüdünden korur.'};
    }
    return {...result,assets,values,score,rawScore,max:MAX_SCORE,assetRequired,steps,incomeEstimate:false,aggregatorRanking:false,officialApproval:false};
  }
  return {MAX_SCORE,POINTS,assess};
});
