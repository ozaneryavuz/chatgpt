from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path

VERSION = 177
TAG = "alo186rehber-21"
MARKER = "data-alo186-contextual-affiliate-v177"
CSS_FILE = "assets/alo186-contextual-affiliate-v177.css"
JS_FILE = "assets/alo186-contextual-affiliate-v177.js"
DISCLOSURE = "Bir Amazon Gelir Ortağı olarak nitelikli satın alımlardan kazanç elde ediyorum."

EXISTING_COMMERCE_MARKERS = (
    "amazon.com.tr",
    "affiliate-panel",
    "affiliatepanel",
    "affiliatecheck",
    "data-alo186-commerce",
    "data-affiliate",
    "koşullu satış ortaklığı yolu",
)


def product(title: str, use_when: str, skip_when: str, query: str, guide: str) -> dict[str, str]:
    return {
        "title": title,
        "useWhen": use_when,
        "skipWhen": skip_when,
        "query": query,
        "guide": guide,
    }


PRODUCTS: dict[str, dict[str, str]] = {
    "powerbank_pd": product(
        "USB-C PD powerbank",
        "Telefon, modem veya düşük güçlü USB-C cihaz için ölçülmüş enerji açığı varsa.",
        "Mevcut powerbank kapasite ve güç testini zaten geçiyorsa yeni ürün almayın.",
        "USB C PD powerbank 20000 mAh",
        "/amazon-elektrik-urunleri/powerbank-usb-c-secimi/",
    ),
    "usb_c_charger": product(
        "Çok portlu USB-C PD şarj cihazı",
        "Toplam güç bütçesi ve her portun PD profili cihazlarla eşleşiyorsa.",
        "Cihazların mevcut adaptörleri güvenli ve yeterliyse ek adaptör almayın.",
        "çok portlu USB C PD şarj cihazı 65W 100W",
        "/amazon-elektrik-urunleri/tasinabilir-enerji-sarj-urunleri/",
    ),
    "usb_c_cable": product(
        "E-marker etiketli USB-C kablo",
        "Kablo güç veya veri hızını sınırlıyor ve gereken W/Gbps değeri doğrulandıysa.",
        "Mevcut kablo hedef güç ve veri testini geçiyorsa değiştirmeyin.",
        "USB C E Marker 100W 240W kablo",
        "/amazon-elektrik-urunleri/tasinabilir-enerji-sarj-urunleri/",
    ),
    "usb_c_hub": product(
        "USB-C çoklayıcı ve görüntü hub'ı",
        "Bilgisayarın port yeteneği, görüntü standardı ve PD geçiş gücü doğrulandıysa.",
        "Tek bir adaptör ihtiyacı çözüyor veya cihaz DisplayPort Alt Mode desteklemiyorsa almayın.",
        "USB C hub HDMI Ethernet PD",
        "/amazon-elektrik-urunleri/tasinabilir-enerji-sarj-urunleri/",
    ),
    "usb_ethernet": product(
        "USB-C Gigabit Ethernet adaptörü",
        "Wi-Fi yerine kablolu bağlantı gerekiyor ve cihaz portu veri aktarımını destekliyorsa.",
        "Sorun modem, servis sağlayıcı veya kablodaysa adaptör almayın.",
        "USB C Gigabit Ethernet adaptörü",
        "/amazon-elektrik-urunleri/tasinabilir-enerji-sarj-urunleri/",
    ),
    "usb_power_meter": product(
        "USB-C güç ölçer",
        "Şarj zincirinde gerçek voltaj, akım ve güç değerini doğrulamak gerekiyorsa.",
        "Sadece günlük şarj için ölçüm gerekmiyorsa ek cihaz almayın.",
        "USB C güç ölçer PD tester",
        "/amazon-elektrik-urunleri/tasinabilir-enerji-sarj-urunleri/",
    ),
    "cat6_cable": product(
        "CAT6 Ethernet patch kablosu",
        "Adaptör ve port Gigabit destekliyor, fakat mevcut kablo hatalı veya yetersizse.",
        "Mevcut kablo bağlantı ve hız testini geçiyorsa yenisini almayın.",
        "CAT6 Ethernet patch kablo",
        "/amazon-elektrik-urunleri/tasinabilir-enerji-sarj-urunleri/",
    ),
    "rechargeable_bulb": product(
        "Şarjlı acil durum ampulü",
        "Duy tipi, anahtar davranışı ve beklenen çalışma süresi testle uygunsa.",
        "Sabit acil aydınlatma projesinin yerine kullanmayın; mevcut lamba yeterliyse almayın.",
        "şarjlı acil durum ampulü E27",
        "/amazon-elektrik-urunleri/acil-aydinlatma-duman-alarmi/",
    ),
    "led_bulb": product(
        "Uygun lümen ve Kelvin değerli LED ampul",
        "Hesaplanan lümen, duy tipi, boyut ve renk sıcaklığı birlikte eşleşiyorsa.",
        "Mevcut aydınlatma ölçümü yeterliyse yalnız daha yüksek watt için ürün almayın.",
        "LED ampul E27 lümen 3000K 4000K",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
    ),
    "flashlight": product(
        "Şarjlı el feneri",
        "Gece tahliye rotası için ayrı, kolay erişilen ve düzenli test edilen ışık gerekiyorsa.",
        "Telefon flaşı ve mevcut fener güvenli süreyi karşılıyorsa yenisini almayın.",
        "şarjlı el feneri USB C",
        "/amazon-elektrik-urunleri/acil-aydinlatma-duman-alarmi/",
    ),
    "headlamp": product(
        "Şarjlı kafa lambası",
        "Eller serbest çalışma veya güvenli hareket için kişisel ışık gerekiyorsa.",
        "Sadece dekoratif kullanım için ya da mevcut ekipman yeterliyse almayın.",
        "şarjlı kafa lambası USB C",
        "/amazon-elektrik-urunleri/acil-aydinlatma-duman-alarmi/",
    ),
    "lantern": product(
        "Şarjlı kamp ve masa feneri",
        "Bir odayı düşük güçle uzun süre aydınlatma ihtiyacı ölçüldüyse.",
        "Tahliye yönlendirmesi gereken yerde sabit acil aydınlatmanın yerine kullanmayın.",
        "şarjlı kamp feneri USB C",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
    ),
    "night_light": product(
        "Sensörlü gece lambası",
        "Karanlıkta koridor ve basamak görünürlüğü için düşük seviyeli yön ışığı gerekiyorsa.",
        "Acil aydınlatma veya duman algılama yerine kullanmayın.",
        "sensörlü gece lambası şarjlı",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
    ),
    "fridge_thermometer": product(
        "Buzdolabı ve dondurucu termometresi",
        "Kesinti sırasında sıcaklık yükselişini kayıtla izlemek gerekiyorsa.",
        "Cihazın kalibre edilmiş kayıt sistemi zaten varsa ikinci ürün almayın.",
        "buzdolabı dondurucu termometresi alarmı",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
    ),
    "freezer_alarm": product(
        "Sıcaklık alarmı ve veri kaydedici",
        "Gıda veya ilaç saklama alanında eşik aşımının duyulması ya da kaydedilmesi gerekiyorsa.",
        "Profesyonel soğuk zincir zorunluluğunda tüketici tipi cihazla yetinmeyin.",
        "dondurucu sıcaklık alarmı data logger",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
    ),
    "water_leak_alarm": product(
        "Su kaçağı alarmı",
        "Bodrum, tesisat altı veya cihaz çevresinde erken su algılama noktası belirlendiyse.",
        "Elektriksel izolasyon, drenaj veya profesyonel sensör sisteminin yerine kullanmayın.",
        "su kaçağı alarmı sensörü",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
    ),
    "water_level_alarm": product(
        "Yüksek su seviye alarmı",
        "Kuyu, hazne veya bodrumda taşma eşiği ve sensör konumu güvenle belirlendiyse.",
        "Şebeke gerilimli sabit tesisata yetkisiz bağlantı gerektiriyorsa almayın.",
        "yüksek su seviye alarmı pilli",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
    ),
    "aquarium_battery_pump": product(
        "Pilli akvaryum hava pompası",
        "Balık yükü ve kesinti süresi için gereken minimum hava debisi hesaplandıysa.",
        "Mevcut yedek hava sistemi testte süreyi karşılıyorsa ek pompa almayın.",
        "pilli akvaryum hava pompası",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
    ),
    "aquarium_usb_pump": product(
        "USB akvaryum hava pompası",
        "Pompanın güç tüketimi ve powerbank çalışma süresi birlikte doğrulandıysa.",
        "USB çıkış kesildiğinde otomatik yeniden başlamıyorsa kritik canlı yükte tek çözüm yapmayın.",
        "USB akvaryum hava pompası powerbank",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
    ),
    "rechargeable_fan": product(
        "Şarjlı masa vantilatörü",
        "Oda sıcaklığı, kişi ihtiyacı ve gereken çalışma süresi ölçüldüyse.",
        "Aşırı sıcaklık sağlık riski oluşturuyorsa yalnız vantilatöre güvenmeyin.",
        "şarjlı masa vantilatörü USB C",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
    ),
    "usb_fan": product(
        "Düşük güçlü USB vantilatör",
        "Powerbank güç bütçesi içinde küçük bir kişisel serinleme yükü gerekiyorsa.",
        "Büyük oda veya sağlık riski için yetersizse ürün alıp yanlış güven oluşturmayın.",
        "USB masa vantilatörü sessiz",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
    ),
    "room_thermometer": product(
        "Oda termometresi ve higrometre",
        "Sıcaklık/nem kararını varsayım yerine ölçümle vermek gerekiyorsa.",
        "Mevcut güvenilir sensör aynı noktayı izliyorsa yenisini almayın.",
        "dijital oda termometresi higrometre",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
    ),
    "smart_plug": product(
        "Enerji ölçümlü akıllı priz",
        "Yük gücü, fiş tipi ve uzaktan kontrolün güvenli kullanım sınırı doğrulandıysa.",
        "Isıtıcı, motor veya yüksek başlangıç akımlı yük üretici sınırını aşıyorsa kullanmayın.",
        "enerji ölçümlü akıllı priz",
        "/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi/",
    ),
    "plug_wattmeter": product(
        "Priz tipi enerji ölçer",
        "Gerçek güç, enerji ve bekleme tüketimini ölçmek için taşınabilir sayaç gerekiyorsa.",
        "Sabit tesisat veya yüksek akım ölçümü gerekiyorsa tüketici tipi ürünü kullanmayın.",
        "priz tipi enerji ölçer wattmetre",
        "/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi/",
    ),
    "grounded_strip": product(
        "Topraklı grup priz",
        "Toprak sürekliliği, kablo kesiti ve toplam yük uygunluk kontrolünü geçtiyse.",
        "Topraklaması belirsiz veya aşırı yüklenen hatta daha çok priz eklemeyin.",
        "topraklı grup priz çocuk korumalı",
        "/amazon-elektrik-urunleri/akim-korumali-grup-priz-secimi/",
    ),
    "extension_cord": product(
        "Uygun kesitli uzatma kablosu",
        "Yük akımı, mesafe, gerilim düşümü ve ortam şartı hesaplandıysa.",
        "Kalıcı tesisat ihtiyacını seyyar kabloyla çözmeyin; makara sarılıyken yüksek yük bağlamayın.",
        "topraklı uzatma kablosu 3x1.5",
        "/amazon-elektrik-urunleri/ev-elektrik-olcum-koruma-urunleri/",
    ),
    "cable_reel": product(
        "Termik korumalı kablo makarası",
        "Açık/sarılı akım sınırı, kablo kesiti ve kullanım ortamı doğrulandıysa.",
        "Sabit tesisat yerine veya tamamen sarılı halde yüksek güçte kullanmayın.",
        "termik korumalı kablo makarası 3x1.5",
        "/amazon-elektrik-urunleri/ev-elektrik-olcum-koruma-urunleri/",
    ),
    "surge_plug": product(
        "Taşınabilir aşırı gerilim korumalı priz",
        "Topraklama doğrulandı ve hassas yük için ek son-kademe koruma gerekiyorsa.",
        "Bina tipi parafudr, doğru topraklama veya elektrikçi incelemesinin yerine kullanmayın.",
        "aşırı gerilim korumalı priz topraklı",
        "/amazon-elektrik-urunleri/akim-korumali-grup-priz-secimi/",
    ),
    "travel_adapter": product(
        "Ülke tipi seyahat priz adaptörü",
        "Gidilecek ülkenin priz standardı ve cihazın giriş gerilimi ayrı ayrı doğrulandıysa.",
        "Adaptörü gerilim dönüştürücü sanmayın; cihaz 100–240 V desteklemiyorsa kullanmayın.",
        "uluslararası seyahat priz adaptörü USB C",
        "/amazon-elektrik-urunleri/tasinabilir-enerji-sarj-urunleri/",
    ),
    "car_charger": product(
        "USB-C PD araç şarj cihazı",
        "Araç priz sigortası, adaptör toplam gücü ve cihaz PD profili uyumluysa.",
        "Yüksek güçlü AC cihazı çalıştırmak için USB araç şarj cihazı almayın.",
        "USB C PD araç şarj cihazı 65W",
        "/amazon-elektrik-urunleri/tasinabilir-enerji-sarj-urunleri/",
    ),
    "modem_mini_ups": product(
        "Modem ve ONT mini UPS",
        "Cihazların voltaj, polarite, konnektör ve toplam watt değerleri tek tek eşleşiyorsa.",
        "Fiber/DSL altyapısı kesintide çalışmıyorsa veya mevcut UPS süreyi karşılıyorsa almayın.",
        "modem mini UPS 12V 9V 5V",
        "/amazon-elektrik-urunleri/modem-mini-ups-secimi/",
    ),
    "portable_power_station": product(
        "Taşınabilir güç istasyonu",
        "Sürekli/başlangıç gücü, Wh ihtiyacı, şarj süresi ve kullanım ortamı hesaplandıysa.",
        "Sabit tesisat, yaşam destek cihazı veya uygun olmayan yüksek güçlü yük için kullanmayın.",
        "taşınabilir güç istasyonu LiFePO4",
        "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi/",
    ),
    "rechargeable_battery": product(
        "Düşük kendi kendine deşarjlı AA/AAA pil",
        "Cihaz üreticisi şarjlı pil gerilimine izin veriyor ve düzenli test planı varsa.",
        "Duman alarmı veya kilit üreticisi tek kullanımlık pil istiyorsa şarjlı pil kullanmayın.",
        "düşük deşarjlı şarjlı AA AAA pil NiMH",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
    ),
    "lock_battery": product(
        "Akıllı kilit için üretici uyumlu pil",
        "Kilit kılavuzundaki kimya, boyut ve voltaj gereksinimi doğrulandıysa.",
        "Farklı pil kimyalarını karıştırmayın; düşük pil uyarısını yalnız yedek güçle ertelemeyin.",
        "akıllı kilit AA alkalin CR123A pil",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
    ),
    "battery_tester": product(
        "Pil test cihazı",
        "Yedek pillerin gerilimini yük altında ayırmak ve bakım kaydı tutmak gerekiyorsa.",
        "Kritik cihaz üreticisinin değiştirme periyodunu yalnız test sonucuyla uzatmayın.",
        "AA AAA 9V pil test cihazı",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/",
    ),
}

