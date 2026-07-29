from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import quote_plus

HOST = "https://www.alo186.com"
CONFIG = Path("alo186/urun-rehberleri/commerce-guides.json")
COLLECTION = "/urun-rehberleri/"


def e(value) -> str:
    return html.escape(str(value), quote=True)


def load(repo_root: Path) -> dict:
    data = json.loads((repo_root / CONFIG).read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1 or data.get("canonicalHost") != HOST:
        raise ValueError("Ticari rehber şeması veya canonical host geçersiz")
    guides = data.get("guides")
    if not isinstance(guides, list) or len(guides) < 8:
        raise ValueError("En az sekiz ticari rehber gerekir")
    seen: set[str] = set()
    for item in guides:
        slug = str(item.get("slug", ""))
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in seen:
            raise ValueError(f"Geçersiz veya yinelenen slug: {slug}")
        seen.add(slug)
        if len(item.get("criteria", [])) < 4 or len(item.get("faqs", [])) < 3 or len(item.get("noBuy", [])) < 3:
            raise ValueError(f"Kalite kapsamı yetersiz: {slug}")
        if item.get("affiliateEnabled"):
            if item.get("affiliatePolicy") != "qualified_search" or len(item.get("gateChecks", [])) < 3:
                raise ValueError(f"Nitelikli affiliate kapısı eksik: {slug}")
            if not item.get("amazonSearchQuery"):
                raise ValueError(f"Amazon arama sorgusu eksik: {slug}")
        elif item.get("affiliatePolicy") != "professional_only" or item.get("amazonSearchQuery"):
            raise ValueError(f"Profesyonel-only ticari sınır hatalı: {slug}")
    return data


def canonical(slug: str) -> str:
    return f"{HOST}/urun-rehberleri/{slug}"


def jsonld(item: dict, date: str) -> str:
    url = canonical(item["slug"])
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "headline": item["h1"],
                "description": item["description"],
                "datePublished": date,
                "dateModified": date,
                "inLanguage": "tr-TR",
                "mainEntityOfPage": url,
                "author": {"@type": "Organization", "name": "ALO186"},
                "publisher": {"@type": "Organization", "name": "ALO186", "url": HOST},
                "isPartOf": {"@type": "CollectionPage", "name": "ALO186 Elektrik Ürün Rehberleri", "url": HOST + COLLECTION},
                "about": [{"@type": "DefinedTerm", "name": term} for term in item["terms"]],
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": row["question"], "acceptedAnswer": {"@type": "Answer", "text": row["answer"]}}
                    for row in item["faqs"]
                ],
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "ALO186", "item": HOST},
                    {"@type": "ListItem", "position": 2, "name": "Ürün rehberleri", "item": HOST + COLLECTION},
                    {"@type": "ListItem", "position": 3, "name": item["h1"], "item": url},
                ],
            },
        ],
    }
    return json.dumps(graph, ensure_ascii=False, separators=(",", ":"))


