from __future__ import annotations

import argparse
import json
import re
import ssl
import time
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, build_opener, HTTPRedirectHandler


CANONICAL_HOST = "https://alo186.com"
LEGACY_HOST = "https://www.alo186.com"
REQUIRED_SECURITY_HEADERS = (
    "strict-transport-security",
    "x-content-type-options",
    "content-security-policy",
    "referrer-policy",
    "permissions-policy",
)
LEGAL_PATHS = {"/", "/elektrik-portali"}
DAMAGE_TERMS = re.compile(r"\b(cihaz|teçhizat|techizat|hasar|zarar)\w*\b", re.IGNORECASE)
APPLICATION_TERMS = re.compile(
    r"\b(başvur|basvur|talep|tazmin|dağıtım şirket|dagitim sirket|edaş|edas)\w*",
    re.IGNORECASE,
)
RESPONSE_TERMS = re.compile(
    r"\b(cevap|yanıt|bildir|haklı bulun|ret|redd|teknik rapor)\w*",
    re.IGNORECASE,
)
STALE_DEADLINE = re.compile(
    r"\b(?:10\s*iş\s*gün|on\s*iş\s*gün)(?:ü|lük|de|den|içinde|icerisinde|içerisinde)?\b",
    re.IGNORECASE,
)
CURRENT_DEADLINE = re.compile(r"\b30\s*(?:takvim\s*)?gün(?:lük|ü|ün|de|den|içinde)?\b", re.IGNORECASE)

