from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

VERSION = 210
SCRIPT_MARKER = 'data-alo186-affiliate-measurement-v210="true"'
INVENTORY_NAME = "affiliate-measurement-v210.json"
ASSET_RELATIVE = Path("assets/affiliate-measurement-v210.js")

ANCHOR_RE = re.compile(r"<a\b[^>]*>", re.IGNORECASE | re.DOTALL)
EXCLUDED_BLOCK_RE = re.compile(
    r"(<(?:script|style)\b[^>]*>.*?</(?:script|style)\s*>)",
    re.IGNORECASE | re.DOTALL,
)


def normalize_base_path(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def _attribute_pattern(name: str) -> re.Pattern[str]:
    return re.compile(
        rf"(?<![\w:-]){re.escape(name)}\s*=\s*(?:\"(?P<dq>[^\"]*)\"|'(?P<sq>[^']*)'|(?P<bare>[^\s>]+))",
        re.IGNORECASE | re.DOTALL,
    )


def get_attr(tag: str, name: str) -> str | None:
    match = _attribute_pattern(name).search(tag)
    if not match:
        return None
    value = match.group("dq")
    if value is None:
        value = match.group("sq")
    if value is None:
        value = match.group("bare")
    return html.unescape(value or "")


def set_attr(tag: str, name: str, value: str) -> str:
    escaped = html.escape(value, quote=True)
    match = _attribute_pattern(name).search(tag)
    replacement = f'{name}="{escaped}"'
    if match:
        return tag[: match.start()] + replacement + tag[match.end() :]
    if tag.endswith(">"):
        return tag[:-1].rstrip() + f" {replacement}>"
    raise ValueError("Geçersiz anchor etiketi")


def _host(href: str) -> str:
    candidate = html.unescape((href or "").strip())
    if candidate.startswith("//"):
        candidate = "https:" + candidate
    parsed = urlparse(candidate)
    return (parsed.hostname or "").lower().rstrip(".")


def is_external_http(href: str) -> bool:
    candidate = html.unescape((href or "").strip())
    if candidate.startswith("//"):
        return True
    parsed = urlparse(candidate)
    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)


def is_amazon_href(href: str) -> bool:
    host = _host(href)
    if host in {"amzn.to", "amzn.eu"}:
        return True
    return bool(host) and (
        host == "amazon.com.tr"
        or host.endswith(".amazon.com.tr")
        or host == "amazon.com"
        or host.endswith(".amazon.com")
    )


def classify_link_type(href: str) -> str:
    candidate = html.unescape((href or "").strip())
    parsed = urlparse("https:" + candidate if candidate.startswith("//") else candidate)
    host = (parsed.hostname or "").lower()
    path = (parsed.path or "").lower()
    query = (parsed.query or "").lower()
    if host in {"amzn.to", "amzn.eu"}:
        return "short"
    if "/dp/" in path or "/gp/product/" in path:
        return "direct_product"
    if path.rstrip("/") == "/s" or "k=" in query or "keywords=" in query:
        return "search"
    return "category_or_other"


def product_key(href: str) -> str:
    normalized = html.unescape((href or "").strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:14]


def route_for(path: Path, site: Path, base_path: str) -> str:
    relative = path.relative_to(site).as_posix()
    if relative == "index.html":
        route = "/"
    elif relative.endswith("/index.html"):
        route = "/" + relative[: -len("index.html")]
    else:
        route = "/" + relative
    if base_path:
        return base_path + route if route != "/" else base_path + "/"
    return route


def cluster_for_route(route: str, base_path: str) -> str:
    cleaned = route[len(base_path) :] if base_path and route.startswith(base_path) else route
    parts = [part for part in cleaned.strip("/").split("/") if part]
    if not parts:
        return "home"
    if parts[0] == "amazon-elektrik-urunleri" and len(parts) > 1:
        return "affiliate-" + re.sub(r"[^a-z0-9-]+", "-", parts[1].lower()).strip("-")[:56]
    return re.sub(r"[^a-z0-9-]+", "-", parts[0].lower()).strip("-")[:56] or "other"


def infer_placement(tag: str) -> str:
    explicit = get_attr(tag, "data-affiliate-placement") or get_attr(tag, "data-placement")
    if explicit:
        return re.sub(r"[^a-z0-9_-]+", "-", explicit.lower()).strip("-")[:48] or "content"
    classes = (get_attr(tag, "class") or "").lower()
    for needle, placement in (
        ("sticky", "sticky"),
        ("comparison", "comparison"),
        ("table", "comparison"),
        ("result", "result"),
        ("hero", "hero"),
        ("card", "card"),
        ("footer", "footer"),
        ("cta", "cta"),
    ):
        if needle in classes:
            return placement
    return "content"


