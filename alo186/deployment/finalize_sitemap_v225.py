from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

VERSION = 225
CANONICAL_ORIGIN = "https://alo186.com"
ROBOTS_TEXT = "User-agent: *\nAllow: /\n\nSitemap: https://alo186.com/sitemap.xml\n"
ALIAS_MARKER = 'data-alo186-content-alias="true"'

# Eski içerik rotaları kullanıcıya ve arama motorlarına yalnız geçiş yüzeyi
# olarak kalabilir; site içindeki bütün yeni yönlendirmeler doğrudan canonical
# hedefe gitmelidir. Böylece alias sayfaları sitemap dışında tutulurken statik
# smoke ve kullanıcı yolculuğu aynı kaynak gerçeğini kullanır.
ALIAS_TARGETS = {
    "/haberler/elektrik-gerilimi-dusuk-yuksek-edas-olcum-talebi": (
        "/haberler/priz-gerilimi-neden-220-volttan-farkli-olabilir/"
    ),
    "/haberler/lifepo4-batarya-sogukta-sarj-edilir-mi": (
        "/haberler/lifepo4-bataryalar-kisin-sarj-edilir-mi/"
    ),
}
HREF_PATTERN = re.compile(
    r"(?P<prefix>\bhref\s*=\s*)(?P<quote>[\"'])(?P<url>[^\"']+)(?P=quote)",
    re.I,
)


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def equivalent_path(left: str, right: str) -> bool:
    def clean(value: str) -> str:
        path = urllib.parse.unquote(urllib.parse.urlsplit(value).path or "/")
        path = "/" + path.lstrip("/")
        return "/" if path == "/" else path.rstrip("/")
    return clean(left) == clean(right)


def route_file(site: Path, url: str, base_path: str) -> Path | None:
    path = urllib.parse.unquote(urllib.parse.urlsplit(url).path or "/")
    base = normalize_base_path(base_path)
    if base and (path == base or path.startswith(base + "/")):
        path = path[len(base):] or "/"
    if path == "/":
        candidate = site / "index.html"
        return candidate if candidate.is_file() else None
    target = site / path.lstrip("/")
    for candidate in (target, target / "index.html", Path(str(target) + ".html")):
        if candidate.is_file():
            return candidate
    return None


def meta_robots(html: str) -> str:
    values = re.findall(
        r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']*)["\']',
        html,
        re.I,
    )
    return " ".join(values).casefold()


def canonical(html: str) -> str:
    values = re.findall(
        r'<link\b[^>]*rel=["\'][^"\']*canonical[^"\']*["\'][^>]*href=["\']([^"\']+)["\']',
        html,
        re.I,
    )
    if not values:
        values = re.findall(
            r'<link\b[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\'][^"\']*canonical[^"\']*["\']',
            html,
            re.I,
        )
    return values[0].strip() if len(values) == 1 else ""


def qualify_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    path = "/" + (parsed.path or "/").lstrip("/")
    return urllib.parse.urlunsplit(("https", "alo186.com", path, "", ""))


def _alias_target(value: str, base_path: str) -> str | None:
    """Bir iç bağlantı alias ise canonical hedefini döndürür.

    Sadece root-relative bağlantılar ile alo186.com / www.alo186.com mutlak
    bağlantıları ele alınır. Haricî hostlara ve göreli dosya bağlantılarına
    dokunulmaz. Query ve fragment korunur.
    """

    parsed = urllib.parse.urlsplit(value)
    absolute = bool(parsed.scheme or parsed.netloc)
    if absolute:
        if parsed.scheme and parsed.scheme.casefold() not in {"http", "https"}:
            return None
        hostname = (parsed.hostname or "").casefold().removeprefix("www.")
        if hostname != "alo186.com":
            return None
    elif not value.startswith("/"):
        return None

    path = urllib.parse.unquote(parsed.path or "/")
    normalized_base = normalize_base_path(base_path)
    had_base = bool(
        normalized_base
        and (path == normalized_base or path.startswith(normalized_base + "/"))
    )
    route = path[len(normalized_base):] or "/" if had_base else path
    route = "/" + route.lstrip("/")
    key = "/" if route == "/" else route.rstrip("/")
    target = ALIAS_TARGETS.get(key)
    if target is None:
        return None

    target_path = (normalized_base + target) if had_base else target
    if absolute:
        return urllib.parse.urlunsplit(
            ("https", "alo186.com", target_path, parsed.query, parsed.fragment)
        )
    return urllib.parse.urlunsplit(("", "", target_path, parsed.query, parsed.fragment))


