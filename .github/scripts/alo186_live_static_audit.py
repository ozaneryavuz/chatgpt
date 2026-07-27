#!/usr/bin/env python3
import concurrent.futures
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

ORIGIN = "https://www.alo186.com"
OUT = Path("artifacts/live-quality")
OUT.mkdir(parents=True, exist_ok=True)
CTX = ssl.create_default_context()
UA = "ALO186-Quality-Audit/1.0"


def normalized(value, base=ORIGIN):
    try:
        url = urllib.parse.urljoin(base, value)
        parts = urllib.parse.urlsplit(url)
        return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path or "/", parts.query, ""))
    except Exception:
        return None


def same_site(url):
    try:
        return urllib.parse.urlsplit(url).hostname in {"alo186.com", "www.alo186.com"}
    except Exception:
        return False


def fetch(url, timeout=20):
    started = time.time()
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xml,text/plain,*/*"})
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=CTX) as response:
            body = response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")
            return {"requested": url, "final": response.geturl(), "status": response.status, "headers": dict(response.headers.items()), "body": body, "ms": round((time.time()-started)*1000)}
    except urllib.error.HTTPError as exc:
        return {"requested": url, "final": exc.geturl(), "status": exc.code, "headers": dict(exc.headers.items()), "body": exc.read().decode("utf-8", errors="replace"), "ms": round((time.time()-started)*1000), "error": str(exc)}
    except Exception as exc:
        return {"requested": url, "final": None, "status": 0, "headers": {}, "body": "", "ms": round((time.time()-started)*1000), "error": str(exc)}


class PageParser(HTMLParser):
    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base = base
        self.title = ""
        self.in_title = False
        self.h1 = 0
        self.links = []
        self.images = []
        self.canonical = None
        self.description = None
        self.robots = None
        self.viewport = None
        self.lang = None
        self.ids = []
        self.jsonld = []
        self.in_jsonld = False
        self.jsonld_buffer = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "html": self.lang = values.get("lang")
        if tag == "title": self.in_title = True
        if tag == "h1": self.h1 += 1
        if values.get("id"): self.ids.append(values["id"])
        if tag == "a" and values.get("href"):
            url = normalized(values["href"], self.base)
            if url: self.links.append(url)
        if tag == "img":
            self.images.append({"src": normalized(values.get("src", ""), self.base), "alt": values.get("alt"), "width": values.get("width"), "height": values.get("height"), "loading": values.get("loading")})
        if tag == "link" and "canonical" in (values.get("rel") or "").lower():
            self.canonical = normalized(values.get("href", ""), self.base)
        if tag == "meta":
            name = (values.get("name") or "").lower()
            if name == "description": self.description = values.get("content")
            if name == "robots": self.robots = values.get("content")
            if name == "viewport": self.viewport = values.get("content")
        if tag == "script" and (values.get("type") or "").lower() == "application/ld+json":
            self.in_jsonld = True
            self.jsonld_buffer = []

    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False
        if tag == "script" and self.in_jsonld:
            self.jsonld.append("".join(self.jsonld_buffer).strip())
            self.in_jsonld = False

    def handle_data(self, data):
        if self.in_title: self.title += data
        if self.in_jsonld: self.jsonld_buffer.append(data)


def parse_page(result):
    parser = PageParser(result.get("final") or result["requested"])
    try: parser.feed(result.get("body", ""))
    except Exception: pass
    duplicate_ids = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
    json_errors, types = [], []
    for index, raw in enumerate(parser.jsonld):
        if not raw: continue
        try:
            value = json.loads(raw)
            nodes = value if isinstance(value, list) else value.get("@graph", [value]) if isinstance(value, dict) else []
            for node in nodes:
                kind = node.get("@type") if isinstance(node, dict) else None
                if isinstance(kind, list): types.extend(kind)
                elif kind: types.append(kind)
        except Exception as exc:
            json_errors.append({"index": index, "error": str(exc)})
    headers = {key.lower(): value for key, value in result.get("headers", {}).items()}
    return {
        "requested": result["requested"], "final": result.get("final"), "status": result["status"], "ms": result["ms"],
        "content_type": headers.get("content-type"), "cache_control": headers.get("cache-control"),
        "hsts": headers.get("strict-transport-security"), "nosniff": headers.get("x-content-type-options"),
        "csp": headers.get("content-security-policy"), "referrer_policy": headers.get("referrer-policy"),
        "title": parser.title.strip(), "description": (parser.description or "").strip(), "canonical": parser.canonical,
        "robots": parser.robots, "viewport": parser.viewport, "lang": parser.lang, "h1_count": parser.h1,
        "duplicate_ids": duplicate_ids, "links": sorted(set(parser.links)), "images": parser.images,
        "jsonld_count": len(parser.jsonld), "jsonld_types": sorted(set(types)), "jsonld_errors": json_errors,
        "tailwind_import": bool(re.search(r"@import\s+[\"']tailwindcss[\"']", result.get("body", ""), re.I)),
        "bytes": len(result.get("body", "").encode("utf-8")), "error": result.get("error")
    }


def sitemap_urls():
    robots = fetch(f"{ORIGIN}/robots.txt")
    seeds = re.findall(r"^\s*Sitemap:\s*(\S+)", robots.get("body", ""), re.I | re.M)
    seeds += [f"{ORIGIN}/sitemap.xml", f"{ORIGIN}/sitemap_index.xml"]
    queue, visited, pages, maps = list(dict.fromkeys(seeds)), set(), set(), []
    while queue and len(visited) < 30:
        url = normalized(queue.pop(0))
        if not url or url in visited: continue
        visited.add(url)
        result = fetch(url)
        locs = []
        try:
            root = ElementTree.fromstring(result.get("body", ""))
            locs = [normalized(node.text or "", url) for node in root.iter() if node.tag.endswith("loc")]
        except Exception: pass
        locs = [item for item in locs if item]
        nested = [item for item in locs if "sitemap" in urllib.parse.urlsplit(item).path.lower()]
        for item in nested: queue.append(item)
        for item in locs:
            if item not in nested and same_site(item): pages.add(item)
        maps.append({"url": url, "status": result["status"], "final": result.get("final"), "content_type": result.get("headers", {}).get("Content-Type"), "loc_count": len(locs), "page_count": len([x for x in locs if x not in nested]), "nested_count": len(nested), "error": result.get("error")})
    return robots, maps, sorted(pages)


robots, maps, listed = sitemap_urls()
fallback = [f"{ORIGIN}/", f"{ORIGIN}/elektrik-kesintisi", f"{ORIGIN}/elektrik-portali", f"{ORIGIN}/il/mugla", f"{ORIGIN}/haberler", f"{ORIGIN}/iletisim", f"{ORIGIN}/acil-numaralar", f"{ORIGIN}/yasal/gizlilik"]
urls = list(dict.fromkeys([f"{ORIGIN}/"] + listed + fallback))[:500]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    pages = list(pool.map(lambda url: parse_page(fetch(url)), urls))
link_urls = sorted({url for page in pages for url in page["links"] if same_site(url)})[:1500]
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
    link_results = list(pool.map(fetch, link_urls))

issues = []
def issue(level, category, url, message, evidence=None): issues.append({"level": level, "category": category, "url": url, "message": message, "evidence": evidence})
if robots["status"] != 200: issue("P0", "indexability", f"{ORIGIN}/robots.txt", f"robots.txt HTTP {robots['status']}")
if not re.search(r"^\s*Sitemap:", robots.get("body", ""), re.I | re.M): issue("P1", "indexability", f"{ORIGIN}/robots.txt", "Sitemap yönergesi eksik")
if not any(item["status"] == 200 and item["page_count"] for item in maps): issue("P0", "indexability", f"{ORIGIN}/sitemap.xml", "Geçerli ve URL içeren sitemap bulunamadı")
listed_norm = {normalized(url) for url in listed}
for page in pages:
    url = page.get("final") or page["requested"]
    if page["status"] < 200 or page["status"] >= 400: issue("P0" if not page["status"] or page["status"] >= 500 else "P1", "http", page["requested"], f"HTTP {page['status'] or 'error'}")
    if 200 <= page["status"] < 400:
        if not page["title"]: issue("P1", "seo", url, "Title eksik")
        if not page["description"]: issue("P2", "seo", url, "Meta description eksik")
        if not page["canonical"]: issue("P1", "canonical", url, "Canonical eksik")
        elif not same_site(page["canonical"]): issue("P0", "canonical", url, "Canonical site dışına işaret ediyor", page["canonical"])
        elif urllib.parse.urlsplit(page["canonical"]).hostname != "www.alo186.com": issue("P1", "canonical", url, "Canonical www standardına uymuyor", page["canonical"])
        if page["robots"] and "noindex" in page["robots"].lower() and normalized(page["requested"]) in listed_norm: issue("P0", "indexability", url, "Sitemap içindeki sayfa noindex")
        if not page["viewport"]: issue("P1", "mobile", url, "Viewport meta etiketi eksik")
        if page["h1_count"] != 1: issue("P1", "semantics", url, f"H1 sayısı {page['h1_count']}")
        if page["duplicate_ids"]: issue("P2", "accessibility", url, "Tekrarlanan id değerleri", page["duplicate_ids"])
        if page["jsonld_errors"]: issue("P1", "schema", url, "Geçersiz JSON-LD", page["jsonld_errors"])
        if any(image["alt"] is None for image in page["images"]): issue("P2", "accessibility", url, "Alt niteliği olmayan görsel")
        if any(image["src"] and (not image["width"] or not image["height"]) for image in page["images"]): issue("P2", "performance", url, "Boyut bilgisi olmayan görsel")
        if page["tailwind_import"]: issue("P0", "performance", url, "Çözümlenemeyen Tailwind importu")
        if not page["hsts"]: issue("P2", "headers", url, "HSTS eksik")
        if not page["nosniff"]: issue("P2", "headers", url, "X-Content-Type-Options eksik")
for result in link_results:
    if result["status"] == 0 or result["status"] >= 400: issue("P0" if not result["status"] or result["status"] >= 500 else "P1", "broken-link", result["requested"], f"İç bağlantı HTTP {result['status'] or 'error'}", result.get("error"))
order = {"P0": 0, "P1": 1, "P2": 2}
issues.sort(key=lambda item: (order.get(item["level"], 9), item["category"], item["url"]))
report = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "origin": ORIGIN, "counts": {"sitemap_pages": len(listed), "crawled_pages": len(pages), "links": len(link_results), "P0": sum(x["level"]=="P0" for x in issues), "P1": sum(x["level"]=="P1" for x in issues), "P2": sum(x["level"]=="P2" for x in issues)}, "robots": {"status": robots["status"], "final": robots.get("final"), "body": robots.get("body", "")[:5000]}, "sitemaps": maps, "pages": pages, "links": [{"requested": x["requested"], "final": x.get("final"), "status": x["status"], "ms": x["ms"], "error": x.get("error")} for x in link_results], "issues": issues}
(OUT / "static-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
lines = ["# ALO186 canlı statik kalite denetimi", "", f"- Sitemap URL: {len(listed)}", f"- Taranan sayfa: {len(pages)}", f"- İç bağlantı: {len(link_results)}", f"- Sorun: P0 {report['counts']['P0']}, P1 {report['counts']['P1']}, P2 {report['counts']['P2']}", "", "## Öncelikli sorunlar", ""]
lines += [f"- **{item['level']} · {item['category']}** — {item['message']} — {item['url']}" for item in issues[:150]]
(OUT / "static-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
