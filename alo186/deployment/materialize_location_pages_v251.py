from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus
from xml.sax.saxutils import escape as xml_escape

VERSION = 251
ORIGIN = "https://alo186.com"
CATALOG = Path("alo186/turkiye-arama/companies.js")
PROVINCE_ROOT = Path("il")
COMPANY_ROOT = Path("dagitim-sirketleri")
MARKER = 'data-alo186-location-page-v251="true"'


@dataclass(frozen=True)
class Company:
    identifier: str
    name: str
    slug: str
    province_ids: tuple[int, ...]
    district_mode: str | None = None


def _normalize_slug(value: str) -> str:
    table = str.maketrans(
        {
            "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g", "ı": "i", "İ": "i",
            "ö": "o", "Ö": "o", "ş": "s", "Ş": "s", "ü": "u", "Ü": "u",
        }
    )
    value = value.translate(table).casefold()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    if not value:
        raise ValueError("Boş il/şirket slugı üretilemez")
    return value


def _catalog(repo_root: Path) -> tuple[dict[int, str], list[Company]]:
    path = Path(repo_root) / CATALOG
    if not path.is_file():
        raise FileNotFoundError(f"Türkiye EDAŞ kataloğu bulunamadı: {path}")
    source = path.read_text(encoding="utf-8", errors="strict")
    province_block = re.search(r"const\s+provinceNames\s*=\s*\{(.*?)\};", source, re.S)
    company_block = re.search(
        r"const\s+companies\s*=\s*\[(.*?)\];\s*\n\s*const\s+istanbulEurope",
        source,
        re.S,
    )
    if not province_block or not company_block:
        raise RuntimeError("companies.js il/EDAŞ kataloğu parse edilemedi")

    provinces = {
        int(identifier): name
        for identifier, name in re.findall(r"(\d+)\s*:\s*'([^']+)'", province_block.group(1))
    }
    pattern = re.compile(
        r"\{id:'([^']+)',code:'[^']+',name:'([^']+)',slug:'([^']+)',"
        r"provinceIds:\[([^\]]+)\](?:,districtMode:'([^']+)')?,aliases:\[[^\]]*\]\}"
    )
    companies = [
        Company(
            identifier=match.group(1),
            name=match.group(2),
            slug=match.group(3),
            province_ids=tuple(int(item.strip()) for item in match.group(4).split(",")),
            district_mode=match.group(5) or None,
        )
        for match in pattern.finditer(company_block.group(1))
    ]
    if len(provinces) != 81:
        raise RuntimeError(f"İl kataloğu 81 kayıt olmalı; bulunan={len(provinces)}")
    if len(companies) != 21:
        raise RuntimeError(f"EDAŞ kataloğu 21 kayıt olmalı; bulunan={len(companies)}")
    covered = {province_id for company in companies for province_id in company.province_ids}
    missing = sorted(set(provinces) - covered)
    if missing:
        raise RuntimeError("EDAŞ kapsamı eksik il kimlikleri: " + ", ".join(map(str, missing)))
    return provinces, companies


def _company_phrase(companies: list[Company]) -> str:
    names = [company.name for company in companies]
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} ve {names[1]}"
    return ", ".join(names[:-1]) + f" ve {names[-1]}"


