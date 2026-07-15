# coding: utf-8

import pytest

from appstoreconnectapi.api.models import App, AppStoreVersion, Build, PreReleaseVersion


class TestAppsAPI:
    def test_retrieves_apps(self, client, mock_api, apps_response):
        mock_api(apps_response)

        apps = client.apps.retrieve()

        assert len(apps) == 1
        assert isinstance(apps[0], App)
        assert apps[0].id == "APP123"
        assert apps[0].bundle_id == "com.example.app"

    def test_sends_expected_request(self, client, mock_api, apps_response):
        request = mock_api(apps_response)

        client.apps.retrieve(
            sort="name",
            filter_bundle_id="com.example.app",
            include=["appStoreVersions", "preReleaseVersions"],
            limit=10,
        )

        args, kwargs = request.call_args
        assert args[0] == "GET"
        assert args[1] == f"{client.base_url}/apps"
        assert kwargs["params"] == {
            "limit": 10,
            "sort": "name",
            "filter[bundleId]": "com.example.app",
            "include": "appStoreVersions,preReleaseVersions",
        }

    def test_raises_on_invalid_sort(self, client, mock_api, apps_response):
        mock_api(apps_response)

        with pytest.raises(ValueError, match="Invalid sort value: platform"):
            client.apps.retrieve(sort="platform")

    def test_raises_on_invalid_include(self, client, mock_api, apps_response):
        mock_api(apps_response)

        with pytest.raises(ValueError, match="Invalid include value: certificates"):
            client.apps.retrieve(include=["appStoreVersions", "certificates"])


class TestAppStoreVersionsAPI:
    def test_retrieves_versions_with_their_builds(self, client, mock_api, app_store_versions_response):
        mock_api(app_store_versions_response)

        versions = client.app_store_versions.retrieve("APP123", include="build")

        assert [version.version_string for version in versions] == ["1.4.0", "1.3.0"]
        assert isinstance(versions[0], AppStoreVersion)
        assert isinstance(versions[0].build, Build)
        assert versions[0].build.version == "42"
        assert versions[1].build is not None and versions[1].build.version == "37"

    def test_sends_expected_request(self, client, mock_api, app_store_versions_response):
        request = mock_api(app_store_versions_response)

        client.app_store_versions.retrieve(
            "APP123",
            filter_platform="IOS",
            filter_app_version_state=["READY_FOR_DISTRIBUTION", "IN_REVIEW"],
            include="build",
            limit=1,
        )

        args, kwargs = request.call_args
        assert args[0] == "GET"
        assert args[1] == f"{client.base_url}/apps/APP123/appStoreVersions"
        assert kwargs["params"] == {
            "limit": 1,
            "filter[platform]": "IOS",
            "filter[appVersionState]": "READY_FOR_DISTRIBUTION,IN_REVIEW",
            "include": "build",
        }

    def test_raises_on_invalid_platform(self, client, mock_api, app_store_versions_response):
        mock_api(app_store_versions_response)

        with pytest.raises(ValueError, match="Invalid platform value: ANDROID"):
            client.app_store_versions.retrieve("APP123", filter_platform="ANDROID")

    def test_raises_on_invalid_app_version_state(self, client, mock_api, app_store_versions_response):
        mock_api(app_store_versions_response)

        with pytest.raises(ValueError, match="Invalid app version state value: READY_FOR_SALE"):
            client.app_store_versions.retrieve("APP123", filter_app_version_state="READY_FOR_SALE")


class TestPreReleaseVersionsAPI:
    def test_retrieves_versions_with_their_builds(self, client, mock_api, pre_release_versions_response):
        mock_api(pre_release_versions_response)

        versions = client.pre_release_versions.retrieve("APP123", include="builds")

        assert [version.version for version in versions] == ["1.5.0", "1.4.0"]
        assert isinstance(versions[0], PreReleaseVersion)
        assert [build.version for build in versions[0].builds] == ["56", "55"]
        assert [build.version for build in versions[1].builds] == ["42"]

    def test_sends_expected_request(self, client, mock_api, pre_release_versions_response):
        request = mock_api(pre_release_versions_response)

        client.pre_release_versions.retrieve(
            "APP123",
            sort="-version",
            filter_platform="IOS",
            filter_builds_processing_state="VALID",
            filter_builds_audience_type="APP_STORE_ELIGIBLE",
            include=["builds", "app"],
            limit=1,
            limit_builds=50,
        )

        args, kwargs = request.call_args
        assert args[0] == "GET"
        assert args[1] == f"{client.base_url}/apps/APP123/preReleaseVersions"
        assert kwargs["params"] == {
            "limit": 1,
            "sort": "-version",
            "filter[platform]": "IOS",
            "filter[builds.processingState]": "VALID",
            "filter[builds.buildAudienceType]": "APP_STORE_ELIGIBLE",
            "include": "builds,app",
            "limit[builds]": 50,
        }

    @pytest.mark.parametrize("expired, expected", [(True, "true"), (False, "false")])
    def test_sends_builds_expired_filter_as_string(self, client, mock_api, pre_release_versions_response, expired, expected):
        request = mock_api(pre_release_versions_response)

        client.pre_release_versions.retrieve("APP123", filter_builds_expired=expired)

        _, kwargs = request.call_args
        assert kwargs["params"]["filter[builds.expired]"] == expected

    def test_omits_builds_expired_filter_by_default(self, client, mock_api, pre_release_versions_response):
        request = mock_api(pre_release_versions_response)

        client.pre_release_versions.retrieve("APP123")

        _, kwargs = request.call_args
        assert "filter[builds.expired]" not in kwargs["params"]

    def test_raises_on_invalid_sort(self, client, mock_api, pre_release_versions_response):
        mock_api(pre_release_versions_response)

        with pytest.raises(ValueError, match="Invalid sort value: -createdDate"):
            client.pre_release_versions.retrieve("APP123", sort="-createdDate")


class TestExistingAPIsParseResponses:
    """
    The API namespaces that predate the `includes` support parse the full JSON response as well.
    """

    def test_bundle_ids_retrieve(self, client, mock_api, bundle_id_payload):
        mock_api({"data": [bundle_id_payload]})

        bundle_ids = client.bundle_ids.retrieve()

        assert [bundle.id for bundle in bundle_ids] == ["ABC123"]

    def test_certificates_retrieve(self, client, mock_api, certificate_payload):
        mock_api({"data": [certificate_payload]})

        certificates = client.certificates.retrieve()

        assert [certificate.id for certificate in certificates] == ["CERT123"]

    def test_profiles_retrieve(self, client, mock_api, profile_payload):
        mock_api({"data": [profile_payload]})

        profiles = client.profiles.retrieve()

        assert [profile.id for profile in profiles] == ["PROF123"]

    def test_profiles_create(self, client, mock_api, profile_payload):
        mock_api({"data": profile_payload})

        profile = client.profiles.create("AppStore Profile", "BUNDLE1", "CERT123")

        assert profile.id == "PROF123"
        assert profile.name == "AppStore Profile"
