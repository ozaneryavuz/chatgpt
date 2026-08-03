from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from html import escape, unescape
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

VERSION = 250
HOST = "https://alo186.com"
ORGANIZATION_ID = HOST + "/#organization"
MARKER = 'data-alo186-affiliate-aeo-v250="true"'
SCHEMA_MARKER = 'data-alo186-affiliate-aeo-schema-v250="true"'
STYLE_MARKER = 'data-alo186-affiliate-aeo-style-v250="true"'
STYLE_SOURCE = Path(__file__).resolve().with_name("affiliate-aeo-v250.css")
STYLE_TARGET = Path("assets/affiliate-aeo-v250.css")
ALO186_ROOT = Path(__file__).resolve().parents[1]
LLMS_SOURCE = ALO186_ROOT / "llms.txt"
ROBOTS_SOURCE = ALO186_ROOT / "robots.txt"
REQUIRED_AFFILIATE_REL = {"sponsored", "nofollow", "noopener"}
AI_CRAWLERS = (
    "OAI-SearchBot",
    "GPTBot",
    "PerplexityBot",
    "ClaudeBot",
    "Bytespider",
    "Google-Extended",
)
ALLOWED_AVAILABILITY = {
    "https://schema.org/InStock",
    "https://schema.org/OutOfStock",
    "https://schema.org/PreOrder",
    "https://schema.org/BackOrder",
    "https://schema.org/LimitedAvailability",
}
ANCHOR_RE = re.compile(r"<a\b[^>]*>", re.I)
HREF_RE = re.compile(r'''\bhref\s*=\s*(["'])(.*?)\1''', re.I | re.S)
REL_RE = re.compile(r'''\brel\s*=\s*(["'])(.*?)\1''', re.I | re.S)
CANONICAL_RE = re.compile(
    r'''<link\b[^>]*\brel\s*=\s*["'][^"']*\bcanonical\b[^"']*["'][^>]*\bhref\s*=\s*["']([^"']+)["'][^>]*>|<link\b[^>]*\bhref\s*=\s*["']([^"']+)["'][^>]*\brel\s*=\s*["'][^"']*\bcanonical\b[^"']*["'][^>]*>''',
    re.I | re.S,
)
HEAD_CLOSE_RE = re.compile(r"</head\s*>", re.I)
MAIN_CLOSE_RE = re.compile(r"</main\s*>", re.I)
BODY_CLOSE_RE = re.compile(r"</body\s*>", re.I)
ID_RE = re.compile(r'''\bid\s*=\s*(["'])(.*?)\1''', re.I | re.S)


@dataclass(frozen=True)
class RecommendationSpec:
    key: str
    deep_id: str
    name: str
    fit: str
    not_fit: str
    check: str
    link_path: str
    link_label: str
    properties: tuple[tuple[str, str], ...] = ()
    offer: dict[str, object] | None = None


@dataclass(frozen=True)
class TargetSpec:
    key: str
    file: Path
    canonical_path: str
    scenario_id: str
    heading: str
    lead: str
    category: str
    recommendations: tuple[RecommendationSpec, ...]
    comparison_rows: tuple[tuple[str, str, str], ...] = ()
    faq_items: tuple[tuple[str, str, str], ...] = ()


