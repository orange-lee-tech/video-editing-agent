"""Public-domain Ed25519 (ref10 / DJB Python), used only for update-manifest signatures."""

from __future__ import annotations

import hashlib
import os

_B = 256
_Q = 2**255 - 19
_L = 2**252 + 27742317777372353535851937790883648493
_D = -121665 * pow(121666, _Q - 2, _Q) % _Q
_I = pow(2, (_Q - 1) // 4, _Q)


def _inv(x: int) -> int:
    return pow(x, _Q - 2, _Q)


def _xrecover(y: int) -> int:
    xx = (y * y - 1) * _inv(_D * y * y + 1)
    x = pow(xx, (_Q + 3) // 8, _Q)
    if (x * x - xx) % _Q != 0:
        x = (x * _I) % _Q
    if x % 2 != 0:
        x = _Q - x
    return x


_BY = 4 * _inv(5) % _Q
_BX = _xrecover(_BY)
_B_POINT = (_BX % _Q, _BY % _Q)


def _edwards(p: tuple[int, int], q: tuple[int, int]) -> tuple[int, int]:
    x1, y1 = p
    x2, y2 = q
    x3 = (x1 * y2 + x2 * y1) * _inv(1 + _D * x1 * x2 * y1 * y2)
    y3 = (y1 * y2 + x1 * x2) * _inv(1 - _D * x1 * x2 * y1 * y2)
    return (x3 % _Q, y3 % _Q)


def _scalarmult(point: tuple[int, int], scalar: int) -> tuple[int, int]:
    if scalar == 0:
        return (0, 1)
    q = _scalarmult(point, scalar // 2)
    q = _edwards(q, q)
    if scalar & 1:
        q = _edwards(q, point)
    return q


def _encodeint(y: int) -> bytes:
    return y.to_bytes(_B // 8, "little")


def _encodepoint(point: tuple[int, int]) -> bytes:
    x, y = point
    packed = bytearray(_encodeint(y))
    packed[-1] |= 0x80 if x & 1 else 0
    return bytes(packed)


def _bit(h: bytes, i: int) -> int:
    return (h[i // 8] >> (i % 8)) & 1


def _decodeint(s: bytes) -> int:
    return int.from_bytes(s, "little")


def _decodepoint(s: bytes) -> tuple[int, int]:
    y = _decodeint(s) & (2**255 - 1)
    x = _xrecover(y)
    if x & 1 != _bit(s, _B - 1):
        x = _Q - x
    point = (x, y)
    if not _isoncurve(point):
        raise ValueError("ed25519 public key is not a valid curve point")
    return point


def _isoncurve(point: tuple[int, int]) -> bool:
    x, y = point
    return (-x * x + y * y - 1 - _D * x * x * y * y) % _Q == 0


def _hint(message: bytes) -> int:
    return _decodeint(hashlib.sha512(message).digest())


def public_key_from_seed(seed: bytes) -> bytes:
    if len(seed) != 32:
        raise ValueError("ed25519 seed must be 32 bytes")
    h = hashlib.sha512(seed).digest()
    a = 2 ** (_B - 2) + sum(2**i * _bit(h, i) for i in range(3, _B - 2))
    return _encodepoint(_scalarmult(_B_POINT, a))


def generate_seed() -> bytes:
    return os.urandom(32)


def sign(seed: bytes, message: bytes) -> bytes:
    if len(seed) != 32:
        raise ValueError("ed25519 seed must be 32 bytes")
    h = hashlib.sha512(seed).digest()
    a = 2 ** (_B - 2) + sum(2**i * _bit(h, i) for i in range(3, _B - 2))
    public = _encodepoint(_scalarmult(_B_POINT, a))
    r = _hint(h[_B // 8 : _B // 4] + message)
    big_r = _scalarmult(_B_POINT, r)
    encoded_r = _encodepoint(big_r)
    s = (r + _hint(encoded_r + public + message) * a) % _L
    return encoded_r + _encodeint(s)


def verify(public: bytes, message: bytes, signature: bytes) -> None:
    if len(public) != 32:
        raise ValueError("ed25519 public key must be 32 bytes")
    if len(signature) != 64:
        raise ValueError("ed25519 signature must be 64 bytes")
    point_a = _decodepoint(public)
    r = signature[:32]
    s = _decodeint(signature[32:])
    if s >= _L:
        raise ValueError("ed25519 signature scalar is out of range")
    point_r = _decodepoint(r)
    k = _hint(r + public + message)
    left = _scalarmult(_B_POINT, s)
    right = _edwards(point_r, _scalarmult(point_a, k))
    if left != right:
        raise ValueError("update manifest signature is invalid")
