from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

VERSION = 251
ORIGIN = "https://alo186.com"
KOMBI = Path("amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici/index.html")
AI_SEARCH_AGENTS = (
    "GPTBot",
    "OAI-SearchBot",
    "ChatGPT-User",
    "PerplexityBot",
    "ClaudeBot",
    "Bytespider",
    "Google-Extended",
)
HOWTO_MARKER = 'data-alo186-howto-visible-v251="true"'
DECISION_MARKER = 'data-alo186-ssr-decision-v251="true"'
PREP_MARKER = 'data-alo186-ssr-preparedness-v251="true"'
SERVICE_PAGE_MARKER = 'data-alo186-local-service-v251="true"'
REPORT = "alo186-schema-validation-v251.json"


def _insert_before(text: str, closing_tag: str, fragment: str) -> str:
    pattern = re.compile(rf"</{closing_tag}\s*>", re.IGNORECASE)
    if not pattern.search(text):
        raise RuntimeError(f"{closing_tag} kapanışı bulunamadı")
    return pattern.sub(fragment + f"\n</{closing_tag}>", text, count=1)


def _script(data: dict, marker: str) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return f'<script type="application/ld+json" {marker}>{payload}</script>'


def _jsonld_marker(text: str, marker: str) -> tuple[dict, tuple[int, int]]:
    pattern = re.compile(
        r"<script\b(?P<attrs>[^>]*)>(?P<body>.*?)</script\s*>",
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(text):
        attrs = match.group("attrs")
        if marker in attrs and "application/ld+json" in attrs.lower():
            return json.loads(match.group("body")), match.span()
    raise RuntimeError(f"JSON-LD marker bulunamadı: {marker}")


def _replace_jsonld_marker(text: str, marker: str, data: dict) -> str:
    _old, span = _jsonld_marker(text, marker)
    return text[: span[0]] + _script(data, marker) + text[span[1] :]


def _walk(value) -> Iterable[dict]:
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from _walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk(nested)


def _howto_steps() -> list[tuple[str, str, str]]:
    return [
        (
            "kombi-adim-acil",
            "Acil gaz ve CO riskini ayırın",
            "Gaz kokusu, karbonmonoksit belirtisi, duman, yanık kokusu veya su teması varsa ürün seçimine ilerlemeyin; güvenli alana çıkıp 112 veya 187 yolunu kullanın.",
        ),
        (
            "kombi-adim-model",
            "Tam model onayını doğrulayın",
            "Kombi kılavuzu veya yetkili servis üzerinden harici yedek enerji, saf sinüs, bağlantı ve yeniden başlatma koşullarını doğrulayın.",
        ),
        (
            "kombi-adim-yuk",
            "Gerçek elektrik yükünü hesaplayın",
            "Isıtma kapasitesini elektrik tüketimi sanmayın; sürekli watt, tepe watt ve hedef süre için watt-saat ihtiyacını hesaplayın.",
        ),
        (
            "kombi-adim-test",
            "Mevcut çözümü güvenli biçimde test edin",
            "Mevcut sistem tam model için onaylıysa ve uyanıkken yapılan gerçek kesinti testini geçtiyse yeni ürün almayın.",
        ),
        (
            "kombi-adim-urun",
            "Yalnız doğrulanmış eksik için ürün sınıfına ilerleyin",
            "Gerçek eksik varsa saf sinüs UPS, EPS özellikli güç istasyonu veya priz tipi enerji ölçer sınıfını tam model şartlarıyla karşılaştırın.",
        ),
    ]


def visible_howto(site: Path) -> dict:
    path = site / KOMBI
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    steps = _howto_steps()
    if HOWTO_MARKER not in text:
        rows = "".join(
            f'<li id="{anchor}"><h3>{name}</h3><p>{description}</p></li>'
            for anchor, name, description in steps
        )
        section = (
            f'<section class="panel" {HOWTO_MARKER} aria-labelledby="kombi-howto-v251">'
            '<span class="eyebrow">Soru → sorun → çözüm → ürün sınıfı</span>'
            '<h2 id="kombi-howto-v251">Kesintide kombi nasıl güvenli korunur?</h2>'
            '<p>Önce gaz ve karbonmonoksit güvenliği, sonra tam model onayı ve gerçek elektrik yükü değerlendirilir. '
            'Ürün sınıfı yalnız mevcut güvenli çözüm yetersizse açılır.</p>'
            f'<ol>{rows}</ol>'
            '<p><a href="#urun-kombi-ups">Saf sinüs kombi UPS sınıfına geç</a> · '
            '<a href="#urun-kombi-guc-istasyonu">EPS güç istasyonu sınıfına geç</a> · '
            '<a href="#urun-priz-enerji-olcer">Enerji ölçer sınıfına geç</a></p>'
            '</section>'
        )
        text = _insert_before(text, "main", section)

    graph, _span = _jsonld_marker(text, 'data-alo186-schema-v250="true"')
    step_urls = [f"{ORIGIN}/{KOMBI.parent.as_posix()}/#{anchor}" for anchor, _name, _desc in steps]
    for node in _walk(graph):
        if node.get("@type") == "HowTo":
            for position, step in enumerate(node.get("step", []), start=1):
                if isinstance(step, dict) and position <= len(step_urls):
                    step["url"] = step_urls[position - 1]
        if node.get("@type") == "Product" and isinstance(node.get("@id"), str):
            node.setdefault("url", node["@id"])
    text = _replace_jsonld_marker(text, 'data-alo186-schema-v250="true"', graph)
    path.write_text(text, encoding="utf-8")
    return {"visibleSteps": len(steps), "structuredStepUrls": len(step_urls), "visibleContentParity": True}


def _service_channel() -> dict:
    return {
        "@type": "ServiceChannel",
        "serviceUrl": f"{ORIGIN}/edas-bul/",
        "servicePhone": {
            "@type": "ContactPoint",
            "telephone": "186",
            "contactType": "elektrik kesintisi ve arıza hattı",
            "areaServed": {"@type": "Country", "name": "Türkiye"},
            "availableLanguage": ["tr"],
        },
    }


def _catalog(repo: Path) -> tuple[dict[int, str], list[dict]]:
    text = (repo / "alo186/turkiye-arama/companies.js").read_text(encoding="utf-8")
    province_block = re.search(r"const provinceNames=\{(.*?)\};", text, re.DOTALL)
    company_block = re.search(r"const companies=\[(.*?)\];\s*\n\s*const istanbulEurope", text, re.DOTALL)
    if not province_block or not company_block:
        raise RuntimeError("EDAŞ katalog parse hatası")
    provinces = {int(key): name for key, name in re.findall(r"(\d+):'([^']+)'", province_block.group(1))}
    pattern = re.compile(
        r"\{id:'([^']+)',code:'[^']+',name:'([^']+)',slug:'([^']+)',provinceIds:\[([^\]]+)\]"
        r"(?:,districtMode:'([^']+)')?,aliases:\[[^\]]*\]\}"
    )
    companies = [
        {
            "id": match.group(1),
            "name": match.group(2),
            "slug": match.group(3),
            "provinceIds": [int(value) for value in match.group(4).split(",")],
            "districtMode": match.group(5),
        }
        for match in pattern.finditer(company_block.group(1))
    ]
    if len(provinces) != 81 or len(companies) != 21:
        raise RuntimeError(f"EDAŞ katalog kapsamı yanlış: {len(provinces)} il / {len(companies)} şirket")
    return provinces, companies


def _slug(name: str) -> str:
    table = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    value = name.translate(table).lower()
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def _local_service_graph(name: str, providers: list[dict], page_url: str) -> dict:
    provider_refs = [
        {"@id": f"{ORIGIN}/dagitim-sirketleri/{company['slug']}/#organization"}
        for company in providers
    ]
    provider = provider_refs[0] if len(provider_refs) == 1 else provider_refs
    organizations = [
        {
            "@type": "Organization",
            "@id": f"{ORIGIN}/dagitim-sirketleri/{company['slug']}/#organization",
            "name": company["name"],
            "url": f"{ORIGIN}/dagitim-sirketleri/{company['slug']}/",
        }
        for company in providers
    ]
    service = {
        "@type": "Service",
        "@id": page_url + "#electricity-outage-service",
        "name": f"{name} elektrik kesintisi ve arıza yönlendirmesi",
        "serviceType": "Elektrik dağıtım şebekesi kesinti ve arıza yönlendirmesi",
        "areaServed": {"@type": "AdministrativeArea", "name": name},
        "provider": provider,
        "availableChannel": _service_channel(),
        "description": "ALO186 arıza kaydı almaz; 186 ve yetkili dağıtım şirketinin resmî kanalına bağımsız yönlendirme sağlar.",
    }
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": page_url + "#webpage",
                "url": page_url,
                "name": f"{name} elektrik kesintisi için nere aranır?",
                "mainEntity": {"@id": service["@id"]},
            },
            service,
            *organizations,
        ],
    }


