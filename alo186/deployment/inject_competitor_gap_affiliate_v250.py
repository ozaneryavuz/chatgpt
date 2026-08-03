from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import quote_plus

VERSION = 250
REVISION = 251
AI_AGENTS = ("GPTBot", "PerplexityBot", "ClaudeBot", "Bytespider", "Google-Extended")
TAG = "alo186rehber-21"
INDEPENDENT = (
    "ALO186 bağımsız bir bilgilendirme platformudur; EDAŞ veya kamu kurumu değildir, "
    "arıza kaydı almaz."
)
KOMBI = Path("amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici/index.html")
SMART_PATH_ID = "akilli-yol-ssr"
PREPAREDNESS_ID = "kisisel-hazirlik-kontrolu-ssr"
PRIMARY_UPS_ANCHOR = "urun-ups-3000va"
_TURKISH_TRANSLATION = str.maketrans(
    {
        "ç": "c",
        "Ç": "C",
        "ğ": "g",
        "Ğ": "G",
        "ı": "i",
        "İ": "I",
        "ö": "o",
        "Ö": "O",
        "ş": "s",
        "Ş": "S",
        "ü": "u",
        "Ü": "U",
    }
)


def _script(data: dict, marker: str) -> str:
    return (
        f'<script type="application/ld+json" {marker}>'
        + json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        + "</script>"
    )


def _head(text: str, fragment: str) -> str:
    if not re.search(r"</head\s*>", text, re.I):
        raise RuntimeError("head kapanışı yok")
    return re.sub(r"</head\s*>", fragment + "\n</head>", text, count=1, flags=re.I)


def _main(text: str, fragment: str) -> str:
    if not re.search(r"</main\s*>", text, re.I):
        raise RuntimeError("main kapanışı yok")
    return re.sub(r"</main\s*>", fragment + "\n</main>", text, count=1, flags=re.I)


def _amazon(query: str) -> str:
    return f"https://www.amazon.com.tr/s?k={quote_plus(query)}&tag={TAG}"


def _slug(value: str) -> str:
    normalized = value.translate(_TURKISH_TRANSLATION).casefold()
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


def robots(site: Path) -> dict:
    path = site / "robots.txt"
    old = path.read_text(encoding="utf-8") if path.is_file() else ""
    sitemaps: list[str] = []
    for line in old.splitlines():
        if line.strip().lower().startswith("sitemap:") and line.strip() not in sitemaps:
            sitemaps.append(line.strip())
    if not sitemaps:
        sitemaps = ["Sitemap: https://alo186.com/sitemap.xml"]

    rows = ["User-agent: *", "Allow: /"]
    for agent in AI_AGENTS:
        rows += ["", f"User-agent: {agent}", "Allow: /"]
    path.write_text("\n".join(rows) + "\n\n" + "\n".join(sitemaps) + "\n", encoding="utf-8")
    return {"explicitAllow": list(AI_AGENTS), "sitemaps": sitemaps}


