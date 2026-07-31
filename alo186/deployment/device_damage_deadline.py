from __future__ import annotations

import re
from pathlib import Path

# Binding rule: Elektrik Piyasasında Dağıtım ve Perakende Satış Faaliyetlerine
# İlişkin Kalite Yönetmeliği, Madde 26/1. The 23 October 2025 amendment changed
# paragraph 2 but did not replace the 30-calendar-day application period in
# paragraph 1.
REGULATION_URL = (
    "https://www.resmigazete.gov.tr/eskiler/2020/12/20201229M1-1.htm"
)
AMENDMENT_URL = "https://www.resmigazete.gov.tr/eskiler/2025/10/20251023-5.htm"
CURRENT_DEADLINE = "30 gün"

DAMAGE_TERMS = re.compile(r"\b(cihaz|teçhizat|techizat|hasar|zarar)\w*\b", re.IGNORECASE)
APPLICATION_TERMS = re.compile(
    r"\b(başvur|basvur|talep|tazmin|dağıtım şirket|dagitim sirket|edaş|edas)\w*",
    re.IGNORECASE,
)
STALE_DEADLINE = re.compile(
    r"\b(?:10\s*iş\s*gün|on\s*iş\s*gün)(?:ü|lük|de|den|içinde|icerisinde|içerisinde)?\b",
    re.IGNORECASE,
)
CURRENT_DEADLINE_PATTERN = re.compile(
    r"\b30\s*(?:takvim\s*)?gün(?:lük|ü|ün|de|den|içinde)?\b",
    re.IGNORECASE,
)
RESPONSE_TERMS = re.compile(
    r"\b(cevap|yanıt|bildir|haklı bulun|ret|redd|teknik rapor)\w*",
    re.IGNORECASE,
)
TEXT_SUFFIXES = {".html", ".htm", ".js", ".mjs", ".json", ".txt", ".xml"}