def _merge_rel(tag: str, required: set[str]) -> tuple[str, bool]:
    tokens = {token.lower() for token in (get_attr(tag, "rel") or "").split() if token.strip()}
    before = set(tokens)
    tokens.update(required)
    return set_attr(tag, "rel", " ".join(sorted(tokens))), tokens != before


def normalize_anchor(tag: str, cluster: str) -> tuple[str, dict[str, object]]:
    href = get_attr(tag, "href") or ""
    target = (get_attr(tag, "target") or "").lower()
    declared = (get_attr(tag, "data-affiliate-network") or "").lower().startswith("amazon")
    affiliate = is_amazon_href(href) or (declared and is_external_http(href))
    updated = tag
    changed = False

    if affiliate:
        updated, rel_changed = _merge_rel(updated, {"sponsored", "nofollow", "noopener"})
        changed = changed or rel_changed
        for name, value in (
            ("data-affiliate-network", "amazon_tr"),
            ("data-affiliate-content-cluster", cluster),
            ("data-affiliate-placement", infer_placement(updated)),
            ("data-affiliate-link-type", classify_link_type(href)),
            ("data-affiliate-product-key", product_key(href)),
            ("data-affiliate-measurement-version", str(VERSION)),
        ):
            if get_attr(updated, name) is None:
                updated = set_attr(updated, name, value)
                changed = True
    elif target == "_blank" and is_external_http(href):
        updated, rel_changed = _merge_rel(updated, {"noopener"})
        changed = changed or rel_changed

    return updated, {
        "affiliate": affiliate,
        "changed": changed,
        "network": "amazon_tr" if affiliate else None,
        "productKey": get_attr(updated, "data-affiliate-product-key") if affiliate else None,
        "placement": get_attr(updated, "data-affiliate-placement") if affiliate else None,
        "linkType": get_attr(updated, "data-affiliate-link-type") if affiliate else None,
        "targetBlank": target == "_blank" if affiliate else None,
    }


