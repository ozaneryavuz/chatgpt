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

PREFIXES = ("haberler/", "sektor-rehberi/", "il/")
EXACT = {
    "index.html",
    "elektrik-portali/index.html",
    "elektrik-kesintisi/index.html",
    "edas-bul/index.html",
    "acil-numaralar/index.html",
    "hakkimizda/index.html",
    "kaynaklar/index.html",
    "hesaplama/index.html",
    "amazon-elektrik-urunleri/index.html",
    "hesaplama/ups-suresi/index.html",
    "hesaplama/jenerator-gucu-secimi/index.html",
    "hesaplama/ev-sarj-uygunluk/index.html",
    "hesaplama/gerilim-koruma-cozum-secici/index.html",
    "hesaplama/yedek-guc-cozum-secici/index.html",
}
CRITICAL = (
    "/elektrik-portali",
    "/edas-bul",
    "/elektrik-kesintisi",
    "/acil-numaralar",
    "/haberler/planli-elektrik-kesintisi-ne-kadar-once-bildirilir",
    "/hesaplama/yedek-guc-cozum-secici/",
    "/haberler/ges-elektrik-kesintisinde-calisir-mi",
    "/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu",
    "/haberler/topraklama-direnci-kac-ohm-olmali",
    POLICY_PATH,
)
REPLACEMENTS = (
    ("50+ elektrik ürünü için Amazon seçim kartları", "Elektrik ürünleri için teknik seçim kartları"),
    ("50+ elektrik ürünü", "Elektrik ürünleri"),
    ("25 rehberin tamamını gör", "Tüm ürün rehberlerini gör"),
)
TAG_RE = re.compile(r"<[^>]+>")
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
P_RE = re.compile(r"<p\b[^>]*>(.*?)</p>", re.I | re.S)
LD_RE = re.compile(
    r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)
PERSONAL_SCHEMA_RE = re.compile(
    r'(?:["\']@type["\']\s*:\s*["\']Person["\']|ProfilePage|/uzman/)',
    re.I,
)


def _base(value: str) -> str:
    value = (value or "").strip()
    return "" if value in {"", "/"} else "/" + value.strip("/")


def _public(base: str, path: str) -> str:
    return _base(base) + "/" + path.lstrip("/")


def _text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(TAG_RE.sub(" ", value))).strip()


def _path(value: str) -> str:
    normalized = "/" + (value or "").strip().strip("/")
    return "/" if normalized == "/" else normalized


def _file(site: Path, route: str) -> Path:
    route = _path(route)
    return site / "index.html" if route == "/" else site / route.strip("/") / "index.html"


def _eligible(relative: str) -> bool:
    return relative != "yayin-politikasi/index.html" and (
        relative in EXACT or relative.startswith(PREFIXES)
    )


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.in_title = False
        self.lang = ""
        self.description = ""
        self.canonical = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {name.casefold(): unescape(value or "") for name, value in attrs}
        folded = tag.casefold()
        if folded == "html":
            self.lang = data.get("lang", "")
        elif folded == "title":
            self.in_title = True
        elif folded == "meta" and data.get("name", "").casefold() == "description":
            self.description = data.get("content", "")
        elif folded == "link" and "canonical" in data.get("rel", "").casefold().split():
            self.canonical = data.get("href", "")

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return _text(" ".join(self.title_parts))


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
        "editor": {
            "@type": "Organization",
            "@id": ORGANIZATION_ID,
            "name": "ALO186",
            "url": HOST,
        },
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
    if "</body>" not in folded and "</html>" in folded:
        point = folded.rfind("</html>")
        html = html[:point].rstrip() + "\n</body>\n" + html[point:]
    elif "</body>" not in folded:
        html += "\n</body>"
    if "</html>" not in html.casefold():
        html += "\n</html>"
    return html + "\n"


def _inject_page(path: Path, site: Path, base: str) -> tuple[bool, int]:
    html = path.read_text(encoding="utf-8")
    relative = path.relative_to(site).as_posix()
    copy_changes = 0
    if relative in {"index.html", "elektrik-portali/index.html"}:
        for old, new in REPLACEMENTS:
            count = html.count(old)
            html = html.replace(old, new)
            copy_changes += count

    if MARKER in html:
        if copy_changes:
            path.write_text(_finish(html), encoding="utf-8")
        return False, copy_changes

    head = _head(html)
    if not head.canonical or "<body" not in html.casefold():
        raise RuntimeError(f"AEO v219 canonical/body eksik: {relative}")
    if PERSONAL_SCHEMA_RE.search(html):
        raise RuntimeError(f"AEO v219 kişisel profil şeması yasak: {relative}")

    style = f'<link rel="stylesheet" href="{_public(base, ASSET)}" {STYLE_MARKER}>'
    head_end = html.casefold().find("</head>")
    if head_end < 0:
        raise RuntimeError(f"AEO v219 </head> eksik: {relative}")
    html = html[:head_end] + style + "\n" + _schema(head.canonical) + "\n" + html[head_end:]

    insertion = html.casefold().rfind("</main>")
    if insertion < 0:
        insertion = html.casefold().rfind("</body>")
    if insertion < 0:
        insertion = len(html)
    html = html[:insertion] + "\n" + _block(base) + "\n" + html[insertion:]
    path.write_text(_finish(html), encoding="utf-8")
    return True, copy_changes


