# coding: utf-8

from ._base import BaseAPI
from .models import Profile


SORT_PROFILE_VALUES = ["name", "-name", "profileType", "-profileType", "profileState", "-profileState", "id", "-id"]
"""List of allowed values for sorting profiles."""
FILTER_PROFILE_STATES = ["ACTIVE", "INACTIVE"]
"""List of allowed values for filtering profiles by profile state."""
FILTER_PROFILE_TYPES = ["IOS_APP_DEVELOPMENT", "IOS_APP_STORE", "IOS_APP_ADHOC", "IOS_APP_INHOUSE", "MAC_APP_DEVELOPMENT", "MAC_APP_STORE", "MAC_APP_DIRECT", "TVOS_APP_DEVELOPMENT", "TVOS_APP_STORE", "TVOS_APP_ADHOC", "TVOS_APP_INHOUSE", "MAC_CATALYST_APP_DEVELOPMENT", "MAC_CATALYST_APP_STORE", "MAC_CATALYST_APP_DIRECT"]
"""List of allowed values for filtering profiles by profile type."""

class ProfilesAPI(BaseAPI):
	"""
	Mobile Provisioning profiles-related API methods.

	:reference: https://developer.apple.com/documentation/appstoreconnectapi/profile
	"""

	def create(self, name: str, bundle_resource_id: str, certificate_ids: list[str] | str) -> Profile:
		"""
		Requests the creation of a new Profile.

		:param name: The name of the Profile to create
		:param bundle_resource_id: The resource ID of the Bundle ID associated with the Profile
		:param certificate_ids: A list of resource IDs of the Certificates to include in the Profile
		:return: The created Profile object
		"""

		if isinstance(certificate_ids, str):
			certificate_ids = [certificate_ids]

		response = self._client._api_post_(
			"/profiles",
			data={
				"data": {
					"type": "profiles",
					"attributes": {
						"name": name,
						"profileType": "IOS_APP_STORE",
					},
					"relationships": {
						"bundleId": {
							"data": {
								"type": "bundleIds",
								"id": bundle_resource_id,
							}
						},
						"certificates": {
							"data": [
								{"type": "certificates", "id": certificate_id} for certificate_id in certificate_ids
							]
						}
					}
				}
			}
		)

		return Profile.from_response(response)

	def retrieve(
		self,
		sort: str | None = None,
		filter_id: str | None = None,
		filter_name: str | None = None,
		filter_profile_state: str | None = None,
		filter_profile_type: list | str = [],
		every: bool = False
	) -> list[Profile]:
		"""
		Retrieve a list of Profiles.

		:return: List of Profile objects
		"""

		if isinstance(filter_profile_type, str):
			filter_profile_type = [filter_profile_type]

		params: dict = {
			"limit": 200
		}
		if sort:
			if sort not in SORT_PROFILE_VALUES:
				raise ValueError(f"Invalid sort value: {sort}. Allowed values are: {SORT_PROFILE_VALUES}")

			params["sort"] = sort
		if filter_id:
			params["filter[id]"] = filter_id
		if filter_name:
			params["filter[name]"] = filter_name
		if filter_profile_state:
			if filter_profile_state not in FILTER_PROFILE_STATES:
				raise ValueError(f"Invalid profile state: {filter_profile_state}. Allowed values are: {FILTER_PROFILE_STATES}")

			params["filter[profileState]"] = filter_profile_state
		if filter_profile_type:
			for profile_type in filter_profile_type:
				if profile_type in FILTER_PROFILE_TYPES:
					continue

				raise ValueError(f"Invalid profile type: {profile_type}. Allowed values are: {FILTER_PROFILE_TYPES}")

			params["filter[profileType]"] = ",".join(filter_profile_type)

		return Profile.list_from_response(self._client._api_get_("/profiles", params=params))

	def delete(self, id: str) -> None:
		"""
		Deletes a Profile by its ID.

		:param id: The ID of the Profile to delete
		"""

		self._client._api_delete_(f"/profiles/{id}")