def _shell(*, title: str, description: str, canonical: str, body: str) -> str:
    return f'''<!doctype html>
<html lang="tr-TR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="theme-color" content="#071631">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description, quote=True)}">
<link rel="canonical" href="{html.escape(canonical, quote=True)}">
<style>
:root{{--navy:#071631;--ink:#172238;--muted:#526178;--line:#dce5f0;--blue:#174bb9;--focus:#ffbf47}}
*{{box-sizing:border-box}}body{{margin:0;font:17px/1.65 system-ui,-apple-system,Segoe UI,sans-serif;color:var(--ink);background:#f7f9fc}}
a{{color:var(--blue)}}a:focus-visible{{outline:4px solid var(--focus);outline-offset:4px}}
header,footer{{background:var(--navy);color:#fff}}header a,footer a{{color:#fff}}
.wrap{{width:min(960px,calc(100% - 32px));margin:auto}}header .wrap,footer .wrap{{padding:18px 0}}
main{{padding:38px 0 64px}}h1{{font-size:clamp(2rem,6vw,4.3rem);line-height:1.04;letter-spacing:-.045em;color:var(--navy)}}
h2{{color:var(--navy);margin-top:2rem}}.eyebrow{{font-weight:900;color:#3153a4;text-transform:uppercase;letter-spacing:.06em;font-size:.78rem}}
.answer,.panel,.alert{{background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px;margin:18px 0}}
.answer{{border-left:6px solid #2b79d6}}.alert{{background:#fff4f4;border-color:#e9aab1}}
.actions{{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}}.button{{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:10px 16px;border-radius:12px;background:var(--blue);color:#fff;text-decoration:none;font-weight:850}}
.button.secondary{{background:#fff;color:var(--blue);border:2px solid var(--blue)}}
.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}.grid a{{min-height:48px;display:flex;align-items:center}}
.fine{{color:var(--muted);font-size:.94rem}}ul,ol{{padding-left:1.35rem}}li{{margin:.55rem 0}}
@media(max-width:680px){{.grid{{grid-template-columns:1fr}}.actions{{display:grid}}.button{{width:100%}}}}
</style>
</head>
<body {MARKER}>
<header><div class="wrap"><a href="/" aria-label="ALO186 ana sayfa"><strong>ALO186</strong></a> · bağımsız elektrik bilgi ağı</div></header>
<main><div class="wrap">{body}</div></main>
<footer><div class="wrap"><p><strong>ALO186 bağımsız bilgilendirme platformudur.</strong> EDAŞ veya kamu kurumu değildir; arıza kaydı almaz ve açık adres, T.C. kimlik numarası ya da tesisat numarası istemez.</p><p><a href="/yayin-ilkeleri">Yayın ilkeleri</a> · <a href="/kaynaklar">Kaynaklar</a> · <a href="/iletisim">Hatalı bilgi bildir</a></p></div></footer>
</body>
</html>'''


