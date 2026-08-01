from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

PAGES_MODE = "github-pages"
SITES_MODE = "chatgpt-sites"
UNKNOWN_MODE = "unknown"

SITES_SIGNATURES = (
    "/_vinext/",
    "/build-assets/",
    "next-router-state-tree",
    "vite-rsc",
    "vinext",
)
STATIC_SNAPSHOT_HEADER = "x-alo186-render-mode: static-snapshot"
STATIC_SNAPSHOT_BODY_SIGNATURES = (
    "data-home-critical-styles",
    "/brand/alo186-logo-",
    'fetchpriority="high"',
)

# ChatGPT Sites canlı navigasyonunda gerçekten yayımlanan, kullanıcıya dönük
# görev rotaları. GitHub Pages artifactına özgü /durum ve /arama köprüleri burada
# kullanılmaz; iki hosting modu aynı URL yüzeyini sunmak zorunda değildir.
CRITICAL_SITES_ROUTES = (
    "/",
    "/karar-motoru",
    "/elektrik-kesintisi",
    "/dagitim-sirketleri",
    "/amazon-elektrik-urunleri",
    "/sektor-rehberi/planli-elektrik-kesintisi-sorgulama",
)


@dataclass(frozen=True)
class CurlResult:
    http_code: int
    content_type: str
    effective_url: str
    redirect_count: int
    body_path: Path
    headers_path: Path
    meta_path: Path


