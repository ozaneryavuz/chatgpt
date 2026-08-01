from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

DEFAULT_ORIGIN = "https://alo186.com"


@dataclass(frozen=True)
class RouteSpec:
    path: str
    title: str
    schema_types: frozenset[str]
    markers: tuple[str, ...]

    @property
    def canonical(self) -> str:
        return f"{DEFAULT_ORIGIN}{self.path}"


ROUTES: tuple[RouteSpec, ...] = (
    RouteSpec(
        path="/hesaplama/asansorde-elektrik-kesintisi-mahsur-kalma-guvenligi/",
        title="Asansörde Elektrik Kesintisi ve Mahsur Kalma Güvenliği",
        schema_types=frozenset({"WebApplication", "FAQPage", "BreadcrumbList"}),
        markers=("kapıyı zorlamayın", "iki yönlü haberleşme", "112"),
    ),
    RouteSpec(
        path="/hesaplama/asansor-otomatik-kurtarma-alarm-aku-jenerator-uygunluk-kontrolu/",
        title="Asansör Otomatik Kurtarma, Alarm, Akü ve Jeneratör Uygunluğu",
        schema_types=frozenset({"WebApplication", "FAQPage", "BreadcrumbList"}),
        markers=("otomatik kurtarma", "gerçek kesinti", "affiliate bağlantısı yoktur"),
    ),
    RouteSpec(
        path="/sektor-rehberi/apartman-otel-asansor-elektrik-kesintisi-test-merkezi/",
        title="Apartman ve Otel Asansör Elektrik Kesintisi Test Merkezi",
        schema_types=frozenset({"Article", "FAQPage", "BreadcrumbList"}),
        markers=("7 günlük", "30 günlük", "90 günlük", "affiliate bağlantısı yoktur"),
    ),
)

AFFILIATE_HOSTS = {"amazon.com.tr", "amzn.to"}
HTML_MEDIA_TYPES = {"text/html", "application/xhtml+xml"}
SITEMAP_MEDIA_TYPES = {"application/xml", "text/xml", "application/xhtml+xml", "text/plain"}


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.canonical = ""
        self.robots = ""
        self.jsonld: list[str] = []
        self.links: list[str] = []
        self._in_title = False
        self._in_jsonld = False
        self._script_parts: list[str] = []

    @staticmethod
    def _attrs(raw: list[tuple[str, str | None]]) -> dict[str, str]:
        return {name.casefold(): value or "" for name, value in raw}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.casefold()
        attributes = self._attrs(attrs)
        if lowered == "title":
            self._in_title = True
        elif lowered == "link":
            rel = set(attributes.get("rel", "").casefold().split())
            if "canonical" in rel:
                self.canonical = attributes.get("href", "").strip()
        elif lowered == "meta" and attributes.get("name", "").casefold() == "robots":
            self.robots = attributes.get("content", "").strip()
        elif lowered == "script" and attributes.get("type", "").casefold() == "application/ld+json":
            self._in_jsonld = True
            self._script_parts = []
        elif lowered == "a":
            href = attributes.get("href", "").strip()
            if href:
                self.links.append(href)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_jsonld:
            self._script_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.casefold()
        if lowered == "title":
            self._in_title = False
        elif lowered == "script" and self._in_jsonld:
            self.jsonld.append("".join(self._script_parts).strip())
            self._in_jsonld = False
            self._script_parts = []

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())


