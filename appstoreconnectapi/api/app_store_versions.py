# coding: utf-8

from ._base import BaseAPI
from .models import AppStoreVersion


FILTER_APP_STORE_VERSION_PLATFORMS = ["IOS", "MAC_OS", "TV_OS", "VISION_OS"]
"""List of allowed values for filtering App Store versions by platform."""
FILTER_APP_STORE_VERSION_STATES = ["ACCEPTED", "DEVELOPER_REJECTED", "IN_REVIEW", "INVALID_BINARY", "METADATA_REJECTED", "PENDING_APPLE_RELEASE", "PENDING_DEVELOPER_RELEASE", "PREPARE_FOR_SUBMISSION", "PROCESSING_FOR_DISTRIBUTION", "READY_FOR_DISTRIBUTION", "READY_FOR_REVIEW", "REJECTED", "REPLACED_WITH_NEW_VERSION", "WAITING_FOR_EXPORT_COMPLIANCE", "WAITING_FOR_REVIEW"]
"""List of allowed values for filtering App Store versions by their state."""
INCLUDE_APP_STORE_VERSION_VALUES = ["app", "appStoreVersionLocalizations", "build", "appStoreVersionPhasedRelease", "gameCenterAppVersion", "routingAppCoverage", "appStoreReviewDetail", "appStoreVersionSubmission", "appClipDefaultExperience", "appStoreVersionExperiments", "appStoreVersionExperimentsV2", "alternativeDistributionPackage"]
"""List of allowed values for including related resources of App Store versions."""

class AppStoreVersionsAPI(BaseAPI):
	"""
	App Store version-related API methods, i.e. the versions of an App that are (or were) published to the App Store.

	:reference: https://developer.apple.com/documentation/appstoreconnectapi/appstoreversion
	"""

	def retrieve(
		self,
		app_id: str,
		filter_id: str | None = None,
		filter_version_string: str | None = None,
		filter_platform: str | None = None,
		filter_app_version_state: list[str] | str = [],
		include: list[str] | str = [],
		limit: int = 200
	) -> list[AppStoreVersion]:
		"""
		Retrieve a list of App Store versions of an App, newest first.

		:param app_id: The resource ID of the App to retrieve the App Store versions of
		:param filter_id: The resource ID of the App Store version to filter by
		:param filter_version_string: The version string (e.g. "1.0.0") to filter the App Store versions by
		:param filter_platform: The platform (e.g. "IOS") to filter the App Store versions by
		:param filter_app_version_state: The state (e.g. "READY_FOR_DISTRIBUTION") to filter the App Store versions by
		:param include: The related resources to include in the response (e.g. "build")
		:param limit: The amount of App Store versions to return (max 200)
		:return: List of AppStoreVersion objects
		"""

		params: dict = {
			"limit": limit
		}
		if filter_id:
			params["filter[id]"] = filter_id
		if filter_version_string:
			params["filter[versionString]"] = filter_version_string
		if filter_platform:
			params["filter[platform]"] = self._validated_values_(filter_platform, FILTER_APP_STORE_VERSION_PLATFORMS, "platform")
		if filter_app_version_state:
			params["filter[appVersionState]"] = self._validated_values_(filter_app_version_state, FILTER_APP_STORE_VERSION_STATES, "app version state")
		if include:
			params["include"] = self._validated_values_(include, INCLUDE_APP_STORE_VERSION_VALUES, "include")

		return AppStoreVersion.list_from_response(self._client._api_get_(f"/apps/{app_id}/appStoreVersions", params))
