# coding: utf-8

"""
Basic usage example for the App Store Connect API client.

Set the following environment variables before running:

    APP_STORE_KEY_ID      - API Key ID
    APP_STORE_ISSUER_ID   - API Issuer ID
    APP_STORE_PRIVATE_KEY - Path to API Private Key (.p8) file

Run with:

    python3 examples/basic_usage.py
"""

import os

from appstoreconnectapi import AppStoreConnectClient


def main() -> None:
	key_id = os.environ["APP_STORE_KEY_ID"]
	issuer_id = os.environ["APP_STORE_ISSUER_ID"]
	private_key_path = os.environ["APP_STORE_PRIVATE_KEY"]

	# AppStoreConnectClient can be either created with "raw" key bytes:
	with open(private_key_path, "rb") as key:
		client = AppStoreConnectClient(
			key_id=key_id,
			issuer_id=issuer_id,
			private_key_bytes=key.read()
		)

	# ...or via helper method from_private_key_file that loads key file by itself:
	client = AppStoreConnectClient.from_private_key_file(
		key_id=key_id,
		issuer_id=issuer_id,
		private_key_path=private_key_path
	)

	print("Authenticated. JWT token (truncated):", client.jwt_token[:32], "...")

	bundle_ids = client.bundle_ids.retrieve()
	print("Bundle IDs:")
	for bundle in bundle_ids:
		print(f"\t- {bundle.name} ({bundle.id})")

	certificates = client.certificates.retrieve()
	print("Certificates:")
	for certificate in certificates:
		print(f"\t- {certificate.name} ({certificate.id})")

	profiles = client.profiles.retrieve()
	print("Profiles:")
	for profile in profiles:
		print(f"\t- {profile.name} ({profile.id})")

if __name__ == "__main__":
	main()