def normalize_origin(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError(f"Canlı origin HTTPS olmalıdır: {value!r}")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError(f"Canlı origin yol veya sorgu içermemelidir: {value!r}")
    return f"https://{parsed.hostname}"


def collect_schema_types(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        raw_type = value.get("@type")
        if isinstance(raw_type, str):
            found.add(raw_type)
        elif isinstance(raw_type, list):
            found.update(item for item in raw_type if isinstance(item, str))
        for child in value.values():
            found.update(collect_schema_types(child))
    elif isinstance(value, list):
        for child in value:
            found.update(collect_schema_types(child))
    return found


def parse_schema_types(payloads: list[str]) -> tuple[set[str], list[str]]:
    found: set[str] = set()
    errors: list[str] = []
    for index, raw in enumerate(payloads):
        try:
            found.update(collect_schema_types(json.loads(raw)))
        except json.JSONDecodeError as exc:
            errors.append(f"jsonld_{index}_invalid:{exc.msg}")
    return found, errors


def affiliate_links(urls: list[str]) -> list[str]:
    matches: list[str] = []
    for url in urls:
        host = (urlparse(url).hostname or "").casefold().removeprefix("www.")
        if host in AFFILIATE_HOSTS:
            matches.append(url)
    return matches


def audit_html(
    html: str,
    spec: RouteSpec,
    *,
    origin: str = DEFAULT_ORIGIN,
    effective_url: str | None = None,
) -> dict[str, Any]:
    parser = HeadParser()
    parser.feed(html)
    parser.close()

    expected_canonical = f"{normalize_origin(origin)}{spec.path}"
    folded = html.casefold()
    schema_types, schema_errors = parse_schema_types(parser.jsonld)
    issues: list[str] = list(schema_errors)

    if len(html.encode("utf-8")) < 1000:
        issues.append("html_body_too_small")
    if spec.title.casefold() not in parser.title.casefold():
        issues.append("expected_title_missing")
    if parser.canonical != expected_canonical:
        issues.append("canonical_mismatch")

    robots_tokens = {token.strip() for token in parser.robots.casefold().split(",") if token.strip()}
    if "noindex" in robots_tokens or "none" in robots_tokens:
        issues.append("route_must_be_indexable")
    if "index" not in robots_tokens:
        issues.append("robots_index_missing")

    missing_types = sorted(spec.schema_types - schema_types)
    if missing_types:
        issues.append("schema_types_missing:" + ",".join(missing_types))

    missing_markers = [marker for marker in spec.markers if marker.casefold() not in folded]
    if missing_markers:
        issues.append("content_markers_missing:" + "|".join(missing_markers))

    commercial_links = affiliate_links(parser.links)
    if commercial_links:
        issues.append("affiliate_links_forbidden")

    if effective_url:
        parsed = urlparse(effective_url)
        expected_host = urlparse(origin).hostname
        if parsed.scheme != "https" or parsed.hostname != expected_host:
            issues.append("effective_origin_mismatch")
        if parsed.path.rstrip("/") != spec.path.rstrip("/"):
            issues.append("effective_path_mismatch")

    return {
        "ok": not issues,
        "path": spec.path,
        "canonical": parser.canonical,
        "expectedCanonical": expected_canonical,
        "title": parser.title,
        "robots": parser.robots,
        "schemaTypes": sorted(schema_types),
        "requiredSchemaTypes": sorted(spec.schema_types),
        "affiliateLinks": commercial_links,
        "bytes": len(html.encode("utf-8")),
        "sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
        "issues": issues,
    }


def audit_sitemap(xml: str, *, origin: str = DEFAULT_ORIGIN) -> dict[str, Any]:
    normalized_origin = normalize_origin(origin)
    expected = [f"{normalized_origin}{spec.path}" for spec in ROUTES]
    missing = [url for url in expected if url not in xml]
    duplicate = [url for url in expected if xml.count(url) != 1]
    issues: list[str] = []
    if missing:
        issues.append("sitemap_routes_missing")
    if duplicate:
        issues.append("sitemap_route_count_must_equal_one")
    if "<urlset" not in xml.casefold() and "<sitemapindex" not in xml.casefold():
        issues.append("sitemap_root_missing")
    return {
        "ok": not issues,
        "expectedUrls": expected,
        "missingUrls": missing,
        "nonUniqueUrls": duplicate,
        "bytes": len(xml.encode("utf-8")),
        "sha256": hashlib.sha256(xml.encode("utf-8")).hexdigest(),
        "issues": issues,
    }


def audit_robots(text: str, *, origin: str = DEFAULT_ORIGIN) -> dict[str, Any]:
    expected = f"Sitemap: {normalize_origin(origin)}/sitemap.xml"
    folded = text.casefold()
    issues: list[str] = []
    if expected.casefold() not in folded:
        issues.append("robots_sitemap_declaration_missing")
    if re.search(r"(?im)^\s*disallow:\s*/\s*$", text):
        issues.append("robots_blocks_entire_site")
    return {
        "ok": not issues,
        "expectedDeclaration": expected,
        "bytes": len(text.encode("utf-8")),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "issues": issues,
    }


@dataclass(frozen=True)
class ResponseSnapshot:
    status: int
    content_type: str
    effective_url: str
    body: str
    headers: dict[str, str]


def fetch(url: str, *, accept: str, timeout: int = 30) -> ResponseSnapshot:
    request = Request(
        url,
        headers={
            "User-Agent": "ALO186-elevator-live-origin-receipt/1.0",
            "Accept": accept,
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
            return ResponseSnapshot(
                status=int(response.status),
                content_type=response.headers.get_content_type(),
                effective_url=response.geturl(),
                body=raw.decode(charset, errors="replace"),
                headers={key.casefold(): value for key, value in response.headers.items()},
            )
    except HTTPError as exc:
        body = exc.read().decode(exc.headers.get_content_charset() or "utf-8", errors="replace")
        return ResponseSnapshot(
            status=int(exc.code),
            content_type=exc.headers.get_content_type(),
            effective_url=exc.geturl(),
            body=body,
            headers={key.casefold(): value for key, value in exc.headers.items()},
        )


def cache_receipt(headers: dict[str, str]) -> dict[str, str]:
    keys = ("age", "cache-control", "cf-cache-status", "etag", "last-modified", "server", "vary")
    return {key: headers.get(key, "") for key in keys if headers.get(key)}


def verify_once(origin: str, *, timeout: int = 30) -> dict[str, Any]:
    normalized_origin = normalize_origin(origin)
    nonce = f"{int(time.time())}-{time.time_ns()}"
    routes: list[dict[str, Any]] = []
    issues: list[str] = []

    for index, spec in enumerate(ROUTES):
        separator = "&" if "?" in spec.path else "?"
        url = f"{normalized_origin}{spec.path}{separator}live_receipt={nonce}-{index}"
        snapshot = fetch(url, accept="text/html,application/xhtml+xml", timeout=timeout)
        route_report = audit_html(
            snapshot.body,
            spec,
            origin=normalized_origin,
            effective_url=snapshot.effective_url,
        )
        route_report.update({
            "status": snapshot.status,
            "contentType": snapshot.content_type,
            "effectiveUrl": snapshot.effective_url,
            "cache": cache_receipt(snapshot.headers),
        })
        if snapshot.status != 200:
            route_report["issues"].append(f"http_status:{snapshot.status}")
        if snapshot.content_type.casefold() not in HTML_MEDIA_TYPES:
            route_report["issues"].append("html_content_type_required")
        route_report["issues"] = sorted(set(route_report["issues"]))
        route_report["ok"] = not route_report["issues"]
        if not route_report["ok"]:
            issues.append(f"route_failed:{spec.path}")
        routes.append(route_report)

    sitemap_snapshot = fetch(
        f"{normalized_origin}/sitemap.xml?live_receipt={nonce}",
        accept="application/xml,text/xml,text/plain",
        timeout=timeout,
    )
    sitemap = audit_sitemap(sitemap_snapshot.body, origin=normalized_origin)
    sitemap.update({
        "status": sitemap_snapshot.status,
        "contentType": sitemap_snapshot.content_type,
        "effectiveUrl": sitemap_snapshot.effective_url,
        "cache": cache_receipt(sitemap_snapshot.headers),
    })
    if sitemap_snapshot.status != 200:
        sitemap["issues"].append(f"http_status:{sitemap_snapshot.status}")
    if sitemap_snapshot.content_type.casefold() not in SITEMAP_MEDIA_TYPES:
        sitemap["issues"].append("sitemap_content_type_unexpected")
    sitemap["issues"] = sorted(set(sitemap["issues"]))
    sitemap["ok"] = not sitemap["issues"]
    if not sitemap["ok"]:
        issues.append("sitemap_failed")

    robots_snapshot = fetch(
        f"{normalized_origin}/robots.txt?live_receipt={nonce}",
        accept="text/plain,*/*;q=0.1",
        timeout=timeout,
    )
    robots = audit_robots(robots_snapshot.body, origin=normalized_origin)
    robots.update({
        "status": robots_snapshot.status,
        "contentType": robots_snapshot.content_type,
        "effectiveUrl": robots_snapshot.effective_url,
        "cache": cache_receipt(robots_snapshot.headers),
    })
    if robots_snapshot.status != 200:
        robots["issues"].append(f"http_status:{robots_snapshot.status}")
    robots["issues"] = sorted(set(robots["issues"]))
    robots["ok"] = not robots["issues"]
    if not robots["ok"]:
        issues.append("robots_failed")

    fingerprint_source = "\n".join(
        [item["sha256"] for item in routes] + [sitemap["sha256"], robots["sha256"]]
    )
    return {
        "ok": not issues,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "origin": normalized_origin,
        "routeCount": len(routes),
        "routes": routes,
        "sitemap": sitemap,
        "robots": robots,
        "liveFingerprint": hashlib.sha256(fingerprint_source.encode("ascii")).hexdigest(),
        "issues": issues,
    }


def verify_with_retry(
    origin: str,
    *,
    attempts: int,
    sleep_seconds: int,
    timeout: int,
) -> dict[str, Any]:
    if attempts < 1:
        raise ValueError("attempts en az 1 olmalıdır")
    reports: list[dict[str, Any]] = []
    last_error = ""
    for attempt in range(1, attempts + 1):
        try:
            report = verify_once(origin, timeout=timeout)
            report["attempt"] = attempt
            reports.append(report)
            if report["ok"]:
                report["attemptsUsed"] = attempt
                report["previousFailures"] = [item["issues"] for item in reports[:-1]]
                return report
            last_error = json.dumps(report["issues"], ensure_ascii=False)
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            reports.append({
                "ok": False,
                "attempt": attempt,
                "checkedAt": datetime.now(timezone.utc).isoformat(),
                "issues": [last_error],
            })
        if attempt < attempts:
            time.sleep(sleep_seconds)

    return {
        "ok": False,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "origin": normalize_origin(origin),
        "attemptsUsed": attempts,
        "issues": ["live_origin_not_verified", last_error],
        "attemptReports": reports,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ALO186 asansör sürekliliği rotaları için canlı origin, cache ve sitemap makbuzu üretir."
    )
    parser.add_argument("--origin", default=DEFAULT_ORIGIN)
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--sleep-seconds", type=int, default=20)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    report = verify_with_retry(
        args.origin,
        attempts=args.attempts,
        sleep_seconds=args.sleep_seconds,
        timeout=args.timeout,
    )
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    sys.stdout.write(payload)
    if args.strict and not report.get("ok"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
