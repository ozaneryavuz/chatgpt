from __future__ import annotations

import html
import json
import re
import unicodedata
from pathlib import Path

VERSION = 220
CANONICAL_ORIGIN = "https://alo186.com"
AFFILIATE_TAG = "alo186rehber-21"
REQUESTED_AI_BOTS = (
    "GPTBot",
    "PerplexityBot",
    "ClaudeBot",
    "Bytespider",
    "Google-Extended",
)

EDAS_SCHEMA_ID = "alo186-edas-service-graph-v220"
EDAS_SSR_ID = "edas-ssr-rehberi"
MATCHER_SCHEMA_ID = "alo186-question-solution-product-v220"
SMART_PATH_ID = "akilli-yol-ssr"
PREPAREDNESS_ID = "kisisel-hazirlik-kontrolu-ssr"

PROVINCE_ORDER = (
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Ankara", "Antalya",
    "Artvin", "Aydın", "Balıkesir", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur",
    "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Edirne",
    "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane",
    "Hakkari", "Hatay", "Isparta", "Mersin", "İstanbul", "İzmir", "Kars", "Kastamonu",
    "Kayseri", "Kırklareli", "Kırşehir", "Kocaeli", "Konya", "Kütahya", "Malatya",
    "Manisa", "Kahramanmaraş", "Mardin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu",
    "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat",
    "Trabzon", "Tunceli", "Şanlıurfa", "Uşak", "Van", "Yozgat", "Zonguldak", "Aksaray",
    "Bayburt", "Karaman", "Kırıkkale", "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır",
    "Yalova", "Karabük", "Kilis", "Osmaniye", "Düzce",
)

COMPANIES = (
    ("toroslar", "Toroslar EDAŞ", "toroslar-edas", ("Adana", "Gaziantep", "Hatay", "Kilis", "Mersin", "Osmaniye")),
    ("akedas", "AKEDAŞ", "akedas", ("Adıyaman", "Kahramanmaraş")),
    ("oedas", "Osmangazi EDAŞ", "oedas", ("Afyonkarahisar", "Bilecik", "Eskişehir", "Kütahya", "Uşak")),
    ("aras", "ARAS EDAŞ", "aras-edas", ("Ağrı", "Erzincan", "Erzurum", "Kars", "Bayburt", "Ardahan", "Iğdır")),
    ("medas", "MEDAŞ", "medas", ("Aksaray", "Karaman", "Kırşehir", "Konya", "Nevşehir", "Niğde")),
    ("yedas", "YEDAŞ", "yedas", ("Amasya", "Çorum", "Ordu", "Samsun", "Sinop")),
    ("baskent", "Başkent EDAŞ", "baskent-edas", ("Ankara", "Çankırı", "Kastamonu", "Kırıkkale", "Bartın", "Karabük", "Zonguldak")),
    ("aedas", "Akdeniz EDAŞ", "akdeniz-edas", ("Antalya", "Burdur", "Isparta")),
    ("coruh", "Çoruh EDAŞ", "coruh-edas", ("Artvin", "Giresun", "Gümüşhane", "Rize", "Trabzon")),
    ("adm", "ADM Elektrik", "adm-elektrik", ("Aydın", "Denizli", "Muğla")),
    ("uedas", "UEDAŞ", "uedas", ("Balıkesir", "Bursa", "Çanakkale", "Yalova")),
    ("dicle", "Dicle Elektrik", "dicle-elektrik", ("Batman", "Diyarbakır", "Mardin", "Siirt", "Şanlıurfa", "Şırnak")),
    ("fedas", "Fırat EDAŞ", "firat-edas", ("Bingöl", "Elazığ", "Malatya", "Tunceli")),
    ("vedas", "VEDAŞ", "vedas", ("Bitlis", "Hakkari", "Muş", "Van")),
    ("sedas", "SEDAŞ", "sedas", ("Bolu", "Kocaeli", "Sakarya", "Düzce")),
    ("tredas", "TREDAŞ", "tredas", ("Edirne", "Kırklareli", "Tekirdağ")),
    ("gdz", "GDZ Elektrik", "gdz-elektrik", ("İzmir", "Manisa")),
    ("kcetas", "KCETAŞ", "kcetas", ("Kayseri",)),
    ("cedas", "Çamlıbel EDAŞ", "cedas", ("Sivas", "Tokat", "Yozgat")),
    ("bedas", "BEDAŞ", "bedas", ("İstanbul",)),
    ("ayedas", "AYEDAŞ", "ayedas", ("İstanbul",)),
)


