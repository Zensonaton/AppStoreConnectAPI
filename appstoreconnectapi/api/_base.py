# coding: utf-8

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..client import AppStoreConnectClient


class BaseAPI:
	"""
	Base class for every API namespace (testflight, certificates, ...).

	Holds a reference back to the owning client so sub-clients can read
	the JWT token, issuer id, etc., and share a single authenticated session.
	"""

	def __init__(self, client: "AppStoreConnectClient") -> None:
		self._client = client

	@property
	def jwt_token(self) -> str:
		"""Convenience access to the client's current JWT token."""

		return self._client.jwt_token

	@staticmethod
	def _validated_values_(values: list[str] | str, allowed_values: list[str], name: str) -> str:
		"""
		Validates the given value(s) against the allowed ones, joining them the way the API expects.

		:param values: The value (or list of values) to validate
		:param allowed_values: List of the values allowed by the API
		:param name: The name of the query parameter, used in the error message (e.g. "sort")
		:return: The validated values, comma-separated
		"""

		if isinstance(values, str):
			values = [values]

		for value in values:
			if value in allowed_values:
				continue

			raise ValueError(f"Invalid {name} value: {value}. Allowed values are: {allowed_values}")

		return ",".join(values)
