from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_ORIGIN = "https://alo186.com"
DEFAULT_REPOSITORY = "ozaneryavuz/chatgpt"

LANGUAGE_PAIRS: dict[str, str] = {
    "/en/": "/elektrik-portali",
    "/en/electricity-outage-turkey/": "/elektrik-kesintisi",
    "/en/electricity-distribution-company-finder/": "/edas-bul",
    "/en/emergency-numbers-turkey/": "/acil-numaralar",
    "/en/about/": "/hakkimizda",
    "/en/editorial-methodology/": "/yayin-ilkeleri",
    "/en/sources/": "/kaynaklar",
    "/en/privacy/": "/gizlilik",
    "/en/contact/": "/iletisim",
    "/en/affiliate-disclosure/": "/yasal/amazon-satis-ortakligi",
}

CALL_ROUTES = {
    "/en/",
    "/en/electricity-outage-turkey/",
    "/en/electricity-distribution-company-finder/",
    "/en/emergency-numbers-turkey/",
}

SAFETY_COMMERCE_CLOSED_ROUTES = {
    "/en/",
    "/en/electricity-outage-turkey/",
    "/en/emergency-numbers-turkey/",
}

FORBIDDEN_SAFETY_TOKENS = (
    "amazon.com",
    "amazon.com.tr",
    "amzn.to",
    'rel="sponsored',
    "buy now",
    "limited stock",
    "add to cart",
)


class LiveValidationError(RuntimeError):
    pass


@dataclass
class RouteResult:
    route: str
    status: int
    canonical: str
    html_lang: str
    checks: list[str] = field(default_factory=list)