def _slugify(value: str) -> str:
    translated = value.translate(
        str.maketrans(
            {
                "ç": "c", "Ç": "C", "ğ": "g", "Ğ": "G", "ı": "i", "İ": "I",
                "ö": "o", "Ö": "O", "ş": "s", "Ş": "S", "ü": "u", "Ü": "U",
            }
        )
    )
    normalized = unicodedata.normalize("NFKD", translated)
    ascii_text = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.casefold()).strip("-")


def _validate_catalog() -> dict[str, tuple[str, ...]]:
    providers: dict[str, list[str]] = {province: [] for province in PROVINCE_ORDER}
    company_ids: set[str] = set()
    for company_id, _name, _slug, provinces in COMPANIES:
        if company_id in company_ids:
            raise RuntimeError(f"Yinelenen EDAŞ kimliği: {company_id}")
        company_ids.add(company_id)
        for province in provinces:
            if province not in providers:
                raise RuntimeError(f"Bilinmeyen il EDAŞ kataloğunda: {province}")
            providers[province].append(company_id)
    missing = [province for province, values in providers.items() if not values]
    unexpected_multiple = [province for province, values in providers.items() if len(values) > 1 and province != "İstanbul"]
    if missing or unexpected_multiple or len(PROVINCE_ORDER) != 81 or len(COMPANIES) != 21:
        raise RuntimeError(
            "EDAŞ kataloğu sözleşmesi bozuldu: "
            f"il={len(PROVINCE_ORDER)}, şirket={len(COMPANIES)}, eksik={missing}, çoklu={unexpected_multiple}"
        )
    if set(providers["İstanbul"]) != {"bedas", "ayedas"}:
        raise RuntimeError("İstanbul BEDAŞ/AYEDAŞ çift sağlayıcı sözleşmesi bozuldu.")
    return {province: tuple(values) for province, values in providers.items()}


PROVINCE_PROVIDERS = _validate_catalog()
COMPANY_BY_ID = {
    company_id: {"name": name, "slug": slug, "provinces": provinces}
    for company_id, name, slug, provinces in COMPANIES
}


def _organization_id(company_id: str) -> str:
    return f"{CANONICAL_ORIGIN}/edas-bul#organization-{company_id}"


def _organization_nodes() -> list[dict[str, object]]:
    nodes: list[dict[str, object]] = []
    for company_id, name, slug, provinces in COMPANIES:
        nodes.append(
            {
                "@type": "Organization",
                "@id": _organization_id(company_id),
                "name": name,
                "url": f"{CANONICAL_ORIGIN}/dagitim-sirketleri/{slug}",
                "areaServed": [
                    {"@type": "AdministrativeArea", "name": province}
                    for province in provinces
                ],
                "description": (
                    f"{name}, belirtilen dağıtım bölgesinde elektrik dağıtım hizmetini işleten kuruluştur. "
                    "ALO186 bu kuruluşun resmî sitesi değildir."
                ),
            }
        )
    return nodes


def _service_node(province: str) -> dict[str, object]:
    province_slug = _slugify(province)
    provider_refs = [
        {"@id": _organization_id(company_id)}
        for company_id in PROVINCE_PROVIDERS[province]
    ]
    provider: object = provider_refs[0] if len(provider_refs) == 1 else provider_refs
    company_names = " ve ".join(COMPANY_BY_ID[company_id]["name"] for company_id in PROVINCE_PROVIDERS[province])
    return {
        "@type": ["GovernmentService", "Service"],
        "@id": f"{CANONICAL_ORIGIN}/il/{province_slug}#elektrik-kesintisi-ariza-hizmeti",
        "name": f"{province} elektrik kesintisi ve arıza yönlendirme hizmeti",
        "serviceType": "Elektrik dağıtım kesintisi ve şebeke arızası yönlendirmesi",
        "description": (
            f"{province} için 186 ve yetkili dağıtım şirketi ({company_names}) yönlendirmesi. "
            "ALO186 bağımsız bilgi platformudur; arıza kaydı almaz ve kamu kurumu değildir."
        ),
        "areaServed": {"@type": "AdministrativeArea", "name": province},
        "provider": provider,
        "serviceOperator": provider,
        "availableChannel": {
            "@type": "ServiceChannel",
            "serviceUrl": f"{CANONICAL_ORIGIN}/il/{province_slug}",
            "servicePhone": {
                "@type": "ContactPoint",
                "telephone": "186",
                "contactType": "electricity outage and distribution fault reporting",
                "availableLanguage": ["tr"],
            },
        },
        "url": f"{CANONICAL_ORIGIN}/il/{province_slug}",
        "isAccessibleForFree": True,
    }


