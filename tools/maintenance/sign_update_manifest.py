from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from video_editing_agent.adapters.product.update_ed25519 import public_key_from_seed
from video_editing_agent.adapters.product.update_signature import (
    UPDATE_MANIFEST_PUBLIC_KEY,
    signed_manifest_text,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sign a 有岐 update manifest with Ed25519")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--seed-hex",
        default=os.environ.get("UPDATE_MANIFEST_SIGNING_KEY", ""),
        help="32-byte Ed25519 seed as hex; defaults to UPDATE_MANIFEST_SIGNING_KEY",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    seed_hex = args.seed_hex.strip()
    if len(seed_hex) != 64:
        raise SystemExit("signing seed must be 32 bytes encoded as 64 hex characters")
    seed = bytes.fromhex(seed_hex)
    public = public_key_from_seed(seed)
    if public != UPDATE_MANIFEST_PUBLIC_KEY:
        raise SystemExit("signing seed does not match the embedded update-manifest public key")
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("update manifest root must be an object")
    payload.pop("signature", None)
    args.output.write_text(signed_manifest_text(payload, seed), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
