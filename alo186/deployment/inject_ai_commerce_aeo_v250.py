from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit

VERSION = 250
MARKER = 'data-alo186-ai-commerce-aeo-v250="true"'
SCHEMA_MARKER = 'data-alo186-schema-v250="true"'
STYLE_MARKER = 'data-alo186-ai-commerce-style-v250="true"'
MANIFEST_RELATIVE = Path("alo186/deployment/ai-commerce-aeo-v250.json")
STYLE_SOURCE = Path("alo186/assets/ai-commerce-aeo-v250.css")
STYLE_TARGET = Path("assets/ai-commerce-aeo-v250.css")
VALIDATION_TARGET = Path("ai-commerce-schema-validation-v250.json")
LLMS_SOURCE = Path("alo186/llms.txt")
LLMS_TARGET = Path("llms.txt")
ROBOTS_SOURCE = Path("alo186/robots.txt")
ROBOTS_TARGET = Path("robots.txt")
AMAZON_HOSTS = {"amazon.com.tr", "www.amazon.com.tr", "amzn.to", "www.amzn.to"}
REQUIRED_REL = ("sponsored", "nofollow", "noopener")
SAFETY_ROUTE_PREFIXES = (
    "acil-numaralar/",
    "en/emergency-numbers-turkey/",
    "en/electricity-outage-turkey/",
)


def load_manifest(repo_root: Path) -> dict:
    path = repo_root / MANIFEST_RELATIVE
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("version") != VERSION:
        raise ValueError(f"AI commerce manifest version yanlış: {payload.get('version')!r}")
    if payload.get("canonicalHost") != "https://alo186.com":
        raise ValueError("AI commerce canonicalHost apex origin olmalıdır.")
    routes = payload.get("routes")
    if not isinstance(routes, list) or not routes:
        raise ValueError("AI commerce route listesi boş.")
    return payload


def absolute_url(host: str, page_path: str, value: str) -> str:
    if value.startswith("#"):
        return host.rstrip("/") + page_path + value
    if value.startswith("/"):
        return host.rstrip("/") + value
    raise ValueError(f"Yalnız iç rota/fragment kabul edilir: {value!r}")


def validated_offers(manifest: dict) -> dict[str, dict]:
    policy = manifest.get("offerPolicy") or {}
    if policy.get("mode") != "fail-closed":
        raise ValueError("Offer policy fail-closed olmalıdır.")
    raw = policy.get("verifiedOffers") or []
    required = {
        "productId",
        "name",
        "url",
        "image",
        "brand",
        "sku",
        "seller",
        "price",
        "priceCurrency",
        "availability",
        "priceValidUntil",
        "verifiedAt",
    }
    offers: dict[str, dict] = {}
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("verifiedOffers kayıtları object olmalıdır.")
        missing = sorted(required - set(item))
        if missing:
            raise ValueError(
                f"Doğrulanmış Offer eksik alan taşıyor ({item.get('productId')}): {', '.join(missing)}"
            )
        product_id = str(item["productId"]).strip()
        if product_id in offers:
            raise ValueError(f"Yinelenen verified Offer productId: {product_id}")
        parsed = urlsplit(str(item["url"]))
        if parsed.scheme != "https" or parsed.hostname not in AMAZON_HOSTS:
            raise ValueError(f"Offer URL doğrulanmış Amazon Türkiye URL'si değil: {item['url']}")
        if not re.fullmatch(r"\d+(?:\.\d{1,2})?", str(item["price"])):
            raise ValueError(f"Offer price sayısal değil: {item['price']!r}")
        if item["priceCurrency"] != "TRY":
            raise ValueError("ALO186 Amazon Türkiye Offer para birimi TRY olmalıdır.")
        offers[product_id] = item
    return offers


