from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS_ROUTE = "/yayin-durumu/"
STATUS_JSON_ROUTE = "/release-status.json"
STATUS_PAGE = Path("yayin-durumu/index.html")
JSONLD_ID = "release-status-jsonld"
CRITICAL_ROUTES = (
    ("/", "Ana sayfa"),
    ("/elektrik-portali", "Elektrik Portalı"),
    ("/edas-bul", "EDAŞ Bulucu"),
    ("/elektrik-durum-merkezi/", "Elektrik Durum Merkezi"),
    ("/haberler/", "Teknik Makaleler"),
    ("/hesaplama/", "Hesaplama Merkezi"),
    (STATUS_ROUTE, "Yayın Durumu"),
)
MONTHS_TR = (
    "",
    "Ocak",
    "Şubat",
    "Mart",
    "Nisan",
    "Mayıs",
    "Haziran",
    "Temmuz",
    "Ağustos",
    "Eylül",
    "Ekim",
    "Kasım",
    "Aralık",
)


def public_url(base_path: str, route: str) -> str:
    prefix = "/" + str(base_path or "").strip("/") if str(base_path or "").strip("/") else ""
    path = "/" + str(route or "").lstrip("/")
    return (prefix + path).replace("//", "/")


def route_target(site: Path, route: str) -> Path:
    clean = "/" + str(route or "").strip().strip("/")
    if clean == "/":
        return site / "index.html"
    candidate = site / clean.lstrip("/")
    if candidate.is_file():
        return candidate
    if (candidate / "index.html").is_file():
        return candidate / "index.html"
    return Path(str(candidate) + ".html")


def replace_element_text(source: str, marker: str, value: str) -> str:
    pattern = re.compile(
        rf'(<(?P<tag>[a-z0-9]+)\b[^>]*\b{re.escape(marker)}\b[^>]*>).*?(</(?P=tag)>)',
        re.IGNORECASE | re.DOTALL,
    )
    escaped = html.escape(str(value))
    source, count = pattern.subn(
        lambda match: match.group(1) + escaped + match.group(3),
        source,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"Yayın durumu alanı bulunamadı: {marker}")
    return source


def set_marked_href(source: str, marker: str, value: str) -> str:
    pattern = re.compile(rf'<a\b(?=[^>]*\b{re.escape(marker)}\b)[^>]*>', re.IGNORECASE)
    match = pattern.search(source)
    if not match:
        raise RuntimeError(f"Yayın durumu bağlantısı bulunamadı: {marker}")
    tag = match.group(0)
    escaped = html.escape(value, quote=True)
    if re.search(r'\shref=["\'][^"\']*["\']', tag, re.IGNORECASE):
        tag = re.sub(r'\shref=["\'][^"\']*["\']', f' href="{escaped}"', tag, count=1, flags=re.IGNORECASE)
    else:
        tag = tag[:-1] + f' href="{escaped}">'
    return source[: match.start()] + tag + source[match.end() :]


