from __future__ import annotations

import re
from pathlib import Path

import inject_live_quality_v218 as core


SKIP_LINK_PATTERN = re.compile(
    r'(<a\b(?=[^>]*\bclass=["\'][^"\']*\bskip-link\b[^"\']*["\'])[^>]*\bhref=["\'])[^"\']*(["\'][^>]*>)',
    re.I,
)
MAIN_PATTERN = re.compile(r'<main\b(?P<attrs>[^>]*)>', re.I)
BODY_PATTERN = re.compile(r'<body\b[^>]*>', re.I)
ID_PATTERN = re.compile(r'\bid=["\']([^"\']+)["\']', re.I)


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


def ensure_skip_links(site: Path, base_path: str) -> dict[str, int]:
    """Repair the critical-page main/skip-link pair instead of trusting stale markup.

    Some legacy pages already contain a skip link, but its fragment does not point
    to an existing main id. The original v218 helper treated any skip link as valid
    and returned early. This compatibility layer makes the pair atomic:

    1. every critical page must have a `<main id>`;
    2. an existing `.skip-link` must target that id;
    3. a missing skip link is inserted immediately after `<body>`.
    """

    injected = target_repaired = main_ids_added = already_valid = missing_main = 0

    for route in core.CRITICAL_ROUTES:
        path = core.route_file(site, route, base_path)
        if path is None:
            continue
        html = path.read_text(encoding="utf-8", errors="strict")
        main_match = MAIN_PATTERN.search(html)
        if not main_match:
            missing_main += 1
            continue

        main_attrs = main_match.group("attrs")
        id_match = ID_PATTERN.search(main_attrs)
        target_id = id_match.group(1) if id_match else "main-content"
        changed = False

        if not id_match:
            opening = f'<main{main_attrs} id="{target_id}">'
            html = html[: main_match.start()] + opening + html[main_match.end() :]
            main_ids_added += 1
            changed = True

        skip_match = SKIP_LINK_PATTERN.search(html)
        expected_href = f"#{target_id}"
        if skip_match:
            current_tag = skip_match.group(0)
            href_match = re.search(r'\bhref=["\']([^"\']*)["\']', current_tag, re.I)
            current_href = href_match.group(1) if href_match else ""
            if current_href != expected_href:
                html = SKIP_LINK_PATTERN.sub(
                    lambda match: match.group(1) + expected_href + match.group(2),
                    html,
                    count=1,
                )
                target_repaired += 1
                changed = True
            else:
                already_valid += 1
        else:
            body_match = BODY_PATTERN.search(html)
            if not body_match:
                continue
            skip = f'<a class="skip-link" href="{expected_href}">İçeriğe geç</a>'
            html = html[: body_match.end()] + "\n" + skip + html[body_match.end() :]
            injected += 1
            changed = True

        if changed:
            path.write_text(html, encoding="utf-8")

    return {
        "injected": injected,
        "targetRepaired": target_repaired,
        "mainIdsAdded": main_ids_added,
        "alreadyValid": already_valid,
        "missingMain": missing_main,
    }


core.install_quality_css = install_quality_css
core.ensure_skip_links = ensure_skip_links
run = core.run
main = core.main


if __name__ == "__main__":
    main()
