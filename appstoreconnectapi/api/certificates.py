# coding: utf-8

from ._base import BaseAPI
from .models import Certificate


SORT_CERTIFICATE_VALUES = ["displayName", "-displayName", "certificateType", "-certificateType", "serialNumber", "-serialNumber", "id", "-id"]
"""List of allowed values for sorting certificates."""
FILTER_CERTIFICATE_TYPES = ["APPLE_PAY", "APPLE_PAY_MERCHANT_IDENTITY", "APPLE_PAY_PSP_IDENTITY", "APPLE_PAY_RSA", "DEVELOPER_ID_KEXT", "DEVELOPER_ID_KEXT_G2", "DEVELOPER_ID_APPLICATION", "DEVELOPER_ID_APPLICATION_G2", "DEVELOPMENT", "DISTRIBUTION", "IDENTITY_ACCESS", "IOS_DEVELOPMENT", "IOS_DISTRIBUTION", "MAC_APP_DISTRIBUTION", "MAC_INSTALLER_DISTRIBUTION", "MAC_APP_DEVELOPMENT", "PASS_TYPE_ID", "PASS_TYPE_ID_WITH_NFC"]
"""List of allowed values for filtering certificates by certificate type."""
FILTER_PASS_TYPE_IDS = ["name", "identifier", "certificates"]
"""List of allowed values for filtering certificates by pass type ID attributes."""

class CertificatesAPI(BaseAPI):
	"""
	Certificate-related API methods.

	:reference: https://developer.apple.com/documentation/appstoreconnectapi/certificate
	"""

	def retrieve(
		self,
		sort: str | None = None,
		filter_id: str | None = None,
		filter_serial_number: str | None = None,
		filter_certificate_type: str | None = None,
		filter_display_name: str | None = None,
		filter_pass_type_ids: str | None = None,
		every: bool = False
	) -> list[Certificate]:
		"""
		Retrieve a list of Certificates.

		:return: List of Certificate objects
		"""

		params: dict = {
			"limit": 200
		}
		if sort:
			if sort not in SORT_CERTIFICATE_VALUES:
				raise ValueError(f"Invalid sort value: {sort}. Allowed values are: {SORT_CERTIFICATE_VALUES}")

			params["sort"] = sort
		if filter_id:
			params["filter[id]"] = filter_id
		if filter_serial_number:
			params["filter[serialNumber]"] = filter_serial_number
		if filter_certificate_type:
			if filter_certificate_type not in FILTER_CERTIFICATE_TYPES:
				raise ValueError(f"Invalid certificate type: {filter_certificate_type}. Allowed values are: {FILTER_CERTIFICATE_TYPES}")

			params["filter[certificateType]"] = filter_certificate_type
		if filter_display_name:
			params["filter[displayName]"] = filter_display_name
		if filter_pass_type_ids:
			if filter_pass_type_ids not in FILTER_PASS_TYPE_IDS:
				raise ValueError(f"Invalid pass type IDs filter: {filter_pass_type_ids}. Allowed values are: {FILTER_PASS_TYPE_IDS}")

			params["filter[passTypeIds]"] = filter_pass_type_ids

		return [
			Certificate(**i) for i in self._client._api_get_("/certificates", params)
		]

	def delete(self, id: str) -> None:
		"""
		Delete a Certificate by its ID.

		:param id: The ID of the Certificate to delete
		"""

		self._client._api_delete_(f"/certificates/{id}")
