from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_ORIGIN = "https://alo186.com"
USER_AGENT = "ALO186-Live-Release-Smoke/1.0"


def normalize_origin(value: str) -> str:
    parsed = urllib.parse.urlsplit(str(value or DEFAULT_ORIGIN).strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Geçersiz origin: {value!r}")
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))


def append_cache_buster(url: str, token: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query.append(("_alo186_smoke", token))
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(query), parsed.fragment))


def fetch_bytes(url: str, token: str, timeout: int = 20) -> tuple[int, dict[str, str], bytes, str]:
    request = urllib.request.Request(
        append_cache_buster(url, token),
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json,text/html;q=0.9,*/*;q=0.1",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return (
            int(response.status),
            {key.lower(): value for key, value in response.headers.items()},
            response.read(),
            response.geturl(),
        )


def fetch_json(url: str, token: str) -> dict[str, Any]:
    status, headers, payload, final_url = fetch_bytes(url, token)
    if status != 200:
        raise RuntimeError(f"JSON endpoint HTTP {status}: {final_url}")
    content_type = headers.get("content-type", "")
    if "json" not in content_type and not payload.lstrip().startswith(b"{"):
        raise RuntimeError(f"JSON endpoint beklenmeyen içerik türü döndürdü: {content_type!r}")
    data = json.loads(payload.decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Yayın durumu JSON kökü nesne değil.")
    return data


def github_compare(repository: str, base_sha: str, head_sha: str, token: str | None) -> str | None:
    if not repository or not token:
        return None
    url = f"https://api.github.com/repos/{repository}/compare/{base_sha}...{head_sha}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None
    status = payload.get("status")
    return str(status) if status else None


def commit_is_expected_or_newer(
    expected: str,
    live: str,
    repository: str,
    token: str | None,
) -> tuple[bool, str]:
    expected = str(expected or "").strip()
    live = str(live or "").strip()
    if not expected:
        return True, "expected-commit-not-required"
    if not live or live == "unknown":
        return False, "live-commit-missing"
    if live == expected or live.startswith(expected) or expected.startswith(live):
        return True, "exact"
    comparison = github_compare(repository, expected, live, token)
    if comparison in {"ahead", "identical"}:
        return True, f"github-compare-{comparison}"
    return False, f"github-compare-{comparison or 'unavailable'}"


def join_origin(origin: str, path: str) -> str:
    parsed = urllib.parse.urlsplit(origin)
    base_path = parsed.path.rstrip("/")
    route = "/" + str(path or "/").lstrip("/")
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, base_path + route, "", ""))


def validate_route(origin: str, route: dict[str, Any], token: str) -> dict[str, Any]:
    path = str(route.get("path") or "/")
    url = join_origin(origin, path)
    status, headers, payload, final_url = fetch_bytes(url, token)
    text = payload.decode("utf-8", errors="replace")
    content_type = headers.get("content-type", "")
    html_ok = "html" in content_type.lower() or "<html" in text[:2000].lower()
    h1_ok = bool(re.search(r"<h1\b", text, re.IGNORECASE))
    return {
        "path": path,
        "label": route.get("label"),
        "url": url,
        "finalUrl": final_url,
        "status": status,
        "html": html_ok,
        "h1": h1_ok,
        "ok": status == 200 and html_ok and h1_ok,
    }


def validate_once(origin: str, expected_commit: str, repository: str, token: str | None, attempt: int) -> dict[str, Any]:
    cache_token = f"{int(time.time())}-{attempt}"
    status_url = join_origin(origin, "/release-status.json")
    record = fetch_json(status_url, cache_token)
    commit_ok, commit_mode = commit_is_expected_or_newer(
        expected_commit,
        str(record.get("commit") or ""),
        repository,
        token,
    )
    critical_routes = record.get("criticalRoutes")
    if not isinstance(critical_routes, list) or not critical_routes:
        raise RuntimeError("Yayın durumu kritik rota listesi taşımıyor.")
    routes = [validate_route(origin, item, cache_token) for item in critical_routes if isinstance(item, dict)]
    status_page_url = join_origin(origin, "/yayin-durumu/")
    _, _, status_html_bytes, status_final_url = fetch_bytes(status_page_url, cache_token)
    status_html = status_html_bytes.decode("utf-8", errors="replace")
    page_commit_visible = str(record.get("commit") or "")[:12] in status_html
    result = {
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "attempt": attempt,
        "origin": origin,
        "expectedCommit": expected_commit,
        "liveCommit": record.get("commit"),
        "commitAccepted": commit_ok,
        "commitAcceptanceMode": commit_mode,
        "status": record.get("status"),
        "canonicalHost": record.get("canonicalHost"),
        "routingVersion": record.get("routingVersion"),
        "routeCount": record.get("routeCount"),
        "articleCount": record.get("articleCount"),
        "deviceDamageDeadline": record.get("deviceDamageDeadline"),
        "allCriticalRoutesPresentInArtifact": record.get("allCriticalRoutesPresent"),
        "criticalRoutes": routes,
        "statusPageFinalUrl": status_final_url,
        "statusPageCommitVisible": page_commit_visible,
    }
    result["ok"] = bool(
        record.get("status") == "ready"
        and record.get("canonicalHost") == "https://alo186.com"
        and record.get("deviceDamageDeadline") == "30 gün"
        and record.get("allCriticalRoutesPresent") is True
        and commit_ok
        and page_commit_visible
        and routes
        and all(item["ok"] for item in routes)
    )
    return result


def self_test() -> None:
    assert normalize_origin("https://alo186.com/") == "https://alo186.com"
    assert join_origin("https://alo186.com", "/haberler/") == "https://alo186.com/haberler/"
    assert join_origin("https://example.test/chatgpt", "/haberler/") == "https://example.test/chatgpt/haberler/"
    assert commit_is_expected_or_newer("abc123", "abc123", "", None) == (True, "exact")
    assert append_cache_buster("https://example.test/a?x=1", "t").count("?") == 1
    print(json.dumps({"ok": True, "selfTest": True}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canlı yayın kimliği ve kritik rota smoke kontrolü.")
    parser.add_argument("--origin", default=DEFAULT_ORIGIN)
    parser.add_argument("--expected-commit", default="")
    parser.add_argument("--repository", default=os.getenv("GITHUB_REPOSITORY", ""))
    parser.add_argument("--attempts", type=int, default=36)
    parser.add_argument("--interval", type=int, default=10)
    parser.add_argument("--report", type=Path, default=Path("alo186-live-release-smoke.json"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return

    origin = normalize_origin(args.origin)
    github_token = os.getenv("GITHUB_TOKEN")
    attempts: list[dict[str, Any]] = []
    last_error = ""
    for attempt in range(1, max(1, args.attempts) + 1):
        try:
            result = validate_once(origin, args.expected_commit, args.repository, github_token, attempt)
            attempts.append(result)
            args.report.write_text(
                json.dumps({"ok": result["ok"], "attempts": attempts}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            if result["ok"]:
                print(json.dumps(result, ensure_ascii=False))
                return
            last_error = "Canlı sözleşme henüz tamamlanmadı."
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            attempts.append(
                {
                    "checkedAt": datetime.now(timezone.utc).isoformat(),
                    "attempt": attempt,
                    "ok": False,
                    "error": last_error,
                }
            )
            args.report.write_text(
                json.dumps({"ok": False, "attempts": attempts}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        if attempt < args.attempts:
            time.sleep(max(0, args.interval))

    print(f"ALO186 canlı yayın smoke başarısız: {last_error}", file=sys.stderr)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