def rewrite_alias_links(site: Path, base_path: str) -> dict[str, Any]:
    """Final artifact içindeki alias href'leri canonical hedeflere taşır."""

    rewrites: list[dict[str, str]] = []
    touched_pages: set[str] = set()

    for path in sorted(site.rglob("*.html")):
        source = path.read_text(encoding="utf-8", errors="strict")

        def replace(match: re.Match[str]) -> str:
            current = match.group("url")
            target = _alias_target(current, base_path)
            if target is None or target == current:
                return match.group(0)
            relative = path.relative_to(site).as_posix()
            touched_pages.add(relative)
            rewrites.append({"page": relative, "from": current, "to": target})
            return f'{match.group("prefix")}{match.group("quote")}{target}{match.group("quote")}'

        updated = HREF_PATTERN.sub(replace, source)
        if updated != source:
            path.write_text(updated, encoding="utf-8")

    # Fail closed: alias rotaları kendi geçiş sayfaları dışında hiçbir HTML
    # href'inde kalmamalıdır. Alias sayfalarının canonical/refresh hedefleri
    # zaten yeni rotadır; dolayısıyla bu kontrol güvenle bütün artifacta uygulanır.
    remaining: list[str] = []
    for path in sorted(site.rglob("*.html")):
        source = path.read_text(encoding="utf-8", errors="strict")
        for match in HREF_PATTERN.finditer(source):
            if _alias_target(match.group("url"), base_path) is not None:
                remaining.append(
                    f'{path.relative_to(site).as_posix()} -> {match.group("url")}'
                )
    if remaining:
        raise RuntimeError(
            "Final artifact içinde canonical hedefe taşınmamış alias bağlantısı kaldı: "
            + "; ".join(remaining[:20])
        )

    return {
        "rewrittenLinkCount": len(rewrites),
        "touchedPageCount": len(touched_pages),
        "rewrites": rewrites[:50],
        "remainingAliasHrefCount": 0,
    }


