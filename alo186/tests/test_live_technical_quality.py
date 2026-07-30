from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

CANONICAL_ORIGIN = "https://alo186.com"
LEGACY_HOST = "www.alo186.com"
IGNORED_SCHEMES = {"mailto", "tel", "javascript", "data", "blob"}
PERSONAL_INPUT_TYPES = {"email", "tel", "password"}
PERSONAL_AUTOCOMPLETE = {
    "name", "honorific-prefix", "given-name", "additional-name", "family-name",
    "email", "tel", "street-address", "address-line1", "address-line2",
    "postal-code", "country", "cc-name", "cc-number", "bday", "sex",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang = ""
        self.title_depth = 0
        self.title_text: list[str] = []
        self.h1_count = 0
        self.main_count = 0
        self.canonicals: list[str] = []
        self.references: list[tuple[str, str, dict[str, str]]] = []
        self.images: list[dict[str, str]] = []
        self.ids: list[str] = []
        self.meta: list[dict[str, str]] = []
        self.personal_fields: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.casefold(): (value or "") for key, value in attrs}
        lower = tag.casefold()
        if lower == "html":
            self.html_lang = values.get("lang", "")
        elif lower == "title":
            self.title_depth += 1
        elif lower == "h1":
            self.h1_count += 1
        elif lower == "main":
            self.main_count += 1
        elif lower == "link" and "canonical" in values.get("rel", "").casefold().split():
            if values.get("href"):
                self.canonicals.append(values["href"])
        elif lower == "meta":
            self.meta.append(values)
        elif lower == "img":
            self.images.append(values)
        elif lower == "input":
            input_type = values.get("type", "text").casefold()
            autocomplete = values.get("autocomplete", "").casefold().split()
            if input_type in PERSONAL_INPUT_TYPES:
                self.personal_fields.append(f"input[type={input_type}]")
            if PERSONAL_AUTOCOMPLETE.intersection(autocomplete):
                self.personal_fields.append(f"input[autocomplete={values.get('autocomplete')}]")

        if values.get("id"):
            self.ids.append(values["id"])
        for key in ("href", "src", "action", "poster", "data-src", "data-href"):
            if values.get(key):
                self.references.append((lower, values[key], values))
        if values.get("srcset"):
            for item in values["srcset"].split(","):
                candidate = item.strip().split(" ", 1)[0]
                if candidate:
                    self.references.append((lower, candidate, values))

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "title" and self.title_depth:
            self.title_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_text.append(data)


def route_exists(site: Path, path: str, base_path: str = "") -> bool:
    decoded = unquote(path or "/")
    if base_path and (decoded == base_path or decoded.startswith(base_path + "/")):
        decoded = decoded[len(base_path):] or "/"
    if decoded == "/":
        return (site / "index.html").is_file()
    target = site / decoded.lstrip("/")
    return target.is_file() or (target / "index.html").is_file()


def local_path_for_reference(page: Path, site: Path, reference: str, base_path: str) -> str | None:
    parsed = urlsplit(reference)
    if parsed.scheme.casefold() in IGNORED_SCHEMES or parsed.netloc:
        return None
    if reference.startswith(("#", "//")) or not parsed.path:
        return None
    if parsed.path.startswith("/"):
        path = parsed.path
    else:
        page_route = "/" + page.parent.relative_to(site).as_posix().strip("/") + "/"
        path = urljoin(page_route, parsed.path)
    normalized = "/" + posixpath.normpath(path).lstrip("/")
    return normalized


def json_ld_blocks(html: str) -> list[str]:
    return re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.I | re.S,
    )


def meta_content(parser: PageParser, name: str) -> str:
    for item in parser.meta:
        if item.get("name", "").casefold() == name.casefold():
            return item.get("content", "")
    return ""