def edas_service_graph() -> dict[str, object]:
    service_nodes = [_service_node(province) for province in PROVINCE_ORDER]
    item_list_id = f"{CANONICAL_ORIGIN}/edas-bul#province-service-list"
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "@id": f"{CANONICAL_ORIGIN}/edas-bul#service-directory",
                "name": "Türkiye il bazlı elektrik kesintisi ve EDAŞ yönlendirme dizini",
                "url": f"{CANONICAL_ORIGIN}/edas-bul",
                "inLanguage": "tr-TR",
                "description": (
                    "81 il için 186 elektrik arıza yönünü ve ilgili dağıtım şirketi kuruluşunu "
                    "kaynak HTML içinde sunan bağımsız rehber."
                ),
                "mainEntity": {"@id": item_list_id},
            },
            {
                "@type": "ItemList",
                "@id": item_list_id,
                "name": "81 il elektrik kesintisi ve dağıtım hizmeti listesi",
                "numberOfItems": 81,
                "itemListOrder": "https://schema.org/ItemListOrderAscending",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": position,
                        "name": province,
                        "item": {"@id": service_nodes[position - 1]["@id"]},
                    }
                    for position, province in enumerate(PROVINCE_ORDER, start=1)
                ],
            },
            *_organization_nodes(),
            *service_nodes,
        ],
    }


def _province_link(province: str) -> str:
    url = f"/il/{_slugify(province)}"
    return f'<a href="{html.escape(url)}">{html.escape(province)}</a>'


def edas_ssr_html() -> str:
    company_cards: list[str] = []
    for company_id, name, slug, provinces in COMPANIES:
        province_links = ", ".join(_province_link(province) for province in provinces)
        istanbul_note = (
            " <small>İstanbul’da ilçe ve yakaya göre BEDAŞ veya AYEDAŞ seçilir.</small>"
            if company_id in {"bedas", "ayedas"}
            else ""
        )
        company_cards.append(
            "".join(
                [
                    f'<article class="panel" data-edas-organization="{html.escape(company_id)}">',
                    f'<h3><a href="/dagitim-sirketleri/{html.escape(slug)}">{html.escape(name)}</a></h3>',
                    f'<p>{province_links}</p>',
                    istanbul_note,
                    "</article>",
                ]
            )
        )
    return "".join(
        [
            f'<section id="{EDAS_SSR_ID}" class="content-section" data-alo186-ssr="true" ',
            'aria-labelledby="edasSsrTitle">',
            '<div class="panel">',
            '<span class="eyebrow">Kaynak HTML’de taranabilir resmî yönlendirme dizini</span>',
            '<h2 id="edasSsrTitle">Şu ilde elektrik kesintisi için nere aranır?</h2>',
            '<p><strong>Dağıtım şebekesi kesintisi ve dış hat arızası için 186</strong>; elektrik çarpması, yangın, duman, kıvılcım veya yere düşmüş iletkende güvenli alana geçip 112 aranır. Yetkili şirket il ve bazı bölgelerde ilçeye göre değişir.</p>',
            '<div class="actions"><a class="btn btn-primary" href="tel:186">186’yı ara</a>',
            '<a class="btn btn-secondary" href="#arama">İl veya ilçe ara</a></div>',
            '<p><small>ALO186 bağımsız bilgilendirme platformudur; EDAŞ veya kamu kurumu değildir ve arıza kaydı almaz.</small></p>',
            '</div>',
            '<div class="search-results" aria-label="21 dağıtım şirketi ve 81 ilin statik listesi">',
            *company_cards,
            '</div>',
            '</section>',
        ]
    )


