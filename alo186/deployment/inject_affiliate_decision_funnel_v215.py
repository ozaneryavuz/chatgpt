from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from affiliate_decision_funnel_v215_config import (
    ASSET_CSS,
    ASSET_JS,
    CONTRACT_NAME,
    EVENTS,
    MARKER,
    PLACEMENTS,
    SCRIPT_MARKER,
    SOURCE_CSS,
    SOURCE_JS,
    STYLE_MARKER,
    TARGETS,
    TIER_COPY,
    TIERS,
    VERSION,
    event_contract,
    normalize_base_path,
    public_url,
)
from affiliate_decision_funnel_v215_markup import funnel_section

OPEN_TAG_RE = {
    tag: re.compile(rf"<{tag}\b[^>]*>", re.IGNORECASE)
    for tag in ("html", "head", "body", "main")
}
CLOSE_TAG_RE = {
    tag: re.compile(rf"</{tag}\s*>", re.IGNORECASE)
    for tag in ("html", "head", "body", "main")
}
SECTION_OPEN_RE = re.compile(r"<section\b[^>]*>", re.IGNORECASE)


def _last_match(pattern: re.Pattern[str], text: str) -> re.Match[str] | None:
    matches = list(pattern.finditer(text))
    return matches[-1] if matches else None


def _required_openings(text: str, path: Path) -> None:
    missing = [tag for tag in ("head", "body", "main") if not OPEN_TAG_RE[tag].search(text)]
    if missing:
        raise RuntimeError(
            f"HTML ana yapısı eksik ({', '.join(missing)}): {path}"
        )


def _needle_position(text: str, needle: str) -> int:
    if needle.casefold() == "</main>":
        match = _last_match(CLOSE_TAG_RE["main"], text)
        return match.start() if match else -1
    return text.casefold().find(needle.casefold())


def insertion_point(text: str, target, path: Path) -> int:
    for needle in target.needles:
        found = _needle_position(text, needle)
        if found < 0:
            continue
        if needle.casefold() == "</main>":
            return found
        sections = list(SECTION_OPEN_RE.finditer(text, 0, found))
        if sections and found - sections[-1].start() < 12000:
            return sections[-1].start()
        return max(text.rfind("<", 0, found), 0)

    main_close = _last_match(CLOSE_TAG_RE["main"], text)
    if main_close:
        return main_close.start()
    body_close = _last_match(CLOSE_TAG_RE["body"], text)
    if body_close:
        return body_close.start()
    html_close = _last_match(CLOSE_TAG_RE["html"], text)
    if html_close:
        return html_close.start()
    raise RuntimeError(f"{target.flow}: güvenli yerleştirme noktası bulunamadı: {path}")


def _inject_stylesheet(
    text: str,
    stylesheet: str,
    path: Path,
    repaired: list[str],
) -> str:
    if STYLE_MARKER in text:
        return text
    fragment = f'<link rel="stylesheet" href="{stylesheet}" {STYLE_MARKER}>\n'
    head_close = _last_match(CLOSE_TAG_RE["head"], text)
    if head_close:
        return text[: head_close.start()] + fragment + text[head_close.start() :]

    head_open = OPEN_TAG_RE["head"].search(text)
    body_open = OPEN_TAG_RE["body"].search(text)
    if not head_open or not body_open or body_open.start() <= head_open.end():
        raise RuntimeError(f"HTML head sınırı güvenle onarılamadı: {path}")
    repaired.append("head")
    return text[: body_open.start()] + fragment + "</head>\n" + text[body_open.start() :]


def _ensure_main_close(text: str, path: Path, repaired: list[str]) -> str:
    if CLOSE_TAG_RE["main"].search(text):
        return text
    if not OPEN_TAG_RE["main"].search(text):
        raise RuntimeError(f"HTML <main> açılışı bulunamadı: {path}")

    body_close = _last_match(CLOSE_TAG_RE["body"], text)
    if body_close:
        repaired.append("main")
        return text[: body_close.start()] + "</main>\n" + text[body_close.start() :]

    html_close = _last_match(CLOSE_TAG_RE["html"], text)
    if html_close and OPEN_TAG_RE["body"].search(text):
        repaired.extend(["main", "body"])
        return (
            text[: html_close.start()]
            + "</main>\n</body>\n"
            + text[html_close.start() :]
        )
    raise RuntimeError(f"HTML main/body sınırı güvenle onarılamadı: {path}")


def _inject_script(
    text: str,
    script: str,
    path: Path,
    repaired: list[str],
) -> str:
    if SCRIPT_MARKER in text:
        return text
    fragment = f'<script defer src="{script}" {SCRIPT_MARKER}></script>\n'
    body_close = _last_match(CLOSE_TAG_RE["body"], text)
    if body_close:
        return text[: body_close.start()] + fragment + text[body_close.start() :]

    html_close = _last_match(CLOSE_TAG_RE["html"], text)
    if html_close and OPEN_TAG_RE["body"].search(text):
        repaired.append("body")
        return text[: html_close.start()] + fragment + "</body>\n" + text[html_close.start() :]
    raise RuntimeError(f"HTML body sınırı güvenle onarılamadı: {path}")


def _ensure_html_close(text: str, path: Path, repaired: list[str]) -> str:
    if CLOSE_TAG_RE["html"].search(text):
        return text
    if not OPEN_TAG_RE["html"].search(text):
        return text
    if not CLOSE_TAG_RE["body"].search(text):
        raise RuntimeError(f"HTML sonu güvenle onarılamadı: {path}")
    repaired.append("html")
    return text.rstrip() + "\n</html>\n"


