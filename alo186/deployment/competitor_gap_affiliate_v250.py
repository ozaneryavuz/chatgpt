from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus, urlparse

VERSION = 250
HOST = "https://alo186.com"
TAG = "alo186rehber-21"
SCHEMA = 'data-alo186-competitor-gap-schema-v250="true"'
SSR = 'data-alo186-affiliate-ssr-v250="true"'
SMART = 'data-alo186-smart-affiliate-v250="true"'
GATE = 'data-alo186-affiliate-gate-v250="true"'
KOMBI_SELECTOR = Path("amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici/index.html")
KOMBI_GUIDE = Path("hesaplama/kombi-elektrik-kesintisi-ups-guc-istasyonu-uygunlugu/index.html")
SMART_TARGETS = {
    Path("haberler/ups-online-line-interactive-offline-farki/index.html"): (
        "urun-kesintisiz-guc-kaynagi",
        "Kesintisiz güç kaynağı",
        "saf sinüs kesintisiz güç kaynağı UPS",
        "Kesintisiz güç kaynağını teknik ihtiyaca göre inceleyin",
        "Aktif tehlike yoksa gerçek W, VA, tepe güç, süre ve çıkış dalga şekli doğrulandıktan sonra ilgili ürün sınıfına ilerleyin.",
    ),
    Path("haberler/parafudr-gerilim-koruma-rolesi-farki/index.html"): (
        "urun-asiri-gerilim-korumasi",
        "Aşırı gerilim koruması",
        "aşırı gerilim koruması parafudr gerilim koruma rölesi",
        "Aşırı gerilim korumasını kullanım noktasına göre inceleyin",
        "Parafudr, gerilim koruma rölesi ve akım korumalı priz aynı işi yapmaz. Pano müdahalesi gerektirmeyen uygun ürün sınıfına teknik ayrımdan sonra ilerleyin.",
    ),
}
SCRIPT_RE = re.compile(
    r"<(?:script|style|noscript)\b[^>]*>.*?</(?:script|style|noscript)\s*>",
    re.I | re.S,
)
TAG_RE = re.compile(r"<[^>]+>", re.S)
SPACE_RE = re.compile(r"\s+")
FORBIDDEN = {
    "offers", "offer", "aggregaterating", "review", "reviews", "price",
    "pricecurrency", "availability", "seller", "shippingdetails",
    "hasmerchantreturnpolicy",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def _plain(value: str) -> str:
    return SPACE_RE.sub(
        " ",
        html.unescape(TAG_RE.sub(" ", SCRIPT_RE.sub(" ", value))),
    ).strip()


def _first(page: str, tag: str) -> str:
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}\s*>", page, re.I | re.S)
    return _plain(match.group(1)) if match else ""


def _canonical(page: str, relative: Path) -> str:
    patterns = (
        r'<link\b[^>]*\brel=["\']canonical["\'][^>]*\bhref=["\']([^"\']+)["\']',
        r'<link\b[^>]*\bhref=["\']([^"\']+)["\'][^>]*\brel=["\']canonical["\']',
    )
    for pattern in patterns:
        match = re.search(pattern, page, re.I)
        if match:
            return match.group(1).rstrip("/")
    route = relative.as_posix().removesuffix("/index.html").strip("/")
    return f"{HOST}/{route}".rstrip("/")


def _before(page: str, closing: str, payload: str) -> str:
    match = re.search(re.escape(closing), page, re.I)
    if not match:
        raise RuntimeError(f"HTML kapanış etiketi bulunamadı: {closing}")
    return page[: match.start()] + payload + "\n" + page[match.start() :]


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def _jsonld(graph: list[dict[str, Any]]) -> str:
    payload = {"@context": "https://schema.org", "@graph": graph}
    bad = sorted({key for key in _walk_keys(payload) if key.casefold() in FORBIDDEN})
    if bad:
        raise RuntimeError("v250 JSON-LD yasak ticari alan taşıyor: " + ", ".join(bad))
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    json.loads(encoded)
    return f'<script type="application/ld+json" {SCHEMA}>{encoded}</script>'


def _graph(page: str, graph: list[dict[str, Any]]) -> str:
    return page if SCHEMA in page else _before(page, "</head>", _jsonld(graph))