def matcher_semantic_graph() -> dict[str, object]:
    page = f"{CANONICAL_ORIGIN}/akilli-urun-secimi"
    question_id = f"{page}#question-kesintide-kombi"
    problem_id = f"{page}#problem-kombi-elektrik-kesintisi"
    howto_id = f"{page}#howto-kesintide-kombi"
    product_id = f"{page}#product-kombi-ups-class"
    list_id = f"{page}#question-problem-solution-product"
    steps = (
        ("Tehlike belirtisini ayırın", "Duman, kıvılcım veya yanık kokusu varsa cihazlara dokunmadan güvenli alana geçin ve 112’yi arayın."),
        ("Kombi teknik verilerini doğrulayın", "Kombi etiketini ve üretici kılavuzunu kullanarak sürekli güç, varsa tepe güç, izin verilen dalga biçimi ve UPS kullanım şartını bulun."),
        ("Güç ve süre hesabını yapın", "Kombi ile birlikte beslenecek pompa veya kontrol yüklerini toplayın; hedef çalışma süresine göre gerekli VA ve Wh sınıfını hesaplayın."),
        ("Uyumluluk sınırını kontrol edin", "Dalga biçimi, geçiş davranışı, çıkış gerilimi ve üretici şartları doğrulanmadan ürünü kombiye bağlamayın."),
        ("Yalnız gerekli ürün sınıfını karşılaştırın", "Hesap sonucu gerçek bir açık gösteriyorsa saf sinüs UPS sınıfını karşılaştırın; 3000 VA her kombi için evrensel seçim değildir."),
    )
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": f"{page}#semantic-decision-page",
                "url": page,
                "name": "ALO186 soru–sorun–çözüm–ürün karar yapısı",
                "inLanguage": "tr-TR",
                "mainEntity": [
                    {"@id": question_id},
                    {"@id": problem_id},
                    {"@id": howto_id},
                    {"@id": product_id},
                    {"@id": list_id},
                ],
            },
            {
                "@type": "Question",
                "@id": question_id,
                "name": "Kesintide kombi nasıl korunur?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": (
                        "Önce tehlike belirtilerini ayırın; ardından kombinin sürekli ve tepe gücünü, "
                        "üreticinin izin verdiği dalga biçimini ve hedef çalışma süresini doğrulayın. "
                        "Hesap sonucu gerektiriyorsa uygun saf sinüs UPS sınıfını karşılaştırın; 3000 VA "
                        "her kombi için otomatik veya evrensel seçim değildir."
                    ),
                },
                "subjectOf": {"@id": howto_id},
            },
            {
                "@type": "DefinedTerm",
                "@id": problem_id,
                "name": "Elektrik kesintisinde kombi kontrolü ve sirkülasyonunun durması",
                "description": (
                    "Kesinti, gerilim dönüşü veya yanlış güç kaynağı seçimi nedeniyle kombi elektroniği, "
                    "kontrol devresi ya da sirkülasyon işlevinin güvenli çalışmaması problemi."
                ),
                "subjectOf": {"@id": howto_id},
            },
            {
                "@type": "HowTo",
                "@id": howto_id,
                "name": "Kesintide kombi nasıl korunur?",
                "description": (
                    "Tehlike ayrımı, teknik veri doğrulama, güç/süre hesabı ve uyumluluk kontrolünden sonra "
                    "gerekli UPS sınıfına ilerleyen ALO186 adımları."
                ),
                "totalTime": "PT10M",
                "about": {"@id": product_id},
                "step": [
                    {
                        "@type": "HowToStep",
                        "position": position,
                        "name": name,
                        "text": text,
                        "url": f"{page}#kombi-adim-{position}",
                    }
                    for position, (name, text) in enumerate(steps, start=1)
                ],
            },
            {
                "@type": "Product",
                "@id": product_id,
                "name": "Kombi için saf sinüs UPS cihaz sınıfı",
                "category": "Kombi UPS",
                "description": (
                    "Belirli marka, model, fiyat veya stok teklifi değildir. Kombinin üretici kılavuzu, "
                    "sürekli/tepe güç ihtiyacı ve hedef çalışma süresine göre doğrulanacak teknik ürün sınıfıdır."
                ),
                "url": f"{page}#urun-ups-3000va",
                "isRelatedTo": {"@id": howto_id},
                "additionalProperty": [
                    {
                        "@type": "PropertyValue",
                        "name": "Dalga biçimi",
                        "value": "Kombi üreticisinin izin verdiği saf sinüs sınıfı",
                    },
                    {
                        "@type": "PropertyValue",
                        "name": "Boyutlandırma",
                        "value": "Sürekli güç, tepe güç ve hedef çalışma süresine göre",
                    },
                    {
                        "@type": "PropertyValue",
                        "name": "Satın alma kapısı",
                        "value": "Teknik hesap ve üretici uyumu olumluysa",
                    },
                ],
            },
            {
                "@type": "ItemList",
                "@id": list_id,
                "name": "Kesintide kombi için Soru–Sorun–Çözüm–Ürün zinciri",
                "numberOfItems": 4,
                "itemListOrder": "https://schema.org/ItemListOrderAscending",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Soru", "item": {"@id": question_id}},
                    {"@type": "ListItem", "position": 2, "name": "Sorun", "item": {"@id": problem_id}},
                    {"@type": "ListItem", "position": 3, "name": "Çözüm", "item": {"@id": howto_id}},
                    {"@type": "ListItem", "position": 4, "name": "Ürün sınıfı", "item": {"@id": product_id}},
                ],
            },
        ],
    }


