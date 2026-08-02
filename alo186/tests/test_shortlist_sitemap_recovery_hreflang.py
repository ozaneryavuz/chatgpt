from __future__ import annotations

import importlib.util
import json
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
DEPLOY = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOY))
spec = importlib.util.spec_from_file_location("shortlist_growth", DEPLOY / "inject_shortlist_growth.py")
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

SITEMAP = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML = "http://www.w3.org/1999/xhtml"

def fake_writer(output: Path, manifest: dict) -> None:
    ET.register_namespace("", SITEMAP)
    ET.register_namespace("xhtml", XHTML)
    root = ET.Element(f"{{{SITEMAP}}}urlset")
    url = ET.SubElement(root, f"{{{SITEMAP}}}url")
    ET.SubElement(url, f"{{{SITEMAP}}}loc").text = manifest["canonicalHost"] + manifest["routes"][0]["canonicalPath"]
    ET.SubElement(url, f"{{{XHTML}}}link", {"rel":"alternate","hreflang":"en","href":manifest["canonicalHost"] + "/en/"})
    ET.ElementTree(root).write(output / "sitemap.xml", encoding="utf-8", xml_declaration=True)

with tempfile.TemporaryDirectory() as tmp:
    site = Path(tmp)
    (site / "sitemap.xml").write_text("<urlset><url>", encoding="utf-8")
    (site / "alo186-release.json").write_text(json.dumps({
        "canonicalHost":"https://alo186.com",
        "routes":[{"canonicalPath":"/active/","source":"alo186/active/index.html","type":"tool"}]
    }), encoding="utf-8")
    module.write_effective_sitemap = fake_writer
    result = module.reconcile_sitemap_with_release(site)
    assert result["recoveredMalformedSitemap"] is True
    tree = ET.parse(site / "sitemap.xml")
    assert len(tree.getroot().findall(f".//{{{XHTML}}}link")) == 1
    locs = [node.text for node in tree.getroot().findall(f".//{{{SITEMAP}}}loc")]
    assert locs == ["https://alo186.com/active/"]
print("Shortlist sitemap recovery hreflang: PASS")