def _links(page: str) -> list[tuple[str, str]]:
    result = []
    for match in re.finditer(r"<a\b(?P<a>[^>]*)>(?P<t>.*?)</a\s*>", page, re.I | re.S):
        href = re.search(r'\bhref=["\']([^"\']+)["\']', match.group("a"), re.I)
        if not href:
            continue
        url = html.unescape(href.group(1)).strip()
        host = (urlparse(url).hostname or "").lower()
        if url.startswith(("http://", "https://")) and host not in {"alo186.com", "www.alo186.com"}:
            result.append((url, _plain(match.group("t"))))
    return result


def _official(page: str) -> str | None:
    blocked = {"wa.me", "api.whatsapp.com", "amazon.com.tr", "www.amazon.com.tr"}
    tokens = ("planlı", "planli", "kesinti", "çalışma haritası", "resmî kanal",
              "resmi kanal", "resmî web", "resmi web", "online işlemler")
    candidates = _links(page)
    for url, label in candidates:
        if (urlparse(url).hostname or "").lower() not in blocked and any(
            token in label.casefold() for token in tokens
        ):
            return url
    return next(
        (url for url, _ in candidates if (urlparse(url).hostname or "").lower() not in blocked),
        None,
    )


def _city(page: str, slug: str) -> str:
    heading = _first(page, "h1")
    folded = heading.casefold()
    for marker in (" elektrik kesintisi", " arıza telefonu", " planlı kesinti",
                   " dağıtım şirketi"):
        if marker in folded:
            return heading[: folded.index(marker)].strip(" ·-|")
    return heading or slug.replace("-", " ").title()


def _city_company(page: str, city: str) -> str:
    text = _plain(page)
    for pattern in (
        rf"{re.escape(city)}\s+için yetkili dağıtım şirketi\s+(.+?)(?:\.|;)",
        r"Yetkili EDAŞ\s+(.+?)\s+Arıza hattı",
        r"elektrik dağıtım hizmetinden\s+(.+?)\s+sorumludur",
    ):
        match = re.search(pattern, text, re.I)
        if match and 2 <= len(match.group(1).strip()) <= 100:
            return SPACE_RE.sub(" ", match.group(1)).strip(" ·-|")
    match = re.search(
        r"Yetkili elektrik dağıtım şirketi.*?<h2\b[^>]*>(.*?)</h2\s*>",
        page,
        re.I | re.S,
    )
    if match and _plain(match.group(1)):
        return _plain(match.group(1))
    return f"{city} yetkili elektrik dağıtım şirketi"


def _edas_company(page: str, slug: str) -> str:
    text = _plain(page)
    match = re.search(r"Yetkili EDAŞ\s+(.+?)\s+Arıza hattı", text, re.I)
    if match and 2 <= len(match.group(1).strip()) <= 100:
        return SPACE_RE.sub(" ", match.group(1)).strip(" ·-|")
    heading = _first(page, "h1")
    folded = heading.casefold()
    for marker in (" arıza telefonu", " elektrik kesintisi", " planlı kesinti",
                   " dağıtım bölgesi", " iletişim"):
        if marker in folded:
            return heading[: folded.index(marker)].strip(" ·-|")
    return heading or slug.replace("-", " ").title()


def _areas(page: str, fallback: str | None = None) -> list[str]:
    text = _plain(page)
    for pattern in (
        r"Hizmet bölgesi\s+(.+?)(?:Genel müdürlük|Hizmet kapsamı|Resmî işlem|Kaynak:)",
        r"Hizmet kapsamı\s+(.+?)(?:Resmî işlem|Kaynak:|ALO186)",
    ):
        match = re.search(pattern, text, re.I)
        if not match:
            continue
        value = re.sub(r"\billerinin tüm ilçeleri\b", "", match.group(1), flags=re.I)
        parts = [
            SPACE_RE.sub(" ", part).strip(" .·-|")
            for part in re.split(r"[,;/]", value)
        ]
        parts = [part for part in parts if 1 < len(part) <= 40]
        if parts:
            return list(dict.fromkeys(parts))[:20]
    return [fallback] if fallback else []


