"""API package for endpoint modules.

This package exposes the FastAPI `app` instance from :mod:`.app`
so importers can use the legacy target ``backend.api:app``.
"""

from .app import app  # re-export app for legacy import paths

__all__ = ["app"]
