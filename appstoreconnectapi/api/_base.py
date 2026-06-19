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
