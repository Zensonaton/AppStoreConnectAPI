# coding: utf-8

import plistlib
from typing import cast


def read_mobileprovision_contents(contents_or_path: str | bytes) -> dict:
	"""
	Reads the contents of a .mobileprovision file and returns it as a dictionary.
	"""

	contents = contents_or_path
	if isinstance(contents_or_path, str):
		with open(contents_or_path, "rb") as f:
			contents = f.read()
	contents = cast(bytes, contents)

	start = contents.find(b'<?xml')
	end = contents.rfind(b'</plist>') + len(b'</plist>')

	return plistlib.loads(contents[start:end])