TARGETS = (
    TargetSpec(
        "power_station_guide",
        Path("amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi/index.html"),
        "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi/",
        "rehber-buzdolabi-icin-power-station-secimi",
        "Buzdolabı, modem ve ofis yükleri için power station sınıfını ayırın.",
        "Wh tek başına yeterli değildir; sürekli güç, kalkış gücü, saf sinüs, EPS geçişi ve doğrudan bağlantı birlikte doğrulanır.",
        "Taşınabilir Güç İstasyonu",
        (
            RecommendationSpec(
                "basic", "urun-sinifi-power-station-temel", "Temel power station sınıfı",
                "Modem, ONT, telefon ve düşük güçlü LED yükleri.",
                "Motor, buzdolabı, sabit tesisat ve sıfır milisaniye isteyen yükler.",
                "Kullanılabilir Wh, sürekli W, port gücü ve doğrudan bağlantı.",
                "/hesaplama/power-station-kapasite-eps-uygunluk/", "Kapasite ve EPS testini aç",
                (("Enerji sınıfı", "Yaklaşık 500 Wh'a kadar"), ("Yük türü", "Düşük güçlü elektronik")),
            ),
            RecommendationSpec(
                "balanced", "urun-sinifi-power-station-dengeli", "Dengeli power station sınıfı",
                "Dizüstü bilgisayar, iletişim ekipmanı ve orta süreli kesintiler.",
                "Saf sinüsü veya tepe gücü doğrulanmamış motorlu yükler.",
                "500–1.200 Wh, saf sinüs, sürekli/tepe W ve EPS davranışı.",
                "/hesaplama/power-station-kapasite-eps-uygunluk/", "Dengeli sınıfı hesapla",
                (("Enerji sınıfı", "Yaklaşık 500–1.200 Wh"), ("Dalga biçimi", "Yüke göre saf sinüs")),
            ),
            RecommendationSpec(
                "long", "urun-sinifi-power-station-uzun-sure", "Uzun süre power station sınıfı",
                "Uzun kesinti, birden fazla taşınabilir yük ve yüksek enerji rezervi.",
                "Tıbbi yük, EV şarjı, bina geri beslemesi ve projeli sabit sistemler.",
                "1.200 Wh üzeri enerji, sıcaklık, havalandırma, şarj ve topraklama.",
                "/hesaplama/power-station-kapasite-eps-uygunluk/", "Uzun süre sınıfını doğrula",
                (("Enerji sınıfı", "1.200 Wh üzeri"), ("Kullanım", "Taşınabilir ve gözetimli")),
            ),
        ),
    ),
    TargetSpec(
        "ups_runtime",
        Path("hesaplama/ups-suresi/index.html"),
        "/hesaplama/ups-suresi/",
        "rehber-ups-calisma-suresi-secimi",
        "UPS hesabını botların da okuyabildiği üç teknik kapasite sınıfına çevirin.",
        "VA değeri çalışma süresi değildir. Gerçek watt, güç faktörü, verim, batarya enerjisi, yaş ve hedef süre birlikte değerlendirilir.",
        "UPS",
        (
            RecommendationSpec(
                "basic", "urun-sinifi-ups-temel", "Temel UPS sınıfı",
                "Modem, küçük ağ cihazı veya tek düşük güçlü elektronik yük.",
                "Motor, pompa, sabit tesisat ve tıbbi yük.",
                "Sürekli W/VA, kullanılabilir Wh, çıkış tipi ve gerçek prova.",
                "/hesaplama/ups-suresi/", "UPS süresini hesapla",
                (("Enerji sınıfı", "Yaklaşık 500 Wh'a kadar"), ("Görev", "Kısa süre ve kontrollü kapanma")),
            ),
            RecommendationSpec(
                "balanced", "urun-sinifi-ups-dengeli", "Dengeli UPS sınıfı",
                "Bilgisayar, ekran, modem ve orta süreli elektronik yükler.",
                "Kalkış akımı yüksek cihazlar veya belirsiz güç faktörü.",
                "500–1.500 Wh, çıkış W/VA, dalga biçimi ve iletişim desteği.",
                "/hesaplama/ups-suresi/", "Dengeli UPS sınıfını hesapla",
                (("Enerji sınıfı", "Yaklaşık 500–1.500 Wh"), ("Görev", "Çoklu elektronik yük")),
            ),
            RecommendationSpec(
                "long", "urun-sinifi-ups-uzun-sure", "Uzun süre UPS sınıfı",
                "Uzun kontrollü kapanma ve daha yüksek batarya rezervi.",
                "Asansör, pompa, tıbbi sistem ve projeli üç faz yükler.",
                "Batarya dizisi, şarj gücü, bypass, sıcaklık ve bakım kapsamı.",
                "/kurumsal-elektrik-surekliligi-on-degerlendirme", "Profesyonel kapasite kapsamını aç",
                (("Enerji sınıfı", "1.500 Wh üzeri"), ("Görev", "Profesyonel koordinasyon")),
            ),
        ),
    ),
    TargetSpec(
        "power_station_calculator",
        Path("hesaplama/power-station-kapasite-eps-uygunluk/index.html"),
        "/hesaplama/power-station-kapasite-eps-uygunluk/",
        "rehber-power-station-kapasite-eps-secimi",
        "Dinamik power station sonucunun temel önerileri HTML içinde hazırdır.",
        "JavaScript çalışmasa da enerji sınıfı, uygun olmayan kullanımlar ve satın alma öncesi kontroller okunabilir.",
        "Power Station Kapasite ve EPS",
        (
            RecommendationSpec(
                "basic", "urun-karti-power-station-500wh-alti", "500 Wh'a kadar temel sınıf",
                "Modem, telefon, düşük güçlü aydınlatma.",
                "Kompresör, motor ve uzun kesinti.",
                "Gerçek W, hedef süre, verim ve rezerv.",
                "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi", "Temel sınıf rehberini aç",
            ),
            RecommendationSpec(
                "balanced", "urun-karti-power-station-500-1200wh", "500–1.200 Wh dengeli sınıf",
                "Dizüstü, iletişim ve orta süreli taşınabilir yükler.",
                "Saf sinüs veya surge kanıtı olmayan motorlu cihaz.",
                "Sürekli/tepe W, saf sinüs ve EPS geçiş süresi.",
                "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi", "Dengeli sınıf rehberini aç",
            ),
            RecommendationSpec(
                "long", "urun-karti-power-station-1200wh-uzeri", "1.200 Wh üzeri uzun süre sınıfı",
                "Uzun kesinti ve birden çok taşınabilir cihaz.",
                "Bina geri beslemesi, EV ve yaşam güvenliği yükleri.",
                "Havalandırma, batarya kimyası, şarj ve bağlantı düzeni.",
                "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi", "Uzun süre rehberini aç",
            ),
        ),
    ),
    TargetSpec(
        "backup_selector",
        Path("hesaplama/yedek-guc-cozum-secici/index.html"),
        "/hesaplama/yedek-guc-cozum-secici/",
        "rehber-ups-mi-power-station-mi",
        "UPS mi, taşınabilir güç istasyonu mu? Göreve göre karar verin.",
        "Anlık geçiş, kullanılabilir enerji, sürekli/tepe güç, taşınabilirlik ve sabit tesisat sınırı aynı matriste görünür.",
        "Yedek Güç Karşılaştırması",
        (
            RecommendationSpec(
                "ups", "cozum-urun-ups-anlik-gecis", "UPS teknik sınıfı",
                "Bilgisayar, ağ ekipmanı ve kontrollü kapanma.",
                "Uzun taşınabilir kullanım veya yüksek motor yükü.",
                "Geçiş süresi, W/VA, Wh, dalga biçimi ve akü sağlığı.",
                "/hesaplama/ups-suresi/", "UPS çalışma süresini hesapla",
            ),
            RecommendationSpec(
                "power_station", "cozum-urun-power-station-uzun-sure", "Power station teknik sınıfı",
                "Taşınabilir enerji ve daha uzun süre hedefi.",
                "Sıfır milisaniye, sabit tesisat veya bina geri beslemesi.",
                "Wh, sürekli/tepe W, saf sinüs, EPS ve doğrudan bağlantı.",
                "/hesaplama/power-station-kapasite-eps-uygunluk/", "Power station kapasitesini hesapla",
            ),
            RecommendationSpec(
                "professional", "cozum-urun-profesyonel-yedek-sistem", "Profesyonel yedek enerji sistemi",
                "Sabit tesisat, jeneratör, transfer, üç faz veya kritik işletme yükü.",
                "Kullanıcının kendi başına ürün ve koruma seçmesi.",
                "Tek hat, kısa devre, seçicilik, topraklama, transfer ve kabul testi.",
                "/kurumsal-elektrik-surekliligi-on-degerlendirme", "Profesyonel kapsamı aç",
            ),
        ),
        (
            ("Geçiş görevi", "Elektronik yükte hızlı veya kesintisiz geçiş için tasarlanır.", "EPS süresi modele bağlıdır; sıfır milisaniye varsayılmaz."),
            ("Enerji süresi", "Wh ve haricî batarya seçeneğine göre hesaplanır.", "Etiket Wh, verim ve rezervle kullanılabilir enerjiye çevrilir."),
            ("Taşınabilirlik", "Genellikle sabit veya masaüstü kullanım.", "Taşınabilir kullanım için uygundur; bina tesisatına geri beslenmez."),
            ("Motor ve tepe güç", "Tam UPS topolojisi ve çıkış sınırı doğrulanır.", "Sürekli ve surge W ayrı doğrulanır; üretici onayı gerekir."),
        ),
    ),
    TargetSpec(
        "voltage_selector",
        Path("hesaplama/gerilim-koruma-cozum-secici/index.html"),
        "/hesaplama/gerilim-koruma-cozum-secici/",
        "rehber-gerilim-dalgalanmasinda-cihaz-koruma",
        "Gerilim dalgalanmasında korumalı priz, röle ve SPD aynı görev değildir.",
        "Önce aktif tehlike, tesisat arızası ve topraklama kanıtı ayrılır; ardından düşük riskli tak-çalıştır veya profesyonel çözüm yolu seçilir.",
        "Gerilim Koruma Ekipmanları",
        (
            RecommendationSpec(
                "strip", "urun-sinifi-akim-korumali-priz-yuksek-joule", "Akım korumalı grup priz sınıfı",
                "Topraklı ve sağlam prizde düşük güçlü tüketici elektroniği.",
                "Topraksız/hasarlı priz, ısıtıcı, motor, EV ve sabit tesisat.",
                "Joule değeri, topraklama, toplam yük, gösterge ve kullanım ömrü.",
                "/hesaplama/akim-korumali-grup-priz-uygunluk/", "Korumalı priz uygunluğunu kontrol et",
            ),
            RecommendationSpec(
                "relay", "urun-sinifi-gerilim-koruma-rolesi", "Gerilim koruma rölesi sınıfı",
                "Alt/üst gerilim eşikleriyle tesisat seviyesinde kontrollü ayırma.",
                "Kullanıcının pano içinde kendi başına montaj yapması.",
                "Şebeke düzeni, eşikler, gecikme, kontaktör ve yetkili uygulama.",
                "/haberler/parafudr-gerilim-koruma-rolesi-farki", "Gerilim rölesi görevini öğren",
            ),
            RecommendationSpec(
                "spd", "urun-sinifi-pano-tipi-spd-profesyonel", "Pano tipi SPD sınıfı",
                "Yıldırım ve anahtarlama darbelerine karşı projeli koruma kademesi.",
                "Tak-çalıştır ürün gibi satın alıp kullanıcı montajı yapmak.",
                "SPD tipi, kısa devre dayanımı, ön koruma, topraklama ve koordinasyon.",
                "/haberler/parafudr-gerilim-koruma-rolesi-farki", "SPD görev ayrımını aç",
            ),
        ),
        faq_items=(
            (
                "faq-bazi-prizler-calismiyor",
                "Evde elektrik var ama bazı prizler çalışmıyorsa ne yapılmalı?",
                "Yanık kokusu, kıvılcım, ısı, duman veya elektrik çarpması riski varsa devreye dokunmayın ve acil güvenlik yolunu izleyin. Belirti yoksa sigorta/RCD durumu ile arızanın tek priz mi, tek devre mi olduğunu yetkili elektrikçiyle doğrulayın.",
            ),
            (
                "faq-voltaj-dalgalanmasi-koruma",
                "Voltaj dalgalanmasında cihazlar nasıl korunur?",
                "Korumalı priz, gerilim rölesi ve pano tipi SPD farklı görev yapar. Önce dalgalanmanın kaynağı, topraklama, tesisat ve cihaz yükü doğrulanmalı; aktif arızada ürün satın almak yerine yetkili müdahale seçilmelidir.",
            ),
        ),
    ),
    TargetSpec(
        "surge_selector",
        Path("hesaplama/akim-korumali-grup-priz-uygunluk/index.html"),
        "/hesaplama/akim-korumali-grup-priz-uygunluk/",
        "rehber-akim-korumali-priz-secimi",
        "Akım korumalı priz seçimini joule etiketiyle sınırlamayın.",
        "Topraklama, yük tipi, toplam güç, fiziksel durum, gösterge ve değiştirme koşulu birlikte okunur.",
        "Akım Korumalı Priz",
        (
            RecommendationSpec(
                "basic", "urun-karti-korumali-priz-temel-elektronik", "Temel elektronik koruma sınıfı",
                "Modem, televizyon, masaüstü elektronik ve düşük güç.",
                "Topraksız priz, ısıtıcı, motor, uzatma zinciri ve EV.",
                "Topraklama, toplam W/A, fiziksel durum ve koruma göstergesi.",
                "/amazon-elektrik-urunleri", "Güvenli ürün rehberlerini aç",
            ),
            RecommendationSpec(
                "higher", "urun-karti-korumali-priz-yuksek-joule", "Yüksek joule sınıfı",
                "Birden fazla hassas elektronik ve daha yüksek darbe enerjisi beklentisi.",
                "Pano tipi SPD veya gerilim rölesi yerine kullanmak.",
                "Joule, sıkıştırma gerilimi, tepki, sigorta ve üretici ömür sonu bilgisi.",
                "/haberler/parafudr-gerilim-koruma-rolesi-farki", "Koruma katmanlarını karşılaştır",
            ),
            RecommendationSpec(
                "monitor", "urun-karti-enerji-izlemeli-korumali-priz", "Enerji izlemeli priz sınıfı",
                "Düşük riskli tek cihaz tüketimini görünür kılmak.",
                "Kalibre kabul ölçümü, sabit tesisat veya kritik otomasyon.",
                "Azami akım, ölçüm kapsamı, kablosuz güvenlik ve yük türü.",
                "/hesaplama/akilli-priz-enerji-olcer-uygunluk/", "Enerji ölçer uygunluğunu kontrol et",
            ),
        ),
    ),
    TargetSpec(
        "preparedness",
        Path("hesaplama/kesinti-hazirlik-plani/index.html"),
        "/hesaplama/kesinti-hazirlik-plani/",
        "rehber-ev-ofis-kesinti-hazirlik-ekipmanlari",
        "Ev ve ofis kesinti hazırlığında ürün sayısından önce görevleri ayırın.",
        "İletişim, internet, aydınlatma ve çalışma sürekliliği ayrı teknik minimumlarla planlanır; acil durumda ürün gösterilmez.",
        "Kesinti Hazırlık Ekipmanları",
        (
            RecommendationSpec(
                "internet", "urun-karti-kesinti-mini-ups", "İnternet sürekliliği sınıfı",
                "Modem, ONT ve düşük güçlü ağ cihazları.",
                "Gerilim, jak veya polaritesi doğrulanmamış cihaz.",
                "Adaptör gerilimi, polarite, toplam W ve hedef süre.",
                "/amazon-elektrik-urunleri/modem-mini-ups-secimi", "Mini UPS rehberini aç",
            ),
            RecommendationSpec(
                "energy", "urun-karti-kesinti-power-station", "Taşınabilir enerji sınıfı",
                "Telefon, dizüstü, modem ve uygun düşük riskli yükler.",
                "Bina geri beslemesi, tıbbi yük ve EV.",
                "Wh, sürekli/tepe W, saf sinüs, EPS ve doğrudan bağlantı.",
                "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi", "Power station rehberini aç",
            ),
            RecommendationSpec(
                "lighting", "urun-karti-kesinti-aydinlatma", "Acil olmayan yedek aydınlatma sınıfı",
                "Ev içi yön bulma ve kısa süreli görev aydınlatması.",
                "Mevzuata bağlı bina acil aydınlatma sistemi yerine kullanmak.",
                "Lümen, çalışma süresi, pil durumu, şarj ve kuru ortam.",
                "/hesaplama/acil-aydinlatma-sure-uygunluk/", "Aydınlatma süresini kontrol et",
            ),
        ),
    ),
    TargetSpec(
        "product_center",
        Path("akilli-urun-secimi/index.html"),
        "/akilli-urun-secimi",
        "urun-secim-kartlari-ssr",
        "Ürün seçim kartlarının temel HTML sürümü.",
        "Dinamik filtreler çalışmasa da UPS, power station ve koruma ekipmanı sınıfları ile teknik kontrol bağlantıları taranabilir.",
        "Teknik Ürün Seçim Kartları",
        (
            RecommendationSpec(
                "ups", "urun-secim-karti-ssr-ups", "UPS seçim kartı",
                "Hızlı geçiş ve kontrollü kapanma isteyen elektronik yükler.",
                "Motor, sabit tesisat ve hesaplanmamış runtime.",
                "W/VA, Wh, dalga biçimi, geçiş ve batarya sağlığı.",
                "/hesaplama/ups-suresi/", "UPS hesabını aç",
            ),
            RecommendationSpec(
                "power_station", "urun-secim-karti-ssr-power-station", "Power station seçim kartı",
                "Taşınabilir enerji ve uzun süre hedefi.",
                "Sıfır milisaniye, bina geri beslemesi ve kritik yük.",
                "Wh, sürekli/tepe W, saf sinüs ve EPS.",
                "/hesaplama/power-station-kapasite-eps-uygunluk/", "Power station testini aç",
            ),
            RecommendationSpec(
                "protection", "urun-secim-karti-ssr-koruma", "Cihaz koruma seçim kartı",
                "Topraklı sağlam prizde düşük riskli tüketici elektroniği.",
                "Aktif arıza, topraksız priz ve pano içinde kullanıcı müdahalesi.",
                "Risk belirtisi, topraklama, koruma görevi ve yük tipi.",
                "/hesaplama/gerilim-koruma-cozum-secici/", "Koruma çözümünü seç",
            ),
        ),
    ),
)