def persist_release_proof(site: Path, report: dict[str, Any]) -> None:
    for name in ("alo186-release.json", "pages-release.json"):
        path = site / name
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["sitemapQualityV225"] = report
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict[str, Any]:
    site = site.resolve()
    normalized_base = normalize_base_path(base_path)
    project_preview = bool(normalized_base)
    sitemap_path = site / "sitemap.xml"
    robots_path = site / "robots.txt"
    if not sitemap_path.is_file():
        raise FileNotFoundError(f"Sitemap bulunamadı: {sitemap_path}")

    alias_link_report = rewrite_alias_links(site, normalized_base)

    try:
        tree = ET.parse(sitemap_path)
    except ET.ParseError as exc:
        raise RuntimeError(f"Sitemap XML ayrıştırılamadı: {exc}") from exc
    root = tree.getroot()
    namespace = root.tag.split("}", 1)[0].lstrip("{") if "}" in root.tag else ""
    prefix = f"{{{namespace}}}" if namespace else ""
    if root.tag.rsplit("}", 1)[-1] != "urlset":
        raise RuntimeError("Final sitemap urlset olmalıdır")

    removed_noindex: list[str] = []
    removed_alias: list[str] = []
    removed_noncanonical: list[str] = []
    removed_missing: list[str] = []
    removed_duplicate: list[str] = []
    normalized_origin = 0
    seen: set[str] = set()
    kept = 0

    for url_node in list(root.findall(f"{prefix}url")):
        loc_node = url_node.find(f"{prefix}loc")
        raw = str(loc_node.text or "").strip() if loc_node is not None else ""
        if not raw:
            root.remove(url_node)
            removed_missing.append("(boş loc)")
            continue
        normalized = qualify_url(raw)
        if raw != normalized:
            normalized_origin += 1
        if normalized in seen:
            root.remove(url_node)
            removed_duplicate.append(normalized)
            continue
        path = route_file(site, normalized, normalized_base)
        if path is None:
            root.remove(url_node)
            removed_missing.append(normalized)
            continue
        source = path.read_text(encoding="utf-8", errors="strict")
        if ALIAS_MARKER in source:
            root.remove(url_node)
            removed_alias.append(normalized)
            continue
        # /chatgpt bütün HTML'yi bilinçli olarak noindex yapan bir preview alanıdır.
        # Bu global preview etiketi canonical sitemap envanterini silmemelidir.
        if not project_preview and "noindex" in meta_robots(source):
            root.remove(url_node)
            removed_noindex.append(normalized)
            continue
        page_canonical = canonical(source)
        if not page_canonical:
            root.remove(url_node)
            removed_noncanonical.append(normalized + " → canonical eksik/çoklu")
            continue
        parsed_canonical = urllib.parse.urlsplit(page_canonical)
        if (
            parsed_canonical.scheme != "https"
            or (parsed_canonical.hostname or "").casefold().removeprefix("www.") != "alo186.com"
            or not equivalent_path(page_canonical, normalized)
        ):
            root.remove(url_node)
            removed_noncanonical.append(normalized + " → " + page_canonical)
            continue
        loc_node.text = normalized
        seen.add(normalized)
        kept += 1

    homepage = CANONICAL_ORIGIN + "/"
    homepage_file = site / "index.html"
    homepage_added = False
    if homepage_file.is_file():
        source = homepage_file.read_text(encoding="utf-8", errors="strict")
        home_indexable = project_preview or "noindex" not in meta_robots(source)
        if ALIAS_MARKER not in source and home_indexable and homepage not in seen:
            url_node = ET.Element(f"{prefix}url")
            loc_node = ET.SubElement(url_node, f"{prefix}loc")
            loc_node.text = homepage
            root.insert(0, url_node)
            seen.add(homepage)
            kept += 1
            homepage_added = True

    if not seen:
        raise RuntimeError("Final sitemap hiçbir canonical URL taşımıyor")
    if homepage_file.is_file() and homepage not in seen:
        raise RuntimeError("Canonical ana sayfa final sitemap içinde yok")

    ET.register_namespace("", namespace or "http://www.sitemaps.org/schemas/sitemap/0.9")
    ET.indent(tree, space="  ")
    tree.write(sitemap_path, encoding="utf-8", xml_declaration=True)
    robots_path.write_text(ROBOTS_TEXT, encoding="utf-8")

    report = {
        "version": VERSION,
        "canonicalOrigin": CANONICAL_ORIGIN,
        "basePath": normalized_base,
        "projectPreviewNoindexIgnored": project_preview,
        "keptUrlCount": kept,
        "homepageAdded": homepage_added,
        "normalizedOriginCount": normalized_origin,
        "removedNoindexCount": len(removed_noindex),
        "removedAliasCount": len(removed_alias),
        "removedNoncanonicalCount": len(removed_noncanonical),
        "removedMissingCount": len(removed_missing),
        "removedDuplicateCount": len(removed_duplicate),
        "removedNoindex": removed_noindex,
        "removedAlias": removed_alias,
        "removedNoncanonical": removed_noncanonical,
        "removedMissing": removed_missing,
        "removedDuplicate": removed_duplicate,
        "aliasLinkRewriteCount": alias_link_report["rewrittenLinkCount"],
        "aliasLinkTouchedPageCount": alias_link_report["touchedPageCount"],
        "aliasLinkRewrites": alias_link_report["rewrites"],
        "remainingAliasHrefCount": alias_link_report["remainingAliasHrefCount"],
        "robotsSingleCanonicalSitemap": True,
        "legacyWwwRejected": True,
    }
    (site / "sitemap-quality-v225.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    persist_release_proof(site, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 final sitemap ve robots canonical kalite v225")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
