from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSS_PATH = ROOT / "alo186" / "assets" / "alo186-accessibility-v215.css"
BUILDER_PATH = ROOT / "alo186" / "deployment" / "build_static_site.py"


def rule_body(css: str, selector: str) -> str:
    pattern = re.compile(re.escape(selector) + r"\s*\{(?P<body>.*?)\}", re.DOTALL)
    match = pattern.search(css)
    assert match, f"CSS kuralı bulunamadı: {selector}"
    return re.sub(r"\s+", "", match.group("body"))


def test_footer_targets_are_real_boxes() -> None:
    css = CSS_PATH.read_text(encoding="utf-8")
    body = rule_body(css, "body footer a[href]")
    assert "display:inline-flex;" in body
    assert "min-inline-size:44px;" in body
    assert "min-block-size:48px;" in body
    assert "align-items:center;" in body
    assert "padding:.625rem.5rem;" in body
    assert "margin:.125rem.25rem.125rem0;" in body
    assert "touch-action:manipulation;" in body


def test_reported_footer_routes_have_fail_closed_override() -> None:
    css = CSS_PATH.read_text(encoding="utf-8")
    for route in ("/haberler", "/haberler/", "/guvenlik-rehberleri", "/guvenlik-rehberleri/"):
        assert f'body footer a[href$="{route}"]' in css
    assert css.count("min-block-size:48px!important") == 1
    assert css.count("padding-block:.625rem!important") == 1


def test_v215_is_cache_busted_and_published_last() -> None:
    builder = BUILDER_PATH.read_text(encoding="utf-8")
    assert 'data-alo186-accessibility-v215="true"' in builder
    assert 'alo186/assets/alo186-accessibility-v215.css' in builder
    assert 'assets/alo186-accessibility-v215.css' in builder
    assert '"version": 215' in builder
    assert '"footerMinimumTouchTargetPx": 48' in builder
    assert '"accessibilityHardeningV215"' in builder
    assert 're.sub(r"</head\\s*>", link + "\\n</head>"' in builder


if __name__ == "__main__":
    test_footer_targets_are_real_boxes()
    test_reported_footer_routes_have_fail_closed_override()
    test_v215_is_cache_busted_and_published_last()
    print("ALO186 footer touch targets v215: PASS")
