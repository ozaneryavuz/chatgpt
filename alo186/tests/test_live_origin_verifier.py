from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "alo186/deployment/verify_live_origin.py"
spec = importlib.util.spec_from_file_location("verify_live_origin", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

assert module.normalize_origin("https://alo186.com/") == "https://alo186.com"
assert module.normalize_origin("https://www.alo186.com/path") == "https://www.alo186.com"

pages = module.classify_release_response(
    200,
    "application/json; charset=utf-8",
    json.dumps({"hostingMode": "github-pages"}),
)
assert pages == module.PAGES_MODE

sites = module.classify_release_response(
    404,
    "text/html; charset=utf-8",
    '<!doctype html><link rel="stylesheet" href="/build-assets/assets/index.css"><script src="/_vinext/app.js"></script>',
    "vary: RSC, Next-Router-State-Tree",
)
assert sites == module.SITES_MODE

assert module.classify_release_response(404, "text/html", "plain not found") == module.UNKNOWN_MODE
assert module.classify_release_response(200, "text/plain", "{}") == module.UNKNOWN_MODE

safe = '<a href="https://www.amazon.com.tr/example" rel="sponsored nofollow noopener">Ürün</a>'
assert module.validate_affiliate_links(safe) == 1
assert module.validate_affiliate_links('<a href="/akilli-urun-secimi">Yerel</a>') == 0
try:
    module.validate_affiliate_links('<a href="https://amzn.to/example" rel="sponsored">Ürün</a>')
except AssertionError as exc:
    assert "unsafe_affiliate_link" in str(exc)
else:
    raise AssertionError("Eksik affiliate rel tokenları reddedilmeliydi")

try:
    module.normalize_origin("http://alo186.com")
except ValueError:
    pass
else:
    raise AssertionError("HTTP origin reddedilmeliydi")

print(json.dumps({
    "ok": True,
    "modes": [module.PAGES_MODE, module.SITES_MODE],
    "unknownModeFailClosed": True,
    "affiliateRelGuard": True,
    "httpsOnly": True,
}, ensure_ascii=False))