def product_entity(
    *,
    host: str,
    page_path: str,
    product: dict,
    offers: dict[str, dict],
) -> dict:
    product_url = host + page_path + "#" + product["id"]
    entity: dict = {
        "@type": "Product",
        "@id": product_url,
        "name": product["name"],
        "description": product["useWhen"],
        "category": product["category"],
        "url": product_url,
        "isRelatedTo": {
            "@type": "WebPage",
            "url": absolute_url(host, page_path, product["guideUrl"]),
            "name": product["guideLabel"],
        },
        "additionalProperty": [
            {
                "@type": "PropertyValue",
                "name": "En uygun kullanım",
                "value": product["bestFor"],
            },
            {
                "@type": "PropertyValue",
                "name": "Teknik kontrol",
                "value": product["technicalCheck"],
            },
            {
                "@type": "PropertyValue",
                "name": "Kullanım sınırı",
                "value": product["limit"],
            },
            {
                "@type": "PropertyValue",
                "name": "Satın almama koşulu",
                "value": product["skipWhen"],
            },
        ],
    }
    offer = offers.get(product["id"])
    if offer:
        entity.update(
            {
                "name": offer["name"],
                "image": offer["image"],
                "brand": {"@type": "Brand", "name": offer["brand"]},
                "sku": offer["sku"],
                "offers": {
                    "@type": "Offer",
                    "url": offer["url"],
                    "price": offer["price"],
                    "priceCurrency": offer["priceCurrency"],
                    "availability": offer["availability"],
                    "priceValidUntil": offer["priceValidUntil"],
                    "seller": {"@type": "Organization", "name": offer["seller"]},
                },
            }
        )
    return entity


def json_ld(route: dict, manifest: dict, offers: dict[str, dict]) -> dict:
    host = manifest["canonicalHost"].rstrip("/")
    page_path = route["path"]
    page_url = host + page_path
    list_items = []
    for position, product in enumerate(route["products"], start=1):
        entity = product_entity(
            host=host,
            page_path=page_path,
            product=product,
            offers=offers,
        )
        list_items.append(
            {
                "@type": "ListItem",
                "position": position,
                "url": entity["url"],
                "item": entity,
            }
        )
    faq_items = []
    for item in route.get("faq", []):
        faq_items.append(
            {
                "@type": "Question",
                "@id": page_url + "#" + item["id"],
                "url": page_url + "#" + item["id"],
                "name": item["question"],
                "acceptedAnswer": {"@type": "Answer", "text": item["answer"]},
            }
        )
    graph: list[dict] = [
        {
            "@type": "ItemList",
            "@id": page_url + "#teknik-cozum-urunleri",
            "name": route["title"],
            "description": route["intro"],
            "itemListOrder": "https://schema.org/ItemListOrderAscending",
            "numberOfItems": len(list_items),
            "itemListElement": list_items,
        }
    ]
    if faq_items:
        graph.append(
            {
                "@type": "FAQPage",
                "@id": page_url + "#cozum-urunleri-sss",
                "mainEntity": faq_items,
            }
        )
    return {"@context": "https://schema.org", "@graph": graph}


def product_card(product: dict) -> str:
    return f'''<article class="alo186-ai-commerce-v250__card" id="{html.escape(product['id'])}">
<h3>{html.escape(product['name'])}</h3>
<dl>
<dt>En uygun senaryo</dt><dd>{html.escape(product['bestFor'])}</dd>
<dt>Teknik kontrol</dt><dd>{html.escape(product['technicalCheck'])}</dd>
<dt>Satın almama / sınır</dt><dd>{html.escape(product['skipWhen'])} {html.escape(product['limit'])}</dd>
</dl>
<a class="alo186-ai-commerce-v250__guide" href="{html.escape(product['guideUrl'])}">{html.escape(product['guideLabel'])} →</a>
</article>'''


def comparison_row(product: dict) -> str:
    return f'''<tr id="tablo-{html.escape(product['id'])}">
<th scope="row"><a href="#{html.escape(product['id'])}">{html.escape(product['name'])}</a></th>
<td>{html.escape(product['bestFor'])}</td>
<td>{html.escape(product['technicalCheck'])}</td>
<td>{html.escape(product['limit'])}</td>
</tr>'''


def faq_html(item: dict) -> str:
    return f'''<details id="{html.escape(item['id'])}">
<summary>{html.escape(item['question'])}</summary>
<p>{html.escape(item['answer'])} <a href="{html.escape(item['linkUrl'])}">{html.escape(item['linkText'])} →</a></p>
</details>'''


