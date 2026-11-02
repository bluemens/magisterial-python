# Movements: the published roster/coaching movement feed.

from __future__ import annotations

from typing import Optional

from .._pagination import AsyncPage, SyncPage
from ..types import (
    MovementChange,
    MovementChangePage,
    MovementEntry,
    MovementPage,
)


class Movements:
    def __init__(self, client) -> None:
        self._client = client

    def list(
        self,
        *,
        kind: Optional[str] = None,
        sport_path: Optional[str] = None,
        since: Optional[str] = None,
        status: Optional[str] = None,
        region: Optional[str] = None,
        region_not: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[MovementEntry]:
        """Published roster and coaching-staff movements, newest first.

        Cross-division; no scope parameters. `kind` filters to 'player' or
        'coach'; `since` is an ISO datetime lower bound on publish time.
        `status` selects the feed tier: 'published' (curated, every plan,
        the default), 'resolved' (identity resolution finished; Enterprise),
        or 'observed' (every non-dismissed event including pending ones;
        Enterprise)."""

        def fetch(c: Optional[str]) -> SyncPage[MovementEntry]:
            raw = self._client.request(
                "GET",
                "/v1/movements",
                params={
                    "kind": kind,
                    "sport_path": sport_path,
                    "since": since,
                    "status": status,
                    "region": region,
                    "region_not": region_not,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = MovementPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)


    def changes(
        self,
        *,
        since: Optional[str] = None,
        kind: Optional[str] = None,
        sport_path: Optional[str] = None,
        sport: Optional[str] = None,
        gender: Optional[str] = None,
        division: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[MovementChange]:
        """The change log of the published movement feed, oldest change first.
        Poll it with `since` to keep a copy of the feed correct."""

        def fetch(c: Optional[str]) -> SyncPage[MovementChange]:
            raw = self._client.request(
                "GET",
                "/v1/movements/changes",
                params={
                    "since": since,
                    "kind": kind,
                    "sport_path": sport_path,
                    "sport": sport,
                    "gender": gender,
                    "division": division,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = MovementChangePage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)


class AsyncMovements:
    def __init__(self, client) -> None:
        self._client = client

    async def list(
        self,
        *,
        kind: Optional[str] = None,
        sport_path: Optional[str] = None,
        since: Optional[str] = None,
        status: Optional[str] = None,
        region: Optional[str] = None,
        region_not: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[MovementEntry]:
        """Published roster and coaching-staff movements, newest first.

        Cross-division; no scope parameters. `kind` filters to 'player' or
        'coach'; `since` is an ISO datetime lower bound on publish time.
        `status` selects the feed tier: 'published' (curated, every plan,
        the default), 'resolved' (identity resolution finished; Enterprise),
        or 'observed' (every non-dismissed event including pending ones;
        Enterprise)."""

        async def fetch(c: Optional[str]) -> AsyncPage[MovementEntry]:
            raw = await self._client.request(
                "GET",
                "/v1/movements",
                params={
                    "kind": kind,
                    "sport_path": sport_path,
                    "since": since,
                    "status": status,
                    "region": region,
                    "region_not": region_not,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = MovementPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)

    async def changes(
        self,
        *,
        since: Optional[str] = None,
        kind: Optional[str] = None,
        sport_path: Optional[str] = None,
        sport: Optional[str] = None,
        gender: Optional[str] = None,
        division: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[MovementChange]:
        """The change log of the published movement feed, oldest change first.
        Poll it with `since` to keep a copy of the feed correct."""

        async def fetch(c: Optional[str]) -> AsyncPage[MovementChange]:
            raw = await self._client.request(
                "GET",
                "/v1/movements/changes",
                params={
                    "since": since,
                    "kind": kind,
                    "sport_path": sport_path,
                    "sport": sport,
                    "gender": gender,
                    "division": division,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = MovementChangePage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)
