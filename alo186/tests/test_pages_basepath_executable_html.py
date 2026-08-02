from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "alo186/deployment/smoke_github_pages.py"
spec = importlib.util.spec_from_file_location("smoke_pages", MODULE)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

html = """<section data-route=\"/hesaplama/\"></section><script>fetch('/assets/app.js');location.href='/route';</script><style>.x{background:url('/assets/a.png')}</style>"""
scan = module.executable_html_text(html)
assert 'data-route' not in scan
assert "fetch('/assets/app.js')" in scan
assert "location.href='/route'" in scan
assert "url('/assets/a.png')" in scan
print('Pages executable HTML base-path guard: PASS')
