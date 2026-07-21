# Natural-language query (usage-billed): async runs, submitted then polled.

from __future__ import annotations

import asyncio
import time
from typing import Optional

from .._exceptions import QueryPollTimeout
from ..types import QueryCreateResponse, QueryRunStatus

TERMINAL_STATUSES = {"done", "error", "cancelled"}

DEFAULT_POLL_INTERVAL = 2.0
DEFAULT_POLL_TIMEOUT = 300.0


class Query:
    def __init__(self, client) -> None:
        self._client = client

    def create(
        self,
        *,
        prompt: str,
        sport: str,
        division: Optional[str] = None,
        gender: Optional[str] = None,
    ) -> QueryCreateResponse:
        """Submit a natural-language query run (returns immediately; the run
        executes server-side). Billed by token usage once it finishes."""
        body = {"prompt": prompt, "sport": sport}
        if division is not None:
            body["division"] = division
        if gender is not None:
            body["gender"] = gender
        # Not retried automatically: each accepted submission bills.
        raw = self._client.request("POST", "/v1/query", json=body)
        return QueryCreateResponse.model_validate(raw)

    def get(self, run_id: str) -> QueryRunStatus:
        """Status of a query run; `answer` and `usage` appear once terminal."""
        return self._client.get_model(f"/v1/query/{run_id}", QueryRunStatus)

    def create_and_poll(
        self,
        *,
        prompt: str,
        sport: str,
        division: Optional[str] = None,
        gender: Optional[str] = None,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        timeout: float = DEFAULT_POLL_TIMEOUT,
    ) -> QueryRunStatus:
        """Submit a query and block until it reaches a terminal state
        (done / error / cancelled). Raises :class:`QueryPollTimeout` if the
        run is still going after ``timeout`` seconds — the run itself keeps
        executing and remains fetchable via :meth:`get`."""
        created = self.create(
            prompt=prompt, sport=sport, division=division, gender=gender
        )
        deadline = time.monotonic() + timeout
        run = self.get(created.run_id)
        while run.status not in TERMINAL_STATUSES:
            if time.monotonic() >= deadline:
                raise QueryPollTimeout(created.run_id, run.status, timeout)
            time.sleep(poll_interval)
            run = self.get(created.run_id)
        return run


class AsyncQuery:
    def __init__(self, client) -> None:
        self._client = client

    async def create(
        self,
        *,
        prompt: str,
        sport: str,
        division: Optional[str] = None,
        gender: Optional[str] = None,
    ) -> QueryCreateResponse:
        """Submit a natural-language query run (returns immediately; the run
        executes server-side). Billed by token usage once it finishes."""
        body = {"prompt": prompt, "sport": sport}
        if division is not None:
            body["division"] = division
        if gender is not None:
            body["gender"] = gender
        raw = await self._client.request("POST", "/v1/query", json=body)
        return QueryCreateResponse.model_validate(raw)

    async def get(self, run_id: str) -> QueryRunStatus:
        """Status of a query run; `answer` and `usage` appear once terminal."""
        return await self._client.get_model(f"/v1/query/{run_id}", QueryRunStatus)

    async def create_and_poll(
        self,
        *,
        prompt: str,
        sport: str,
        division: Optional[str] = None,
        gender: Optional[str] = None,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        timeout: float = DEFAULT_POLL_TIMEOUT,
    ) -> QueryRunStatus:
        """Submit a query and wait until it reaches a terminal state
        (done / error / cancelled). Raises :class:`QueryPollTimeout` if the
        run is still going after ``timeout`` seconds — the run itself keeps
        executing and remains fetchable via :meth:`get`."""
        created = await self.create(
            prompt=prompt, sport=sport, division=division, gender=gender
        )
        loop = asyncio.get_event_loop()
        deadline = loop.time() + timeout
        run = await self.get(created.run_id)
        while run.status not in TERMINAL_STATUSES:
            if loop.time() >= deadline:
                raise QueryPollTimeout(created.run_id, run.status, timeout)
            await asyncio.sleep(poll_interval)
            run = await self.get(created.run_id)
        return run
