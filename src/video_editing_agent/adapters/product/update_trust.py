from __future__ import annotations

import ctypes
import os
from pathlib import Path
from typing import Protocol

_MZ = b"MZ"
_SIGNED_PRODUCT_EXECUTABLES = frozenset(
    {
        "videoeditingagent.exe",
        "videoeditingagent-cli.exe",
    }
)
WTD_UI_NONE = 2
WTD_REVOKE_NONE = 0
WTD_CHOICE_FILE = 1
WTD_STATEACTION_VERIFY = 1
WTD_STATEACTION_CLOSE = 2
WTD_CACHE_ONLY_URL_RETRIEVAL = 0x00001000
CERT_QUERY_OBJECT_FILE = 1
CERT_QUERY_CONTENT_FLAG_PKCS7_SIGNED_EMBED = 0x00000400
CERT_QUERY_FORMAT_FLAG_BINARY = 2
CERT_NAME_SIMPLE_DISPLAY_TYPE = 4
TRUST_E_NOSIGNATURE = 0x800B0100
CRYPT_E_NO_MATCH = 0x80092009


class WINTRUST_FILE_INFO(ctypes.Structure):
    _fields_ = [
        ("cbStruct", ctypes.c_uint32),
        ("pcwszFilePath", ctypes.c_wchar_p),
        ("hFile", ctypes.c_void_p),
        ("pgKnownSubject", ctypes.c_void_p),
    ]


class _WINTRUST_DATA_UNION(ctypes.Union):
    _fields_ = [("pFile", ctypes.POINTER(WINTRUST_FILE_INFO))]


class WINTRUST_DATA(ctypes.Structure):
    _anonymous_ = ("union",)
    _fields_ = [
        ("cbStruct", ctypes.c_uint32),
        ("pPolicyCallbackData", ctypes.c_void_p),
        ("pSIPClientData", ctypes.c_void_p),
        ("dwUIChoice", ctypes.c_uint32),
        ("fdwRevocationChecks", ctypes.c_uint32),
        ("dwUnionChoice", ctypes.c_uint32),
        ("union", _WINTRUST_DATA_UNION),
        ("dwStateAction", ctypes.c_uint32),
        ("hWVTStateData", ctypes.c_void_p),
        ("pwszURLReference", ctypes.c_wchar_p),
        ("dwProvFlags", ctypes.c_uint32),
        ("dwUIContext", ctypes.c_uint32),
        ("pSignatureSettings", ctypes.c_void_p),
    ]


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", ctypes.c_uint32),
        ("Data2", ctypes.c_uint16),
        ("Data3", ctypes.c_uint16),
        ("Data4", ctypes.c_ubyte * 8),
    ]


WINTRUST_ACTION_GENERIC_VERIFY_V2 = GUID(
    0x00AAC56B,
    0xCD44,
    0x11D0,
    (ctypes.c_ubyte * 8)(0x8C, 0xC2, 0x00, 0xC0, 0x4F, 0xC2, 0x95, 0xEE),
)


class ReplacementTrust(Protocol):
    def publisher_of(self, path: Path) -> str | None: ...


class UnsignedReplacementTrust:
    def publisher_of(self, path: Path) -> str | None:
        del path
        return None