def section_html(route: dict, manifest: dict, offers: dict[str, dict]) -> str:
    cards = "\n".join(product_card(product) for product in route["products"])
    rows = "\n".join(comparison_row(product) for product in route["products"])
    faq = "\n".join(faq_html(item) for item in route.get("faq", []))
    payload = json.dumps(
        json_ld(route, manifest, offers),
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    return f'''<section class="alo186-ai-commerce-v250" {MARKER} data-rendering="static-prerender" aria-labelledby="teknik-cozum-urunleri">
<span class="alo186-ai-commerce-v250__eyebrow">Sorundan ürüne · statik ve taranabilir karar katmanı</span>
<h2 id="teknik-cozum-urunleri">{html.escape(route['title'])}</h2>
<p class="alo186-ai-commerce-v250__lead">{html.escape(route['intro'])}</p>
<p class="alo186-ai-commerce-v250__notice"><strong>Ticari şeffaflık:</strong> Önce teknik ihtiyacı ve mevcut ekipmanı doğrulayın. ALO186 fiyat, stok, puan veya garanti iddiası üretmez. Amazon bağlantısı varsa satış ortaklığı olarak işaretlenir.</p>
<div class="alo186-ai-commerce-v250__table-wrap" role="region" aria-label="Ürün sınıfı karşılaştırma tablosu" tabindex="0">
<table>
<caption>{html.escape(route['title'])}</caption>
<thead><tr><th scope="col">Çözüm sınıfı</th><th scope="col">En uygun senaryo</th><th scope="col">Doğrulanacak teknik değer</th><th scope="col">Sınır</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</div>
<div class="alo186-ai-commerce-v250__grid">{cards}</div>
<div class="alo186-ai-commerce-v250__faq" id="cozum-urunleri-sss">{faq}</div>
<p class="alo186-ai-commerce-v250__meta">Şema politikası: Product sınıfları görünür içerikle eşleşir; Offer yalnız doğrulanmış fiyat, stok, satıcı ve son geçerlilik tarihi bulunduğunda fail-closed katalogdan üretilir.</p>
<script type="application/ld+json" {SCHEMA_MARKER}>{payload}</script>
</section>'''


def inject_style(html_text: str) -> str:
    if STYLE_MARKER in html_text:
        return html_text
    link = f'<link rel="stylesheet" href="/{STYLE_TARGET.as_posix()}" {STYLE_MARKER}>'
    updated, count = re.subn(
        r"</head\s*>",
        link + "\n</head>",
        html_text,
        count=1,
        flags=re.IGNORECASE,
    )
    if count != 1:
        raise RuntimeError("AI commerce style için </head> bulunamadı.")
    return updated


def inject_section(html_text: str, section: str) -> str:
    if MARKER in html_text:
        return html_text
    updated, count = re.subn(
        r"</main\s*>",
        section + "\n</main>",
        html_text,
        count=1,
        flags=re.IGNORECASE,
    )
    if count == 1:
        return updated
    updated, count = re.subn(
        r"</body\s*>",
        section + "\n</body>",
        html_text,
        count=1,
        flags=re.IGNORECASE,
    )
    if count != 1:
        raise RuntimeError("AI commerce SSR bölümü için </main> veya </body> bulunamadı.")
    return updated


def annotate_amazon_links(html_text: str) -> tuple[str, int]:
    pattern = re.compile(r"<a\b[^>]*>", re.IGNORECASE | re.DOTALL)
    changed = 0

    def rewrite(match: re.Match[str]) -> str:
        nonlocal changed
        tag = match.group(0)
        href_match = re.search(
            r"\bhref\s*=\s*([\"'])(.*?)\1",
            tag,
            re.IGNORECASE | re.DOTALL,
        )
        if not href_match:
            return tag
        parsed = urlsplit(html.unescape(href_match.group(2)).strip())
        if parsed.hostname not in AMAZON_HOSTS:
            return tag
        rel_match = re.search(
            r"\brel\s*=\s*([\"'])(.*?)\1",
            tag,
            re.IGNORECASE | re.DOTALL,
        )
        tokens = []
        if rel_match:
            tokens.extend(rel_match.group(2).split())
        normalized = []
        for token in [*tokens, *REQUIRED_REL]:
            if token.casefold() not in {value.casefold() for value in normalized}:
                normalized.append(token)
        rel_value = " ".join(normalized)
        if rel_match:
            updated = tag[: rel_match.start()] + f'rel="{rel_value}"' + tag[rel_match.end() :]
        else:
            updated = tag[:-1].rstrip() + f' rel="{rel_value}">'
        if updated != tag:
            changed += 1
        return updated

    return pattern.sub(rewrite, html_text), changed


def route_file(output: Path, relative: str) -> Path:
    return output / relative


def validate_internal_link(output: Path, page_file: Path, url: str) -> bool:
    if url.startswith("#"):
        target_id = url[1:]
        text = page_file.read_text(encoding="utf-8")
        return bool(re.search(rf'\bid=["\']{re.escape(target_id)}["\']', text))
    path = url.split("#", 1)[0].split("?", 1)[0].strip("/")
    if not path:
        return True
    direct = output / path
    return direct.is_file() or (direct / "index.html").is_file() or (output / (path + ".html")).is_file()


def audit(output: Path, manifest: dict, offers: dict[str, dict]) -> dict:
    failures: list[str] = []
    route_reports: list[dict] = []
    all_ids: dict[str, str] = {}
    item_list_count = product_count = faq_count = offer_count = 0
    direct_amazon_links = annotated_amazon_links = 0

    for route in manifest["routes"]:
        path = route_file(output, route["file"])
        if not path.is_file():
            failures.append(f"Hedef artifact rotası eksik: {route['file']}")
            continue
        text = path.read_text(encoding="utf-8")
        if text.count(MARKER) != 1:
            failures.append(f"AI commerce marker tekil değil: {route['path']}")
        if 'data-rendering="static-prerender"' not in text:
            failures.append(f"SSR/static-prerender işareti eksik: {route['path']}")
        if "<table" not in text or "<tbody" not in text:
            failures.append(f"Semantik karşılaştırma tablosu eksik: {route['path']}")
        ids = re.findall(r'\bid=["\']([^"\']+)["\']', text)
        duplicates = sorted({value for value in ids if ids.count(value) > 1})
        if duplicates:
            failures.append(f"Yinelenen id ({route['path']}): {', '.join(duplicates)}")
        for product in route["products"]:
            if product["id"] not in ids:
                failures.append(f"Ürün deep-link id eksik: {route['path']}#{product['id']}")
            owner = all_ids.setdefault(product["id"], route["path"])
            if owner != route["path"]:
                failures.append(f"Site genelinde yinelenen ürün id: {product['id']}")
            if not validate_internal_link(output, path, product["guideUrl"]):
                failures.append(f"Ürün rehber linki kırık: {product['guideUrl']}")
        for item in route.get("faq", []):
            if item["id"] not in ids:
                failures.append(f"FAQ deep-link id eksik: {route['path']}#{item['id']}")
            if not validate_internal_link(output, path, item["linkUrl"]):
                failures.append(f"FAQ çözüm linki kırık: {route['path']} -> {item['linkUrl']}")

        blocks = re.findall(
            rf'<script\b[^>]*{re.escape(SCHEMA_MARKER)}[^>]*>(.*?)</script>',
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if len(blocks) != 1:
            failures.append(f"JSON-LD v250 tekil değil: {route['path']}")
        else:
            try:
                payload = json.loads(blocks[0].replace("<\\/", "</"))
            except json.JSONDecodeError as exc:
                failures.append(f"JSON-LD parse hatası ({route['path']}): {exc}")
            else:
                graph = payload.get("@graph") or []
                lists = [node for node in graph if node.get("@type") == "ItemList"]
                faqs = [node for node in graph if node.get("@type") == "FAQPage"]
                if len(lists) != 1:
                    failures.append(f"ItemList eksik/çoğul: {route['path']}")
                else:
                    item_list_count += 1
                    items = lists[0].get("itemListElement") or []
                    if len(items) != len(route["products"]):
                        failures.append(f"ItemList ürün sayısı yanlış: {route['path']}")
                    for list_item in items:
                        product = list_item.get("item") or {}
                        if product.get("@type") != "Product":
                            failures.append(f"ItemList Product taşımıyor: {route['path']}")
                        product_count += 1
                        if "offers" in product:
                            offer_count += 1
                if route.get("faq") and len(faqs) != 1:
                    failures.append(f"FAQPage eksik/çoğul: {route['path']}")
                faq_count += len(faqs)

        for anchor in re.findall(r"<a\b[^>]*>", text, re.IGNORECASE | re.DOTALL):
            href_match = re.search(r"\bhref\s*=\s*([\"'])(.*?)\1", anchor, re.IGNORECASE | re.DOTALL)
            if not href_match:
                continue
            parsed = urlsplit(html.unescape(href_match.group(2)).strip())
            if parsed.hostname not in AMAZON_HOSTS:
                continue
            direct_amazon_links += 1
            rel_match = re.search(r"\brel\s*=\s*([\"'])(.*?)\1", anchor, re.IGNORECASE | re.DOTALL)
            tokens = {token.casefold() for token in (rel_match.group(2).split() if rel_match else [])}
            if set(REQUIRED_REL).issubset(tokens):
                annotated_amazon_links += 1
            else:
                failures.append(f"Amazon rel eksik: {route['path']}")

        route_reports.append(
            {
                "route": route["path"],
                "productAnchorCount": len(route["products"]),
                "faqAnchorCount": len(route.get("faq", [])),
                "staticComparisonTable": True,
                "jsonLdTypes": ["ItemList", "ListItem", "Product", "FAQPage"],
            }
        )

    if offer_count != len(offers):
        failures.append(
            f"Fail-closed Offer sayısı yanlış: emitted={offer_count}, verified={len(offers)}"
        )
    llms = output / LLMS_TARGET
    robots = output / "robots.txt"
    css = output / STYLE_TARGET
    if not llms.is_file():
        failures.append("llms.txt artifactta eksik")
    if not robots.is_file():
        failures.append("robots.txt artifactta eksik")
    if not css.is_file():
        failures.append("AI commerce CSS artifactta eksik")

    report = {
        "ok": not failures,
        "version": VERSION,
        "generatedAt": manifest["generatedAt"],
        "routeCount": len(route_reports),
        "itemListCount": item_list_count,
        "productEntityCount": product_count,
        "faqPageCount": faq_count,
        "verifiedOfferCount": len(offers),
        "emittedOfferCount": offer_count,
        "offerPolicy": manifest["offerPolicy"]["mode"],
        "directAmazonLinkCount": direct_amazon_links,
        "annotatedAmazonLinkCount": annotated_amazon_links,
        "staticPrerendered": True,
        "javascriptRequiredForCoreRecommendations": False,
        "routes": route_reports,
        "externalValidatorStatus": {
            "googleRichResults": "tool-ready; Product rich-result eligibility intentionally unavailable without verified offers/reviews",
            "schemaOrg": "JSON-LD parsed and type/property contracts checked locally; live URL validation follows deployment",
        },
        "failures": failures,
    }
    if failures:
        raise RuntimeError("AI commerce AEO v250 denetimi başarısız:\n- " + "\n- ".join(failures))
    return report


def apply_ai_commerce_aeo(repo_root: Path, output: Path) -> dict:
    manifest = load_manifest(repo_root)
    offers = validated_offers(manifest)
    style_source = repo_root / STYLE_SOURCE
    if not style_source.is_file():
        raise FileNotFoundError(f"AI commerce CSS kaynağı eksik: {style_source}")
    style_target = output / STYLE_TARGET
    style_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(style_source, style_target)

    llms_source = repo_root / LLMS_SOURCE
    if not llms_source.is_file():
        raise FileNotFoundError(f"llms.txt kaynağı eksik: {llms_source}")
    shutil.copy2(llms_source, output / LLMS_TARGET)

    robots_source = repo_root / ROBOTS_SOURCE
    if not robots_source.is_file():
        raise FileNotFoundError(f"robots.txt kaynağı eksik: {robots_source}")
    shutil.copy2(robots_source, output / ROBOTS_TARGET)

    injected = already = amazon_links_changed = 0
    target_files = {route["file"] for route in manifest["routes"]}
    for route in manifest["routes"]:
        path = output / route["file"]
        if not path.is_file():
            raise FileNotFoundError(f"AI commerce hedef rotası artifactta eksik: {route['file']}")
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            already += 1
        else:
            text = inject_style(text)
            text = inject_section(text, section_html(route, manifest, offers))
            injected += 1
        text, changed = annotate_amazon_links(text)
        amazon_links_changed += changed
        path.write_text(text, encoding="utf-8")

    for path in sorted(output.rglob("*.html")):
        relative = path.relative_to(output).as_posix()
        if relative in target_files:
            continue
        if any(relative.startswith(prefix) for prefix in SAFETY_ROUTE_PREFIXES):
            continue
        text = path.read_text(encoding="utf-8")
        updated, changed = annotate_amazon_links(text)
        if changed:
            path.write_text(updated, encoding="utf-8")
            amazon_links_changed += changed

    report = audit(output, manifest, offers)
    report.update(
        {
            "injectedRouteCount": injected,
            "alreadyInjectedRouteCount": already,
            "amazonRelAnnotationsAdded": amazon_links_changed,
            "affiliateTag": manifest["affiliateTag"],
        }
    )
    (output / VALIDATION_TARGET).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report