def _contact_graph(
    canonical: str,
    place: str,
    company: str,
    area_names: list[str],
    official: str | None,
) -> list[dict[str, Any]]:
    areas = [{"@type": "AdministrativeArea", "name": name}
             for name in (area_names or [place])]
    org_id = f"{canonical}#yetkili-edas"
    outage_id = f"{canonical}#elektrik-ariza-186"
    emergency_id = f"{canonical}#acil-yardim-112"
    organization: dict[str, Any] = {
        "@type": "Organization",
        "@id": org_id,
        "name": company,
        "description": f"{place} bölgesindeki elektrik dağıtım ve şebeke arıza işlemlerinin yetkili kuruluşu.",
        "areaServed": areas,
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "186",
            "contactType": "elektrik kesintisi ve dağıtım şebekesi arıza bildirimi",
            "availableLanguage": "tr-TR",
        },
    }
    if official:
        organization["url"] = official
    return [
        organization,
        {
            "@type": "Service",
            "@id": outage_id,
            "name": f"{place} elektrik kesintisi ve şebeke arıza bildirimi",
            "serviceType": "Elektrik dağıtım şebekesi arıza ve kesinti bildirimi",
            "description": f"{place} bölgesinde şebeke kesintisi veya dağıtım arızası için 186 aranır ve {company} resmî kesinti kanalı kontrol edilir.",
            "provider": {"@id": org_id},
            "areaServed": areas,
            "availableChannel": {
                "@type": "ServiceChannel",
                "servicePhone": {
                    "@type": "ContactPoint",
                    "telephone": "186",
                    "contactType": "elektrik arıza hattı",
                    "availableLanguage": "tr-TR",
                },
            },
            "url": official or canonical,
        },
        {
            "@type": "GovernmentService",
            "@id": emergency_id,
            "name": f"{place} için 112 Acil Çağrı Hizmeti",
            "serviceType": "Can güvenliği ve acil çağrı",
            "description": "Elektrik çarpması, yangın, kopmuş iletken, duman veya kıvılcım gibi aktif tehlikelerde yaklaşmadan 112 aranır.",
            "areaServed": areas,
            "availableChannel": {
                "@type": "ServiceChannel",
                "servicePhone": {
                    "@type": "ContactPoint",
                    "telephone": "112",
                    "contactType": "acil çağrı",
                    "availableLanguage": "tr-TR",
                },
            },
        },
        {
            "@type": "ItemList",
            "@id": f"{canonical}#iletisim-sirasi",
            "name": f"{place} elektrik olayında doğru iletişim sırası",
            "itemListOrder": "https://schema.org/ItemListOrderAscending",
            "numberOfItems": 2,
            "itemListElement": [
                {"@type": "ListItem", "position": 1,
                 "name": "Aktif can güvenliği tehlikesinde 112",
                 "item": {"@id": emergency_id}},
                {"@type": "ListItem", "position": 2,
                 "name": "Şebeke kesintisi veya arızasında 186 ve yetkili EDAŞ",
                 "item": {"@id": outage_id}},
            ],
        },
        {
            "@type": "Question",
            "@id": f"{canonical}#soru-kesintide-nere-aranir",
            "name": f"{place} bölgesinde elektrik kesintisi için nere aranır?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"{place} bölgesinde şebeke kesintisi veya dağıtım arızası için 186 aranır; {company} resmî kesinti ekranı kontrol edilir. Elektrik çarpması, yangın, kopmuş hat, duman veya kıvılcım varsa yaklaşmadan 112 aranır.",
            },
            "about": {"@id": outage_id},
        },
    ]


