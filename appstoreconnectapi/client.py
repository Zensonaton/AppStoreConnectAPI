# coding: utf-8

import time

import jwt
import requests

from appstoreconnectapi.consts import BASE_API_URL

from .api.app_store_versions import AppStoreVersionsAPI
from .api.apps import AppsAPI
from .api.bundle_ids import BundleIDsAPI
from .api.certificates import CertificatesAPI
from .api.pre_release_versions import PreReleaseVersionsAPI
from .api.profiles import ProfilesAPI


class AppStoreConnectClient:
	"""
	App Store Connect API client.
	"""

	key_id: str
	"""API Key ID"""
	issuer_id: str
	"""API Issuer ID"""
	private_key: bytes
	"""API Private Key (.p8) contents"""
	jwt_token: str
	"""JWT token for Apple Store Connect API authentication"""

	base_url: str
	"""Base URL for Apple Store Connect API"""
	http_client: requests.Session
	"""HTTP client session for making API requests"""

	apps: AppsAPI
	"""Apps API namespace"""
	app_store_versions: AppStoreVersionsAPI
	"""App Store versions API namespace"""
	bundle_ids: BundleIDsAPI
	"""Bundle IDs API namespace"""
	certificates: CertificatesAPI
	"""Certificates API namespace"""
	pre_release_versions: PreReleaseVersionsAPI
	"""Pre-release (TestFlight) versions API namespace"""
	profiles: ProfilesAPI
	"""Profiles API namespace"""

	def __init__(self, key_id: str, issuer_id: str, private_key_bytes: bytes) -> None:
		"""
		:param key_id: API Key ID
		:param issuer_id: API Issuer ID
		:param private_key_bytes: API Private Key (.p8) contents
		"""

		self.key_id = key_id
		self.issuer_id = issuer_id
		self.private_key = private_key_bytes
		self.jwt_token = self._create_jwt_token_(issuer_id, key_id, private_key_bytes)

		self.base_url = BASE_API_URL
		self.http_client = requests.Session()

		self.apps = AppsAPI(self)
		self.app_store_versions = AppStoreVersionsAPI(self)
		self.bundle_ids = BundleIDsAPI(self)
		self.certificates = CertificatesAPI(self)
		self.pre_release_versions = PreReleaseVersionsAPI(self)
		self.profiles = ProfilesAPI(self)

	@staticmethod
	def from_private_key_file(key_id: str, issuer_id: str, private_key_path: str) -> "AppStoreConnectClient":
		"""
		Creates AppStoreConnectClient from given private key file path.

		:param key_id: API Key ID
		:param issuer_id: API Issuer ID
		:param private_key_path: Path to API Private Key (.p8) file
		:return: AppStoreConnectClient instance
		"""

		with open(private_key_path, "rb") as f:
			private_key_bytes = f.read()

		return AppStoreConnectClient(key_id, issuer_id, private_key_bytes)

	def _api_http_headers_(self) -> dict:
		"""
		Returns HTTP headers for API requests.

		:return: dict with HTTP headers
		"""

		return {
			"Authorization": f"Bearer {self.jwt_token}",
			"Content-Type": "application/json",
		}

	def _api_request_(self, method: str, path: str, params: dict = {}, data: dict | None = None) -> dict:
		"""
		Performs a request to Apple Store Connect API.

		:param method: HTTP method (e.g. "GET", "POST", "DELETE")
		:param path: API endpoint path that comes after the base URL (e.g. "/testflight/betaTesters")
		:param params: dict representing the query parameters, if any
		:param data: dict representing the JSON payload, if any
		:return: dict representing the JSON response
		"""

		response = self.http_client.request(
			method,
			f"{self.base_url}{path}",
			json=data,
			params=params,
			headers=self._api_http_headers_(),
		)
		json = response.json()
		if not isinstance(json, dict):
			raise ValueError("Expected JSON response to be a dict")

		errors = json.get("errors")
		if errors:
			error = errors[0]

			# TODO(Zensonaton): Implement custom Exception type
			raise Exception(
				f"{error['code']}: {error['title']}\n"
				f"{error['detail']}"
			)

		return json

	def _api_get_(self, path: str, params: dict = {}) -> dict:
		"""
		Performs a GET request to Apple Store Connect API.

		:param path: API endpoint path that comes after the base URL (e.g. "/testflight/betaTesters")
		:param params: dict representing the query parameters, if any
		:return: dict representing the JSON response
		"""

		return self._api_request_("GET", path, params)

	def _api_post_(self, path: str, params: dict = {}, data: dict = {}) -> dict:
		"""
		Performs a POST request to Apple Store Connect API.

		:param path: API endpoint path that comes after the base URL (e.g. "/testflight/betaTesters")
		:param data: dict representing the JSON payload
		:param params: dict representing the query parameters, if any
		:return: dict representing the JSON response
		"""

		return self._api_request_("POST", path, params, data)

	def _api_delete_(self, path: str, params: dict = {}) -> dict:
		"""
		Performs a DELETE request to Apple Store Connect API.

		:param path: API endpoint path that comes after the base URL (e.g. "/testflight/betaTesters")
		:param params: dict representing the query parameters, if any
		:return: dict representing the JSON response
		"""

		return self._api_request_("DELETE", path, params)

	@staticmethod
	def _jwt_header_(key_id: str) -> dict:
		"""
		Initializes JWT token header for Apple Store Connect.

		:param key_id: API Key ID
		:return: dict for JWT token header
		"""

		return {
			"kid": key_id,
			"typ": "JWT",
		}

	@staticmethod
	def _jwt_payload_(issuer_id: str, ttl: int = 1200) -> dict:
		"""
		Initializes JWT token payload for Apple Store Connect.

		:param issuer_id: API Issuer ID
		:param ttl: Expiration time in seconds (max 1200)
		:return: dict for JWT token payload
		"""

		now = int(time.time())
		if ttl > 1200:
			raise ValueError("Time to live (ttl) can't be more than 1200 seconds (20 minutes)")

		return {
			"iss": issuer_id,
			"iat": now,
			"exp": now + ttl,
			"aud": "appstoreconnect-v1",
		}

	@staticmethod
	def _create_jwt_token_(issuer_id: str, key_id: str, private_key_contents_or_path: str | bytes) -> str:
		"""
		Returns a JWT token for Apple Store Connect.

		:param issuer_id: API Issuer ID
		:param key_id: API Key ID
		:param private_key_contents_or_path: API Private Key (.p8) contents or path
		"""

		header = AppStoreConnectClient._jwt_header_(key_id)
		payload = AppStoreConnectClient._jwt_payload_(issuer_id)

		private_key = private_key_contents_or_path
		if isinstance(private_key_contents_or_path, str):
			with open(private_key_contents_or_path, "r") as f:
				private_key = f.read()

		return jwt.encode(
			payload=payload,
			key=private_key,
			algorithm="ES256",
			headers=header,
		)
