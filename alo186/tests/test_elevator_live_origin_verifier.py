from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "alo186/deployment/verify_elevator_live_origin.py"
spec = importlib.util.spec_from_file_location("verify_elevator_live_origin", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

assert module.normalize_origin("https://alo186.com/") == "https://alo186.com"
try:
    module.normalize_origin("http://alo186.com")
except ValueError:
    pass
else:
    raise AssertionError("HTTP origin reddedilmeliydi")

assert len(module.ROUTES) == 3
assert len({route.path for route in module.ROUTES}) == 3
assert all(route.path.endswith("/") for route in module.ROUTES)

first = module.ROUTES[0]
valid_html = f"""<!doctype html>
<html lang="tr"><head>
<title>{first.title} | ALO186</title>
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="https://alo186.com{first.path}">
<script type="application/ld+json">{{
  "@context":"https://schema.org",
  "@graph":[
    {{"@type":"WebApplication"}},
    {{"@type":"FAQPage"}},
    {{"@type":"BreadcrumbList"}}
  ]
}}</script>
</head><body>
<h1>{first.title}</h1>
<p>Kapıyı zorlamayın. İki yönlü haberleşme sistemini kullanın; sağlık veya yangın acilinde 112.</p>
{'güvenli içerik ' * 100}
</body></html>"""
report = module.audit_html(
    valid_html,
    first,
    effective_url=f"https://alo186.com{first.path}?live_receipt=test",
)
assert report["ok"], report
assert report["affiliateLinks"] == []
assert set(report["requiredSchemaTypes"]) <= set(report["schemaTypes"])

noindex = valid_html.replace("index,follow,max-image-preview:large", "noindex,follow")
report = module.audit_html(noindex, first)
assert not report["ok"]
assert "route_must_be_indexable" in report["issues"]

wrong_canonical = valid_html.replace(
    f"https://alo186.com{first.path}",
    "https://alo186.com/yanlis-rota/",
)
report = module.audit_html(wrong_canonical, first)
assert "canonical_mismatch" in report["issues"]

missing_schema = valid_html.replace('{"@type":"FAQPage"},', "")
report = module.audit_html(missing_schema, first)
assert any(issue.startswith("schema_types_missing:") for issue in report["issues"])

commercial = valid_html.replace(
    "</body>",
    '<a href="https://www.amazon.com.tr/example">Ürün</a></body>',
)
report = module.audit_html(commercial, first)
assert "affiliate_links_forbidden" in report["issues"]

wrong_route = module.audit_html(
    valid_html,
    first,
    effective_url="https://alo186.com/hesaplama/baska/",
)
assert "effective_path_mismatch" in wrong_route["issues"]

sitemap = "<?xml version='1.0'?><urlset>" + "".join(
    f"<url><loc>https://alo186.com{route.path}</loc></url>" for route in module.ROUTES
) + "</urlset>"
sitemap_report = module.audit_sitemap(sitemap)
assert sitemap_report["ok"], sitemap_report

missing_sitemap = sitemap.replace(f"<url><loc>https://alo186.com{module.ROUTES[-1].path}</loc></url>", "")
sitemap_report = module.audit_sitemap(missing_sitemap)
assert not sitemap_report["ok"]
assert "sitemap_routes_missing" in sitemap_report["issues"]

robots_report = module.audit_robots("User-agent: *\nAllow: /\nSitemap: https://alo186.com/sitemap.xml\n")
assert robots_report["ok"], robots_report
blocked_robots = module.audit_robots("User-agent: *\nDisallow: /\n")
assert not blocked_robots["ok"]
assert "robots_blocks_entire_site" in blocked_robots["issues"]

print(json.dumps({
    "ok": True,
    "routeCount": len(module.ROUTES),
    "canonicalGuard": True,
    "indexabilityGuard": True,
    "schemaGuard": True,
    "affiliateGuard": True,
    "sitemapGuard": True,
    "robotsGuard": True,
}, ensure_ascii=False))