def _amazon_search(query: str) -> str:
    encoded = query.replace(" ", "+")
    return f"https://www.amazon.com.tr/s?k={encoded}&tag={AFFILIATE_TAG}"


def matcher_ssr_html() -> str:
    steps = (
        ("Soru", "Kesintide hangi cihazın çalışmaya devam etmesi gerekiyor?"),
        ("Sorun", "Kesinti süresi, sürekli/tepe güç ve cihaz uyumu bilinmiyor mu?"),
        ("Çözüm", "Önce ücretsiz hesap ve üretici kılavuzu ile teknik minimumu doğrulayın."),
        ("Ürün", "Yalnız hesap sonucu gerçek bir açık bırakıyorsa ilgili ürün sınıfını karşılaştırın."),
    )
    step_html = "".join(
        f'<li id="kombi-adim-{position}"><strong>{html.escape(label)}:</strong> {html.escape(text)}</li>'
        for position, (label, text) in enumerate(steps, start=1)
    )
    ups_url = _amazon_search("kombi ups saf sinus 3000va")
    ups_category_url = _amazon_search("kesintisiz guc kaynagi saf sinus kombi ups")
    surge_url = _amazon_search("fisli asiri gerilim korumali grup priz joule")
    affiliate_rel = "sponsored nofollow noopener noreferrer"
    return "".join(
        [
            f'<section id="{SMART_PATH_ID}" class="content-section" data-alo186-ssr="true" ',
            'aria-labelledby="smartPathTitle"><div class="panel">',
            '<span class="eyebrow">Botlar ve JavaScript kapalı kullanıcılar için kaynak HTML kararı</span>',
            '<h2 id="smartPathTitle">Akıllı Yol: Soru → Sorun → Çözüm → Ürün</h2>',
            '<p>Bu karar özeti JavaScript çalışmadan da kaynak kodda görünür. Tehlike varsa ticari bağlantı kullanılmaz; güvenli alana geçilir ve 112 aranır.</p>',
            f'<ol class="side-checklist">{step_html}</ol>',
            '<div class="actions"><a class="btn btn-primary" href="/hesaplama/ups-suresi/">UPS çalışma süresini hesapla</a>',
            '<a class="btn btn-secondary" href="/hesaplama/gerilim-koruma-cozum-secici/">Koruma çözümünü ayır</a></div>',
            '</div></section>',
            f'<section id="{PREPAREDNESS_ID}" class="content-section" data-alo186-ssr="true" ',
            'aria-labelledby="preparednessTitle"><div class="panel">',
            '<span class="eyebrow">Kişisel veri istemeyen statik ön kontrol</span>',
            '<h2 id="preparednessTitle">Kişisel Hazırlık Kontrolü</h2>',
            '<ul class="side-checklist">',
            '<li>Kombinin model etiketi ve üretici kılavuzu elinizde mi?</li>',
            '<li>Sürekli güç, varsa tepe güç ve hedef çalışma süresi biliniyor mu?</li>',
            '<li>Üretici, kullanılacak güç kaynağının dalga biçimine ve geçiş davranışına izin veriyor mu?</li>',
            '<li>Mevcut cihazınız bu teknik minimumları zaten karşılıyor mu?</li>',
            '<li>Sonuç belirsizse satın alma yerine yetkili servis veya elektrik uzmanı kontrolüne geçildi mi?</li>',
            '</ul>',
            '<div class="journey-columns">',
            '<article class="journey-box" data-product-class="kombi-ups">',
            '<h3>Kesintide kombi için UPS sınıfı</h3>',
            '<p>Hesap ve üretici uyumu gerçek bir ihtiyaç gösteriyorsa saf sinüs kombi UPS kategorisini karşılaştırın. 3000 VA yalnız arama sınıfıdır; her kombi için otomatik seçim değildir.</p>',
            '<div class="actions">',
            f'<a id="urun-ups-3000va" class="btn btn-primary" href="{html.escape(ups_url)}" target="_blank" rel="{affiliate_rel}">Kombi UPS 3000 VA sınıfını karşılaştır</a>',
            f'<a id="urun-kesintisiz-guc-kaynagi" class="btn btn-secondary" href="{html.escape(ups_category_url)}" target="_blank" rel="{affiliate_rel}">Kesintisiz güç kaynağı kategorisini aç</a>',
            '</div><small>Fiyat, stok, satıcı, teslimat, garanti ve son teknik özellik Amazon Türkiye sayfasında yeniden doğrulanır.</small>',
            '</article>',
            '<article class="journey-box" data-product-class="plug-in-surge-protection">',
            '<h3>Fişli cihazlar için aşırı gerilim koruması</h3>',
            '<p>Yalnız tak-çalıştır tüketici tipi grup priz kategorisini açar. Mevcut ürün yeterliyse yenisini almayın; toplam yük ve ürün etiketini yeniden kontrol edin.</p>',
            '<div class="actions">',
            f'<a id="urun-asiri-gerilim-korumasi" class="btn btn-secondary" href="{html.escape(surge_url)}" target="_blank" rel="{affiliate_rel}">Aşırı gerilim korumalı grup priz kategorisini aç</a>',
            '</div><small>Bu bağlantı sabit tesisat projesi veya profesyonel ölçüm yerine geçmez.</small>',
            '</article>',
            '</div>',
            '<p class="disclosure"><strong>Satış ortaklığı:</strong> Amazon bağlantıları satış ortaklığı bağlantısıdır. Nitelikli satın alımlardan komisyon kazanılabilir; kullanıcıya ek maliyet yansımaz. Mevcut ürün yeterliyse satın almamak geçerli sonuçtur.</p>',
            '</div></section>',
        ]
    )