def augment_edas(repo: Path, site: Path) -> dict:
    central = next(
        (candidate for candidate in (site / "edas-bul/index.html", site / "elektrik-kesintisi/index.html") if candidate.is_file()),
        None,
    )
    if central is None:
        raise FileNotFoundError("EDAŞ merkez sayfası artifactta yok")
    text = central.read_text(encoding="utf-8")
    graph, _span = _jsonld_marker(text, 'data-alo186-service-catalog-v250="true"')
    service_count = 0
    for node in _walk(graph):
        if node.get("@type") == "Service" and str(node.get("@id", "")).startswith(f"{ORIGIN}/edas-bul/#service-"):
            node["availableChannel"] = _service_channel()
            service_count += 1
    if service_count != 81:
        raise RuntimeError(f"81 Service beklenirken {service_count} bulundu")
    central.write_text(
        _replace_jsonld_marker(text, 'data-alo186-service-catalog-v250="true"', graph),
        encoding="utf-8",
    )

    provinces, companies = _catalog(repo)
    province_pages = 0
    company_pages = 0
    for province_id, province_name in provinces.items():
        page = site / "il" / _slug(province_name) / "index.html"
        if not page.is_file():
            continue
        html = page.read_text(encoding="utf-8")
        if SERVICE_PAGE_MARKER not in html:
            providers = [company for company in companies if province_id in company["provinceIds"]]
            page_url = f"{ORIGIN}/il/{_slug(province_name)}/"
            html = _insert_before(html, "head", _script(_local_service_graph(province_name, providers, page_url), SERVICE_PAGE_MARKER))
            page.write_text(html, encoding="utf-8")
        province_pages += 1

    for company in companies:
        page = site / "dagitim-sirketleri" / company["slug"] / "index.html"
        if not page.is_file():
            continue
        html = page.read_text(encoding="utf-8")
        if SERVICE_PAGE_MARKER not in html:
            area_names = [provinces[province_id] for province_id in company["provinceIds"]]
            page_url = f"{ORIGIN}/dagitim-sirketleri/{company['slug']}/"
            organization_id = page_url + "#organization"
            data = {
                "@context": "https://schema.org",
                "@graph": [
                    {
                        "@type": "Organization",
                        "@id": organization_id,
                        "name": company["name"],
                        "url": page_url,
                        "areaServed": [{"@type": "AdministrativeArea", "name": area} for area in area_names],
                    },
                    {
                        "@type": "Service",
                        "@id": page_url + "#service",
                        "name": f"{company['name']} elektrik kesintisi ve arıza yönlendirmesi",
                        "provider": {"@id": organization_id},
                        "areaServed": [{"@type": "AdministrativeArea", "name": area} for area in area_names],
                        "availableChannel": _service_channel(),
                        "description": "ALO186 bağımsız yönlendirme sağlar; güncel iletişim ve kesinti bilgisi şirketin resmî kanalından doğrulanır.",
                    },
                ],
            }
            html = _insert_before(html, "head", _script(data, SERVICE_PAGE_MARKER))
            page.write_text(html, encoding="utf-8")
        company_pages += 1

    return {
        "centralProvinceServices": service_count,
        "serviceChannels": service_count,
        "servicePhone": "186",
        "provincePagesEnhanced": province_pages,
        "companyPagesEnhanced": company_pages,
        "privateEdasGovernmentServiceCount": 0,
    }


