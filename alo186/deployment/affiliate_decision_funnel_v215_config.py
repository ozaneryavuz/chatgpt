from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

VERSION = 215
MARKER = 'data-alo186-affiliate-decision-v215="true"'
STYLE_MARKER = 'data-alo186-affiliate-decision-v215-style="true"'
SCRIPT_MARKER = 'data-alo186-affiliate-decision-v215-script="true"'
ASSET_JS = Path("assets/affiliate-decision-funnel-v215.js")
ASSET_CSS = Path("assets/affiliate-decision-funnel-v215.css")
SOURCE_JS = Path(__file__).with_name("affiliate_decision_funnel_v215.js")
SOURCE_CSS = Path(__file__).with_name("affiliate_decision_funnel_v215.css")
CONTRACT_NAME = "affiliate-event-contract-v215.json"
PLACEMENTS = (
    "decision_intro",
    "decision_tier_card",
    "decision_result_cta",
    "decision_no_buy",
    "decision_blocked",
)
EVENTS = (
    "affiliate_decision_view",
    "affiliate_decision_result",
    "affiliate_decision_select",
    "no_buy_result",
    "commerce_blocked",
)
REASONS = (
    "existing_solution_sufficient",
    "insufficient_evidence",
    "professional_only",
    "unsafe_equipment",
    "medical_or_life_safety",
)
TIERS = ("basic", "balanced", "long_runtime")


@dataclass(frozen=True)
class Target:
    flow: str
    path: Path
    title: str
    lead: str
    route: str
    label: str
    needles: tuple[str, ...]
    controls: bool = False


TARGETS = (
    Target(
        "mini_ups",
        Path("amazon-elektrik-urunleri/modem-mini-ups-secimi/index.html"),
        "Mini UPS için doğru teknik sınıfı belirleyin.",
        "Gerilim, jak ve polarite doğrulanmadan ürün yolu açılmaz.",
        "/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/",
        "Modem ve ONT teknik seçicisini aç",
        ("Güvenli ticari rota", "Kısa yanıtlar", "</main>"),
        True,
    ),
    Target(
        "ups_runtime",
        Path("hesaplama/ups-suresi/index.html"),
        "UPS hesabını üç kapasite sınıfına çevirin.",
        "VA ile Wh’yi ayırın; sürekli yük, tepe güç, verim ve hedef süreyi birlikte doğrulayın.",
        "/akilli-urun-secimi?kategori=ups",
        "UPS teknik sınıflarını karşılaştır",
        ('<div id="productRoute"', '<section class="content-section faq"', "</main>"),
    ),
    Target(
        "power_station",
        Path("hesaplama/power-station-kapasite-eps-uygunluk/index.html"),
        "Wh sonucunu güvenlik ve EPS kapısıyla yorumlayın.",
        "Kapasiteye ek olarak saf sinüs, sürekli/tepe güç, geçiş ve bağlantı biçimi doğrulanır.",
        "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi",
        "Power station teknik rehberini aç",
        ('id="productRoute"', 'id="commercePath"', "</main>"),
    ),
)

