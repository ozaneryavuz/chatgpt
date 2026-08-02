from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

VERSION = 219
HOST = "https://alo186.com"
POLICY_PATH = "/yayin-politikasi"
POLICY_URL = HOST + POLICY_PATH
ORGANIZATION_ID = HOST + "/#organization"
MARKER = 'data-alo186-aeo-institutional-v219="true"'
STYLE_MARKER = 'data-alo186-aeo-institutional-style-v219="true"'
SCHEMA_MARKER = 'data-alo186-aeo-institutional-schema-v219="true"'
ASSET = "assets/aeo-institutional-v219.css"
CSS_SOURCE = Path(__file__).resolve().with_name("aeo-institutional-v219.css")
PERSONAL_SCHEMA_RE = re.compile(
    r'''(?:["']@type["']\s*:\s*["']Person["']|ProfilePage|/uzman/)''', re.I
)
TAG_RE = re.compile(r"<[^>]+>")
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
P_RE = re.compile(r"<p\b[^>]*>(.*?)</p>", re.I | re.S)
LD_RE = re.compile(
    r'''<script\b[^>]*type=["']application/ld\+json["'][^>]*>(.*?)</script>''',
    re.I | re.S,
)

PREFIXES = ("haberler/", "sektor-rehberi/", "il/")
EXACT = {
    "index.html", "elektrik-portali/index.html", "elektrik-kesintisi/index.html",
    "edas-bul/index.html", "acil-numaralar/index.html", "hakkimizda/index.html",
    "kaynaklar/index.html", "hesaplama/index.html", "amazon-elektrik-urunleri/index.html",
    "hesaplama/ups-suresi/index.html", "hesaplama/jenerator-gucu-secimi/index.html",
    "hesaplama/ev-sarj-uygunluk/index.html",
    "hesaplama/gerilim-koruma-cozum-secici/index.html",
    "hesaplama/yedek-guc-cozum-secici/index.html",
}
CRITICAL = (
    "/elektrik-portali", "/edas-bul", "/elektrik-kesintisi", "/acil-numaralar",
    "/haberler/planli-elektrik-kesintisi-ne-kadar-once-bildirilir",
    "/hesaplama/yedek-guc-cozum-secici/",
    "/haberler/ges-elektrik-kesintisinde-calisir-mi",
    "/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu",
    "/haberler/topraklama-direnci-kac-ohm-olmali", POLICY_PATH,
)
REPLACEMENTS = (
    ("50+ elektrik ürünü için Amazon seçim kartları", "Elektrik ürünleri için teknik seçim kartları"),
    ("50+ elektrik ürünü", "Elektrik ürünleri"),
    ("25 rehberin tamamını gör", "Tüm ürün rehberlerini gör"),
)


def _base(value: str) -> str:
    value = (value or "").strip()
    return "" if value in {"", "/"} else "/" + value.strip("/")


def _public(base: str, path: str) -> str:
    return _base(base) + "/" + path.lstrip("/")


def _route(value: str) -> str:
    value = "/" + (value or "").strip().strip("/")
    return "/" if value == "/" else value


def _file(site: Path, route: str) -> Path:
    route = _route(route)
    return site / "index.html" if route == "/" else site / route.strip("/") / "index.html"


def _visible(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(TAG_RE.sub(" ", value))).strip()


def _eligible(relative: str) -> bool:
    return relative != "yayin-politikasi/index.html" and (
        relative in EXACT or relative.startswith(PREFIXES)
    )


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.title_parts: list[str] = []
        self.in_title = False
        self.description = ""
        self.canonical = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = {key.casefold(): unescape(value or "") for key, value in attrs}
        tag = tag.casefold()
        if tag == "html":
            self.lang = attrs_map.get("lang", "")
        elif tag == "title":
            self.in_title = True
        elif tag == "meta" and attrs_map.get("name", "").casefold() == "description":
            self.description = attrs_map.get("content", "")
        elif tag == "link" and "canonical" in attrs_map.get("rel", "").casefold().split():
            self.canonical = attrs_map.get("href", "")

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return _visible(" ".join(self.title_parts))


def _head(html: str) -> HeadParser:
    parser = HeadParser()
    parser.feed(html)
    parser.close()
    return parser