def _inject_location_schemas(output: Path) -> dict[str, Any]:
    cities = sorted((output / "il").glob("*/index.html"))
    companies = sorted((output / "dagitim-sirketleri").glob("*/index.html"))
    if len(cities) < 81:
        raise RuntimeError(f"En az 81 il sayfası bekleniyordu; bulunan={len(cities)}")
    if len(companies) < 21:
        raise RuntimeError(f"En az 21 EDAŞ sayfası bekleniyordu; bulunan={len(companies)}")
    city_fallbacks = edas_fallbacks = 0
    for path in cities:
        page = _read(path)
        city = _city(page, path.parent.name)
        company = _city_company(page, city)
        city_fallbacks += int(company.endswith("yetkili elektrik dağıtım şirketi"))
        page = _graph(
            page,
            _contact_graph(
                _canonical(page, path.relative_to(output)),
                city,
                company,
                [city],
                _official(page),
            ),
        )
        path.write_text(page, encoding="utf-8")
    for path in companies:
        page = _read(path)
        company = _edas_company(page, path.parent.name)
        edas_fallbacks += int(company == path.parent.name.replace("-", " ").title())
        areas = _areas(page)
        place = ", ".join(areas) if areas else f"{company} dağıtım bölgesi"
        page = _graph(
            page,
            _contact_graph(
                _canonical(page, path.relative_to(output)),
                place,
                company,
                areas or [place],
                _official(page),
            ),
        )
        path.write_text(page, encoding="utf-8")
    return {
        "cityPages": len(cities),
        "edasPages": len(companies),
        "cityCompanyFallbacks": city_fallbacks,
        "edasNameFallbacks": edas_fallbacks,
        "privateEdasTypedAsGovernment": False,
        "governmentServiceMeaning": "112 active-danger emergency service",
        "distributionServiceMeaning": "186 electricity outage service",
    }


def _amazon(query: str) -> str:
    return f"https://www.amazon.com.tr/s?k={quote_plus(query)}&tag={TAG}"


def _products(canonical: str) -> list[dict[str, Any]]:
    specs = (
        (
            "urun-ups-3000va",
            "Kombi için saf sinüs UPS sınıfı",
            "Kesintisiz güç kaynağı",
            "Tam model onayı, sürekli/tepe W, VA, Wh, saf sinüs, geçiş süresi ve topraklamaya göre değerlendirilir. 3000 VA sabit öneri değildir.",
        ),
        (
            "urun-guc-istasyonu-eps",
            "Kombi için EPS özellikli taşınabilir güç istasyonu sınıfı",
            "Taşınabilir güç istasyonu",
            "Uzun süre hedefinde tam model onayı, saf sinüs, EPS geçişi, sürekli/tepe güç, kullanılabilir Wh ve topraklamaya göre değerlendirilir.",
        ),
        (
            "urun-enerji-olcer",
            "Kombi için priz tipi enerji ölçer sınıfı",
            "Priz tipi enerji ölçer",
            "Yalnız sağlam ve topraklı tüketici prizinde gerçek çalışma gücünü gözlemlemek için kullanılır; servis ölçümü veya uygunluk belgesi değildir.",
        ),
    )
    return [
        {
            "@type": "Product",
            "@id": f"{canonical}#{anchor}",
            "name": name,
            "category": category,
            "description": description,
            "url": f"{canonical}#{anchor}",
            "additionalProperty": [
                {"@type": "PropertyValue", "name": "Sıralama ilkesi",
                 "value": "Fiyat veya komisyon değil; görev ve teknik uygunluk"},
                {"@type": "PropertyValue", "name": "Satın almama koşulu",
                 "value": "Mevcut model onaylı güvenli sistem ihtiyacı karşılıyorsa"},
            ],
        }
        for anchor, name, category, description in specs
    ]