def guide_html(item: dict, data: dict) -> str:
    cards = "".join(f'<article class="card"><h3>{e(row["title"])}</h3><p>{e(row["text"])}</p></article>' for row in item["whoFor"])
    rows = "".join(f'<tr><th scope="row">{e(row["name"])}</th><td>{e(row["verify"])}</td><td>{e(row["avoid"])}</td></tr>' for row in item["criteria"])
    no_buy = "".join(f"<li>{e(value)}</li>" for value in item["noBuy"])
    faq = "".join(f'<details><summary>{e(row["question"])}</summary><p>{e(row["answer"])}</p></details>' for row in item["faqs"])
    related = "".join(f'<a class="button secondary" href="{e(row["path"])}">{e(row["label"])}</a>' for row in item["related"])
    marker = ' data-alo186-affiliate-gate="qualified"' if item["affiliateEnabled"] else ""
    if item["affiliateEnabled"]:
        checks = "".join(f'<label class="gate-check"><input type="checkbox" data-commerce-check><span>{e(value)}</span></label>' for value in item["gateChecks"])
        amazon = f'https://www.amazon.com.tr/s?k={quote_plus(item["amazonSearchQuery"])}&tag={quote_plus(data["affiliateTag"])}'
        gate = f'''<section id="amazon" class="commerce-gate" data-commerce-gate data-category="{e(item["category"])}" data-affiliate-policy="qualified_search"><span class="eyebrow">Nitelikli Amazon arama kapısı</span><h2>Teknik kontroller tamamlanmadan mağaza aramasını açmayın.</h2><p class="affiliate"><strong>Reklam / satış ortaklığı:</strong> Aşağıdaki Amazon bağlantısı satış ortaklığı bağlantısıdır. Nitelikli satın alımlardan komisyon kazanılabilir; kullanıcıya ek maliyet yansımaz. Bu bağlantı ürün önerisi değildir. Fiyat, stok, satıcı, teslimat, garanti ve nihai teknik özellik Amazon’un güncel sayfasında doğrulanır.</p><div class="gate-checks">{checks}</div><p class="gate-status" data-commerce-status role="status">Teknik kontroller bekleniyor.</p><a class="button affiliate-link" data-affiliate-link href="{e(amazon)}" target="_blank" rel="sponsored nofollow noopener" aria-disabled="true" tabindex="-1">Amazon’da teknik aramayı aç</a><p class="affiliate">Mevcut ürününüz ihtiyacınızı karşılıyorsa satın almayın. Arama sonuçları uygunluk onayı değildir.</p></section>'''
    else:
        gate = f'''<section id="amazon" class="danger" data-affiliate-policy="professional_only"><h2>Bu kategoride doğrudan mağaza bağlantısı yok</h2><p>Sabit tesisat ve proje uyumu gerektiren bu kategoride yanlış ürün seçimi ciddi risk oluşturabilir. ALO186 Amazon veya başka mağaza bağlantısı açmaz; önce proje değerleri ve profesyonel doğrulama gerekir.</p><p><a class="button" href="{e(item["toolPath"])}">{e(item["toolLabel"])}</a></p></section>'''
    return f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>{e(item["title"])}</title><meta name="description" content="{e(item["description"])}"><meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#071631"><link rel="canonical" href="{canonical(item["slug"])}"><link rel="stylesheet" href="/haberler/alo186-article.css"><link rel="stylesheet" href="/urun-rehberleri/commerce-guide.css"><script type="application/ld+json">{jsonld(item, data["generatedAt"])}</script></head><body data-alo186-commerce-guide="true" data-commerce-category="{e(item["category"])}" data-risk="{e(item["risk"])}" data-affiliate-policy="{e(item["affiliatePolicy"])}"><header class="top"><div class="wrap"><a class="brand" href="/"><span>186</span><div><strong>ALO186</strong><small>Bağımsız elektrik bilgi ağı</small></div></a><nav aria-label="Ana bağlantılar"><a href="/urun-rehberleri/">Ürün rehberleri</a><a href="{e(item["toolPath"])}">Ücretsiz test</a><a href="/akilli-urun-secimi">Akıllı ürün merkezi</a></nav></div></header><main class="wrap"><article{marker}><header class="hero"><span class="eyebrow">{e(item["eyebrow"])}</span><h1>{e(item["h1"])}</h1><p class="lead">{e(item["description"])}</p><div class="meta"><span>Son editoryal doğrulama: 29 Temmuz 2026</span><span>Amazon fiyatı, stok ve puanı kopyalanmaz</span><span>Mevcut ürün yeterliyse satın almama sonucu korunur</span></div></header><div class="answer"><strong>Doğrudan cevap</strong>{e(item["answer"])}</div><div class="layout"><div class="article"><section id="kime-uygun"><h2>Bu rehber hangi ihtiyaçlar için?</h2><div class="grid">{cards}</div></section><section id="kriterler"><h2>Satın almadan önce karşılaştırılacak teknik alanlar</h2><div class="table-wrap"><table><thead><tr><th>Alan</th><th>Doğrulayın</th><th>Kaçının</th></tr></thead><tbody>{rows}</tbody></table></div></section><section id="satinalmama"><h2>Yeni ürün almamanız gereken durumlar</h2><ul class="checklist">{no_buy}</ul></section><section class="cta" id="ucretsiz-kontrol"><h2>Önce ücretsiz uygunluk kontrolünü tamamlayın.</h2><p>Hesabı tamamladıktan sonra seçiminizi Akıllı Ürün Merkezi’nde kategori filtresiyle yeniden kontrol edin.</p><div class="buttons"><a class="button" href="{e(item["toolPath"])}">{e(item["toolLabel"])}</a><a class="button secondary" href="{e(item["productCenterPath"])}">Kategori ürün merkezini aç</a></div></section>{gate}<section class="faq" id="sss"><h2>Sık sorulan sorular</h2>{faq}</section><section id="ilgili"><h2>İlgili ücretsiz araç ve rehberler</h2><div class="buttons">{related}</div></section><section id="yontem"><h2>Yayın ve ticari güven yöntemi</h2><p>Bu sayfa ürünleri fiyat, stok, puan, satıcı, marka komisyonu veya garanti iddiasıyla sıralamaz. Amazon araması yalnız görünür kontrol listesi tamamlandığında açılır; profesyonel seçim gereken kategoride mağaza bağlantısı kapalıdır.</p></section></div><aside class="toc"><strong>Sayfa özeti</strong><a href="#kime-uygun">Kullanım alanları</a><a href="#kriterler">Teknik kriterler</a><a href="#satinalmama">Satın almama</a><a href="#ucretsiz-kontrol">Ücretsiz kontrol</a><a href="#amazon">Amazon kapısı</a><a href="#sss">SSS</a></aside></div></article></main><footer class="footer"><div class="wrap"><strong>ALO186</strong><p>Bağımsız bilgilendirme platformudur; ürün satıcısı veya resmî kurum değildir. 112 ve 186 yönlendirmelerinde ticari bağlantı gösterilmez.</p></div></footer><script src="/urun-rehberleri/commerce-guide.js" defer></script></body></html>'''


