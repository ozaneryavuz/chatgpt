from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import Browser, Page, sync_playwright

APEX = "https://alo186.com"
WWW = "https://www.alo186.com"
DEFAULT_OUTPUT = Path("/tmp/alo186-live-technical-audit")
KEY_ROUTES = (
    "/",
    "/elektrik-kesintisi",
    "/elektrik-durum-merkezi",
    "/elektrik-portali",
    "/edas-bul",
    "/karar-motoru",
    "/akilli-urun-secimi",
    "/amazon-elektrik-urunleri",
    "/urun-bilgi-grafigi/",
    "/hesaplama/",
    "/hesaplama/home-office-internet-sureklilik-plani/",
    "/hesaplama/aydinlatma-ihtiyac-ve-ampul-uygunluk/",
    "/hesaplama/kesinti-hazirlik-envanteri/",
    "/haberler/ups-eco-modu-online-cift-cevrim-farki",
    "/sektor-rehberi/elektrik-sayaci-arizasi",
)
DEVICES = {
    "mobile": {"viewport": {"width": 390, "height": 844}, "device_scale_factor": 1, "is_mobile": True, "has_touch": True},
    "desktop": {"viewport": {"width": 1440, "height": 900}, "device_scale_factor": 1, "is_mobile": False, "has_touch": False},
}
PERSONAL_DATA_RE = re.compile(
    r"(?:^|[-_\s])(ad|soyad|isim|name|email|e-posta|mail|telefon|phone|tel|adres|address|tc|kimlik|abone|subscriber|saya[cç]|plaka)(?:$|[-_\s])",
    re.IGNORECASE,
)
OFFICIAL_IMPERSONATION_RE = re.compile(
    r"(?:resm[iî]\s+(?:edaş|dağıtım|başvuru|ihbar|kayıt)\s+(?:merkezi|kanalı|formu)|edaş\s+resm[iî]\s+sitesi|kamu\s+kurumu\s+olarak)",
    re.IGNORECASE,
)
FORBIDDEN_COMMERCE_SCHEMA = {"Offer", "AggregateOffer"}


@dataclass
class Finding:
    severity: str
    check: str
    message: str
    url: str | None = None
    device: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