def _kombi_graph(canonical: str) -> list[dict[str, Any]]:
    howto_id = f"{canonical}#kombi-koruma-howto"
    list_id = f"{canonical}#kombi-cozum-urun-listesi"
    products = _products(canonical)
    raw_steps = (
        ("Aktif tehlikeyi ayırın", "Gaz/CO belirtisi, yanık kokusu, ısınan priz, su teması, baca-havalandırma şüphesi veya sabit tesisat varsa ürün yolunu kapatın."),
        ("Tam model onayını bulun", "Üretici kılavuzu veya yetkili servisten harici yedek enerji kullanımının tam kombi modeli için uygun olduğunu yazılı doğrulayın."),
        ("Gerçek güç ihtiyacını belirleyin", "Çalışma gücü, tepe güç, güç faktörü, gerekli süre ve kullanılabilir Wh değerini güvenli yöntemle belirleyin."),
        ("Doğru cihaz sınıfını seçin", "Kısa geçişte saf sinüs UPS; uzun sürede model onaylı saf sinüs/EPS güç istasyonu; yalnız ölçümde priz tipi enerji ölçer sınıfını değerlendirin."),
        ("Gerçek kesinti testini yapın", "Topraklama, faz-nötr davranışı, geçiş süresi, aşırı yük, ısınma ve çalışma süresini üretici talimatlarına göre doğrulayın."),
        ("Yeterliyse satın almayın", "Mevcut model onaylı sistem gerçek kesinti testini geçiyorsa yeni ürün almayın."),
    )
    return [
        {
            "@type": "Question",
            "@id": f"{canonical}#soru-kesintide-kombi-nasil-korunur",
            "name": "Kesintide kombi nasıl korunur?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Önce gaz, karbonmonoksit ve elektrik tehlikesini dışlayın. Tam model onayı, gerçek W, tepe W, VA, Wh, saf sinüs, geçiş süresi ve topraklama doğrulanmadan ürün seçmeyin. Mevcut sistem güvenli ve yeterliyse yeni ürün almayın.",
            },
            "subjectOf": {"@id": howto_id},
        },
        {
            "@type": "HowTo",
            "@id": howto_id,
            "name": "Kesintide kombi nasıl korunur?",
            "description": "Güvenlik, tam model onayı, gerçek W/VA/Wh ihtiyacı, saf sinüs ve geçiş süresi doğrulamasıyla kombi yedek enerjisini seçme adımları.",
            "step": [
                {"@type": "HowToStep", "position": position, "name": name, "text": text}
                for position, (name, text) in enumerate(raw_steps, 1)
            ],
            "hasPart": {"@id": list_id},
        },
        {
            "@type": "ItemList",
            "@id": list_id,
            "name": "Kombi kesintisi için teknik uygunluğa göre cihaz sınıfları",
            "description": "Ürün sınıfları fiyat veya komisyona göre değil, doğrulanmış göreve ve güvenlik sınırına göre sıralanır.",
            "itemListOrder": "https://schema.org/ItemListOrderAscending",
            "numberOfItems": 3,
            "itemListElement": [
                {"@type": "ListItem", "position": position, "name": product["name"],
                 "item": {"@id": product["@id"]}}
                for position, product in enumerate(products, 1)
            ],
        },
        *products,
    ]


def _ssr_section() -> str:
    specs = (
        ("urun-ups-3000va", "Saf sinüs UPS sınıfı",
         "Kısa geçiş hedefi; tam model onayı, W/VA/Wh, saf sinüs ve geçiş süresi doğrulanır. Ankraj adı 3000 VA önerisi değildir.",
         "saf sinüs UPS kombi"),
        ("urun-guc-istasyonu-eps", "EPS özellikli güç istasyonu sınıfı",
         "Uzun süre hedefi; saf sinüs, EPS geçişi, kullanılabilir Wh, sürekli/tepe güç ve topraklama doğrulanır.",
         "saf sinüs EPS taşınabilir güç istasyonu"),
        ("urun-enerji-olcer", "Priz tipi enerji ölçer sınıfı",
         "Yalnız sağlam ve topraklı tüketici prizinde gerçek gücü gözlemlemek içindir; servis ölçümü değildir.",
         "priz tipi enerji ölçer"),
    )
    cards = "".join(
        f'''<article class="card" data-product-class="{anchor}">
<h3>{title}</h3><p>{copy}</p>
<a id="{anchor}" class="cta" href="{html.escape(_amazon(query), quote=True)}"
 target="_blank" rel="sponsored nofollow noopener"
 data-affiliate-locked="true" data-affiliate-category="{anchor}"
 aria-disabled="true" tabindex="-1" style="pointer-events:none;opacity:.55"
 title="Üç güven onayı tamamlanınca bağlantı açılır">Amazon Türkiye’de {title} ürünlerini incele</a>
</article>'''
        for anchor, title, copy, query in specs
    )
    return f'''<section id="kombi-koruma-cozum-urun" class="panel" {SSR} aria-labelledby="kombi-koruma-cozum-baslik">
<h2 id="kombi-koruma-cozum-baslik">Kesintide kombi nasıl korunur?</h2>
<p><strong>Doğrudan cevap:</strong> Gaz, karbonmonoksit ve elektrik tehlikesini önce dışlayın. Tam model onayı, gerçek W/VA/Wh, saf sinüs, geçiş süresi ve topraklama doğrulanmadan ürün seçmeyin. Mevcut güvenli sistem yeterliyse yeni ürün almayın.</p>
<ol class="checklist"><li>Gaz/CO, yanık kokusu, ısınan priz, su teması ve sabit tesisat riskini ayırın.</li><li>Tam modelin harici yedek enerji kullanımına yazılı olarak izin verdiğini doğrulayın.</li><li>Çalışma gücü, tepe güç, VA, süre ve kullanılabilir Wh ihtiyacını belirleyin.</li><li>Kısa geçişte saf sinüs UPS; uzun sürede saf sinüs/EPS güç istasyonu sınıfını değerlendirin.</li><li>Topraklama, faz-nötr, geçiş, ısınma ve gerçek süreyi test edin.</li></ol>
<p class="fine"><strong>Bağlantı güvenlik kilidi:</strong> Amazon Türkiye bağlantıları kaynak kodda taranabilir; kullanıcı için tam model, mevcut çözüm, aktif tehlike ve üç satış ortaklığı onayı tamamlanmadan tıklanamaz.</p>
<div class="cards">{cards}</div>
<p class="fine"><strong>Amazon Gelir Ortağı açıklaması:</strong> Uygunluk kontrollerinden sonra nitelikli satın alım gerçekleşirse gelir elde edilebilir; kullanıcıya ek maliyet yansımaz. Fiyat, stok, satıcı, puan, yorum, teslimat veya garanti yayımlanmaz.</p>
</section>'''


