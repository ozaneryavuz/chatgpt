from __future__ import annotations

from affiliate_decision_funnel_v215_config import MARKER, TIER_COPY, Target, public_url


def mini_controls() -> str:
    return '''<div class="adf-mini" data-decision-mini-controls role="group" aria-label="Mini UPS teknik sınıfı">
<label>Adaptör gerilimi tam okunuyor mu?<select name="voltage"><option value="">Seçin</option><option value="known">Evet</option><option value="unknown">Hayır / emin değilim</option></select></label>
<label>Jak ölçüsü ve polarite doğrulandı mı?<select name="connector"><option value="">Seçin</option><option value="known">Evet</option><option value="unknown">Hayır / emin değilim</option></select></label>
<label>Beslenecek cihaz zinciri<select name="devices"><option value="one">Tek modem/ONT</option><option value="two">Modem + ONT</option><option value="multi">Modem + ONT + router/switch</option></select></label>
<label>Hedef süre<select name="duration"><option value="short">2 saate kadar</option><option value="medium">2–6 saat</option><option value="long">6 saatten uzun</option></select></label>
<button type="button" data-decision-mini-submit>Teknik sınıfı belirle</button></div>'''


def tier_cards(target: Target, base: str) -> str:
    target_url = public_url(base, target.route)
    separator = "&amp;" if "?" in target_url else "?"
    return "".join(
        f'''<article class="adf-card" data-decision-tier-card="{tier}" data-decision-placement="decision_tier_card"><span>{index:02d} · Teknik sınıf</span><h3>{title}</h3><dl><div><dt>Kimler için?</dt><dd>{fit}</dd></div><div><dt>Uygun değil</dt><dd>{bad}</dd></div><div><dt>Önce kontrol et</dt><dd>{check}</dd></div></dl><a hidden data-decision-action="selector" data-decision-tier="{tier}" data-decision-placement="decision_result_cta" href="{target_url}{separator}tier={tier}">{target.label} →</a></article>'''
        for index, (tier, title, fit, bad, check) in enumerate(
            TIER_COPY[target.flow], 1
        )
    )


def funnel_section(target: Target, base: str) -> str:
    controls = (
        mini_controls()
        if target.controls
        else '<p class="adf-note">Yukarıdaki hesabı tamamlayın. Ham watt, Wh ve cihaz girdileri analitiğe gönderilmez.</p>'
    )
    professional_url = public_url(
        base, "/kurumsal-elektrik-surekliligi-on-degerlendirme"
    )
    return f'''<section class="affiliate-decision-funnel" {MARKER} data-decision-flow="{target.flow}" data-decision-placement="decision_intro">
<div class="adf-head"><div><span>Hesap → güvenlik kapısı → en fazla üç seçenek</span><h2>{target.title}</h2></div><p>{target.lead}</p></div>
<div class="adf-disclosure"><strong>Satış ortaklığı açıklaması:</strong> Sonraki teknik seçici satış ortaklığı bağlantıları içerebilir. ALO186 nitelikli satın alımlardan gelir elde edebilir; kullanıcıya ek maliyet yansımaz. Fiyat, stok, puan, satıcı ve garanti burada yayımlanmaz.</div>
{controls}
<div class="adf-status" data-decision-status aria-live="polite"><strong>Önce teknik sonucu oluşturun.</strong><span>Belirsiz veya yüksek riskli sonuçta ürün yolu açılmaz.</span></div>
<div class="adf-grid">{tier_cards(target, base)}</div>
<div class="adf-no-buy" data-decision-no-buy-panel hidden><strong>Satın alma gerekmiyor.</strong><span>Mevcut güvenli çözüm hedefi karşılıyorsa bakım ve tekrar test yeterlidir.</span></div>
<div class="adf-blocked" data-decision-blocked-panel hidden><strong>Ticari yol kapatıldı.</strong><span data-decision-blocked-copy>Eksik kanıt veya güvenlik sınırı nedeniyle ürün seçimine ilerlemeyin.</span></div>
<div class="adf-actions"><button type="button" data-decision-no-buy>Mevcut çözümüm testte yeterli — yeni ürün alma</button><a hidden data-decision-professional href="{professional_url}">Profesyonel ön değerlendirmeyi aç →</a></div>
</section>'''