# Only publication routes known to carry the obsolete FAQ wording are migrated.
# Replacements are exact and idempotent: if source files are corrected later,
# already-current strings remain untouched.
REPLACEMENTS: dict[str, tuple[tuple[str, str], ...]] = {
    "elektrik-portali/index.html": (
        ("Cihaz hasarında başvuru süresi 10 iş günüdür", "Cihaz hasarında başvuru süresi 30 gündür"),
        (
            "zararın ortaya çıktığı tarihten itibaren <strong>10 iş günü içinde</strong>",
            "zararın ortaya çıktığı tarihten itibaren <strong>30 gün içinde</strong>",
        ),
        ("EDAŞ · cihaz hasarı · 10 iş günü", "EDAŞ · cihaz hasarı · 30 gün"),
    ),
    "mevzuat/index.html": (("Cihaz hasarı ve 10 iş günü", "Cihaz hasarı ve 30 gün"),),
    "hesaplama/cihaz-hasari-basvuru-takibi/index.html": (
        ("Cihaz Hasarı Başvuru Takibi ve 10 İş Günü Kontrolü", "Cihaz Hasarı Başvuru Takibi ve 30 Gün Kontrolü"),
        ("cihaz hasarı için 10 iş günlük başvuru süresini", "cihaz hasarı için 30 günlük başvuru süresini"),
        ("Cihaz hasarı için başvuru süresi kaç iş günüdür?", "Cihaz hasarı için başvuru süresi kaç gündür?"),
        ("zarar tarihinden itibaren 10 iş günü içinde", "zararın ortaya çıktığı tarihten itibaren 30 gün içinde"),
        (
            "Resmî tatiller ve somut olay için şirketin resmî kanalını doğrulayın.",
            "Somut olay için güncel mevzuatı ve şirketin resmî kanalını doğrulayın.",
        ),
        ("10 iş günü · kanıt dosyası · yerel takip", "30 gün · kanıt dosyası · yerel takip"),
        ("Araç yaklaşık iş günü kontrolü", "Araç yaklaşık takvim günü kontrolü"),
        ("Yaklaşık son iş günü", "Yaklaşık son gün"),
        ("Kalan hafta içi günü", "Kalan takvim günü"),
        ("hasar taleplerinde <strong>10 iş günü</strong> sınırını", "hasar taleplerinde <strong>30 gün</strong> sınırını"),
        ("<summary>10 iş günü geçtiyse araç ne yapar?</summary>", "<summary>30 gün geçtiyse araç ne yapar?</summary>"),
    ),
    "hesaplama/cihaz-hasari-basvuru-takibi/app.js": (
        (
            "function addBusinessDays(date,count){const d=new Date(date);let added=0;while(added<count){d.setDate(d.getDate()+1);const day=d.getDay();if(day!==0&&day!==6)added++;}return d}",
            "function addCalendarDays(date,count){const d=new Date(date);d.setDate(d.getDate()+count);return d}",
        ),
        (
            "function businessDaysUntil(from,to){const a=new Date(from);a.setHours(0,0,0,0);const b=new Date(to);b.setHours(0,0,0,0);let n=0,dir=a<=b?1:-1;while((dir===1&&a<b)||(dir===-1&&a>b)){a.setDate(a.getDate()+dir);if(a.getDay()!==0&&a.getDay()!==6)n+=dir;}return n}",
            "function calendarDaysUntil(from,to){const a=new Date(from);a.setHours(0,0,0,0);const b=new Date(to);b.setHours(0,0,0,0);return Math.round((b-a)/86400000)}",
        ),
        (
            "const deadline=addBusinessDays(event,10),remaining=businessDaysUntil(new Date(),deadline)",
            "const deadline=addCalendarDays(event,30),remaining=calendarDaysUntil(new Date(),deadline)",
        ),
        (
            "Bu yardımcı yalnız hafta sonlarını dışlar; resmî tatiller ve somut hukuki süre hesabı için resmî kanal veya uzman doğrulaması gerekir.",
            "Bu yardımcı 30 takvim gününü yaklaşık hesaplar; somut hukuki süre için güncel mevzuatı, resmî kanalı veya uzman görüşünü doğrulayın.",
        ),
        ("Yaklaşık hesapta son iş gününe çok az süre kaldı.", "Yaklaşık hesapta son güne çok az süre kaldı."),
        ("10 iş günlük özel süreyi kaçırmadan", "30 günlük süreyi kaçırmadan"),
        ("officialHolidaysExcluded:false,businessDayWindow:10", "calendarDayWindow:30"),
    ),
    "hesaplama/kesinti-gunlugu/index.html": (("zararın ortaya çıktığı tarihten itibaren 10 iş günü içinde", "zararın ortaya çıktığı tarihten itibaren 30 gün içinde"),),
    "hesaplama/kesinti-gunlugu/app.js": (("10 iş günlük süre açıklanır", "30 günlük süre düzenlenir"),),
    "hesaplama/kesinti-gunlugu/core.js": (("10 iş günlük süre açıklanır", "30 günlük süre düzenlenir"),),
    "hesaplama/elektrik-planim/growth-core.js": (("cihaz hasarında 10 iş günlük resmî süreyi", "cihaz hasarında 30 günlük resmî süreyi"),),
    "hesaplama/elektrik-planim/core.js": (("10 iş günlük resmî başvuru süresini", "30 günlük resmî başvuru süresini"),),
    "hesaplama/elektrik-cihaz-hasari-edas-basvuru-paketi/index.html": (
        ("cihaz hasarı için 10 iş günlük başvuru süresini", "cihaz hasarı için 30 günlük başvuru süresini"),
        ("zararın ortaya çıktığı tarihten itibaren 10 iş günü içinde", "zararın ortaya çıktığı tarihten itibaren 30 gün içinde"),
        ("10 iş günü · kanıt kontrolü · resmî başvuru", "30 gün · kanıt kontrolü · resmî başvuru"),
        (
            "Bu araçtaki iş günü hesabı hafta sonlarını dışlayan ön hesaplamadır; resmî tatiller ve somut olay için dağıtım şirketinin güncel süreci ayrıca doğrulanmalıdır.",
            "Bu araçtaki takvim günü hesabı yaklaşık bir ön kontroldür; somut olay için güncel mevzuatı ve dağıtım şirketinin resmî açıklamasını ayrıca doğrulayın.",
        ),
        ("<summary>On iş günü geçmişse araç ne yapar?</summary>", "<summary>30 gün geçmişse araç ne yapar?</summary>"),
    ),
    "hesaplama/elektrik-cihaz-hasari-edas-basvuru-paketi/app.js": (
        (
            "function addBusinessDays(date,count){const d=new Date(`${date}T12:00:00`);let added=0;while(added<count){d.setDate(d.getDate()+1);const day=d.getDay();if(day!==0&&day!==6)added++}return d}",
            "function addCalendarDays(date,count){const d=new Date(`${date}T12:00:00`);d.setDate(d.getDate()+count);return d}",
        ),
        (
            "function businessDaysElapsed(start,end=new Date()){const a=new Date(`${start}T12:00:00`),b=new Date(end);if(b<a)return 0;let n=0,d=new Date(a);while(d<b){d.setDate(d.getDate()+1);const day=d.getDay();if(day!==0&&day!==6&&d<=b)n++}return n}",
            "function calendarDaysElapsed(start,end=new Date()){const a=new Date(`${start}T12:00:00`),b=new Date(end);if(b<a)return 0;return Math.floor((b-a)/86400000)}",
        ),
        ("deadline=addBusinessDays(date,10),elapsed=businessDaysElapsed(date)", "deadline=addCalendarDays(date,30),elapsed=calendarDaysElapsed(date)"),
        ("Zararın ortaya çıktığı tarihten itibaren 10 iş günü dolmadan", "Zararın ortaya çıktığı tarihten itibaren 30 gün dolmadan"),
        ("businessDaysElapsed:elapsed,deadlineEstimateExcludesPublicHolidays:true", "calendarDaysElapsed:elapsed,calendarDayWindow:30"),
    ),
    "haberler/dusuk-yuksek-voltaj-edas-teknik-kalite-olcumu/index.html": (("Varsa cihaz hasarı için ayrı 10 iş günü başvuru kaydı", "Varsa cihaz hasarı için ayrı 30 günlük başvuru kaydı"),),
    "haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu/index.html": (
        ("10 iş günlük süreyi ve işlem adımlarını öğrenin.", "30 günlük süreyi ve işlem adımlarını öğrenin."),
        ("zararın ortaya çıktığı tarihten itibaren 10 iş günü içinde dağıtım şirketine talepte bulunulabilir.", "zararın ortaya çıktığı tarihten itibaren 30 gün içinde dağıtım şirketine talepte bulunulur."),
        ("zarar tarihinden itibaren 10 iş günü içinde bölgenizdeki dağıtım şirketine", "zararın ortaya çıktığı tarihten itibaren 30 gün içinde bölgenizdeki dağıtım şirketine"),
        ("Cihaz hasarı başvurusunda özel süre 10 iş günüdür", "Cihaz hasarı başvurusunda süre 30 gündür"),
        ("talebin zararın ortaya çıktığı tarihten itibaren <strong>10 iş günü</strong> içinde", "talebin zararın ortaya çıktığı tarihten itibaren <strong>30 gün</strong> içinde"),
        ("<summary>10 iş günü geçtiyse başvuru yapılamaz mı?</summary>", "<summary>30 gün geçtiyse başvuru yapılamaz mı?</summary>"),
        ("EPDK açıklaması hasar tazmini talebi için 10 iş günlük süre belirtir.", "Kalite Yönetmeliği Madde 26 hasar tazmini talebi için 30 günlük süre düzenler."),
        ("<a href=\"#sure\">10 iş günü</a>", "<a href=\"#sure\">30 gün</a>"),
    ),
    "haberler/planli-elektrik-kesintisi-ne-kadar-once-bildirilir/index.html": (("Cihaz hasarı için 10 iş günü başvuru rehberini aç", "Cihaz hasarı için 30 günlük başvuru rehberini aç"),),
    "haberler/elektrik-kesintisi-tazminati-edas-12-saat-yillik-kesinti/index.html": (
        ("zararın ortaya çıktığı tarihten itibaren 10 iş günlük başvuru süresi belirtilir.", "zararın ortaya çıktığı tarihten itibaren 30 günlük başvuru süresi düzenlenir."),
        ("Zararın ortaya çıktığı tarihten itibaren 10 iş günü içinde ayrı talep", "Zararın ortaya çıktığı tarihten itibaren 30 gün içinde ayrı talep"),
    ),
    "haberler/elektrik-gerilimi-dusuk-yuksek-edas-olcum-talebi/index.html": (("ayrı zarar tazmini sürecinin 10 iş günü sınırını", "ayrı zarar tazmini sürecinin 30 günlük sınırını"),),
    "haberler/elektrik-kesintisi-tazminati-otomatik-odeme-12-saat/index.html": (
        ("EPDK açıklamasındaki on iş günlük talep süresi", "Kalite Yönetmeliği Madde 26 kapsamındaki 30 günlük talep süresi"),
        ("<td>On iş günü içinde talep</td>", "<td>30 gün içinde talep</td>"),
        ("zararın ortaya çıktığı tarihten itibaren on iş günü içinde dağıtım şirketine talepte bulunulabilir.", "zararın ortaya çıktığı tarihten itibaren 30 gün içinde dağıtım şirketine talepte bulunulur."),
        ("On iş günlük ayrı başvuru süresini", "30 günlük ayrı başvuru süresini"),
    ),
}


