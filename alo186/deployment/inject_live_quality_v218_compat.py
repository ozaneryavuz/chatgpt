from __future__ import annotations

import re
from pathlib import Path

import inject_live_quality_v218 as core


def install_quality_css(site: Path) -> dict[str, object]:
    """Inject v218 CSS even when a legacy growth page lost its head terminator.

    The canonical source remains valid, but some late route generators can emit a
    `<head>...<body>` transition without `</head>`. Rather than silently omitting
    the site-wide quality layer, the final artifact repairs that boundary and then
    lets the normal critical-page audit decide whether the page is publishable.
    """

    target = site / core.ASSET_RELATIVE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(core.QUALITY_CSS, encoding="utf-8")
    link = f'<link rel="stylesheet" href="/{core.ASSET_RELATIVE.as_posix()}" {core.STYLE_MARKER}>'
    injected = existing = repaired_head = created_head = 0
    failures: list[str] = []

    for path in sorted(site.rglob("*.html")):
        html = path.read_text(encoding="utf-8", errors="strict")
        if core.STYLE_MARKER in html:
            existing += 1
            continue

        updated, count = re.subn(r"</head\s*>", link + "\n</head>", html, count=1, flags=re.I)
        if count == 1:
            path.write_text(updated, encoding="utf-8")
            injected += 1
            continue

        body = re.search(r"<body\b", html, re.I)
        head = re.search(r"<head\b[^>]*>", html, re.I)
        if body and head and head.start() < body.start():
            updated = html[: body.start()] + link + "\n</head>\n" + html[body.start() :]
            path.write_text(updated, encoding="utf-8")
            injected += 1
            repaired_head += 1
            continue

        html_tag = re.search(r"<html\b[^>]*>", html, re.I)
        if body and html_tag and html_tag.end() <= body.start():
            updated = html[: html_tag.end()] + "\n<head>" + link + "</head>\n" + html[html_tag.end() :]
            path.write_text(updated, encoding="utf-8")
            injected += 1
            created_head += 1
            continue

        failures.append(path.relative_to(site).as_posix())

    if failures:
        raise RuntimeError("Live quality CSS için onarılamayan HTML: " + ", ".join(failures[:30]))
    return {
        "asset": f"/{core.ASSET_RELATIVE.as_posix()}",
        "injectedPages": injected,
        "alreadyPresent": existing,
        "repairedHeadBoundaries": repaired_head,
        "createdHeadElements": created_head,
    }


core.install_quality_css = install_quality_css
run = core.run
main = core.main


if __name__ == "__main__":
    main()
