from __future__ import annotations

import argparse
import html as html_module
import json
import re
import socket
import ssl
import subprocess
import time
import unicodedata
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


STATIC_PATHS = (
    "/elektrik-portali",
    "/edas-bul",
    "/karar-motoru",
    "/hesaplama/",
    "/akilli-urun-secimi",
    "/isletme-surekliligi",
)
API_HEALTH_PATHS = ("/health/live", "/health/ready")
KG_HEALTH_PATH = "/api/v1/kg/public/health"
REQUIRED_API_HEADERS = (
    "x-request-id",
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
)

# Elektrik Piyasasında Dağıtım ve Perakende Satış Faaliyetlerine İlişkin
# Kalite Yönetmeliği Madde 26/1, cihaz/teçhizat hasarı tazmin talebini zararın
# ortaya çıktığı tarihten itibaren 30 gün içinde dağıtım şirketine bağlar.
# 23.10.2025 değişikliği ikinci fıkrayı değiştirmiş, bu süreyi kaldırmamıştır.
EPDK_DEVICE_DAMAGE_SOURCE = (
    "https://www.resmigazete.gov.tr/eskiler/2020/12/20201229M1-1.htm"
)
EPDK_DEVICE_DAMAGE_AMENDMENT_SOURCE = (
    "https://www.resmigazete.gov.tr/eskiler/2025/10/20251023-5.htm"
)
DEVICE_DAMAGE_STRICT_PATHS = ("/", "/elektrik-portali")
DEVICE_DAMAGE_CANDIDATE_PATHS = (
    "/cihaz-hasari-gorevleri",
    "/elektrik-gorevleri",
    "/sektor-rehberi",
    "/sektor-rehberi/elektrik-kesintisi-tazminati",
    "/sektor-rehberi/elektrikli-cihaz-hasar-basvurusu",
    "/sektor-rehberi/gerilim-dalgalanmasi-teknik-kalite",
)
DAMAGE_TERMS = ("cihaz", "techizat", "hasar", "zarar")
CLAIM_TERMS = ("basvur", "tazmin", "talep", "dagitim", "edas")
RESPONSE_TERMS = ("cevap", "yanit", "bildir", "hakli bulun", "ret", "redd", "teknik rapor")
STATEMENT_BOUNDARIES = "|.!?;"


def resolve(hostname: str) -> dict[str, object]:
    started = time.perf_counter()
    try:
        addresses = sorted(
            {item[4][0] for item in socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)}
        )
        return {
            "ok": bool(addresses),
            "hostname": hostname,
            "addresses": addresses,
            "durationMs": round((time.perf_counter() - started) * 1000, 1),
        }
    except OSError as exc:
        return {
            "ok": False,
            "hostname": hostname,
            "error": str(exc),
            "durationMs": round((time.perf_counter() - started) * 1000, 1),
        }