def audit(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = "" if not base_path or base_path == "/" else "/" + base_path.strip("/")
    failures: list[str] = []
    warnings: list[str] = []
    link_count = 0
    image_count = 0
    jsonld_count = 0
    indexable_count = 0
    noindex_count = 0

    html_paths = sorted(site.rglob("*.html"))
    if not html_paths:
        failures.append("Artifactta HTML bulunamadı")

    for page in html_paths:
        relative = page.relative_to(site).as_posix()
        html = page.read_text(encoding="utf-8", errors="ignore")
        parser = PageParser()
        try:
            parser.feed(html)
        except Exception as exc:  # pragma: no cover - defensive parser guard
            failures.append(f"HTML ayrıştırılamadı: {relative}: {exc}")
            continue

        robots = meta_content(parser, "robots").casefold()
        noindex = "noindex" in robots
        if noindex:
            noindex_count += 1
        else:
            indexable_count += 1
            if len(parser.canonicals) != 1:
                failures.append(f"Indexlenebilir sayfada canonical sayısı {len(parser.canonicals)}: {relative}")
            elif not parser.canonicals[0].startswith(CANONICAL_ORIGIN + "/"):
                failures.append(f"Canonical apex değil: {relative}: {parser.canonicals[0]}")
            if parser.h1_count != 1:
                failures.append(f"Indexlenebilir sayfada H1 sayısı {parser.h1_count}: {relative}")
            if parser.main_count != 1:
                failures.append(f"Indexlenebilir sayfada main sayısı {parser.main_count}: {relative}")
            if not "".join(parser.title_text).strip():
                failures.append(f"Title boş: {relative}")
            if not meta_content(parser, "description").strip():
                failures.append(f"Meta description eksik: {relative}")
            if re.search(r'<meta\s+http-equiv=["\']refresh["\']', html, re.I):
                failures.append(f"Indexlenebilir sayfada meta refresh var: {relative}")

        normalized_lang = parser.html_lang.casefold().replace("_", "-").strip()
            expected_lang = "en" if relative == "en/index.html" or relative.startswith("en/") else "tr"
            actual_primary_lang = normalized_lang.split("-", 1)[0] if normalized_lang else ""
            if actual_primary_lang != expected_lang:
                failures.append(
                    f"html lang beklenen {expected_lang}, bulunan {parser.html_lang or 'boş'}: {relative}"
                )
        if "width=device-width" not in meta_content(parser, "viewport"):
            failures.append(f"Mobil viewport eksik: {relative}")
        if LEGACY_HOST in html:
            failures.append(f"www host artifactta kaldı: {relative}")
        if 'data-alo186-technical-quality="true"' not in html:
            failures.append(f"Responsive hardening eksik: {relative}")

        duplicate_ids = [item for item, count in Counter(parser.ids).items() if count > 1]
        if duplicate_ids:
            failures.append(f"Yinelenen id: {relative}: {', '.join(duplicate_ids[:8])}")

        for block_index, block in enumerate(json_ld_blocks(html), start=1):
            jsonld_count += 1
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                failures.append(f"Geçersiz JSON-LD: {relative} blok {block_index}: {exc.msg}")

        for image in parser.images:
            image_count += 1
            alt_present = "alt" in image
            decorative = image.get("role", "").casefold() == "presentation" or image.get("aria-hidden", "").casefold() == "true"
            if not alt_present and not decorative:
                failures.append(f"Alt metni olmayan görsel: {relative}: {image.get('src', image.get('data-src', ''))}")
            source = image.get("src") or image.get("data-src")
            if source:
                local = local_path_for_reference(page, site, source, base_path)
                if local and not route_exists(site, local, base_path):
                    failures.append(f"Yüklenemeyen yerel görsel: {relative} -> {source}")

        if parser.personal_fields and not noindex:
            failures.append(f"Kişisel veri alanı bulunan indexlenebilir sayfa: {relative}: {', '.join(parser.personal_fields[:6])}")

        for tag, reference, attrs in parser.references:
            local = local_path_for_reference(page, site, reference, base_path)
            if not local:
                continue
            link_count += 1
            if not route_exists(site, local, base_path):
                failures.append(f"Kırık yerel referans: {relative} [{tag}] -> {reference}")
            if tag == "a" and attrs.get("target") == "_blank" and "noopener" not in attrs.get("rel", "").casefold().split():
                warnings.append(f"target=_blank noopener eksik: {relative} -> {reference}")

    robots_path = site / "robots.txt"
    sitemap_path = site / "sitemap.xml"
    if not robots_path.is_file():
        failures.append("robots.txt eksik")
    else:
        robots = robots_path.read_text(encoding="utf-8")
        if "User-agent: *" not in robots or "Allow: /" not in robots:
            failures.append("robots.txt genel tarama sözleşmesi eksik")
        if f"Sitemap: {CANONICAL_ORIGIN}/sitemap.xml" not in robots:
            failures.append("robots.txt apex sitemap adresini taşımıyor")
        if LEGACY_HOST in robots:
            failures.append("robots.txt www host taşıyor")

    sitemap_urls: list[str] = []
    if not sitemap_path.is_file():
        failures.append("sitemap.xml eksik")
    else:
        try:
            root = ET.fromstring(sitemap_path.read_text(encoding="utf-8"))
            sitemap_urls = [element.text.strip() for element in root.iter() if element.tag.endswith("loc") and element.text]
        except ET.ParseError as exc:
            failures.append(f"sitemap.xml geçersiz XML: {exc}")
        duplicates = [url for url, count in Counter(sitemap_urls).items() if count > 1]
        if duplicates:
            failures.append("Sitemap yinelenen URL: " + ", ".join(duplicates[:10]))
        for url in sitemap_urls:
            parsed = urlsplit(url)
            if f"{parsed.scheme}://{parsed.netloc}" != CANONICAL_ORIGIN:
                failures.append(f"Sitemap canonical host dışında: {url}")
                continue
            if not route_exists(site, parsed.path, base_path):
                failures.append(f"Sitemap URL artifactta yok: {url}")

    route_bridges = 0
    bridge_path = site / "route-bridges.json"
    if bridge_path.is_file():
        payload = json.loads(bridge_path.read_text(encoding="utf-8"))
        route_bridges = int(payload.get("count") or 0)
        for item in payload.get("routes", []):
            source = str(item.get("source") or "")
            target = str(item.get("target") or "")
            if source.startswith(("/hesaplama/", "/hizmetler/")) and target == "/elektrik-portali":
                warnings.append(f"Genel portala düşen bridge incelenmeli: {source} -> {target}")

    if base_path and indexable_count:
        failures.append(f"Project-path artifactında {indexable_count} indexlenebilir HTML var")
    if not base_path and not indexable_count:
        failures.append("Custom-domain artifactında indexlenebilir sayfa yok")

    report = {
        "ok": not failures,
        "site": str(site),
        "basePath": base_path,
        "htmlCount": len(html_paths),
        "indexableHtmlCount": indexable_count,
        "noindexHtmlCount": noindex_count,
        "localReferenceCount": link_count,
        "imageCount": image_count,
        "jsonLdBlockCount": jsonld_count,
        "sitemapUrlCount": len(sitemap_urls),
        "routeBridgeCount": route_bridges,
        "failureCount": len(failures),
        "warningCount": len(warnings),
        "failures": failures[:200],
        "warnings": warnings[:200],
        "personalDataFieldsAdded": 0,
        "officialAffiliationClaimed": False,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 final artifact teknik kalite denetimi")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    audit(args.site, args.base_path)


if __name__ == "__main__":
    main()