def _checksums(site: Path) -> None:
    target = site / "checksums.sha256"
    if not target.exists():
        return
    target.unlink()
    files = sorted(path for path in site.rglob("*") if path.is_file())
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(site).as_posix()}"
        for path in files
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
    replacements = 0
    for path in sorted(site.rglob("index.html")):
        relative = path.relative_to(site).as_posix()
        if _eligible(relative):
            changed, count = _inject_page(path, site, base)
            replacements += count
            if changed:
                newly_injected.append(relative)

    active = [
        path.relative_to(site).as_posix()
        for path in sorted(site.rglob("index.html"))
        if _eligible(path.relative_to(site).as_posix())
        and MARKER in path.read_text(encoding="utf-8", errors="ignore")
    ]
    if not active:
        raise RuntimeError("AEO v219 hiçbir sayfaya uygulanamadı")

    release_path = site / "pages-release.json"
    if release_path.is_file():
        release = json.loads(release_path.read_text(encoding="utf-8"))
        previous = (
            release.get("aeoInstitutional")
            if isinstance(release.get("aeoInstitutional"), dict)
            else {}
        )
        release["aeoInstitutional"] = {
            "version": VERSION,
            "basePath": base,
            "policyPath": POLICY_PATH,
            "policyCanonical": POLICY_URL,
            "editorEntity": "ALO186",
            "editorType": "Organization",
            "publishingPrinciples": POLICY_URL,
            "injectedPageCount": len(active),
            "injectedPages": active,
            "newlyInjectedPageCount": len(newly_injected),
            "newlyInjectedPages": newly_injected,
            "volatileCopyReplacements": int(previous.get("volatileCopyReplacements", 0))
            + replacements,
            "personalProfilePublished": False,
            "personalContactPublished": False,
        }
        release_path.write_text(
            json.dumps(release, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    _checksums(site)
    return {
        "ok": True,
        "version": VERSION,
        "basePath": base,
        "policyPath": POLICY_PATH,
        "injectedPageCount": len(active),
        "newlyInjectedPageCount": len(newly_injected),
        "volatileCopyReplacements": replacements,
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
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


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


def _has_institutional_editor(docs: list[object]) -> bool:
    for doc in docs:
        for node in _walk(doc):
            editor = node.get("editor")
            if isinstance(editor, dict) and editor.get("@id") == ORGANIZATION_ID:
                return editor.get("@type") in {None, "Organization"}
    return False


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
            if f"{parsed.scheme}://{parsed.netloc}" != HOST:
                errors.append(f"Sitemap origin yanlış: {node.text.strip()}")
            else:
                paths.add(_path(parsed.path))
    return paths


def _contracts(repo: Path, sitemap: set[str], errors: list[str]) -> dict:
    metrics: dict[str, int] = {}
    specs = (
        ("intent-registry-v219.json", "intents", "intentCount", 15),
        ("ai-citation-benchmark-v219.json", "queries", "queryCount", 15),
    )
    for filename, key, metric, minimum in specs:
        path = repo / "alo186/aeo" / filename
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{filename} geçersiz/eksik: {exc}")
            continue
        items = payload.get(key, [])
        if payload.get("version") != VERSION or not isinstance(items, list) or len(items) < minimum:
            errors.append(f"{filename} sürüm/adet sözleşmesi başarısız")
            continue
        if payload.get("policy", {}).get("personalProfilesAllowed") is True:
            errors.append(f"{filename} kişisel profil politikasını ihlal ediyor")

        identifiers: set[str] = set()
        texts: set[str] = set()
        targets: set[str] = set()
        for item in items:
            identifier = str(item.get("intentId") or item.get("id") or "").strip()
            text = str(item.get("question") or item.get("query") or "").strip().casefold()
            target = _path(str(item.get("canonicalPath") or item.get("expectedPath") or ""))
            if not identifier or not text or identifier in identifiers or text in texts:
                errors.append(f"{filename} yinelenen/eksik kayıt: {identifier}")
            if key == "intents" and target in targets:
                errors.append(f"{filename} aynı canonical cevabı yineliyor: {target}")
            if target not in sitemap:
                errors.append(f"{filename} hedefi sitemapte yok: {target}")
            identifiers.add(identifier)
            texts.add(text)
            targets.add(target)
        metrics[metric] = len(identifiers)
    return metrics


def validate(site: Path, repo_root: Path, require_release_proof: bool = False) -> dict:
    site = site.resolve()
    repo_root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    sitemap = _sitemap(site, errors)

    try:
        robots = (site / "robots.txt").read_text(encoding="utf-8").casefold()
    except OSError as exc:
        robots = ""
        errors.append(f"robots.txt eksik: {exc}")
    if "user-agent: *" not in robots or "allow: /" not in robots:
        errors.append("robots genel tarama izni eksik")
    if f"sitemap: {HOST}/sitemap.xml" not in robots:
        errors.append("robots canonical sitemap eksik")
    if re.search(r"user-agent:\s*oai-searchbot[\s\S]{0,300}disallow:\s*/(?:\s|$)", robots):
        errors.append("OAI-SearchBot tamamen engellenmiş")

    metrics = _contracts(repo_root, sitemap, errors)
    pages: list[dict] = []
    for route in CRITICAL:
        path = _file(site, route)
        page_errors: list[str] = []
        if not path.is_file():
            errors.append(f"Kritik AEO sayfası eksik: {route}")
            pages.append({"path": route, "errors": ["eksik"]})
            continue

        html = path.read_text(encoding="utf-8", errors="ignore")
        head = _head(html)
        docs = _jsonld(html, page_errors, route)
        h1 = H1_RE.findall(html)
        parsed = urlsplit(head.canonical)
        if len(head.title) < 12:
            page_errors.append("title eksik/kısa")
        if len(head.description.strip()) < 50:
            page_errors.append("description eksik/kısa")
        if len(h1) != 1:
            page_errors.append(f"H1 sayısı {len(h1)}")
        if not head.lang:
            page_errors.append("html lang eksik")
        if f"{parsed.scheme}://{parsed.netloc}" != HOST or _path(parsed.path) != _path(route):
            page_errors.append(f"canonical uyumsuz: {head.canonical}")
        if not docs:
            page_errors.append("JSON-LD eksik")
        if PERSONAL_SCHEMA_RE.search(html):
            page_errors.append("kişisel profil veya Person schema bulundu")

        if route == POLICY_PATH:
            if not {"Organization", "WebPage"}.issubset(_types(docs)):
                page_errors.append("Organization/WebPage schema eksik")
            folded = html.casefold()
            for token in (
                "kurumsal yayın denetimi",
                "dogrulama-yontemi",
                "kişisel isim",
                "bağımsız bilgilendirme platformudur",
            ):
                if token.casefold() not in folded:
                    page_errors.append(f"yayın politikası bilgisi eksik: {token}")
        else:
            h1_match = H1_RE.search(html)
            answer = None
            if h1_match:
                answer = P_RE.search(html[h1_match.end() : h1_match.end() + 5000])
            if len(_text(answer.group(1)) if answer else "") < 60:
                page_errors.append("alınabilir doğrudan cevap kısa/eksik")
            if MARKER not in html:
                page_errors.append("kurumsal yayın denetimi görünür değil")
            if not _has_institutional_editor(docs):
                page_errors.append("WebPage.editor Organization eksik")

        errors.extend(f"{route}: {item}" for item in page_errors)
        pages.append({"path": route, "errors": page_errors, "title": head.title})

    release: dict = {}
    release_path = site / "pages-release.json"
    if release_path.is_file():
        try:
            release = json.loads(release_path.read_text(encoding="utf-8")).get(
                "aeoInstitutional", {}
            )
        except json.JSONDecodeError as exc:
            errors.append(f"pages-release geçersiz: {exc}")
    elif require_release_proof:
        errors.append("pages-release kanıtı eksik")

    if require_release_proof:
        valid_release = (
            release.get("version") == VERSION
            and release.get("policyCanonical") == POLICY_URL
            and release.get("editorType") == "Organization"
            and release.get("personalProfilePublished") is False
            and release.get("personalContactPublished") is False
        )
        if not valid_release:
            errors.append("AEO kurumsal release kanıtı eksik/yanlış")

    score = max(0, 100 - min(80, len(errors) * 7) - min(20, len(warnings) * 2))
    return {
        "ok": not errors,
        "version": VERSION,
        "score": score,
        "metrics": {
            "sitemapPathCount": len(sitemap),
            "criticalPageCount": len(CRITICAL),
            "criticalPagePassCount": sum(not page["errors"] for page in pages),
            **metrics,
        },
        "pages": pages,
        "release": release,
        "warnings": warnings,
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    inject_parser = sub.add_parser("inject")
    inject_parser.add_argument("--site", type=Path, required=True)
    inject_parser.add_argument("--base-path", default="")

    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("--site", type=Path, required=True)
    validate_parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    validate_parser.add_argument("--report", type=Path)
    validate_parser.add_argument("--require-release-proof", action="store_true")

    args = parser.parse_args()
    if args.command == "inject":
        report = inject(args.site, args.base_path)
    else:
        report = validate(args.site, args.repo_root, args.require_release_proof)

    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if getattr(args, "report", None):
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