def _schema(canonical: str) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "@id": canonical.rstrip("/") + "#webpage",
        "editor": {"@type": "Organization", "@id": ORGANIZATION_ID,
                   "name": "ALO186", "url": HOST},
        "publishingPrinciples": POLICY_URL,
    }
    return (
        f'<script type="application/ld+json" {SCHEMA_MARKER}>'
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )


def _block(base: str) -> str:
    href = _public(base, POLICY_PATH)
    return f'''<aside class="alo-aeo-institutional-v219" {MARKER} aria-label="Kurumsal yayın denetimi">
  <div class="alo-aeo-institutional-v219__identity"><span>Kurumsal yayın denetimi</span><strong><a href="{href}">ALO186 teknik yayın politikası</a></strong><p>Kaynak, güvenlik sınırı, güncellik ve düzeltme süreci</p></div>
  <a class="alo-aeo-institutional-v219__method" href="{href}#dogrulama-yontemi">Doğrulama yöntemini incele</a>
</aside>'''


def _finish(html: str) -> str:
    html = html.rstrip()
    folded = html.casefold()
    if "</body>" not in folded:
        point = folded.rfind("</html>")
        html = html[:point].rstrip() + "\n</body>\n" + html[point:] if point >= 0 else html + "\n</body>"
    if "</html>" not in html.casefold():
        html += "\n</html>"
    return html + "\n"


def _inject_page(path: Path, site: Path, base: str) -> tuple[bool, int]:
    html = path.read_text(encoding="utf-8")
    relative = path.relative_to(site).as_posix()
    replacements = 0
    if relative in {"index.html", "elektrik-portali/index.html"}:
        for old, new in REPLACEMENTS:
            count = html.count(old)
            html = html.replace(old, new)
            replacements += count
    if MARKER in html:
        if replacements:
            path.write_text(_finish(html), encoding="utf-8")
        return False, replacements
    if PERSONAL_SCHEMA_RE.search(html):
        raise RuntimeError(f"AEO v219 kişisel profil şeması yasak: {relative}")
    head = _head(html)
    if not head.canonical or "<body" not in html.casefold():
        raise RuntimeError(f"AEO v219 canonical/body eksik: {relative}")
    head_end = html.casefold().find("</head>")
    if head_end < 0:
        raise RuntimeError(f"AEO v219 </head> eksik: {relative}")
    style = f'<link rel="stylesheet" href="{_public(base, ASSET)}" {STYLE_MARKER}>'
    html = html[:head_end] + style + "\n" + _schema(head.canonical) + "\n" + html[head_end:]
    point = html.casefold().rfind("</main>")
    if point < 0:
        point = html.casefold().rfind("</body>")
    html = html[:point] + "\n" + _block(base) + "\n" + html[point:]
    path.write_text(_finish(html), encoding="utf-8")
    return True, replacements


