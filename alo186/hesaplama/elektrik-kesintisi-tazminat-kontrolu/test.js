const fs=require('fs');
const path=require('path');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
for(const token of ['id="checker"','id="result"','12 saati','30 gün','Hizmet Kalitesi Yönetmeliğinin 26 ncı maddesine göre','FAQPage','WebApplication','/edas-bul','ALO186 EDAŞ, TEDAŞ, EPDK veya kamu kurumu değildir','aria-invalid','hours>8760']){
  if(!html.includes(token)) throw new Error(`Eksik sözleşme: ${token}`);
}
for(const forbidden of ['on iş günü','"@type":"Offer"','"@type":"Product"','amazon.com.tr','alo186rehber-21']){
  if(html.includes(forbidden)) throw new Error(`Yasaklı içerik: ${forbidden}`);
}
if(!/addEventListener\('submit'/.test(html)) throw new Error('Karar motoru submit olayı eksik');
console.log('outage compensation checker: PASS');