def _city_page(city: str, companies: list[Company]) -> str:
    slug = _normalize_slug(city)
    canonical = f"{ORIGIN}/il/{slug}"
    company_phrase = _company_phrase(companies)
    if len(companies) == 2 and any(company.district_mode for company in companies):
        direct = (
            f"{city} için yetkili dağıtım şirketi bulunduğunuz yakaya göre {company_phrase}. "
            "Şebeke kesintisi veya dağıtım arızası için 186 aranır; ilçe/yaka seçimi resmî kesinti ekranı açılmadan önce doğrulanır."
        )
        detail = (
            "İstanbul Avrupa Yakası BEDAŞ, Anadolu Yakası AYEDAŞ hizmet bölgesindedir. "
            "İlçe seçmeden tek şirket adı vermek doğru değildir."
        )
    else:
        direct = (
            f"{city} için yetkili dağıtım şirketi {company_phrase}. Şebeke kesintisi veya "
            "dağıtım arızası için 186 aranır; planlı kesinti bilgisi yetkili şirketin resmî kanalından doğrulanır."
        )
        detail = (
            f"{city} elektrik dağıtım hizmetinden {company_phrase} sorumludur. ALO186 kesinti süresi tahmini "
            "üretmez ve ihbar kaydı almaz; doğru resmî kanala yönlendirir."
        )
    company_links = "".join(
        f'<li><a href="/dagitim-sirketleri/{html.escape(company.slug, quote=True)}">{html.escape(company.name)} iletişim ve hizmet bölgesi rehberi</a></li>'
        for company in companies
    )
    query = quote_plus(city)
    body = f'''
<p class="eyebrow">{html.escape(city)} · elektrik kesintisi ve doğru kanal</p>
<h1>{html.escape(city)} elektrik kesintisi, 186 ve yetkili dağıtım şirketi</h1>
<section class="answer" aria-labelledby="dogrudan-yanit"><h2 id="dogrudan-yanit">Doğrudan cevap</h2><p><strong>{html.escape(direct)}</strong></p></section>
<div class="actions"><a class="button" href="tel:186">186’yı ara</a><a class="button secondary" href="/elektrik-kesintisi?q={query}">Resmî kesinti kanalını bul</a></div>
<section class="alert"><h2>Aktif tehlike varsa</h2><p>Elektrik çarpması, yangın, duman, kıvılcım veya kopmuş iletken varsa yaklaşmayın; güvenli uzaklığa geçip <a href="tel:112"><strong>112’yi arayın</strong></a>. Ürün veya kesinti sorgulamasına ilerlemeyin.</p></section>
<section class="panel"><h2>{html.escape(city)} bölgesinde hangi kanal kullanılır?</h2><p>{html.escape(detail)}</p><ol><li>Çevrede de elektrik yoksa 186 ve yetkili dağıtım şirketinin resmî kesinti ekranını kullanın.</li><li>Yalnız daire veya binada sorun varsa pano kapağını açmadan bina yönetimi ya da yetkili elektrikçiye ilerleyin.</li><li>Can güvenliği riski varsa 112 önceliklidir.</li></ol></section>
<section class="panel"><h2>Yetkili dağıtım şirketi rehberi</h2><ul>{company_links}</ul></section>
<section class="panel"><h2>Sık sorulan soru</h2><h3>{html.escape(city)} bölgesinde elektrik kesintisi için nere aranır?</h3><p>{html.escape(direct)}</p></section>
<p class="fine">Şirketin telefon, WhatsApp, kesinti ekranı ve hizmet bağlantıları değişebilir. İşlem öncesinde resmî şirket ekranındaki güncel bilgiyi yeniden doğrulayın.</p>'''
    return _shell(
        title=f"{city} Elektrik Kesintisi, 186 ve Yetkili EDAŞ | ALO186",
        description=f"{city} elektrik kesintisinde 186, 112 ve yetkili dağıtım şirketi ayrımını görün; resmî kesinti kanalına kişisel veri paylaşmadan ilerleyin.",
        canonical=canonical,
        body=body,
    )


def _company_page(company: Company, provinces: dict[int, str]) -> str:
    canonical = f"{ORIGIN}/dagitim-sirketleri/{company.slug}"
    areas = [provinces[province_id] for province_id in company.province_ids]
    area_text = ", ".join(areas)
    area_links = "".join(
        f'<li><a href="/il/{_normalize_slug(city)}">{html.escape(city)} elektrik kesintisi ve 186 rehberi</a></li>'
        for city in areas
    )
    special = ""
    if company.district_mode == "istanbul_europe":
        special = " Bu şirket İstanbul Avrupa Yakası ilçelerinde yetkilidir; Anadolu Yakası için AYEDAŞ kullanılır."
    elif company.district_mode == "istanbul_asia":
        special = " Bu şirket İstanbul Anadolu Yakası ilçelerinde yetkilidir; Avrupa Yakası için BEDAŞ kullanılır."
    body = f'''
<p class="eyebrow">Dağıtım şirketi hizmet rehberi</p>
<h1>{html.escape(company.name)} arıza telefonu, kesinti kanalı ve hizmet bölgesi</h1>
<section class="answer"><h2>Doğrudan cevap</h2><p><strong>{html.escape(company.name)} hizmet bölgesindeki şebeke kesintisi ve dağıtım arızaları için 186 aranır. Planlı kesinti, sayaç ve şebeke işlemleri şirketin resmî kanalından doğrulanır.</strong></p></section>
<div class="actions"><a class="button" href="tel:186">186’yı ara</a><a class="button secondary" href="/elektrik-kesintisi?q={quote_plus(company.name)}">Resmî kesinti kanalını bul</a></div>
<section class="alert"><h2>Aktif tehlike varsa</h2><p>Elektrik çarpması, yangın, duman, kıvılcım veya kopmuş iletken varsa yaklaşmayın; güvenli uzaklığa geçip <a href="tel:112"><strong>112’yi arayın</strong></a>.</p></section>
<section class="panel"><h2>Hizmet bölgesi</h2><p>{html.escape(area_text)}{html.escape(special)}</p><div class="grid"><ul>{area_links}</ul></div></section>
<section class="panel"><h2>Resmî işlem sırası</h2><ol><li>Aktif tehlikede 112’yi arayın.</li><li>Şebeke kesintisi veya dağıtım arızasında 186’yı kullanın.</li><li>Planlı kesinti ve şirket işlemlerini resmî şirket ekranından doğrulayın.</li><li>Yalnız iç tesisatı etkileyen sorunda yetkili elektrikçiye ilerleyin.</li></ol></section>
<section class="panel"><h2>{html.escape(company.name)} hangi illerde hizmet verir?</h2><p>{html.escape(company.name)}, {html.escape(area_text)} bölgesinde elektrik dağıtım hizmeti yürütür.{html.escape(special)}</p></section>
<p class="fine">ALO186, {html.escape(company.name)} adına kayıt veya ihbar almaz. Güncel telefon, kesinti ekranı ve işlem koşulları şirketin resmî kanalında doğrulanmalıdır.</p>'''
    return _shell(
        title=f"{company.name} 186, Kesinti ve Hizmet Bölgesi | ALO186",
        description=f"{company.name} için 186 arıza hattı, 112 güvenlik ayrımı, hizmet verdiği iller ve resmî kesinti kanalına yönlendirme.",
        canonical=canonical,
        body=body,
    )


