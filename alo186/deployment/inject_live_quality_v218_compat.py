from __future__ import annotations

import json
import re
from pathlib import Path

import finalize_pages_service_worker as sw_finalizer
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
WWW_HTTPS_ORIGIN = "https://www.alo186.com"
WWW_HTTP_ORIGIN = "http://www.alo186.com"
APEX_ORIGIN = "https://alo186.com"


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


def install_quality_css(site: Path) -> dict[str, object]:
    """Inject v218 CSS with legacy-head repair and project-path awareness."""
    target = site / core.ASSET_RELATIVE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(core.QUALITY_CSS, encoding="utf-8")
    base_path = artifact_base_path(site)
    asset_href = (
        f"{base_path}/{core.ASSET_RELATIVE.as_posix()}"
        if base_path
        else f"/{core.ASSET_RELATIVE.as_posix()}"
    )
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

        updated, count = re.subn(
            r"</head\s*>",
            link + "\n</head>",
            html,
            count=1,
            flags=re.I,
        )
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
            updated = (
                html[: html_tag.end()]
                + "\n<head>"
                + link
                + "</head>\n"
                + html[html_tag.end() :]
            )
            path.write_text(updated, encoding="utf-8")
            injected += 1
            created_head += 1
            continue

        failures.append(path.relative_to(site).as_posix())

    if failures:
        raise RuntimeError(
            "Live quality CSS için onarılamayan HTML: " + ", ".join(failures[:30])
        )
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


def normalize_canonical_origin(site: Path) -> dict[str, object]:
    """Collapse all late-generated first-party URLs onto the apex HTTPS origin."""
    targets = sorted(site.rglob("*.html"))
    for relative in (Path("sitemap.xml"), Path("robots.txt")):
        candidate = site / relative
        if candidate.is_file():
            targets.append(candidate)

    files_changed = 0
    replacements = 0
    changed_files: list[str] = []
    for path in targets:
        text = path.read_text(encoding="utf-8", errors="strict")
        count = text.count(WWW_HTTPS_ORIGIN) + text.count(WWW_HTTP_ORIGIN)
        if count == 0:
            continue
        updated = text.replace(WWW_HTTPS_ORIGIN, APEX_ORIGIN).replace(
            WWW_HTTP_ORIGIN, APEX_ORIGIN
        )
        path.write_text(updated, encoding="utf-8")
        files_changed += 1
        replacements += count
        changed_files.append(path.relative_to(site).as_posix())

    return {
        "apexOrigin": APEX_ORIGIN,
        "filesScanned": len(targets),
        "filesChanged": files_changed,
        "replacementCount": replacements,
        "changedFiles": changed_files[:100],
    }


core.install_quality_css = install_quality_css
core.ensure_skip_links = ensure_skip_links
_CORE_RUN = core.run


def run(site: Path, base_path: str = "") -> dict[str, object]:
    resolved = site.resolve()
    normalization = normalize_canonical_origin(resolved)
    report = _CORE_RUN(resolved, base_path)
    report["canonicalOriginNormalization"] = normalization

    service_worker = sw_finalizer.finalize_and_record(resolved, base_path)
    report["serviceWorkerRegistrationFinalization"] = service_worker

    receipt = resolved / core.RECEIPT_RELATIVE
    receipt.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for name in ("alo186-release.json", "pages-release.json"):
        path = resolved / name
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["liveQualityV218"] = report
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    core.recompute_checksums(resolved)
    return report


def main() -> None:
    parser = core.argparse.ArgumentParser(
        description=(
            "ALO186 final artifact UX, canonical-origin, servis-worker ve kopya kalite kapısı "
            "v218 uyumluluk katmanı"
        )
    )
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
