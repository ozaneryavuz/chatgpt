const fs = require('fs');
const path = require('path');

const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');

for (const token of [
  'id="checker"',
  'id="result"',
  '12 saati',
  '30 gün',
  'FAQPage',
  'WebApplication',
  '/edas-bul',
  'data-evidence-download',
  'outage_compensation_result'
]) {
  if (!html.includes(token)) throw new Error(`Eksik sözleşme: ${token}`);
}

for (const forbidden of ['on iş günü', '10 iş günü', '"@type":"Offer"', 'amazon.com.tr', 'alo186rehber-21']) {
  if (html.includes(forbidden)) throw new Error(`Yasaklı içerik: ${forbidden}`);
}
if (!/addEventListener\('submit'/.test(html)) throw new Error('Karar motoru submit olayı eksik');
if (!/Blob\(/.test(html)) throw new Error('Kanıt dosyası indirme işlevi eksik');

console.log('outage compensation checker: PASS');
