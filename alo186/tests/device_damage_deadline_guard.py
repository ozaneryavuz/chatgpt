#!/usr/bin/env python3
"""Fail closed when the published ALO186 bundle uses an obsolete device-damage deadline."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from device_damage_deadline import (  # noqa: E402
    CURRENT_DEADLINE,
    CURRENT_DEADLINE_PATTERN,
    STALE_DEADLINE,
    find_current_application_deadlines,
    find_stale_application_deadlines,
)


def self_test() -> None:
    stale = "Cihaz hasarı için zararın doğduğu tarihten itibaren 10 iş günü içinde EDAŞ'a başvurun."
    current = "Cihaz hasarı için zararın ortaya çıktığı tarihten itibaren 30 gün içinde dağıtım şirketine talepte bulunun."
    response = "Başvurunun haklı bulunmadığı durumda dağıtım şirketi 10 iş günü içinde teknik raporu bildirir."
    assert STALE_DEADLINE.search(stale)
    assert CURRENT_DEADLINE_PATTERN.search(current)
    assert STALE_DEADLINE.search(response)


def build_and_validate() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="alo186-device-damage-deadline-") as folder:
        output = Path(folder) / "site"
        subprocess.run(
            [
                sys.executable,
                "alo186/deployment/build_static_site.py",
                "--output",
                str(output),
                "--commit",
                "deadline-guard",
            ],
            cwd=ROOT,
            check=True,
        )
        stale = find_stale_application_deadlines(output)
        current = find_current_application_deadlines(output)
        if stale:
            raise AssertionError(
                "Yayın paketinde cihaz hasarı başvurusu için eski 10 iş günü ifadesi bulundu:\n- "
                + "\n- ".join(stale)
            )
        if not current:
            raise AssertionError("Yayın paketinde cihaz hasarı başvurusunu 30 güne bağlayan metin yok.")
        release = json.loads((output / "alo186-release.json").read_text(encoding="utf-8"))
        assert release["deviceDamageDeadline"] == CURRENT_DEADLINE
        assert int(release["deviceDamageVerifiedLocations"]) > 0
        htaccess = (output / ".htaccess").read_text(encoding="utf-8")
        assert "mod_substitute" not in htaccess.lower()
        assert "Substitute \"s|" not in htaccess
        return {
            "deadline": release["deviceDamageDeadline"],
            "verifiedLocations": release["deviceDamageVerifiedLocations"],
            "normalizedFiles": release["deviceDamageNormalizedFiles"],
        }


def main() -> int:
    self_test()
    report = build_and_validate()
    print(json.dumps({"ok": True, **report}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
