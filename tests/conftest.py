# coding: utf-8

import base64
from datetime import datetime, timedelta, timezone
from typing import Callable
from unittest.mock import MagicMock

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import NameOID

from appstoreconnectapi.client import AppStoreConnectClient


@pytest.fixture
def private_key_pem() -> bytes:
    key = ec.generate_private_key(ec.SECP256R1())

    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


@pytest.fixture
def client(private_key_pem) -> AppStoreConnectClient:
    return AppStoreConnectClient("KEY123", "ISSUER123", private_key_pem)


@pytest.fixture
def mock_response() -> Callable[[dict | list], MagicMock]:
    def _mock_response(json_data: dict | list) -> MagicMock:
        response = MagicMock()
        response.json.return_value = json_data

        return response

    return _mock_response


@pytest.fixture
def mock_api(client, mock_response) -> Callable[[dict], MagicMock]:
    """
    Makes the client answer its next request with the given JSON response, returning the mocked request.
    """

    def _mock_api(json_data: dict) -> MagicMock:
        client.http_client.request = MagicMock(return_value=mock_response(json_data))

        return client.http_client.request

    return _mock_api


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


@pytest.fixture
def app_payload() -> dict:
    return {
        "id": "APP123",
        "type": "apps",
        "attributes": {
            "name": "Example App",
            "bundleId": "com.example.app",
            "sku": "EXAMPLE",
            "primaryLocale": "en-US",
            "isOrEverWasMadeForKids": False,
            "contentRightsDeclaration": "DOES_NOT_USE_THIRD_PARTY_CONTENT",
            "streamlinedPurchasingEnabled": True,
        },
    }


@pytest.fixture
def apps_response(app_payload) -> dict:
    return {"data": [app_payload]}


@pytest.fixture
def app_store_versions_response() -> dict:
    """
    Response of the App Store versions endpoint, requested with `include=["build"]`.
    """

    return {
        "data": [
            {
                "id": "VERSION1",
                "type": "appStoreVersions",
                "attributes": {
                    "versionString": "1.4.0",
                    "platform": "IOS",
                    "appVersionState": "READY_FOR_DISTRIBUTION",
                    "releaseType": "MANUAL",
                    "downloadable": True,
                    "createdDate": "2024-06-01T00:00:00.000+00:00",
                },
                "relationships": {
                    "build": {"data": {"id": "BUILD1", "type": "builds"}},
                },
            },
            {
                "id": "VERSION2",
                "type": "appStoreVersions",
                "attributes": {
                    "versionString": "1.3.0",
                    "platform": "IOS",
                    "appVersionState": "REPLACED_WITH_NEW_VERSION",
                    "createdDate": "2024-05-01T00:00:00.000+00:00",
                },
                "relationships": {
                    "build": {"data": {"id": "BUILD2", "type": "builds"}},
                },
            },
        ],
        "included": [
            {
                "id": "BUILD1",
                "type": "builds",
                "attributes": {"version": "42", "processingState": "VALID"},
            },
            {
                "id": "BUILD2",
                "type": "builds",
                "attributes": {"version": "37", "processingState": "VALID"},
            },
        ],
    }


@pytest.fixture
def pre_release_versions_response(app_payload) -> dict:
    """
    Response of the pre-release versions endpoint, requested with `include=["builds", "app"]`.
    """

    return {
        "data": [
            {
                "id": "PRERELEASE1",
                "type": "preReleaseVersions",
                "attributes": {"version": "1.5.0", "platform": "IOS"},
                "relationships": {
                    "builds": {
                        "data": [
                            {"id": "BUILD3", "type": "builds"},
                            {"id": "BUILD4", "type": "builds"},
                        ]
                    },
                    "app": {"data": {"id": "APP123", "type": "apps"}},
                },
            },
            {
                "id": "PRERELEASE2",
                "type": "preReleaseVersions",
                "attributes": {"version": "1.4.0", "platform": "IOS"},
                "relationships": {
                    "builds": {"data": [{"id": "BUILD1", "type": "builds"}]},
                    "app": {"data": None},
                },
            },
        ],
        "included": [
            {
                "id": "BUILD3",
                "type": "builds",
                "attributes": {
                    "version": "56",
                    "uploadedDate": "2024-06-10T00:00:00.000+00:00",
                    "expired": False,
                    "minOsVersion": "16.0",
                    "processingState": "VALID",
                    "buildAudienceType": "APP_STORE_ELIGIBLE",
                },
            },
            {
                "id": "BUILD4",
                "type": "builds",
                "attributes": {"version": "55", "expired": True, "processingState": "VALID"},
            },
            {
                "id": "BUILD1",
                "type": "builds",
                "attributes": {"version": "42", "processingState": "VALID"},
            },
            app_payload,
            {
                "id": "UNKNOWN1",
                "type": "unknownResources",
                "attributes": {"whatever": True},
            },
        ],
    }
