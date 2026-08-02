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

VERSION = 216
HOST = "https://alo186.com"
PROFILE_PATH = "/uzman/ozan-eryavuz"
PROFILE_URL = HOST + PROFILE_PATH
PERSON_ID = PROFILE_URL + "#person"
MARKER = 'data-alo186-authority-v216="true"'
STYLE_MARKER = 'data-alo186-authority-style-v216="true"'
SCHEMA_MARKER = 'data-alo186-authority-schema-v216="true"'
ASSET = "assets/aeo-authority-v216.css"
CSS_SOURCE = Path(__file__).resolve().with_name("aeo-authority-v216.css")
PREFIXES = ("haberler/", "sektor-rehberi/", "il/")
EXACT = {
    "index.html", "elektrik-portali/index.html", "elektrik-kesintisi/index.html",
    "edas-bul/index.html", "acil-numaralar/index.html", "hakkimizda/index.html",
    "kaynaklar/index.html", "hesaplama/index.html", "amazon-elektrik-urunleri/index.html",
    "hesaplama/ups-suresi/index.html", "hesaplama/jenerator-gucu-secimi/index.html",
    "hesaplama/ev-sarj-uygunluk/index.html", "hesaplama/gerilim-koruma-cozum-secici/index.html",
    "hesaplama/yedek-guc-cozum-secici/index.html",
}
CRITICAL = (
    "/elektrik-portali", "/edas-bul", "/elektrik-kesintisi", "/acil-numaralar",
    "/haberler/planli-elektrik-kesintisi-ne-kadar-once-bildirilir",
    "/hesaplama/yedek-guc-cozum-secici/",
    "/haberler/ges-elektrik-kesintisinde-calisir-mi",
    "/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu",
    "/haberler/topraklama-direnci-kac-ohm-olmali", PROFILE_PATH,
)
REPLACEMENTS = (
    ("50+ elektrik ürünü için Amazon seçim kartları", "Elektrik ürünleri için teknik seçim kartları"),
    ("50+ elektrik ürünü", "Elektrik ürünleri"),
    ("25 rehberin tamamını gör", "Tüm ürün rehberlerini gör"),
)
CANONICAL_RE = re.compile(r'<link\b[^>]*\brel=["\']canonical["\'][^>]*\bhref=["\']([^"\']+)["\'][^>]*>|<link\b[^>]*\bhref=["\']([^"\']+)["\'][^>]*\brel=["\']canonical["\'][^>]*>', re.I)
TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.I | re.S)
DESC_RE = re.compile(r'<meta\b[^>]*\bname=["\']description["\'][^>]*\bcontent=["\']([^"\']*)["\'][^>]*>|<meta\b[^>]*\bcontent=["\']([^"\']*)["\'][^>]*\bname=["\']description["\'][^>]*>', re.I)
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
P_RE = re.compile(r"<p\b[^>]*>(.*?)</p>", re.I | re.S)
LD_RE = re.compile(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")


def _base(value: str) -> str:
    value = (value or "").strip()
    return "" if value in {"", "/"} else "/" + value.strip("/")


def _public(base: str, path: str) -> str:
    return _base(base) + "/" + path.lstrip("/")


def _text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(TAG_RE.sub(" ", value))).strip()


def _path(value: str) -> str:
    value = "/" + (value or "").strip().strip("/")
    return "/" if value == "/" else value


def _file(site: Path, route: str) -> Path:
    route = _path(route)
    return site / "index.html" if route == "/" else site / route.strip("/") / "index.html"


def _canonical(html: str) -> str:
    match = CANONICAL_RE.search(html)
    return next((group for group in match.groups() if group), "").strip() if match else ""


def _eligible(relative: str) -> bool:
    return relative != "uzman/ozan-eryavuz/index.html" and (relative in EXACT or relative.startswith(PREFIXES))


def _schema(canonical: str) -> str:
    payload = {
        "@context": "https://schema.org", "@type": "WebPage",
        "@id": canonical.rstrip("/") + "#webpage",
        "editor": {"@type": "Person", "@id": PERSON_ID, "name": "Ozan Eryavuz",
                   "jobTitle": "Elektrik-Elektronik Mühendisi", "url": PROFILE_URL},
    }
    return f'<script type="application/ld+json" {SCHEMA_MARKER}>' + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "</script>"


