#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


class PageParser(HTMLParser):
    SKIP = {"script", "style", "svg", "template", "noscript"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.text_parts: list[str] = []
        self.hrefs: list[str] = []
        self.canonical = ""
        self.title_parts: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        values = {key.casefold(): value or "" for key, value in attrs}
        if tag in self.SKIP:
            self.skip_depth += 1
            return
        if tag == "title":
            self.in_title = True
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"])
        if tag == "link" and "canonical" in values.get("rel", "").casefold().split():
            self.canonical = values.get("href", "")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag in self.SKIP and self.skip_depth:
            self.skip_depth -= 1
            return
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        value = re.sub(r"\s+", " ", data).strip()
        if not value:
            return
        self.text_parts.append(value)
        if self.in_title:
            self.title_parts.append(value)

    @property
    def visible_text(self) -> str:
        return " ".join(self.text_parts)

    @property
    def title(self) -> str:
        return " ".join(self.title_parts)


@dataclass(frozen=True)
class FetchResult:
    url: str
    status: int
    html: str
    source: str
    error: str = ""


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object bekleniyordu: {path}")
    return value


def fixture_path(root: Path, url: str) -> Path:
    parsed = urlparse(url)
    relative = parsed.path.strip("/")
    if not relative:
        return root / "index.html"
    direct = root / relative
    if direct.suffix:
        return direct
    return direct / "index.html"


def fetch_page(url: str, *, user_agent: str, timeout: int, fixture_root: Path | None) -> FetchResult:
    if fixture_root is not None:
        path = fixture_path(fixture_root, url)
        if not path.is_file():
            return FetchResult(url=url, status=404, html="", source=str(path), error="fixture missing")
        return FetchResult(url=url, status=200, html=path.read_text(encoding="utf-8"), source=str(path))

    request = urllib.request.Request(
        url,
        headers={"User-Agent": user_agent, "Accept": "text/html,application/xhtml+xml"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
            return FetchResult(
                url=response.geturl(),
                status=int(getattr(response, "status", 200)),
                html=raw.decode(charset, errors="replace"),
                source="live-http",
            )
    except urllib.error.HTTPError as exc:
        return FetchResult(url=url, status=exc.code, html="", source="live-http", error=str(exc))
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return FetchResult(url=url, status=0, html="", source="live-http", error=str(exc))


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def evaluate(page: dict[str, Any], fetched: FetchResult) -> dict[str, Any]:
    parser = PageParser()
    if fetched.html:
        parser.feed(fetched.html)
    visible = normalize(parser.visible_text)
    required = [str(item) for item in page.get("requiredText", [])]
    forbidden = [str(item) for item in page.get("forbiddenText", [])]
    missing = [item for item in required if normalize(item) not in visible]
    present_forbidden = [item for item in forbidden if normalize(item) in visible]
    direct_amazon = [
        href for href in parser.hrefs
        if any(host in href.casefold() for host in ("amazon.com.tr", "amzn.to"))
    ]
    canonical_expected = str(page["url"]).rstrip("/") + "/"
    canonical_actual = parser.canonical.strip()
    canonical_ok = not canonical_actual or canonical_actual.rstrip("/") + "/" == canonical_expected
    issues: list[str] = []
    if fetched.status != 200:
        issues.append(f"HTTP {fetched.status or 'error'}")
    if missing:
        issues.append("required text missing")
    if present_forbidden:
        issues.append("forbidden text present")
    if page.get("forbidDirectAmazonHref") and direct_amazon:
        issues.append("direct Amazon href present")
    if not canonical_ok:
        issues.append("canonical mismatch")
    return {
        "id": page["id"],
        "url": page["url"],
        "priority": page.get("priority", "P2"),
        "sourceFile": page["source"],
        "httpStatus": fetched.status,
        "finalUrl": fetched.url,
        "fetchSource": fetched.source,
        "fetchError": fetched.error,
        "title": parser.title,
        "canonical": canonical_actual,
        "canonicalOk": canonical_ok,
        "missingRequiredText": missing,
        "presentForbiddenText": present_forbidden,
        "directAmazonHrefs": direct_amazon,
        "contentSha256": hashlib.sha256(fetched.html.encode("utf-8")).hexdigest() if fetched.html else "",
        "drift": bool(issues),
        "issues": issues,
    }


def build_patch(results: list[dict[str, Any]], *, version: int, generated_at: str) -> dict[str, Any]:
    actions = []
    for result in results:
        if not result["drift"]:
            continue
        actions.append(
            {
                "priority": result["priority"],
                "targetUrl": result["url"],
                "sourceFile": result["sourceFile"],
                "mode": "merge-into-existing-chatgpt-sites-page",
                "preserveNativeSitesDesign": True,
                "replaceBlindly": False,
                "acceptance": {
                    "http200": True,
                    "canonical": result["url"],
                    "removeForbiddenText": result["presentForbiddenText"],
                    "addRequiredText": result["missingRequiredText"],
                    "removeDirectAmazonHrefsBeforeTechnicalGate": bool(result["directAmazonHrefs"]),
                },
                "reasons": result["issues"],
            }
        )
    actions.sort(key=lambda item: (item["priority"], item["targetUrl"]))
    return {
        "schemaVersion": 1,
        "growthVersion": version,
        "target": "ChatGPT Sites",
        "siteSlug": "alo186",
        "canonicalHost": "https://alo186.com",
        "generatedAt": generated_at,
        "status": "patch-required" if actions else "no-drift",
        "automaticPublishAllowed": False,
        "connectedSitesWriteRequired": True,
        "actions": actions,
    }


def run(config_path: Path, output: Path, fixture_root: Path | None = None) -> dict[str, Any]:
    config = load_json(config_path)
    pages = config.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("En az bir kritik sayfa gerekir")
    output.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    results = [
        evaluate(
            page,
            fetch_page(
                str(page["url"]),
                user_agent=str(config.get("userAgent") or "ALO186-Live-Drift"),
                timeout=int(config.get("timeoutSeconds") or 20),
                fixture_root=fixture_root,
            ),
        )
        for page in pages
    ]
    patch = build_patch(results, version=int(config.get("version") or 0), generated_at=generated_at)
    report = {
        "schemaVersion": 1,
        "growthVersion": int(config.get("version") or 0),
        "generatedAt": generated_at,
        "canonicalHost": config.get("canonicalHost"),
        "checked": len(results),
        "driftCount": sum(1 for item in results if item["drift"]),
        "healthyCount": sum(1 for item in results if not item["drift"]),
        "results": results,
        "topActions": patch["actions"][:3],
    }
    (output / "live-drift-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "sites-delta-patch-v259.json").write_text(json.dumps(patch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = [
        "# ALO186 ChatGPT Sites canlı drift raporu",
        "",
        f"- Kontrol edilen kritik sayfa: **{report['checked']}**",
        f"- Drift bulunan: **{report['driftCount']}**",
        f"- Sağlıklı: **{report['healthyCount']}**",
        "",
    ]
    for index, action in enumerate(report["topActions"], start=1):
        summary.extend([
            f"## {index}. {action['targetUrl']}",
            f"- Kaynak: `{action['sourceFile']}`",
            f"- Neden: {', '.join(action['reasons'])}",
            "",
        ])
    (output / "SUMMARY.md").write_text("\n".join(summary), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 ChatGPT Sites kritik canlı içerik drift denetimi")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixture-root", type=Path)
    args = parser.parse_args()
    report = run(args.config, args.output, args.fixture_root)
    print(json.dumps({"ok": True, "checked": report["checked"], "driftCount": report["driftCount"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