def normalize_base_path(value: str) -> str:
    cleaned = (value or "").strip()
    return "" if cleaned in {"", "/"} else "/" + cleaned.strip("/")


def public_url(base: str, path: str) -> str:
    path = "/" + path.lstrip("/")
    return normalize_base_path(base) + path


def canonical_from_html(html: str, fallback_path: str) -> str:
    match = CANONICAL_RE.search(html)
    raw = unescape(next((group for group in match.groups() if group), "")) if match else ""
    if not raw:
        raw = HOST + fallback_path
    parsed = urlsplit(raw)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.casefold() not in {"alo186.com", "www.alo186.com"}:
        raise RuntimeError(f"AEO v250 canonical origin geçersiz: {raw}")
    if parsed.query or parsed.fragment:
        raise RuntimeError(f"AEO v250 canonical query/fragment taşıyor: {raw}")
    return urlunsplit(("https", "alo186.com", parsed.path or "/", "", ""))


def verified_offer(record: dict[str, object] | None, *, today: date | None = None) -> dict[str, object] | None:
    """Emit an Offer only for a complete, fresh and explicit merchant payload.

    Production target records intentionally omit offer data until a compliant
    merchant/PA-API feed supplies price, currency, availability and validity.
    """
    if not record:
        return None
    required = {
        "merchantUrl", "price", "priceCurrency", "availability",
        "priceValidUntil", "verifiedAt",
    }
    if not required.issubset(record):
        return None
    try:
        price = float(record["price"])
        valid_until = date.fromisoformat(str(record["priceValidUntil"]))
        verified_at = date.fromisoformat(str(record["verifiedAt"]))
    except (TypeError, ValueError):
        return None
    parsed = urlsplit(str(record["merchantUrl"]))
    currency = str(record["priceCurrency"]).upper()
    availability = str(record["availability"])
    current = today or datetime.now(timezone.utc).date()
    if (
        price <= 0
        or currency != "TRY"
        or parsed.scheme != "https"
        or parsed.netloc.casefold() not in {"amazon.com.tr", "www.amazon.com.tr"}
        or availability not in ALLOWED_AVAILABILITY
        or verified_at > current
        or current - verified_at > timedelta(days=1)
        or valid_until < current
    ):
        return None
    return {
        "@type": "Offer",
        "url": str(record["merchantUrl"]),
        "price": f"{price:.2f}",
        "priceCurrency": currency,
        "availability": availability,
        "priceValidUntil": valid_until.isoformat(),
        "seller": {"@type": "Organization", "name": "Amazon.com.tr"},
    }