def _block(base: str) -> str:
    href = _public(base, PROFILE_PATH)
    return f'''<aside class="alo-authority-v216" {MARKER} aria-label="Teknik yayın sorumluluğu">
  <div class="alo-authority-v216__identity"><span>Teknik yayın sorumlusu</span><strong><a href="{href}">Ozan Eryavuz</a></strong><p>Elektrik-Elektronik Mühendisi · kaynak, güvenlik sınırı ve güncellik süreci</p></div>
  <a class="alo-authority-v216__method" href="{href}#yayin-yontemi">Uzmanlık ve yayın yöntemi</a>
</aside>'''


def _finish(html: str) -> str:
    html = html.rstrip()
    folded = html.casefold()
    if "</body>" not in folded and "</html>" in folded:
        pos = folded.rfind("</html>")
        html = html[:pos].rstrip() + "\n</body>\n" + html[pos:]
    elif "</body>" not in folded:
        html += "\n</body>"
    if "</html>" not in html.casefold():
        html += "\n</html>"
    return html + "\n"


def _inject_page(path: Path, site: Path, base: str) -> tuple[bool, int]:
    html = path.read_text(encoding="utf-8")
    relative = path.relative_to(site).as_posix()
    changed_copy = 0
    if relative in {"index.html", "elektrik-portali/index.html"}:
        for old, new in REPLACEMENTS:
            count = html.count(old)
            html = html.replace(old, new)
            changed_copy += count
    if MARKER in html:
        if changed_copy:
            path.write_text(_finish(html), encoding="utf-8")
        return False, changed_copy
    canonical = _canonical(html)
    if not canonical or "<body" not in html.casefold():
        raise RuntimeError(f"AEO v216 canonical/body eksik: {relative}")
    link = f'<link rel="stylesheet" href="{_public(base, ASSET)}" {STYLE_MARKER}>'
    head = html.casefold().find("</head>")
    if head < 0:
        raise RuntimeError(f"AEO v216 </head> eksik: {relative}")
    html = html[:head] + link + "\n" + _schema(canonical) + "\n" + html[head:]
    point = html.casefold().rfind("</main>")
    if point < 0:
        point = html.casefold().rfind("</body>")
    if point < 0:
        point = len(html)
    html = html[:point] + "\n" + _block(base) + "\n" + html[point:]
    path.write_text(_finish(html), encoding="utf-8")
    return True, changed_copy


def _checksums(site: Path) -> None:
    target = site / "checksums.sha256"
    if not target.exists():
        return
    target.unlink()
    files = sorted(path for path in site.rglob("*") if path.is_file())
    target.write_text("\n".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(site).as_posix()}" for path in files) + "\n", encoding="utf-8")


