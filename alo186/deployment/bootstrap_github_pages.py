#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any


DEFAULT_API_BASE = "https://api.github.com"
DEFAULT_API_VERSION = "2022-11-28"
DEFAULT_CUSTOM_DOMAIN = "www.alo186.com"


class PagesBootstrapError(RuntimeError):
    pass


@dataclass(frozen=True)
class BootstrapResult:
    repository: str
    custom_domain: str
    created: bool
    updated: bool
    build_type: str | None
    status: str | None
    html_url: str | None
    https_enforced: bool | None
    protected_domain_state: str | None


class GitHubPagesApi:
    def __init__(self, *, token: str, api_base: str = DEFAULT_API_BASE) -> None:
        if not token.strip():
            raise PagesBootstrapError("ALO186_PAGES_ADMIN_TOKEN zorunludur.")
        self._token = token.strip()
        self._api_base = api_base.rstrip("/")

    def request(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        accepted: tuple[int, ...] = (200,),
    ) -> tuple[int, dict[str, Any] | None]:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            f"{self._api_base}{path}",
            data=body,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
                "User-Agent": "ALO186-Pages-Bootstrap/1.0",
                "X-GitHub-Api-Version": DEFAULT_API_VERSION,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
                parsed = json.loads(raw.decode("utf-8")) if raw else None
                status = response.status
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            parsed = None
            if raw:
                try:
                    parsed = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    parsed = {"message": raw.decode("utf-8", errors="replace")[:1000]}
            status = exc.code
        except urllib.error.URLError as exc:
            raise PagesBootstrapError(f"GitHub Pages API erişilemedi: {exc.reason}") from exc

        if status not in accepted:
            message = parsed.get("message") if isinstance(parsed, dict) else None
            detail = f": {message}" if message else ""
            raise PagesBootstrapError(f"GitHub Pages API {method} {path} HTTP {status}{detail}")
        return status, parsed


def _normalise_domain(value: str | None) -> str:
    return (value or "").strip().lower().rstrip(".")


def ensure_pages(
    *,
    repository: str,
    custom_domain: str,
    token: str,
    api_base: str = DEFAULT_API_BASE,
) -> BootstrapResult:
    if repository.count("/") != 1 or any(part.strip() != part or not part for part in repository.split("/")):
        raise PagesBootstrapError("Repository owner/name biçiminde olmalıdır.")
    domain = _normalise_domain(custom_domain)
    if not domain or "/" in domain or ":" in domain:
        raise PagesBootstrapError("Custom domain yalnız hostname olmalıdır.")

    api = GitHubPagesApi(token=token, api_base=api_base)
    endpoint = f"/repos/{repository}/pages"
    status, _site = api.request("GET", endpoint, accepted=(200, 404))
    created = False
    if status == 404:
        create_status, _ = api.request(
            "POST",
            endpoint,
            payload={"build_type": "workflow"},
            accepted=(201, 409),
        )
        created = create_status == 201

    api.request(
        "PUT",
        endpoint,
        payload={"build_type": "workflow", "cname": domain},
        accepted=(204,),
    )
    _, current = api.request("GET", endpoint, accepted=(200,))
    if not isinstance(current, dict):
        raise PagesBootstrapError("GitHub Pages doğrulama cevabı beklenen JSON nesnesi değil.")

    build_type = current.get("build_type")
    current_domain = _normalise_domain(current.get("cname"))
    if build_type != "workflow":
        raise PagesBootstrapError(f"Pages build_type doğrulanamadı: {build_type!r}")
    if current_domain != domain:
        raise PagesBootstrapError(
            f"Pages custom domain doğrulanamadı: beklenen={domain!r} görülen={current_domain!r}"
        )

    certificate = current.get("https_certificate")
    protected_domain_state = current.get("protected_domain_state")
    if protected_domain_state is None and isinstance(certificate, dict):
        protected_domain_state = certificate.get("state")

    return BootstrapResult(
        repository=repository,
        custom_domain=domain,
        created=created,
        updated=True,
        build_type=build_type,
        status=current.get("status"),
        html_url=current.get("html_url"),
        https_enforced=current.get("https_enforced"),
        protected_domain_state=protected_domain_state,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="GitHub Pages'i workflow modunda etkinleştirir ve ALO186 custom domainini idempotent ayarlar."
    )
    parser.add_argument("--repository", default=os.getenv("GITHUB_REPOSITORY", ""))
    parser.add_argument("--custom-domain", default=DEFAULT_CUSTOM_DOMAIN)
    parser.add_argument("--api-base", default=os.getenv("GITHUB_API_URL", DEFAULT_API_BASE))
    args = parser.parse_args(argv)

    token = os.getenv("ALO186_PAGES_ADMIN_TOKEN", "")
    try:
        result = ensure_pages(
            repository=args.repository,
            custom_domain=args.custom_domain,
            token=token,
            api_base=args.api_base,
        )
    except PagesBootstrapError as exc:
        print(f"Pages bootstrap başarısız: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