def kombi_graph() -> dict:
    page = "https://alo186.com/amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici/"
    question = page + "#question-kesintide-kombi"
    problem = page + "#problem-kombi-kesinti"
    how_to = page + "#howto"
    chain = page + "#soru-sorun-cozum-urun"
    product_list = page + "#urun-siniflari"

    products = [
        (
            PRIMARY_UPS_ANCHOR,
            "Kombi için saf sinüs UPS ürün sınıfı",
            "Kombi UPS",
            "3000 VA yalnız taranabilir kategori ankrajıdır; tam model onayı, sürekli/tepe güç, "
            "geçiş süresi ve hedef çalışma süresi hesaplanmadan uygunluk anlamına gelmez.",
        ),
        (
            "urun-kombi-guc-istasyonu",
            "Saf sinüs ve EPS özellikli güç istasyonu ürün sınıfı",
            "Taşınabilir enerji depolama",
            "Uzun süre ihtiyacında W, Wh, EPS geçişi, topraklama ve üretici onayı doğrulanırsa değerlendirilir.",
        ),
        (
            "urun-priz-enerji-olcer",
            "Priz tipi enerji ölçer ürün sınıfı",
            "Elektrik ölçüm cihazı",
            "Yalnız sağlam topraklı prizde gözlem içindir; arıza teşhisi veya tesisat uygunluğu garantisi vermez.",
        ),
    ]
    entities = [
        {
            "@type": "Product",
            "@id": page + "#" + anchor,
            "name": name,
            "category": category,
            "description": description,
            "isRelatedTo": {"@id": how_to},
        }
        for anchor, name, category, description in products
    ]
    steps = [
        (
            "Acil gaz ve CO riskini ayırın",
            "Gaz kokusu, CO belirtisi, duman, yanık kokusu veya su teması varsa ürüne ilerlemeyin; "
            "güvenli alana çıkıp 112 veya 187 yolunu kullanın.",
        ),
        (
            "Tam model onayını doğrulayın",
            "Kılavuz veya yetkili servis üzerinden harici yedek enerji, saf sinüs ve bağlantı koşullarını doğrulayın.",
        ),
        (
            "Gerçek elektrik yükünü hesaplayın",
            "Isıtma kapasitesi ile elektrik tüketimini ayırın; sürekli W, tepe W ve hedef süre için Wh hesabı yapın.",
        ),
        (
            "Mevcut çözümü test edin",
            "Mevcut sistem model onaylı ve güvenli gerçek kesinti testini geçtiyse yeni ürün almayın.",
        ),
        (
            "Yalnız doğrulanmış eksik için ilerleyin",
            "Gerçek eksik varsa UPS, EPS güç istasyonu veya enerji ölçer sınıfını teknik koşullarla karşılaştırın.",
        ),
    ]
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": "https://alo186.com/#organization",
                "name": "ALO186",
                "url": "https://alo186.com/",
                "description": INDEPENDENT,
            },
            {
                "@type": "WebPage",
                "@id": page + "#webpage",
                "url": page,
                "name": "Kombi Yedek Enerji Ürün Seçici",
                "publisher": {"@id": "https://alo186.com/#organization"},
                "mainEntity": {"@id": chain},
                "about": [
                    {"@id": question},
                    {"@id": problem},
                    {"@id": how_to},
                    {"@id": product_list},
                    *[{"@id": entity["@id"]} for entity in entities],
                ],
            },
            {
                "@type": "Question",
                "@id": question,
                "name": "Kesintide kombi nasıl korunur?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": (
                        "Önce gaz, karbonmonoksit, duman, yanık kokusu ve su teması riskini ayırın. "
                        "Kombi üreticisinin tam model onayını doğrulayın; sürekli/tepe W ve hedef süre için "
                        "Wh hesabı yapın. Mevcut güvenli çözüm testi geçiyorsa yeni ürün almayın; yalnız gerçek "
                        "eksik kalırsa saf sinüs UPS veya uygun EPS güç istasyonu sınıfını karşılaştırın."
                    ),
                },
                "subjectOf": {"@id": how_to},
            },
            {
                "@type": "DefinedTerm",
                "@id": problem,
                "name": "Elektrik kesintisinde kombi kontrolü ve sirkülasyonunun durması",
                "description": (
                    "Kesinti, gerilim dönüşü veya yanlış yedek güç seçimi nedeniyle kombi elektroniği, "
                    "kontrol devresi ya da sirkülasyon işlevinin güvenli çalışmaması problemi."
                ),
                "subjectOf": {"@id": how_to},
            },
            {
                "@type": "HowTo",
                "@id": how_to,
                "name": "Elektrik kesintisinde kombi nasıl güvenli korunur?",
                "description": (
                    "Önce gaz/CO güvenliği ve model onayı, sonra W-Wh hesabı ve mevcut çözüm testi; "
                    "yalnız gerçek eksikte ürün sınıfı."
                ),
                "totalTime": "PT10M",
                "about": {"@id": entities[0]["@id"]},
                "step": [
                    {"@type": "HowToStep", "position": index, "name": name, "text": text}
                    for index, (name, text) in enumerate(steps, 1)
                ],
            },
            {
                "@type": "ItemList",
                "@id": product_list,
                "name": "Kombi kesintisi ürün sınıfları",
                "numberOfItems": 3,
                "itemListElement": [
                    {"@type": "ListItem", "position": index, "item": entity}
                    for index, entity in enumerate(entities, 1)
                ],
            },
            {
                "@type": "ItemList",
                "@id": chain,
                "name": "Kesintide kombi için Soru–Sorun–Çözüm–Ürün zinciri",
                "numberOfItems": 4,
                "itemListOrder": "https://schema.org/ItemListOrderAscending",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Soru", "item": {"@id": question}},
                    {"@type": "ListItem", "position": 2, "name": "Sorun", "item": {"@id": problem}},
                    {"@type": "ListItem", "position": 3, "name": "Çözüm", "item": {"@id": how_to}},
                    {"@type": "ListItem", "position": 4, "name": "Ürün sınıfı", "item": {"@id": entities[0]["@id"]}},
                ],
            },
        ],
    }