def _validate_document(text: str, path: Path) -> None:
    _required_openings(text, path)
    missing = [
        tag for tag in ("head", "main", "body")
        if not CLOSE_TAG_RE[tag].search(text)
    ]
    if missing:
        raise RuntimeError(
            f"HTML kapanışları eksik ({', '.join(missing)}): {path}"
        )

    head_open = OPEN_TAG_RE["head"].search(text)
    head_close = CLOSE_TAG_RE["head"].search(text)
    body_open = OPEN_TAG_RE["body"].search(text)
    main_open = OPEN_TAG_RE["main"].search(text)
    main_close = _last_match(CLOSE_TAG_RE["main"], text)
    body_close = _last_match(CLOSE_TAG_RE["body"], text)
    assert head_open and head_close and body_open and main_open and main_close and body_close
    if not (
        head_open.start()
        < head_close.start()
        < body_open.start()
        < main_open.start()
        < main_close.start()
        < body_close.start()
    ):
        raise RuntimeError(f"HTML ana etiket sırası geçersiz: {path}")
    if text.count(MARKER) != 1:
        raise RuntimeError(f"Karar hunisi işaretçisi tekil değil: {path}")
    if text.count(STYLE_MARKER) != 1 or text.count(SCRIPT_MARKER) != 1:
        raise RuntimeError(f"Karar hunisi asset işaretçileri tekil değil: {path}")


def inject_page(path: Path, target, base: str) -> dict[str, object]:
    if not path.is_file():
        raise FileNotFoundError(f"Karar hunisi hedefi bulunamadı: {path}")
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        _validate_document(text, path)
        return {"injected": False, "repairedClosures": []}

    _required_openings(text, path)
    repaired: list[str] = []
    stylesheet = public_url(base, "/" + ASSET_CSS.as_posix())
    script = public_url(base, "/" + ASSET_JS.as_posix())

    text = _inject_stylesheet(text, stylesheet, path, repaired)
    point = insertion_point(text, target, path)
    text = text[:point] + funnel_section(target, base) + "\n" + text[point:]
    text = _ensure_main_close(text, path, repaired)
    text = _inject_script(text, script, path, repaired)
    text = _ensure_html_close(text, path, repaired)
    _validate_document(text, path)

    path.write_text(text, encoding="utf-8")
    return {
        "injected": True,
        "repairedClosures": list(dict.fromkeys(repaired)),
    }


def recompute_checksums(site: Path) -> None:
    path = site / "checksums.sha256"
    if not path.exists():
        return
    path.unlink()
    files = sorted(item for item in site.rglob("*") if item.is_file())
    path.write_text(
        "\n".join(
            f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}"
            for item in files
        )
        + "\n",
        encoding="utf-8",
    )


def write_assets(site: Path) -> None:
    if not SOURCE_JS.is_file() or not SOURCE_CSS.is_file():
        raise FileNotFoundError("v215 karar hunisi kaynak assetları eksik")
    (site / ASSET_JS).parent.mkdir(parents=True, exist_ok=True)
    (site / ASSET_JS).write_text(SOURCE_JS.read_text(encoding="utf-8"), encoding="utf-8")
    (site / ASSET_CSS).write_text(SOURCE_CSS.read_text(encoding="utf-8"), encoding="utf-8")
    (site / CONTRACT_NAME).write_text(
        json.dumps(event_contract(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def update_release(
    site: Path,
    base: str,
    injected: list[str],
    normalized_closures: dict[str, list[str]],
) -> None:
    path = site / "pages-release.json"
    if not path.is_file():
        return
    release = json.loads(path.read_text(encoding="utf-8"))
    previous = release.get("affiliateDecisionFunnel")
    retained_normalizations: dict[str, list[str]] = {}
    if isinstance(previous, dict) and isinstance(previous.get("normalizedClosures"), dict):
        retained_normalizations = {
            str(flow): [str(tag) for tag in tags]
            for flow, tags in previous["normalizedClosures"].items()
            if isinstance(tags, list)
        }
    retained_normalizations.update(normalized_closures)
    release["affiliateDecisionFunnel"] = {
        "version": VERSION,
        "basePath": base,
        "flows": [target.flow for target in TARGETS],
        "injectedFlows": injected,
        "tierCount": len(TIERS),
        "placements": list(PLACEMENTS),
        "events": list(EVENTS),
        "eventContract": CONTRACT_NAME,
        "normalizedClosures": retained_normalizations,
        "documentRepairPolicy": "only-missing-closing-tags-with-valid-open-structure",
        "rawDestinationUrlStored": False,
        "numericElectricalInputsStored": False,
        "userOrDeviceIdentifierStored": False,
        "directAmazonLinksAdded": 0,
        "noBuyOutcome": True,
        "commerceBlockOutcome": True,
    }
    path.write_text(
        json.dumps(release, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def inject(site: Path, base: str = "") -> dict:
    site = site.resolve()
    base = normalize_base_path(base)
    write_assets(site)

    page_results: dict[str, dict[str, object]] = {}
    for target in TARGETS:
        page_results[target.flow] = inject_page(site / target.path, target, base)

    injected = [
        flow for flow, result in page_results.items()
        if result["injected"] is True
    ]
    normalized_closures = {
        flow: list(result["repairedClosures"])
        for flow, result in page_results.items()
        if result["repairedClosures"]
    }
    update_release(site, base, injected, normalized_closures)
    recompute_checksums(site)
    return {
        "ok": True,
        "version": VERSION,
        "basePath": base,
        "flows": [target.flow for target in TARGETS],
        "injectedFlows": injected,
        "normalizedClosures": normalized_closures,
        "tierCount": len(TIERS),
        "events": list(EVENTS),
        "directAmazonLinksAdded": 0,
        "rawDestinationUrlStored": False,
        "numericElectricalInputsStored": False,
        "userOrDeviceIdentifierStored": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(inject(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
