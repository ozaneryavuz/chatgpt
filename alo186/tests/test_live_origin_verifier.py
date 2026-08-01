from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "alo186/deployment/verify_live_origin.py"
spec = importlib.util.spec_from_file_location("verify_live_origin", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

assert module.normalize_origin("https://alo186.com/") == "https://alo186.com"
assert module.normalize_origin("https://www.alo186.com/path") == "https://www.alo186.com"

pages = module.classify_release_response(
    200,
    "application/json; charset=utf-8",
    json.dumps({"hostingMode": "github-pages"}),
)
assert pages == module.PAGES_MODE

vinext_body = (
    '<!doctype html><link rel="stylesheet" href="/build-assets/assets/index.css">'
    '<script src="/_vinext/app.js"></script>'
)
vinext_headers = "vary: RSC, Next-Router-State-Tree"
sites = module.classify_release_response(
    404,
    "text/html; charset=utf-8",
    vinext_body,
    vinext_headers,
)
assert sites == module.SITES_MODE
assert module.detect_sites_render_signature(vinext_body, vinext_headers) == "vinext/cloudflare"

static_body = (
    '<!doctype html><style data-home-critical-styles></style>'
    '<link rel="preload" as="image" href="/brand/alo186-logo-196.webp" '
    'fetchPriority="high">'
)
static_headers = "x-alo186-render-mode: static-snapshot\nserver: cloudflare"
static_sites = module.classify_release_response(
    404,
    "text/html; charset=utf-8",
    static_body,
    static_headers,
)
assert static_sites == module.SITES_MODE
assert (
    module.detect_sites_render_signature(static_body, static_headers)
    == "static-snapshot/cloudflare"
)

# Static snapshot sınıflandırması yalnız platformun açık render başlığı ve üç
# bağımsız gövde işareti birlikte bulunduğunda açılmalıdır.
assert module.detect_sites_render_signature(static_body, "server: cloudflare") == ""
assert (
    module.detect_sites_render_signature(
        '<style data-home-critical-styles></style>'
        '<link href="/brand/alo186-logo-196.webp">',
        static_headers,
    )
    == ""
)
assert (
    module.classify_release_response(
        404,
        "text/html",
        static_body,
        "x-alo186-render-mode: something-else",
    )
    == module.UNKNOWN_MODE
)

assert module.read_header_value(
    "HTTP/2 200\nX-ALO186-Render-Mode: static-snapshot\n",
    "x-alo186-render-mode",
) == "static-snapshot"
assert module.read_header_value("server: cloudflare\n", "x-alo186-render-mode") == ""

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
    "vinextSignatureGuard": True,
    "staticSnapshotGuard": True,
    "unknownModeFailClosed": True,
    "affiliateRelGuard": True,
    "httpsOnly": True,
}, ensure_ascii=False))
