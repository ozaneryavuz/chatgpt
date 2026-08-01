from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

TARGET_RENDER_WIDTH = 162
TARGET_RENDER_HEIGHT = 28
MAX_INTRINSIC_WIDTH = TARGET_RENDER_WIDTH * 2
MAX_INTRINSIC_HEIGHT = TARGET_RENDER_HEIGHT * 2
MAX_REASONABLE_CANDIDATE_WIDTH = 640
EXPECTED_SIZES = "(max-width: 480px) 150px, 162px"
LOGO_MARKERS = ("/brand/alo186-logo", "brand-logo")
MODERN_IMAGE_TYPES = {"image/avif", "image/webp"}


@dataclass(frozen=True)
class LogoElement:
    attributes: dict[str, str]
    picture_sources: tuple[dict[str, str], ...]


class BrandLogoParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.logo: LogoElement | None = None
        self._picture_depth = 0
        self._picture_sources: list[dict[str, str]] = []

    @staticmethod
    def _attrs(raw: list[tuple[str, str | None]]) -> dict[str, str]:
        return {name.casefold(): value or "" for name, value in raw}

    @staticmethod
    def _is_brand_logo(attributes: dict[str, str]) -> bool:
        haystack = " ".join(
            attributes.get(key, "")
            for key in ("src", "srcset", "class", "alt")
        ).casefold()
        return any(marker in haystack for marker in LOGO_MARKERS)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.casefold()
        attributes = self._attrs(attrs)
        if lowered == "picture":
            self._picture_depth += 1
            if self._picture_depth == 1:
                self._picture_sources = []
            return
        if lowered == "source" and self._picture_depth:
            self._picture_sources.append(attributes)
            return
        if lowered == "img" and self.logo is None and self._is_brand_logo(attributes):
            self.logo = LogoElement(attributes, tuple(self._picture_sources))

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() != "picture" or not self._picture_depth:
            return
        self._picture_depth -= 1
        if self._picture_depth == 0:
            self._picture_sources = []


def _positive_int(value: str) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _normalize_sizes(sizes: str) -> str:
    return re.sub(r"\s+", " ", sizes.strip())


def _slot_widths_px(sizes: str) -> list[int]:
    # Yalnız doğrulanmış sizes sözleşmesi kabul edilir; vw/vh gibi dallar sessizce atlanmaz.
    if _normalize_sizes(sizes) != EXPECTED_SIZES:
        return []
    without_conditions = re.sub(r"\([^)]*\)", "", sizes)
    return [int(value) for value in re.findall(r"(?<![\w.-])(\d+)px\b", without_conditions, re.I)]


def _candidate_widths(attributes: dict[str, str]) -> list[int]:
    values = " ".join((attributes.get("src", ""), attributes.get("srcset", "")))
    widths = {int(value) for value in re.findall(r"[?&]w=(\d+)\b", values, re.I)}
    widths.update(int(value) for value in re.findall(r"(?:^|[,\s])(\d+)w(?:\s|,|$)", values, re.I))
    return sorted(widths)


def _uses_modern_format(logo: LogoElement) -> bool:
    for source in logo.picture_sources:
        if source.get("type", "").casefold() in MODERN_IMAGE_TYPES:
            return True
    values = " ".join(
        [logo.attributes.get("src", ""), logo.attributes.get("srcset", "")]
        + [source.get("srcset", "") for source in logo.picture_sources]
    ).casefold()
    return bool(re.search(r"\.(?:avif|webp)(?:[?#\s,]|$)", values))


def _uses_image_optimizer(logo: LogoElement) -> bool:
    values = " ".join((logo.attributes.get("src", ""), logo.attributes.get("srcset", ""))).casefold()
    return "/_vinext/image?" in values or "/_next/image?" in values


