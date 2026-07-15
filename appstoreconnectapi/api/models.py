# coding: utf-8

import base64
from datetime import datetime
from typing import Any, ClassVar, TypeVar

from cryptography import x509
from pydantic import BaseModel, ConfigDict, SerializeAsAny, model_validator
from pydantic.alias_generators import to_camel
from cryptography import x509
from cryptography.hazmat.backends import default_backend


_ResourceT = TypeVar("_ResourceT", bound="_Resource")
"""Type variable for any of the resource models."""

class _Resource(BaseModel):
	"""
	Base class for every resource model.

	Flattens Apple API's nested `attributes` dict into the model fields, and resolves
	the resources of the response's `included` section into the `includes` field.
	"""

	model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

	resource_type: ClassVar[str] = ""
	"""Apple API's `type` of the resource (e.g. "appStoreVersions")."""
	resource_models: ClassVar[dict[str, type["_Resource"]]] = {}
	"""Every known resource model, keyed by its `resource_type`."""

	id: str
	"""Resource ID of the resource."""
	includes: list[SerializeAsAny["_Resource"]] = []
	"""
	Related resources the API returned in the response's `included` section.

	Only gets filled if the request asked for them (e.g. `include=["builds"]`).
	Use `get_includes()` to retrieve the ones of a specific type.
	"""

	def __init_subclass__(cls, **kwargs: Any) -> None:
		super().__init_subclass__(**kwargs)

		if cls.resource_type:
			_Resource.resource_models[cls.resource_type] = cls

	@model_validator(mode="before")
	@classmethod
	def _flatten_attributes(cls, data: Any) -> Any:
		if isinstance(data, dict) and "attributes" in data:
			flat: dict = {"id": data.get("id")}
			flat.update(data["attributes"])

			return flat

		return data

	@classmethod
	def from_response(cls: type[_ResourceT], response: dict) -> _ResourceT:
		"""
		Builds a resource from an API response that holds a single resource.

		:param response: dict representing the JSON response
		:return: The resource, with its `includes` resolved
		"""

		return cls._from_data_(response["data"], cls._parse_included_(response))

	@classmethod
	def list_from_response(cls: type[_ResourceT], response: dict) -> list[_ResourceT]:
		"""
		Builds a list of resources from an API response that holds a list of resources.

		:param response: dict representing the JSON response
		:return: List of the resources, with their `includes` resolved
		"""

		included = cls._parse_included_(response)

		return [cls._from_data_(i, included) for i in response["data"]]

	def get_includes(self, model: type[_ResourceT]) -> list[_ResourceT]:
		"""
		Returns the included related resources of the given type.

		:param model: The resource model to look for (e.g. Build)
		:return: List of the included resources of that model
		"""

		return [include for include in self.includes if isinstance(include, model)]

	@classmethod
	def _from_data_(cls: type[_ResourceT], data: dict, included: dict[tuple[str, str], "_Resource"]) -> _ResourceT:
		"""
		Builds a resource from a single API resource object, linking it to the included resources it refers to.

		:param data: dict representing the API resource object
		:param included: The response's included resources, keyed by their type and ID
		:return: The resource, with its `includes` resolved
		"""

		resource = cls.model_validate(data)
		resource.includes = cls._linked_resources_(data.get("relationships", {}), included)

		return resource

	@staticmethod
	def _parse_included_(response: dict) -> dict[tuple[str, str], "_Resource"]:
		"""
		Parses the resources of the response's `included` section, keying them by their type and ID.

		Included resources of a type that has no model are skipped.

		:param response: dict representing the JSON response
		:return: The included resources, keyed by their type and ID
		"""

		included: dict[tuple[str, str], _Resource] = {}
		for item in response.get("included", []):
			model = _Resource.resource_models.get(item["type"])
			if not model:
				continue

			included[(item["type"], item["id"])] = model.model_validate(item)

		return included

	@staticmethod
	def _linked_resources_(relationships: dict, included: dict[tuple[str, str], "_Resource"]) -> list["_Resource"]:
		"""
		Returns the included resources that the given relationships refer to.

		:param relationships: dict representing the `relationships` section of an API resource object
		:param included: The response's included resources, keyed by their type and ID
		:return: List of the included resources the relationships refer to
		"""

		resources: list[_Resource] = []
		for relationship in relationships.values():
			# A relationship refers to either a single resource ("build") or a list of them ("builds").
			links = relationship.get("data") or []
			if isinstance(links, dict):
				links = [links]

			for link in links:
				resource = included.get((link["type"], link["id"]))
				if not resource:
					continue

				resources.append(resource)

		return resources


