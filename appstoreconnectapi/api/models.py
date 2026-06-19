# coding: utf-8

import base64
from datetime import datetime
from typing import Any

from cryptography import x509
from pydantic import BaseModel, ConfigDict, model_validator
from pydantic.alias_generators import to_camel
from cryptography import x509
from cryptography.hazmat.backends import default_backend


class _Resource(BaseModel):
	"""
	Flattens Apple API's nested `attributes` dict into the model fields.
	"""

	model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

	@model_validator(mode="before")
	@classmethod
	def _flatten_attributes(cls, data: Any) -> Any:
		if isinstance(data, dict) and "attributes" in data:
			flat: dict = {"id": data.get("id")}
			flat.update(data["attributes"])

			return flat

		return data


class BundleID(_Resource):
	"""
	Bundle ID resource model.
	"""

	id: str
	"""Resource ID of the Bundle ID."""
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

	id: str
	"""Resource ID of the Certificate."""
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

class Profile(_Resource):
	"""
	Mobile Provisioning Profile resource model.
	"""

	id: str
	"""Resource ID of the Profile."""
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
