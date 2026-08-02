const fs=require('fs');
const path=require('path');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
for(const token of ['id="selector"','id="result"','anti-islanding','IEC 62116','kritik yük panosu','nötr-topraklama','WebApplication',"pv==='unknown'",'Önce inverter modelini ve topolojiyi doğrulayın','hours<0.5||hours>72','aria-invalid','Mevcut string inverter için koşullu AC bağlı depolama adayı','Hibrit etiketi yeterli değildir','ALO186 EPC, inverter üreticisi, elektrik yüklenicisi, EDAŞ veya resmî kabul kuruluşu değildir']){
  if(!html.includes(token)) throw new Error(`Eksik sözleşme: ${token}`);
}
for(const forbidden of ['"@type":"Offer"','"@type":"Product"','amazon.com.tr','alo186rehber-21']){
  if(html.includes(forbidden)) throw new Error(`Yasaklı içerik: ${forbidden}`);
}
if(!html.includes('geri besleme yapmayın')) throw new Error('Geri besleme güvenlik sınırı eksik');
console.log('PV backup architecture selector: PASS');