def _schema_for(target: TargetSpec, canonical: str) -> tuple[dict[str, object], int]:
    graph: list[dict[str, object]] = []
    guide_id = canonical.rstrip("/") + "#technical-product-guide"
    list_id = canonical.rstrip("/") + "#solution-product-list"
    recommendation_ids: list[str] = []
    emitted_offers = 0

    for position, recommendation in enumerate(target.recommendations, 1):
        product_id = canonical.rstrip("/") + f"#product-{recommendation.key}"
        recommendation_id = canonical.rstrip("/") + f"#recommendation-{recommendation.key}"
        recommendation_ids.append(recommendation_id)
        product: dict[str, object] = {
            "@type": "Product",
            "@id": product_id,
            "name": recommendation.name,
            "category": target.category,
            "description": recommendation.fit + " " + recommendation.check,
            "url": canonical + "#" + recommendation.deep_id,
            "additionalProperty": [
                {"@type": "PropertyValue", "name": "Kimler için", "value": recommendation.fit},
                {"@type": "PropertyValue", "name": "Uygun değil", "value": recommendation.not_fit},
                {"@type": "PropertyValue", "name": "Önce kontrol et", "value": recommendation.check},
                *(
                    {"@type": "PropertyValue", "name": name, "value": value}
                    for name, value in recommendation.properties
                ),
            ],
        }
        offer = verified_offer(recommendation.offer)
        if offer:
            product["offers"] = offer
            emitted_offers += 1
        graph.append(product)
        graph.append(
            {
                "@type": "Recommendation",
                "@id": recommendation_id,
                "name": recommendation.name + " teknik uygunluk önerisi",
                "url": canonical + "#" + recommendation.deep_id,
                "category": "Bağımsız teknik uygunluk önerisi",
                "reviewBody": recommendation.fit + " Satın almadan önce: " + recommendation.check,
                "itemReviewed": {"@id": product_id},
                "author": {"@type": "Organization", "@id": ORGANIZATION_ID, "name": "ALO186"},
                "positiveNotes": {
                    "@type": "ItemList",
                    "itemListElement": [{"@type": "ListItem", "position": 1, "name": recommendation.fit}],
                },
                "negativeNotes": {
                    "@type": "ItemList",
                    "itemListElement": [{"@type": "ListItem", "position": 1, "name": recommendation.not_fit}],
                },
            }
        )

    graph.insert(
        0,
        {
            "@type": "Guide",
            "@id": guide_id,
            "name": target.heading,
            "description": target.lead,
            "url": canonical + "#" + target.scenario_id,
            "inLanguage": "tr-TR",
            "publisher": {"@type": "Organization", "@id": ORGANIZATION_ID, "name": "ALO186"},
            "hasPart": [{"@id": value} for value in recommendation_ids],
        },
    )
    graph.insert(
        1,
        {
            "@type": "ItemList",
            "@id": list_id,
            "name": target.heading + " — çözüm ürünleri",
            "itemListOrder": "https://schema.org/ItemListOrderAscending",
            "numberOfItems": len(target.recommendations),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": position,
                    "url": canonical + "#" + recommendation.deep_id,
                    "item": {"@id": canonical.rstrip("/") + f"#product-{recommendation.key}"},
                }
                for position, recommendation in enumerate(target.recommendations, 1)
            ],
        },
    )

    if target.comparison_rows:
        graph.append(
            {
                "@type": "ItemList",
                "@id": canonical.rstrip("/") + "#comparison-matrix",
                "name": "UPS ve taşınabilir güç istasyonu karşılaştırma matrisi",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": position,
                        "item": {
                            "@type": "Thing",
                            "name": label,
                            "description": "UPS: " + ups + " Power station: " + station,
                        },
                    }
                    for position, (label, ups, station) in enumerate(target.comparison_rows, 1)
                ],
            }
        )

    if target.faq_items:
        solution_url = canonical + "#" + target.scenario_id
        graph.append(
            {
                "@type": "FAQPage",
                "@id": canonical.rstrip("/") + "#solution-faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": question,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": answer + " İlgili Koruma Ekipmanını İnceleyin: " + solution_url,
                        },
                    }
                    for _faq_id, question, answer in target.faq_items
                ],
            }
        )

    return {"@context": "https://schema.org", "@graph": graph}, emitted_offers


