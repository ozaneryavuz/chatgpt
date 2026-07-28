from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("synthetic_check.py")
SPEC = importlib.util.spec_from_file_location("alo186_synthetic_check", MODULE_PATH)
assert SPEC and SPEC.loader
synthetic_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(synthetic_check)


def analyze(html: str) -> dict[str, object]:
    return synthetic_check.analyze_device_damage_text(html)


def test_detects_30_day_device_damage_claim_in_visible_text() -> None:
    result = analyze(
        """
        <main>
          <h2>Elektrik kesintisi cihazımı bozdu</h2>
          <p>Zararın ortaya çıktığı tarihten itibaren 30 gün içinde EDAŞ kaydı açın.</p>
          <p>ALO186 arıza ihbarı almaz.</p>
        </main>
        """
    )
    assert result["has30DayDamageClaim"] is True
    assert result["has10BusinessDayDamageClaim"] is False
    assert result["hasAlo186NoApplicationDisclaimer"] is True


def test_accepts_10_business_day_official_channel_wording() -> None:
    result = analyze(
        """
        <main>
          <h2>Elektrik kesintisi cihazımı bozdu</h2>
          <p>
            Dağıtım şebekesinden kaynaklandığını düşündüğünüz cihaz hasarı için,
            zararın ortaya çıktığı tarihten itibaren 10 iş günü içinde ilgili
            dağıtım şirketinin resmî kanalına başvurun.
          </p>
          <p>ALO186 başvuru veya hasar kaydı almaz.</p>
        </main>
        """
    )
    assert result["has30DayDamageClaim"] is False
    assert result["has10BusinessDayDamageClaim"] is True
    assert result["hasAlo186NoApplicationDisclaimer"] is True


def test_jsonld_old_deadline_is_detected_even_when_visible_text_is_correct() -> None:
    result = analyze(
        """
        <p>Cihaz hasarı için 10 iş günü içinde dağıtım şirketine başvurun.</p>
        <p>ALO186 başvuru almaz.</p>
        <script type="application/ld+json">
        {
          "@type": "FAQPage",
          "mainEntity": [{
            "name": "Cihaz hasarı başvurusu",
            "acceptedAnswer": {
              "text": "Hasar için 30 gün içinde EDAŞ'a talepte bulunun."
            }
          }]
        }
        </script>
        """
    )
    assert result["has10BusinessDayDamageClaim"] is True
    assert result["has30DayDamageClaim"] is True


def test_unrelated_30_day_period_is_not_a_false_positive() -> None:
    result = analyze(
        """
        <main>
          <p>Fatura itirazınıza verilen yanıtı 30 gün saklayın.</p>
          <p>Cihaz hasarı için 10 iş günü içinde dağıtım şirketine başvurun.</p>
          <p>ALO186 ihbar veya başvuru toplamaz.</p>
        </main>
        """
    )
    assert result["has30DayDamageClaim"] is False
    assert result["has10BusinessDayDamageClaim"] is True


def test_turkish_character_folding_covers_techizat_and_resmi_wording() -> None:
    result = analyze(
        """
        <p>
          Teçhizat zararının ortaya çıktığı tarihten itibaren 10 iş günü içerisinde
          ilgili dağıtım şirketinin resmî başvuru kanalını kullanın.
        </p>
        <p>ALO186 resmî kurum değildir ve hasar kaydı almaz.</p>
        """
    )
    assert result["has10BusinessDayDamageClaim"] is True
    assert result["hasAlo186NoApplicationDisclaimer"] is True
