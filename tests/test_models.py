# coding: utf-8

import base64
from datetime import datetime, timezone

from cryptography import x509

from appstoreconnectapi.api.models import (
    App,
    AppStoreVersion,
    Build,
    BundleID,
    Certificate,
    PreReleaseVersion,
    Profile,
    _Resource,
)


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


class TestApp:
    def test_flattens_attributes(self, app_payload):
        app = App.model_validate(app_payload)

        assert app.id == "APP123"
        assert app.name == "Example App"
        assert app.bundle_id == "com.example.app"
        assert app.sku == "EXAMPLE"
        assert app.primary_locale == "en-US"
        assert app.is_or_ever_was_made_for_kids is False
        assert app.content_rights_declaration == "DOES_NOT_USE_THIRD_PARTY_CONTENT"
        assert app.streamlined_purchasing_enabled is True

    def test_optional_attributes_default_to_none(self, app_payload):
        del app_payload["attributes"]["sku"]
        del app_payload["attributes"]["primaryLocale"]
        app = App.model_validate(app_payload)

        assert app.sku is None
        assert app.primary_locale is None


class TestAppStoreVersion:
    def test_flattens_attributes(self, app_store_versions_response):
        version = AppStoreVersion.model_validate(app_store_versions_response["data"][0])

        assert version.id == "VERSION1"
        assert version.version_string == "1.4.0"
        assert version.platform == "IOS"
        assert version.app_version_state == "READY_FOR_DISTRIBUTION"
        assert version.release_type == "MANUAL"
        assert version.downloadable is True
        assert isinstance(version.created_date, datetime)
        assert version.created_date.year == 2024

    def test_build_property_returns_included_build(self, app_store_versions_response):
        version = AppStoreVersion.list_from_response(app_store_versions_response)[0]

        assert isinstance(version.build, Build)
        assert version.build.version == "42"

    def test_build_property_is_none_without_includes(self, app_store_versions_response):
        version = AppStoreVersion.model_validate(app_store_versions_response["data"][0])

        assert version.build is None


class TestBuild:
    def test_flattens_attributes(self, pre_release_versions_response):
        build = Build.model_validate(pre_release_versions_response["included"][0])

        assert build.id == "BUILD3"
        assert build.version == "56"
        assert build.expired is False
        assert build.min_os_version == "16.0"
        assert build.processing_state == "VALID"
        assert build.build_audience_type == "APP_STORE_ELIGIBLE"
        assert isinstance(build.uploaded_date, datetime)


class TestPreReleaseVersion:
    def test_flattens_attributes(self, pre_release_versions_response):
        version = PreReleaseVersion.model_validate(pre_release_versions_response["data"][0])

        assert version.id == "PRERELEASE1"
        assert version.version == "1.5.0"
        assert version.platform == "IOS"

    def test_builds_property_returns_included_builds(self, pre_release_versions_response):
        version = PreReleaseVersion.list_from_response(pre_release_versions_response)[0]

        assert [build.version for build in version.builds] == ["56", "55"]

    def test_builds_property_is_empty_without_includes(self, pre_release_versions_response):
        version = PreReleaseVersion.model_validate(pre_release_versions_response["data"][0])

        assert version.builds == []


class TestIncludes:
    def test_defaults_to_empty_list(self, bundle_id_payload):
        bundle = BundleID.model_validate(bundle_id_payload)

        assert bundle.includes == []

    def test_from_response_resolves_includes(self, pre_release_versions_response):
        response = {
            "data": pre_release_versions_response["data"][0],
            "included": pre_release_versions_response["included"],
        }
        version = PreReleaseVersion.from_response(response)

        assert version.id == "PRERELEASE1"
        assert [include.id for include in version.includes] == ["BUILD3", "BUILD4", "APP123"]

    def test_list_from_response_resolves_includes(self, pre_release_versions_response):
        versions = PreReleaseVersion.list_from_response(pre_release_versions_response)

        assert [include.id for include in versions[0].includes] == ["BUILD3", "BUILD4", "APP123"]
        assert [include.id for include in versions[1].includes] == ["BUILD1"]

    def test_resolves_only_own_relationships(self, pre_release_versions_response):
        first, second = PreReleaseVersion.list_from_response(pre_release_versions_response)

        assert [build.version for build in first.builds] == ["56", "55"]
        assert [build.version for build in second.builds] == ["42"]

    def test_includes_are_parsed_into_their_models(self, pre_release_versions_response):
        version = PreReleaseVersion.list_from_response(pre_release_versions_response)[0]

        assert [type(include) for include in version.includes] == [Build, Build, App]

    def test_get_includes_filters_by_model(self, pre_release_versions_response):
        version = PreReleaseVersion.list_from_response(pre_release_versions_response)[0]

        apps = version.get_includes(App)

        assert len(apps) == 1
        assert apps[0].bundle_id == "com.example.app"

    def test_get_includes_returns_empty_list_for_absent_model(self, pre_release_versions_response):
        version = PreReleaseVersion.list_from_response(pre_release_versions_response)[1]

        assert version.get_includes(App) == []

    def test_empty_relationship_is_skipped(self, pre_release_versions_response):
        version = PreReleaseVersion.list_from_response(pre_release_versions_response)[1]

        assert version.get_includes(App) == []
        assert len(version.includes) == 1

    def test_unknown_included_types_are_skipped(self, pre_release_versions_response):
        versions = PreReleaseVersion.list_from_response(pre_release_versions_response)
        included_ids = [include.id for version in versions for include in version.includes]

        assert "UNKNOWN1" not in included_ids

    def test_response_without_included_section(self, apps_response):
        apps = App.list_from_response(apps_response)

        assert apps[0].includes == []

    def test_includes_are_dumped_as_their_own_model(self, pre_release_versions_response):
        version = PreReleaseVersion.list_from_response(pre_release_versions_response)[0]

        dumped = version.model_dump()

        assert dumped["version"] == "1.5.0"
        assert dumped["includes"][0]["version"] == "56"
        assert dumped["includes"][2]["bundle_id"] == "com.example.app"

    def test_every_model_is_registered_by_its_resource_type(self):
        assert _Resource.resource_models["apps"] is App
        assert _Resource.resource_models["appStoreVersions"] is AppStoreVersion
        assert _Resource.resource_models["builds"] is Build
        assert _Resource.resource_models["bundleIds"] is BundleID
        assert _Resource.resource_models["certificates"] is Certificate
        assert _Resource.resource_models["preReleaseVersions"] is PreReleaseVersion
        assert _Resource.resource_models["profiles"] is Profile


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