def _recommendation_cards(target: TargetSpec, base: str) -> str:
    cards: list[str] = []
    for index, recommendation in enumerate(target.recommendations, 1):
        href = public_url(base, recommendation.link_path)
        properties = "".join(
            f"<li><strong>{escape(name)}:</strong> {escape(value)}</li>"
            for name, value in recommendation.properties
        )
        extra = f"<ul>{properties}</ul>" if properties else ""
        cards.append(
            f'''<article id="{recommendation.deep_id}" class="alo-affiliate-aeo-v250__card" data-product-recommendation="{recommendation.key}">
<span>{index:02d} · Çözüm ürün sınıfı</span><h3>{escape(recommendation.name)}</h3>
<dl><div><dt>Kimler için?</dt><dd>{escape(recommendation.fit)}</dd></div><div><dt>Uygun değil</dt><dd>{escape(recommendation.not_fit)}</dd></div><div><dt>Önce kontrol et</dt><dd>{escape(recommendation.check)}</dd></div></dl>{extra}
<a href="{escape(href, quote=True)}">{escape(recommendation.link_label)} →</a></article>'''
        )
    return "".join(cards)


def _comparison_table(target: TargetSpec) -> str:
    if not target.comparison_rows:
        return ""
    rows = "".join(
        f"<tr><th scope=\"row\">{escape(label)}</th><td>{escape(ups)}</td><td>{escape(station)}</td></tr>"
        for label, ups, station in target.comparison_rows
    )
    return (
        '<div class="alo-affiliate-aeo-v250__table"><table>'
        '<caption>UPS ve taşınabilir güç istasyonu karşılaştırma matrisi</caption>'
        '<thead><tr><th>Kriter</th><th>UPS</th><th>Taşınabilir güç istasyonu</th></tr></thead>'
        f"<tbody>{rows}</tbody></table></div>"
    )


