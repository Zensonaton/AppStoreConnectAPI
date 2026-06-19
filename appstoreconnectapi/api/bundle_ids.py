# coding: utf-8

from ._base import BaseAPI
from .models import BundleID


SORT_BUNDLE_ID_VALUES = ["name", "-name", "platform", "-platform", "identifier", "-identifier", "seedId", "-seedId", "id", "-id"]
"""List of allowed values for sorting Bundle IDs."""
FILTER_BUNDLE_ID_PLATFORMS = ["IOS", "MAC_OS", "UNIVERSAL"]
"""List of allowed values for filtering Bundle IDs by platform."""

class BundleIDsAPI(BaseAPI):
	"""
	Bundle ID-related API methods.

	:reference: https://developer.apple.com/documentation/appstoreconnectapi/bundleid
	"""

	def retrieve(
		self,
		sort: str | None = None,
		filter_id: str | None = None,
		filter_identifier: str | None = None,
		filter_name: str | None = None,
		filter_platform: str | None = None,
		filter_seed_id: str | None = None,
		every: bool = False
	) -> list[BundleID]:
		"""
		Retrieve a list of Bundle IDs.

		:return: List of BundleID objects
		"""

		params: dict = {
			"limit": 200
		}
		if sort:
			if sort not in SORT_BUNDLE_ID_VALUES:
				raise ValueError(f"Invalid sort value: {sort}. Allowed values are: {SORT_BUNDLE_ID_VALUES}")

			params["sort"] = sort
		if filter_id:
			params["filter[id]"] = filter_id
		if filter_identifier:
			params["filter[identifier]"] = filter_identifier
		if filter_name:
			params["filter[name]"] = filter_name
		if filter_platform:
			if filter_platform not in FILTER_BUNDLE_ID_PLATFORMS:
				raise ValueError(f"Invalid platform: {filter_platform}. Allowed values are: {FILTER_BUNDLE_ID_PLATFORMS}")

			params["filter[platform]"] = filter_platform
		if filter_seed_id:
			params["filter[seedId]"] = filter_seed_id

		return [
			BundleID(**i) for i in self._client._api_get_("/bundleIds", params)
		]