def _json_script(script_id: str, payload: dict[str, object]) -> str:
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    return f'<script id="{script_id}" type="application/ld+json">{serialized}</script>'


def _inject_before(source: str, closing_tag_pattern: str, fragment: str, label: str) -> str:
    matches = list(re.finditer(closing_tag_pattern, source, re.IGNORECASE))
    if not matches:
        raise RuntimeError(f"{label}: kapanış etiketi bulunamadı")
    match = matches[0]
    return source[: match.start()] + fragment + "\n" + source[match.start() :]


def _replace_noscript(source: str, replacement: str, label: str) -> str:
    pattern = re.compile(r"<noscript>.*?</noscript>", re.IGNORECASE | re.DOTALL)
    updated, count = pattern.subn(replacement, source, count=1)
    if count != 1:
        raise RuntimeError(f"{label}: noscript bloğu tekil değil veya bulunamadı")
    return updated


def _inject_edas(path: Path) -> str:
    source = path.read_text(encoding="utf-8", errors="strict")
    marker_state = (f'id="{EDAS_SCHEMA_ID}"' in source, f'id="{EDAS_SSR_ID}"' in source)
    if all(marker_state):
        return "already-present"
    if any(marker_state):
        raise RuntimeError("EDAŞ v220 kısmi enjeksiyon bulundu; yayın fail-closed durduruldu.")
    source = _inject_before(source, r"</head\s*>", _json_script(EDAS_SCHEMA_ID, edas_service_graph()), "EDAŞ")
    source = _inject_before(source, r"</main\s*>", edas_ssr_html(), "EDAŞ")
    source = _replace_noscript(
        source,
        '<noscript><div class="noscript">81 il ve 21 dağıtım şirketinin statik listesi kaynak HTML içinde yukarıda sunulur. Etkileşimli ilçe filtresi için JavaScript etkinleştirilebilir.</div></noscript>',
        "EDAŞ",
    )
    path.write_text(source, encoding="utf-8")
    return "injected"