def _faq_block(target: TargetSpec, base: str) -> str:
    if not target.faq_items:
        return ""
    href = public_url(base, target.canonical_path) + "#" + target.scenario_id
    items = "".join(
        f'''<details id="{faq_id}"><summary>{escape(question)}</summary><p>{escape(answer)} <a href="{escape(href, quote=True)}">İlgili Koruma Ekipmanını İnceleyin</a>.</p></details>'''
        for faq_id, question, answer in target.faq_items
    )
    return '<div class="alo-affiliate-aeo-v250__faq" aria-label="Çözüm ürünleriyle devam eden sık sorulanlar">' + items + "</div>"


def _visible_block(target: TargetSpec, base: str) -> str:
    return f'''<section id="{target.scenario_id}" class="alo-affiliate-aeo-v250" {MARKER} aria-labelledby="{target.scenario_id}-baslik">
<div class="alo-affiliate-aeo-v250__head"><div><span class="alo-affiliate-aeo-v250__eyebrow">JS olmadan okunabilir teknik öneri</span><h2 id="{target.scenario_id}-baslik">{escape(target.heading)}</h2></div><p class="alo-affiliate-aeo-v250__lead">{escape(target.lead)}</p></div>
<div class="alo-affiliate-aeo-v250__grid">{_recommendation_cards(target, base)}</div>
{_comparison_table(target)}{_faq_block(target, base)}
<p class="alo-affiliate-aeo-v250__notice"><strong>Ticari şeffaflık:</strong> Bu statik özet ürün tipi ve teknik eşik önerir; fiyat, stok, puan, satıcı veya garanti yayımlamaz. Amazon bağlantısı bulunan sonraki sayfalarda satış ortaklığı ilişkisi ayrıca açıklanır. Mevcut çözüm yeterliyse yeni ürün alınmamalıdır.</p>
</section>'''