def runtime_asset() -> str:
    return f'''(()=>{{
  'use strict';
  const VERSION='{VERSION}';
  const AMAZON_HOST=(host)=>host==='amzn.to'||host==='amzn.eu'||host==='amazon.com.tr'||host.endsWith('.amazon.com.tr')||host==='amazon.com'||host.endsWith('.amazon.com');
  const safeUrl=(value)=>{{try{{return new URL(value,window.location.href);}}catch(_error){{return null;}}}};
  const isAffiliate=(link)=>{{
    const declared=(link.dataset.affiliateNetwork||'').toLowerCase();
    if(declared.startsWith('amazon'))return true;
    const url=safeUrl(link.getAttribute('href')||'');
    return Boolean(url&&AMAZON_HOST(url.hostname.toLowerCase()));
  }};
  const hashKey=(value)=>{{let hash=2166136261;for(let index=0;index<value.length;index++){{hash^=value.charCodeAt(index);hash=Math.imul(hash,16777619);}}return (hash>>>0).toString(36);}};
  const cluster=()=>{{
    const parts=window.location.pathname.split('/').filter(Boolean);
    if(parts[0]==='chatgpt')parts.shift();
    if(!parts.length)return 'home';
    if(parts[0]==='amazon-elektrik-urunleri'&&parts[1])return ('affiliate-'+parts[1]).slice(0,56);
    return (parts[0]||'other').slice(0,56);
  }};
  const linkType=(link,url)=>{{
    if(link.dataset.affiliateLinkType)return link.dataset.affiliateLinkType;
    const host=(url?.hostname||'').toLowerCase();
    const path=(url?.pathname||'').toLowerCase();
    if(host==='amzn.to'||host==='amzn.eu')return 'short';
    if(path.includes('/dp/')||path.includes('/gp/product/'))return 'direct_product';
    const normalizedPath=path.endsWith('/')?path.slice(0,-1):path;
    if(normalizedPath==='/s'||url?.searchParams.has('k')||url?.searchParams.has('keywords'))return 'search';
    return 'category_or_other';
  }};
  const placement=(link)=>link.dataset.affiliatePlacement||link.closest('[data-affiliate-placement]')?.dataset.affiliatePlacement||(link.closest('table')?'comparison':link.closest('[class*="result"]')?'result':link.closest('[class*="card"]')?'card':'content');
  const analyticsReady=()=>window.alo186Analytics?.getConsent?.()==='granted'&&typeof window.gtag==='function'&&Boolean(document.querySelector('[data-alo186-ga4-loader="true"]'));
  let suppressGenericAffiliate=false;
  const originalGtag=window.gtag;
  if(typeof originalGtag==='function'&&!originalGtag.__alo186AffiliateV210){{
    const wrapped=function(...args){{
      const params=args[2]||{{}};
      if(suppressGenericAffiliate&&args[0]==='event'&&args[1]==='affiliate_click'&&String(params.measurement_version||'')!==VERSION){{
        suppressGenericAffiliate=false;
        return;
      }}
      return originalGtag.apply(this,args);
    }};
    wrapped.__alo186AffiliateV210=true;
    window.gtag=wrapped;
  }}
  const send=(name,params)=>{{
    if(!analyticsReady())return false;
    window.gtag('event',name,params);
    return true;
  }};
  let pageViewSent=false;
  const sendPageView=()=>{{
    if(pageViewSent)return;
    const links=[...document.querySelectorAll('a')].filter(isAffiliate);
    if(!links.length)return;
    pageViewSent=send('affiliate_page_view',{{
      affiliate_network:'amazon_tr',
      page_path:window.location.pathname,
      content_cluster:cluster(),
      affiliate_link_count:links.length,
      measurement_version:VERSION
    }});
  }};
  window.addEventListener('click',(event)=>{{
    const consentButton=event.target.closest?.('[data-alo186-consent-choice="granted"]');
    if(consentButton)window.setTimeout(sendPageView,0);
    const link=event.target.closest?.('a');
    if(!link||!isAffiliate(link))return;
    sendPageView();
    const href=link.getAttribute('href')||'';
    const url=safeUrl(href);
    const sent=send('affiliate_click',{{
      affiliate_network:'amazon_tr',
      page_path:window.location.pathname,
      content_cluster:link.dataset.affiliateContentCluster||cluster(),
      link_placement:placement(link),
      link_type:linkType(link,url),
      product_key:link.dataset.affiliateProductKey||hashKey(href),
      measurement_version:VERSION
    }});
    if(sent){{
      suppressGenericAffiliate=true;
      queueMicrotask(()=>{{suppressGenericAffiliate=false;}});
    }}
  }},{{capture:true}});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',sendPageView,{{once:true}});else queueMicrotask(sendPageView);
  const observer=new MutationObserver(()=>{{sendPageView();if(pageViewSent)observer.disconnect();}});
  observer.observe(document.documentElement,{{childList:true,subtree:true}});
  window.setTimeout(()=>observer.disconnect(),15000);
}})();
'''


def script_tag(base_path: str) -> str:
    src = public_url(base_path, "/" + ASSET_RELATIVE.as_posix())
    return f'<script defer src="{src}" {SCRIPT_MARKER}></script>'


def inject_page(path: Path, site: Path, base_path: str) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="strict")
    route = route_for(path, site, base_path)
    cluster = cluster_for_route(route, base_path)
    records: list[dict[str, object]] = []
    segments = EXCLUDED_BLOCK_RE.split(text)

    def replace(match: re.Match[str]) -> str:
        updated, record = normalize_anchor(match.group(0), cluster)
        records.append(record)
        return updated

    for index in range(0, len(segments), 2):
        segments[index] = ANCHOR_RE.sub(replace, segments[index])
    updated_text = "".join(segments)

    if SCRIPT_MARKER not in updated_text:
        lowered = updated_text.lower()
        position = lowered.rfind("</body>")
        if position >= 0:
            updated_text = updated_text[:position] + script_tag(base_path) + "\n" + updated_text[position:]

    changed = updated_text != text
    if changed:
        path.write_text(updated_text, encoding="utf-8")

    affiliate_records = [record for record in records if record["affiliate"]]
    blank_external_count = sum(
        1
        for segment_index in range(0, len(EXCLUDED_BLOCK_RE.split(updated_text)), 2)
        for match in ANCHOR_RE.finditer(EXCLUDED_BLOCK_RE.split(updated_text)[segment_index])
        if (get_attr(match.group(0), "target") or "").lower() == "_blank"
        and is_external_http(get_attr(match.group(0), "href") or "")
        and "noopener" in set((get_attr(match.group(0), "rel") or "").split())
    )
    return {
        "route": route,
        "cluster": cluster,
        "instrumented": SCRIPT_MARKER in updated_text,
        "affiliateLinkCount": len(affiliate_records),
        "normalizedAffiliateLinkCount": len(affiliate_records),
        "protectedBlankExternalLinkCount": blank_external_count,
        "links": [
            {
                "network": record["network"],
                "productKey": record["productKey"],
                "placement": record["placement"],
                "linkType": record["linkType"],
                "targetBlank": record["targetBlank"],
            }
            for record in affiliate_records
        ],
    }


