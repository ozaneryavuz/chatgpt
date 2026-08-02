from __future__ import annotations

import argparse
import hashlib
import json
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


def insertion_point(text: str, target) -> int:
    for needle in target.needles:
        found = text.find(needle)
        if found < 0:
            continue
        if needle == "</main>":
            return found
        section_start = text.rfind("<section", 0, found)
        if section_start >= 0 and found - section_start < 12000:
            return section_start
        return max(text.rfind("<", 0, found), 0)
    raise RuntimeError(f"{target.flow}: yerleştirme noktası bulunamadı")


def inject_page(path: Path, target, base: str) -> bool:
    if not path.is_file():
        raise FileNotFoundError(f"Karar hunisi hedefi bulunamadı: {path}")
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    lowered = text.casefold()
    if not all(tag in lowered for tag in ("<html", "<head", "<body")):
        raise RuntimeError(f"HTML belge iskeleti eksik: {path}")
    stylesheet = public_url(base, "/" + ASSET_CSS.as_posix())
    script = public_url(base, "/" + ASSET_JS.as_posix())
    style_tag = f'<link rel="stylesheet" href="{stylesheet}" {STYLE_MARKER}>\n'
    head_close = lowered.find("</head>")
    if head_close >= 0:
        text = text[:head_close] + style_tag + text[head_close:]
    else:
        body_start = lowered.find("<body")
        text = text[:body_start] + style_tag + text[body_start:]
    point = insertion_point(text, target)
    text = text[:point] + funnel_section(target, base) + "\n" + text[point:]
    lowered = text.casefold()
    script_tag = f'<script defer src="{script}" {SCRIPT_MARKER}></script>\n'
    body_close = lowered.find("</body>")
    if body_close >= 0:
        text = text[:body_close] + script_tag + text[body_close:]
    else:
        html_close = lowered.find("</html>")
        if html_close >= 0:
            text = text[:html_close] + script_tag + text[html_close:]
        else:
            text = text.rstrip() + "\n" + script_tag
    path.write_text(text, encoding="utf-8")
    return True


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


def update_release(site: Path, base: str, injected: list[str]) -> None:
    path = site / "pages-release.json"
    if not path.is_file():
        return
    release = json.loads(path.read_text(encoding="utf-8"))
    release["affiliateDecisionFunnel"] = {
        "version": VERSION,
        "basePath": base,
        "flows": [target.flow for target in TARGETS],
        "injectedFlows": injected,
        "tierCount": len(TIERS),
        "placements": list(PLACEMENTS),
        "events": list(EVENTS),
        "eventContract": CONTRACT_NAME,
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
    injected = [
        target.flow
        for target in TARGETS
        if inject_page(site / target.path, target, base)
    ]
    update_release(site, base, injected)
    recompute_checksums(site)
    return {
        "ok": True,
        "version": VERSION,
        "basePath": base,
        "flows": [target.flow for target in TARGETS],
        "injectedFlows": injected,
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