def _insert_before_last(pattern: re.Pattern[str], html: str, fragment: str, label: str) -> str:
    matches = list(pattern.finditer(html))
    if not matches:
        raise RuntimeError(f"AEO v250 {label} kapanışı bulunamadı")
    point = matches[-1].start()
    return html[:point] + fragment + "\n" + html[point:]


def _existing_ids(html: str) -> set[str]:
    return {unescape(match.group(2)).strip() for match in ID_RE.finditer(html)}


def inject_target(path: Path, target: TargetSpec, base: str) -> dict[str, object]:
    if not path.is_file():
        raise FileNotFoundError(f"AEO v250 hedef sayfası eksik: {path}")
    html = path.read_text(encoding="utf-8", errors="strict")
    if MARKER in html:
        return {"injected": False, "offerCount": 0, "canonical": canonical_from_html(html, target.canonical_path)}

    ids = _existing_ids(html)
    required_ids = {target.scenario_id, *(item.deep_id for item in target.recommendations)}
    required_ids.update(item[0] for item in target.faq_items)
    collision = sorted(required_ids & ids)
    if collision:
        raise RuntimeError(f"AEO v250 deep-link id çakışması ({target.key}): {', '.join(collision)}")

    canonical = canonical_from_html(html, target.canonical_path)
    schema, offer_count = _schema_for(target, canonical)
    schema_tag = (
        f'<script type="application/ld+json" {SCHEMA_MARKER}>'
        + json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )
    style_href = public_url(base, "/" + STYLE_TARGET.as_posix())
    style_tag = f'<link rel="stylesheet" href="{style_href}" {STYLE_MARKER}>'
    html = _insert_before_last(HEAD_CLOSE_RE, html, style_tag + "\n" + schema_tag, "head")
    close_pattern = MAIN_CLOSE_RE if MAIN_CLOSE_RE.search(html) else BODY_CLOSE_RE
    html = _insert_before_last(close_pattern, html, _visible_block(target, base), "main/body")
    path.write_text(html, encoding="utf-8")
    return {"injected": True, "offerCount": offer_count, "canonical": canonical}


def _is_affiliate_href(href: str) -> bool:
    parsed = urlsplit(unescape(href).strip())
    host = parsed.netloc.casefold().split(":", 1)[0]
    return host in {"amazon.com.tr", "www.amazon.com.tr", "amzn.to"}


def _normalize_anchor(anchor: str) -> tuple[str, bool]:
    href_match = HREF_RE.search(anchor)
    if not href_match or not _is_affiliate_href(href_match.group(2)):
        return anchor, False
    rel_match = REL_RE.search(anchor)
    if rel_match:
        tokens = [token.casefold() for token in rel_match.group(2).split() if token]
        merged = list(dict.fromkeys(tokens + sorted(REQUIRED_AFFILIATE_REL)))
        replacement = f'rel={rel_match.group(1)}{" ".join(merged)}{rel_match.group(1)}'
        normalized = anchor[: rel_match.start()] + replacement + anchor[rel_match.end() :]
        return normalized, normalized != anchor
    normalized = anchor[:-1].rstrip() + ' rel="sponsored nofollow noopener">'
    return normalized, True