def inject(site: Path, base: str = "") -> dict:
    site = site.resolve(); base = _base(base)
    if not site.is_dir() or not CSS_SOURCE.is_file():
        raise FileNotFoundError("AEO v216 site veya CSS kaynağı eksik")
    asset = site / ASSET; asset.parent.mkdir(parents=True, exist_ok=True)
    asset.write_text(CSS_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
    new: list[str] = []; replacements = 0
    for path in sorted(site.rglob("index.html")):
        relative = path.relative_to(site).as_posix()
        if _eligible(relative):
            changed, count = _inject_page(path, site, base)
            replacements += count
            if changed: new.append(relative)
    active = [p.relative_to(site).as_posix() for p in sorted(site.rglob("index.html")) if _eligible(p.relative_to(site).as_posix()) and MARKER in p.read_text(encoding="utf-8", errors="ignore")]
    if not active:
        raise RuntimeError("AEO v216 hiçbir sayfaya uygulanamadı")
    release_path = site / "pages-release.json"
    if release_path.is_file():
        release = json.loads(release_path.read_text(encoding="utf-8"))
        previous = release.get("aeoAuthority") if isinstance(release.get("aeoAuthority"), dict) else {}
        release["aeoAuthority"] = {
            "version": VERSION, "basePath": base, "profile": PROFILE_PATH,
            "profileCanonical": PROFILE_URL, "editorName": "Ozan Eryavuz",
            "editorRole": "Elektrik-Elektronik Mühendisi", "schemaProperty": "editor",
            "injectedPageCount": len(active), "injectedPages": active,
            "newlyInjectedPageCount": len(new), "newlyInjectedPages": new,
            "volatileCopyReplacements": int(previous.get("volatileCopyReplacements", 0)) + replacements,
            "personalContactPublished": False,
        }
        release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _checksums(site)
    return {"ok": True, "version": VERSION, "basePath": base, "profile": PROFILE_PATH,
            "injectedPageCount": len(active), "newlyInjectedPageCount": len(new),
            "volatileCopyReplacements": replacements}


class _Head(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True); self.title=[]; self.in_title=False; self.lang=""; self.description=""; self.canonical=""
    def handle_starttag(self, tag, attrs):
        data = {k.casefold(): unescape(v or "") for k, v in attrs}; tag = tag.casefold()
        if tag == "html": self.lang = data.get("lang", "")
        elif tag == "title": self.in_title = True
        elif tag == "meta" and data.get("name", "").casefold() == "description": self.description = data.get("content", "")
        elif tag == "link" and "canonical" in data.get("rel", "").casefold().split(): self.canonical = data.get("href", "")
    def handle_endtag(self, tag):
        if tag.casefold() == "title": self.in_title = False
    def handle_data(self, data):
        if self.in_title: self.title.append(data)


def _jsonld(html: str, errors: list[str], label: str) -> list[object]:
    docs=[]
    for i, raw in enumerate(LD_RE.findall(html), 1):
        try: docs.append(json.loads(unescape(raw.strip())))
        except json.JSONDecodeError as exc: errors.append(f"{label}: JSON-LD {i} geçersiz: {exc}")
    return docs


def _walk(value):
    if isinstance(value, dict):
        yield value
        for item in value.values(): yield from _walk(item)
    elif isinstance(value, list):
        for item in value: yield from _walk(item)


def _types(docs: list[object]) -> set[str]:
    result=set()
    for doc in docs:
        for node in _walk(doc):
            value=node.get("@type")
            if isinstance(value, str): result.add(value)
            elif isinstance(value, list): result.update(map(str, value))
    return result


def _has_editor(docs: list[object]) -> bool:
    return any(isinstance(node.get("editor"), dict) and node["editor"].get("@id") == PERSON_ID for doc in docs for node in _walk(doc))


def _sitemap(site: Path, errors: list[str]) -> set[str]:
    try: root = ET.fromstring((site / "sitemap.xml").read_text(encoding="utf-8"))
    except (OSError, ET.ParseError) as exc: errors.append(f"sitemap.xml geçersiz/eksik: {exc}"); return set()
    paths=set()
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] == "loc" and node.text:
            parsed=urlsplit(node.text.strip())
            if f"{parsed.scheme}://{parsed.netloc}" != HOST: errors.append(f"Sitemap origin yanlış: {node.text.strip()}")
            else: paths.add(_path(parsed.path))
    return paths


def _contracts(repo: Path, sitemap: set[str], errors: list[str]) -> dict:
    result={}
    for name, key, min_count in (("intent-registry-v216.json", "intents", 15), ("ai-citation-benchmark-v216.json", "queries", 15)):
        path=repo / "alo186/aeo" / name
        try: payload=json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc: errors.append(f"{name} geçersiz/eksik: {exc}"); continue
        items=payload.get(key, [])
        if payload.get("version") != VERSION or not isinstance(items, list) or len(items) < min_count: errors.append(f"{name} sürüm/adet sözleşmesi başarısız")
        ids=set(); targets=set(); texts=set()
        for item in items:
            ident=str(item.get("intentId") or item.get("id") or "").strip(); target=_path(str(item.get("canonicalPath") or item.get("expectedPath") or "")); text=str(item.get("question") or item.get("query") or "").strip().casefold()
            if not ident or not text or ident in ids or text in texts: errors.append(f"{name} yinelenen/eksik kayıt: {ident}")
            if target in targets and key == "intents": errors.append(f"{name} aynı canonical cevabı yineliyor: {target}")
            if target not in sitemap: errors.append(f"{name} hedefi sitemapte yok: {target}")
            ids.add(ident); texts.add(text); targets.add(target)
        result["intentCount" if key == "intents" else "queryCount"] = len(ids)
    return result


