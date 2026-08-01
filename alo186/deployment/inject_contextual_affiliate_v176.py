from __future__ import annotations

import argparse
import base64
import json
import zlib
from pathlib import Path

_PAYLOAD_DIR = Path(__file__).with_name("contextual-affiliate-v176-payload")


def _payload(name: str) -> bytes:
    parts = sorted(_PAYLOAD_DIR.glob(f"{name}-*.txt"))
    if not parts:
        raise FileNotFoundError(f"ALO186 v176 payload eksik: {name}")
    encoded = "".join(path.read_text(encoding="ascii").strip() for path in parts)
    return zlib.decompress(base64.b64decode(encoded))


_impl_ns: dict[str, object] = {
    "__name__": "_alo186_contextual_affiliate_v176_impl",
    "__file__": __file__,
}
exec(compile(_payload("impl").decode("utf-8"), __file__ + "::<impl>", "exec"), _impl_ns)
for _name, _value in _impl_ns.items():
    if not _name.startswith("__"):
        globals()[_name] = _value
_impl_run = _impl_ns["run"]


def embedded_catalog() -> dict:
    return json.loads(_payload("catalog").decode("utf-8"))


def materialize_catalog(site: Path) -> Path:
    target = Path(site) / "amazon-elektrik-urunleri/konuya-gore-urun-haritasi/catalog-v176.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(embedded_catalog(), ensure_ascii=False, indent=2) + "\n"
    if not target.is_file() or target.read_text(encoding="utf-8") != rendered:
        target.write_text(rendered, encoding="utf-8")
    return target


def run(site: Path, base_path: str = "") -> dict:
    materialize_catalog(Path(site))
    return _impl_run(Path(site), base_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 bağlamsal affiliate ürün haritasını final artifacta ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