def fetch(
    url: str,
    timeout: float,
    *,
    api_health: bool = False,
    knowledge_graph_health: bool = False,
) -> dict[str, object]:
    started = time.perf_counter()
    request = Request(
        url,
        headers={"User-Agent": "ALO186-Synthetic/2.3", "Accept": "application/json,text/html,*/*"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(64_000)
            headers = {key.lower(): value for key, value in response.headers.items()}
            result: dict[str, object] = {
                "ok": response.status == 200,
                "status": response.status,
                "finalUrl": response.geturl(),
                "contentType": headers.get("content-type"),
                "durationMs": round((time.perf_counter() - started) * 1000, 1),
                "bytesRead": len(body),
            }
            if api_health or knowledge_graph_health:
                try:
                    payload = json.loads(body.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    payload = None
                missing_headers = [name for name in REQUIRED_API_HEADERS if not headers.get(name)]
                if api_health:
                    status_value = payload.get("status") if isinstance(payload, dict) else None
                    result.update(
                        {
                            "jsonStatus": status_value,
                            "missingSecurityHeaders": missing_headers,
                            "ok": response.status == 200
                            and status_value in {"ok", "ready"}
                            and not missing_headers,
                        }
                    )
                else:
                    score = float(payload.get("score", 0)) if isinstance(payload, dict) else 0.0
                    entities = int(payload.get("entities", 0)) if isinstance(payload, dict) else 0
                    assertions = int(payload.get("assertions", 0)) if isinstance(payload, dict) else 0
                    result.update(
                        {
                            "knowledgeGraphScore": score,
                            "knowledgeGraphEntities": entities,
                            "knowledgeGraphAssertions": assertions,
                            "missingSecurityHeaders": missing_headers,
                            "ok": response.status == 200
                            and score >= 70
                            and entities > 0
                            and assertions > 0
                            and not missing_headers,
                        }
                    )
                    if not result["ok"]:
                        result["error"] = "Knowledge Graph boş, düşük skorlu veya güvenlik başlığı eksik."
            else:
                result["ok"] = response.status == 200 and len(body) >= 200
            return result
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return {
            "ok": False,
            "error": str(exc),
            "durationMs": round((time.perf_counter() - started) * 1000, 1),
        }


def _fold_content(value: str) -> str:
    """HTML, görünür metin ve JSON-LD içeriğini arama için sadeleştirir.

    Etiketler `|` sınırına çevrilir. Böylece birbirinden bağımsız kart veya paragraf
    metinleri geniş bir karakter penceresinde yanlışlıkla aynı hukukî bağlama girmez.
    Script içindeki JSON-LD metni korunur.
    """

    decoded = html_module.unescape(value)
    with_boundaries = re.sub(r"<[^>]+>", " | ", decoded)
    normalized = unicodedata.normalize("NFKD", with_boundaries)
    without_marks = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", without_marks.casefold()).strip()


def _has_terms(value: str, terms: tuple[str, ...]) -> bool:
    return any(term in value for term in terms)


def _left_boundary(value: str, position: int, floor: int) -> int:
    found = max(value.rfind(char, floor, position) for char in STATEMENT_BOUNDARIES)
    return found + 1 if found >= floor else floor


def _right_boundary(value: str, position: int, ceiling: int) -> int:
    candidates = [value.find(char, position, ceiling) for char in STATEMENT_BOUNDARIES]
    found = [item for item in candidates if item >= 0]
    return min(found) if found else ceiling


def _statement_context(value: str, start: int, end: int, radius: int = 420) -> str:
    floor = max(0, start - radius)
    ceiling = min(len(value), end + radius)
    left = _left_boundary(value, start, floor)
    right = _right_boundary(value, end, ceiling)
    return value[left:right].strip(" |")


def _previous_statement(value: str, start: int, radius: int = 260) -> str:
    floor = max(0, start - radius)
    current_left = _left_boundary(value, start, floor)
    if current_left <= floor:
        return ""
    previous_end = max(floor, current_left - 1)
    previous_left = _left_boundary(value, previous_end, floor)
    return value[previous_left:previous_end].strip(" |")


def _claim_context(value: str, start: int, end: int) -> str:
    """Süre ifadesinin ait olduğu cümle/kart bağlamını döndürür."""

    current = _statement_context(value, start, end)
    if _has_terms(current, DAMAGE_TERMS):
        return current
    if _has_terms(current, CLAIM_TERMS):
        previous = _previous_statement(value, start)
        if _has_terms(previous, DAMAGE_TERMS):
            return f"{previous} | {current}".strip()
    return current


def analyze_device_damage_text(raw_html: str) -> dict[str, object]:
    """Madde 26/1 kapsamındaki 30 günlük talep süresini ve eski FAQ metnini tarar.

    Görünür HTML ile JSON-LD birlikte değerlendirilir. Başvurunun reddedilmesi
    hâlindeki 10 iş günlük bildirim süresi, kullanıcının talep süresi değildir ve
    eski başvuru süresi olarak sınıflandırılmaz.
    """

    text = _fold_content(raw_html)
    stale_contexts: list[str] = []
    current_contexts: list[str] = []

    for match in re.finditer(r"\b10\s*is\s*gun(?:u|luk|unde|unden)?\b", text):
        nearby = _claim_context(text, match.start(), match.end())
        if (
            _has_terms(nearby, DAMAGE_TERMS)
            and _has_terms(nearby, CLAIM_TERMS)
            and not _has_terms(nearby, RESPONSE_TERMS)
        ):
            stale_contexts.append(nearby[:720])

    for match in re.finditer(r"\b30\s*(?:takvim\s*)?gun(?:luk|u|un|de|den)?\b", text):
        nearby = _claim_context(text, match.start(), match.end())
        if _has_terms(nearby, DAMAGE_TERMS) and _has_terms(nearby, CLAIM_TERMS):
            current_contexts.append(nearby[:720])

    disclaimer_patterns = (
        r"alo186.{0,320}(?:basvuru|ihbar|ariza|hasar|kayit).{0,180}(?:almaz|toplamaz|degildir|yapmaz)",
        r"(?:basvuru|ihbar|ariza|hasar|kayit).{0,180}(?:almaz|toplamaz|degildir|yapmaz).{0,320}alo186",
    )
    has_disclaimer = any(re.search(pattern, text) for pattern in disclaimer_patterns)

    return {
        "has30DayDamageClaim": bool(current_contexts),
        "has10BusinessDayDamageClaim": bool(stale_contexts),
        "hasAlo186NoApplicationDisclaimer": has_disclaimer,
        "badContexts": stale_contexts[:5],
        "goodContexts": current_contexts[:3],
    }


def device_damage_deadline_check(
    base_url: str,
    path: str,
    timeout: float,
    *,
    strict: bool,
) -> dict[str, object]:
    started = time.perf_counter()
    url = f"{base_url.rstrip('/')}{path}"
    request = Request(
        url,
        headers={
            "User-Agent": "ALO186-Legal-Accuracy-Monitor/2.0",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(512_000)
            content_type = response.headers.get("content-type", "")
            raw = body.decode("utf-8", errors="replace")
            analysis = analyze_device_damage_text(raw)
            ok = (
                response.status == 200
                and "text/html" in content_type.lower()
                and not analysis["has10BusinessDayDamageClaim"]
                and (
                    not strict
                    or (
                        analysis["has30DayDamageClaim"]
                        and analysis["hasAlo186NoApplicationDisclaimer"]
                    )
                )
            )
            result: dict[str, object] = {
                "ok": ok,
                "kind": "legal-content",
                "rule": "device-damage-claim-deadline",
                "path": path,
                "requestedUrl": url,
                "finalUrl": response.geturl(),
                "status": response.status,
                "contentType": content_type,
                "strict": strict,
                "sourceUrl": EPDK_DEVICE_DAMAGE_SOURCE,
                "amendmentUrl": EPDK_DEVICE_DAMAGE_AMENDMENT_SOURCE,
                "durationMs": round((time.perf_counter() - started) * 1000, 1),
                **analysis,
            }
            if not ok:
                reasons: list[str] = []
                if response.status != 200:
                    reasons.append(f"HTTP {response.status}")
                if "text/html" not in content_type.lower():
                    reasons.append("HTML yanıtı değil")
                if analysis["has10BusinessDayDamageClaim"]:
                    reasons.append("cihaz/teçhizat hasarı talebinde eski 10 iş günü ifadesi bulundu")
                if strict and not analysis["has30DayDamageClaim"]:
                    reasons.append("Madde 26/1 kapsamındaki 30 gün ifadesi bulunamadı")
                if strict and not analysis["hasAlo186NoApplicationDisclaimer"]:
                    reasons.append("ALO186'in başvuru/ihbar almadığı açıklanmıyor")
                result["error"] = "; ".join(reasons)
            return result
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return {
            "ok": False,
            "kind": "legal-content",
            "rule": "device-damage-claim-deadline",
            "path": path,
            "requestedUrl": url,
            "strict": strict,
            "sourceUrl": EPDK_DEVICE_DAMAGE_SOURCE,
            "amendmentUrl": EPDK_DEVICE_DAMAGE_AMENDMENT_SOURCE,
            "error": str(exc),
            "durationMs": round((time.perf_counter() - started) * 1000, 1),
        }


def device_damage_deadline_checks(web_base: str, timeout: float) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    seen: set[str] = set()

    # Hukukî açıdan en kritik ana sayfa ve portal hem apex hem www üzerinde ayrı
    # doğrulanır; canonical/host geçişlerinde eski cache'in kalması böyle yakalanır.
    for base in ("https://alo186.com", "https://www.alo186.com"):
        for path in DEVICE_DAMAGE_STRICT_PATHS:
            url = f"{base}{path}"
            if url not in seen:
                checks.append(device_damage_deadline_check(base, path, timeout, strict=True))
                seen.add(url)

    # Diğer aday sayfalar canonical web base üzerinde bağlam içinde taranır. Başvuru
    # reddi sonrasında dağıtım şirketinin 10 iş günlük bildirim süresi yanlış pozitif
    # sayılmaz; kullanıcının talep süresi 30 gün olarak aranır.
    for path in DEVICE_DAMAGE_CANDIDATE_PATHS:
        url = f"{web_base.rstrip('/')}{path}"
        if url not in seen:
            checks.append(device_damage_deadline_check(web_base, path, timeout, strict=False))
            seen.add(url)
    return checks


def tls_expiry(hostname: str, port: int = 443, timeout: float = 10.0) -> dict[str, object]:
    # create_default_context + server_hostname exact ve wildcard SAN eşleşmesini
    # TLS handshake sırasında doğrular; tekrar exact string karşılaştırması yapılmaz.
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as tls_sock:
            certificate = tls_sock.getpeercert()
    expires = datetime.strptime(certificate["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(
        tzinfo=timezone.utc
    )
    remaining = expires - datetime.now(timezone.utc)
    sans = [value for kind, value in certificate.get("subjectAltName", []) if kind == "DNS"]
    return {
        "ok": remaining.days >= 21,
        "hostname": hostname,
        "expiresAt": expires.isoformat(),
        "daysRemaining": remaining.days,
        "hostnameVerifiedByTlsContext": True,
        "subjectAltNames": sans,
        "issuer": dict(item[0] for item in certificate.get("issuer", [])),
    }


def dig_txt(name: str) -> list[str]:
    try:
        process = subprocess.run(
            ["dig", "+short", "TXT", name],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [line.strip().replace('"', "") for line in process.stdout.splitlines() if line.strip()]


def email_dns(domain: str) -> list[dict[str, object]]:
    spf = [value for value in dig_txt(domain) if "v=spf1" in value.lower()]
    dmarc = dig_txt(f"_dmarc.{domain}")
    return [
        {"ok": len(spf) == 1, "kind": "email-dns", "name": "spf", "recordCount": len(spf)},
        {
            "ok": any("V=DMARC1" in value.upper() for value in dmarc),
            "kind": "email-dns",
            "name": "dmarc",
            "recordCount": len(dmarc),
        },
    ]


def hostname(base_url: str) -> str:
    parsed = urlparse(base_url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError(f"HTTPS base URL bekleniyor: {base_url}")
    return parsed.hostname


def run(
    web_base: str,
    api_base: str,
    timeout: float,
    *,
    check_email_dns: bool = False,
    email_domain: str = "alo186.com",
) -> dict[str, object]:
    web_host, api_host = hostname(web_base), hostname(api_base)
    dns_checks = [resolve(web_host), resolve(api_host)]
    checks: list[dict[str, object]] = []
    for path in STATIC_PATHS:
        result = fetch(f"{web_base.rstrip('/')}{path}", timeout)
        result.update({"kind": "web", "path": path})
        checks.append(result)
    for path in API_HEALTH_PATHS:
        result = fetch(f"{api_base.rstrip('/')}{path}", timeout, api_health=True)
        result.update({"kind": "api", "path": path})
        checks.append(result)
    kg_result = fetch(
        f"{api_base.rstrip('/')}{KG_HEALTH_PATH}",
        timeout,
        knowledge_graph_health=True,
    )
    kg_result.update({"kind": "knowledge-graph", "path": KG_HEALTH_PATH})
    checks.append(kg_result)

    legal_content_checks = device_damage_deadline_checks(web_base, timeout)

    tls_checks = []
    for host in {web_host, api_host}:
        try:
            tls_checks.append(tls_expiry(host, timeout=timeout))
        except Exception as exc:  # noqa: BLE001
            tls_checks.append({"ok": False, "hostname": host, "error": str(exc)})

    email_checks = email_dns(email_domain) if check_email_dns else []
    all_checks = [*dns_checks, *checks, *legal_content_checks, *tls_checks, *email_checks]
    failures = [item for item in all_checks if not item.get("ok")]
    return {
        "ok": not failures,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "webBase": web_base,
        "apiBase": api_base,
        "dns": dns_checks,
        "checks": checks,
        "legalContent": legal_content_checks,
        "tls": tls_checks,
        "emailDns": email_checks,
        "failureCount": len(failures),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "ALO186 web/API/Knowledge Graph/DNS/TLS ve cihaz hasarı başvuru süresi "
            "sentetik kontrolü"
        )
    )
    parser.add_argument("--web-base", default="https://www.alo186.com")
    parser.add_argument("--api-base", default="https://api.alo186.com")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--output", default="")
    parser.add_argument("--check-email-dns", action="store_true")
    parser.add_argument("--email-domain", default="alo186.com")
    args = parser.parse_args()
    result = run(
        args.web_base,
        args.api_base,
        args.timeout,
        check_email_dns=args.check_email_dns,
        email_domain=args.email_domain,
    )
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")
    print(payload)
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