def _refresh_checksums(site: Path) -> None:
    target = site / "checksums.sha256"
    if not target.exists():
        return
    target.unlink()
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(site).as_posix()}"
        for path in sorted(site.rglob("*")) if path.is_file()
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def inject(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base = _base(base_path)
    if not site.is_dir() or not CSS_SOURCE.is_file():
        raise FileNotFoundError("AEO v219 site veya CSS kaynağı eksik")
    asset = site / ASSET
    asset.parent.mkdir(parents=True, exist_ok=True)
    asset.write_text(CSS_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
    newly_injected: list[str] = []
    copy_replacements = 0
    for path in sorted(site.rglob("index.html")):
        relative = path.relative_to(site).as_posix()
        if _eligible(relative):
            changed, count = _inject_page(path, site, base)
            copy_replacements += count
            if changed:
                newly_injected.append(relative)
    active = [
        path.relative_to(site).as_posix() for path in sorted(site.rglob("index.html"))
        if _eligible(path.relative_to(site).as_posix())
        and MARKER in path.read_text(encoding="utf-8", errors="ignore")
    ]
    if not active:
        raise RuntimeError("AEO v219 hiçbir sayfaya uygulanamadı")
    release_path = site / "pages-release.json"
    if release_path.is_file():
        release = json.loads(release_path.read_text(encoding="utf-8"))
        previous = release.get("aeoInstitutional", {})
        release["aeoInstitutional"] = {
            "version": VERSION, "basePath": base,
            "policyPath": POLICY_PATH, "policyCanonical": POLICY_URL,
            "editorEntity": "ALO186", "editorType": "Organization",
            "publishingPrinciples": POLICY_URL,
            "injectedPageCount": len(active), "injectedPages": active,
            "newlyInjectedPageCount": len(newly_injected),
            "newlyInjectedPages": newly_injected,
            "volatileCopyReplacements": int(previous.get("volatileCopyReplacements", 0)) + copy_replacements,
            "personalProfilePublished": False,
            "personalContactPublished": False,
        }
        release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _refresh_checksums(site)
    return {
        "ok": True, "version": VERSION, "basePath": base,
        "policyPath": POLICY_PATH, "injectedPageCount": len(active),
        "newlyInjectedPageCount": len(newly_injected),
        "volatileCopyReplacements": copy_replacements,
        "personalProfilePublished": False,
    }


def _jsonld(html: str, errors: list[str], label: str) -> list[object]:
    docs: list[object] = []
    for index, raw in enumerate(LD_RE.findall(html), 1):
        try:
            docs.append(json.loads(unescape(raw.strip())))
        except json.JSONDecodeError as exc:
            errors.append(f"{label}: JSON-LD {index} geçersiz: {exc}")
    return docs


def _walk(value: object):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _types(docs: list[object]) -> set[str]:
    result: set[str] = set()
    for doc in docs:
        for node in _walk(doc):
            value = node.get("@type")
            if isinstance(value, str):
                result.add(value)
            elif isinstance(value, list):
                result.update(map(str, value))
    return result


def _has_editor(docs: list[object]) -> bool:
    return any(
        isinstance(node.get("editor"), dict)
        and node["editor"].get("@id") == ORGANIZATION_ID
        and node["editor"].get("@type") in {None, "Organization"}
        for doc in docs for node in _walk(doc)
    )


def _sitemap(site: Path, errors: list[str]) -> set[str]:
    try:
        root = ET.fromstring((site / "sitemap.xml").read_text(encoding="utf-8"))
    except (OSError, ET.ParseError) as exc:
        errors.append(f"sitemap.xml geçersiz/eksik: {exc}")
        return set()
    paths: set[str] = set()
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] == "loc" and node.text:
            parsed = urlsplit(node.text.strip())
            if f"{parsed.scheme}://{parsed.netloc}" == HOST:
                paths.add(_route(parsed.path))
            else:
                errors.append(f"Sitemap origin yanlış: {node.text.strip()}")
    return paths


def _contracts(repo: Path, sitemap: set[str], errors: list[str]) -> dict[str, int]:
    metrics: dict[str, int] = {}
    for filename, key, metric in (
        ("intent-registry-v219.json", "intents", "intentCount"),
        ("ai-citation-benchmark-v219.json", "queries", "queryCount"),
    ):
        try:
            payload = json.loads((repo / "alo186/aeo" / filename).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{filename} geçersiz/eksik: {exc}")
            continue
        items = payload.get(key, [])
        if payload.get("version") != VERSION or not isinstance(items, list) or len(items) < 15:
            errors.append(f"{filename} sürüm/adet sözleşmesi başarısız")
            continue
        if payload.get("policy", {}).get("personalProfilesAllowed") is True:
            errors.append(f"{filename} kişisel profil politikasını ihlal ediyor")
        ids: set[str] = set()
        texts: set[str] = set()
        targets: set[str] = set()
        for item in items:
            identifier = str(item.get("intentId") or item.get("id") or "").strip()
            text = str(item.get("question") or item.get("query") or "").strip().casefold()
            target = _route(str(item.get("canonicalPath") or item.get("expectedPath") or ""))
            if not identifier or not text or identifier in ids or text in texts:
                errors.append(f"{filename} yinelenen/eksik kayıt: {identifier}")
            if key == "intents" and target in targets:
                errors.append(f"{filename} aynı canonical cevabı yineliyor: {target}")
            if target not in sitemap:
                errors.append(f"{filename} hedefi sitemapte yok: {target}")
            ids.add(identifier); texts.add(text); targets.add(target)
        metrics[metric] = len(ids)
    return metrics


def validate(site: Path, repo_root: Path, require_release_proof: bool = False) -> dict:
    site = site.resolve(); repo_root = repo_root.resolve()
    errors: list[str] = []; warnings: list[str] = []
    sitemap = _sitemap(site, errors)
    try:
        robots = (site / "robots.txt").read_text(encoding="utf-8").casefold()
    except OSError as exc:
        robots = ""; errors.append(f"robots.txt eksik: {exc}")
    if "user-agent: *" not in robots or "allow: /" not in robots:
        errors.append("robots genel tarama izni eksik")
    if f"sitemap: {HOST}/sitemap.xml" not in robots:
        errors.append("robots canonical sitemap eksik")
    if re.search(r"user-agent:\s*oai-searchbot[\s\S]{0,300}disallow:\s*/(?:\s|$)", robots):
        errors.append("OAI-SearchBot tamamen engellenmiş")
    metrics = _contracts(repo_root, sitemap, errors)
    pages: list[dict] = []
    for route in CRITICAL:
        path = _file(site, route); page_errors: list[str] = []
        if not path.is_file():
            errors.append(f"Kritik AEO sayfası eksik: {route}")
            pages.append({"path": route, "errors": ["eksik"]}); continue
        html = path.read_text(encoding="utf-8", errors="ignore")
        head = _head(html); docs = _jsonld(html, page_errors, route)
        if len(head.title) < 12: page_errors.append("title eksik/kısa")
        if len(head.description.strip()) < 50: page_errors.append("description eksik/kısa")
        if len(H1_RE.findall(html)) != 1: page_errors.append("tek H1 sözleşmesi başarısız")
        if not head.lang: page_errors.append("html lang eksik")
        parsed = urlsplit(head.canonical)
        if f"{parsed.scheme}://{parsed.netloc}" != HOST:
            page_errors.append(f"canonical origin uyumsuz: {head.canonical}")
        if not docs: page_errors.append("JSON-LD eksik")
        if PERSONAL_SCHEMA_RE.search(html): page_errors.append("kişisel profil veya Person schema bulundu")
        if route == POLICY_PATH:
            if not {"Organization", "WebPage"}.issubset(_types(docs)):
                page_errors.append("Organization/WebPage schema eksik")
            folded = html.casefold()
            for token in ("kurumsal yayın denetimi", "dogrulama-yontemi", "kişisel isim", "bağımsız bilgilendirme platformudur"):
                if token.casefold() not in folded: page_errors.append(f"yayın politikası bilgisi eksik: {token}")
        else:
            h1 = H1_RE.search(html)
            answer = P_RE.search(html[h1.end():h1.end()+5000]) if h1 else None
            if len(_visible(answer.group(1)) if answer else "") < 60:
                page_errors.append("alınabilir doğrudan cevap kısa/eksik")
            if MARKER not in html: page_errors.append("kurumsal yayın denetimi görünür değil")
            if not _has_editor(docs): page_errors.append("WebPage.editor Organization eksik")
        errors.extend(f"{route}: {item}" for item in page_errors)
        pages.append({"path": route, "errors": page_errors, "title": head.title})
    release: dict = {}
    release_path = site / "pages-release.json"
    if release_path.is_file():
        try:
            release = json.loads(release_path.read_text(encoding="utf-8")).get("aeoInstitutional", {})
        except json.JSONDecodeError as exc:
            errors.append(f"pages-release geçersiz: {exc}")
    elif require_release_proof:
        errors.append("pages-release kanıtı eksik")
    if require_release_proof and not (
        release.get("version") == VERSION
        and release.get("policyCanonical") == POLICY_URL
        and release.get("editorType") == "Organization"
        and release.get("personalProfilePublished") is False
        and release.get("personalContactPublished") is False
    ):
        errors.append("AEO kurumsal release kanıtı eksik/yanlış")
    score = max(0, 100 - min(80, len(errors) * 7) - min(20, len(warnings) * 2))
    return {
        "ok": not errors, "version": VERSION, "score": score,
        "metrics": {"sitemapPathCount": len(sitemap), "criticalPageCount": len(CRITICAL),
                    "criticalPagePassCount": sum(not page["errors"] for page in pages), **metrics},
        "pages": pages, "release": release, "warnings": warnings, "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    inject_parser = commands.add_parser("inject")
    inject_parser.add_argument("--site", type=Path, required=True)
    inject_parser.add_argument("--base-path", default="")
    validate_parser = commands.add_parser("validate")
    validate_parser.add_argument("--site", type=Path, required=True)
    validate_parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    validate_parser.add_argument("--report", type=Path)
    validate_parser.add_argument("--require-release-proof", action="store_true")
    args = parser.parse_args()
    report = inject(args.site, args.base_path) if args.command == "inject" else validate(
        args.site, args.repo_root, args.require_release_proof
    )
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if getattr(args, "report", None):
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    print(output, end="")
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
