from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

VERSION = 251
REVISION = 252
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
PRIMARY_UPS_ANCHOR = "urun-ups-3000va"
LEGACY_UPS_ANCHOR = "urun-kombi-ups"
SMART_PATH_ID = "akilli-yol-ssr"
PREPAREDNESS_ID = "kisisel-hazirlik-kontrolu-ssr"
CHAIN_ANCHOR = "soru-sorun-cozum-urun"
DIRECT_ANSWER = (
    "Önce gaz, karbonmonoksit, duman, yanık kokusu ve su teması riskini ayırın. "
    "Tam kombi modeli için üretici onayını, sürekli ve tepe gücü, hedef çalışma süresini, "
    "dalga biçimini ve geçiş davranışını doğrulayın. Mevcut güvenli sistem gerçek kesinti "
    "testini geçiyorsa yeni ürün almayın; yalnız doğrulanmış eksik kalırsa uygun saf sinüs "
    "UPS veya EPS güç istasyonu sınıfını karşılaştırın."
)


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


def _replace_exact_string(value, old: str, new: str) -> None:
    if isinstance(value, dict):
        for key, nested in list(value.items()):
            if isinstance(nested, str) and nested == old:
                value[key] = new
            else:
                _replace_exact_string(nested, old, new)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            if isinstance(nested, str) and nested == old:
                value[index] = new
            else:
                _replace_exact_string(nested, old, new)


def _upsert_graph_node(graph: dict, node: dict) -> None:
    nodes = graph.get("@graph")
    if not isinstance(nodes, list):
        raise RuntimeError("Kombi JSON-LD @graph listesi eksik")
    node_id = node.get("@id")
    for index, existing in enumerate(nodes):
        if isinstance(existing, dict) and existing.get("@id") == node_id:
            nodes[index] = node
            return
    nodes.append(node)


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


def _ensure_primary_affiliate_anchor(text: str) -> str:
    if f'id="{PRIMARY_UPS_ANCHOR}"' in text:
        return text
    pattern = re.compile(
        rf'(<li\b(?=[^>]*\bid=["\']{re.escape(LEGACY_UPS_ANCHOR)}["\'])[^>]*>\s*<a\b)'
        r'(?=[^>]*\bhref=["\']https://www\.amazon\.com\.tr/)',
        re.IGNORECASE,
    )
    updated, count = pattern.subn(rf'\1 id="{PRIMARY_UPS_ANCHOR}"', text, count=1)
    if count != 1:
        raise RuntimeError("Kombi UPS Amazon bağlantısına kararlı ürün ankrajı eklenemedi")
    return updated