PLACEMENTS: dict[str, tuple[str, str, str]] = {
    "hesaplama/powerbank-ucak-wh-kabin-bagaji-uygunluk/index.html": ("powerbank_pd", "usb_c_charger", "usb_c_cable"),
    "hesaplama/powerbank-ucak-wh-uygunluk/index.html": ("powerbank_pd", "usb_power_meter", "usb_c_cable"),
    "hesaplama/usb-c-sarj-zinciri-uygunluk/index.html": ("usb_c_charger", "usb_c_cable", "usb_power_meter"),
    "hesaplama/usb-c-set-kisa-listesi/index.html": ("usb_c_charger", "usb_c_cable", "usb_c_hub"),
    "hesaplama/usb-c-sarj-cihazi-kablo-uygunluk/index.html": ("usb_c_charger", "usb_c_cable", "usb_power_meter"),
    "hesaplama/usb-c-urun-kabul-testi/index.html": ("usb_power_meter", "usb_c_cable", "usb_c_charger"),
    "hesaplama/akim-korumali-grup-priz-uygunluk/index.html": ("surge_plug", "grounded_strip", "plug_wattmeter"),
    "sektor-rehberi/usb-c-seyahat-sarj-ve-power-bank-test-merkezi/index.html": ("usb_c_charger", "usb_c_cable", "powerbank_pd"),
    "urun-bilgi-grafigi/usb-c-ekosistemi/index.html": ("usb_c_charger", "usb_c_hub", "usb_ethernet"),
    "hesaplama/acil-aydinlatma-sure-uygunluk/index.html": ("rechargeable_bulb", "flashlight", "lantern"),
    "hesaplama/aydinlatma-ihtiyac-ve-ampul-uygunluk/index.html": ("led_bulb", "night_light", "rechargeable_bulb"),
    "hesaplama/acil-aydinlatma-test-bakim-gunlugu/index.html": ("rechargeable_bulb", "flashlight", "rechargeable_battery"),
    "sektor-rehberi/ev-acil-aydinlatma-batarya-test-merkezi/index.html": ("flashlight", "headlamp", "lantern"),
    "sektor-rehberi/elektrik-kesintisi-gece-guvenligi-aydinlatma-merkezi/index.html": ("flashlight", "lantern", "night_light"),
    "sektor-rehberi/elektrik-kesintisi-aydinlatma-ve-guvenli-uzatma-merkezi/index.html": ("rechargeable_bulb", "extension_cord", "cable_reel"),
    "hesaplama/buzdolabi-dondurucu-kesinti-guvenligi/index.html": ("fridge_thermometer", "freezer_alarm", "portable_power_station"),
    "hesaplama/buzdolabi-dondurucu-sicaklik-alarmi-uygunluk/index.html": ("fridge_thermometer", "freezer_alarm", "smart_plug"),
    "sektor-rehberi/buzdolabi-dondurucu-soguk-zincir-kesinti-merkezi/index.html": ("fridge_thermometer", "freezer_alarm", "portable_power_station"),
    "sektor-rehberi/elektrik-kesintisi-buzdolabi-gida-guvenligi-merkezi/index.html": ("fridge_thermometer", "freezer_alarm", "lantern"),
    "sektor-rehberi/ev-bodrum-su-baskini-elektrik-kesintisi-test-merkezi/index.html": ("water_leak_alarm", "water_level_alarm", "flashlight"),
    "hesaplama/akvaryum-elektrik-kesintisi-yedek-guc-uygunluk/index.html": ("aquarium_battery_pump", "aquarium_usb_pump", "powerbank_pd"),
    "sektor-rehberi/akvaryum-elektrik-kesintisi-sureklilik-merkezi/index.html": ("aquarium_battery_pump", "aquarium_usb_pump", "powerbank_pd"),
    "sektor-rehberi/akvaryum-elektrik-kesintisi-tekrar-test-merkezi/index.html": ("aquarium_battery_pump", "powerbank_pd", "room_thermometer"),
    "hesaplama/vantilator-hava-sogutucu-klima-karar/index.html": ("rechargeable_fan", "usb_fan", "room_thermometer"),
    "hesaplama/vantilator-hava-sogutucu-portatif-klima-karsilastirma/index.html": ("rechargeable_fan", "usb_fan", "powerbank_pd"),
    "sektor-rehberi/sicak-hava-elektrik-kesintisi-serinleme-test-merkezi/index.html": ("rechargeable_fan", "usb_fan", "powerbank_pd"),
    "sektor-rehberi/akilli-kilit-erisim-surekliligi-test-merkezi/index.html": ("lock_battery", "battery_tester", "powerbank_pd"),
    "hesaplama/akilli-priz-yuk-enerji-uygunluk/index.html": ("smart_plug", "plug_wattmeter", "surge_plug"),
    "hesaplama/uzatma-kablosu-kablo-makarasi-yuk-uygunluk/index.html": ("extension_cord", "cable_reel", "grounded_strip"),
    "hesaplama/priz-tipi-enerji-olcer-standby-deneyi/index.html": ("plug_wattmeter", "smart_plug", "surge_plug"),
    "hesaplama/gece-baz-yuk-standby-tuketim-deneyi/index.html": ("plug_wattmeter", "smart_plug", "grounded_strip"),
    "hesaplama/akilli-priz-enerji-anomali-gunlugu/index.html": ("smart_plug", "plug_wattmeter", "surge_plug"),
    "sektor-rehberi/priz-uzatma-kablosu-koruma-test-merkezi/index.html": ("grounded_strip", "extension_cord", "cable_reel"),
    "hesaplama/seyahat-priz-adaptoru-voltaj-donusturucu-uygunluk/index.html": ("travel_adapter", "usb_c_charger", "usb_c_cable"),
    "hesaplama/arac-12v-priz-inverter-yuk-uygunluk/index.html": ("car_charger", "usb_c_cable", "powerbank_pd"),
    "hesaplama/sac-kurutma-kettle-seyahat-gerilim-uygunluk/index.html": ("travel_adapter", "usb_c_charger", "usb_c_cable"),
    "sektor-rehberi/yurt-disi-seyahat-priz-sarj-tekrar-test-merkezi/index.html": ("travel_adapter", "usb_c_charger", "powerbank_pd"),
    "sektor-rehberi/elektronik-cihaz-guc-seyahat-koruma-merkezi/index.html": ("travel_adapter", "surge_plug", "usb_c_charger"),
    "hesaplama/home-office-internet-sureklilik-plani/index.html": ("modem_mini_ups", "powerbank_pd", "usb_c_charger"),
    "hesaplama/tv-oyun-konsolu-modem-yedek-guc-uygunluk/index.html": ("modem_mini_ups", "portable_power_station", "grounded_strip"),
}