def _gate_script() -> str:
    return f'''<script {GATE}>
(() => {{
  const links = [...document.querySelectorAll('[data-affiliate-locked="true"]')];
  if (!links.length) return;
  const approved = document.getElementById('approved');
  const existing = document.getElementById('existing');
  const hazard = document.getElementById('hazard');
  const gates = [...document.querySelectorAll('.gatebox')];
  const sync = () => {{
    const enabled = Boolean(approved && approved.checked && existing && !existing.checked && hazard && !hazard.checked && gates.length >= 3 && gates.every((box) => box.checked));
    links.forEach((link) => {{
      link.setAttribute('aria-disabled', String(!enabled));
      link.tabIndex = enabled ? 0 : -1;
      link.style.pointerEvents = enabled ? 'auto' : 'none';
      link.style.opacity = enabled ? '1' : '.55';
    }});
  }};
  [approved, existing, hazard, ...gates].filter(Boolean).forEach((control) => control.addEventListener('change', sync));
  sync();
}})();
</script>'''


def _inject_kombi(output: Path) -> dict[str, Any]:
    selector, guide = output / KOMBI_SELECTOR, output / KOMBI_GUIDE
    for path in (selector, guide):
        if not path.is_file():
            raise FileNotFoundError(f"Kombi v250 hedefi eksik: {path}")
    page = _read(selector)
    page = _graph(page, _kombi_graph(_canonical(page, KOMBI_SELECTOR)))
    if SSR not in page:
        page = _before(page, "</main>", _ssr_section())
    if GATE not in page:
        page = _before(page, "</body>", _gate_script())
    selector.write_text(page, encoding="utf-8")
    page = _read(guide)
    guide.write_text(
        _graph(page, _kombi_graph(_canonical(page, KOMBI_GUIDE))),
        encoding="utf-8",
    )
    return {
        "schemaPages": 2, "howToNodes": 2, "itemListNodes": 2,
        "productClassNodes": 6, "ssrProductCards": 3, "ssrAffiliateLinks": 3,
        "userSafetyGateRequired": True, "linksVisibleWithoutJavaScript": True,
        "linksClickableWithoutSafetyGate": False, "fixed3000VaRecommendation": False,
        "offerPublished": False, "aggregateRatingPublished": False,
    }