def kombi_ssr() -> str:
    rows = [
        (
            PRIMARY_UPS_ANCHOR,
            "Saf sinüs UPS / Kombi UPS kategorisini Amazon Türkiye'de incele",
            "saf sinüs ups kombi 3000va",
        ),
        (
            "urun-kombi-guc-istasyonu",
            "Saf sinüs / EPS güç istasyonu kategorisini incele",
            "saf sinüs güç istasyonu eps",
        ),
        (
            "urun-priz-enerji-olcer",
            "Priz tipi enerji ölçer kategorisini incele",
            "priz tipi enerji ölçer",
        ),
    ]
    items = "".join(
        (
            '<li><a id="{anchor}" href="{url}" rel="sponsored nofollow noopener" '
            'target="_blank">{label}</a></li>'
        ).format(
            anchor=html.escape(anchor, quote=True),
            url=html.escape(_amazon(query), quote=True),
            label=html.escape(label),
        )
        for anchor, label, query in rows
    )
    smart_path = (
        f'<section id="{SMART_PATH_ID}" class="panel" data-alo186-smart-path-v251="true">'
        '<h2>Akıllı Yol: Soru → Sorun → Çözüm → Ürün</h2>'
        '<ol>'
        '<li><strong>Soru:</strong> Kesintide kombi nasıl korunur?</li>'
        '<li><strong>Sorun:</strong> Kontrol elektroniği ve sirkülasyon durabilir; yanlış dalga biçimi, güç veya bağlantı yeni risk oluşturabilir.</li>'
        '<li><strong>Çözüm:</strong> Önce gaz/CO güvenliğini ayırın, tam model onayını doğrulayın, W–Wh hesabı yapın ve mevcut sistemi gerçek kesinti testinden geçirin.</li>'
        '<li><strong>Ürün:</strong> Yalnız ölçülmüş açık kalırsa saf sinüs UPS, uygun EPS güç istasyonu veya enerji ölçer sınıfına ilerleyin.</li>'
        '</ol>'
        '<p>3000 VA ifadesi bir kategori ankrajıdır; her kombi için otomatik uygunluk veya satın alma önerisi değildir.</p>'
        '</section>'
    )
    preparedness = (
        f'<section id="{PREPAREDNESS_ID}" class="panel" data-alo186-ssr-affiliate-v250="true" '
        'data-alo186-preparedness-v251="true">'
        '<h2>Kişisel Hazırlık Kontrolü</h2>'
        '<ul>'
        '<li>Gaz kokusu, CO belirtisi, duman, yanık kokusu, su teması veya ısınan priz yok.</li>'
        '<li>Tam kombi modeli için üretici kılavuzu veya yetkili servis harici yedek enerji kullanımını onaylıyor.</li>'
        '<li>Sürekli W, tepe W, geçiş süresi ve hedef çalışma süresi biliniyor.</li>'
        '<li>Mevcut güvenli sistem gerçek kesinti testini geçmediyse veya ihtiyacı karşılamıyorsa ürün sınıfı değerlendiriliyor.</li>'
        '<li>Belirsizlikte alışveriş yerine yetkili servis veya elektrik uzmanı kontrolüne geçiliyor.</li>'
        '</ul>'
        '<p><strong>Affiliate açıklaması:</strong> Amazon Türkiye bağlantıları satış ortaklığı bağlantılarıdır; '
        'nitelikli satın alım olursa gelir elde edebilirim. Fiyat, stok, puan, teslimat ve garanti bilgisi yayımlanmaz.</p>'
        '<p>Mevcut güvenli sistem tam model için onaylı ve gerçek kesinti testini geçtiyse yeni ürün almayın. '
        'Gaz/CO belirtisi, duman, ısınma, su teması veya sabit tesisat işi varsa alışverişe ilerlemeyin.</p>'
        '<ul>'
        + items
        + '</ul>'
        '<p>Bağlantılar belirli bir ürünün kombiyle uyumlu olduğu anlamına gelmez; model kılavuzu, saf sinüs, '
        'W/Wh, geçiş süresi, nötr-toprak ve RCD davranışı yeniden doğrulanmalıdır.</p>'
        '</section>'
    )
    return smart_path + preparedness


