from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import html
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable

VERSION = 225
DEFAULT_ORIGIN = "https://alo186.com"
CANONICAL_HOST = "alo186.com"
WWW_HOST = "www.alo186.com"
USER_AGENT = "ALO186-Live-Origin-Quality/225 (+https://alo186.com/)"
CRITICAL_ROUTES = (
    "/",
    "/elektrik-portali/",
    "/edas-bul/",
    "/elektrik-durum-merkezi/",
    "/hesaplama/",
    "/amazon-elektrik-urunleri/",
    "/akilli-urun-secimi/",
    "/urun-bilgi-grafigi/",
    "/arama/",
)
PERSONAL_FIELD_TOKENS = (
    "ad-soyad", "ad_soyad", "fullname", "full-name", "email", "e-posta",
    "eposta", "telefon", "phone", "address", "açık-adres", "acik-adres",
    "abone", "subscriber", "tc-kimlik", "tckn", "tesisat-no",
)
NON_HTTP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:", "blob:")
STATIC_ASSET_SUFFIXES = (".css", ".js", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".avif", ".gif", ".ico", ".woff", ".woff2")
DYNAMIC_COUNT_PATTERNS = (
    re.compile(r"\b\d+\s+rehber(?:in)?\b", re.I),
    re.compile(r"\b\d+\s+(?:model|ürün|urun)(?:i)?\s+doğrulanmış\b", re.I),
    re.compile(r"\b\d+\s+kaynaklı\s+makale\b", re.I),
)


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    url: str = ""
    detail: str = ""


@dataclass
class RedirectHop:
    status: int
    source: str
    target: str


@dataclass
class FetchResult:
    requested_url: str
    final_url: str = ""
    status: int = 0
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    elapsed_ms: int = 0
    redirects: list[RedirectHop] = field(default_factory=list)
    error: str = ""

    def text(self) -> str:
        if not self.body:
            return ""
        content_type = self.headers.get("content-type", "")
        match = re.search(r"charset=([^;\s]+)", content_type, re.I)
        charset = match.group(1).strip('"\'') if match else "utf-8"
        try:
            return self.body.decode(charset, errors="replace")
        except LookupError:
            return self.body.decode("utf-8", errors="replace")


@dataclass
class HtmlAudit:
    lang: str = ""
    title: str = ""
    description_count: int = 0
    viewport_ok: bool = False
    h1_count: int = 0
    canonical_values: list[str] = field(default_factory=list)
    robots_values: list[str] = field(default_factory=list)
    jsonld_blocks: list[str] = field(default_factory=list)
    references: list[tuple[str, str]] = field(default_factory=list)
    images: list[dict[str, str]] = field(default_factory=list)
    ids: set[str] = field(default_factory=set)
    main_ids: set[str] = field(default_factory=set)
    skip_targets: list[str] = field(default_factory=list)
    personal_fields: list[str] = field(default_factory=list)
    placeholder_links: int = 0
    visible_parts: list[str] = field(default_factory=list)
    skip_depth: int = 0

    @property
    def visible_text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.visible_parts)).strip()


@dataclass
class LighthouseProfile:
    profile: str
    path: str
    performance: float | None = None
    accessibility: float | None = None
    best_practices: float | None = None
    seo: float | None = None
    lcp_ms: float | None = None
    cls: float | None = None
    tbt_ms: float | None = None
    speed_index_ms: float | None = None
    total_byte_weight: float | None = None
    audited_url: str = ""


@dataclass
class Report:
    version: int
    checked_at: str
    origin: str
    expected_commit: str
    hosting_mode: str = "unknown"
    ok: bool = False
    critical_route_count: int = len(CRITICAL_ROUTES)
    successful_critical_routes: int = 0
    sitemap_declared_count: int = 0
    sitemap_url_count: int = 0
    sitemap_checked_count: int = 0
    internal_link_count: int = 0
    internal_broken_count: int = 0
    internal_redirect_count: int = 0
    image_count: int = 0
    image_error_count: int = 0
    static_asset_count: int = 0
    static_asset_error_count: int = 0
    lighthouse: list[LighthouseProfile] = field(default_factory=list)
    field_core_web_vitals_available: bool = False
    routes: dict[str, dict[str, Any]] = field(default_factory=dict)
    sitemaps: list[dict[str, Any]] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)

    def add(self, severity: str, code: str, message: str, url: str = "", detail: str = "") -> None:
        self.issues.append(Issue(severity, code, message, url, detail))

    def to_json(self) -> dict[str, Any]:
        value = asdict(self)
        value["severityCounts"] = {
            severity: sum(1 for issue in self.issues if issue.severity == severity)
            for severity in ("P0", "P1", "P2", "INFO")
        }
        return value