CSS = r"""/* ALO186 contextual affiliate growth v177 */
.alo186-contextual-commerce{margin:28px auto;padding:clamp(18px,3vw,28px);border:1px solid #d9e3ee;border-radius:22px;background:linear-gradient(180deg,#fff 0%,#f7fafc 100%);box-shadow:0 14px 38px rgba(7,22,49,.09);color:#17233a}
.alo186-contextual-commerce *{box-sizing:border-box;overflow-wrap:anywhere}
.alo186-contextual-commerce__head{max-width:800px}.alo186-contextual-commerce__eyebrow{display:inline-flex;margin:0 0 8px;padding:5px 9px;border-radius:999px;background:#eaf4ff;color:#0b4f8a;font-size:.78rem;font-weight:850;letter-spacing:.02em}.alo186-contextual-commerce h2{margin:0 0 10px;font-size:clamp(1.35rem,3vw,1.9rem);line-height:1.16;color:#071631}.alo186-contextual-commerce__intro{margin:0;color:#4b5f78;line-height:1.65}
.alo186-contextual-commerce__cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:20px 0}.alo186-contextual-product{display:flex;min-width:0;flex-direction:column;padding:17px;border:1px solid #d6e1ec;border-radius:17px;background:#fff}.alo186-contextual-product h3{margin:4px 0 10px;font-size:1.05rem;line-height:1.32;color:#071631}.alo186-contextual-product p{margin:0 0 9px;color:#475a72;font-size:.92rem;line-height:1.55}.alo186-contextual-product__label{font-size:.72rem;font-weight:850;letter-spacing:.05em;text-transform:uppercase;color:#116399}
.alo186-contextual-product__actions{display:grid;gap:8px;margin-top:auto;padding-top:8px}.alo186-contextual-product__actions a{display:inline-flex;min-height:44px;align-items:center;justify-content:center;padding:10px 12px;border-radius:11px;text-align:center;font-weight:800;text-decoration:none}.alo186-contextual-product__guide{border:1px solid #b9c9d8;background:#fff;color:#17395c}.alo186-contextual-product__store{border:1px solid #071631;background:#071631;color:#fff}.alo186-contextual-product__store[aria-disabled="true"]{cursor:not-allowed;border-color:#aab5c1;background:#e6ebf0;color:#5e6b78}
.alo186-contextual-gate{margin:0;padding:15px;border:1px solid #cdd9e5;border-radius:15px;background:#f9fbfd}.alo186-contextual-gate legend{padding:0 6px;font-weight:850;color:#071631}.alo186-contextual-gate label{display:flex;gap:10px;align-items:flex-start;margin:10px 0;color:#263b54;line-height:1.5}.alo186-contextual-gate input{width:20px;height:20px;flex:0 0 20px;margin-top:2px;accent-color:#0b6b4d}.alo186-contextual-commerce__disclosure{margin:13px 0 5px;color:#344a62;font-size:.86rem;line-height:1.55}.alo186-contextual-commerce__status{min-height:1.35em;margin:0;color:#0b6b4d;font-size:.86rem;font-weight:750}.alo186-contextual-commerce a:focus-visible,.alo186-contextual-commerce input:focus-visible{outline:3px solid #f59e0b;outline-offset:3px}
@media(max-width:880px){.alo186-contextual-commerce__cards{grid-template-columns:1fr}.alo186-contextual-product{min-height:0}}@media(max-width:520px){.alo186-contextual-commerce{margin:22px 0;padding:16px;border-radius:16px}.alo186-contextual-product__actions a{width:100%}}@media(forced-colors:active){.alo186-contextual-commerce,.alo186-contextual-product,.alo186-contextual-gate{border:2px solid CanvasText;background:Canvas;color:CanvasText;box-shadow:none}.alo186-contextual-product__store{border:2px solid LinkText;background:Canvas;color:LinkText}}
"""