def inject_kombi(site: Path) -> dict:
    path = site / KOMBI
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    if 'data-alo186-schema-v250="true"' not in text:
        text = _head(text, _script(kombi_graph(), 'data-alo186-schema-v250="true"'))
    if 'data-alo186-ssr-affiliate-v250="true"' not in text:
        text = _main(text, kombi_ssr())
    path.write_text(text, encoding="utf-8")
    return {
        "howTo": True,
        "questionProblemSolutionProduct": True,
        "itemList": True,
        "genericProductEntities": 3,
        "offers": False,
        "ratings": False,
        "ssrAffiliateLinks": 3,
        "ssrModules": [SMART_PATH_ID, PREPAREDNESS_ID],
        "primaryAffiliateAnchor": PRIMARY_UPS_ANCHOR,
    }


def _catalog(repo: Path):
    text = (repo / "alo186/turkiye-arama/companies.js").read_text(encoding="utf-8")
    province_block = re.search(r"const provinceNames=\{(.*?)\};", text, re.S)
    company_block = re.search(r"const companies=\[(.*?)\];\s*\n\s*const istanbulEurope", text, re.S)
    if not province_block or not company_block:
        raise RuntimeError("EDAŞ katalog parse hatası")
    provinces = {int(index): name for index, name in re.findall(r"(\d+):'([^']+)'", province_block.group(1))}
    pattern = re.compile(
        r"\{id:'([^']+)',code:'[^']+',name:'([^']+)',slug:'([^']+)',provinceIds:\[([^\]]+)\]"
        r"(?:,districtMode:'[^']+')?,aliases:\[[^\]]*\]\}"
    )
    companies = [
        {
            "id": match.group(1),
            "name": match.group(2),
            "slug": match.group(3),
            "provinceIds": [int(value) for value in match.group(4).split(",")],
        }
        for match in pattern.finditer(company_block.group(1))
    ]
    if len(provinces) != 81 or len(companies) != 21:
        raise RuntimeError(f"Kapsam: {len(provinces)} il, {len(companies)} şirket")
    return provinces, companies