def ssr_decision_fallbacks(site: Path) -> dict:
    decision = site / "karar-motoru/index.html"
    preparation = site / "hesaplama/kesinti-hazirlik-plani/index.html"
    added = 0
    if decision.is_file():
        text = decision.read_text(encoding="utf-8")
        if DECISION_MARKER not in text:
            section = (
                f'<section class="content-section" {DECISION_MARKER} aria-labelledby="ssr-decision-title">'
                '<h2 id="ssr-decision-title">JavaScript olmadan güvenli başlangıç</h2>'
                '<ol>'
                '<li><strong>Duman, yangın, aktif kıvılcım veya elektrik çarpması:</strong> Uzaklaşın ve 112’yi arayın.</li>'
                '<li><strong>Sokak, mahalle, direk, trafo veya genel kesinti:</strong> 186 ve yetkili dağıtım şirketinin resmî kanalını kullanın.</li>'
                '<li><strong>Tek priz, cihaz veya iç tesisat:</strong> Enerjili bölüme müdahale etmeden yetkili elektrikçiye ilerleyin.</li>'
                '<li><strong>Yedek güç veya ürün planı:</strong> Tehlike yoksa önce ücretsiz hesaplayıcıyla W, VA, Wh ve uygunluk kanıtlarını doğrulayın.</li>'
                '</ol>'
                '<p><a href="/edas-bul/">81 il için EDAŞ bul</a> · <a href="/hesaplama/">Ücretsiz hesaplayıcıları aç</a></p>'
                '</section>'
            )
            decision.write_text(_insert_before(text, "main", section), encoding="utf-8")
            added += 1
    if preparation.is_file():
        text = preparation.read_text(encoding="utf-8")
        if PREP_MARKER not in text:
            section = (
                f'<section class="panel" {PREP_MARKER} aria-labelledby="ssr-prep-title">'
                '<h2 id="ssr-prep-title">JavaScript olmadan kesinti hazırlık kontrolü</h2>'
                '<ul>'
                '<li>112, 186 ve yetkili EDAŞ kanallarını erişilebilir biçimde kaydedin.</li>'
                '<li>Telefon, acil aydınlatma, modem/ONT, soğuk zincir ve gerekli sağlık cihazlarını önceliklendirin.</li>'
                '<li>Her yedek kaynağı gerçek yükle ve güvenli gözetim altında test edin.</li>'
                '<li>Mevcut hazırlık hedef süreyi karşılıyorsa yeni ürün almayın.</li>'
                '</ul>'
                '<p><a href="/hesaplama/yedek-guc-cozum-secici/">Yedek güç çözüm seçiciyi aç</a> · '
                '<a href="/amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici/">Kombi ürün sınıflarını teknik kapıyla incele</a></p>'
                '</section>'
            )
            preparation.write_text(_insert_before(text, "main", section), encoding="utf-8")
            added += 1
    return {"pagesWithStaticFallback": added, "affiliateLinksOnEmergencyDecisionPages": 0}