def audit_html(html: str) -> dict:
    parser = BrandLogoParser()
    parser.feed(html)
    parser.close()

    expected = {
        "renderedWidth": TARGET_RENDER_WIDTH,
        "renderedHeight": TARGET_RENDER_HEIGHT,
        "maximumIntrinsicWidth": MAX_INTRINSIC_WIDTH,
        "maximumIntrinsicHeight": MAX_INTRINSIC_HEIGHT,
        "sizes": EXPECTED_SIZES,
        "loading": "eager",
        "fetchPriority": "high",
        "decoding": "async",
    }
    if parser.logo is None:
        return {
            "ok": False,
            "hardIssues": ["brand_logo_not_found"],
            "recommendations": [],
            "expected": expected,
            "logo": None,
        }

    logo = parser.logo
    attrs = logo.attributes
    width = _positive_int(attrs.get("width", ""))
    height = _positive_int(attrs.get("height", ""))
    sizes = attrs.get("sizes", "").strip()
    slot_widths = _slot_widths_px(sizes)
    candidate_widths = _candidate_widths(attrs)
    bounded_sizes = _normalize_sizes(sizes) == EXPECTED_SIZES
    aspect_ratio_ok = (
        width is not None
        and height is not None
        and width * TARGET_RENDER_HEIGHT == height * TARGET_RENDER_WIDTH
    )
    modern_format = _uses_modern_format(logo)
    optimizer = _uses_image_optimizer(logo)

    issues: list[str] = []
    recommendations: list[str] = []

    if attrs.get("fetchpriority", "").casefold() != "high":
        issues.append("fetchpriority_must_be_high")
    if attrs.get("loading", "").casefold() != "eager":
        issues.append("above_the_fold_logo_must_load_eagerly")
    if attrs.get("decoding", "").casefold() != "async":
        issues.append("decoding_should_be_async")
    if width is None:
        issues.append("intrinsic_width_missing")
    elif width > MAX_INTRINSIC_WIDTH:
        issues.append("intrinsic_width_exceeds_2x_rendered_width")
    if height is None:
        issues.append("intrinsic_height_missing")
    elif height > MAX_INTRINSIC_HEIGHT:
        issues.append("intrinsic_height_exceeds_2x_rendered_height")
    if width is not None and height is not None and not aspect_ratio_ok:
        issues.append("intrinsic_aspect_ratio_must_match_162x28")
    if not bounded_sizes:
        issues.append("sizes_must_bound_logo_slot_to_150_162px")
    if candidate_widths and max(candidate_widths) > MAX_REASONABLE_CANDIDATE_WIDTH and not bounded_sizes:
        issues.append("unbounded_srcset_can_download_oversized_candidate")

    if optimizer and not modern_format:
        recommendations.append("verify_vinext_response_content_type_is_avif_or_webp")
    elif not modern_format:
        recommendations.append("publish_explicit_avif_or_webp_logo_sources")

    return {
        "ok": not issues,
        "hardIssues": issues,
        "recommendations": recommendations,
        "expected": expected,
        "logo": {
            "src": attrs.get("src", ""),
            "srcset": attrs.get("srcset", ""),
            "sizes": sizes,
            "slotWidthsPx": slot_widths,
            "width": width,
            "height": height,
            "aspectRatioValid": aspect_ratio_ok,
            "loading": attrs.get("loading", ""),
            "fetchPriority": attrs.get("fetchpriority", ""),
            "decoding": attrs.get("decoding", ""),
            "candidateWidths": candidate_widths,
            "usesImageOptimizer": optimizer,
            "usesExplicitModernFormat": modern_format,
            "pictureSources": [dict(source) for source in logo.picture_sources],
        },
    }


def fetch_html(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "ALO186-brand-logo-contract/1.0",
            "Accept": "text/html,application/xhtml+xml",
            "Cache-Control": "no-cache",
        },
    )
    with urlopen(request, timeout=30) as response:
        media_type = response.headers.get_content_type()
        if media_type != "text/html":
            raise RuntimeError(f"Beklenen text/html, alınan: {media_type}")
        return response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 marka logosunun canlı performans sözleşmesini denetler.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--url", default="https://alo186.com/")
    source.add_argument("--html-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    html = args.html_file.read_text(encoding="utf-8") if args.html_file else fetch_html(args.url)
    report = audit_html(html)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    sys.stdout.write(payload)
    if args.strict and not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