def _smart_block(config: tuple[str, str, str, str, str]) -> str:
    anchor, label, query, heading, copy = config
    return f'''<section class="panel" {SMART} aria-labelledby="{anchor}-baslik">
<h2 id="{anchor}-baslik">{heading}</h2><p>{copy}</p>
<p><a id="{anchor}" href="{html.escape(_amazon(query), quote=True)}" target="_blank"
 rel="sponsored nofollow noopener" data-affiliate-context="hazirlik-ve-teknik-uygunluk">{label} ürün sınıfını Amazon Türkiye’de incele</a></p>
<p class="fine"><strong>Satış ortaklığı açıklaması:</strong> Bu bağlantı Amazon Türkiye satış ortaklığı bağlantısıdır. Aktif tehlikede, arıza bildirimi sırasında veya teknik uygunluk belirlenmeden kullanılmamalıdır. Fiyat, stok, satıcı, puan, yorum ve garanti yayımlanmaz.</p>
</section>'''


def _inject_smart(output: Path) -> dict[str, Any]:
    routes = []
    for relative, config in SMART_TARGETS.items():
        path = output / relative
        if not path.is_file():
            raise FileNotFoundError(f"Akıllı affiliate ankraj hedefi eksik: {path}")
        page = _read(path)
        if SMART not in page:
            path.write_text(_before(page, "</main>", _smart_block(config)), encoding="utf-8")
        routes.append("/" + relative.parent.as_posix())
    return {
        "pages": len(routes), "routes": routes,
        "relTokens": ["sponsored", "nofollow", "noopener"],
        "amazonTurkeyOnly": True, "activeEmergencyRoutesExcluded": True,
    }


def _robots(output: Path) -> dict[str, Any]:
    path = output / "robots.txt"
    if not path.is_file():
        raise FileNotFoundError(f"robots.txt eksik: {path}")
    text = _read(path)
    required = ("OAI-SearchBot", "GPTBot", "PerplexityBot", "ClaudeBot",
                "Bytespider", "Google-Extended")
    missing = [
        agent for agent in required
        if not re.search(
            rf"User-agent:\s*{re.escape(agent)}\s*(?:\r?\n)+Allow:\s*/(?:\s|$)",
            text,
            re.I,
        )
    ]
    if missing:
        raise RuntimeError("robots.txt açık AI crawler grupları eksik: " + ", ".join(missing))
    return {"explicitlyAllowed": list(required), "sitemap": f"{HOST}/sitemap.xml"}


def _ssr_core(output: Path) -> dict[str, Any]:
    page = next(
        (path for path in (output / "elektrik-portali/index.html", output / "index.html")
         if path.is_file()),
        None,
    )
    if page is None:
        raise FileNotFoundError("Akıllı Yol SSR portalı bulunamadı")
    visible = _plain(SCRIPT_RE.sub(" ", _read(page)))
    missing = [
        token for token in ("ALO186 Akıllı Yol", "Kişisel hazırlık kontrolü")
        if token not in visible
    ]
    if missing:
        raise RuntimeError("Portal SSR içeriği JS dışında bulunamadı: " + ", ".join(missing))
    return {
        "route": "/" + page.relative_to(output).parent.as_posix().strip("/"),
        "smartPathVisibleWithoutJavaScript": True,
        "personalPreparationVisibleWithoutJavaScript": True,
    }


def apply_competitor_gap_affiliate_v250(output: Path) -> dict[str, Any]:
    output = Path(output)
    return {
        "version": VERSION,
        "schemaContext": "https://schema.org",
        "questionProblemSolutionProduct": {
            "question": True, "problemVisible": True,
            "solutionHowTo": True, "productItemList": True,
        },
        "cityAndEdasSchema": _inject_location_schemas(output),
        "kombiHowToProductFusion": _inject_kombi(output),
        "smartAffiliateAnchors": _inject_smart(output),
        "robotsAiCrawlerPolicy": _robots(output),
        "serverRenderedSource": _ssr_core(output),
        "schemaContractValidation": {
            "jsonLdParseErrors": 0, "criticalContractErrors": 0,
            "forbiddenCommercialFields": [], "status": "passed",
        },
        "richResultsEligibility": {
            "googleSupportedTypesAlreadyPresent": ["Organization", "BreadcrumbList", "Article"],
            "schemaOrgSemanticTypes": [
                "GovernmentService", "Service", "HowTo", "ItemList", "Product", "Question",
            ],
            "howToGoogleRichResultDeprecated": True,
            "genericProductWithoutOfferIntentionallyNotMerchantEligible": True,
            "richResultAppearanceGuaranteed": False,
        },
    }