class App(_Resource):
	"""
	App resource model.
	"""

	resource_type: ClassVar[str] = "apps"

	name: str
	"""The name of the App."""
	bundle_id: str
	"""The bundle identifier string of the App (e.g. "com.example.app")."""
	sku: str | None = None
	"""The SKU of the App, if any."""
	primary_locale: str | None = None
	"""The primary locale of the App (e.g. "en-US"), if any."""
	is_or_ever_was_made_for_kids: bool | None = None
	"""Whether the App is (or ever was) a part of the Kids category, if known."""
	content_rights_declaration: str | None = None
	"""The content rights declaration of the App (e.g. "DOES_NOT_USE_THIRD_PARTY_CONTENT"), if any."""
	streamlined_purchasing_enabled: bool | None = None
	"""Whether the App has streamlined purchasing enabled, if known."""

class AppStoreVersion(_Resource):
	"""
	App Store version resource model, i.e. a version of an App that is (or was) published to the App Store.
	"""

	resource_type: ClassVar[str] = "appStoreVersions"

	version_string: str
	"""The version string of the App Store version (e.g. "1.0.0")."""
	platform: str | None = None
	"""The platform of the App Store version (e.g. "IOS"), if any."""
	app_version_state: str | None = None
	"""The state of the App Store version (e.g. "READY_FOR_DISTRIBUTION"), if any."""
	copyright: str | None = None
	"""The copyright of the App Store version, if any."""
	review_type: str | None = None
	"""The review type of the App Store version (e.g. "APP_STORE"), if any."""
	release_type: str | None = None
	"""The release type of the App Store version (e.g. "MANUAL"), if any."""
	earliest_release_date: datetime | None = None
	"""The earliest date the App Store version can be released at, if any."""
	downloadable: bool | None = None
	"""Whether the App Store version is downloadable, if known."""
	created_date: datetime | None = None
	"""The creation date of the App Store version, if any."""

	@property
	def build(self) -> "Build | None":
		"""
		The Build of the App Store version, if it was included in the response (i.e. `include=["build"]`).
		"""

		builds = self.get_includes(Build)

		return builds[0] if builds else None

class Build(_Resource):
	"""
	Build resource model.
	"""

	resource_type: ClassVar[str] = "builds"

	version: str
	"""The build number of the Build (e.g. "42")."""
	uploaded_date: datetime | None = None
	"""The upload date of the Build, if any."""
	expiration_date: datetime | None = None
	"""The expiration date of the Build, if any."""
	expired: bool | None = None
	"""Whether the Build is expired, if known."""
	min_os_version: str | None = None
	"""The minimal OS version the Build can be installed on (e.g. "16.0"), if any."""
	processing_state: str | None = None
	"""The processing state of the Build (e.g. "VALID"), if any."""
	build_audience_type: str | None = None
	"""The audience the Build is available to (e.g. "APP_STORE_ELIGIBLE"), if any."""
	uses_non_exempt_encryption: bool | None = None
	"""Whether the Build uses non-exempt encryption, if known."""

