# Magisterial — official Python SDK for the Magisterial developer API.
# Docs: https://api.magisterial.ai/v1/docs   Spec: https://api.magisterial.ai/v1/openapi.json

from . import types
from ._client import AsyncMagisterial, Magisterial
from ._exceptions import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    BillingError,
    ExportPollTimeout,
    InternalServerError,
    MagisterialError,
    NotFoundError,
    PermissionDeniedError,
    QueryPollTimeout,
    RateLimitError,
    UnprocessableEntityError,
)
from ._pagination import AsyncPage, SyncPage
from ._version import __version__

__all__ = [
    "Magisterial",
    "AsyncMagisterial",
    "SyncPage",
    "AsyncPage",
    "types",
    "MagisterialError",
    "APIConnectionError",
    "APITimeoutError",
    "APIStatusError",
    "BadRequestError",
    "AuthenticationError",
    "BillingError",
    "PermissionDeniedError",
    "NotFoundError",
    "UnprocessableEntityError",
    "RateLimitError",
    "InternalServerError",
    "QueryPollTimeout",
    "ExportPollTimeout",
    "__version__",
]
