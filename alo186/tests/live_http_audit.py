from __future__ import annotations

import argparse
import json
import re
import ssl
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit

CANONICAL_ORIGIN = "https://alo186.com"
LEGACY_ORIGIN = "https://www.alo186.com"
USER_AGENT = "ALO186-Technical-Quality-Audit/1.0 (+https://alo186.com/)"
SAMPLE_PATHS = (
    "/",
    "/elektrik-portali",
    "/amazon-elektrik-urunleri",
    "/akilli-urun-secimi",
    "/hesaplama/",
    "/il/adana",
    "/haberler/ups-online-line-interactive-offline-farki",
)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


@dataclass
class Response:
    requested: str
    final: str
    status: int
    headers: dict[str, str]
    body: bytes


def fetch(url: str, *, follow_redirects: bool = True, retries: int = 3, timeout: int = 25) -> Response:
    handlers: list[object] = [urllib.request.HTTPSHandler(context=ssl.create_default_context())]
    if not follow_redirects:
        handlers.insert(0, NoRedirect())
    opener = urllib.request.build_opener(*handlers)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xml,text/plain;q=0.9,*/*;q=0.5"})
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with opener.open(request, timeout=timeout) as response:
                return Response(url, response.geturl(), int(response.status), dict(response.headers.items()), response.read())
        except urllib.error.HTTPError as exc:
            if not follow_redirects and exc.code in {301, 302, 303, 307, 308}:
                return Response(url, url, int(exc.code), dict(exc.headers.items()), exc.read())
            last_error = exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
        if attempt + 1 < retries:
            time.sleep(2 ** attempt)
    raise RuntimeError(f"HTTP isteği başarısız: {url}: {last_error}")


def canonical_from_html(body: bytes) -> list[str]:
    text = body.decode("utf-8", errors="replace")
    links: list[str] = []
    for tag in re.findall(r"<link\b[^>]*>", text, re.I):
        if not re.search(r"\brel=[\"'][^\"']*\bcanonical\b[^\"']*[\"']", tag, re.I):
            continue
        match = re.search(r"\bhref=[\"']([^\"']+)[\"']", tag, re.I)
        if match:
            links.append(match.group(1))
    return links


def audit(base: str) -> dict:
    base = base.rstrip("/")
    failures: list[str] = []
    checks: list[dict] = []

    legacy = fetch(LEGACY_ORIGIN + "/", follow_redirects=False)
    location = legacy.headers.get("Location", "")
    checks.append({"name": "www redirect", "status": legacy.status, "location": location})
    if legacy.status not in {301, 308}:
        failures.append(f"www kök kalıcı yönlendirme değil: HTTP {legacy.status}")
    if not location.startswith(CANONICAL_ORIGIN + "/"):
        failures.append(f"www yönlendirme hedefi apex değil: {location or 'eksik'}")

    for path in SAMPLE_PATHS:
        response = fetch(base + path)
        canonicals = canonical_from_html(response.body) if "text/html" in response.headers.get("Content-Type", "") else []
        checks.append({"name": path, "status": response.status, "final": response.final, "canonicals": canonicals})
        if response.status != 200:
            failures.append(f"Canlı rota HTTP {response.status}: {path}")
        if not response.final.startswith(CANONICAL_ORIGIN + "/"):
            failures.append(f"Canlı rota son URL apex değil: {path} -> {response.final}")
        if path != "/" and not response.final.rstrip("/").endswith(path.rstrip("/")):
            failures.append(f"Beklenmeyen canlı yönlendirme: {path} -> {response.final}")
        if len(canonicals) != 1:
            failures.append(f"Canlı canonical sayısı {len(canonicals)}: {path}")
        elif not canonicals[0].startswith(CANONICAL_ORIGIN + "/"):
            failures.append(f"Canlı canonical apex değil: {path} -> {canonicals[0]}")

    robots_response = fetch(base + "/robots.txt")
    robots = robots_response.body.decode("utf-8", errors="replace")
    checks.append({"name": "robots", "status": robots_response.status, "body": robots})
    if robots_response.status != 200:
        failures.append(f"robots.txt HTTP {robots_response.status}")
    if "User-agent: *" not in robots or "Allow: /" not in robots:
        failures.append("robots.txt genel tarama sözleşmesi eksik")
    if f"Sitemap: {CANONICAL_ORIGIN}/sitemap.xml" not in robots:
        failures.append("robots.txt apex sitemap adresini taşımıyor")
    if "www.alo186.com" in robots:
        failures.append("robots.txt www host taşıyor")

    sitemap_response = fetch(base + "/sitemap.xml")
    sitemap_text = sitemap_response.body.decode("utf-8", errors="replace")
    sitemap_urls: list[str] = []
    try:
        root = ET.fromstring(sitemap_text)
        sitemap_urls = [node.text.strip() for node in root.iter() if node.tag.endswith("loc") and node.text]
    except ET.ParseError as exc:
        failures.append(f"Canlı sitemap XML geçersiz: {exc}")
    checks.append({"name": "sitemap", "status": sitemap_response.status, "urlCount": len(sitemap_urls)})
    if sitemap_response.status != 200:
        failures.append(f"sitemap.xml HTTP {sitemap_response.status}")
    if not sitemap_urls:
        failures.append("Canlı sitemap URL içermiyor")
    if len(sitemap_urls) != len(set(sitemap_urls)):
        failures.append("Canlı sitemap yinelenen URL içeriyor")
    for url in sitemap_urls:
        parsed = urlsplit(url)
        if f"{parsed.scheme}://{parsed.netloc}" != CANONICAL_ORIGIN:
            failures.append(f"Sitemap URL apex dışında: {url}")
            break

    report = {
        "ok": not failures,
        "auditedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "canonicalOrigin": CANONICAL_ORIGIN,
        "samplePathCount": len(SAMPLE_PATHS),
        "sitemapUrlCount": len(sitemap_urls),
        "failureCount": len(failures),
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canlı HTTP, yönlendirme, canonical, robots ve sitemap denetimi")
    parser.add_argument("--base", default=CANONICAL_ORIGIN)
    args = parser.parse_args()
    audit(args.base)


if __name__ == "__main__":
    main()