class Audit:
    def __init__(self, output: Path) -> None:
        self.output = output
        self.output.mkdir(parents=True, exist_ok=True)
        (self.output / "screenshots").mkdir(exist_ok=True)
        self.findings: list[Finding] = []
        self.results: dict[str, Any] = {
            "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "origins": {},
            "robots": {},
            "sitemap": {},
            "pages": [],
            "pageSpeed": {},
        }
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ALO186-Live-Technical-Audit/1.0 (+https://alo186.com)",
            "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.7",
        })

    def add(self, severity: str, check: str, message: str, *, url: str | None = None, device: str | None = None, **evidence: Any) -> None:
        self.findings.append(Finding(severity, check, message, url, device, evidence))

    def request(self, url: str, *, allow_redirects: bool = True, timeout: int = 30) -> requests.Response | None:
        try:
            return self.session.get(url, allow_redirects=allow_redirects, timeout=timeout)
        except requests.RequestException as exc:
            self.add("P1", "http", f"HTTP isteği başarısız: {exc}", url=url)
            return None

    def audit_origins(self) -> str:
        candidates = [
            "http://alo186.com/",
            "http://www.alo186.com/",
            "https://alo186.com/",
            "https://www.alo186.com/",
        ]
        final_hosts: Counter[str] = Counter()
        for url in candidates:
            response = self.request(url)
            if response is None:
                continue
            chain = [{"status": item.status_code, "url": item.url, "location": item.headers.get("location")} for item in response.history]
            final = {"status": response.status_code, "url": response.url, "chain": chain}
            self.results["origins"][url] = final
            host = urlsplit(response.url).netloc.lower()
            if response.status_code == 200:
                final_hosts[host] += 1
            if response.status_code != 200:
                self.add("P1", "redirect", f"Alan adı zinciri 200 ile sonuçlanmadı ({response.status_code}).", url=url, chain=chain, final=response.url)
            if len(response.history) > 2:
                self.add("P2", "redirect", f"Gereksiz uzun yönlendirme zinciri: {len(response.history)} atlama.", url=url, chain=chain)
        preferred_host = final_hosts.most_common(1)[0][0] if final_hosts else "alo186.com"
        preferred = f"https://{preferred_host}"
        https_apex = self.results["origins"].get("https://alo186.com/", {})
        https_www = self.results["origins"].get("https://www.alo186.com/", {})
        if https_apex.get("url") and https_www.get("url") and urlsplit(https_apex["url"]).netloc != urlsplit(https_www["url"]).netloc:
            self.add("P1", "preferred-host", "HTTPS apex ve www tek bir tercih edilen hostta birleşmiyor.", evidence={"apex": https_apex, "www": https_www})
        return preferred

    def audit_robots(self, preferred: str) -> None:
        for origin in (APEX, WWW):
            url = f"{origin}/robots.txt"
            response = self.request(url)
            if response is None:
                continue
            text = response.text
            record = {"status": response.status_code, "finalUrl": response.url, "contentType": response.headers.get("content-type"), "body": text[:5000]}
            self.results["robots"][origin] = record
            if response.status_code != 200:
                self.add("P1", "robots", f"robots.txt HTTP {response.status_code} döndürüyor.", url=url)
                continue
            if not re.search(r"(?im)^\s*user-agent\s*:", text):
                self.add("P1", "robots", "robots.txt içinde User-agent yönergesi yok.", url=url)
            if re.search(r"(?im)^\s*disallow\s*:\s*/\s*$", text):
                self.add("P0", "robots", "robots.txt tüm siteyi taramaya kapatıyor.", url=url)
            sitemap_refs = re.findall(r"(?im)^\s*sitemap\s*:\s*(\S+)", text)
            if not sitemap_refs:
                self.add("P2", "robots", "robots.txt sitemap konumunu bildirmiyor.", url=url)
            for ref in sitemap_refs:
                if urlsplit(ref).netloc and f"https://{urlsplit(ref).netloc}" != preferred:
                    self.add("P1", "robots", "robots.txt sitemap URL'si tercih edilen hostla uyuşmuyor.", url=url, sitemap=ref, preferred=preferred)

    @staticmethod
    def parse_sitemap(text: str) -> list[str]:
        root = ET.fromstring(text)
        return [node.text.strip() for node in root.findall(".//{*}loc") if node.text and node.text.strip()]

    def inspect_html_response(self, url: str, response: requests.Response) -> dict[str, Any]:
        soup = BeautifulSoup(response.text, "lxml")
        canonical_nodes = soup.select('link[rel~="canonical"]')
        robots = [node.get("content", "") for node in soup.select('meta[name="robots" i]')]
        jsonld_errors: list[str] = []
        jsonld_types: list[str] = []
        for script in soup.select('script[type="application/ld+json"]'):
            raw = script.string or script.get_text() or ""
            try:
                payload = json.loads(raw)
                stack = [payload]
                while stack:
                    item = stack.pop()
                    if isinstance(item, dict):
                        value = item.get("@type")
                        if isinstance(value, str):
                            jsonld_types.append(value)
                        elif isinstance(value, list):
                            jsonld_types.extend(str(v) for v in value)
                        stack.extend(item.values())
                    elif isinstance(item, list):
                        stack.extend(item)
            except Exception as exc:  # noqa: BLE001
                jsonld_errors.append(str(exc))
        forms = []
        for field in soup.select("input,textarea,select"):
            descriptor = " ".join(str(field.get(key, "")) for key in ("type", "name", "id", "placeholder", "autocomplete", "aria-label"))
            if PERSONAL_DATA_RE.search(descriptor):
                forms.append(descriptor.strip())
        official_matches = sorted(set(match.group(0) for match in OFFICIAL_IMPERSONATION_RE.finditer(soup.get_text(" ", strip=True))))
        return {
            "title": soup.title.string.strip() if soup.title and soup.title.string else "",
            "description": (soup.select_one('meta[name="description" i]') or {}).get("content", "") if soup.select_one('meta[name="description" i]') else "",
            "canonicalCount": len(canonical_nodes),
            "canonical": canonical_nodes[0].get("href") if len(canonical_nodes) == 1 else None,
            "robots": robots,
            "h1Count": len(soup.select("h1")),
            "jsonLdErrors": jsonld_errors,
            "jsonLdTypes": sorted(set(jsonld_types)),
            "personalDataFields": forms,
            "officialImpersonationPhrases": official_matches,
        }

    def audit_sitemap(self, preferred: str) -> list[str]:
        url = f"{preferred}/sitemap.xml"
        response = self.request(url)
        if response is None:
            return []
        self.results["sitemap"]["status"] = response.status_code
        self.results["sitemap"]["finalUrl"] = response.url
        if response.status_code != 200:
            self.add("P0", "sitemap", f"sitemap.xml HTTP {response.status_code} döndürüyor.", url=url)
            return []
        try:
            urls = self.parse_sitemap(response.text)
        except Exception as exc:  # noqa: BLE001
            self.add("P0", "sitemap", f"sitemap.xml XML olarak ayrıştırılamadı: {exc}", url=url)
            return []
        self.results["sitemap"]["urlCount"] = len(urls)
        self.results["sitemap"]["sample"] = urls[:20]
        if not urls:
            self.add("P0", "sitemap", "sitemap.xml URL içermiyor.", url=url)
            return []
        host_mismatches = [item for item in urls if f"{urlsplit(item).scheme}://{urlsplit(item).netloc}" != preferred]
        if host_mismatches:
            self.add("P1", "sitemap", f"Sitemap içinde tercih edilen host dışında {len(host_mismatches)} URL var.", url=url, sample=host_mismatches[:10], preferred=preferred)

        def inspect(item: str) -> dict[str, Any]:
            try:
                result = self.session.get(item, timeout=25, allow_redirects=True)
                data = {"url": item, "status": result.status_code, "finalUrl": result.url, "redirects": len(result.history)}
                if "text/html" in result.headers.get("content-type", "") or result.text.lstrip().lower().startswith("<!doctype html"):
                    data.update(self.inspect_html_response(item, result))
                return data
            except requests.RequestException as exc:
                return {"url": item, "error": str(exc)}

        checked: list[dict[str, Any]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
            futures = [executor.submit(inspect, item) for item in urls]
            for future in concurrent.futures.as_completed(futures):
                checked.append(future.result())
        self.results["sitemap"]["checked"] = checked
        for item in checked:
            item_url = item["url"]
            if item.get("error"):
                self.add("P1", "sitemap-url", f"Sitemap URL'si alınamadı: {item['error']}", url=item_url)
                continue
            if item.get("status") != 200:
                self.add("P1", "sitemap-url", f"Sitemap URL'si HTTP {item.get('status')} döndürüyor.", url=item_url, final=item.get("finalUrl"))
                continue
            if item.get("redirects", 0):
                self.add("P2", "sitemap-url", "Sitemap URL'si yönlendirme yapıyor; doğrudan son URL listelenmeli.", url=item_url, final=item.get("finalUrl"), redirects=item.get("redirects"))
            if item.get("canonicalCount") != 1:
                self.add("P1", "canonical", f"Sitemap sayfasında canonical sayısı {item.get('canonicalCount')}.", url=item_url)
            canonical = item.get("canonical")
            if canonical:
                canonical_origin = f"{urlsplit(canonical).scheme}://{urlsplit(canonical).netloc}"
                if canonical_origin != preferred:
                    self.add("P1", "canonical", "Canonical host canlı tercih edilen hostla uyuşmuyor.", url=item_url, canonical=canonical, preferred=preferred)
            if any("noindex" in value.lower() for value in item.get("robots", [])):
                self.add("P1", "indexability", "Sitemap'teki URL noindex taşıyor.", url=item_url, robots=item.get("robots"))
            if item.get("h1Count") != 1:
                self.add("P2", "heading", f"Sayfada H1 sayısı {item.get('h1Count')}.", url=item_url)
            if not item.get("title"):
                self.add("P2", "seo", "Sayfa title etiketi taşımıyor.", url=item_url)
            if not item.get("description"):
                self.add("P2", "seo", "Sayfa meta description taşımıyor.", url=item_url)
            if item.get("jsonLdErrors"):
                self.add("P1", "schema", "JSON-LD ayrıştırma hatası var.", url=item_url, errors=item.get("jsonLdErrors"))
            forbidden = FORBIDDEN_COMMERCE_SCHEMA.intersection(item.get("jsonLdTypes", []))
            if forbidden and not any(token in item_url for token in ("amazon-elektrik-urunleri", "akilli-urun-secimi", "urun-bilgi-grafigi")):
                self.add("P1", "schema", "Teknik içerikte ticari Offer şeması bulundu.", url=item_url, types=sorted(forbidden))
            if item.get("personalDataFields") and not any(token in item_url for token in ("iletisim", "kurumsal", "tedarikci")):
                self.add("P0", "privacy", "Kamu yararı/karar sayfasında kişisel veri alanı bulundu.", url=item_url, fields=item.get("personalDataFields")[:10])
            if item.get("officialImpersonationPhrases"):
                self.add("P0", "trust", "Resmî kurum izlenimi oluşturabilecek ifade bulundu.", url=item_url, phrases=item.get("officialImpersonationPhrases"))
        return urls

    def audit_internal_links(self, preferred: str) -> None:
        links: set[str] = set()
        source_pages: list[str] = []
        for route in KEY_ROUTES:
            url = urljoin(preferred + "/", route.lstrip("/"))
            response = self.request(url)
            if response is None or response.status_code != 200:
                continue
            source_pages.append(url)
            soup = BeautifulSoup(response.text, "lxml")
            for node in soup.select("a[href]"):
                href = node.get("href", "").strip()
                if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                    continue
                absolute = urljoin(response.url, href)
                parsed = urlsplit(absolute)
                if parsed.netloc.lower() not in {"alo186.com", "www.alo186.com"}:
                    continue
                links.add(urlunsplit((parsed.scheme or "https", parsed.netloc, parsed.path or "/", parsed.query, "")))

        def check(item: str) -> tuple[str, int | None, str | None, int, str | None]:
            try:
                response = self.session.get(item, timeout=20, allow_redirects=True)
                return item, response.status_code, response.url, len(response.history), None
            except requests.RequestException as exc:
                return item, None, None, 0, str(exc)

        records = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
            for result in executor.map(check, sorted(links)):
                item, status, final, redirects, error = result
                records.append({"url": item, "status": status, "finalUrl": final, "redirects": redirects, "error": error})
                if error or status is None:
                    self.add("P1", "broken-link", f"İç bağlantı alınamadı: {error}", url=item)
                elif status >= 400:
                    self.add("P1", "broken-link", f"İç bağlantı HTTP {status} döndürüyor.", url=item, final=final)
                elif redirects > 2:
                    self.add("P2", "redirect", f"İç bağlantı {redirects} yönlendirme atlaması yapıyor.", url=item, final=final)
        self.results["internalLinks"] = {"sourcePages": source_pages, "linkCount": len(links), "checked": records}

    @staticmethod
    def perf_observer_script() -> str:
        return """
        (() => {
          window.__alo186Perf = {cls: 0, lcp: 0, longTasks: 0};
          try { new PerformanceObserver(list => { for (const e of list.getEntries()) if (!e.hadRecentInput) window.__alo186Perf.cls += e.value; }).observe({type:'layout-shift', buffered:true}); } catch {}
          try { new PerformanceObserver(list => { const entries=list.getEntries(); if(entries.length) window.__alo186Perf.lcp=entries[entries.length-1].startTime; }).observe({type:'largest-contentful-paint', buffered:true}); } catch {}
          try { new PerformanceObserver(list => { window.__alo186Perf.longTasks += list.getEntries().length; }).observe({type:'longtask', buffered:true}); } catch {}
        })();
        """

    def audit_browser_page(self, browser: Browser, preferred: str, route: str, device_name: str, settings: dict[str, Any], axe_source: str) -> None:
        context = browser.new_context(**settings, locale="tr-TR", color_scheme="light", reduced_motion="reduce")
        page = context.new_page()
        console_errors: list[str] = []
        page_errors: list[str] = []
        failed_requests: list[str] = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        page.on("requestfailed", lambda req: failed_requests.append(f"{req.method} {req.url}: {req.failure}"))
        page.add_init_script(self.perf_observer_script())
        url = urljoin(preferred + "/", route.lstrip("/"))
        response = None
        try:
            response = page.goto(url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(1800)
        except Exception as exc:  # noqa: BLE001
            self.add("P1", "browser-navigation", f"Tarayıcı sayfayı açamadı: {exc}", url=url, device=device_name)
            context.close()
            return
        status = response.status if response else None
        if status != 200:
            self.add("P1", "browser-navigation", f"Tarayıcı HTTP {status} gördü.", url=url, device=device_name)

        slug = re.sub(r"[^a-z0-9]+", "-", route.lower()).strip("-") or "home"
        screenshot = self.output / "screenshots" / f"{device_name}-{slug}.png"
        page.screenshot(path=str(screenshot), full_page=True)

        metrics = page.evaluate(
            """() => {
              const doc=document.documentElement;
              const body=document.body;
              const interactive=[...document.querySelectorAll('button,input,select,textarea,[role="button"],a[href]')].filter(el=>{
                const s=getComputedStyle(el),r=el.getBoundingClientRect();
                if(s.display==='none'||s.visibility==='hidden'||Number(s.opacity)===0||r.width===0||r.height===0)return false;
                if(el.matches('a[href]')&&s.display==='inline')return false;
                return true;
              });
              const smallTargets=interactive.map(el=>{const r=el.getBoundingClientRect();return {tag:el.tagName,id:el.id||'',text:(el.innerText||el.getAttribute('aria-label')||'').trim().slice(0,80),w:Math.round(r.width),h:Math.round(r.height)}}).filter(x=>x.w<44||x.h<44).slice(0,30);
              const overflowing=[...document.querySelectorAll('body *')].map(el=>{const r=el.getBoundingClientRect();return {el,r,s:getComputedStyle(el)}}).filter(x=>x.r.right>innerWidth+2||x.r.left<-2).slice(0,30).map(x=>({tag:x.el.tagName,id:x.el.id||'',class:x.el.className?.toString().slice(0,100)||'',left:Math.round(x.r.left),right:Math.round(x.r.right),width:Math.round(x.r.width)}));
              const clipped=[...document.querySelectorAll('body *')].map(el=>{const s=getComputedStyle(el),r=el.getBoundingClientRect();const clips=['hidden','clip'].includes(s.overflow)||['hidden','clip'].includes(s.overflowX)||['hidden','clip'].includes(s.overflowY);return {el,s,r,clips}}).filter(x=>x.clips&&((x.el.scrollWidth>x.el.clientWidth+2)||(x.el.scrollHeight>x.el.clientHeight+2))&&(x.el.innerText||'').trim()).slice(0,30).map(x=>({tag:x.el.tagName,id:x.el.id||'',class:x.el.className?.toString().slice(0,100)||'',text:(x.el.innerText||'').trim().slice(0,100),client:[x.el.clientWidth,x.el.clientHeight],scroll:[x.el.scrollWidth,x.el.scrollHeight]}));
              const images=[...document.images].map(img=>({src:img.currentSrc||img.src,alt:img.getAttribute('alt'),complete:img.complete,naturalWidth:img.naturalWidth,naturalHeight:img.naturalHeight,loading:img.loading}));
              const fixed=[...document.querySelectorAll('body *')].filter(el=>{const s=getComputedStyle(el),r=el.getBoundingClientRect();return ['fixed','sticky'].includes(s.position)&&s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0}).map(el=>{const r=el.getBoundingClientRect();return {tag:el.tagName,id:el.id||'',class:el.className?.toString().slice(0,100)||'',rect:{x:r.x,y:r.y,w:r.width,h:r.height}}});
              const paint=performance.getEntriesByType('paint').reduce((a,e)=>(a[e.name]=e.startTime,a),{});
              const nav=performance.getEntriesByType('navigation')[0];
              return {viewport:{w:innerWidth,h:innerHeight},scrollWidth:Math.max(doc.scrollWidth,body?.scrollWidth||0),overflowing,clipped,smallTargets,images,fixed,perf:{...(window.__alo186Perf||{}),fcp:paint['first-contentful-paint']||0,domContentLoaded:nav?.domContentLoadedEventEnd||0,load:nav?.loadEventEnd||0,transferSize:nav?.transferSize||0},title:document.title,h1:document.querySelectorAll('h1').length,lang:document.documentElement.lang,main:document.querySelectorAll('main').length};
            }"""
        )
        broken_images = [item for item in metrics["images"] if item["complete"] and item["naturalWidth"] == 0]
        missing_alt = [item for item in metrics["images"] if item["alt"] is None]
        if metrics["scrollWidth"] > metrics["viewport"]["w"] + 2 or metrics["overflowing"]:
            self.add("P1", "mobile-overflow" if device_name == "mobile" else "layout-overflow", "Yatay taşma bulundu.", url=url, device=device_name, viewport=metrics["viewport"], scrollWidth=metrics["scrollWidth"], offenders=metrics["overflowing"][:10])
        if metrics["clipped"]:
            self.add("P2", "text-clipping", f"{len(metrics['clipped'])} metin alanında kırpılma sinyali bulundu.", url=url, device=device_name, sample=metrics["clipped"][:10])
        if broken_images:
            self.add("P1", "broken-image", f"{len(broken_images)} görsel yüklenemedi.", url=url, device=device_name, images=broken_images[:10])
        if missing_alt:
            self.add("P2", "image-alt", f"{len(missing_alt)} görsel alt niteliği taşımıyor.", url=url, device=device_name, images=missing_alt[:10])
        if metrics["smallTargets"]:
            self.add("P2", "tap-target", f"{len(metrics['smallTargets'])} etkileşim hedefi 44×44 px altında.", url=url, device=device_name, sample=metrics["smallTargets"][:15])
        if console_errors or page_errors:
            self.add("P2", "javascript", "Tarayıcı konsolu veya sayfa JavaScript hatası üretti.", url=url, device=device_name, console=console_errors[:10], pageErrors=page_errors[:10])
        if failed_requests:
            self.add("P2", "network", f"{len(failed_requests)} kaynak isteği başarısız oldu.", url=url, device=device_name, failures=failed_requests[:15])
        if metrics["h1"] != 1:
            self.add("P2", "heading", f"Tarayıcı DOM'unda H1 sayısı {metrics['h1']}.", url=url, device=device_name)
        if not metrics["lang"]:
            self.add("P2", "accessibility", "html lang niteliği yok.", url=url, device=device_name)
        if metrics["main"] != 1:
            self.add("P2", "accessibility", f"main landmark sayısı {metrics['main']}.", url=url, device=device_name)
        perf = metrics["perf"]
        if perf.get("lcp", 0) > 4000:
            self.add("P1", "lcp", f"Laboratuvar LCP {perf['lcp']:.0f} ms (zayıf).", url=url, device=device_name, metrics=perf)
        elif perf.get("lcp", 0) > 2500:
            self.add("P2", "lcp", f"Laboratuvar LCP {perf['lcp']:.0f} ms (iyileştirilmeli).", url=url, device=device_name, metrics=perf)
        if perf.get("cls", 0) > 0.25:
            self.add("P1", "cls", f"Laboratuvar CLS {perf['cls']:.3f} (zayıf).", url=url, device=device_name, metrics=perf)
        elif perf.get("cls", 0) > 0.1:
            self.add("P2", "cls", f"Laboratuvar CLS {perf['cls']:.3f} (iyileştirilmeli).", url=url, device=device_name, metrics=perf)

        axe = {"violations": []}
        try:
            page.add_script_tag(content=axe_source)
            axe = page.evaluate("""async () => await axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']},resultTypes:['violations']})""")
        except Exception as exc:  # noqa: BLE001
            self.add("P2", "accessibility-runner", f"axe-core çalıştırılamadı: {exc}", url=url, device=device_name)
        serious = [item for item in axe.get("violations", []) if item.get("impact") in {"critical", "serious"}]
        moderate = [item for item in axe.get("violations", []) if item.get("impact") in {"moderate", "minor"}]
        if serious:
            self.add("P1", "accessibility", f"axe-core {len(serious)} ciddi/kritik erişilebilirlik ihlali buldu.", url=url, device=device_name, violations=[{"id": item.get("id"), "impact": item.get("impact"), "help": item.get("help"), "nodes": len(item.get("nodes", []))} for item in serious])
        if moderate:
            self.add("P2", "accessibility", f"axe-core {len(moderate)} orta/düşük erişilebilirlik ihlali buldu.", url=url, device=device_name, violations=[{"id": item.get("id"), "impact": item.get("impact"), "help": item.get("help"), "nodes": len(item.get("nodes", []))} for item in moderate[:12]])

        self.results["pages"].append({
            "url": url,
            "finalUrl": page.url,
            "device": device_name,
            "status": status,
            "screenshot": str(screenshot),
            "metrics": metrics,
            "axe": {"violations": [{"id": item.get("id"), "impact": item.get("impact"), "help": item.get("help"), "nodes": len(item.get("nodes", []))} for item in axe.get("violations", [])]},
            "consoleErrors": console_errors,
            "pageErrors": page_errors,
            "failedRequests": failed_requests,
        })
        context.close()

    def audit_browser(self, preferred: str) -> None:
        axe_path = Path(os.environ.get("AXE_CORE_PATH", "node_modules/axe-core/axe.min.js"))
        if not axe_path.is_file():
            self.add("P2", "accessibility-runner", f"axe-core bulunamadı: {axe_path}")
            axe_source = ""
        else:
            axe_source = axe_path.read_text(encoding="utf-8")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
            for route in KEY_ROUTES:
                for device_name, settings in DEVICES.items():
                    self.audit_browser_page(browser, preferred, route, device_name, settings, axe_source)
            browser.close()

    def audit_pagespeed(self, preferred: str) -> None:
        endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        for strategy in ("mobile", "desktop"):
            params = [("url", preferred + "/"), ("strategy", strategy)]
            for category in ("performance", "accessibility", "best-practices", "seo"):
                params.append(("category", category))
            response = None
            for attempt in range(3):
                try:
                    response = self.session.get(endpoint, params=params, timeout=120)
                    if response.status_code not in {429, 500, 502, 503, 504}:
                        break
                except requests.RequestException:
                    response = None
                time.sleep(3 * (attempt + 1))
            if response is None or response.status_code != 200:
                status = response.status_code if response is not None else None
                self.results["pageSpeed"][strategy] = {"available": False, "status": status, "message": (response.text[:500] if response is not None else "request failed")}
                self.add("P2", "pagespeed", f"PageSpeed Insights API sonucu alınamadı (HTTP {status}).", url=preferred + "/", device=strategy)
                continue
            data = response.json()
            lighthouse = data.get("lighthouseResult", {})
            categories = {key: round(value.get("score", 0) * 100) for key, value in lighthouse.get("categories", {}).items()}
            audits = lighthouse.get("audits", {})
            metrics = {
                "fcpMs": audits.get("first-contentful-paint", {}).get("numericValue"),
                "lcpMs": audits.get("largest-contentful-paint", {}).get("numericValue"),
                "speedIndexMs": audits.get("speed-index", {}).get("numericValue"),
                "tbtMs": audits.get("total-blocking-time", {}).get("numericValue"),
                "cls": audits.get("cumulative-layout-shift", {}).get("numericValue"),
            }
            loading = data.get("loadingExperience", {})
            origin_loading = data.get("originLoadingExperience", {})
            record = {"available": True, "categories": categories, "lab": metrics, "field": loading.get("metrics", {}), "originField": origin_loading.get("metrics", {})}
            self.results["pageSpeed"][strategy] = record
            performance = categories.get("performance", 100)
            accessibility = categories.get("accessibility", 100)
            seo = categories.get("seo", 100)
            if performance < 50:
                self.add("P1", "pagespeed", f"PageSpeed {strategy} performans skoru {performance}.", url=preferred + "/", device=strategy, record=record)
            elif performance < 90:
                self.add("P2", "pagespeed", f"PageSpeed {strategy} performans skoru {performance}.", url=preferred + "/", device=strategy, record=record)
            if accessibility < 90:
                self.add("P1", "pagespeed", f"PageSpeed {strategy} erişilebilirlik skoru {accessibility}.", url=preferred + "/", device=strategy, record=record)
            if seo < 90:
                self.add("P1", "pagespeed", f"PageSpeed {strategy} SEO skoru {seo}.", url=preferred + "/", device=strategy, record=record)

    def write_reports(self, preferred: str) -> int:
        severity_order = {"P0": 0, "P1": 1, "P2": 2}
        self.findings.sort(key=lambda item: (severity_order.get(item.severity, 9), item.check, item.url or "", item.device or ""))
        payload = {
            **self.results,
            "preferredOrigin": preferred,
            "summary": dict(Counter(item.severity for item in self.findings)),
            "findings": [asdict(item) for item in self.findings],
        }
        (self.output / "audit.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        lines = [
            "# ALO186 canlı teknik kalite denetimi",
            "",
            f"- Tercih edilen canlı origin: `{preferred}`",
            f"- P0: {payload['summary'].get('P0', 0)}",
            f"- P1: {payload['summary'].get('P1', 0)}",
            f"- P2: {payload['summary'].get('P2', 0)}",
            "",
            "## Önceliklendirilmiş bulgular",
            "",
        ]
        if not self.findings:
            lines.append("Yayın engelleyici veya iyileştirme gerektiren bulgu bulunmadı.")
        for index, item in enumerate(self.findings, 1):
            suffix = " · ".join(part for part in (item.url, item.device) if part)
            lines.extend([f"### {index}. {item.severity} · {item.check}", "", item.message + (f"  \n`{suffix}`" if suffix else ""), ""])
            if item.evidence:
                lines.extend(["```json", json.dumps(item.evidence, ensure_ascii=False, indent=2)[:5000], "```", ""])
        lines.extend(["## PageSpeed / Lighthouse", "", "```json", json.dumps(self.results["pageSpeed"], ensure_ascii=False, indent=2), "```", ""])
        (self.output / "report.md").write_text("\n".join(lines), encoding="utf-8")
        print(json.dumps({"ok": not any(item.severity in {"P0", "P1"} for item in self.findings), "preferredOrigin": preferred, "summary": payload["summary"], "output": str(self.output)}, ensure_ascii=False, indent=2))
        return 1 if any(item.severity in {"P0", "P1"} for item in self.findings) else 0

    def run(self) -> int:
        preferred = self.audit_origins()
        self.audit_robots(preferred)
        self.audit_sitemap(preferred)
        self.audit_internal_links(preferred)
        self.audit_browser(preferred)
        self.audit_pagespeed(preferred)
        return self.write_reports(preferred)


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canlı site mobil/masaüstü teknik kalite denetimi")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    sys.exit(Audit(args.output).run())


if __name__ == "__main__":
    main()