class RedirectRecorder(urllib.request.HTTPRedirectHandler):
    def __init__(self, hops: list[RedirectHop]):
        super().__init__()
        self.hops = hops

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        self.hops.append(RedirectHop(int(code), req.full_url, urllib.parse.urljoin(req.full_url, newurl)))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


class PageParser(HTMLParser):
    HIDDEN = {"script", "style", "noscript", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.audit = HtmlAudit()
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.casefold()
        values = {str(key).casefold(): (value or "") for key, value in attrs}
        if name == "html":
            self.audit.lang = values.get("lang", "")
        if name in self.HIDDEN:
            self.audit.skip_depth += 1
        if name == "title":
            self.in_title = True
        identifier = values.get("id")
        if identifier:
            self.audit.ids.add(identifier)
        if name == "main" and identifier:
            self.audit.main_ids.add(identifier)
        if name == "h1":
            self.audit.h1_count += 1
        if name == "meta":
            meta_name = values.get("name", "").casefold()
            content = values.get("content", "")
            if meta_name == "viewport" and "width=device-width" in content.casefold():
                self.audit.viewport_ok = True
            elif meta_name == "description" and content.strip():
                self.audit.description_count += 1
            elif meta_name == "robots":
                self.audit.robots_values.append(content)
        if name == "link" and "canonical" in values.get("rel", "").casefold().split() and values.get("href"):
            self.audit.canonical_values.append(values["href"])
        if name == "script" and values.get("type", "").casefold() == "application/ld+json":
            self.audit.jsonld_blocks.append("")
        for attribute in ("href", "src", "action", "poster", "data-src"):
            reference = values.get(attribute)
            if reference:
                self.audit.references.append((attribute, reference))
                if attribute == "href" and reference.strip() == "#":
                    self.audit.placeholder_links += 1
        if name == "a" and "skip-link" in values.get("class", "").split():
            target = values.get("href", "")
            if target.startswith("#") and len(target) > 1:
                self.audit.skip_targets.append(target[1:])
        if name == "img":
            self.audit.images.append(values)
        if name in {"input", "textarea", "select"}:
            field_type = values.get("type", "").casefold()
            identity = " ".join((values.get("name", ""), values.get("id", ""), values.get("autocomplete", ""))).casefold()
            if field_type in {"email", "tel"} or any(token in identity for token in PERSONAL_FIELD_TOKENS):
                self.audit.personal_fields.append(identity.strip() or field_type)

    def handle_endtag(self, tag: str) -> None:
        name = tag.casefold()
        if name == "title":
            self.in_title = False
        if name in self.HIDDEN and self.audit.skip_depth:
            self.audit.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.audit.title += data
        if self.audit.jsonld_blocks and self.audit.skip_depth and self.get_starttag_text() is not None:
            # JSON-LD is reparsed from the source with a regular expression below.
            pass
        if not self.audit.skip_depth and data.strip():
            self.audit.visible_parts.append(data)


def parse_html(source: str) -> HtmlAudit:
    parser = PageParser()
    parser.feed(source)
    parser.close()
    parser.audit.title = re.sub(r"\s+", " ", html.unescape(parser.audit.title)).strip()
    parser.audit.jsonld_blocks = re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        source,
        re.I | re.S,
    )
    return parser.audit


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def lower_headers(headers: Iterable[tuple[str, str]]) -> dict[str, str]:
    return {str(key).casefold(): str(value) for key, value in headers}


