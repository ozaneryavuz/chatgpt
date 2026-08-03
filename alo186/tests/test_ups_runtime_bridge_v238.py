from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

import prepare_github_pages as pages  # noqa: E402

ALIAS = "/hesaplama/ups-calisma-suresi"
TARGET = "/hesaplama/yedek-guc-cozum-secici/"

assert pages.choose_bridge_target(ALIAS) == TARGET
assert pages.choose_bridge_target(ALIAS + "/?kaynak=eski") == TARGET
assert pages._core.choose_bridge_target(ALIAS) == TARGET
assert pages.choose_bridge_target("/hesaplama/bilinmeyen-arac") == "/elektrik-portali"

with tempfile.TemporaryDirectory() as temporary:
    site = Path(temporary)
    (site / "index.html").write_text(
        f'<!doctype html><html><body><a href="{ALIAS}">UPS süresi</a></body></html>',
        encoding="utf-8",
    )
    target = site / TARGET.strip("/") / "index.html"
    target.parent.mkdir(parents=True)
    target.write_text("<!doctype html><html><body>Yedek güç seçici</body></html>", encoding="utf-8")

    bridges, generated = pages._core.create_route_bridges(site, "")
    bridge = site / ALIAS.strip("/") / "index.html"
    html = bridge.read_text(encoding="utf-8")

    assert bridges == [{"source": ALIAS, "target": TARGET}]
    assert bridge.resolve() in generated
    assert f'href="{TARGET}"' in html
    assert f'<link rel="canonical" href="https://alo186.com{TARGET}">' in html
    assert "href=\"/elektrik-portali\"" not in html
    assert "noindex,follow" in html

print(json.dumps({
    "ok": True,
    "source": ALIAS,
    "target": TARGET,
    "genericPortalFallbackRemoved": True,
    "canonicalOrigin": "https://alo186.com",
}, ensure_ascii=False))
