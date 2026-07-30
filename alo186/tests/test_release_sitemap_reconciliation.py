from __future__ import annotations
import json,sys,tempfile,xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'alo186'/'deployment'))
from inject_shortlist_growth import reconcile_sitemap_with_release
def main()->None:
    with tempfile.TemporaryDirectory() as directory:
        site=Path(directory)
        site.joinpath('sitemap.xml').write_text('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://alo186.com/existing</loc></url></urlset>',encoding='utf-8')
        routes=[{'canonicalPath':'/existing','source':'alo186/existing/index.html','type':'article'},{'canonicalPath':'/haberler/elektrik-ark-hatasi-afdd-rcd-sigorta-farki','source':'alo186/haberler/elektrik-ark-hatasi-afdd-rcd-sigorta-farki/index.html','type':'article'}]
        site.joinpath('alo186-release.json').write_text(json.dumps({'canonicalHost':'https://alo186.com','routes':routes}),encoding='utf-8')
        result=reconcile_sitemap_with_release(site)
        assert result['addedCount']==1,result
        paths={(urlsplit(node.text or '').path.rstrip('/') or '/') for node in ET.parse(site/'sitemap.xml').getroot().iter() if node.tag.endswith('loc')}
        assert paths=={'/existing','/haberler/elektrik-ark-hatasi-afdd-rcd-sigorta-farki'},paths
    print({'ok':True,'policy':'active release routes reconciled after growth injectors'})
if __name__=='__main__': main()
