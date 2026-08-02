from __future__ import annotations

import json
import re
from pathlib import Path
from xml.etree import ElementTree

import inject_live_quality_v218 as core


SKIP_LINK_PATTERN = re.compile(
    r'(<a\b(?=[^>]*\bclass=["\'][^"\']*\bskip-link\b[^"\']*["\'])[^>]*\bhref=["\'])[^"\']*(["\'][^>]*>)',
    re.I,
)
MAIN_PATTERN = re.compile(r'<main\b(?P<attrs>[^>]*)>', re.I)
BODY_PATTERN = re.compile(r'<body\b[^>]*>', re.I)
ID_PATTERN = re.compile(r'\bid=["\']([^"\']+)["\']', re.I)
QUALITY_LINK_PATTERN = re.compile(
    r'(<link\b(?=[^>]*data-alo186-live-quality-v218=["\']true["\'])[^>]*\bhref=["\'])[^"\']*(["\'][^>]*>)',
    re.I,
)
LEGACY_ORIGIN = "https://www.alo186.com"
CANONICAL_ORIGIN = "https://alo186.com"


def artifact_base_path(site: Path) -> str:
    release_path = site / "pages-release.json"
    if not release_path.is_file():
        return ""
    try:
        payload = json.loads(release_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    value = payload.get("basePath")
    return core.normalize_base_path(value) if isinstance(value, str) else ""


def normalize_late_canonical_origin(site: Path) -> dict[str, object]:
    """Normalize routes created after Pages preparation to the apex origin."""
    changed_pages: list[str] = []
    for relative in (
        Path("hesaplama/elektrik-planim/index.html"),
        Path("hesaplama/elektrik-kesintisi-kiti/index.html"),
    ):
        path = site / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="strict")
        updated = text.replace(LEGACY_ORIGIN, CANONICAL_ORIGIN)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed_pages.append(relative.as_posix())

    sitemap = site / "sitemap.xml"
    changed_locations = 0
    if sitemap.is_file():
        try:
            tree = ElementTree.parse(sitemap)
        except ElementTree.ParseError as exc:
            raise AssertionError(f"sitemap.xml parse edilemiyor: {exc}") from exc
        for node in tree.getroot().findall(".//{*}loc"):
            value = (node.text or "").strip()
            if value.startswith(LEGACY_ORIGIN + "/"):
                node.text = CANONICAL_ORIGIN + value[len(LEGACY_ORIGIN):]
                changed_locations += 1
        if changed_locations:
            ElementTree.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
            ElementTree.register_namespace("xhtml", "http://www.w3.org/1999/xhtml")
            tree.write(sitemap, encoding="utf-8", xml_declaration=True)

    return {
        "changedPages": changed_pages,
        "changedPageCount": len(changed_pages),
        "changedSitemapLocations": changed_locations,
        "canonicalOrigin": CANONICAL_ORIGIN,
    }


def install_quality_css(site: Path) -> dict[str, object]:
    """Inject v218 CSS with legacy-head repair and project-path awareness."""
    target = site / core.ASSET_RELATIVE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(core.QUALITY_CSS, encoding="utf-8")
    base_path = artifact_base_path(site)
    asset_href = f"{base_path}/{core.ASSET_RELATIVE.as_posix()}" if base_path else f"/{core.ASSET_RELATIVE.as_posix()}"
    link = f'<link rel="stylesheet" href="{asset_href}" {core.STYLE_MARKER}>'
    injected = existing = repaired_head = created_head = base_path_adjusted = 0
    failures: list[str] = []

    for path in sorted(site.rglob("*.html")):
        html = path.read_text(encoding="utf-8", errors="strict")
        if core.STYLE_MARKER in html:
            updated, count = QUALITY_LINK_PATTERN.subn(
                lambda match: match.group(1) + asset_href + match.group(2),
                html,
                count=1,
            )
            if count == 1 and updated != html:
                path.write_text(updated, encoding="utf-8")
                base_path_adjusted += 1
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
        "asset": asset_href,
        "basePath": base_path,
        "injectedPages": injected,
        "alreadyPresent": existing,
        "basePathAdjustedPages": base_path_adjusted,
        "repairedHeadBoundaries": repaired_head,
        "createdHeadElements": created_head,
    }


def ensure_skip_links(site: Path, base_path: str) -> dict[str, int]:
    """Repair the critical-page main/skip-link pair instead of trusting stale markup."""
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
_original_run = core.run


def run(site: Path, base_path: str = "") -> dict[str, object]:
    normalization = normalize_late_canonical_origin(site.resolve())
    report = _original_run(site, base_path)
    report["lateCanonicalNormalization"] = normalization
    return report


main = core.main


if __name__ == "__main__":
    main()
