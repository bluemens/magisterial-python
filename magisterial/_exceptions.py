# Exception hierarchy for the Magisterial SDK.
#
# Every non-2xx API response raises an APIStatusError subclass carrying the
# parsed `{"error": {"type", "code", "message"}}` envelope. Transport-level
# failures (DNS, TLS, timeouts) raise APIConnectionError / APITimeoutError.

from __future__ import annotations

from typing import Any, Optional

import httpx


class MagisterialError(Exception):
    """Base class for every error raised by this SDK."""


class APIConnectionError(MagisterialError):
    """The request never produced an HTTP response (network/TLS failure)."""

    def __init__(self, message: str = "Connection error.") -> None:
        super().__init__(message)


class APITimeoutError(APIConnectionError):
    """The request timed out."""

    def __init__(self) -> None:
        super().__init__("Request timed out.")


class QueryPollTimeout(MagisterialError):
    """create_and_poll gave up before the query run reached a terminal state.

    The run keeps executing server-side; fetch it later with
    ``client.query.get(run_id)``.
    """

    def __init__(self, run_id: str, last_status: str, timeout: float) -> None:
        self.run_id = run_id
        self.last_status = last_status
        super().__init__(
            f"Query run {run_id} still '{last_status}' after {timeout:.0f}s; "
            f"poll client.query.get({run_id!r}) to retrieve it later."
        )


class APIStatusError(MagisterialError):
    """A non-2xx response from the API."""

    def __init__(self, response: httpx.Response) -> None:
        self.response = response
        self.status_code = response.status_code
        self.body: Any = None
        self.error_type: Optional[str] = None
        self.error_code: Optional[str] = None
        message = f"HTTP {self.status_code}"
        try:
            self.body = response.json()
        except Exception:
            message = response.text or message
        if isinstance(self.body, dict):
            err = self.body.get("error")
            if isinstance(err, dict):
                self.error_type = err.get("type")
                self.error_code = err.get("code")
                message = err.get("message") or message
            elif "detail" in self.body:  # FastAPI 422 validation shape
                message = f"Request validation failed: {self.body['detail']}"
        super().__init__(message)

    @property
    def retry_after(self) -> Optional[float]:
        value = self.response.headers.get("Retry-After")
        try:
            return float(value) if value is not None else None
        except ValueError:
            return None


class BadRequestError(APIStatusError):
    """400 — invalid scope, cursor, or parameter."""


class AuthenticationError(APIStatusError):
    """401 — missing, malformed, or revoked API key."""


class BillingError(APIStatusError):
    """402 — API billing not enabled, or the monthly budget is exhausted."""


class PermissionDeniedError(APIStatusError):
    """403 — the account may not perform this action (e.g. alert limit)."""


class NotFoundError(APIStatusError):
    """404 — no such resource in the requested scope."""


class UnprocessableEntityError(APIStatusError):
    """422 — the request body failed validation."""


class RateLimitError(APIStatusError):
    """429 — rate limit exceeded; honor ``retry_after`` before retrying."""


class InternalServerError(APIStatusError):
    """5xx — server-side failure."""


_STATUS_TO_ERROR = {
    400: BadRequestError,
    401: AuthenticationError,
    402: BillingError,
    403: PermissionDeniedError,
    404: NotFoundError,
    422: UnprocessableEntityError,
    429: RateLimitError,
}


def error_from_response(response: httpx.Response) -> APIStatusError:
    if response.status_code >= 500:
        return InternalServerError(response)
    cls = _STATUS_TO_ERROR.get(response.status_code, APIStatusError)
    return cls(response)