JS = rf"""/* ALO186 contextual affiliate growth v177 */
(function(){{
  'use strict';
  var TAG = '{TAG}';
  var SELECTOR = '[{MARKER}]';
  function event(name, params){{
    try {{
      if (window.alo186Analytics && typeof window.alo186Analytics.track === 'function') {{
        window.alo186Analytics.track(name, params || {{}});
      }}
    }} catch (_) {{}}
  }}
  function storeUrl(query){{ return 'https://www.amazon.com.tr/s?k=' + encodeURIComponent(query) + '&tag=' + encodeURIComponent(TAG); }}
  function init(section){{
    if (section.dataset.alo186ContextualReady === 'true') return;
    section.dataset.alo186ContextualReady = 'true';
    var checks = Array.prototype.slice.call(section.querySelectorAll('[data-affiliate-gate]'));
    var links = Array.prototype.slice.call(section.querySelectorAll('[data-affiliate-query]'));
    var status = section.querySelector('[data-affiliate-status]');
    var opened = false;
    function sync(){{
      var allowed = checks.length === 3 && checks.every(function(input){{ return input.checked; }});
      links.forEach(function(link){{
        if (allowed) {{ link.href=storeUrl(link.dataset.affiliateQuery||'');link.target='_blank';link.rel='sponsored nofollow noopener';link.removeAttribute('aria-disabled');link.removeAttribute('tabindex'); }}
        else {{ link.href='#';link.removeAttribute('target');link.rel='';link.setAttribute('aria-disabled','true');link.setAttribute('tabindex','-1'); }}
      }});
      if (status) status.textContent=allowed?'Teknik ve ticari kontroller tamamlandı; ürün seçenekleri açıldı.':'Ürün bağlantıları üç kontrol tamamlanana kadar kapalıdır.';
      if (allowed&&!opened) {{ opened=true;event('affiliate_gate_open',{{destination_type:'amazon',route_group:(location.pathname.split('/').filter(Boolean)[0]||'home'),action_type:'three_gate',content_group:'contextual_v177'}}); }}
    }}
    checks.forEach(function(input){{input.addEventListener('change',sync);}});
    links.forEach(function(link){{link.addEventListener('click',function(e){{if(link.getAttribute('aria-disabled')==='true'){{e.preventDefault();return;}}event('affiliate_product_select',{{destination_type:'amazon',route_group:(location.pathname.split('/').filter(Boolean)[0]||'home'),action_type:'product_select',content_group:(link.dataset.productClass||'contextual_v177')}});}});}});
    sync();
    if ('IntersectionObserver' in window) {{ var observer=new IntersectionObserver(function(entries){{if(entries.some(function(item){{return item.isIntersecting;}})){{event('affiliate_context_view',{{destination_type:'amazon',route_group:(location.pathname.split('/').filter(Boolean)[0]||'home'),action_type:'module_view',content_group:'contextual_v177'}});observer.disconnect();}}}},{{threshold:0.25}});observer.observe(section); }}
    else event('affiliate_context_view',{{destination_type:'amazon',route_group:(location.pathname.split('/').filter(Boolean)[0]||'home'),action_type:'module_view',content_group:'contextual_v177'}});
  }}
  function boot(){{Array.prototype.forEach.call(document.querySelectorAll(SELECTOR),init);}}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{{once:true}});else boot();
}})();
"""


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def closing_index(html_text: str, closing: str) -> int:
    index = html_text.rfind(closing)
    if index >= 0:
        return index
    matches = list(re.finditer(re.escape(closing), html_text, re.IGNORECASE))
    return matches[-1].start() if matches else -1


