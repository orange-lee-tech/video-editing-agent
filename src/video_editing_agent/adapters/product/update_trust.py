from __future__ import annotations

import ctypes
import hashlib
import os
from dataclasses import dataclass
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
CERT_FIND_SUBJECT_CERT = 0x000B0000
CMSG_SIGNER_CERT_INFO_PARAM = 7
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


class CERT_CONTEXT(ctypes.Structure):
    _fields_ = [
        ("dwCertEncodingType", ctypes.c_uint32),
        ("pbCertEncoded", ctypes.POINTER(ctypes.c_ubyte)),
        ("cbCertEncoded", ctypes.c_uint32),
        ("pCertInfo", ctypes.c_void_p),
        ("hCertStore", ctypes.c_void_p),
    ]


WINTRUST_ACTION_GENERIC_VERIFY_V2 = GUID(
    0x00AAC56B,
    0xCD44,
    0x11D0,
    (ctypes.c_ubyte * 8)(0x8C, 0xC2, 0x00, 0xC0, 0x4F, 0xC2, 0x95, 0xEE),
)


@dataclass(frozen=True, slots=True)
class SignerIdentity:
    certificate_sha256: str
    subject: str

    def __post_init__(self) -> None:
        fingerprint = self.certificate_sha256.casefold()
        if len(fingerprint) != 64 or any(ch not in "0123456789abcdef" for ch in fingerprint):
            raise ValueError("signer certificate SHA-256 fingerprint is invalid")
        if not self.subject.strip():
            raise ValueError("signer certificate subject must not be blank")


class ReplacementTrust(Protocol):
    def publisher_of(self, path: Path) -> SignerIdentity | None: ...


class UnsignedReplacementTrust:
    def publisher_of(self, path: Path) -> SignerIdentity | None:
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
    def publisher_of(self, path: Path) -> SignerIdentity | None:
        if not looks_like_pe(path):
            return None
        status = _win_verify_trust(path)
        if status in {TRUST_E_NOSIGNATURE, CRYPT_E_NO_MATCH}:
            return None
        if status != 0:
            raise ValueError(f"Authenticode verification failed: 0x{status & 0xFFFFFFFF:08X}")
        identity = _authenticode_signer_identity(path)
        if identity is None:
            raise ValueError("Authenticode signature did not resolve its signer certificate")
        return identity


def enforce_replacement_trust(
    staged: Path,
    *,
    destination: Path,
    previous_publisher: SignerIdentity | None,
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
    if (
        previous_publisher
        and new_publisher.certificate_sha256.casefold()
        != previous_publisher.certificate_sha256.casefold()
    ):
        raise ValueError(
            f"replacement {destination.name} signer certificate "
            f"{new_publisher.certificate_sha256!r} ({new_publisher.subject}) does not match "
            f"installed signer certificate {previous_publisher.certificate_sha256!r} "
            f"({previous_publisher.subject})"
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


def _authenticode_signer_identity(path: Path) -> SignerIdentity | None:
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
    context = ctypes.c_void_p()
    try:
        signer_info_size = ctypes.c_uint32()
        crypt32.CryptMsgGetParam.restype = ctypes.c_int
        if not crypt32.CryptMsgGetParam(
            message,
            CMSG_SIGNER_CERT_INFO_PARAM,
            0,
            None,
            ctypes.byref(signer_info_size),
        ):
            return None
        signer_info = ctypes.create_string_buffer(signer_info_size.value)
        if not crypt32.CryptMsgGetParam(
            message,
            CMSG_SIGNER_CERT_INFO_PARAM,
            0,
            signer_info,
            ctypes.byref(signer_info_size),
        ):
            return None

        crypt32.CertFindCertificateInStore.restype = ctypes.c_void_p
        context = ctypes.c_void_p(
            crypt32.CertFindCertificateInStore(
                store,
                encoding.value,
                0,
                CERT_FIND_SUBJECT_CERT,
                ctypes.cast(signer_info, ctypes.c_void_p),
                None,
            )
        )
        if not context.value:
            return None

        cert_context = ctypes.cast(context, ctypes.POINTER(CERT_CONTEXT)).contents
        encoded = ctypes.string_at(cert_context.pbCertEncoded, cert_context.cbCertEncoded)
        fingerprint = hashlib.sha256(encoded).hexdigest()

        crypt32.CertGetNameStringW.restype = ctypes.c_uint32
        length = crypt32.CertGetNameStringW(
            context,
            CERT_NAME_SIMPLE_DISPLAY_TYPE,
            0,
            None,
            None,
            0,
        )
        if length <= 1:
            return None
        buffer = ctypes.create_unicode_buffer(length)
        crypt32.CertGetNameStringW(
            context,
            CERT_NAME_SIMPLE_DISPLAY_TYPE,
            0,
            None,
            buffer,
            length,
        )
        if not buffer.value.strip():
            return None
        return SignerIdentity(fingerprint, buffer.value.strip())
    finally:
        if context.value:
            crypt32.CertFreeCertificateContext(context)
        if store:
            crypt32.CertCloseStore(store, 0)
        if message:
            crypt32.CryptMsgClose(message)