TIER_COPY = {
    "mini_ups": (
        (
            "basic",
            "Temel güvenli sınıf",
            "Tek modem/ONT ve 2 saate kadar.",
            "Belirsiz gerilim, jak veya polarite.",
            "Gerilim, polarite, jak, çıkış akımı ve gerçek prova.",
        ),
        (
            "balanced",
            "Dengeli sınıf",
            "Modem + ONT veya 2–6 saat.",
            "PoE/özel adaptör ya da saha arızası.",
            "Toplam W, çıkış sayısı ve kullanılabilir Wh.",
        ),
        (
            "long_runtime",
            "Uzun süre sınıfı",
            "Çoklu ağ cihazı veya 6 saatten uzun.",
            "Tıbbi yük ve doğrulanmamış bağlantı.",
            "Zincir yükü, Wh rezervi, sıcaklık ve batarya yaşı.",
        ),
    ),
    "ups_runtime": (
        (
            "basic",
            "Temel UPS sınıfı",
            "Düşük güçlü elektronik yük ve yaklaşık 500 Wh’a kadar.",
            "Motor, 2 kW üzeri yük veya üç faz.",
            "Sürekli W, VA, güç faktörü, Wh ve gerçek runtime.",
        ),
        (
            "balanced",
            "Dengeli UPS sınıfı",
            "Birden fazla elektronik yük ve 500–1.500 Wh.",
            "0 ms zorunluluğu veya sabit tesisat.",
            "Çıkış W/VA, akü kimyası, iletişim ve tepe güç.",
        ),
        (
            "long_runtime",
            "Uzun süre UPS sınıfı",
            "1.500 Wh üzeri veya uzun kontrollü kapanma.",
            "Asansör, pompa, tıbbi yük ve proje sistemleri.",
            "Batarya dizisi, şarj, sıcaklık, bakım ve bypass.",
        ),
    ),
    "power_station": (
        (
            "basic",
            "Temel power station sınıfı",
            "Telefon, modem, LED ve yaklaşık 500 Wh’a kadar.",
            "Motor, sabit tesisat veya 0 ms geçiş.",
            "Wh, sürekli W, port gücü ve doğrudan bağlantı.",
        ),
        (
            "balanced",
            "Dengeli power station sınıfı",
            "Dizüstü/iletişim yükü ve 500–1.200 Wh.",
            "Onaysız motor, yetersiz surge veya saf sinüs belirsizliği.",
            "Saf sinüs, sürekli/tepe W, EPS ve gerçek prova.",
        ),
        (
            "long_runtime",
            "Uzun süre power station sınıfı",
            "1.200 Wh üzeri, taşınabilir ve gözetimli kullanım.",
            "Tıbbi yük, EV şarjı veya bina geri beslemesi.",
            "Havalandırma, kimya, ısı, şarj ve topraklama.",
        ),
    ),
}


def normalize_base_path(value: str) -> str:
    cleaned = (value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def public_url(base: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base}{route}" if base else route


def event_contract() -> dict:
    common = {
        "version": {"type": "integer", "required": True, "allowed": [VERSION]},
        "flow": {
            "type": "enum",
            "required": True,
            "allowed": [item.flow for item in TARGETS],
        },
        "placement": {
            "type": "enum",
            "required": True,
            "allowed": list(PLACEMENTS),
        },
    }
    return {
        "version": VERSION,
        "name": "ALO186 affiliate decision funnel event contract",
        "privacy": {
            "requiresAnalyticsConsentForGa4": True,
            "rawDestinationUrlAllowed": False,
            "amazonSearchQueryAllowed": False,
            "asinAllowed": False,
            "freeTextAllowed": False,
            "userOrDeviceIdentifierAllowed": False,
            "numericElectricalInputsAllowed": False,
        },
        "events": {
            "affiliate_decision_view": {"parameters": common},
            "affiliate_decision_result": {
                "parameters": {
                    **common,
                    "state": {
                        "type": "enum",
                        "required": True,
                        "allowed": ["eligible"],
                    },
                    "tier": {
                        "type": "enum",
                        "required": True,
                        "allowed": list(TIERS),
                    },
                }
            },
            "affiliate_decision_select": {
                "parameters": {
                    **common,
                    "tier": {
                        "type": "enum",
                        "required": True,
                        "allowed": list(TIERS),
                    },
                }
            },
            "no_buy_result": {
                "parameters": {
                    **common,
                    "reason": {
                        "type": "enum",
                        "required": True,
                        "allowed": [REASONS[0]],
                    },
                }
            },
            "commerce_blocked": {
                "parameters": {
                    **common,
                    "reason": {
                        "type": "enum",
                        "required": True,
                        "allowed": list(REASONS[1:]),
                    },
                }
            },
        },
    }
