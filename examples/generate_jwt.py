# coding: utf-8

"""
Generates a valid JWT from given input.

Set the following environment variables before running:

    APP_STORE_KEY_ID      - API Key ID
    APP_STORE_ISSUER_ID   - API Issuer ID
    APP_STORE_PRIVATE_KEY - Path to API Private Key (.p8) file

Run with:

    python3 examples/generate_jwt.py
"""

import os

from appstoreconnectapi import AppStoreConnectClient


def main() -> None:
	key_id = os.environ["APP_STORE_KEY_ID"]
	issuer_id = os.environ["APP_STORE_ISSUER_ID"]
	private_key_path = os.environ["APP_STORE_PRIVATE_KEY"]

	# Create an AppStoreConnectClient.
	client = AppStoreConnectClient.from_private_key_file(
		key_id=key_id,
		issuer_id=issuer_id,
		private_key_path=private_key_path
	)

	print(f"JWT token: \"{client.jwt_token}\"")

if __name__ == "__main__":
	main()