def normalize_published_site(root: Path) -> list[str]:
    changed: list[str] = []
    missing: list[str] = []
    for relative, replacements in REPLACEMENTS.items():
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in replacements:
            if old in text:
                text = text.replace(old, new)
            elif new not in text:
                missing.append(f"{relative}: {old}")
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(relative)
    if missing:
        raise RuntimeError(
            "Cihaz hasarı süre normalizasyonunda beklenen kaynak kalıbı bulunamadı:\n- "
            + "\n- ".join(missing)
        )
    return changed


def _contexts(text: str, pattern: re.Pattern[str], radius: int = 320):
    normalized = re.sub(r"\s+", " ", text)
    for match in pattern.finditer(normalized):
        start = max(0, match.start() - radius)
        end = min(len(normalized), match.end() + radius)
        yield match, normalized[start:end]


def find_stale_application_deadlines(root: Path) -> list[str]:
    violations: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for match, context in _contexts(text, STALE_DEADLINE):
            if (
                DAMAGE_TERMS.search(context)
                and APPLICATION_TERMS.search(context)
                and not RESPONSE_TERMS.search(context)
            ):
                violations.append(
                    f"{path.relative_to(root)}:{match.start()} -> {context[:640]}"
                )
    return violations


def find_current_application_deadlines(root: Path) -> list[str]:
    locations: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for match, context in _contexts(text, CURRENT_DEADLINE_PATTERN):
            if DAMAGE_TERMS.search(context) and APPLICATION_TERMS.search(context):
                locations.append(f"{path.relative_to(root)}:{match.start()}")
    return locations


def validate_published_site(root: Path) -> dict[str, object]:
    stale = find_stale_application_deadlines(root)
    current = find_current_application_deadlines(root)
    if stale:
        raise RuntimeError(
            "Cihaz hasarı başvurusunda yürürlükteki 30 gün yerine eski 10 iş günü ifadesi bulundu:\n- "
            + "\n- ".join(stale)
        )
    if not current:
        raise RuntimeError("Cihaz hasarı başvurusunu 30 güne bağlayan yayın metni bulunamadı.")
    return {
        "deadline": CURRENT_DEADLINE,
        "regulationUrl": REGULATION_URL,
        "amendmentUrl": AMENDMENT_URL,
        "verifiedLocations": len(current),
    }
