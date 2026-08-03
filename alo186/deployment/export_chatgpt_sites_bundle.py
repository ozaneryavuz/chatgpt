from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_ROOT = REPO_ROOT / "alo186"
DEPLOYMENT = SITE_ROOT / "deployment"
POLICY_PATH = DEPLOYMENT / "chatgpt-sites-export-policy.json"
MANIFEST_PATH = DEPLOYMENT / "routing-manifest.json"
OVERLAY_DIR = DEPLOYMENT / "routing-overlays"
CONSOLIDATIONS_PATH = DEPLOYMENT / "content-consolidations.json"

TEXT_ASSET_SUFFIXES = {".css", ".js", ".json", ".webmanifest", ".xml", ".txt"}
BINARY_ASSET_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".ico", ".avif", ".gif"}
ASSET_SUFFIXES = TEXT_ASSET_SUFFIXES | BINARY_ASSET_SUFFIXES
INTERACTIVE_TYPES = {"tool", "calculator", "business-tool", "commerce-guide"}
EXCLUDED_PARTS = {
    ".git",
    ".github",
    "deployment",
    "tests",
    "test",
    "audits",
    "reports",
    "artifacts",
    "node_modules",
    "__pycache__",
}


class MainTextExtractor(HTMLParser):
    BLOCK_TAGS = {
        "article",
        "aside",
        "blockquote",
        "br",
        "div",
        "dl",
        "dt",
        "dd",
        "figcaption",
        "figure",
        "footer",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "section",
        "summary",
        "table",
        "tbody",
        "td",
        "th",
        "thead",
        "tr",
        "ul",
    }
    SKIP_TAGS = {"script", "style", "svg", "noscript", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.main_seen = False
        self.skip_depth = 0
        self.parts: list[str] = []
        self.current_href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        if tag == "main":
            self.main_seen = True
            self.in_main = True
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag == "a":
            self.current_href = dict(attrs).get("href")
        if tag in self.BLOCK_TAGS and (self.in_main or not self.main_seen):
            self.parts.append("\n")
        if tag == "li" and (self.in_main or not self.main_seen):
            self.parts.append("- ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag in self.SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        if tag == "a":
            if self.current_href and not self.current_href.startswith("#"):
                self.parts.append(f" ({self.current_href})")
            self.current_href = None
        if tag in self.BLOCK_TAGS and (self.in_main or not self.main_seen):
            self.parts.append("\n")
        if tag == "main":
            self.in_main = False

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.in_main or not self.main_seen:
            value = re.sub(r"\s+", " ", data).strip()
            if value:
                self.parts.append(value + " ")

    def text(self) -> str:
        value = "".join(self.parts)
        value = re.sub(r"[ \t]+\n", "\n", value)
        value = re.sub(r"\n[ \t]+", "\n", value)
        value = re.sub(r"\n{3,}", "\n\n", value)
        value = re.sub(r" {2,}", " ", value)
        return value.strip()


def read_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_route_record(raw: dict[str, Any], source_label: str) -> dict[str, str]:
    if {"source", "canonicalPath", "type"}.issubset(raw):
        source = str(raw["source"]).strip()
        canonical = str(raw["canonicalPath"]).strip()
        route_type = str(raw["type"]).strip() or "page"
    elif {"path", "file", "intent"}.issubset(raw):
        source = "alo186/" + str(raw["file"]).strip().lstrip("/")
        canonical = str(raw["path"]).strip()
        route_type = "article" if canonical.startswith("/haberler/") else "page"
    else:
        raise ValueError(f"Desteklenmeyen routing kaydı ({source_label}): {raw!r}")
    if not source.startswith("alo186/") or not source.endswith("index.html"):
        raise ValueError(f"Geçersiz routing source ({source_label}): {source}")
    if not canonical.startswith("/") or "//" in canonical:
        raise ValueError(f"Geçersiz canonical yol ({source_label}): {canonical}")
    return {"source": source, "canonicalPath": canonical, "type": route_type}


def load_effective_routes() -> list[dict[str, str]]:
    base = read_json(MANIFEST_PATH, {})
    if not isinstance(base, dict) or not isinstance(base.get("routes"), list):
        raise ValueError("routing-manifest.json geçersiz")
    by_path: dict[str, dict[str, str]] = {}
    for raw in base["routes"]:
        route = normalize_route_record(raw, "routing-manifest.json")
        by_path[route["canonicalPath"]] = route
    if OVERLAY_DIR.is_dir():
        for overlay_path in sorted(OVERLAY_DIR.glob("*.json")):
            overlay = read_json(overlay_path, {})
            if not isinstance(overlay, dict):
                continue
            for raw in overlay.get("routes", []):
                route = normalize_route_record(raw, overlay_path.name)
                by_path[route["canonicalPath"]] = route
    return sorted(by_path.values(), key=lambda item: item["canonicalPath"])


def load_aliases() -> tuple[set[str], list[dict[str, str]]]:
    payload = read_json(CONSOLIDATIONS_PATH, {})
    items = payload.get("consolidations", []) if isinstance(payload, dict) else []
    aliases: set[str] = set()
    redirects: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        alias = str(item.get("aliasPath") or "").strip()
        target = str(item.get("canonicalPath") or "").strip()
        if alias.startswith("/") and target.startswith("/"):
            aliases.add(alias)
            redirects.append(
                {
                    "from": alias,
                    "to": target,
                    "status": "permanent",
                    "reason": str(item.get("reason") or "İçerik niyeti konsolidasyonu"),
                }
            )
    return aliases, redirects


def first_match(pattern: str, text: str, flags: int = re.I | re.S) -> str:
    match = re.search(pattern, text, flags)
    return unescape(match.group(1).strip()) if match else ""


def extract_title(html: str) -> str:
    return re.sub(r"\s+", " ", first_match(r"<title\b[^>]*>(.*?)</title>", html)).strip()


def extract_meta_description(html: str) -> str:
    patterns = (
        r'<meta\b(?=[^>]*\bname=["\']description["\'])(?=[^>]*\bcontent=["\']([^"\']*)["\'])[^>]*>',
        r'<meta\b(?=[^>]*\bcontent=["\']([^"\']*)["\'])(?=[^>]*\bname=["\']description["\'])[^>]*>',
    )
    for pattern in patterns:
        value = first_match(pattern, html)
        if value:
            return re.sub(r"\s+", " ", value).strip()
    return ""


def extract_canonical(html: str) -> str:
    return first_match(r'<link\b(?=[^>]*\brel=["\']canonical["\'])(?=[^>]*\bhref=["\']([^"\']+)["\'])[^>]*>', html)


def extract_h1(html: str) -> str:
    value = first_match(r"<h1\b[^>]*>(.*?)</h1>", html)
    return re.sub(r"<[^>]+>", " ", value).strip() if value else ""


def extract_lang(html: str) -> str:
    return first_match(r'<html\b[^>]*\blang=["\']([^"\']+)["\']', html) or "tr"


def jsonld_blocks(html: str) -> list[Any]:
    values: list[Any] = []
    for raw in re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.I | re.S,
    ):
        try:
            values.append(json.loads(raw.strip()))
        except json.JSONDecodeError:
            values.append({"_invalid": True, "raw": raw.strip()[:1000]})
    return values


def collect_schema_types(value: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        item_type = value.get("@type")
        if isinstance(item_type, str):
            result.add(item_type)
        elif isinstance(item_type, list):
            result.update(str(item) for item in item_type)
        for child in value.values():
            result.update(collect_schema_types(child))
    elif isinstance(value, list):
        for child in value:
            result.update(collect_schema_types(child))
    return result


def extract_text(html: str) -> str:
    parser = MainTextExtractor()
    parser.feed(html)
    return parser.text()


def extract_local_refs(html: str, source_file: Path) -> set[Path]:
    refs: set[Path] = set()
    for value in re.findall(r'\b(?:src|href|poster)=["\']([^"\']+)["\']', html, re.I):
        clean = value.split("#", 1)[0].split("?", 1)[0].strip()
        if not clean or clean.startswith(("http://", "https://", "mailto:", "tel:", "data:", "#", "/")):
            continue
        resolved = (source_file.parent / clean).resolve()
        try:
            resolved.relative_to(SITE_ROOT.resolve())
        except ValueError:
            continue
        if resolved.is_file() and resolved.suffix.casefold() in ASSET_SUFFIXES:
            refs.add(resolved)
    for value in re.findall(r"\burl\((?:['\"]?)([^)'\"]+)", html, re.I):
        clean = value.split("#", 1)[0].split("?", 1)[0].strip()
        if not clean or clean.startswith(("http://", "https://", "data:", "/")):
            continue
        resolved = (source_file.parent / clean).resolve()
        try:
            resolved.relative_to(SITE_ROOT.resolve())
        except ValueError:
            continue
        if resolved.is_file() and resolved.suffix.casefold() in ASSET_SUFFIXES:
            refs.add(resolved)
    return refs


def route_category(route: dict[str, str]) -> str:
    path = route["canonicalPath"]
    route_type = route["type"]
    if path.startswith("/il/"):
        return "location-province"
    if path.startswith("/dagitim-sirketi/"):
        return "location-company"
    if path.startswith("/amazon-elektrik-urunleri/") or route_type == "commerce-guide":
        return "affiliate-guide"
    if path.startswith("/haberler/") or route_type == "article":
        return "technical-article"
    if route_type in INTERACTIVE_TYPES or path.startswith("/hesaplama/"):
        return "interactive-tool"
    if route_type in {"service", "partnership"} or path.startswith("/hizmet"):
        return "professional-service"
    if path.startswith("/en/"):
        return "english-core"
    return "core-page"


def route_priority(route: dict[str, str], policy: dict[str, Any]) -> int:
    path = route["canonicalPath"]
    if path in set(policy.get("coreRoutes", [])):
        return 0
    category = route_category(route)
    if category in {"location-province", "location-company", "interactive-tool", "professional-service"}:
        return 1
    if category in {"technical-article", "affiliate-guide"}:
        return 2
    return 3


def import_mode(route: dict[str, str]) -> str:
    category = route_category(route)
    if category == "interactive-tool":
        return "sites-interactive-app"
    if category in {"location-province", "location-company"}:
        return "sites-structured-page"
    if category == "affiliate-guide":
        return "sites-native-page-with-commerce-gate"
    return "sites-native-page"


def route_matches_patterns(route: str, patterns: Iterable[str]) -> bool:
    lowered = route.casefold()
    return any(str(pattern).casefold() in lowered for pattern in patterns)


def amazon_links(html: str) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for match in re.finditer(r"<a\b([^>]*)>", html, re.I | re.S):
        attrs = match.group(1)
        href = first_match(r'\bhref=["\']([^"\']+)["\']', attrs)
        data_href = first_match(r'\bdata-(?:affiliate-)?href=["\']([^"\']+)["\']', attrs)
        target = href or data_href
        if target and any(host in target.casefold() for host in ("amazon.com.tr", "amzn.to")):
            result.append(
                {
                    "target": target,
                    "rel": first_match(r'\brel=["\']([^"\']+)["\']', attrs),
                    "locked": "href=" not in attrs.casefold() and bool(data_href),
                }
            )
    return result


def affiliate_contract(html: str, policy: dict[str, Any]) -> dict[str, Any]:
    links = amazon_links(html)
    visible = extract_text(html).casefold()
    disclosure = any(token in visible for token in ("satış ortaklığı", "satis ortakligi", "gelir ortağı", "gelir ortagi", "affiliate"))
    no_buy = any(
        token in visible
        for token in (
            "yeni ürün almayın",
            "yeni urun almayin",
            "satın alma yapmayacağım",
            "satin alma yapmayacagim",
            "mevcut çözüm yeterli",
            "mevcut cozum yeterli",
            "satın almama",
            "satin almama",
        )
    )
    required_rel = {str(item).casefold() for item in policy["trustRules"]["affiliateRelRequired"]}
    unsafe_links: list[str] = []
    for item in links:
        if item["locked"]:
            continue
        rel = {token.casefold() for token in item["rel"].split()}
        if not required_rel.issubset(rel):
            unsafe_links.append(item["target"])
    return {
        "hasAffiliateLinks": bool(links),
        "linkCount": len(links),
        "disclosureVisible": disclosure,
        "noBuyOutcomeVisible": no_buy,
        "unsafeStaticLinks": unsafe_links,
        "safe": not links or (disclosure and no_buy and not unsafe_links),
    }


def professional_lead(route: str, policy: dict[str, Any]) -> bool:
    return route_matches_patterns(route, policy.get("professionalLeadKeywords", []))


def safe_filename(route: str) -> str:
    value = route.strip("/") or "home"
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value)
    return value[:180]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def copy_preserving_site_path(source: Path, target_root: Path) -> str:
    relative = source.relative_to(SITE_ROOT)
    destination = target_root / "source" / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination.relative_to(target_root).as_posix()


def markdown_document(record: dict[str, Any], body_text: str) -> str:
    frontmatter = {
        "title": record["title"],
        "description": record["description"],
        "canonicalPath": record["canonicalPath"],
        "canonicalUrl": record["canonicalUrl"],
        "contentType": record["category"],
        "importMode": record["importMode"],
        "priority": record["priority"],
        "language": record["language"],
        "sourceFile": record["source"],
        "schemaTypes": record["schemaTypes"],
        "affiliate": record["affiliate"],
        "professionalLead": record["professionalLead"],
    }
    return "---\n" + json.dumps(frontmatter, ensure_ascii=False, indent=2) + "\n---\n\n" + body_text + "\n"


def build_site_brief(policy: dict[str, Any], stats: dict[str, Any], source_commit: str) -> str:
    return f"""# ALO186 → ChatGPT Sites ana aktarım brifi

Kaynak commit: `{source_commit}`  
Paket sürümü: `{policy['version']}`  
Hedef site slug: `{policy['siteSlug']}`

## Yeni işletim modeli

ChatGPT Sites; içerik, veri, dosya, sürüm, yayın ve analitik için yeni tek kaynak sistemidir. GitHub paketi yalnız ilk aktarım ve arşiv kaynağıdır. Aktarım sonrasında içerik değişiklikleri ChatGPT Sites içinde yapılmalıdır.

## Değişmez güven sözleşmesi

- ALO186 bağımsız bilgi platformudur; EDAŞ, TEDAŞ, EPDK, EMO, GİB veya kamu kurumu değildir.
- Arıza, tazminat, abonelik veya kişisel başvuru kaydı almaz.
- 112, 186, resmî EDAŞ ve yetkin elektrikçi ayrımı her ticari içerikten önce gelir.
- Aktif tehlike, yaşam güvenliği, medikal, yangın, sabit tesisat ve yüksek güçlü profesyonel sistemlerde tüketici affiliate yolu kapalıdır.
- Yalnız Amazon Türkiye satış ortaklığı kullanılır ve ilişki bağlantıdan önce görünür biçimde açıklanır.
- Doğrulanmamış fiyat, stok, puan, yorum, teslimat veya garanti yayımlanmaz.
- Mevcut güvenli çözüm yeterliyse sonuç açıkça “yeni ürün almayın” olmalıdır.
- `Product` şeması yalnız genel ürün sınıfını anlatabilir; doğrulanmamış `Offer`, `AggregateRating` veya `Review` üretilemez.

## Sites bilgi mimarisi

1. Ana görev merkezi: güvenlik, EDAŞ, 60 saniyelik karar, ücretsiz araçlar.
2. 81 il ve 21 dağıtım şirketi: statik, JS gerektirmeyen, resmî kanal odaklı sayfalar.
3. Hesaplama ve karar araçları: interaktif Sites uygulamaları; temel cevap ve güvenlik fallback’i kaynak HTML’de görünür.
4. Teknik rehberler: soru → sorun → kanıt → güvenli çözüm → sonraki adım.
5. Affiliate rehberleri: ücretsiz teknik kontrol → satın almama → doğrulanmış eksik → açık affiliate geçişi.
6. Profesyonel hizmetler: trafo, jeneratör, GES, EV şarj, pano, harmonik ve proje konularında ürün yerine nitelikli mühendislik talebi.

## Paket özeti

- Aktarıma hazır sayfa: **{stats['importReady']}**
- İnsan incelemesine ayrılan sayfa: **{stats['reviewOnly']}**
- İl sayfası: **{stats['provincePages']}**
- Dağıtım şirketi sayfası: **{stats['companyPages']}**
- Interaktif araç: **{stats['interactiveTools']}**
- Teknik makale: **{stats['technicalArticles']}**
- Affiliate rehberi: **{stats['affiliateGuides']}**
- Redirect/konsolidasyon: **{stats['redirectCount']}**

## Yayın kabulü

Her sayfa için benzersiz canonical, title, meta açıklaması, tek H1, mobil okunabilirlik, erişilebilir dokunma hedefleri ve bağlamsal iç bağlantılar kontrol edilmelidir. Sitemap yalnız canonical sayfaları içermeli; alias yollar redirect haritasından yönetilmelidir.
"""


def build_import_order() -> str:
    return """# ChatGPT Sites aktarım sırası

## Aşama 1 — Güven ve ana navigasyon

`SITE_BRIEF.md`, yayın ilkeleri, affiliate açıklaması, gizlilik, kaynaklar, acil numaralar ve ana görev merkezini içe alın. Bu katman tamamlanmadan ürün veya hizmet sayfalarını yayımlamayın.

## Aşama 2 — EDAŞ ve konum verisi

`data/location-services.json` içindeki 81 il ve 21 şirket kayıtlarını Sites veri koleksiyonlarına aktarın. Her sayfada ALO186 bağımsızlık açıklaması, 186 hizmet kanalı ve gerçek 112 kamu hizmeti ayrımı korunmalıdır.

## Aşama 3 — Ücretsiz araçlar

`sites-interactive-app` kayıtlarını interaktif Sites uygulamaları olarak kurun. `source/` altındaki HTML/JS/CSS işlevlerini taşıyın; ancak sayfanın doğrudan cevabı, güvenlik sınırı ve noscript/fallback içeriği SSR olarak görünür kalsın.

## Aşama 4 — Teknik rehberler

`technical-article` sayfalarını doğal Sites sayfalarına dönüştürün. Kaynaklar, güncelleme tarihi, kapsam dışı hususlar ve güvenli CTA korunmalıdır.

## Aşama 5 — Affiliate rehberleri

Yalnız `importReady=true` olan affiliate sayfalarını aktarın. `review/` kayıtları otomatik yayımlanamaz. Amazon bağlantısı; teknik kontrol, satın almama sonucu ve görünür satış ortaklığı açıklamasından sonra açılmalıdır.

## Aşama 6 — Profesyonel hizmetler

Trafo, jeneratör, GES, EV şarj, pano, harmonik, OG/AG ve proje içeriklerini mühendislik lead yolculuğuna bağlayın; tüketici ürün kartına dönüştürmeyin.

## Aşama 7 — Redirect, sitemap ve alan adı

`data/redirects.json` haritasını uygulayın. Canonical host `https://alo186.com` olarak korunmalı, ardından ChatGPT Sites'in sağladığı özel alan DNS kayıtları uygulanmalıdır.
"""


def export_bundle(output: Path, source_commit: str) -> dict[str, Any]:
    policy = read_json(POLICY_PATH, {})
    if not isinstance(policy, dict) or policy.get("targetPlatform") != "ChatGPT Sites":
        raise ValueError("ChatGPT Sites export politikası eksik veya geçersiz")

    aliases, redirects = load_aliases()
    routes = [route for route in load_effective_routes() if route["canonicalPath"] not in aliases]
    review_patterns = policy.get("reviewOnlyRoutePatterns", [])

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    (output / "content/pages").mkdir(parents=True)
    (output / "review").mkdir(parents=True)
    (output / "data").mkdir(parents=True)
    (output / "policies").mkdir(parents=True)

    records: list[dict[str, Any]] = []
    review_records: list[dict[str, Any]] = []
    copied_assets: set[str] = set()
    category_counts: Counter[str] = Counter()

    for route in routes:
        source_file = REPO_ROOT / route["source"]
        if not source_file.is_file():
            review_records.append({**route, "reason": "Kaynak dosya bulunamadı"})
            continue
        html = source_file.read_text(encoding="utf-8")
        title = extract_title(html)
        description = extract_meta_description(html)
        h1 = extract_h1(html)
        canonical = extract_canonical(html)
        language = extract_lang(html)
        schemas = jsonld_blocks(html)
        schema_types = sorted(set().union(*(collect_schema_types(item) for item in schemas))) if schemas else []
        category = route_category(route)
        affiliate = affiliate_contract(html, policy)
        pattern_review = route_matches_patterns(route["canonicalPath"], review_patterns)
        has_required_metadata = bool(title and description and h1)
        canonical_url = policy["canonicalHost"] + route["canonicalPath"]
        canonical_ok = not canonical or urlparse(canonical).netloc in {"alo186.com", "www.alo186.com"}
        import_ready = has_required_metadata and canonical_ok and not pattern_review and affiliate["safe"]
        review_reasons: list[str] = []
        if not has_required_metadata:
            review_reasons.append("Title/meta/H1 eksik")
        if not canonical_ok:
            review_reasons.append("Canonical farklı origin kullanıyor")
        if pattern_review:
            review_reasons.append("Elektrik odağı zayıf genel aksesuar deseni")
        if not affiliate["safe"]:
            review_reasons.append("Affiliate açıklaması, satın almama sonucu veya rel sözleşmesi eksik")

        source_copy = copy_preserving_site_path(source_file, output)
        for asset in extract_local_refs(html, source_file):
            asset_key = asset.relative_to(SITE_ROOT).as_posix()
            if asset_key not in copied_assets:
                copy_preserving_site_path(asset, output)
                copied_assets.add(asset_key)

        record: dict[str, Any] = {
            "canonicalPath": route["canonicalPath"],
            "canonicalUrl": canonical_url,
            "sourceCanonical": canonical,
            "source": route["source"],
            "sourceCopy": source_copy,
            "routeType": route["type"],
            "category": category,
            "importMode": import_mode(route),
            "priority": route_priority(route, policy),
            "title": title,
            "description": description,
            "h1": h1,
            "language": language,
            "schemaTypes": schema_types,
            "jsonLd": schemas,
            "interactive": route["type"] in INTERACTIVE_TYPES or bool(re.search(r"<script\b(?![^>]*ld\+json)", html, re.I)),
            "affiliate": affiliate,
            "professionalLead": professional_lead(route["canonicalPath"], policy),
            "importReady": import_ready,
            "reviewReasons": review_reasons,
        }
        records.append(record)
        category_counts[category] += 1

        markdown = markdown_document(record, extract_text(html))
        md_name = safe_filename(route["canonicalPath"]) + ".md"
        md_root = output / ("content/pages" if import_ready else "review")
        (md_root / md_name).write_text(markdown, encoding="utf-8")

    ready = sorted((item for item in records if item["importReady"]), key=lambda item: (item["priority"], item["canonicalPath"]))
    review = sorted((item for item in records if not item["importReady"]), key=lambda item: item["canonicalPath"])
    review.extend(review_records)

    location_records = [
        {
            "canonicalPath": item["canonicalPath"],
            "title": item["title"],
            "description": item["description"],
            "category": item["category"],
            "jsonLd": item["jsonLd"],
            "sourceCopy": item["sourceCopy"],
        }
        for item in ready
        if item["category"] in {"location-province", "location-company"}
    ]

    navigation: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in ready:
        navigation[item["category"]].append(
            {
                "canonicalPath": item["canonicalPath"],
                "title": item["title"],
                "description": item["description"],
                "priority": item["priority"],
                "importMode": item["importMode"],
            }
        )

    stats = {
        "effectiveRoutes": len(routes),
        "importReady": len(ready),
        "reviewOnly": len(review),
        "provincePages": category_counts["location-province"],
        "companyPages": category_counts["location-company"],
        "interactiveTools": category_counts["interactive-tool"],
        "technicalArticles": category_counts["technical-article"],
        "affiliateGuides": category_counts["affiliate-guide"],
        "professionalServices": category_counts["professional-service"],
        "redirectCount": len(redirects),
        "copiedAssets": len(copied_assets),
    }

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest = {
        "schemaVersion": 1,
        "siteSlug": policy["siteSlug"],
        "targetPlatform": policy["targetPlatform"],
        "targetSourceOfTruth": policy["targetSourceOfTruth"],
        "canonicalHost": policy["canonicalHost"],
        "generatedAt": generated_at,
        "sourceCommit": source_commit,
        "stats": stats,
        "policies": policy["trustRules"],
        "pages": ready,
        "reviewOnly": review,
    }
    write_json(output / "sites-import.json", manifest)
    write_json(output / "data/navigation.json", dict(navigation))
    write_json(output / "data/location-services.json", location_records)
    write_json(output / "data/redirects.json", redirects)
    write_json(output / "data/export-stats.json", stats)
    write_json(output / "review/review-index.json", review)

    (output / "SITE_BRIEF.md").write_text(build_site_brief(policy, stats, source_commit), encoding="utf-8")
    (output / "IMPORT_ORDER.md").write_text(build_import_order(), encoding="utf-8")
    (output / "policies/trust-and-commerce.md").write_text(
        "# ALO186 güven ve ticari yönetişim\n\n"
        "Bu dosya `chatgpt-sites-export-policy.json` içindeki kuralların insan tarafından okunabilir özetidir. "
        "ALO186 resmî kurum değildir; aktif tehlikede ticaret kapalıdır; yalnız Amazon Türkiye satış ortaklığı kullanılır; "
        "fiyat, stok, puan ve garanti yayımlanmaz; mevcut çözüm yeterliyse yeni ürün önerilmez.\n",
        encoding="utf-8",
    )

    checksums: list[str] = []
    for path in sorted(item for item in output.rglob("*") if item.is_file() and item.name != "checksums.sha256"):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        checksums.append(f"{digest}  {path.relative_to(output).as_posix()}")
    (output / "checksums.sha256").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 GitHub içeriğini ChatGPT Sites aktarım paketine dönüştürür")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--commit", default=os.environ.get("GITHUB_SHA", "unknown"))
    args = parser.parse_args()
    manifest = export_bundle(args.output.resolve(), args.commit)
    print(json.dumps({"ok": True, "output": str(args.output), "stats": manifest["stats"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