def validate(site: Path, repo_root: Path, require_release_proof: bool = False) -> dict:
    site=site.resolve(); repo_root=repo_root.resolve(); errors=[]; warnings=[]
    sitemap=_sitemap(site, errors)
    try: robots=(site / "robots.txt").read_text(encoding="utf-8").casefold()
    except OSError as exc: robots=""; errors.append(f"robots.txt eksik: {exc}")
    if "user-agent: *" not in robots or "allow: /" not in robots: errors.append("robots genel tarama izni eksik")
    if f"sitemap: {HOST}/sitemap.xml" not in robots: errors.append("robots canonical sitemap eksik")
    if re.search(r"user-agent:\s*oai-searchbot[\s\S]{0,300}disallow:\s*/(?:\s|$)", robots): errors.append("OAI-SearchBot tamamen engellenmiş")
    metrics=_contracts(repo_root, sitemap, errors)
    page_results=[]
    for route in CRITICAL:
        path=_file(site, route); page_errors=[]
        if not path.is_file(): errors.append(f"Kritik AEO sayfası eksik: {route}"); page_results.append({"path":route,"errors":["eksik"]}); continue
        html=path.read_text(encoding="utf-8", errors="ignore"); parser=_Head(); parser.feed(html); parser.close(); docs=_jsonld(html, page_errors, route)
        title=_text(" ".join(parser.title)); h1=H1_RE.findall(html); canonical=parser.canonical; parsed=urlsplit(canonical)
        if len(title) < 12: page_errors.append("title eksik/kısa")
        if len(parser.description.strip()) < 50: page_errors.append("description eksik/kısa")
        if len(h1) != 1: page_errors.append(f"H1 sayısı {len(h1)}")
        if not parser.lang: page_errors.append("html lang eksik")
        if f"{parsed.scheme}://{parsed.netloc}" != HOST or _path(parsed.path) != _path(route): page_errors.append(f"canonical uyumsuz: {canonical}")
        if not docs: page_errors.append("JSON-LD eksik")
        if route == PROFILE_PATH:
            types=_types(docs)
            if not {"Person","ProfilePage"}.issubset(types): page_errors.append("Person/ProfilePage schema eksik")
            folded_html = html.casefold()
            for token in ("Ozan Eryavuz","Elektrik-Elektronik Mühendisi","yayin-yontemi","Bağımsız bilgilendirme platformudur"):
                if token.casefold() not in folded_html: page_errors.append(f"profil bilgisi eksik: {token}")
        else:
            answer_match=P_RE.search(html[H1_RE.search(html).end():H1_RE.search(html).end()+5000]) if H1_RE.search(html) else None
            if len(_text(answer_match.group(1)) if answer_match else "") < 60: page_errors.append("alınabilir doğrudan cevap kısa/eksik")
            if MARKER not in html: page_errors.append("görünür teknik sorumlu eksik")
            if not _has_editor(docs): page_errors.append("WebPage.editor Person eksik")
        errors.extend(f"{route}: {item}" for item in page_errors)
        page_results.append({"path":route,"errors":page_errors,"title":title})
    release={}
    release_path = site / "pages-release.json"
    if release_path.is_file():
        try:
            release=json.loads(release_path.read_text(encoding="utf-8")).get("aeoAuthority", {})
        except json.JSONDecodeError as exc:
            errors.append(f"pages-release geçersiz: {exc}")
    elif require_release_proof:
        errors.append("pages-release kanıtı eksik")
    if require_release_proof and (release.get("version") != VERSION or release.get("profileCanonical") != PROFILE_URL or release.get("personalContactPublished") is not False):
        errors.append("AEO release kanıtı eksik/yanlış")
    score=max(0,100-min(80,len(errors)*7)-min(20,len(warnings)*2))
    return {"ok":not errors,"version":VERSION,"score":score,"metrics":{"sitemapPathCount":len(sitemap),"criticalPageCount":len(CRITICAL),"criticalPagePassCount":sum(not p["errors"] for p in page_results),**metrics},"pages":page_results,"release":release,"warnings":warnings,"errors":errors}


def main() -> None:
    parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest="command", required=True)
    add=sub.add_parser("inject"); add.add_argument("--site", type=Path, required=True); add.add_argument("--base-path", default="")
    check=sub.add_parser("validate"); check.add_argument("--site", type=Path, required=True); check.add_argument("--repo-root", type=Path, default=Path.cwd()); check.add_argument("--report", type=Path); check.add_argument("--require-release-proof", action="store_true")
    args=parser.parse_args()
    report=inject(args.site,args.base_path) if args.command=="inject" else validate(args.site,args.repo_root,args.require_release_proof)
    rendered=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if getattr(args,"report",None): args.report.parent.mkdir(parents=True,exist_ok=True); args.report.write_text(rendered,encoding="utf-8")
    print(rendered,end="")
    if not report["ok"]: raise SystemExit(1)


if __name__ == "__main__": main()
