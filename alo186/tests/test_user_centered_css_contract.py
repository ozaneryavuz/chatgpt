from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "styles.css"


def test_portal_css_has_user_centered_quality_contract() -> None:
    css = CSS.read_text(encoding="utf-8")
    required = (
        "text-wrap:balance",
        "min-width:0",
        "min-height:44px",
        "max-width:72ch",
        "content-visibility:auto",
        "contain-intrinsic-size:1px 280px",
        "@media(max-width:720px)",
        "overflow-wrap:anywhere",
        "prefers-reduced-motion:reduce",
    )
    missing = [token for token in required if token not in css]
    assert not missing, f"Kullanıcı odaklı CSS sözleşmesi eksik: {missing}"


def test_quality_contract_does_not_hide_overflow_or_focus() -> None:
    css = CSS.read_text(encoding="utf-8")
    forbidden = (
        "body{overflow-x:hidden",
        "outline:none",
        "outline:0",
    )
    leaked = [token for token in forbidden if token in css]
    assert not leaked, f"Hata veya odağı gizleyen CSS yayınlanamaz: {leaked}"
