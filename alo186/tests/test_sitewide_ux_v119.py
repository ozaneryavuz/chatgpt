from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
css = (ROOT / "alo186/assets/alo186-ux.css").read_text(encoding="utf-8")

required = (
    "@media (forced-colors: active)",
    "@media (prefers-contrast: more)",
    "border: 2px solid CanvasText",
    "color: HighlightText",
    "background: Highlight",
    "outline: 3px solid Highlight",
    "grid-template-columns: repeat(4, minmax(0, 1fr))",
    ".alo-ux-mobilebar a { min-width: 0;",
)
for token in required:
    assert token in css, token

assert "outline: 0" not in css
assert "outline:none" not in css.replace(" ", "")

print({
    "ok": True,
    "forcedColors": True,
    "prefersContrast": True,
    "visibleFocus": True,
    "mobileMinWidthGuard": True,
})