def recompute_checksums(site: Path) -> None:
    checksum_path = site / "checksums.sha256"
    if not checksum_path.exists():
        return
    checksum_path.unlink()
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(site).as_posix()}"
        for path in sorted(item for item in site.rglob("*") if item.is_file())
    ]
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_inventory(site: Path, pages: list[dict[str, object]], base_path: str) -> dict[str, object]:
    affiliate_pages = [page for page in pages if page["affiliateLinkCount"]]
    inventory: dict[str, object] = {
        "version": VERSION,
        "basePath": base_path,
        "asset": public_url(base_path, "/" + ASSET_RELATIVE.as_posix()),
        "privacy": {
            "rawDestinationUrlStored": False,
            "rawSearchQueryStored": False,
            "userIdentifierStored": False,
        },
        "events": ["affiliate_page_view", "affiliate_click"],
        "summary": {
            "scannedPages": len(pages),
            "instrumentedPages": sum(1 for page in pages if page["instrumented"]),
            "staticAffiliatePages": len(affiliate_pages),
            "staticAffiliateLinks": sum(int(page["affiliateLinkCount"]) for page in pages),
            "normalizedAffiliateLinks": sum(int(page["normalizedAffiliateLinkCount"]) for page in pages),
            "protectedBlankExternalLinks": sum(int(page["protectedBlankExternalLinkCount"]) for page in pages),
            "directProductLinks": sum(1 for page in pages for link in page["links"] if link["linkType"] == "direct_product"),
            "searchLinks": sum(1 for page in pages for link in page["links"] if link["linkType"] == "search"),
            "shortLinks": sum(1 for page in pages for link in page["links"] if link["linkType"] == "short"),
        },
        "pages": [
            {
                "route": page["route"],
                "contentCluster": page["cluster"],
                "affiliateLinkCount": page["affiliateLinkCount"],
                "links": page["links"],
            }
            for page in affiliate_pages
        ],
    }
    (site / INVENTORY_NAME).write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return inventory


def update_release(site: Path, inventory: dict[str, object]) -> None:
    path = site / "pages-release.json"
    if not path.is_file():
        return
    release = json.loads(path.read_text(encoding="utf-8"))
    summary = inventory["summary"]
    release["affiliateMeasurement"] = {
        "version": VERSION,
        "asset": inventory["asset"],
        "inventory": public_url(str(inventory["basePath"]), "/" + INVENTORY_NAME),
        "events": inventory["events"],
        "scannedPages": summary["scannedPages"],
        "instrumentedPages": summary["instrumentedPages"],
        "staticAffiliateLinks": summary["staticAffiliateLinks"],
        "normalizedAffiliateLinks": summary["normalizedAffiliateLinks"],
        "rawDestinationUrlInAnalytics": False,
        "personalIdentifiers": False,
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def inject(site: Path, base_path: str = "") -> dict[str, object]:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    html_files = sorted(path for path in site.rglob("*.html") if path.is_file())
    if not html_files:
        raise RuntimeError("ALO186 HTML artifactı bulunamadı")

    asset_path = site / ASSET_RELATIVE
    asset_path.parent.mkdir(parents=True, exist_ok=True)
    asset_path.write_text(runtime_asset(), encoding="utf-8")

    pages = [inject_page(path, site, base_path) for path in html_files]
    inventory = write_inventory(site, pages, base_path)
    update_release(site, inventory)
    recompute_checksums(site)
    return {
        "ok": True,
        "version": VERSION,
        "basePath": base_path,
        "asset": ASSET_RELATIVE.as_posix(),
        "inventory": INVENTORY_NAME,
        "events": inventory["events"],
        **inventory["summary"],
        "rawDestinationUrlInAnalytics": False,
        "personalIdentifiers": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 affiliate bağlantılarını ölçer, normalize eder ve envanterler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(inject(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
