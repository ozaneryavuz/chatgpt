from __future__ import annotations

import sys
import tempfile
from pathlib import Path

DEPLOYMENT = Path(__file__).resolve().parents[1] / "deployment"
sys.path.insert(0, str(DEPLOYMENT))

import inject_intent_tools_run135 as intent  # noqa: E402


VALID_FORM = """<!doctype html><html><body>
<input id="hours" type="number" min="0" max="8760">
<script>
const input=document.getElementById('hours');
const rawHours=input.value.trim();
const hours=rawHours===''?Number.NaN:Number(rawHours);
const valid = rawHours !== '' && Number.isFinite(hours) && hours >= 0 && hours <= 8760;
</script><p>30 gün</p></body></html>"""

LEGACY_FORM = """<!doctype html><html><body>
<input id="hours" type="number" min="0">
<script>
const input=document.getElementById('hours');
    const hours=Number(input.value);
if(!Number.isFinite(hours)||hours<0||hours>8760){throw new Error('invalid');}
</script><p>30 gün</p></body></html>"""

UNSAFE_FORM = """<!doctype html><html><body>
<input id="hours" type="number" min="0" max="8760">
<script>
const input=document.getElementById('hours');
const rawHours=input.value.trim();
const hours=rawHours===''?Number.NaN:Number(rawHours);
const valid=Number.isFinite(hours);
</script><p>30 gün</p></body></html>"""


def write_page(root: Path, html: str) -> Path:
    page = root / intent.ROUTES[0].strip("/") / "index.html"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(html, encoding="utf-8")
    return page


def valid_form_is_already_hardened() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        page = write_page(root, VALID_FORM)
        before = page.read_text(encoding="utf-8")
        assert intent.harden_outage_input(root) is False
        assert page.read_text(encoding="utf-8") == before
        assert intent.has_fail_closed_outage_bounds(before)


def legacy_form_is_hardened_once() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        page = write_page(root, LEGACY_FORM)
        assert intent.harden_outage_input(root) is True
        hardened = page.read_text(encoding="utf-8")
        assert 'max="8760"' in hardened
        assert "const rawHours=input.value.trim();" in hardened
        assert "rawHours===''?Number.NaN:Number(rawHours)" in hardened
        assert intent.OUTAGE_INVALID_CONDITION in intent.normalize_javascript(hardened)
        assert intent.harden_outage_input(root) is False
        assert page.read_text(encoding="utf-8") == hardened


def unsafe_form_is_rejected() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        write_page(root, UNSAFE_FORM)
        try:
            intent.harden_outage_input(root)
        except RuntimeError as exc:
            assert "doğrulama kalıbı" in str(exc)
        else:
            raise AssertionError("Gerçek 0–8760 fail-closed sınırı olmayan sayfa reddedilmeliydi")


if __name__ == "__main__":
    valid_form_is_already_hardened()
    legacy_form_is_hardened_once()
    unsafe_form_is_rejected()
    print("run135 outage duration idempotency: PASS")
