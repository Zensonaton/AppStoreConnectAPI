# coding: utf-8

from ._base import BaseAPI
from .models import PreReleaseVersion


SORT_PRE_RELEASE_VERSION_VALUES = ["version", "-version"]
"""List of allowed values for sorting pre-release versions."""
FILTER_PRE_RELEASE_VERSION_PLATFORMS = ["IOS", "MAC_OS", "TV_OS", "VISION_OS"]
"""List of allowed values for filtering pre-release versions by platform."""
FILTER_BUILD_PROCESSING_STATES = ["PROCESSING", "FAILED", "INVALID", "VALID"]
"""List of allowed values for filtering pre-release versions by the processing state of their Builds."""
FILTER_BUILD_AUDIENCE_TYPES = ["INTERNAL_ONLY", "APP_STORE_ELIGIBLE"]
"""List of allowed values for filtering pre-release versions by the audience type of their Builds."""
INCLUDE_PRE_RELEASE_VERSION_VALUES = ["builds", "app"]
"""List of allowed values for including related resources of pre-release versions."""

class PreReleaseVersionsAPI(BaseAPI):
	"""
	Pre-release version-related API methods, i.e. the TestFlight versions of an App.

	:reference: https://developer.apple.com/documentation/appstoreconnectapi/prereleaseversion
	"""

	def retrieve(
		self,
		filter_app: str | None = None,
		sort: str | None = None,
		filter_version: str | None = None,
		filter_platform: str | None = None,
		filter_builds_expired: bool | None = None,
		filter_builds_processing_state: str | None = None,
		filter_builds_version: str | None = None,
		filter_builds_audience_type: str | None = None,
		include: list[str] | str = [],
		limit: int = 200,
		limit_builds: int | None = None
	) -> list[PreReleaseVersion]:
		"""
		Retrieve a list of pre-release (TestFlight) versions.

		:param filter_app: The resource ID of the App to filter the pre-release versions by
		:param sort: The attribute to sort the pre-release versions by (e.g. "-version")
		:param filter_version: The version string (e.g. "1.0.0") to filter the pre-release versions by
		:param filter_platform: The platform (e.g. "IOS") to filter the pre-release versions by
		:param filter_builds_expired: Whether the Builds of the pre-release versions are expired
		:param filter_builds_processing_state: The processing state (e.g. "VALID") of the Builds of the pre-release versions
		:param filter_builds_version: The build number (e.g. "42") of the Builds of the pre-release versions
		:param filter_builds_audience_type: The audience type (e.g. "APP_STORE_ELIGIBLE") of the Builds of the pre-release versions
		:param include: The related resources to include in the response (e.g. "builds")
		:param limit: The amount of pre-release versions to return (max 200)
		:param limit_builds: The amount of included Builds to return per pre-release version (max 50)
		:return: List of PreReleaseVersion objects
		"""

		params: dict = {
			"limit": limit
		}
		if filter_app:
			params["filter[app]"] = filter_app
		if sort:
			params["sort"] = self._validated_values_(sort, SORT_PRE_RELEASE_VERSION_VALUES, "sort")
		if filter_version:
			params["filter[version]"] = filter_version
		if filter_platform:
			params["filter[platform]"] = self._validated_values_(filter_platform, FILTER_PRE_RELEASE_VERSION_PLATFORMS, "platform")
		if filter_builds_expired is not None:
			params["filter[builds.expired]"] = "true" if filter_builds_expired else "false"
		if filter_builds_processing_state:
			params["filter[builds.processingState]"] = self._validated_values_(filter_builds_processing_state, FILTER_BUILD_PROCESSING_STATES, "build processing state")
		if filter_builds_version:
			params["filter[builds.version]"] = filter_builds_version
		if filter_builds_audience_type:
			params["filter[builds.buildAudienceType]"] = self._validated_values_(filter_builds_audience_type, FILTER_BUILD_AUDIENCE_TYPES, "build audience type")
		if include:
			params["include"] = self._validated_values_(include, INCLUDE_PRE_RELEASE_VERSION_VALUES, "include")
		if limit_builds:
			params["limit[builds]"] = limit_builds

		return PreReleaseVersion.list_from_response(
			self._client._api_get_("/preReleaseVersions", params)
		)