def edas_graph(repo: Path) -> dict:
    provinces, companies = _catalog(repo)
    organizations = [
        {
            "@type": "Organization",
            "@id": f"https://alo186.com/dagitim-sirketleri/{company['slug']}/#organization",
            "name": company["name"],
            "url": f"https://alo186.com/dagitim-sirketleri/{company['slug']}/",
            "areaServed": [
                {"@type": "AdministrativeArea", "name": provinces[province_id]}
                for province_id in company["provinceIds"]
            ],
            "description": "Güncel iletişim ve kesinti bilgisi şirketin resmî kanalından doğrulanmalıdır.",
        }
        for company in companies
    ]
    items = []
    for province_id, name in sorted(provinces.items()):
        references = [
            {"@id": f"https://alo186.com/dagitim-sirketleri/{company['slug']}/#organization"}
            for company in companies
            if province_id in company["provinceIds"]
        ]
        provider = references[0] if len(references) == 1 else references
        province_url = f"https://alo186.com/il/{_slug(name)}"
        service = {
            "@type": "Service",
            "@id": f"https://alo186.com/edas-bul/#service-{province_id}",
            "name": f"{name} elektrik kesintisi ve arıza yönlendirmesi",
            "serviceType": "Elektrik dağıtım şebekesi kesinti ve arıza yönlendirmesi",
            "areaServed": {"@type": "AdministrativeArea", "name": name},
            "provider": provider,
            "serviceOperator": provider,
            "url": province_url,
            "availableChannel": {
                "@type": "ServiceChannel",
                "serviceUrl": province_url,
                "servicePhone": {
                    "@type": "ContactPoint",
                    "telephone": "186",
                    "contactType": "electricity outage and distribution fault reporting",
                    "availableLanguage": ["tr"],
                },
            },
            "description": (
                "ALO186 arıza kaydı almaz; 186 ve yetkili şirketin resmî kanalına bağımsız yönlendirme sağlar."
            ),
        }
        items.append({"@type": "ListItem", "position": len(items) + 1, "item": service})
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": "https://alo186.com/#organization",
                "name": "ALO186",
                "url": "https://alo186.com/",
                "description": INDEPENDENT,
            },
            {
                "@type": "WebPage",
                "@id": "https://alo186.com/edas-bul/#webpage",
                "url": "https://alo186.com/edas-bul/",
                "name": "81 İl İçin Yetkili Elektrik Dağıtım Şirketini Bulma",
                "publisher": {"@id": "https://alo186.com/#organization"},
                "mainEntity": {"@id": "https://alo186.com/edas-bul/#province-services"},
            },
            {
                "@type": "ItemList",
                "@id": "https://alo186.com/edas-bul/#province-services",
                "name": "81 il elektrik kesintisi ve EDAŞ yönlendirme hizmetleri",
                "numberOfItems": 81,
                "itemListElement": items,
            },
            *organizations,
        ],
    }


def inject_edas(repo: Path, site: Path) -> dict:
    path = next(
        (
            candidate
            for candidate in (site / "edas-bul/index.html", site / "elektrik-kesintisi/index.html")
            if candidate.is_file()
        ),
        None,
    )
    if not path:
        raise FileNotFoundError("EDAŞ bulucu artifact yok")
    text = path.read_text(encoding="utf-8")
    if 'data-alo186-service-catalog-v250="true"' not in text:
        path.write_text(
            _head(text, _script(edas_graph(repo), 'data-alo186-service-catalog-v250="true"')),
            encoding="utf-8",
        )
    return {
        "provinceServices": 81,
        "organizations": 21,
        "serviceChannels186": 81,
        "schema": "Service + Organization + ServiceChannel",
        "governmentServiceForPrivateEdas": False,
        "reason": "Özel dağıtım şirketlerini GovernmentService olarak işaretlemek resmî kamu hizmeti izlenimi yaratır.",
    }