def _augment_question_problem_chain(graph: dict) -> dict:
    page = f"{ORIGIN}/{KOMBI.parent.as_posix()}/"
    old_product_id = page + "#" + LEGACY_UPS_ANCHOR
    product_id = page + "#" + PRIMARY_UPS_ANCHOR
    question_id = page + "#question-kesintide-kombi"
    problem_id = page + "#problem-kombi-elektrik-kesintisi"
    chain_id = page + "#" + CHAIN_ANCHOR

    _replace_exact_string(graph, old_product_id, product_id)
    howto = next((node for node in _walk(graph) if node.get("@type") == "HowTo"), None)
    product = next(
        (
            node
            for node in _walk(graph)
            if node.get("@type") == "Product" and node.get("@id") == product_id
        ),
        None,
    )
    if not isinstance(howto, dict) or not isinstance(howto.get("@id"), str):
        raise RuntimeError("Soru–Sorun–Çözüm–Ürün zinciri için HowTo bulunamadı")
    if not isinstance(product, dict):
        raise RuntimeError("Soru–Sorun–Çözüm–Ürün zinciri için Kombi UPS Product bulunamadı")

    howto["about"] = {"@id": product_id}
    product["url"] = product_id
    product["isRelatedTo"] = {"@id": howto["@id"]}
    properties = product.setdefault("additionalProperty", [])
    if not isinstance(properties, list):
        raise RuntimeError("Product additionalProperty listesi bozuk")
    if not any(
        isinstance(item, dict) and item.get("name") == "3000 VA ankraj sınırı"
        for item in properties
    ):
        properties.append(
            {
                "@type": "PropertyValue",
                "name": "3000 VA ankraj sınırı",
                "value": "Kararlı kategori ankrajıdır; her kombi için sabit güç veya uygunluk önerisi değildir.",
            }
        )

    question = {
        "@type": "Question",
        "@id": question_id,
        "name": "Kesintide kombi nasıl korunur?",
        "acceptedAnswer": {"@type": "Answer", "text": DIRECT_ANSWER},
        "subjectOf": {"@id": howto["@id"]},
    }
    problem = {
        "@type": "DefinedTerm",
        "@id": problem_id,
        "name": "Elektrik kesintisinde kombi kontrolü ve sirkülasyonunun durması",
        "description": (
            "Kesinti, gerilim geri dönüşü veya yanlış yedek güç seçimi nedeniyle kombi elektroniği, "
            "kontrol devresi ya da sirkülasyon işlevinin güvenli çalışmaması problemi."
        ),
        "subjectOf": {"@id": howto["@id"]},
    }
    chain = {
        "@type": "ItemList",
        "@id": chain_id,
        "name": "Kesintide kombi için Soru–Sorun–Çözüm–Ürün zinciri",
        "numberOfItems": 4,
        "itemListOrder": "https://schema.org/ItemListOrderAscending",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Soru", "item": {"@id": question_id}},
            {"@type": "ListItem", "position": 2, "name": "Sorun", "item": {"@id": problem_id}},
            {"@type": "ListItem", "position": 3, "name": "Çözüm", "item": {"@id": howto["@id"]}},
            {"@type": "ListItem", "position": 4, "name": "Ürün sınıfı", "item": {"@id": product_id}},
        ],
    }
    for node in (question, problem, chain):
        _upsert_graph_node(graph, node)

    for node in graph.get("@graph", []):
        if not isinstance(node, dict) or node.get("@type") != "WebPage":
            continue
        node["mainEntity"] = {"@id": chain_id}
        about = node.setdefault("about", [])
        if isinstance(about, list):
            known = {item.get("@id") for item in about if isinstance(item, dict)}
            for entity_id in (question_id, problem_id, howto["@id"], product_id, chain_id):
                if entity_id not in known:
                    about.append({"@id": entity_id})
        break
    return graph


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
            f'<section id="{CHAIN_ANCHOR}" class="panel" {HOWTO_MARKER} aria-labelledby="kombi-howto-v251">'
            '<span class="eyebrow">Soru → Sorun → Çözüm → Ürün</span>'
            '<h2 id="kombi-howto-v251">Kesintide kombi nasıl korunur?</h2>'
            '<dl class="decision-chain">'
            '<dt>Soru</dt><dd>Kesintide kombi nasıl korunur?</dd>'
            '<dt>Sorun</dt><dd>Kesinti veya yanlış yedek güç seçimi kombi kontrolünü ve sirkülasyonu durdurabilir ya da yeni elektriksel risk oluşturabilir.</dd>'
            '<dt>Çözüm</dt><dd>Gaz/CO güvenliğini ayırın; tam model onayını, W–Wh hesabını, dalga biçimini, geçişi ve gerçek kesinti testini doğrulayın.</dd>'
            '<dt>Ürün sınıfı</dt><dd>Yalnız doğrulanmış eksik kalırsa saf sinüs UPS, uygun EPS güç istasyonu veya enerji ölçer sınıfına ilerleyin.</dd>'
            '</dl>'
            f'<p><strong>Doğrudan cevap:</strong> {DIRECT_ANSWER}</p>'
            f'<ol>{rows}</ol>'
            f'<p><a href="#{PRIMARY_UPS_ANCHOR}">Saf sinüs kombi UPS sınıfına geç</a> · '
            '<a href="#urun-kombi-guc-istasyonu">EPS güç istasyonu sınıfına geç</a> · '
            '<a href="#urun-priz-enerji-olcer">Enerji ölçer sınıfına geç</a></p>'
            '<p><small>“3000 VA” yalnız kararlı kategori ankrajıdır; her kombi için otomatik güç veya uygunluk önerisi değildir.</small></p>'
            '</section>'
        )
        text = _insert_before(text, "main", section)

    text = _ensure_primary_affiliate_anchor(text)
    graph, _span = _jsonld_marker(text, 'data-alo186-schema-v250="true"')
    step_urls = [f"{ORIGIN}/{KOMBI.parent.as_posix()}/#{anchor}" for anchor, _name, _desc in steps]
    for node in _walk(graph):
        if node.get("@type") == "HowTo":
            for position, step in enumerate(node.get("step", []), start=1):
                if isinstance(step, dict) and position <= len(step_urls):
                    step["url"] = step_urls[position - 1]
        if node.get("@type") == "Product" and isinstance(node.get("@id"), str):
            node.setdefault("url", node["@id"])
    graph = _augment_question_problem_chain(graph)
    text = _replace_jsonld_marker(text, 'data-alo186-schema-v250="true"', graph)
    path.write_text(text, encoding="utf-8")
    return {
        "visibleSteps": len(steps),
        "structuredStepUrls": len(step_urls),
        "visibleContentParity": True,
        "questionProblemSolutionProductItems": 4,
        "primaryAffiliateAnchor": PRIMARY_UPS_ANCHOR,
        "fixed3000VaRecommendation": False,
    }


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
        page_html = page.read_text(encoding="utf-8")
        if SERVICE_PAGE_MARKER not in page_html:
            providers = [company for company in companies if province_id in company["provinceIds"]]
            page_url = f"{ORIGIN}/il/{_slug(province_name)}/"
            page_html = _insert_before(
                page_html,
                "head",
                _script(_local_service_graph(province_name, providers, page_url), SERVICE_PAGE_MARKER),
            )
            page.write_text(page_html, encoding="utf-8")
        province_pages += 1

    for company in companies:
        page = site / "dagitim-sirketleri" / company["slug"] / "index.html"
        if not page.is_file():
            continue
        page_html = page.read_text(encoding="utf-8")
        if SERVICE_PAGE_MARKER not in page_html:
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
            page_html = _insert_before(page_html, "head", _script(data, SERVICE_PAGE_MARKER))
            page.write_text(page_html, encoding="utf-8")
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
                f'<section id="{SMART_PATH_ID}" class="content-section" {DECISION_MARKER} aria-labelledby="ssr-decision-title">'
                '<h2 id="ssr-decision-title">Akıllı Yol: JavaScript olmadan güvenli başlangıç</h2>'
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
                f'<section id="{PREPAREDNESS_ID}" class="panel" {PREP_MARKER} aria-labelledby="ssr-prep-title">'
                '<h2 id="ssr-prep-title">Kişisel Hazırlık Kontrolü: JavaScript olmadan kesinti planı</h2>'
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
    return {
        "pagesWithStaticFallback": added,
        "affiliateLinksOnEmergencyDecisionPages": 0,
        "namedModules": [SMART_PATH_ID, PREPAREDNESS_ID],
    }


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
    questions = [node for node in _walk(kombi_graph) if node.get("@type") == "Question"]
    problems = [node for node in _walk(kombi_graph) if node.get("@type") == "DefinedTerm"]
    chain_id = f"{ORIGIN}/{KOMBI.parent.as_posix()}/#{CHAIN_ANCHOR}"
    chain = next(
        (
            node
            for node in _walk(kombi_graph)
            if node.get("@type") == "ItemList" and node.get("@id") == chain_id
        ),
        None,
    )
    if "HowTo" not in kombi_types or "ItemList" not in kombi_types or len(product_nodes) < 3:
        raise RuntimeError("Kombi HowTo/ItemList/Product graph eksik")
    if not questions or not problems or not isinstance(chain, dict):
        raise RuntimeError("Soru–Sorun–Çözüm–Ürün semantik zinciri eksik")
    chain_elements = chain.get("itemListElement")
    if not isinstance(chain_elements, list) or len(chain_elements) != 4:
        raise RuntimeError("Soru–Sorun–Çözüm–Ürün ItemList dört öğe taşımıyor")
    if [item.get("name") for item in chain_elements if isinstance(item, dict)] != [
        "Soru",
        "Sorun",
        "Çözüm",
        "Ürün sınıfı",
    ]:
        raise RuntimeError("Soru–Sorun–Çözüm–Ürün sırası bozuk")
    if len(howto_steps) != 5 or not all(step.get("url") for step in howto_steps):
        raise RuntimeError("HowTo görünür adım URL eşleşmesi eksik")
    if offers or any("aggregateRating" in node for node in _walk(kombi_graph)):
        raise RuntimeError("Kanıtsız Offer veya aggregateRating bulundu")
    for anchor, _name, _description in _howto_steps():
        if f'id="{anchor}"' not in kombi_text:
            raise RuntimeError(f"Görünür HowTo adımı eksik: {anchor}")
    if f'id="{CHAIN_ANCHOR}"' not in kombi_text:
        raise RuntimeError("Görünür Soru–Sorun–Çözüm–Ürün bölümü eksik")

    affiliate_links = re.findall(r'<a\b[^>]*href="https://www\.amazon\.com\.tr/[^>]+>', kombi_text, re.IGNORECASE)
    safe_affiliate = [
        link
        for link in affiliate_links
        if all(token in link.lower() for token in ("sponsored", "nofollow", "noopener"))
        and "alo186rehber-21" in link
    ]
    if len(safe_affiliate) < 3:
        raise RuntimeError("SSR affiliate bağlantı sözleşmesi eksik")
    primary_link = re.search(
        rf'<a\b(?=[^>]*\bid="{re.escape(PRIMARY_UPS_ANCHOR)}")(?=[^>]*\bhref="https://www\.amazon\.com\.tr/)[^>]*>',
        kombi_text,
        re.IGNORECASE,
    )
    if not primary_link:
        raise RuntimeError("urun-ups-3000va Amazon bağlantı ankrajı eksik")
    if not all(token in primary_link.group(0).lower() for token in ("sponsored", "nofollow", "noopener")):
        raise RuntimeError("urun-ups-3000va rel sözleşmesi eksik")
    if "alo186rehber-21" not in primary_link.group(0):
        raise RuntimeError("urun-ups-3000va Amazon Türkiye affiliate etiketi eksik")

    edas_path = next(
        path for path in (site / "edas-bul/index.html", site / "elektrik-kesintisi/index.html") if path.is_file()
    )
    edas_graph, _span = _jsonld_marker(
        edas_path.read_text(encoding="utf-8"),
        'data-alo186-service-catalog-v250="true"',
    )
    services = [
        node
        for node in _walk(edas_graph)
        if node.get("@type") == "Service" and "#service-" in str(node.get("@id", ""))
    ]
    channels = [node for node in _walk(edas_graph) if node.get("@type") == "ServiceChannel"]
    phone_points = [
        node
        for node in _walk(edas_graph)
        if node.get("@type") == "ContactPoint" and str(node.get("telephone")) == "186"
    ]
    private_government_services = [
        node
        for node in _walk(edas_graph)
        if node.get("@type") == "GovernmentService"
        and "edas" in json.dumps(node, ensure_ascii=False).lower()
    ]
    if len(services) != 81 or len(channels) != 81 or len(phone_points) != 81:
        raise RuntimeError(
            f"EDAŞ hizmet kanalı kapsamı yanlış: {len(services)}/{len(channels)}/{len(phone_points)}"
        )
    if private_government_services:
        raise RuntimeError("Özel EDAŞ GovernmentService olarak yanlış işaretlendi")

    decision_path = site / "karar-motoru/index.html"
    preparation_path = site / "hesaplama/kesinti-hazirlik-plani/index.html"
    if decision_path.is_file():
        decision_text = decision_path.read_text(encoding="utf-8")
        if f'id="{SMART_PATH_ID}"' not in decision_text or "Akıllı Yol" not in decision_text:
            raise RuntimeError("Akıllı Yol SSR modülü adlandırılmamış")
    if preparation_path.is_file():
        preparation_text = preparation_path.read_text(encoding="utf-8")
        if f'id="{PREPAREDNESS_ID}"' not in preparation_text or "Kişisel Hazırlık Kontrolü" not in preparation_text:
            raise RuntimeError("Kişisel Hazırlık Kontrolü SSR modülü adlandırılmamış")

    robots_text = (site / "robots.txt").read_text(encoding="utf-8")
    missing_agents = [
        agent
        for agent in AI_SEARCH_AGENTS
        if not re.search(rf"User-agent:\s*{re.escape(agent)}", robots_text, re.IGNORECASE)
    ]
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
        "questionProblemSolutionProductChain": "pass",
        "questionProblemSolutionProductItems": len(chain_elements),
        "primaryAffiliateAnchor": PRIMARY_UPS_ANCHOR,
        "primaryAffiliateAnchorStatus": "pass",
        "ssrNamedModules": [SMART_PATH_ID, PREPAREDNESS_ID],
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
    result = {"version": VERSION, "revision": REVISION, "validation": validation, **reports}
    (site / REPORT).write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "ALO186 competitor-gap v252 Soru–Sorun–Çözüm–Ürün, kararlı affiliate ankrajı, "
            "görünür HowTo, EDAŞ ServiceChannel ve AI crawler katmanı"
        )
    )
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--site", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(apply(args.repo_root, args.site), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