def looks_like_pe(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return handle.read(2) == _MZ
    except OSError:
        return False


def default_replacement_trust() -> ReplacementTrust:
    if os.name == "nt":
        return WindowsAuthenticodeTrust()
    return UnsignedReplacementTrust()


class WindowsAuthenticodeTrust:
    def publisher_of(self, path: Path) -> str | None:
        if not looks_like_pe(path):
            return None
        status = _win_verify_trust(path)
        if status in {TRUST_E_NOSIGNATURE, CRYPT_E_NO_MATCH}:
            return None
        if status != 0:
            raise ValueError(f"Authenticode verification failed: 0x{status & 0xFFFFFFFF:08X}")
        name = _leaf_publisher_name(path)
        if name is None or not name.strip():
            raise ValueError("Authenticode signature did not include a publisher")
        return name.strip()


def enforce_replacement_trust(
    staged: Path,
    *,
    destination: Path,
    previous_publisher: str | None,
    trust: ReplacementTrust,
) -> None:
    if not looks_like_pe(staged):
        return
    new_publisher = trust.publisher_of(staged)
    required = destination.name.casefold() in _SIGNED_PRODUCT_EXECUTABLES or bool(
        previous_publisher
    )
    if not required:
        return
    if new_publisher is None:
        raise ValueError(f"replacement {destination.name} is not Authenticode-signed")
    if previous_publisher and new_publisher.casefold() != previous_publisher.casefold():
        raise ValueError(
            f"replacement {destination.name} publisher {new_publisher!r} does not match "
            f"installed publisher {previous_publisher!r}"
        )


def _win_verify_trust(path: Path) -> int:
    windll = getattr(ctypes, "windll", None)
    if windll is None:
        raise ValueError("Authenticode verification requires Windows")
    file_info = WINTRUST_FILE_INFO(ctypes.sizeof(WINTRUST_FILE_INFO), str(path), None, None)
    data = WINTRUST_DATA()
    data.cbStruct = ctypes.sizeof(WINTRUST_DATA)
    data.dwUIChoice = WTD_UI_NONE
    data.fdwRevocationChecks = WTD_REVOKE_NONE
    data.dwUnionChoice = WTD_CHOICE_FILE
    data.pFile = ctypes.pointer(file_info)
    data.dwStateAction = WTD_STATEACTION_VERIFY
    data.dwProvFlags = WTD_CACHE_ONLY_URL_RETRIEVAL
    action = WINTRUST_ACTION_GENERIC_VERIFY_V2
    verify = windll.wintrust.WinVerifyTrust
    verify.argtypes = [ctypes.c_void_p, ctypes.POINTER(GUID), ctypes.c_void_p]
    verify.restype = ctypes.c_long
    status = int(verify(None, ctypes.byref(action), ctypes.byref(data)))
    data.dwStateAction = WTD_STATEACTION_CLOSE
    verify(None, ctypes.byref(action), ctypes.byref(data))
    return status & 0xFFFFFFFF


def _leaf_publisher_name(path: Path) -> str | None:
    windll = getattr(ctypes, "windll", None)
    if windll is None:
        return None
    crypt32 = windll.crypt32
    encoding = ctypes.c_uint32()
    content_type = ctypes.c_uint32()
    format_type = ctypes.c_uint32()
    store = ctypes.c_void_p()
    message = ctypes.c_void_p()
    crypt32.CryptQueryObject.restype = ctypes.c_int
    if not crypt32.CryptQueryObject(
        CERT_QUERY_OBJECT_FILE,
        ctypes.c_wchar_p(str(path)),
        CERT_QUERY_CONTENT_FLAG_PKCS7_SIGNED_EMBED,
        CERT_QUERY_FORMAT_FLAG_BINARY,
        0,
        ctypes.byref(encoding),
        ctypes.byref(content_type),
        ctypes.byref(format_type),
        ctypes.byref(store),
        ctypes.byref(message),
        None,
    ):
        return None
    try:
        crypt32.CertEnumCertificatesInStore.restype = ctypes.c_void_p
        context = crypt32.CertEnumCertificatesInStore(store, None)
        if not context:
            return None
        crypt32.CertGetNameStringW.restype = ctypes.c_uint32
        length = crypt32.CertGetNameStringW(
            context, CERT_NAME_SIMPLE_DISPLAY_TYPE, 0, None, None, 0
        )
        if length <= 1:
            crypt32.CertFreeCertificateContext(context)
            return None
        buffer = ctypes.create_unicode_buffer(length)
        crypt32.CertGetNameStringW(
            context, CERT_NAME_SIMPLE_DISPLAY_TYPE, 0, None, buffer, length
        )
        crypt32.CertFreeCertificateContext(context)
        return buffer.value
    finally:
        if store:
            crypt32.CertCloseStore(store, 0)
        if message:
            crypt32.CryptMsgClose(message)
