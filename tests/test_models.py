# coding: utf-8

import base64
from datetime import datetime, timezone

from cryptography import x509

from appstoreconnectapi.api.models import BundleID, Certificate, Profile


class TestBundleID:
    def test_flattens_attributes(self, bundle_id_payload):
        bundle = BundleID.model_validate(bundle_id_payload)

        assert bundle.id == "ABC123"
        assert bundle.identifier == "com.example.app"
        assert bundle.name == "Example App"
        assert bundle.platform == "IOS"
        assert bundle.seed_id == "SEED99"

    def test_camel_case_alias(self, bundle_id_payload):
        del bundle_id_payload["attributes"]["seedId"]
        bundle = BundleID.model_validate(bundle_id_payload)

        assert bundle.seed_id is None

    def test_populate_by_snake_case_name(self):
        bundle = BundleID.model_validate(
            {
                "id": "X",
                "identifier": "com.x",
                "name": "X",
                "platform": "IOS",
                "seed_id": "S",
            }
        )

        assert bundle.seed_id == "S"


class TestCertificate:
    def test_flattens_attributes(self, certificate_payload):
        cert = Certificate.model_validate(certificate_payload)

        assert cert.id == "CERT123"
        assert cert.name == "Dist Cert"
        assert cert.display_name == "Distribution Certificate"
        assert cert.certificate_type == "DISTRIBUTION"
        assert cert.serial_number == "0011AABB"
        assert cert.platform == "IOS"

    def test_expiration_date_parsed_as_datetime(self, certificate_payload):
        cert = Certificate.model_validate(certificate_payload)

        assert isinstance(cert.expiration_date, datetime)
        assert cert.expiration_date.year == 2030

    def test_valid_certificate_properties(self, certificate_payload):
        cert = Certificate.model_validate(certificate_payload)

        assert cert.days_until_expiration > 0
        assert cert.is_expired is False
        assert cert.is_valid is True

    def test_expired_certificate_properties(self, certificate_payload):
        certificate_payload["attributes"]["expirationDate"] = "2000-01-01T00:00:00.000+00:00"
        cert = Certificate.model_validate(certificate_payload)

        assert cert.days_until_expiration < 0
        assert cert.is_expired is True
        assert cert.is_valid is False

    def test_contents_as_bytes(self, certificate_payload):
        cert = Certificate.model_validate(certificate_payload)
        expected = base64.b64decode(certificate_payload["attributes"]["certificateContent"])

        assert cert.contents_as_bytes == expected

    def test_x509_certificate(self, certificate_payload, der_certificate):
        source_cert, _ = der_certificate
        cert = Certificate.model_validate(certificate_payload)

        parsed = cert.x509_certificate

        assert isinstance(parsed, x509.Certificate)
        assert parsed.serial_number == source_cert.serial_number


class TestProfile:
    def test_flattens_attributes(self, profile_payload):
        profile = Profile.model_validate(profile_payload)

        assert profile.id == "PROF123"
        assert profile.name == "AppStore Profile"
        assert profile.platform == "IOS"
        assert profile.profile_type == "IOS_APP_STORE"
        assert profile.profile_state == "ACTIVE"
        assert profile.uuid == "11111111-2222-3333-4444-555555555555"

    def test_dates_parsed_as_datetime(self, profile_payload):
        profile = Profile.model_validate(profile_payload)

        assert isinstance(profile.created_date, datetime)
        assert isinstance(profile.expiration_date, datetime)
        assert profile.created_date.year == 2024

    def test_valid_profile_properties(self, profile_payload):
        profile = Profile.model_validate(profile_payload)

        assert profile.days_until_expiration > 0
        assert profile.is_expired is False
        assert profile.is_valid is True

    def test_expired_profile_properties(self, profile_payload):
        profile_payload["attributes"]["expirationDate"] = "2000-01-01T00:00:00.000+00:00"
        profile = Profile.model_validate(profile_payload)

        assert profile.is_expired is True
        assert profile.is_valid is False

    def test_contents_as_bytes(self, profile_payload):
        profile = Profile.model_validate(profile_payload)

        assert profile.contents_as_bytes == b"mobileprovision-bytes"


def test_days_until_expiration_handles_naive_now():
    payload = {
        "id": "C",
        "attributes": {
            "name": "n",
            "displayName": "d",
            "certificateType": "DISTRIBUTION",
            "expirationDate": datetime(2030, 1, 1, tzinfo=timezone.utc),
            "certificateContent": base64.b64encode(b"x").decode(),
            "serialNumber": "1",
        },
    }
    cert = Certificate.model_validate(payload)

    assert cert.days_until_expiration > 0