def hub_html(data: dict) -> str:
    cards = []
    for item in data["guides"]:
        policy = "Nitelikli Amazon araması" if item["affiliateEnabled"] else "Mağaza bağlantısı kapalı"
        cards.append(f'<article class="card commerce-card"><span class="eyebrow">{e(item["risk"])} · {e(policy)}</span><h2>{e(item["h1"])}</h2><p>{e(item["description"])}</p><a class="button card-link" href="/urun-rehberleri/{e(item["slug"])}">Rehberi aç</a></article>')
    item_list = [{"@type": "ListItem", "position": index, "name": item["h1"], "url": canonical(item["slug"])} for index, item in enumerate(data["guides"], start=1)]
    schema = {"@context": "https://schema.org", "@type": "CollectionPage", "name": data["collection"]["h1"], "description": data["collection"]["description"], "url": HOST + COLLECTION, "dateModified": data["generatedAt"], "mainEntity": {"@type": "ItemList", "numberOfItems": len(item_list), "itemListElement": item_list}}
    return f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>{e(data["collection"]["title"])}</title><meta name="description" content="{e(data["collection"]["description"])}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{HOST}{COLLECTION}"><link rel="stylesheet" href="/haberler/alo186-article.css"><link rel="stylesheet" href="/urun-rehberleri/commerce-guide.css"><script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script></head><body data-alo186-commerce-collection="true"><header class="top"><div class="wrap"><a class="brand" href="/"><span>186</span><div><strong>ALO186</strong><small>Bağımsız elektrik bilgi ağı</small></div></a><nav aria-label="Ana bağlantılar"><a href="/elektrik-portali">Portal</a><a href="/hesaplama/">Hesaplayıcılar</a><a href="/akilli-urun-secimi">Akıllı ürün merkezi</a></nav></div></header><main class="wrap"><header class="hero"><span class="eyebrow">8 kategori · Amazon satış ortaklığı · satın almama koruması</span><h1>{e(data["collection"]["h1"])}</h1><p class="lead">{e(data["collection"]["lead"])}</p><div class="meta"><span>Fiyat ve stok gösterilmez</span><span>Ücretsiz araç önce gelir</span><span>Sabit tesisatta affiliate kapalıdır</span></div></header><div class="answer"><strong>Ticari şeffaflık</strong>ALO186 ürün satıcısı değildir. Düşük riskli sayfalardaki Amazon bağlantıları satış ortaklığı bağlantısıdır; nitelikli satın alımlardan komisyon kazanılabilir ve kullanıcıya ek maliyet yansımaz. Komisyon sayfa sırasını veya teknik sonucu değiştiremez.</div><section class="article"><h2>İhtiyaca göre ürün rehberleri</h2><div class="guide-catalog">{''.join(cards)}</div></section><section class="cta"><h2>Üründen önce ihtiyacı eşleştirin.</h2><p>Mevcut ekipman yeterliyse satın almama sonucu veren ve teknik veri eksikse Amazon bağlantısını kapatan karar aracını kullanın.</p><div class="buttons"><a class="button" href="/akilli-urun-secimi">Akıllı ürün merkezini aç</a><a class="button secondary" href="/hesaplama/">Ücretsiz hesaplayıcıları aç</a></div></section></main><footer class="footer"><div class="wrap"><strong>ALO186</strong><p>Bağımsız elektrik bilgi ağıdır; Amazon veya dağıtım şirketi değildir. Acil durumda 112, elektrik dağıtım arızasında 186 kullanılır.</p></div></footer></body></html>'''


def generate(repo_root: Path, output_root: Path) -> dict:
    data = load(repo_root)
    target = output_root / "urun-rehberleri"
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.html").write_text(hub_html(data), encoding="utf-8")
    for item in data["guides"]:
        folder = target / item["slug"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "index.html").write_text(guide_html(item, data), encoding="utf-8")
    release = {"schemaVersion": 1, "generatedAt": data["generatedAt"], "collectionPath": COLLECTION, "guideCount": len(data["guides"]), "affiliateEnabledCount": sum(1 for item in data["guides"] if item["affiliateEnabled"]), "professionalOnlyCount": sum(1 for item in data["guides"] if not item["affiliateEnabled"]), "staticPricesStored": False, "staticStockStored": False, "guides": [{"slug": item["slug"], "canonicalPath": f'/urun-rehberleri/{item["slug"]}', "category": item["category"], "risk": item["risk"], "affiliatePolicy": item["affiliatePolicy"], "affiliateEnabled": bool(item["affiliateEnabled"]), "toolPath": item["toolPath"]} for item in data["guides"]]}
    (target / "commerce-release.json").write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return release


def inject_collection_link(site: Path) -> bool:
    target = site / "akilli-urun-secimi" / "index.html"
    if not target.is_file():
        return False
    text = target.read_text(encoding="utf-8")
    updated = text.replace("https://www.alo186.com/amazon-elektrik-urunleri", COLLECTION).replace('href="/amazon-elektrik-urunleri"', f'href="{COLLECTION}"')
    if updated == text:
        return False
    target.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 kaliteli ticari ürün rehberlerini üretir")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(generate(args.repo_root.resolve(), args.output.resolve()), ensure_ascii=False))


if __name__ == "__main__":
    main()
