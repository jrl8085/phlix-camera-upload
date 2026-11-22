"""Phlix Camera Upload helper.

A small server that runs next to a Plex Media Server and receives the photos
and videos the Phlix app uploads from an iPhone or iPad, writing them into a
folder that a Plex photo library watches.

Only the Python standard library is used, so the whole program can be read in
one sitting and the Docker image needs nothing installed with pip.
"""

__version__ = "1.0.1"

#: Version of the HTTP API in `server.py`. The app refuses a helper whose
#: major API version it does not know, so raise it only for a breaking change.
API_VERSION = 1

#: Name the helper answers with on `/api/v1/hello`. The app looks for exactly
#: this string before it trusts that a port belongs to the helper.
SERVICE_NAME = "phlix-camera-upload"

#: Default TCP port: P-H-L-X on a phone keypad.
DEFAULT_PORT = 7459