def inject_asset(html_text: str, tag: str, closing: str) -> str:
    if tag in html_text:
        return html_text
    index = closing_index(html_text, closing)
    if index < 0:
        raise RuntimeError(f"HTML kapanış etiketi eksik: {closing}")
    return html_text[:index] + tag + "\n" + html_text[index:]


def section_html(route: str, product_keys: tuple[str, str, str], base_path: str) -> str:
    slug = hashlib.sha1(route.encode("utf-8")).hexdigest()[:10]
    cards: list[str] = []
    for key in product_keys:
        item = PRODUCTS[key]
        cards.append(f'''<article class="alo186-contextual-product" data-product-class="{html.escape(key)}"><span class="alo186-contextual-product__label">İlgili ürün sınıfı</span><h3>{html.escape(item["title"])}</h3><p><strong>Ne zaman anlamlı?</strong> {html.escape(item["useWhen"])}</p><p><strong>Satın almayın:</strong> {html.escape(item["skipWhen"])}</p><div class="alo186-contextual-product__actions"><a class="alo186-contextual-product__guide" href="{html.escape(public_url(base_path, item["guide"]))}">Önce teknik ürün rehberini aç</a><a class="alo186-contextual-product__store" href="#" aria-disabled="true" tabindex="-1" data-affiliate-query="{html.escape(item["query"])}" data-product-class="{html.escape(key)}">Amazon Türkiye seçeneklerini aç</a></div></article>''')
    return f'''<section class="alo186-contextual-commerce" {MARKER}="true" data-affiliate-route="/{html.escape(route.removesuffix('index.html'))}" aria-labelledby="affiliate-context-title-{slug}"><div class="alo186-contextual-commerce__head"><span class="alo186-contextual-commerce__eyebrow">Sonuca bağlı ürün seçenekleri</span><h2 id="affiliate-context-title-{slug}">Bu rehberde doğrulanan ihtiyaca göre ürün sınıfları</h2><p class="alo186-contextual-commerce__intro">Önce mevcut ekipmanı test edin. Yalnız gerçek bir açık kaldıysa teknik rehberi inceleyin; mağaza bağlantısı üç onaydan sonra açılır. ALO186 fiyat, stok, puan, satıcı, teslimat veya garanti bilgisi yayımlamaz.</p></div><div class="alo186-contextual-commerce__cards">{''.join(cards)}</div><fieldset class="alo186-contextual-gate"><legend>Mağaza seçeneklerini açmadan önce</legend><label><input type="checkbox" data-affiliate-gate="need"><span>Mevcut güvenli ürünüm bu rehberde belirlenen ihtiyacı karşılamıyor.</span></label><label><input type="checkbox" data-affiliate-gate="fit"><span>Voltaj, güç, kapasite, bağlantı ve kullanım ortamı uygunluğunu kontrol ettim.</span></label><label><input type="checkbox" data-affiliate-gate="disclosure"><span>Bağlantının satış ortaklığı bağlantısı olduğunu ve güncel bilgileri Amazon Türkiye'de doğrulamam gerektiğini anladım.</span></label></fieldset><p class="alo186-contextual-commerce__disclosure"><strong>Şeffaflık:</strong> {DISCLOSURE} Mevcut ürün yeterliyse satın almama seçeneği önceliklidir.</p><p class="alo186-contextual-commerce__status" data-affiliate-status role="status" aria-live="polite">Ürün bağlantıları üç kontrol tamamlanana kadar kapalıdır.</p></section>'''