def inject_112(site: Path) -> dict:
    path = site / "acil-numaralar/index.html"
    if not path.is_file():
        return {"added": False, "optionalRouteMissing": True}
    text = path.read_text(encoding="utf-8")
    marker = 'data-alo186-government-service-v250="true"'
    if marker not in text:
        data = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "GovernmentService",
                    "@id": "https://alo186.com/acil-numaralar/#112-service",
                    "name": "112 Acil Çağrı Hizmeti",
                    "serviceType": "Ulusal acil çağrı yönlendirmesi",
                    "areaServed": {"@type": "Country", "name": "Türkiye"},
                    "provider": {"@id": "https://alo186.com/acil-numaralar/#112-organization"},
                    "description": "ALO186 bu hizmeti sunmaz; yalnız doğru numaraya bağımsız yönlendirme yapar.",
                },
                {
                    "@type": "GovernmentOrganization",
                    "@id": "https://alo186.com/acil-numaralar/#112-organization",
                    "name": "112 Acil Çağrı Merkezi",
                },
                {
                    "@type": "Organization",
                    "@id": "https://alo186.com/#organization",
                    "name": "ALO186",
                    "url": "https://alo186.com/",
                    "description": INDEPENDENT,
                },
            ],
        }
        path.write_text(_head(text, _script(data, marker)), encoding="utf-8")
    return {"added": True, "governmentService": "112 only", "privateEdasMislabelled": False}


def anchor_section(kind: str) -> str:
    if kind == "ups":
        title = "Teknik sonucu doğruladıktan sonra ürün sınıfını inceleyin"
        intro = "W, VA, Wh, geçiş süresi ve dalga biçimi hesabı mevcut sistemin yetersiz olduğunu gösteriyorsa ilerleyin."
        rows = [
            ("urun-ups-saf-sinus", "Saf sinüs UPS kategorisini incele", "saf sinüs ups"),
            ("urun-guc-istasyonu-eps", "EPS güç istasyonu kategorisini incele", "eps özellikli güç istasyonu saf sinüs"),
        ]
    else:
        title = "Priz tipi korumayı yalnız doğru kullanım sınırında değerlendirin"
        intro = (
            "Korumalı priz; topraklama, RCD, pano tipi SPD veya gerilim rölesinin yerine geçmez. "
            "Mevcut sağlam çözüm yeterliyse yeni ürün almayın."
        )
        rows = [
            ("urun-akim-korumali-priz", "Akım korumalı priz kategorisini incele", "akım korumalı priz")
        ]
    links = "".join(
        (
            '<li><a id="{anchor}" href="{url}" rel="sponsored nofollow noopener" '
            'target="_blank">{label}</a></li>'
        ).format(
            anchor=html.escape(anchor, quote=True),
            url=html.escape(_amazon(query), quote=True),
            label=html.escape(label),
        )
        for anchor, label, query in rows
    )
    return (
        f'<section class="related-products" data-alo186-affiliate-anchors-v250="{kind}">'
        f"<h2>{title}</h2><p>{intro}</p>"
        "<p><strong>Affiliate açıklaması:</strong> Bağlantılar Amazon Türkiye satış ortaklığı bağlantılarıdır. "
        "Fiyat, stok, puan, teslimat ve garanti mağazada doğrulanır.</p>"
        f"<ul>{links}</ul></section>"
    )


def inject_anchors(site: Path) -> dict:
    targets = {
        Path("haberler/ups-mi-tasinabilir-guc-istasyonu-mu/index.html"): "ups",
        Path("haberler/korumali-priz-ne-zaman-yeterli-degildir/index.html"): "surge",
    }
    changed: list[str] = []
    for relative, kind in targets.items():
        path = site / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        marker = f'data-alo186-affiliate-anchors-v250="{kind}"'
        if marker not in text:
            path.write_text(_main(text, anchor_section(kind)), encoding="utf-8")
            changed.append(relative.as_posix())
    return {"changed": changed, "rel": "sponsored nofollow noopener"}


