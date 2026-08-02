const fs=require('fs');
const path=require('path');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
for(const token of ['id="selector"','id="result"','6 mA DC','IEC 62955','IEC 62752','Mode 2: IC-CPD + üst tesisat Tip A adayı','Mode 3: Tip A + doğrulanmış 6 mA DC RDC-DD adayı',"mode==='unknown'","external==='none'",'Tip A','Tip B','ayrı devre','WebApplication','ALO186 ürün satıcısı, şarj ağı işletmecisi, EDAŞ veya kamu kurumu değildir']){
  if(!html.includes(token)) throw new Error(`Eksik sözleşme: ${token}`);
}
for(const forbidden of ['"@type":"Offer"','"@type":"Product"','amazon.com.tr','alo186rehber-21']){
  if(html.includes(forbidden)) throw new Error(`Yasaklı içerik: ${forbidden}`);
}
if(!html.includes('yalnız standart Tip AC')) throw new Error('Tip AC güvenlik sınırı eksik');
console.log('EV residual-current selector: PASS');
