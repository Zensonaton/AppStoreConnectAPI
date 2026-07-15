# coding: utf-8

from ._base import BaseAPI
from .models import App


SORT_APP_VALUES = ["name", "-name", "bundleId", "-bundleId", "sku", "-sku"]
"""List of allowed values for sorting Apps."""
INCLUDE_APP_VALUES = ["appEncryptionDeclarations", "appStoreIcon", "ciProduct", "betaGroups", "appStoreVersions", "preReleaseVersions", "betaAppLocalizations", "builds", "betaLicenseAgreement", "betaAppReviewDetail", "appInfos", "appClips", "endUserLicenseAgreement", "inAppPurchases", "subscriptionGroups", "gameCenterEnabledVersions", "appCustomProductPages", "inAppPurchasesV2", "promotedPurchases", "appEvents", "reviewSubmissions", "subscriptionGracePeriod", "gameCenterDetail", "appStoreVersionExperimentsV2", "androidToIosAppMappingDetails"]
"""List of allowed values for including related resources of Apps."""

class AppsAPI(BaseAPI):
	"""
	App-related API methods.

	:reference: https://developer.apple.com/documentation/appstoreconnectapi/app
	"""

	def retrieve(
		self,
		sort: str | None = None,
		filter_id: str | None = None,
		filter_bundle_id: str | None = None,
		filter_name: str | None = None,
		filter_sku: str | None = None,
		include: list[str] | str = [],
		limit: int = 200
	) -> list[App]:
		"""
		Retrieve a list of Apps.

		:param sort: The attribute to sort the Apps by (e.g. "name")
		:param filter_id: The resource ID of the App to filter by
		:param filter_bundle_id: The bundle identifier string (e.g. "com.example.app") to filter the Apps by
		:param filter_name: The name of the App to filter by
		:param filter_sku: The SKU of the App to filter by
		:param include: The related resources to include in the response (e.g. "appStoreVersions")
		:param limit: The amount of Apps to return (max 200)
		:return: List of App objects
		"""

		params: dict = {
			"limit": limit
		}
		if sort:
			params["sort"] = self._validated_values_(sort, SORT_APP_VALUES, "sort")
		if filter_id:
			params["filter[id]"] = filter_id
		if filter_bundle_id:
			params["filter[bundleId]"] = filter_bundle_id
		if filter_name:
			params["filter[name]"] = filter_name
		if filter_sku:
			params["filter[sku]"] = filter_sku
		if include:
			params["include"] = self._validated_values_(include, INCLUDE_APP_VALUES, "include")

		return App.list_from_response(self._client._api_get_("/apps", params))
