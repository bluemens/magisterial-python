# Bulk exports (usage-billed by result size): async jobs, submitted then
# polled; succeeded jobs carry a short-lived download_url minted per read.

from __future__ import annotations

import time
from typing import Optional

from .._exceptions import ExportPollTimeout
from .._pagination import AsyncPage, SyncPage
from ..types import ExportCreateResponse, ExportJobStatus, ExportListPage

TERMINAL_STATUSES = {"succeeded", "failed", "expired"}

DEFAULT_POLL_INTERVAL = 5.0
DEFAULT_POLL_TIMEOUT = 600.0


def _create_body(
    dataset: str,
    sport: str,
    division: str,
    format: Optional[str],
    gender: Optional[str],
    season: Optional[str],
    conference: Optional[str],
) -> dict:
    body = {"dataset": dataset, "sport": sport, "division": division}
    for key, value in (
        ("format", format),
        ("gender", gender),
        ("season", season),
        ("conference", conference),
    ):
        if value is not None:
            body[key] = value
    return body


class Exports:
    def __init__(self, client) -> None:
        self._client = client

    def create(
        self,
        *,
        dataset: str,
        sport: str,
        division: str,
        format: Optional[str] = None,
        gender: Optional[str] = None,
        season: Optional[str] = None,
        conference: Optional[str] = None,
    ) -> ExportCreateResponse:
        """Submit an export job (one dataset in one scope, gzipped flat file).
        Billed by result size once it finishes; not retried automatically."""
        raw = self._client.request(
            "POST",
            "/v1/exports",
            json=_create_body(dataset, sport, division, format, gender, season, conference),
        )
        return ExportCreateResponse.model_validate(raw)

    def get(self, export_id: str) -> ExportJobStatus:
        """Job status. `download_url` appears once succeeded and is minted
        fresh (short-lived) on every read — re-poll for a new one."""
        return self._client.get_model(f"/v1/exports/{export_id}", ExportJobStatus)

    def list(
        self, *, limit: Optional[int] = None, cursor: Optional[str] = None
    ) -> SyncPage[ExportJobStatus]:
        """This account's export jobs, newest first."""

        def fetch(c: Optional[str]) -> SyncPage[ExportJobStatus]:
            raw = self._client.request(
                "GET", "/v1/exports", params={"limit": limit, "cursor": c}
            )
            parsed = ExportListPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)

    def create_and_poll(
        self,
        *,
        dataset: str,
        sport: str,
        division: str,
        format: Optional[str] = None,
        gender: Optional[str] = None,
        season: Optional[str] = None,
        conference: Optional[str] = None,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        timeout: float = DEFAULT_POLL_TIMEOUT,
    ) -> ExportJobStatus:
        """Submit an export and block until it reaches a terminal state
        (succeeded / failed / expired). Raises :class:`ExportPollTimeout` if
        still running after ``timeout`` seconds — the job keeps executing and
        remains fetchable via :meth:`get`."""
        created = self.create(
            dataset=dataset, sport=sport, division=division, format=format,
            gender=gender, season=season, conference=conference,
        )
        deadline = time.monotonic() + timeout
        job = self.get(created.export_id)
        while job.status not in TERMINAL_STATUSES:
            if time.monotonic() >= deadline:
                raise ExportPollTimeout(created.export_id, job.status, timeout)
            time.sleep(poll_interval)
            job = self.get(created.export_id)
        return job


class AsyncExports:
    def __init__(self, client) -> None:
        self._client = client

    async def create(
        self,
        *,
        dataset: str,
        sport: str,
        division: str,
        format: Optional[str] = None,
        gender: Optional[str] = None,
        season: Optional[str] = None,
        conference: Optional[str] = None,
    ) -> ExportCreateResponse:
        """Submit an export job (one dataset in one scope, gzipped flat file).
        Billed by result size once it finishes; not retried automatically."""
        raw = await self._client.request(
            "POST",
            "/v1/exports",
            json=_create_body(dataset, sport, division, format, gender, season, conference),
        )
        return ExportCreateResponse.model_validate(raw)

    async def get(self, export_id: str) -> ExportJobStatus:
        """Job status. `download_url` appears once succeeded and is minted
        fresh (short-lived) on every read — re-poll for a new one."""
        return await self._client.get_model(f"/v1/exports/{export_id}", ExportJobStatus)

    async def list(
        self, *, limit: Optional[int] = None, cursor: Optional[str] = None
    ) -> AsyncPage[ExportJobStatus]:
        """This account's export jobs, newest first."""

        async def fetch(c: Optional[str]) -> AsyncPage[ExportJobStatus]:
            raw = await self._client.request(
                "GET", "/v1/exports", params={"limit": limit, "cursor": c}
            )
            parsed = ExportListPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)

    async def create_and_poll(
        self,
        *,
        dataset: str,
        sport: str,
        division: str,
        format: Optional[str] = None,
        gender: Optional[str] = None,
        season: Optional[str] = None,
        conference: Optional[str] = None,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        timeout: float = DEFAULT_POLL_TIMEOUT,
    ) -> ExportJobStatus:
        """Submit an export and wait until it reaches a terminal state
        (succeeded / failed / expired). Raises :class:`ExportPollTimeout` if
        still running after ``timeout`` seconds — the job keeps executing and
        remains fetchable via :meth:`get`."""
        import asyncio

        created = await self.create(
            dataset=dataset, sport=sport, division=division, format=format,
            gender=gender, season=season, conference=conference,
        )
        loop = asyncio.get_event_loop()
        deadline = loop.time() + timeout
        job = await self.get(created.export_id)
        while job.status not in TERMINAL_STATUSES:
            if loop.time() >= deadline:
                raise ExportPollTimeout(created.export_id, job.status, timeout)
            await asyncio.sleep(poll_interval)
            job = await self.get(created.export_id)
        return job
