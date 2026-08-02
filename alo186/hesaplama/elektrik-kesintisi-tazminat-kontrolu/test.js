const fs=require('fs');
const path=require('path');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
for(const token of [
  'id="checker"',
  'id="result"',
  'id="downloadEvidence"',
  '12 saati',
  '30 gün',
  'Hizmet Kalitesi Yönetmeliğinin 26 ncı maddesine göre',
  'FAQPage',
  'WebApplication',
  '/edas-bul',
  'ALO186 EDAŞ, TEDAŞ, EPDK veya kamu kurumu değildir',
  'const rawHours=input.value.trim()',
  "rawHours===''?Number.NaN:Number(rawHours)",
  'const valid=rawHours!==',
  'aria-invalid',
  'alo186-kesinti-tazminati-kanit-plani.txt',
  'outage_compensation_result',
  'outage_compensation_evidence_download',
  'Dosya yalnız bu cihazda oluşturulur',
  "window.dataLayer.push({event:eventName,result_class:resultClass,tool:'outage_compensation',alo186_no_pii:true})"
]){
  if(!html.includes(token)) throw new Error(`Eksik sözleşme: ${token}`);
}
for(const forbidden of ['on iş günü','"@type":"Offer"','"@type":"Product"','amazon.com.tr','alo186rehber-21']){
  if(html.includes(forbidden)) throw new Error(`Yasaklı içerik: ${forbidden}`);
}
if(!/addEventListener\('submit'/.test(html)) throw new Error('Karar motoru submit olayı eksik');
if(/dataLayer\.push\([^)]*(?:hours|rawHours|noticeText|causeText|repeatedText)/s.test(html)) throw new Error('Kullanıcı girdisi analitiğe gönderilemez');
if(!/new Blob\(\[evidenceText\]/.test(html)) throw new Error('Yerel kanıt dosyası üretimi eksik');
console.log('outage compensation evidence plan: PASS');
