# coding: utf-8

"""
Example for requesting provisioning profile (or reusing existing one) for a given bundle ID and certificate.
If a profile with the same name, bundle ID and certificate(s) already exists, it will be returned instead of creating a new one.

Set the following environment variables before running:

    APP_STORE_KEY_ID		- API Key ID
    APP_STORE_ISSUER_ID		- API Issuer ID
    APP_STORE_PRIVATE_KEY 	- Path to API Private Key (.p8) file

Non-required environment variables:

	APP_STORE_PROFILE_NAME	- Name of the provisioning profile to create or reuse
	APP_STORE_BUNDLE_ID		- Bundle ID (e.g. "com.example.app") to associate the provisioning profile with
	APP_STORE_PROFILE_TYPE	- Type of the provisioning profile (e.g. "IOS_APP_STORE", "IOS_APP_DEVELOPMENT", etc.)

Run with:

    python3 examples/request_profile.py
"""

import os
import sys

from cryptography import x509

from appstoreconnectapi import AppStoreConnectClient
from appstoreconnectapi.api.models import Profile


def resolve_bundle_resource_id(client: AppStoreConnectClient, bundle_id: str) -> str:
	"""
	Return the resource ID of the registered Bundle ID, exiting if it isn't registered.
	"""

	bundle_ids = client.bundle_ids.retrieve(filter_identifier=bundle_id)
	if not bundle_ids:
		sys.exit(f"Bundle ID {bundle_id} isn't registered")

	bundle_resource_id = bundle_ids[0].id
	print(f"{bundle_resource_id} will be used as Bundle Resource ID.")

	return bundle_resource_id


def find_reusable_profile(client: AppStoreConnectClient, profile_name: str, profile_type: str) -> Profile | None:
	"""
	Return an existing, non-expired profile to reuse.

	If a matching profile exists but is expired, it is deleted so a fresh one can be created.
	Returns None when no reusable profile is available.
	"""

	profiles = client.profiles.retrieve(filter_name=profile_name, filter_profile_type=profile_type)
	if not profiles:
		print(f"No \"{profile_name}\" profile found, creating new one")

		return None

	profile = profiles[0]
	if profile.is_expired:
		print(f"Profile with ID {profile.id} is expired, renewing")
		client.profiles.delete(profile.id)

		return None

	return profile


def select_distribution_certificate(client: AppStoreConnectClient) -> str:
	"""
	Return the ID of the valid distribution certificate expiring soonest, exiting if none are valid.
	"""

	print("Distribution certificates:")
	certificates = client.certificates.retrieve(filter_certificate_type="DISTRIBUTION")
	for certificate in certificates:
		if certificate.is_valid:
			validity_str = f"valid for {certificate.days_until_expiration} days ({certificate.expiration_date.strftime('%Y-%m-%d')})"
		else:
			validity_str = "expired"

		attributes = certificate.x509_certificate.subject.get_attributes_for_oid(x509.NameOID.USER_ID)
		team_id = attributes[0].value if attributes else "<UNKNOWN>"

		print(f" - {certificate.name} ({certificate.id}, team {team_id}): {validity_str}")

	valid_certificates = sorted(
		(cert for cert in certificates if cert.is_valid),
		key=lambda cert: cert.expiration_date
	)
	if not valid_certificates:
		sys.exit("No valid distribution certificates found.")

	certificate_id = valid_certificates[0].id
	print(f"Certificate {certificate_id} will be used for provisioning profile.")

	return certificate_id


def main() -> None:
	bundle_id = os.environ.get("APP_STORE_BUNDLE_ID", "com.example.app")
	profile_type = os.environ.get("APP_STORE_PROFILE_TYPE", "IOS_APP_STORE")
	profile_name = os.environ.get("APP_STORE_PROFILE_NAME", f"Example profile for {bundle_id} ({profile_type})")

	client = AppStoreConnectClient.from_private_key_file(
		key_id=os.environ["APP_STORE_KEY_ID"],
		issuer_id=os.environ["APP_STORE_ISSUER_ID"],
		private_key_path=os.environ["APP_STORE_PRIVATE_KEY"]
	)

	bundle_resource_id = resolve_bundle_resource_id(client, bundle_id)

	profile = find_reusable_profile(client, profile_name, profile_type)
	if not profile:
		certificate_id = select_distribution_certificate(client)

		profile = client.profiles.create(
			name=profile_name,
			bundle_resource_id=bundle_resource_id,
			certificate_ids=certificate_id
		)

	filename = f"{profile_name}.mobileprovision"
	with open(filename, "wb") as provisioning:
		provisioning.write(profile.contents_as_bytes)

		print(f"Successfully created {filename}")


if __name__ == "__main__":
	main()
