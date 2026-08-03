from __future__ import annotations

"""Load the reviewed v260 implementation from the repository payload.

The payload is stored under .github so it never enters the public site artifact.
Keeping the loader small also makes the production import contract explicit.
"""

import base64
import gzip
import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_PARTS = sorted((_REPO / ".github/v260-payload").glob("part*"))
_KEY = "alo186/deployment/inject_competitor_gap_affiliate_v260.py"
if not _PARTS:
    raise FileNotFoundError("ALO186 v260 implementation payload is missing")
_payload = json.loads("".join(path.read_text(encoding="utf-8") for path in _PARTS))
if _KEY not in _payload:
    raise RuntimeError("ALO186 v260 implementation key is missing")
_source = gzip.decompress(base64.b64decode(_payload[_KEY])).decode("utf-8")
exec(compile(_source, str(Path(__file__).with_suffix(".impl.py")), "exec"), globals(), globals())
