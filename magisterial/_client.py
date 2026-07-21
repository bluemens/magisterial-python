# The Magisterial client core: auth, transport, retries, and JSON<->model
# plumbing shared by every resource namespace. Public entry points are
# ``Magisterial`` (sync) and ``AsyncMagisterial``.

from __future__ import annotations

import os
import random
from typing import Any, Dict, Mapping, Optional, Type, TypeVar

import httpx
from pydantic import BaseModel

from ._exceptions import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    MagisterialError,
    error_from_response,
)
from ._version import __version__

M = TypeVar("M", bound=BaseModel)

DEFAULT_BASE_URL = "https://api.magisterial.ai"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2

# Methods safe to retry unconditionally. POSTs are retried only when the
# caller opts in (search is a read; query/alert creates are billable).
_IDEMPOTENT_METHODS = {"GET", "DELETE"}


def _clean_params(params: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    return {k: v for k, v in (params or {}).items() if v is not None}


class _ClientConfig:
    def __init__(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        timeout: float,
        max_retries: int,
    ) -> None:
        self.api_key = api_key or os.environ.get("MAGISTERIAL_API_KEY")
        if not self.api_key:
            raise MagisterialError(
                "No API key provided. Pass api_key=... or set the "
                "MAGISTERIAL_API_KEY environment variable. Create keys at "
                "https://magisterial.ai/console/api-keys"
            )
        self.base_url = (
            base_url
            or os.environ.get("MAGISTERIAL_BASE_URL")
            or DEFAULT_BASE_URL
        ).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": f"magisterial-python/{__version__}",
        }


def _retry_delay(response: Optional[httpx.Response], attempt: int) -> float:
    """Seconds to sleep before retry `attempt` (0-based), honoring Retry-After."""
    if response is not None:
        header = response.headers.get("Retry-After")
        if header:
            try:
                return max(0.0, float(header))
            except ValueError:
                pass
    # Exponential backoff with jitter: ~0.5s, ~1s, ~2s ...
    return 0.5 * (2**attempt) * (1 + random.random() * 0.25)


def _should_retry(response: httpx.Response) -> bool:
    return response.status_code == 429 or response.status_code >= 500


class Magisterial:
    """Synchronous client for the Magisterial developer API.

    >>> client = Magisterial()  # reads MAGISTERIAL_API_KEY
    >>> page = client.players.search(sport="soccer", division="D1")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self._config = _ClientConfig(api_key, base_url, timeout, max_retries)
        self._http = http_client or httpx.Client(timeout=timeout)

        from .resources.alerts import Alerts
        from .resources.exports import Exports
        from .resources.games import Games
        from .resources.persons import Persons
        from .resources.players import Players
        from .resources.portal import Portal
        from .resources.query import Query
        from .resources.reference import Reference
        from .resources.teams import Teams

        self.reference = Reference(self)
        self.players = Players(self)
        self.teams = Teams(self)
        self.persons = Persons(self)
        self.games = Games(self)
        self.portal = Portal(self)
        self.query = Query(self)
        self.alerts = Alerts(self)
        self.exports = Exports(self)

    # -- transport ---------------------------------------------------------

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Optional[Any] = None,
        retryable: Optional[bool] = None,
    ) -> Any:
        """Perform a request and return decoded JSON, retrying 429/5xx and
        connection failures for idempotent (or explicitly retryable) calls."""
        import time

        url = self._config.base_url + path
        can_retry = (
            method in _IDEMPOTENT_METHODS if retryable is None else retryable
        )
        attempts = self._config.max_retries + 1 if can_retry else 1
        last_exc: Optional[Exception] = None

        for attempt in range(attempts):
            try:
                response = self._http.request(
                    method,
                    url,
                    params=_clean_params(params),
                    json=json,
                    headers=self._config.headers,
                )
            except httpx.TimeoutException as exc:
                last_exc = APITimeoutError()
                last_exc.__cause__ = exc
                response = None
            except httpx.HTTPError as exc:
                last_exc = APIConnectionError(str(exc) or "Connection error.")
                last_exc.__cause__ = exc
                response = None

            if response is not None:
                if response.status_code < 400:
                    return response.json()
                last_exc = error_from_response(response)
                if not (attempt < attempts - 1 and _should_retry(response)):
                    raise last_exc
            elif attempt >= attempts - 1:
                raise last_exc  # type: ignore[misc]

            time.sleep(
                _retry_delay(
                    getattr(last_exc, "response", None)
                    if isinstance(last_exc, APIStatusError)
                    else None,
                    attempt,
                )
            )

        raise last_exc  # type: ignore[misc]  # unreachable, defensive

    def get_model(self, path: str, model: Type[M], **params: Any) -> M:
        return model.model_validate(self.request("GET", path, params=params))

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "Magisterial":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


class AsyncMagisterial:
    """Asynchronous client for the Magisterial developer API.

    >>> client = AsyncMagisterial()
    >>> page = await client.players.search(sport="soccer", division="D1")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._config = _ClientConfig(api_key, base_url, timeout, max_retries)
        self._http = http_client or httpx.AsyncClient(timeout=timeout)

        from .resources.alerts import AsyncAlerts
        from .resources.exports import AsyncExports
        from .resources.games import AsyncGames
        from .resources.persons import AsyncPersons
        from .resources.players import AsyncPlayers
        from .resources.portal import AsyncPortal
        from .resources.query import AsyncQuery
        from .resources.reference import AsyncReference
        from .resources.teams import AsyncTeams

        self.reference = AsyncReference(self)
        self.players = AsyncPlayers(self)
        self.teams = AsyncTeams(self)
        self.persons = AsyncPersons(self)
        self.games = AsyncGames(self)
        self.portal = AsyncPortal(self)
        self.query = AsyncQuery(self)
        self.alerts = AsyncAlerts(self)
        self.exports = AsyncExports(self)

    # -- transport ---------------------------------------------------------

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Optional[Any] = None,
        retryable: Optional[bool] = None,
    ) -> Any:
        import asyncio

        url = self._config.base_url + path
        can_retry = (
            method in _IDEMPOTENT_METHODS if retryable is None else retryable
        )
        attempts = self._config.max_retries + 1 if can_retry else 1
        last_exc: Optional[Exception] = None

        for attempt in range(attempts):
            try:
                response = await self._http.request(
                    method,
                    url,
                    params=_clean_params(params),
                    json=json,
                    headers=self._config.headers,
                )
            except httpx.TimeoutException as exc:
                last_exc = APITimeoutError()
                last_exc.__cause__ = exc
                response = None
            except httpx.HTTPError as exc:
                last_exc = APIConnectionError(str(exc) or "Connection error.")
                last_exc.__cause__ = exc
                response = None

            if response is not None:
                if response.status_code < 400:
                    return response.json()
                last_exc = error_from_response(response)
                if not (attempt < attempts - 1 and _should_retry(response)):
                    raise last_exc
            elif attempt >= attempts - 1:
                raise last_exc  # type: ignore[misc]

            await asyncio.sleep(
                _retry_delay(
                    getattr(last_exc, "response", None)
                    if isinstance(last_exc, APIStatusError)
                    else None,
                    attempt,
                )
            )

        raise last_exc  # type: ignore[misc]  # unreachable, defensive

    async def get_model(self, path: str, model: Type[M], **params: Any) -> M:
        return model.model_validate(
            await self.request("GET", path, params=params)
        )

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> "AsyncMagisterial":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()