ROUTES = [
    ("/", "Elektrik kesintisi", "https://alo186.com/"),
    ("/elektrik-portali", "ALO186", "https://alo186.com/elektrik-portali"),
    ("/edas-bul", "EDAŞ", "https://alo186.com/edas-bul"),
    ("/karar-motoru", "186 mı", "https://alo186.com/karar-motoru"),
    ("/hesaplama/", "Hesaplama", "https://alo186.com/hesaplama/"),
    ("/akilli-urun-secimi", "Ürün", "https://alo186.com/akilli-urun-secimi"),
    ("/isletme-surekliligi", "Sürekliliği", "https://alo186.com/isletme-surekliligi"),
    ("/fatura-analizi", "Faturası", "https://alo186.com/fatura-analizi"),
    ("/hesaplama/yedek-guc", "Yedek Güç", "https://alo186.com/hesaplama/yedek-guc"),
    ("/hesaplama/kesinti-maliyeti", "Kesinti", "https://alo186.com/hesaplama/kesinti-maliyeti"),
]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.canonical: str | None = None
        self.assets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical = values.get("href")
        if tag == "link" and values.get("rel") == "stylesheet" and values.get("href"):
            self.assets.append(values["href"] or "")
        if tag == "script" and values.get("src"):
            self.assets.append(values["src"] or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()


def fetch(url: str, timeout: int = 20) -> tuple[int, str, bytes, dict[str, str], float]:
    request = Request(
        url,
        headers={
            "User-Agent": "ALO186-Production-Smoke/2.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "identity",
        },
    )
    started = time.perf_counter()
    with build_opener(HTTPRedirectHandler()).open(request, timeout=timeout) as response:
        body = response.read()
        duration = time.perf_counter() - started
        headers = {key.lower(): value for key, value in response.headers.items()}
        return response.status, response.geturl(), body, headers, duration


def normalize_url(value: str) -> str:
    return value.rstrip("/")


def stale_deadline_contexts(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text)
    contexts: list[str] = []
    for match in STALE_DEADLINE.finditer(normalized):
        start = max(0, match.start() - 260)
        end = min(len(normalized), match.end() + 260)
        context = normalized[start:end]
        if (
            DAMAGE_TERMS.search(context)
            and APPLICATION_TERMS.search(context)
            and not RESPONSE_TERMS.search(context)
        ):
            contexts.append(context[:520])
    return contexts


def current_deadline_contexts(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text)
    contexts: list[str] = []
    for match in CURRENT_DEADLINE.finditer(normalized):
        start = max(0, match.start() - 260)
        end = min(len(normalized), match.end() + 260)
        context = normalized[start:end]
        if DAMAGE_TERMS.search(context) and APPLICATION_TERMS.search(context):
            contexts.append(context[:520])
    return contexts


def has_independent_platform_notice(text: str) -> bool:
    lowered = text.lower()
    return any(
        phrase in lowered
        for phrase in (
            "başvuru almaz",
            "başvuru veya hasar kaydı almaz",
            "arıza ihbarı almaz",
            "edaş veya kamu kurumu değildir",
            "bağımsız bilgilendirme platformudur",
        )
    )


def run(base_url: str, check_assets: bool = True) -> dict:
    base_url = base_url.rstrip("/")
    results: list[dict] = []
    failures: list[str] = []

    # www URL'nin aynı path ile tek canonical apex hostuna ulaşmasını doğrula.
    www_url = LEGACY_HOST + "/"
    try:
        status, final_url, _body, _headers, duration = fetch(www_url)
        results.append(
            {
                "path": "www-redirect",
                "status": status,
                "requestedUrl": www_url,
                "finalUrl": final_url,
                "durationMs": round(duration * 1000, 1),
            }
        )
        if status != 200 or normalize_url(final_url) != normalize_url(f"{CANONICAL_HOST}/"):
            failures.append(f"www canonical yönlendirme yanlış: {www_url} → {final_url} (HTTP {status})")
    except (HTTPError, URLError, TimeoutError, ssl.SSLError) as exc:
        failures.append(f"www canonical yönlendirme erişim hatası: {exc}")

    for path, marker, canonical in ROUTES:
        url = f"{base_url}{path}"
        try:
            status, final_url, body, headers, duration = fetch(url)
            text = body.decode("utf-8", errors="replace")
            parser = PageParser()
            parser.feed(text)
            row = {
                "path": path,
                "status": status,
                "finalUrl": final_url,
                "durationMs": round(duration * 1000, 1),
                "title": parser.title,
                "canonical": parser.canonical,
                "contentType": headers.get("content-type"),
                "securityHeaders": {name: headers.get(name) for name in REQUIRED_SECURITY_HEADERS},
            }
            if status != 200:
                failures.append(f"{path}: HTTP {status}")
            if marker.lower() not in (parser.title + " " + text[:30000]).lower():
                failures.append(f"{path}: beklenen içerik işareti yok: {marker}")
            if not parser.canonical or normalize_url(parser.canonical) != normalize_url(canonical):
                failures.append(f"{path}: canonical yanlış: {parser.canonical!r}")
            if normalize_url(final_url).startswith(LEGACY_HOST):
                failures.append(f"{path}: canonical olmayan www final URL: {final_url}")
            for header_name in REQUIRED_SECURITY_HEADERS:
                if not headers.get(header_name):
                    failures.append(f"{path}: güvenlik başlığı eksik: {header_name}")

            if path in LEGAL_PATHS:
                stale_contexts = stale_deadline_contexts(text)
                current_contexts = current_deadline_contexts(text)
                for context in stale_contexts:
                    failures.append(f"{path}: cihaz hasarı başvurusunda eski 10 iş günü ifadesi → {context}")
                if not current_contexts:
                    failures.append(f"{path}: cihaz hasarı için görünür 30 gün ifadesi yok")
                if not has_independent_platform_notice(text):
                    failures.append(f"{path}: ALO186 bağımsızlık/başvuru almama açıklaması yok")
                row["deviceDamageDeadline"] = "30 gün" if current_contexts else None
                row["staleDeviceDamageDeadlineContexts"] = stale_contexts

            if check_assets:
                asset_rows = []
                for reference in parser.assets[:16]:
                    asset_url = urljoin(final_url, reference)
                    try:
                        asset_status, asset_final, _asset_body, asset_headers, asset_duration = fetch(asset_url)
                        asset_rows.append(
                            {
                                "url": asset_final,
                                "status": asset_status,
                                "contentType": asset_headers.get("content-type"),
                                "durationMs": round(asset_duration * 1000, 1),
                            }
                        )
                        if asset_status != 200:
                            failures.append(f"{path}: asset HTTP {asset_status}: {reference}")
                        if reference.endswith(".js") and "javascript" not in (asset_headers.get("content-type") or ""):
                            failures.append(f"{path}: JS MIME yanlış: {reference}")
                        if reference.endswith(".css") and "css" not in (asset_headers.get("content-type") or ""):
                            failures.append(f"{path}: CSS MIME yanlış: {reference}")
                    except (HTTPError, URLError, TimeoutError, ssl.SSLError) as exc:
                        asset_rows.append({"url": asset_url, "error": str(exc)})
                        failures.append(f"{path}: asset erişim hatası: {reference} → {exc}")
                row["assets"] = asset_rows
            results.append(row)
        except (HTTPError, URLError, TimeoutError, ssl.SSLError) as exc:
            failures.append(f"{path}: erişim hatası: {exc}")
            results.append({"path": path, "error": str(exc)})

    for root_path in ("/robots.txt", "/sitemap.xml", "/tailwindcss", "/404.html"):
        try:
            status, final_url, body, headers, duration = fetch(f"{base_url}{root_path}")
            content_type = headers.get("content-type") or ""
            results.append(
                {
                    "path": root_path,
                    "status": status,
                    "finalUrl": final_url,
                    "contentType": content_type,
                    "durationMs": round(duration * 1000, 1),
                }
            )
            if status != 200:
                failures.append(f"{root_path}: HTTP {status}")
            if root_path == "/tailwindcss" and "css" not in content_type:
                failures.append(f"{root_path}: CSS MIME yanlış: {content_type!r}")
            if root_path == "/robots.txt" and f"Sitemap: {CANONICAL_HOST}/sitemap.xml" not in body.decode("utf-8", errors="replace"):
                failures.append("/robots.txt: canonical sitemap adresi yanlış")
            if root_path == "/sitemap.xml" and LEGACY_HOST in body.decode("utf-8", errors="replace"):
                failures.append("/sitemap.xml: eski www origin içeriyor")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{root_path}: erişim hatası: {exc}")

    output = {
        "ok": not failures,
        "baseUrl": base_url,
        "canonicalHost": CANONICAL_HOST,
        "requiredSecurityHeaders": list(REQUIRED_SECURITY_HEADERS),
        "deviceDamageDeadline": "30 gün",
        "results": results,
        "failures": failures,
    }
    if failures:
        raise SystemExit(json.dumps(output, ensure_ascii=False, indent=2))
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canlı canonical, güvenlik ve hukukî içerik smoke testi.")
    parser.add_argument("--base-url", default=CANONICAL_HOST)
    parser.add_argument("--skip-assets", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.base_url, check_assets=not args.skip_assets), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
