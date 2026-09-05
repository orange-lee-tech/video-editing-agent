from __future__ import annotations

import json
from collections.abc import Mapping
from typing import cast

from video_editing_agent.adapters.product import update_ed25519

UPDATE_SIGNATURE_ALGORITHM = "ed25519"
UPDATE_SIGNATURE_KEY_ID = "vea-update-manifest-v1"
# Production public key for VideoEditingAgent-updater.exe. The matching seed is a
# release secret (UPDATE_MANIFEST_SIGNING_KEY) and must never be committed.
UPDATE_MANIFEST_PUBLIC_KEY = bytes.fromhex(
    "ef69d6406c43ac83fea6c8d10845359d0f75f105789d05f6ec85f00408a141d9"
)


def canonical_manifest_body(payload: Mapping[str, object]) -> bytes:
    body = {key: value for key, value in payload.items() if key != "signature"}
    return json.dumps(
        body,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sign_manifest_payload(payload: Mapping[str, object], seed: bytes) -> dict[str, object]:
    if "signature" in payload:
        raise ValueError("manifest payload already contains a signature field")
    if len(seed) != 32:
        raise ValueError("update signing seed must be 32 bytes")
    document = dict(payload)
    signature = update_ed25519.sign(seed, canonical_manifest_body(document))
    document["signature"] = {
        "alg": UPDATE_SIGNATURE_ALGORITHM,
        "key_id": UPDATE_SIGNATURE_KEY_ID,
        "sig": signature.hex(),
    }
    return document


def verify_manifest_signature(
    payload: Mapping[str, object],
    *,
    public_key: bytes = UPDATE_MANIFEST_PUBLIC_KEY,
) -> None:
    raw_signature = payload.get("signature")
    if not isinstance(raw_signature, dict):
        raise ValueError("update manifest signature is missing")
    algorithm = raw_signature.get("alg")
    key_id = raw_signature.get("key_id")
    signature_hex = raw_signature.get("sig")
    if algorithm != UPDATE_SIGNATURE_ALGORITHM or key_id != UPDATE_SIGNATURE_KEY_ID:
        raise ValueError("update manifest signature algorithm/key id is unsupported")
    if not isinstance(signature_hex, str):
        raise ValueError("update manifest signature is invalid")
    try:
        signature = bytes.fromhex(signature_hex.strip())
    except ValueError as exc:
        raise ValueError("update manifest signature is not hex") from exc
    if len(public_key) != 32 or public_key == bytes(32):
        raise ValueError("update manifest public key is not configured")
    update_ed25519.verify(public_key, canonical_manifest_body(payload), signature)


def signed_manifest_text(payload: Mapping[str, object], seed: bytes) -> str:
    document = sign_manifest_payload(payload, seed)
    return json.dumps(cast(dict[str, object], document), ensure_ascii=False, indent=2) + "\n"