def fetch(url: str, timeout: float = 20.0, max_bytes: int = 5_000_000, follow_redirects: bool = True) -> FetchResult:
    hops: list[RedirectHop] = []
    handlers: list[Any] = [urllib.request.HTTPSHandler(context=ssl.create_default_context())]
    handlers.append(RedirectRecorder(hops) if follow_redirects else NoRedirect())
    opener = urllib.request.build_opener(*handlers)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml,text/plain,image/avif,image/webp,image/*,*/*;q=0.5",
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
        },
    )
    start = time.monotonic()
    try:
        with opener.open(request, timeout=timeout) as response:
            body = response.read(max_bytes + 1)
            if len(body) > max_bytes:
                body = body[:max_bytes]
            return FetchResult(
                requested_url=url,
                final_url=response.geturl(),
                status=int(response.status),
                headers=lower_headers(response.headers.items()),
                body=body,
                elapsed_ms=int((time.monotonic() - start) * 1000),
                redirects=hops,
            )
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read(max_bytes)
        except OSError:
            body = b""
        return FetchResult(
            requested_url=url,
            final_url=exc.geturl() or url,
            status=int(exc.code),
            headers=lower_headers(exc.headers.items()) if exc.headers else {},
            body=body,
            elapsed_ms=int((time.monotonic() - start) * 1000),
            redirects=hops,
            error=f"HTTPError: {exc}",
        )
    except (urllib.error.URLError, TimeoutError, OSError, ssl.SSLError) as exc:
        return FetchResult(
            requested_url=url,
            final_url=url,
            elapsed_ms=int((time.monotonic() - start) * 1000),
            redirects=hops,
            error=f"{type(exc).__name__}: {exc}",
        )


def normalize_route_path(path: str) -> str:
    clean = urllib.parse.unquote(path or "/")
    clean = "/" + clean.lstrip("/")
    clean = re.sub(r"/{2,}", "/", clean)
    return clean


def equivalent_path(left: str, right: str) -> bool:
    def normalized(value: str) -> str:
        path = normalize_route_path(urllib.parse.urlsplit(value).path)
        return "/" if path == "/" else path.rstrip("/")
    return normalized(left) == normalized(right)