def _inject_matcher(path: Path) -> str:
    source = path.read_text(encoding="utf-8", errors="strict")
    marker_state = (
        f'id="{MATCHER_SCHEMA_ID}"' in source,
        f'id="{SMART_PATH_ID}"' in source,
        f'id="{PREPAREDNESS_ID}"' in source,
    )
    if all(marker_state):
        return "already-present"
    if any(marker_state):
        raise RuntimeError("Ürün eşleştirme v220 kısmi enjeksiyon bulundu; yayın fail-closed durduruldu.")
    source = _inject_before(source, r"</head\s*>", _json_script(MATCHER_SCHEMA_ID, matcher_semantic_graph()), "Ürün eşleştirme")
    insertion_marker = re.search(r"<section\s+id=[\"']savedDecision[\"']", source, re.IGNORECASE)
    if insertion_marker:
        source = source[: insertion_marker.start()] + matcher_ssr_html() + "\n" + source[insertion_marker.start() :]
    else:
        source = _inject_before(source, r"</main\s*>", matcher_ssr_html(), "Ürün eşleştirme")
    source = _replace_noscript(
        source,
        '<noscript><div class="noscript">Akıllı Yol, Kişisel Hazırlık Kontrolü ve kontrollü ürün kategorisi bağlantıları kaynak HTML içinde yukarıda görünür. Kişiselleştirilmiş hesap ve kısa liste için JavaScript etkinleştirilebilir.</div></noscript>',
        "Ürün eşleştirme",
    )
    path.write_text(source, encoding="utf-8")
    return "injected"


def verify_ai_crawlers(robots_path: Path) -> list[str]:
    if not robots_path.is_file():
        raise FileNotFoundError(f"robots.txt bulunamadı: {robots_path}")
    source = robots_path.read_text(encoding="utf-8", errors="strict")
    verified: list[str] = []
    for bot in REQUESTED_AI_BOTS:
        pattern = re.compile(
            rf"^User-agent:\s*{re.escape(bot)}\s*$\n(?P<body>.*?)(?=^User-agent:|\Z)",
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        match = pattern.search(source)
        if not match or not re.search(r"^Allow:\s*/\s*$", match.group("body"), re.IGNORECASE | re.MULTILINE):
            raise RuntimeError(f"robots.txt AI tarayıcı erişimi eksik veya kapalı: {bot}")
        verified.append(bot)
    return verified


def install(repo_root: Path, output: Path) -> dict[str, object]:
    del repo_root  # Public contract symmetry with other build installers.
    output = output.resolve()
    edas_path = output / "edas-bul/index.html"
    matcher_path = output / "akilli-urun-secimi/index.html"
    for required in (edas_path, matcher_path):
        if not required.is_file():
            raise FileNotFoundError(f"ALO186 v220 hedef rotası eksik: {required}")

    edas_state = _inject_edas(edas_path)
    matcher_state = _inject_matcher(matcher_path)
    verified_bots = verify_ai_crawlers(output / "robots.txt")

    return {
        "version": VERSION,
        "routes": ["/edas-bul", "/akilli-urun-secimi"],
        "edasState": edas_state,
        "matcherState": matcher_state,
        "organizationCount": len(COMPANIES),
        "governmentServiceCount": len(PROVINCE_ORDER),
        "howToCount": 1,
        "genericProductClassCount": 1,
        "questionProblemSolutionProductItemListCount": 1,
        "ssrModuleIds": [EDAS_SSR_ID, SMART_PATH_ID, PREPAREDNESS_ID],
        "affiliateAnchorIds": [
            "urun-ups-3000va",
            "urun-kesintisiz-guc-kaynagi",
            "urun-asiri-gerilim-korumasi",
        ],
        "affiliateRelTokens": ["sponsored", "nofollow", "noopener", "noreferrer"],
        "verifiedAiCrawlers": verified_bots,
        "javascriptRequiredForCoreAnswer": False,
        "priceStockRatingAdded": False,
        "specificProductEndorsementAdded": False,
    }


__all__ = [
    "AFFILIATE_TAG",
    "CANONICAL_ORIGIN",
    "COMPANIES",
    "EDAS_SCHEMA_ID",
    "EDAS_SSR_ID",
    "MATCHER_SCHEMA_ID",
    "PREPAREDNESS_ID",
    "PROVINCE_ORDER",
    "REQUESTED_AI_BOTS",
    "SMART_PATH_ID",
    "VERSION",
    "edas_service_graph",
    "install",
    "matcher_semantic_graph",
    "verify_ai_crawlers",
]