def _write_page(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        existing = path.read_text(encoding="utf-8", errors="strict")
        if MARKER not in existing:
            return "preserved"
        if existing == content:
            return "unchanged"
    path.write_text(content, encoding="utf-8")
    return "written"


def _update_sitemap(site: Path, urls: list[str]) -> dict[str, int]:
    path = Path(site) / "sitemap.xml"
    if not path.is_file():
        raise FileNotFoundError(f"Ana sitemap bulunamadı: {path}")
    source = path.read_text(encoding="utf-8", errors="strict")
    if "</urlset>" not in source:
        raise RuntimeError("sitemap.xml geçerli urlset kapanışı taşımıyor")
    existing = set(re.findall(r"<loc>(.*?)</loc>", source, re.S))
    missing = [url for url in urls if url not in existing]
    if missing:
        entries = "".join(f"  <url><loc>{xml_escape(url)}</loc></url>\n" for url in missing)
        source = source.replace("</urlset>", entries + "</urlset>", 1)
        path.write_text(source, encoding="utf-8")
    return {"existing": len(urls) - len(missing), "added": len(missing)}


def materialize(repo_root: Path, site: Path) -> dict[str, object]:
    repo_root, site = Path(repo_root), Path(site)
    provinces, companies = _catalog(repo_root)
    companies_by_province = {
        province_id: [company for company in companies if province_id in company.province_ids]
        for province_id in provinces
    }
    city_states = {"written": 0, "preserved": 0, "unchanged": 0}
    company_states = {"written": 0, "preserved": 0, "unchanged": 0}
    urls: list[str] = []

    for province_id, city in sorted(provinces.items()):
        slug = _normalize_slug(city)
        target = site / PROVINCE_ROOT / slug / "index.html"
        state = _write_page(target, _city_page(city, companies_by_province[province_id]))
        city_states[state] += 1
        urls.append(f"{ORIGIN}/il/{slug}")

    for company in companies:
        target = site / COMPANY_ROOT / company.slug / "index.html"
        state = _write_page(target, _company_page(company, provinces))
        company_states[state] += 1
        urls.append(f"{ORIGIN}/dagitim-sirketleri/{company.slug}")

    sitemap = _update_sitemap(site, urls)
    return {
        "version": VERSION,
        "provincePages": len(provinces),
        "companyPages": len(companies),
        "provincePageStates": city_states,
        "companyPageStates": company_states,
        "sitemap": sitemap,
        "canonicalOrigin": ORIGIN,
        "staticHtml": True,
        "javascriptRequired": False,
        "personalDataRequested": False,
        "privateCompaniesPresentedAsGovernment": False,
    }