def has_existing_commerce(html_text: str) -> bool:
    folded = html_text.casefold()
    return any(marker.casefold() in folded for marker in EXISTING_COMMERCE_MARKERS)


def write_assets(site: Path) -> None:
    css = site / CSS_FILE
    js = site / JS_FILE
    css.parent.mkdir(parents=True, exist_ok=True)
    js.parent.mkdir(parents=True, exist_ok=True)
    css.write_text(CSS, encoding="utf-8")
    js.write_text(JS, encoding="utf-8")


def update_release(path: Path, base_path: str, report: dict[str, object]) -> None:
    if not path.is_file():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["contextualAffiliateGrowth"] = {
        "version": VERSION,
        "basePath": base_path,
        "targetRouteCount": len(PLACEMENTS),
        "injectedRouteCount": report["injectedRouteCount"],
        "alreadyInjectedRouteCount": report["alreadyInjectedRouteCount"],
        "missingRouteCount": report["missingRouteCount"],
        "skippedExistingCommerceRouteCount": report["skippedExistingCommerceRouteCount"],
        "placementCount": report["placementCount"],
        "productClassCount": report["productClassCount"],
        "gateCount": 3,
        "affiliateTag": TAG,
        "directStoreUrlsInHtml": 0,
        "highRiskDirectLinks": 0,
        "priceStockRatingClaims": False,
        "productImagesAdded": False,
        "personalDataCollectionAdded": False,
        "existingProductFirst": True,
        "events": ["affiliate_context_view", "affiliate_gate_open", "affiliate_product_select", "affiliate_click"],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def audit(site: Path, base_path: str = "") -> dict[str, object]:
    base_path = normalize_base_path(base_path)
    failures: list[str] = []
    modules = 0
    cards = 0
    product_classes: set[str] = set()
    for route, keys in PLACEMENTS.items():
        path = site / route
        if not path.is_file():
            failures.append(f"Hedef rota eksik: {route}")
            continue
        text = path.read_text(encoding="utf-8")
        if MARKER not in text:
            failures.append(f"Bağlamsal ürün modülü eksik: {route}")
            continue
        modules += text.count(MARKER)
        if text.count(MARKER) != 1:
            failures.append(f"Bağlamsal ürün modülü yinelenmiş: {route}")
        if text.count('data-affiliate-gate=') != 3:
            failures.append(f"Üçlü güven kapısı eksik: {route}")
        card_count = text.count('class="alo186-contextual-product"')
        cards += card_count
        if card_count != len(keys):
            failures.append(f"Ürün kartı sayısı yanlış: {route} -> {card_count}")
        if DISCLOSURE not in text:
            failures.append(f"Amazon açıklaması eksik: {route}")
        if re.search(r'<a\b[^>]*href=["\']https?://(?:www\.)?amazon\.com\.tr', text, re.IGNORECASE):
            failures.append(f"HTML içinde kapısız mağaza bağlantısı var: {route}")
        for malformed in ("</main<section", "</body<script", "</head<link"):
            if malformed in text.casefold():
                failures.append(f"HTML kapanış etiketi bozuldu: {route} -> {malformed}")
        if public_url(base_path, "/" + CSS_FILE) not in text:
            failures.append(f"CSS bağlantısı eksik: {route}")
        if public_url(base_path, "/" + JS_FILE) not in text:
            failures.append(f"JS bağlantısı eksik: {route}")
        for key in keys:
            product_classes.add(key)
            if f'data-product-class="{key}"' not in text:
                failures.append(f"Ürün sınıfı eksik: {route} -> {key}")
    css = site / CSS_FILE
    js = site / JS_FILE
    if not css.is_file() or not js.is_file():
        failures.append("Bağlamsal ürün CSS/JS dosyaları eksik")
    else:
        css_text = css.read_text(encoding="utf-8")
        js_text = js.read_text(encoding="utf-8")
        for token in ("min-height:44px", "focus-visible", "@media(max-width:520px)"):
            if token not in css_text:
                failures.append(f"Mobil/erişilebilirlik CSS sözleşmesi eksik: {token}")
        for token in (TAG, "affiliate_context_view", "affiliate_gate_open", "affiliate_product_select", "encodeURIComponent", "sponsored nofollow noopener"):
            if token not in js_text:
                failures.append(f"Affiliate JS sözleşmesi eksik: {token}")
        for forbidden in ("localStorage", "sessionStorage", "document.cookie"):
            if forbidden in js_text:
                failures.append(f"Kişisel iz bırakabilecek depolama kullanımı: {forbidden}")
    if failures:
        raise RuntimeError("ALO186 bağlamsal affiliate v177 denetimi başarısız:\n- " + "\n- ".join(failures[:100]))
    return {"ok": True, "targetRouteCount": len(PLACEMENTS), "moduleCount": modules, "placementCount": cards, "productClassCount": len(product_classes), "gateCount": 3, "directStoreUrlsInHtml": 0, "highRiskDirectLinks": 0, "personalDataCollectionAdded": False, "productImagesAdded": False}


def run(site: Path, base_path: str = "") -> dict[str, object]:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    if not site.is_dir():
        raise FileNotFoundError(f"Yayın artifactı bulunamadı: {site}")
    write_assets(site)
    injected = already = missing = skipped = 0
    for route, keys in PLACEMENTS.items():
        path = site / route
        if not path.is_file():
            missing += 1
            continue
        source = path.read_text(encoding="utf-8")
        if MARKER in source:
            already += 1
            continue
        if has_existing_commerce(source):
            skipped += 1
            continue
        css_tag = f'<link rel="stylesheet" href="{html.escape(public_url(base_path, "/" + CSS_FILE))}" data-alo186-contextual-affiliate-css-v177="true">'
        js_tag = f'<script defer src="{html.escape(public_url(base_path, "/" + JS_FILE))}" data-alo186-contextual-affiliate-js-v177="true"></script>'
        updated = inject_asset(source, css_tag, "</head>")
        main_end = closing_index(updated, "</main>")
        if main_end < 0:
            raise RuntimeError(f"Hedef rotada </main> yok: {route}")
        updated = updated[:main_end] + section_html(route, keys, base_path) + "\n" + updated[main_end:]
        updated = inject_asset(updated, js_tag, "</body>")
        path.write_text(updated, encoding="utf-8")
        injected += 1
    report: dict[str, object] = {"version": VERSION, "basePath": base_path, "injectedRouteCount": injected, "alreadyInjectedRouteCount": already, "missingRouteCount": missing, "skippedExistingCommerceRouteCount": skipped, "placementCount": (injected + already) * 3, "productClassCount": len({key for keys in PLACEMENTS.values() for key in keys})}
    update_release(site / "alo186-release.json", base_path, report)
    update_release(site / "pages-release.json", base_path, report)
    if missing or skipped:
        raise RuntimeError(f"ALO186 bağlamsal affiliate v177 hedefleri eksik/çakışmalı: missing={missing}, skipped={skipped}")
    report.update(audit(site, base_path))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 yüksek niyetli rehberlerine üç kapılı bağlamsal ürün sınıfları ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
