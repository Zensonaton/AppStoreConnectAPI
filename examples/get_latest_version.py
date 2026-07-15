# coding: utf-8

"""
Example for getting the latest App Store and TestFlight (pre-release) version of an App.

Set the following environment variables before running:

    APP_STORE_KEY_ID      - API Key ID
    APP_STORE_ISSUER_ID   - API Issuer ID
    APP_STORE_PRIVATE_KEY - Path to API Private Key (.p8) file

Non-required environment variables:

    APP_STORE_BUNDLE_ID   - Bundle ID (e.g. "com.example.app") of the App to look up

Run with:

    python3 examples/latest_versions.py
"""

import os
import sys

from appstoreconnectapi import AppStoreConnectClient
from appstoreconnectapi.api.models import App


def resolve_app(client: AppStoreConnectClient, bundle_id: str) -> App:
	"""
	Returns the App Store application associated with given bundle_id.
	"""

	apps = client.apps.retrieve(
		filter_bundle_id=bundle_id,
		fields_apps="",
		limit=1
	)
	if not apps:
		sys.exit(f"No App found for bundle ID {bundle_id}")

	app = apps[0]
	print(f"{app.name} ({app.id}) will be used.")

	return app

def print_app_store_version(client: AppStoreConnectClient, app: App) -> None:
	"""
	Prints application version from App Store.
	"""

	versions = client.app_store_versions.retrieve(
		app.id,
		filter_platform="IOS",
		filter_app_version_state="READY_FOR_DISTRIBUTION",
		include="build",
		limit=1
	)
	if not versions:
		print("App Store: no version ready for distribution")

		return

	version = versions[0]
	build_number = version.build.version if version.build else "<UNKNOWN>"
	print(f"App Store: {version.version_string} (build {build_number})")

def print_testflight_version(client: AppStoreConnectClient, app: App) -> None:
	"""
	Prints application version from TestFlight (pre-release).
	"""

	versions = client.pre_release_versions.retrieve(
		filter_app=app.id,
		filter_platform="IOS",
		include="builds",
		limit=1,
		limit_builds=1
	)
	if not versions:
		print("TestFlight: no pre-release version found")

		return

	version = versions[0]
	build_number = version.builds[0].version if version.builds else "<UNKNOWN>"
	print(f"TestFlight: {version.version} (build {build_number})")


def main() -> None:
	bundle_id = os.environ.get("APP_STORE_BUNDLE_ID", "com.example.app")

	client = AppStoreConnectClient.from_private_key_file(
		key_id=os.environ["APP_STORE_KEY_ID"],
		issuer_id=os.environ["APP_STORE_ISSUER_ID"],
		private_key_path=os.environ["APP_STORE_PRIVATE_KEY"]
	)

	app = resolve_app(client, bundle_id)

	print_app_store_version(client, app)
	print_testflight_version(client, app)


if __name__ == "__main__":
	main()