def normalize_origin(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError(f"Canlı origin yalnız HTTPS ve geçerli host kullanmalı: {value!r}")
    return f"https://{parsed.hostname}"


def read_header_value(headers: str, name: str) -> str:
    matches = re.findall(
        rf"^{re.escape(name)}:\s*(.*?)\s*$",
        headers,
        flags=re.I | re.M,
    )
    return matches[-1].strip() if matches else ""


def detect_sites_render_signature(body: str, headers: str = "") -> str:
    folded_body = body.casefold()
    folded_headers = headers.casefold()
    combined = f"{folded_headers}\n{folded_body}"
    if any(token in combined for token in SITES_SIGNATURES):
        return "vinext/cloudflare"
    if (
        STATIC_SNAPSHOT_HEADER in folded_headers
        and all(token in folded_body for token in STATIC_SNAPSHOT_BODY_SIGNATURES)
    ):
        return "static-snapshot/cloudflare"
    return ""


def classify_release_response(http_code: int, content_type: str, body: str, headers: str = "") -> str:
    media_type = content_type.split(";", 1)[0].strip().casefold()
    if http_code == 200 and media_type in {"application/json", "application/manifest+json"}:
        return PAGES_MODE
    if http_code in {200, 404} and media_type == "text/html" and detect_sites_render_signature(body, headers):
        return SITES_MODE
    return UNKNOWN_MODE


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_curl(
    *,
    url: str,
    name: str,
    diagnostics: Path,
    follow: bool = True,
    head: bool = False,
    accept: str | None = None,
    fail_http: bool = False,
) -> CurlResult:
    body_path = diagnostics / f"{name}.body"
    headers_path = diagnostics / f"{name}.headers"
    meta_path = diagnostics / f"{name}.meta"
    command = [
        "curl",
        "--silent",
        "--show-error",
        "--connect-timeout",
        "10",
        "--max-time",
        "30",
        "--retry",
        "2",
        "--retry-all-errors",
        "--retry-delay",
        "1",
        "-H",
        "Cache-Control: no-cache, no-store, max-age=0",
        "-H",
        "Pragma: no-cache",
        "-D",
        str(headers_path),
        "--write-out",
        "%{http_code}\t%{content_type}\t%{url_effective}\t%{num_redirects}\n",
    ]
    if follow:
        command.append("--location")
    if head:
        command.extend(["--head", "--output", "/dev/null"])
    else:
        command.extend(["--output", str(body_path)])
    if accept:
        command.extend(["-H", f"Accept: {accept}"])
    if fail_http:
        command.append("--fail-with-body")
    command.append(url)
    completed = subprocess.run(command, check=False, text=True, capture_output=True)
    meta_path.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0 and fail_http:
        raise RuntimeError(f"curl başarısız ({name}): {completed.stderr.strip()}")
    parts = completed.stdout.strip().split("\t")
    if len(parts) != 4:
        raise RuntimeError(f"curl metadata ayrıştırılamadı ({name}): {completed.stdout!r} {completed.stderr!r}")
    return CurlResult(
        http_code=int(parts[0]),
        content_type=parts[1],
        effective_url=parts[2],
        redirect_count=int(parts[3]),
        body_path=body_path,
        headers_path=headers_path,
        meta_path=meta_path,
    )


def verify_alias(alias_origin: str, live_origin: str, diagnostics: Path) -> dict:
    result = run_curl(
        url=f"{alias_origin}/pages-release.json?alias_check={int(time.time())}",
        name="alias",
        diagnostics=diagnostics,
        follow=False,
        head=True,
    )
    meta = result.meta_path.read_text(encoding="utf-8").strip().split("\t")
    headers = result.headers_path.read_text(encoding="utf-8", errors="ignore")
    location_match = re.search(r"^location:\s*(\S+)", headers, re.I | re.M)
    redirect_url = location_match.group(1) if location_match else ""
    target = urlparse(redirect_url)
    live = urlparse(live_origin)
    if result.http_code not in {301, 302, 307, 308}:
        raise AssertionError(("www_alias_status", result.http_code, meta))
    if target.scheme != "https" or target.hostname != live.hostname:
        raise AssertionError(("www_alias_target", redirect_url, live_origin))
    if target.path != "/pages-release.json":
        raise AssertionError(("www_alias_path", target.path))
    return {
        "status": result.http_code,
        "redirect": redirect_url,
        "effectiveUrl": result.effective_url,
    }


def compare_commits(repository: str, token: str, base: str, head: str, diagnostics: Path) -> str:
    if base == head:
        return "identical"
    if not repository or not token:
        raise RuntimeError("Commit soy doğrulaması için repository ve GitHub tokenı gerekli")
    result = run_curl(
        url=f"https://api.github.com/repos/{repository}/compare/{base}...{head}",
        name="commit-compare",
        diagnostics=diagnostics,
        accept="application/vnd.github+json",
        fail_http=True,
    )
    payload = json.loads(result.body_path.read_text(encoding="utf-8"))
    status = str(payload.get("status") or "")
    if status not in {"ahead", "identical"}:
        raise AssertionError(("served_commit_does_not_contain_expected", base, head, status))
    return status


def verify_pages_mode(
    release_result: CurlResult,
    expected_commit: str,
    live_origin: str,
    repository: str,
    token: str,
    diagnostics: Path,
) -> dict:
    payload = json.loads(release_result.body_path.read_text(encoding="utf-8"))
    served_commit = str(payload.get("commit") or "")
    if not re.fullmatch(r"[0-9a-f]{40}", served_commit):
        raise AssertionError(("invalid_served_commit", served_commit))
    if payload.get("hostingMode") != "github-pages":
        raise AssertionError(("hosting_mode", payload.get("hostingMode")))
    if payload.get("canonicalHost") != live_origin:
        raise AssertionError(("canonical_host", payload.get("canonicalHost"), live_origin))
    compare_status = compare_commits(repository, token, expected_commit, served_commit, diagnostics)
    return {
        "mode": PAGES_MODE,
        "servedCommit": served_commit,
        "containsExpectedCommit": True,
        "compareStatus": compare_status,
        "exactCommitReceiptAvailable": True,
        "releaseSha256": sha256(release_result.body_path),
        "releaseRouteCount": payload.get("routeCount"),
    }


def assert_html_result(result: CurlResult, expected_host: str, route: str) -> str:
    media_type = result.content_type.split(";", 1)[0].strip().casefold()
    parsed = urlparse(result.effective_url)
    if result.http_code != 200:
        raise AssertionError(("route_status", route, result.http_code, result.effective_url))
    if media_type != "text/html":
        raise AssertionError(("route_content_type", route, result.content_type))
    if parsed.hostname != expected_host:
        raise AssertionError(("route_host", route, result.effective_url))
    body = result.body_path.read_text(encoding="utf-8", errors="ignore")
    if len(body) < 1000:
        raise AssertionError(("route_body_too_small", route, len(body)))
    return body


def validate_affiliate_links(html: str) -> int:
    anchors = re.findall(r"<a\b([^>]*)>", html, re.I | re.S)
    count = 0
    for raw in anchors:
        href_match = re.search(r"href=[\"']([^\"']+)[\"']", raw, re.I)
        if not href_match:
            continue
        host = (urlparse(href_match.group(1)).hostname or "").casefold().removeprefix("www.")
        if host not in {"amazon.com.tr", "amzn.to"}:
            continue
        count += 1
        rel_match = re.search(r"rel=[\"']([^\"']+)[\"']", raw, re.I)
        rel = set((rel_match.group(1) if rel_match else "").casefold().split())
        missing = {"sponsored", "nofollow", "noopener"} - rel
        if missing:
            raise AssertionError(("unsafe_affiliate_link", sorted(missing), href_match.group(1)))
    return count


def verify_sites_mode(live_origin: str, diagnostics: Path) -> dict:
    host = urlparse(live_origin).hostname or ""
    route_results: list[dict] = []
    homepage = ""
    homepage_headers = ""
    commerce = ""
    for index, route in enumerate(CRITICAL_SITES_ROUTES):
        result = run_curl(
            url=f"{live_origin}{route}?live_check={int(time.time())}-{index}",
            name=f"route-{index}",
            diagnostics=diagnostics,
            follow=True,
            accept="text/html",
            fail_http=True,
        )
        body = assert_html_result(result, host, route)
        headers = result.headers_path.read_text(encoding="utf-8", errors="ignore")
        route_results.append({
            "route": route,
            "status": result.http_code,
            "contentType": result.content_type,
            "effectiveUrl": result.effective_url,
            "sha256": sha256(result.body_path),
            "bytes": result.body_path.stat().st_size,
            "renderMode": read_header_value(headers, "x-alo186-render-mode") or None,
        })
        if route == "/":
            homepage = body
            homepage_headers = headers
        if route == "/amazon-elektrik-urunleri":
            commerce = body

    folded_home = homepage.casefold()
    if "alo186" not in folded_home or "bağımsız" not in folded_home:
        raise AssertionError("Canlı ana sayfa ALO186 bağımsızlık kimliğini taşımıyor")
    platform_signature = detect_sites_render_signature(homepage, homepage_headers)
    if not platform_signature:
        raise AssertionError(
            "Canlı ana sayfa doğrulanmış Vinext veya ALO186 static-snapshot imzasını taşımıyor"
        )
    folded_commerce = commerce.casefold()
    if "satış ortaklığı" not in folded_commerce and "affiliate" not in folded_commerce:
        raise AssertionError("Canlı ticari merkez satış ortaklığı açıklaması taşımıyor")
    affiliate_count = validate_affiliate_links(commerce)

    auxiliary: list[dict] = []
    for name, route, accepted in (
        ("robots", "/robots.txt", {"text/plain"}),
        ("sitemap", "/sitemap.xml", {"application/xml", "text/xml"}),
    ):
        result = run_curl(
            url=f"{live_origin}{route}?live_check={int(time.time())}",
            name=name,
            diagnostics=diagnostics,
            follow=True,
            fail_http=True,
        )
        media_type = result.content_type.split(";", 1)[0].strip().casefold()
        if result.http_code != 200 or media_type not in accepted:
            raise AssertionError((name, result.http_code, result.content_type, result.effective_url))
        body = result.body_path.read_text(encoding="utf-8", errors="ignore")
        if name == "robots" and "sitemap" not in body.casefold():
            raise AssertionError("robots.txt sitemap bildirimi taşımıyor")
        if name == "sitemap" and live_origin not in body:
            raise AssertionError("sitemap.xml apex origin taşımıyor")
        auxiliary.append({
            "name": name,
            "status": result.http_code,
            "contentType": result.content_type,
            "sha256": sha256(result.body_path),
            "bytes": result.body_path.stat().st_size,
        })

    fingerprint_source = "\n".join(item["sha256"] for item in route_results + auxiliary)
    fingerprint = hashlib.sha256(fingerprint_source.encode("ascii")).hexdigest()
    return {
        "mode": SITES_MODE,
        "servedCommit": None,
        "containsExpectedCommit": None,
        "compareStatus": "unavailable-on-chatgpt-sites",
        "exactCommitReceiptAvailable": False,
        "liveContentContractVerified": True,
        "liveContentFingerprint": fingerprint,
        "criticalRoutes": route_results,
        "auxiliaryFiles": auxiliary,
        "visibleAffiliateLinkCount": affiliate_count,
        "platformSignature": platform_signature,
    }


def verify(
    *,
    origin: str,
    alias_origin: str,
    expected_commit: str,
    repository: str,
    token: str,
    diagnostics: Path,
    attempts: int,
    sleep_seconds: int,
) -> dict:
    live_origin = normalize_origin(origin)
    live_alias = normalize_origin(alias_origin)
    diagnostics.mkdir(parents=True, exist_ok=True)
    alias = verify_alias(live_alias, live_origin, diagnostics)

    final_release: CurlResult | None = None
    mode = UNKNOWN_MODE
    mode_details: dict | None = None
    for attempt in range(1, attempts + 1):
        result = run_curl(
            url=f"{live_origin}/pages-release.json?deploy={expected_commit}-{attempt}-{int(time.time())}",
            name="release",
            diagnostics=diagnostics,
            follow=True,
            accept="application/json",
            fail_http=False,
        )
        body = result.body_path.read_text(encoding="utf-8", errors="ignore") if result.body_path.exists() else ""
        headers = result.headers_path.read_text(encoding="utf-8", errors="ignore") if result.headers_path.exists() else ""
        mode = classify_release_response(result.http_code, result.content_type, body, headers)
        final_release = result
        if mode == SITES_MODE:
            mode_details = verify_sites_mode(live_origin, diagnostics)
            break
        if mode == PAGES_MODE:
            try:
                mode_details = verify_pages_mode(
                    result,
                    expected_commit,
                    live_origin,
                    repository,
                    token,
                    diagnostics,
                )
                break
            except (AssertionError, RuntimeError, json.JSONDecodeError):
                if attempt == attempts:
                    raise
        if attempt < attempts:
            time.sleep(sleep_seconds)

    if mode_details is None or final_release is None:
        raise RuntimeError(
            f"Canlı origin modu doğrulanamadı: status={getattr(final_release, 'http_code', None)} "
            f"content_type={getattr(final_release, 'content_type', None)!r} mode={mode}"
        )

    receipt = {
        "ok": True,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "expectedCommit": expected_commit,
        "canonicalOrigin": live_origin,
        "wwwAlias": alias,
        "releaseProbe": {
            "status": final_release.http_code,
            "contentType": final_release.content_type,
            "effectiveUrl": final_release.effective_url,
            "redirectCount": final_release.redirect_count,
            "sha256": sha256(final_release.body_path) if final_release.body_path.exists() else None,
        },
        **mode_details,
    }
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canlı originini GitHub Pages veya ChatGPT Sites modunda doğrular.")
    parser.add_argument("--origin", default="https://alo186.com")
    parser.add_argument("--alias-origin", default="https://www.alo186.com")
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN", ""))
    parser.add_argument("--diagnostics", type=Path, default=Path("/tmp/alo186-live-origin"))
    parser.add_argument("--receipt", type=Path, default=Path("/tmp/alo186-live-origin-receipt.json"))
    parser.add_argument("--attempts", type=int, default=24)
    parser.add_argument("--sleep-seconds", type=int, default=10)
    args = parser.parse_args()
    receipt = verify(
        origin=args.origin,
        alias_origin=args.alias_origin,
        expected_commit=args.expected_commit,
        repository=args.repository,
        token=args.github_token,
        diagnostics=args.diagnostics,
        attempts=max(1, args.attempts),
        sleep_seconds=max(0, args.sleep_seconds),
    )
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
