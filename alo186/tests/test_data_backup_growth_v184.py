from pathlib import Path
import json,re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[2]
PAGES=[
 ROOT/'alo186/hesaplama/elektrik-kesintisi-bilgisayar-veri-yedekleme-rpo-rto-plani/index.html',
 ROOT/'alo186/amazon-elektrik-urunleri/harici-ssd-hdd-usb-yedekleme-urun-secici/index.html',
 ROOT/'alo186/sektor-rehberi/ev-ofis-veri-yedekleme-geri-yukleme-test-merkezi/index.html']
for p in PAGES:
 assert p.exists(),p
 s=p.read_text(encoding='utf-8')
 assert '<link rel="canonical" href="https://alo186.com/' in s
 assert 'FAQPage' in s and 'BreadcrumbList' in s and 'WebApplication' in s
 assert 'resmî kurum değildir' in s
 assert 'Product' not in s and 'Offer' not in s and 'aggregateRating' not in s and 'availability' not in s
 assert not re.search(r'href="https://www\.amazon\.com\.tr',s)
 scripts=re.findall(r'<script>(.*?)</script>',s,re.S)
 assert scripts
 with tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf-8') as f:
  f.write('\n'.join(scripts)); name=f.name
 subprocess.run(['node','--check',name],check=True,capture_output=True,text=True)
calc=PAGES[0].read_text(encoding='utf-8')
assert 'RPO' in calc and 'RTO' in calc and 'yeni ürün almayın' in calc.lower()
assert 'needConfirm' in calc and 'specConfirm' in calc and 'adConfirm' in calc
assert 'alo186rehber-21' in calc and 'sponsored nofollow noopener' in calc
selector=PAGES[1].read_text(encoding='utf-8')
for term in ['Taşınabilir SSD','Harici HDD','USB bellek','NVMe']:
 assert term in selector
assert 'slice(0,3)' in selector
assert 'needConfirm' in selector and 'specConfirm' in selector and 'adConfirm' in selector
assert 'alo186rehber-21' in selector and 'sponsored nofollow noopener' in selector
tracker=PAGES[2].read_text(encoding='utf-8')
assert '7/30/90' in tracker and 'application/json' in tracker and 'text/calendar' in tracker
assert 'kişisel veri' in tracker.lower() and 'yeni ürün almayın' in tracker.lower()
overlay=ROOT/'alo186/deployment/routing-overlays/184-data-backup-growth.json'
data=json.loads(overlay.read_text(encoding='utf-8'))
assert data['version']==184 and len(data['routes'])==3
assert len({r['canonicalPath'] for r in data['routes']})==3
print('ALO186 data backup growth v184 contract passed')