def normalize_affiliate_links(site: Path) -> dict[str, object]:
    changed_links = 0
    affiliate_links = 0
    changed_pages: list[str] = []
    for path in sorted(site.rglob("*.html")):
        html = path.read_text(encoding="utf-8", errors="strict")

        def replace(match: re.Match[str]) -> str:
            nonlocal changed_links, affiliate_links
            anchor, changed = _normalize_anchor(match.group(0))
            href_match = HREF_RE.search(match.group(0))
            if href_match and _is_affiliate_href(href_match.group(2)):
                affiliate_links += 1
            if changed:
                changed_links += 1
            return anchor

        updated = ANCHOR_RE.sub(replace, html)
        if updated != html:
            path.write_text(updated, encoding="utf-8")
            changed_pages.append(path.relative_to(site).as_posix())
    return {
        "affiliateLinkCount": affiliate_links,
        "normalizedLinkCount": changed_links,
        "changedPages": changed_pages,
        "requiredRel": sorted(REQUIRED_AFFILIATE_REL),
    }


def install_root_files(site: Path) -> dict[str, object]:
    for source in (LLMS_SOURCE, ROBOTS_SOURCE):
        if not source.is_file():
            raise FileNotFoundError(f"AEO v250 kök kaynak eksik: {source}")
    shutil.copy2(LLMS_SOURCE, site / "llms.txt")
    shutil.copy2(ROBOTS_SOURCE, site / "robots.txt")
    robots = (site / "robots.txt").read_text(encoding="utf-8")
    missing = [crawler for crawler in AI_CRAWLERS if f"User-agent: {crawler}" not in robots]
    if missing:
        raise RuntimeError("AEO v250 robots AI crawler eksik: " + ", ".join(missing))
    llms = (site / "llms.txt").read_text(encoding="utf-8")
    required_headings = (
        "## Resmî ve acil kanallar",
        "## Teknik çözüm ve ekipman rehberleri",
        "### Ev ve ofis kesinti hazırlığı",
        "### Cihaz ve pano koruma ekipmanları",
        "### GES ve yedek enerji sistemleri",
    )
    if any(value not in llms for value in required_headings):
        raise RuntimeError("AEO v250 llms.txt hiyerarşisi eksik")
    return {
        "llmsInstalled": True,
        "robotsInstalled": True,
        "crawlerCount": len(AI_CRAWLERS),
        "crawlers": list(AI_CRAWLERS),
    }


def _refresh_checksums(site: Path) -> None:
    target = site / "checksums.sha256"
    if not target.exists():
        return
    target.unlink()
    files = sorted(path for path in site.rglob("*") if path.is_file())
    target.write_text(
        "\n".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(site).as_posix()}"
            for path in files
        )
        + "\n",
        encoding="utf-8",
    )


def _update_release(site: Path, result: dict[str, object]) -> None:
    path = site / "pages-release.json"
    if not path.is_file():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["affiliateAeoV250"] = result
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def inject(site: Path, base_path: str = "") -> dict[str, object]:
    site = site.resolve()
    base = normalize_base_path(base_path)
    if not site.is_dir() or not STYLE_SOURCE.is_file():
        raise FileNotFoundError("AEO v250 site veya stil kaynağı eksik")
    style_target = site / STYLE_TARGET
    style_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(STYLE_SOURCE, style_target)
    root_files = install_root_files(site)

    target_results: dict[str, dict[str, object]] = {}
    for target in TARGETS:
        target_results[target.key] = inject_target(site / target.file, target, base)

    affiliate_links = normalize_affiliate_links(site)
    emitted_offers = sum(int(value["offerCount"]) for value in target_results.values())
    injected = [key for key, value in target_results.items() if value["injected"]]
    result: dict[str, object] = {
        "version": VERSION,
        "ok": True,
        "basePath": base,
        "targetCount": len(TARGETS),
        "targets": [target.key for target in TARGETS],
        "injectedTargets": injected,
        "deepLinkCount": sum(1 + len(target.recommendations) + len(target.faq_items) for target in TARGETS),
        "ssrRecommendationCardCount": sum(len(target.recommendations) for target in TARGETS),
        "schemaTypes": ["Guide", "Product", "Recommendation", "ItemList", "FAQPage"],
        "comparisonMatrixCount": sum(bool(target.comparison_rows) for target in TARGETS),
        "offerPolicy": "conditional_verified_merchant_payload_only",
        "offerFreshnessHours": 24,
        "emittedOfferCount": emitted_offers,
        "fakePriceOrStockPublished": False,
        "affiliateLinks": affiliate_links,
        "rootFiles": root_files,
    }
    _update_release(site, result)
    _refresh_checksums(site)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 affiliate AEO, deep-link, SSR, llms.txt ve crawler katmanı v250")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(inject(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