def human_datetime(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        return "Yayın sırasında oluşturuldu"
    try:
        parsed = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
    except ValueError:
        return cleaned
    return f"{parsed.day} {MONTHS_TR[parsed.month]} {parsed.year} · {parsed.strftime('%H:%M')} UTC"


def update_manifest(site: Path, base_path: str) -> bool:
    target = site / "manifest.webmanifest"
    if not target.is_file():
        return False
    manifest = json.loads(target.read_text(encoding="utf-8"))
    shortcuts = manifest.setdefault("shortcuts", [])
    url = public_url(base_path, STATUS_ROUTE)
    if any(isinstance(item, dict) and item.get("url") == url for item in shortcuts):
        return False
    shortcuts.append({"name": "Yayın Durumu", "short_name": "Yayın", "url": url})
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def run(
    site: Path,
    base_path: str,
    canonical_release: dict[str, Any],
    repository: str,
    requested_commit: str,
) -> dict[str, Any]:
    page = site / STATUS_PAGE
    if not page.is_file():
        raise FileNotFoundError(f"Yayın durumu sayfası artifactta yok: {page}")

    pages_release_path = site / "pages-release.json"
    pages_release = (
        json.loads(pages_release_path.read_text(encoding="utf-8"))
        if pages_release_path.is_file()
        else {}
    )
    commit = str(pages_release.get("commit") or requested_commit or canonical_release.get("commit") or "unknown")
    generated_at = str(
        pages_release.get("generatedAt")
        or canonical_release.get("generatedAt")
        or datetime.now(timezone.utc).isoformat()
    )
    canonical_host = str(pages_release.get("canonicalHost") or "https://alo186.com").rstrip("/")
    routing_version = int(canonical_release.get("routingVersion", 0))
    route_count = int(canonical_release.get("routeCount", len(canonical_release.get("routes", []))))
    article_count = int(canonical_release.get("articleCount", 0))
    deadline = str(canonical_release.get("deviceDamageDeadline") or "30 gün")
    if deadline != "30 gün":
        raise RuntimeError(f"Yayın durumu için cihaz hasarı süresi yanlış: {deadline!r}")

    route_results = []
    missing_routes: list[str] = []
    for route, label in CRITICAL_ROUTES:
        target = route_target(site, route)
        present = target.is_file()
        if not present:
            missing_routes.append(route)
        route_results.append(
            {
                "path": route.lstrip("/"),
                "label": label,
                "present": present,
                "artifactFile": target.relative_to(site).as_posix() if present else None,
            }
        )
    if missing_routes:
        raise RuntimeError("Yayın durumu kritik rota eksik: " + ", ".join(missing_routes))

    source_commit_url = f"https://github.com/{repository}/commit/{commit}"
    status_json_url = f"{canonical_host}{STATUS_JSON_ROUTE}"
    status_page_url = f"{canonical_host}{STATUS_ROUTE}"
    record: dict[str, Any] = {
        "schemaVersion": 1,
        "status": "ready",
        "scope": "published-artifact",
        "generatedAt": generated_at,
        "commit": commit,
        "sourceCommitUrl": source_commit_url,
        "canonicalHost": canonical_host,
        "statusPageUrl": status_page_url,
        "statusJsonUrl": status_json_url,
        "artifactStatusPath": public_url(base_path, STATUS_JSON_ROUTE),
        "artifactStatusPagePath": public_url(base_path, STATUS_ROUTE),
        "routingVersion": routing_version,
        "routeCount": route_count,
        "articleCount": article_count,
        "deviceDamageDeadline": deadline,
        "deviceDamageRegulationUrl": canonical_release.get("deviceDamageRegulationUrl"),
        "deviceDamageAmendmentUrl": canonical_release.get("deviceDamageAmendmentUrl"),
        "criticalRoutes": route_results,
        "verifiedCriticalRouteCount": len(route_results),
        "allCriticalRoutesPresent": True,
        "editorialTrust": {
            "articleTrustBlock": True,
            "publicationPrinciplesUrl": f"{canonical_host}/yayin-ilkeleri",
            "sourcesUrl": f"{canonical_host}/kaynaklar",
            "correctionsUrl": f"{canonical_host}/iletisim",
        },
        "limitations": [
            "Bu kayıt ALO186 yayın paketinin teknik kimliğini gösterir; resmî başvuru kaydı değildir.",
            "Mevzuat, standart, üretici kılavuzu ve EDAŞ verileri her içerikteki kaynak tarihiyle ayrıca doğrulanmalıdır.",
        ],
    }
    status_path = site / STATUS_JSON_ROUTE.lstrip("/")
    status_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    source = page.read_text(encoding="utf-8")
    source = replace_element_text(source, "data-release-status", "Yayın paketi hazır ve kritik rotalar doğrulandı.")
    source = replace_element_text(source, "data-release-commit", commit[:12])
    source = replace_element_text(source, "data-release-routing", f"v{routing_version}")
    source = replace_element_text(source, "data-release-routes", str(route_count))
    source = replace_element_text(source, "data-release-articles", str(article_count))
    source = replace_element_text(source, "data-release-deadline", deadline)
    source = replace_element_text(source, "data-release-generated", human_datetime(generated_at))
    source = re.sub(
        r'(<time\b[^>]*\bdata-release-generated\b[^>]*?)\sdatetime=["\'][^"\']*["\']',
        rf'\1 datetime="{html.escape(generated_at, quote=True)}"',
        source,
        count=1,
        flags=re.IGNORECASE,
    )
    route_items = "".join(
        f'<li><a href="{html.escape(public_url(base_path, item["path"]), quote=True)}">'
        f'<span aria-hidden="true" class="release-good">✓</span>&nbsp;{html.escape(item["label"])}</a></li>'
        for item in route_results
    )
    source, count = re.subn(
        r'(<ul\b[^>]*\bdata-release-critical-routes\b[^>]*>).*?(</ul>)',
        rf"\1{route_items}\2",
        source,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if count != 1:
        raise RuntimeError("Yayın durumu kritik rota listesi bulunamadı.")
    source = set_marked_href(source, "data-release-json", public_url(base_path, STATUS_JSON_ROUTE))
    source = set_marked_href(source, "data-release-source", source_commit_url)

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "name": "ALO186 Yayın Durumu ve Teknik Doğrulama Kayıtları",
                "url": status_page_url,
                "description": "ALO186 canlı yayın kimliği, routing sürümü, rota bütünlüğü ve teknik yayın sınırları.",
                "inLanguage": "tr-TR",
                "dateModified": generated_at,
                "mainEntity": {"@id": f"{status_page_url}#dataset"},
                "about": [
                    {"@type": "DefinedTerm", "name": "Yayın kimliği"},
                    {"@type": "DefinedTerm", "name": "Routing sürümü"},
                    {"@type": "DefinedTerm", "name": "Canonical rota"},
                    {"@type": "DefinedTerm", "name": "Teknik makale"},
                    {"@type": "DefinedTerm", "name": "Cihaz hasarı başvuru süresi"},
                ],
            },
            {
                "@type": "Dataset",
                "@id": f"{status_page_url}#dataset",
                "name": "ALO186 yayın paketi durumu",
                "description": "ALO186 yayın commitini, routing sürümünü, rota ve makale sayılarını ve kritik rota doğrulamasını içeren makine tarafından okunabilir kayıt.",
                "version": commit,
                "dateModified": generated_at,
                "distribution": {
                    "@type": "DataDownload",
                    "encodingFormat": "application/json",
                    "contentUrl": status_json_url,
                },
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "Yayın kimliği neyi gösterir?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Canlı ALO186 paketinin hangi kaynak commit ve routing sürümünden üretildiğini gösterir. Resmî EDAŞ başvurusu veya mevzuatın değişmeyeceği garantisi değildir.",
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "Bir içerik hatası nasıl bildirilir?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "İletişim ve düzeltme kanalı üzerinden sayfa adresi, hatalı bölüm ve doğrulanabilir kaynak paylaşılabilir. Kişisel veya hassas veri gönderilmemelidir.",
                        },
                    },
                ],
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "ALO186", "item": f"{canonical_host}/"},
                    {"@type": "ListItem", "position": 2, "name": "Yayın durumu", "item": status_page_url},
                ],
            },
        ],
    }
    schema_text = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
    pattern = rf'(<script\s+id=["\']{re.escape(JSONLD_ID)}["\'][^>]*>).*?(</script>)'
    source, count = re.subn(
        pattern,
        rf"\g<1>{schema_text}\g<2>",
        source,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if count != 1:
        raise RuntimeError("Yayın durumu JSON-LD alanı bulunamadı.")
    page.write_text(source, encoding="utf-8")

    manifest_shortcut = update_manifest(site, base_path)
    return {
        "route": public_url(base_path, STATUS_ROUTE),
        "json": public_url(base_path, STATUS_JSON_ROUTE),
        "commit": commit,
        "routingVersion": routing_version,
        "routeCount": route_count,
        "articleCount": article_count,
        "deviceDamageDeadline": deadline,
        "criticalRouteCount": len(route_results),
        "allCriticalRoutesPresent": True,
        "manifestShortcutAdded": manifest_shortcut,
        "personalDataStored": False,
    }