def validate(site: Path) -> dict:
    kombi = (site / KOMBI).read_text(encoding="utf-8").lower()
    if (
        kombi.count('data-alo186-schema-v250="true"') != 1
        or kombi.count('data-alo186-ssr-affiliate-v250="true"') != 1
    ):
        raise RuntimeError("v250 kombi marker tekil değil")
    if kombi.count(f'id="{SMART_PATH_ID}"') != 1 or kombi.count(f'id="{PREPAREDNESS_ID}"') != 1:
        raise RuntimeError("v251 adlandırılmış SSR modülleri eksik veya yinelenmiş")
    for schema_type in ("question", "definedterm", "howto", "itemlist", "product"):
        if f'"@type":"{schema_type}"' not in kombi:
            raise RuntimeError(f"kombi semantik türü eksik: {schema_type}")
    if "soru–sorun–çözüm–ürün" not in kombi:
        raise RuntimeError("Soru–Sorun–Çözüm–Ürün zinciri eksik")
    if any(token in kombi for token in ('"offers"', "aggregaterating", "pricecurrency", "availability", "warranty")):
        raise RuntimeError("doğrulanmamış ticari schema alanı")

    section = re.search(
        r'<section[^>]+data-alo186-ssr-affiliate-v250="true".*?</section>',
        kombi,
        re.S,
    )
    if not section or section.group(0).count('rel="sponsored nofollow noopener"') != 3:
        raise RuntimeError("SSR affiliate rel sözleşmesi")
    for anchor in (PRIMARY_UPS_ANCHOR, "urun-kombi-guc-istasyonu", "urun-priz-enerji-olcer"):
        if f'id="{anchor}"' not in section.group(0):
            raise RuntimeError(f"SSR affiliate ankrajı eksik: {anchor}")

    edas_path = next(
        (
            candidate
            for candidate in (site / "edas-bul/index.html", site / "elektrik-kesintisi/index.html")
            if candidate.is_file()
        ),
        None,
    )
    if not edas_path:
        raise RuntimeError("EDAŞ doğrulama artifactı yok")
    edas = edas_path.read_text(encoding="utf-8").lower()
    if '"numberofitems":81' not in edas or edas.count('"telephone":"186"') != 81:
        raise RuntimeError("81 il / 186 ServiceChannel sözleşmesi eksik")
    if '"@type":"governmentservice"' in edas:
        raise RuntimeError("özel EDAŞ hizmeti GovernmentService olarak yanlış etiketlendi")

    robots_text = (site / "robots.txt").read_text(encoding="utf-8")
    for agent in AI_AGENTS:
        if f"User-agent: {agent}\nAllow: /" not in robots_text:
            raise RuntimeError(agent)
    return {
        "jsonLdSyntax": "pass",
        "schemaOrgTypes": [
            "Question",
            "DefinedTerm",
            "HowTo",
            "ItemList",
            "Product",
            "Service",
            "ServiceChannel",
            "Organization",
            "GovernmentService",
        ],
        "newGoogleRichResultEligibility": [],
        "richResultsNote": (
            "Product zengin sonucu Offer, Review veya AggregateRating ister; doğrulanmamış fiyat, stok ve puan "
            "eklenmedi. HowTo güncel Google rich-result galerisinde desteklenmez."
        ),
        "validatorMethod": "Yerel JSON-LD parse, referans, görünür içerik, SSR ve güvenlik sözleşmesi denetimi",
        "ssrNamedModules": "pass",
        "affiliateRel": "pass",
        "robots": "pass",
    }


def apply(repo: Path, site: Path, base_path: str = "") -> dict:
    del base_path
    report = {
        "version": VERSION,
        "revision": REVISION,
        "robots": robots(site),
        "kombi": inject_kombi(site),
        "anchors": inject_anchors(site),
        "edas": inject_edas(repo, site),
        "governmentService": inject_112(site),
    }
    report["validation"] = validate(site)
    (site / "alo186-competitor-gap-affiliate-v250.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(
        json.dumps(
            apply(args.repo.resolve(), args.site.resolve(), args.base_path),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