def jsonld_types(payload: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(payload, dict):
        value = payload.get("@type")
        if isinstance(value, str):
            found.add(value)
        elif isinstance(value, list):
            found.update(str(item) for item in value)
        for nested in payload.values():
            found.update(jsonld_types(nested))
    elif isinstance(payload, list):
        for nested in payload:
            found.update(jsonld_types(nested))
    return found


def resolve_url(origin: str, page_url: str, reference: str) -> str | None:
    reference = html.unescape(reference.strip())
    if not reference or reference.startswith(NON_HTTP_SCHEMES) or reference.startswith("#"):
        return None
    absolute = urllib.parse.urljoin(page_url, reference)
    parsed = urllib.parse.urlsplit(absolute)
    if parsed.scheme not in {"http", "https"}:
        return None
    host = (parsed.hostname or "").casefold().removeprefix("www.")
    if host != urllib.parse.urlsplit(origin).hostname:
        return None
    return urllib.parse.urlunsplit(("https", CANONICAL_HOST, normalize_route_path(parsed.path), parsed.query, ""))


def audit_www_redirect(report: Report, timeout: float) -> None:
    result = fetch("https://www.alo186.com/", timeout=timeout, follow_redirects=False)
    location = result.headers.get("location", "")
    if result.status not in {301, 308}:
        report.add("P1", "www_redirect_not_permanent", "www alan adı kalıcı 301/308 yönlendirmesi vermiyor.", result.requested_url, f"HTTP {result.status}")
        return
    target = urllib.parse.urljoin(result.requested_url, location)
    if target != "https://alo186.com/":
        report.add("P1", "www_redirect_wrong_target", "www yönlendirmesi apex ana sayfaya gitmiyor.", result.requested_url, target)


def audit_page(report: Report, origin: str, route: str, response: FetchResult) -> HtmlAudit | None:
    url = origin.rstrip("/") + route
    route_report: dict[str, Any] = {
        "status": response.status,
        "finalUrl": response.final_url,
        "elapsedMs": response.elapsed_ms,
        "redirects": [asdict(item) for item in response.redirects],
    }
    report.routes[route] = route_report
    if response.error and not response.status:
        report.add("P0", "critical_route_transport_error", "Kritik rota ağ/TLS hatası verdi.", url, response.error)
        return None
    if response.status != 200:
        report.add("P0" if route == "/" else "P1", "critical_route_http", "Kritik rota HTTP 200 vermiyor.", url, f"HTTP {response.status}")
        return None
    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type.casefold():
        report.add("P1", "critical_route_content_type", "Kritik rota HTML içeriği vermiyor.", url, content_type)
        return None
    if response.redirects:
        report.add("P2", "critical_route_redirect", "Canonical kritik rota ek yönlendirme zinciri kullanıyor.", url, json.dumps([asdict(item) for item in response.redirects], ensure_ascii=False))
    audit = parse_html(response.text())
    route_report.update({
        "title": audit.title,
        "h1Count": audit.h1_count,
        "canonical": audit.canonical_values,
        "jsonLdCount": len(audit.jsonld_blocks),
        "imageCount": len(audit.images),
    })
    report.successful_critical_routes += 1
    if not audit.lang:
        report.add("P1", "missing_lang", "HTML lang niteliği eksik.", url)
    if not audit.title:
        report.add("P1", "missing_title", "Title eksik.", url)
    if audit.description_count != 1:
        report.add("P1", "description_count", "Tek ve dolu meta description gerekli.", url, str(audit.description_count))
    if not audit.viewport_ok:
        report.add("P1", "missing_viewport", "Mobil viewport eksik.", url)
    if audit.h1_count != 1:
        report.add("P1", "h1_count", "Sayfa tam bir H1 taşımalı.", url, str(audit.h1_count))
    if len(audit.canonical_values) != 1:
        report.add("P1", "canonical_count", "Sayfa tek canonical taşımalı.", url, json.dumps(audit.canonical_values, ensure_ascii=False))
    else:
        canonical = urllib.parse.urlsplit(audit.canonical_values[0])
        if canonical.scheme != "https" or (canonical.hostname or "").casefold() != CANONICAL_HOST:
            report.add("P1", "canonical_origin", "Canonical yalnız https://alo186.com originini kullanmalı.", url, audit.canonical_values[0])
        elif not equivalent_path(canonical.path, route):
            report.add("P1", "canonical_path", "Canonical path canlı rota ile uyuşmuyor.", url, audit.canonical_values[0])
    robots_text = " ".join(audit.robots_values).casefold()
    x_robots = response.headers.get("x-robots-tag", "").casefold()
    if "noindex" in robots_text or "noindex" in x_robots:
        report.add("P1", "critical_noindex", "Kritik rota noindex olamaz.", url, f"meta={robots_text}; header={x_robots}")
    if not audit.jsonld_blocks:
        report.add("P1", "missing_jsonld", "Kritik rota yapılandırılmış veri taşımıyor.", url)
    else:
        observed: set[str] = set()
        for block in audit.jsonld_blocks:
            try:
                observed.update(jsonld_types(json.loads(html.unescape(block.strip()))))
            except json.JSONDecodeError as exc:
                report.add("P1", "invalid_jsonld", "JSON-LD ayrıştırılamadı.", url, str(exc))
        route_report["schemaTypes"] = sorted(observed)
    if not audit.skip_targets or not any(target in audit.main_ids or target in audit.ids for target in audit.skip_targets):
        report.add("P1", "skip_link", "Skip-link görünür bir main hedefiyle eşleşmiyor.", url, json.dumps(audit.skip_targets))
    if audit.personal_fields:
        report.add("P0", "personal_data_field", "Kritik sayfa kişisel veri alanı yayımlıyor.", url, ", ".join(audit.personal_fields))
    if audit.placeholder_links:
        report.add("P2", "placeholder_link", "İşlevsiz href=# bağlantısı bulundu.", url, str(audit.placeholder_links))
    for image in audit.images:
        report.image_count += 1
        if "alt" not in image:
            report.add("P1", "image_missing_alt", "Görsel alt niteliği taşımıyor.", url, image.get("src", ""))
        if not (image.get("width") and image.get("height")):
            report.add("P2", "image_intrinsic_size", "Görsel intrinsic width/height taşımıyor; CLS riski var.", url, image.get("src", ""))
        if image.get("loading", "").casefold() not in {"lazy", "eager"}:
            report.add("P2", "image_loading_policy", "Görsel loading politikası açık değil.", url, image.get("src", ""))
    for pattern in DYNAMIC_COUNT_PATTERNS:
        matches = pattern.findall(audit.visible_text)
        if matches:
            report.add("P2", "brittle_visible_count", "Canlı sayfada hızla eskiyebilen sabit içerik/ürün sayacı var.", url, pattern.pattern)
    visible = audit.visible_text.casefold()
    if route == "/" and ("bağımsız" not in visible or "kamu kurumu değildir" not in visible):
        report.add("P0", "independence_disclosure", "Ana sayfada bağımsızlık ve kamu kurumu olmadığı açıklaması eksik.", url)
    return audit


def parse_robots(text: str) -> tuple[bool, list[str]]:
    allow_root = False
    sitemaps: list[str] = []
    current_agents: list[str] = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        key = key.casefold()
        if key == "user-agent":
            current_agents = [value.casefold()]
        elif key == "allow" and "*" in current_agents and value == "/":
            allow_root = True
        elif key == "disallow" and "*" in current_agents and value == "/":
            allow_root = False
        elif key == "sitemap" and value:
            sitemaps.append(value)
    return allow_root, sitemaps


def parse_sitemap(text: str) -> tuple[str, list[str]]:
    root = ET.fromstring(text)
    local = root.tag.rsplit("}", 1)[-1]
    namespace = root.tag.split("}", 1)[0].lstrip("{") if "}" in root.tag else ""
    prefix = f"{{{namespace}}}" if namespace else ""
    if local == "urlset":
        return "urlset", [str(item.text or "").strip() for item in root.findall(f"{prefix}url/{prefix}loc") if str(item.text or "").strip()]
    if local == "sitemapindex":
        return "sitemapindex", [str(item.text or "").strip() for item in root.findall(f"{prefix}sitemap/{prefix}loc") if str(item.text or "").strip()]
    raise ValueError(f"Desteklenmeyen sitemap kökü: {root.tag}")


def audit_robots_and_sitemaps(report: Report, origin: str, timeout: float) -> list[str]:
    robots_url = origin.rstrip("/") + "/robots.txt"
    robots = fetch(robots_url, timeout=timeout)
    if robots.status != 200:
        report.add("P0", "robots_http", "robots.txt HTTP 200 vermiyor.", robots_url, f"HTTP {robots.status}; {robots.error}")
        return []
    allow_root, declared = parse_robots(robots.text())
    if not allow_root:
        report.add("P0", "robots_blocks_root", "robots.txt tüm siteyi taramaya açmıyor.", robots_url)
    if not declared:
        report.add("P1", "robots_missing_sitemap", "robots.txt sitemap bildirmiyor.", robots_url)
    report.sitemap_declared_count = len(declared)
    queue = list(dict.fromkeys(declared))
    visited: set[str] = set()
    urls: list[str] = []
    while queue:
        sitemap_url = queue.pop(0)
        if sitemap_url in visited:
            continue
        visited.add(sitemap_url)
        parsed_url = urllib.parse.urlsplit(sitemap_url)
        if parsed_url.scheme != "https" or (parsed_url.hostname or "").casefold() != CANONICAL_HOST:
            report.add("P1", "sitemap_origin", "Sitemap bildirimi apex HTTPS originini kullanmıyor.", sitemap_url)
            continue
        response = fetch(sitemap_url, timeout=timeout)
        item = {"url": sitemap_url, "status": response.status, "elapsedMs": response.elapsed_ms, "urlCount": 0, "kind": ""}
        report.sitemaps.append(item)
        if response.status != 200:
            report.add("P1", "sitemap_http", "Sitemap HTTP 200 vermiyor.", sitemap_url, f"HTTP {response.status}; {response.error}")
            continue
        try:
            kind, entries = parse_sitemap(response.text())
        except (ET.ParseError, ValueError) as exc:
            report.add("P1", "sitemap_xml", "Sitemap XML ayrıştırılamadı.", sitemap_url, str(exc))
            continue
        item["kind"] = kind
        item["urlCount"] = len(entries)
        if kind == "sitemapindex":
            queue.extend(entry for entry in entries if entry not in visited)
        else:
            urls.extend(entries)
    duplicates = len(urls) - len(set(urls))
    if duplicates:
        report.add("P1", "sitemap_duplicates", "Sitemaplerde yinelenen URL var.", detail=str(duplicates))
    unique = list(dict.fromkeys(urls))
    report.sitemap_url_count = len(unique)
    for url in unique:
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != "https" or (parsed.hostname or "").casefold() != CANONICAL_HOST:
            report.add("P1", "sitemap_entry_origin", "Sitemap URL’si apex HTTPS originini kullanmıyor.", url)
    if origin.rstrip("/") + "/" not in unique:
        report.add("P1", "sitemap_missing_home", "Ana sayfa sitemap envanterinde yok.", origin.rstrip("/") + "/")
    return unique


def audit_sitemap_pages(report: Report, urls: list[str], timeout: float, workers: int, max_urls: int) -> None:
    selected = urls[:max_urls]
    report.sitemap_checked_count = len(selected)
    def probe(url: str) -> tuple[str, FetchResult, HtmlAudit | None]:
        response = fetch(url, timeout=timeout)
        content_type = response.headers.get("content-type", "").casefold()
        audit = parse_html(response.text()) if response.status == 200 and "text/html" in content_type else None
        return url, response, audit
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        for url, response, audit in executor.map(probe, selected):
            if response.status != 200:
                report.add("P1", "sitemap_page_http", "Sitemap URL’si HTTP 200 vermiyor.", url, f"HTTP {response.status}; {response.error}")
                continue
            if audit is None:
                report.add("P1", "sitemap_page_not_html", "Sitemap URL’si HTML vermiyor.", url, response.headers.get("content-type", ""))
                continue
            robots = " ".join(audit.robots_values).casefold() + " " + response.headers.get("x-robots-tag", "").casefold()
            if "noindex" in robots:
                report.add("P1", "sitemap_noindex", "Noindex sayfa sitemap içinde bulunuyor.", url)
            if len(audit.canonical_values) != 1:
                report.add("P1", "sitemap_canonical_count", "Sitemap sayfası tek canonical taşımıyor.", url, json.dumps(audit.canonical_values))
            elif not equivalent_path(audit.canonical_values[0], url) or (urllib.parse.urlsplit(audit.canonical_values[0]).hostname or "").casefold() != CANONICAL_HOST:
                report.add("P1", "sitemap_noncanonical", "Sitemap URL’si başka bir canonical hedef gösteriyor.", url, audit.canonical_values[0])


def audit_references(report: Report, origin: str, page_audits: dict[str, tuple[str, HtmlAudit]], timeout: float, workers: int) -> None:
    references: dict[str, str] = {}
    image_urls: set[str] = set()
    asset_urls: set[str] = set()
    for _route, (page_url, audit) in page_audits.items():
        for attribute, reference in audit.references:
            resolved = resolve_url(origin, page_url, reference)
            if not resolved:
                continue
            references.setdefault(resolved, page_url)
            path = urllib.parse.urlsplit(resolved).path.casefold()
            if attribute in {"src", "data-src", "poster"} and path.endswith((".png", ".jpg", ".jpeg", ".webp", ".svg", ".avif", ".gif")):
                image_urls.add(resolved)
            if path.endswith(STATIC_ASSET_SUFFIXES):
                asset_urls.add(resolved)
    report.internal_link_count = len(references)
    report.static_asset_count = len(asset_urls)
    def probe(item: tuple[str, str]) -> tuple[str, str, FetchResult]:
        url, source = item
        return url, source, fetch(url, timeout=timeout)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        for url, source, response in executor.map(probe, references.items()):
            if response.status >= 400 or not response.status:
                report.internal_broken_count += 1
                if url in asset_urls:
                    report.static_asset_error_count += 1
                if url in image_urls:
                    report.image_error_count += 1
                report.add("P1", "broken_internal_reference", "Kritik sayfadaki iç bağlantı veya varlık yüklenemiyor.", url, f"Kaynak={source}; HTTP {response.status}; {response.error}")
            elif response.redirects:
                report.internal_redirect_count += 1
                report.add("P2", "internal_redirect", "Kritik sayfa canonical olmayan yönlendirmeli iç bağlantı kullanıyor.", url, json.dumps([asdict(item) for item in response.redirects], ensure_ascii=False))
            if url in asset_urls and response.status == 200:
                content_type = response.headers.get("content-type", "").casefold()
                suffix = urllib.parse.urlsplit(url).path.casefold()
                if suffix.endswith(".css") and "text/css" not in content_type:
                    report.add("P1", "css_content_type", "CSS yanlış content-type ile sunuluyor.", url, content_type)
                if suffix.endswith(".js") and not any(token in content_type for token in ("javascript", "ecmascript", "text/plain")):
                    report.add("P1", "js_content_type", "JavaScript yanlış content-type ile sunuluyor.", url, content_type)


def lighthouse_profile(path: Path, profile: str) -> LighthouseProfile:
    payload = json.loads(path.read_text(encoding="utf-8"))
    categories = payload.get("categories", {})
    audits = payload.get("audits", {})
    score = lambda key: categories.get(key, {}).get("score")  # noqa: E731
    numeric = lambda key: audits.get(key, {}).get("numericValue")  # noqa: E731
    return LighthouseProfile(
        profile=profile,
        path=str(path),
        performance=score("performance"),
        accessibility=score("accessibility"),
        best_practices=score("best-practices"),
        seo=score("seo"),
        lcp_ms=numeric("largest-contentful-paint"),
        cls=numeric("cumulative-layout-shift"),
        tbt_ms=numeric("total-blocking-time"),
        speed_index_ms=numeric("speed-index"),
        total_byte_weight=numeric("total-byte-weight"),
        audited_url=str(payload.get("finalDisplayedUrl") or payload.get("finalUrl") or ""),
    )


def audit_lighthouse(report: Report, mobile: Path | None, desktop: Path | None) -> None:
    for path, profile in ((mobile, "mobile"), (desktop, "desktop")):
        if path is None:
            continue
        if not path.is_file():
            report.add("P1", "lighthouse_missing", "Lighthouse raporu bulunamadı.", detail=str(path))
            continue
        try:
            item = lighthouse_profile(path, profile)
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            report.add("P1", "lighthouse_invalid", "Lighthouse raporu ayrıştırılamadı.", detail=f"{path}: {exc}")
            continue
        report.lighthouse.append(item)
        thresholds = {
            "performance": 0.75 if profile == "mobile" else 0.85,
            "accessibility": 0.95,
            "best_practices": 0.90,
            "seo": 0.95,
        }
        for field_name, minimum in thresholds.items():
            value = getattr(item, field_name)
            if value is None or value < minimum:
                report.add("P1", f"lighthouse_{field_name}", f"{profile} Lighthouse {field_name} eşiğin altında.", item.audited_url, f"değer={value}; eşik={minimum}")
        lcp_limit = 4_000 if profile == "mobile" else 2_500
        tbt_limit = 600 if profile == "mobile" else 300
        if item.lcp_ms is None or item.lcp_ms > lcp_limit:
            report.add("P1", "lighthouse_lcp", f"{profile} Lighthouse LCP laboratuvar eşiğini aşıyor.", item.audited_url, f"{item.lcp_ms} ms > {lcp_limit} ms")
        if item.cls is None or item.cls > 0.1:
            report.add("P1", "lighthouse_cls", f"{profile} Lighthouse CLS eşiğini aşıyor.", item.audited_url, f"{item.cls} > 0.1")
        if item.tbt_ms is None or item.tbt_ms > tbt_limit:
            report.add("P2", "lighthouse_tbt", f"{profile} Lighthouse TBT iyileştirilmeli.", item.audited_url, f"{item.tbt_ms} ms > {tbt_limit} ms")


def detect_hosting_mode(origin: str, timeout: float) -> tuple[str, str]:
    marker = fetch(origin.rstrip("/") + "/pages-release.json", timeout=timeout)
    if marker.status == 200:
        try:
            payload = json.loads(marker.text())
            return "github-pages", str(payload.get("commit") or "")
        except json.JSONDecodeError:
            return "invalid-release-marker", ""
    homepage = fetch(origin.rstrip("/") + "/", timeout=timeout)
    header_text = " ".join(f"{key}:{value}" for key, value in homepage.headers.items()).casefold()
    body = homepage.text().casefold()
    if "cloudflare" in header_text or "static-snapshot" in body or "chatgpt" in body or "vinext" in body:
        return "chatgpt-sites", ""
    return "external-host", ""


def render_markdown(report: Report) -> str:
    counts = report.to_json()["severityCounts"]
    lines = [
        "# ALO186 canlı-origin teknik kalite v225",
        "",
        f"- Kontrol: `{report.checked_at}`",
        f"- Origin: `{report.origin}`",
        f"- Hosting modu: `{report.hosting_mode}`",
        f"- Sonuç: **{'BAŞARILI' if report.ok else 'BAŞARISIZ'}**",
        f"- P0 / P1 / P2: **{counts['P0']} / {counts['P1']} / {counts['P2']}**",
        f"- Kritik rotalar: **{report.successful_critical_routes}/{report.critical_route_count}**",
        f"- Sitemap URL: **{report.sitemap_url_count}**; kontrol edilen: **{report.sitemap_checked_count}**",
        f"- Kırık iç referans: **{report.internal_broken_count}**; yönlendirmeli iç referans: **{report.internal_redirect_count}**",
        "",
        "## Bulgular",
        "",
    ]
    if not report.issues:
        lines.append("Bulgusuz tamamlandı.")
    else:
        for issue in sorted(report.issues, key=lambda item: ("P0", "P1", "P2", "INFO").index(item.severity)):
            suffix = f" — {issue.url}" if issue.url else ""
            detail = f" — {issue.detail}" if issue.detail else ""
            lines.append(f"- **{issue.severity} {issue.code}:** {issue.message}{suffix}{detail}")
    lines.extend(["", "## Core Web Vitals notu", "", "Lighthouse sonuçları kontrollü laboratuvar ölçümüdür. Gerçek kullanıcı Core Web Vitals alan verisi bu makbuzda ayrıca doğrulanmadıkça `field_core_web_vitals_available=false` kalır.", ""])
    return "\n".join(lines)


def run(
    *,
    origin: str,
    expected_commit: str,
    timeout: float,
    workers: int,
    max_sitemap_urls: int,
    mobile_lighthouse: Path | None,
    desktop_lighthouse: Path | None,
) -> Report:
    origin = origin.rstrip("/")
    report = Report(version=VERSION, checked_at=utc_now(), origin=origin, expected_commit=expected_commit)
    report.hosting_mode, live_commit = detect_hosting_mode(origin, timeout)
    if live_commit and expected_commit and not live_commit.startswith(expected_commit) and not expected_commit.startswith(live_commit):
        report.add("P1", "live_commit_mismatch", "Canlı Pages commit’i beklenen kaynak commit ile uyuşmuyor.", origin + "/pages-release.json", f"live={live_commit}; expected={expected_commit}")
    elif not live_commit and expected_commit:
        report.add("INFO", "exact_commit_unavailable", "Dış canlı origin exact commit makbuzu sunmuyor; içerik ve teknik sözleşmeler bağımsız denetlendi.", origin)
    audit_www_redirect(report, timeout)
    page_audits: dict[str, tuple[str, HtmlAudit]] = {}
    for route in CRITICAL_ROUTES:
        page_url = origin + route
        response = fetch(page_url, timeout=timeout)
        audit = audit_page(report, origin, route, response)
        if audit is not None:
            page_audits[route] = (response.final_url or page_url, audit)
    sitemap_urls = audit_robots_and_sitemaps(report, origin, timeout)
    audit_sitemap_pages(report, sitemap_urls, timeout, workers, max_sitemap_urls)
    audit_references(report, origin, page_audits, timeout, workers)
    audit_lighthouse(report, mobile_lighthouse, desktop_lighthouse)
    report.ok = not any(issue.severity in {"P0", "P1"} for issue in report.issues)
    report.checked_at = utc_now()
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canlı origin teknik kalite, sitemap, bağlantı, erişilebilirlik ve Lighthouse denetimi")
    parser.add_argument("--origin", default=DEFAULT_ORIGIN)
    parser.add_argument("--expected-commit", default="")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--max-sitemap-urls", type=int, default=800)
    parser.add_argument("--mobile-lighthouse", type=Path)
    parser.add_argument("--desktop-lighthouse", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--no-fail", action="store_true", help="Rapor üretir fakat P0/P1 için exit 1 vermez")
    args = parser.parse_args()
    report = run(
        origin=args.origin,
        expected_commit=args.expected_commit,
        timeout=args.timeout,
        workers=args.workers,
        max_sitemap_urls=args.max_sitemap_urls,
        mobile_lighthouse=args.mobile_lighthouse,
        desktop_lighthouse=args.desktop_lighthouse,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report.to_json(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report.to_json(), ensure_ascii=False, indent=2))
    if not report.ok and not args.no_fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