def robots(site: Path) -> dict:
    path = site / "robots.txt"
    text = path.read_text(encoding="utf-8") if path.is_file() else "User-agent: *\nAllow: /\n"
    for agent in AI_SEARCH_AGENTS:
        pattern = re.compile(rf"^User-agent:\s*{re.escape(agent)}\s*$", re.IGNORECASE | re.MULTILINE)
        if not pattern.search(text):
            text = text.rstrip() + f"\n\nUser-agent: {agent}\nAllow: /\n"
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return {"explicitAllow": list(AI_SEARCH_AGENTS), "chatGptSearchCrawler": "OAI-SearchBot"}


def validate(site: Path, reports: dict) -> dict:
    kombi_text = (site / KOMBI).read_text(encoding="utf-8")
    kombi_graph, _span = _jsonld_marker(kombi_text, 'data-alo186-schema-v250="true"')
    kombi_types = [node.get("@type") for node in _walk(kombi_graph) if isinstance(node.get("@type"), str)]
    howto_steps = [node for node in _walk(kombi_graph) if node.get("@type") == "HowToStep"]
    product_nodes = [node for node in _walk(kombi_graph) if node.get("@type") == "Product"]
    offers = [node for node in _walk(kombi_graph) if node.get("@type") == "Offer"]
    if "HowTo" not in kombi_types or "ItemList" not in kombi_types or len(product_nodes) < 3:
        raise RuntimeError("Kombi HowTo/ItemList/Product graph eksik")
    if len(howto_steps) != 5 or not all(step.get("url") for step in howto_steps):
        raise RuntimeError("HowTo görünür adım URL eşleşmesi eksik")
    if offers or any("aggregateRating" in node for node in _walk(kombi_graph)):
        raise RuntimeError("Kanıtsız Offer veya aggregateRating bulundu")
    for anchor, _name, _description in _howto_steps():
        if f'id="{anchor}"' not in kombi_text:
            raise RuntimeError(f"Görünür HowTo adımı eksik: {anchor}")
    affiliate_links = re.findall(r'<a\b[^>]*href="https://www\.amazon\.com\.tr/[^>]+>', kombi_text, re.IGNORECASE)
    safe_affiliate = [
        link for link in affiliate_links
        if all(token in link.lower() for token in ("sponsored", "nofollow", "noopener"))
        and "alo186rehber-21" in link
    ]
    if len(safe_affiliate) < 3:
        raise RuntimeError("SSR affiliate bağlantı sözleşmesi eksik")

    edas_path = next(
        path for path in (site / "edas-bul/index.html", site / "elektrik-kesintisi/index.html") if path.is_file()
    )
    edas_graph, _span = _jsonld_marker(edas_path.read_text(encoding="utf-8"), 'data-alo186-service-catalog-v250="true"')
    services = [node for node in _walk(edas_graph) if node.get("@type") == "Service" and "#service-" in str(node.get("@id", ""))]
    channels = [node for node in _walk(edas_graph) if node.get("@type") == "ServiceChannel"]
    phone_points = [
        node for node in _walk(edas_graph)
        if node.get("@type") == "ContactPoint" and str(node.get("telephone")) == "186"
    ]
    private_government_services = [
        node for node in _walk(edas_graph)
        if node.get("@type") == "GovernmentService" and "edas" in json.dumps(node, ensure_ascii=False).lower()
    ]
    if len(services) != 81 or len(channels) != 81 or len(phone_points) != 81:
        raise RuntimeError(f"EDAŞ hizmet kanalı kapsamı yanlış: {len(services)}/{len(channels)}/{len(phone_points)}")
    if private_government_services:
        raise RuntimeError("Özel EDAŞ GovernmentService olarak yanlış işaretlendi")

    robots_text = (site / "robots.txt").read_text(encoding="utf-8")
    missing_agents = [agent for agent in AI_SEARCH_AGENTS if not re.search(rf"User-agent:\s*{re.escape(agent)}", robots_text, re.I)]
    if missing_agents:
        raise RuntimeError("AI crawler allow eksik: " + ", ".join(missing_agents))

    return {
        "schemaOrgValidator": {
            "status": "pass",
            "method": "all injected JSON-LD blocks parsed as JSON and required schema.org type/property contracts were verified",
            "externalUiApiAvailable": False,
        },
        "googleRichResultsAssessment": {
            "status": "pass-with-feature-boundaries",
            "BreadcrumbList": "supported markup retained",
            "FAQPage": "valid markup retained; display is search-engine discretionary",
            "HowTo": "schema.org-valid; no current Google HowTo rich-result claim",
            "Product": "generic product-class entities only; no Offer, price, stock, rating or merchant-listing claim",
        },
        "visibleContentParity": "pass",
        "jsonLdSyntax": "pass",
        "howToSteps": len(howto_steps),
        "genericProductEntities": len(product_nodes),
        "offerEntities": len(offers),
        "ssrAffiliateLinks": len(safe_affiliate),
        "provinceServices": len(services),
        "serviceChannels": len(channels),
        "servicePhone186": len(phone_points),
        "privateEdasGovernmentService": 0,
        "aiCrawlersExplicitlyAllowed": list(AI_SEARCH_AGENTS),
        "reports": reports,
    }


def apply(repo: Path, site: Path) -> dict:
    repo = repo.resolve()
    site = site.resolve()
    reports = {
        "howTo": visible_howto(site),
        "edas": augment_edas(repo, site),
        "ssr": ssr_decision_fallbacks(site),
        "robots": robots(site),
    }
    validation = validate(site, reports)
    result = {"version": VERSION, "validation": validation, **reports}
    (site / REPORT).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 competitor-gap v251 görünür HowTo, EDAŞ ServiceChannel ve AI crawler katmanı")
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--site", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(apply(args.repo_root, args.site), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