@dataclass
class SmokeReport:
    ok: bool
    checked_at: str
    origin: str
    expected_commit: str
    live_commit: str = ""
    live_commit_relation: str = "unknown"
    attempts: int = 0
    route_count: int = 0
    sitemap_url_count: int = 0
    routes: list[RouteResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


def _attributes(tag: str) -> dict[str, str]:
    return {
        key.casefold(): value
        for key, _quote, value in re.findall(
            r"([:\w-]+)\s*=\s*([\"'])(.*?)\2",
            tag,
            flags=re.IGNORECASE | re.DOTALL,
        )
    }


def _link_relations(html: str) -> list[dict[str, str]]:
    return [_attributes(tag) for tag in re.findall(r"<link\b[^>]*>", html, flags=re.IGNORECASE)]


def _meta_elements(html: str) -> list[dict[str, str]]:
    return [_attributes(tag) for tag in re.findall(r"<meta\b[^>]*>", html, flags=re.IGNORECASE)]


def _html_language(html: str) -> str:
    match = re.search(r"<html\b[^>]*\blang\s*=\s*([\"'])(.*?)\1", html, flags=re.IGNORECASE | re.DOTALL)
    return match.group(2).strip() if match else ""


def _canonical(html: str) -> str:
    for attrs in _link_relations(html):
        rel = {item.casefold() for item in attrs.get("rel", "").split()}
        if "canonical" in rel:
            return attrs.get("href", "").strip()
    return ""


def _alternates(html: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for attrs in _link_relations(html):
        rel = {item.casefold() for item in attrs.get("rel", "").split()}
        hreflang = attrs.get("hreflang", "").strip()
        href = attrs.get("href", "").strip()
        if "alternate" in rel and hreflang and href:
            result[hreflang.casefold()] = href
    return result


def _robots_content(html: str) -> str:
    for attrs in _meta_elements(html):
        if attrs.get("name", "").casefold() == "robots":
            return attrs.get("content", "").casefold()
    return ""


def _json_ld_blocks(html: str) -> list[dict[str, Any]]:
    blocks = re.findall(
        r"<script\b[^>]*type\s*=\s*([\"'])application/ld\+json\1[^>]*>(.*?)</script>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    parsed: list[dict[str, Any]] = []
    for _quote, block in blocks:
        value = json.loads(block)
        if not isinstance(value, dict):
            raise LiveValidationError("JSON-LD kök nesnesi object değil")
        parsed.append(value)
    return parsed


def _contains_in_language_en(value: Any) -> bool:
    if isinstance(value, dict):
        if value.get("inLanguage") == "en":
            return True
        return any(_contains_in_language_en(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_in_language_en(item) for item in value)
    return False


def parse_release_marker(release_text: str) -> str:
    release = json.loads(release_text)
    if not isinstance(release, dict):
        raise LiveValidationError("pages-release.json kök nesnesi object değil")
    return str(release.get("commit", "")).strip()


def validate_english_page(route: str, html: str, origin: str, status: int = 200) -> RouteResult:
    if route not in LANGUAGE_PAIRS:
        raise LiveValidationError(f"Bilinmeyen İngilizce rota: {route}")
    if status != 200:
        raise LiveValidationError(f"{route} HTTP {status}")

    checks: list[str] = []
    html_lang = _html_language(html)
    primary_lang = html_lang.casefold().replace("_", "-").split("-", 1)[0]
    if primary_lang != "en":
        raise LiveValidationError(f"{route} html lang beklenen en, bulunan {html_lang or 'boş'}")
    checks.append("html-lang-en")

    robots = _robots_content(html)
    if "index" not in robots or "noindex" in robots:
        raise LiveValidationError(f"{route} indekslenebilir robots sözleşmesini karşılamıyor: {robots or 'boş'}")
    checks.append("indexable")

    expected_canonical = origin.rstrip("/") + route
    canonical = _canonical(html)
    if canonical != expected_canonical:
        raise LiveValidationError(
            f"{route} canonical beklenen {expected_canonical}, bulunan {canonical or 'boş'}"
        )
    checks.append("self-canonical")

    alternates = _alternates(html)
    expected_turkish = origin.rstrip("/") + LANGUAGE_PAIRS[route]
    expected_alternates = {
        "en": expected_canonical,
        "tr-tr": expected_turkish,
        "x-default": expected_turkish,
    }
    for hreflang, expected_url in expected_alternates.items():
        actual = alternates.get(hreflang, "")
        if actual != expected_url:
            raise LiveValidationError(
                f"{route} hreflang {hreflang} beklenen {expected_url}, bulunan {actual or 'boş'}"
            )
    checks.append("reciprocal-hreflang")

    if not re.search(r"<h1\b", html, flags=re.IGNORECASE):
        raise LiveValidationError(f"{route} H1 eksik")
    if "Direct answer:" not in html:
        raise LiveValidationError(f"{route} doğrudan cevap bloğu eksik")
    checks.append("direct-answer")

    json_ld = _json_ld_blocks(html)
    if not json_ld:
        raise LiveValidationError(f"{route} JSON-LD eksik")
    if not any(_contains_in_language_en(block) for block in json_ld):
        raise LiveValidationError(f"{route} JSON-LD inLanguage=en eksik")
    checks.append("valid-json-ld")

    folded = html.casefold()
    if route in CALL_ROUTES:
        if 'href="tel:112"' not in folded or 'href="tel:186"' not in folded:
            raise LiveValidationError(f"{route} 112/186 doğrudan arama bağlantısı eksik")
        checks.append("112-186-call-links")
    if route == "/en/emergency-numbers-turkey/":
        if 'href="tel:187"' not in folded:
            raise LiveValidationError(f"{route} 187 doğrudan arama bağlantısı eksik")
        checks.append("187-call-link")

    if route in SAFETY_COMMERCE_CLOSED_ROUTES:
        found = [token for token in FORBIDDEN_SAFETY_TOKENS if token in folded]
        if found:
            raise LiveValidationError(f"{route} güvenlik sayfasında ticari token bulundu: {', '.join(found)}")
        checks.append("safety-commerce-closed")

    if route == "/en/electricity-distribution-company-finder/":
        required = (
    "81 provinces",
    "21 electricity distribution regions",
    'src="/edas-bul/companies.js"',
    'src="/en/assets/finder.js"',
)
        missing = [token for token in required if token not in html]
        if missing:
            raise LiveValidationError(f"{route} EDAŞ bulucu kapsamı eksik: {', '.join(missing)}")
        checks.append("81-provinces-21-companies")

    return RouteResult(
        route=route,
        status=status,
        canonical=canonical,
        html_lang=html_lang,
        checks=checks,
    )


def validate_sitemap(xml_text: str, origin: str) -> set[str]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise LiveValidationError(f"Sitemap XML parse hatası: {exc}") from exc

    urls = {
        element.text.strip()
        for element in root.iter()
        if element.tag.rsplit("}", 1)[-1] == "loc" and element.text and element.text.strip()
    }
    missing = [origin.rstrip("/") + route for route in LANGUAGE_PAIRS if origin.rstrip("/") + route not in urls]
    if missing:
        raise LiveValidationError("Sitemap İngilizce rota eksik: " + ", ".join(missing))
    return urls


def fetch_text(url: str, timeout: float = 25.0) -> tuple[int, str, dict[str, str]]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ALO186-English-Live-Smoke/1.0 (+https://alo186.com/en/)",
            "Accept": "text/html,application/json,application/xml,text/xml;q=0.9,*/*;q=0.5",
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            content_type = response.headers.get_content_charset() or "utf-8"
            return response.status, raw.decode(content_type, errors="replace"), dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, body, dict(exc.headers.items())


def compare_commits(repository: str, base: str, head: str, token: str = "") -> str:
    if not base or not head:
        return "unknown"
    if base == head:
        return "identical"
    url = f"https://api.github.com/repos/{repository}/compare/{base}...{head}"
    headers = {
        "User-Agent": "ALO186-English-Live-Smoke/1.0",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return "unknown"
    return str(payload.get("status", "unknown"))


def _cache_busted(url: str, expected_commit: str, attempt: int) -> str:
    separator = "&" if "?" in url else "?"
    query = urllib.parse.urlencode(
        {
            "alo186_release_check": expected_commit[:12] or "manual",
            "attempt": attempt,
            "ts": int(time.time()),
        }
    )
    return f"{url}{separator}{query}"


def run_live_smoke(
    *,
    origin: str,
    repository: str,
    expected_commit: str,
    github_token: str,
    attempts: int,
    interval: float,
    timeout: float,
    report_path: Path,
) -> SmokeReport:
    origin = origin.rstrip("/")
    report = SmokeReport(
        ok=False,
        checked_at=datetime.now(timezone.utc).isoformat(),
        origin=origin,
        expected_commit=expected_commit,
    )
    last_error = "Canlı doğrulama başlatılamadı"

    for attempt in range(1, attempts + 1):
        report.attempts = attempt
        try:
            release_url = _cache_busted(f"{origin}/pages-release.json", expected_commit, attempt)
            release_status, release_text, _headers = fetch_text(release_url, timeout=timeout)
            if release_status != 200:
                raise LiveValidationError(f"pages-release.json HTTP {release_status}")
            live_commit = parse_release_marker(release_text)
            report.live_commit = live_commit
            relation = compare_commits(repository, expected_commit, live_commit, github_token)
            report.live_commit_relation = relation
            if relation not in {"identical", "ahead"}:
                raise LiveValidationError(
                    f"Canlı commit beklenen yayını içermiyor: expected={expected_commit}, live={live_commit}, relation={relation}"
                )

            route_results: list[RouteResult] = []
            for route in LANGUAGE_PAIRS:
                url = _cache_busted(origin + route, expected_commit, attempt)
                status, html, _route_headers = fetch_text(url, timeout=timeout)
                route_results.append(validate_english_page(route, html, origin, status=status))

            sitemap_url = _cache_busted(f"{origin}/sitemap.xml", expected_commit, attempt)
            sitemap_status, sitemap_text, _sitemap_headers = fetch_text(sitemap_url, timeout=timeout)
            if sitemap_status != 200:
                raise LiveValidationError(f"sitemap.xml HTTP {sitemap_status}")
            sitemap_urls = validate_sitemap(sitemap_text, origin)

            report.ok = True
            report.routes = route_results
            report.route_count = len(route_results)
            report.sitemap_url_count = len(sitemap_urls)
            report.errors = []
            report.checked_at = datetime.now(timezone.utc).isoformat()
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report.to_json(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return report
        except (LiveValidationError, json.JSONDecodeError, urllib.error.URLError, TimeoutError) as exc:
            last_error = str(exc)
            report.errors = [last_error]
            report.checked_at = datetime.now(timezone.utc).isoformat()
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report.to_json(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if attempt < attempts:
                time.sleep(interval)

    raise LiveValidationError(last_error)


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 İngilizce canlı yayın rotalarını doğrular.")
    parser.add_argument("--origin", default=DEFAULT_ORIGIN)
    parser.add_argument("--repository", default=os.getenv("GITHUB_REPOSITORY", DEFAULT_REPOSITORY))
    parser.add_argument("--expected-commit", default=os.getenv("GITHUB_SHA", "").strip())
    parser.add_argument("--github-token", default=os.getenv("GITHUB_TOKEN", ""))
    parser.add_argument("--attempts", type=int, default=36)
    parser.add_argument("--interval", type=float, default=15.0)
    parser.add_argument("--timeout", type=float, default=25.0)
    parser.add_argument("--report", type=Path, default=Path("/tmp/alo186-live-english-report.json"))
    args = parser.parse_args()

    if not args.expected_commit:
        parser.error("--expected-commit veya GITHUB_SHA zorunludur")
    if args.attempts < 1:
        parser.error("--attempts en az 1 olmalıdır")
    if args.interval < 0:
        parser.error("--interval negatif olamaz")

    try:
        report = run_live_smoke(
            origin=args.origin,
            repository=args.repository,
            expected_commit=args.expected_commit,
            github_token=args.github_token,
            attempts=args.attempts,
            interval=args.interval,
            timeout=args.timeout,
            report_path=args.report,
        )
    except LiveValidationError as exc:
        print(json.dumps({"ok": False, "error": str(exc), "report": str(args.report)}, ensure_ascii=False))
        raise SystemExit(1) from exc

    print(json.dumps(report.to_json(), ensure_ascii=False))


if __name__ == "__main__":
    main()