class BundleID(_Resource):
	"""
	Bundle ID resource model.
	"""

	resource_type: ClassVar[str] = "bundleIds"

	identifier: str
	"""The bundle identifier string (e.g. "com.example.app")."""
	name: str
	"""The name of the Bundle ID."""
	platform: str
	"""The platform for the Bundle ID (e.g. "iOS")."""
	seed_id: str | None = None
	"""The seed ID associated with the Bundle ID, if any."""

class Certificate(_Resource):
	"""
	Certificate resource model.
	"""

	resource_type: ClassVar[str] = "certificates"

	name: str
	"""The name of the Certificate."""
	display_name: str
	"""The display name of the Certificate."""
	certificate_type: str
	"""The type of the Certificate (e.g. "DISTRIBUTION")."""
	expiration_date: datetime
	"""The expiration date of the Certificate."""
	certificate_content: str
	"""The content of the Certificate, base64-encoded DER."""
	serial_number: str
	"""The serial number of the Certificate."""
	platform: str | None = None
	"""The platform associated with the Certificate, if any."""

	@property
	def days_until_expiration(self) -> int:
		"""
		The number of whole days until the Certificate expires (negative if already expired).
		"""

		now = datetime.now(self.expiration_date.tzinfo)

		return (self.expiration_date - now).days

	@property
	def is_expired(self) -> bool:
		"""
		Whether the Certificate has already expired.
		"""

		return self.days_until_expiration < 0

	@property
	def is_valid(self) -> bool:
		"""
		Whether the Certificate is still valid (i.e. not yet expired).
		"""

		return not self.is_expired

	@property
	def contents_as_bytes(self) -> bytes:
		"""
		The raw bytes of the Certificate content (DER format).
		"""

		return base64.b64decode(self.certificate_content)

	@property
	def x509_certificate(self) -> x509.Certificate:
		"""
		The Certificate content parsed as an x509.Certificate object.
		"""

		return x509.load_der_x509_certificate(self.contents_as_bytes, default_backend())

class PreReleaseVersion(_Resource):
	"""
	Pre-release version resource model, i.e. a TestFlight version of an App.
	"""

	resource_type: ClassVar[str] = "preReleaseVersions"

	version: str
	"""The version string of the pre-release version (e.g. "1.0.0")."""
	platform: str | None = None
	"""The platform of the pre-release version (e.g. "IOS"), if any."""

	@property
	def builds(self) -> list[Build]:
		"""
		The Builds of the pre-release version that were included in the response (i.e. `include=["builds"]`).
		"""

		return self.get_includes(Build)

class Profile(_Resource):
	"""
	Mobile Provisioning Profile resource model.
	"""

	resource_type: ClassVar[str] = "profiles"

	name: str
	"""The name of the Profile."""
	platform: str
	"""The platform for the Profile (e.g. "iOS")."""
	profile_type: str
	"""The type of the Profile (e.g. "IOS_APP_STORE")."""
	profile_state: str
	"""The state of the Profile (e.g. "ACTIVE")."""
	profile_content: str
	"""The content of the Profile, base64-encoded .mobileprovision file."""
	uuid: str
	"""The UUID of the Profile."""
	created_date: datetime
	"""The creation date of the Profile."""
	expiration_date: datetime
	"""The expiration date of the Profile."""

	@property
	def days_until_expiration(self) -> int:
		"""
		The number of whole days until the Profile expires (negative if already expired).
		"""

		now = datetime.now(self.expiration_date.tzinfo)

		return (self.expiration_date - now).days

	@property
	def is_expired(self) -> bool:
		"""
		Whether the Profile has already expired.
		"""

		return self.days_until_expiration < 0

	@property
	def is_valid(self) -> bool:
		"""
		Whether the Profile is still valid (i.e. not yet expired).
		"""

		return not self.is_expired

	@property
	def contents_as_bytes(self) -> bytes:
		"""
		The raw bytes of the Profile content (.mobileprovision format).
		"""

		return base64.b64decode(self.profile_content)
