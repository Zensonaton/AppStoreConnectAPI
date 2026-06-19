# coding: utf-8

import base64
from datetime import datetime, timedelta, timezone

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


@pytest.fixture
def der_certificate() -> tuple[x509.Certificate, str]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Test")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(1234567890)
        .not_valid_before(datetime.now(timezone.utc) - timedelta(days=1))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
        .sign(key, hashes.SHA256())
    )
    der = cert.public_bytes(serialization.Encoding.DER)
    encoded = base64.b64encode(der).decode()

    return cert, encoded


@pytest.fixture
def bundle_id_payload() -> dict:
    return {
        "id": "ABC123",
        "type": "bundleIds",
        "attributes": {
            "identifier": "com.example.app",
            "name": "Example App",
            "platform": "IOS",
            "seedId": "SEED99",
        },
    }


@pytest.fixture
def certificate_payload(der_certificate) -> dict:
    _, encoded = der_certificate

    return {
        "id": "CERT123",
        "type": "certificates",
        "attributes": {
            "name": "Dist Cert",
            "displayName": "Distribution Certificate",
            "certificateType": "DISTRIBUTION",
            "expirationDate": "2030-01-01T00:00:00.000+00:00",
            "certificateContent": encoded,
            "serialNumber": "0011AABB",
            "platform": "IOS",
        },
    }


@pytest.fixture
def profile_payload() -> dict:
    return {
        "id": "PROF123",
        "type": "profiles",
        "attributes": {
            "name": "AppStore Profile",
            "platform": "IOS",
            "profileType": "IOS_APP_STORE",
            "profileState": "ACTIVE",
            "profileContent": base64.b64encode(b"mobileprovision-bytes").decode(),
            "uuid": "11111111-2222-3333-4444-555555555555",
            "createdDate": "2024-01-01T00:00:00.000+00:00",
            "expirationDate": "2030-01-01T00:00:00.000+00:00",
        },
    }
