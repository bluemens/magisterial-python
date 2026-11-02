# Portal supply: transfer portal counts per program and position group, and their change log.

from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

from .._pagination import AsyncPage, SyncPage
from ..types import (
    PortalSupplyChange,
    PortalSupplyChangePage,
    PortalSupplyEntry,
    PortalSupplyPage,
)


def _since_str(since: Union[str, datetime, None]) -> Optional[str]:
    return since.isoformat() if isinstance(since, datetime) else since


class PortalSupply:
    def __init__(self, client) -> None:
        self._client = client

    def list(
        self,
        *,
        sport_path: Optional[str] = None,
        sport: Optional[str] = None,
        gender: Optional[str] = None,
        division: Optional[str] = None,
        conference: Optional[str] = None,
        conference_not: Optional[str] = None,
        team_id: Optional[str] = None,
        lane: Optional[str] = None,
        include_zero: Optional[bool] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[PortalSupplyEntry]:
        """Who is in the transfer portal at each program, as counts per position
        group with no one named. Counts are taken once a day; keep a copy current
        with `changes`. Developer Ultra and up."""

        def fetch(c: Optional[str]) -> SyncPage[PortalSupplyEntry]:
            raw = self._client.request(
                "GET",
                "/v1/portal/supply",
                params={
                    "sport_path": sport_path,
                    "sport": sport,
                    "gender": gender,
                    "division": division,
                    "conference": conference,
                    "conference_not": conference_not,
                    "team_id": team_id,
                    "lane": lane,
                    "include_zero": include_zero,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = PortalSupplyPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)

    def changes(
        self,
        *,
        since: Union[str, datetime, None] = None,
        sport_path: Optional[str] = None,
        sport: Optional[str] = None,
        gender: Optional[str] = None,
        division: Optional[str] = None,
        team_id: Optional[str] = None,
        lane: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[PortalSupplyChange]:
        """The change log of the portal supply feed, oldest change first. Pass the
        last entry's `changed_at` as `since` on the next poll (inclusive) and apply
        each entry by `supply.id`. Developer Ultra and up."""
        since_value = _since_str(since)

        def fetch(c: Optional[str]) -> SyncPage[PortalSupplyChange]:
            raw = self._client.request(
                "GET",
                "/v1/portal/supply/changes",
                params={
                    "since": since_value,
                    "sport_path": sport_path,
                    "sport": sport,
                    "gender": gender,
                    "division": division,
                    "team_id": team_id,
                    "lane": lane,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = PortalSupplyChangePage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)


class AsyncPortalSupply:
    def __init__(self, client) -> None:
        self._client = client

    async def list(
        self,
        *,
        sport_path: Optional[str] = None,
        sport: Optional[str] = None,
        gender: Optional[str] = None,
        division: Optional[str] = None,
        conference: Optional[str] = None,
        conference_not: Optional[str] = None,
        team_id: Optional[str] = None,
        lane: Optional[str] = None,
        include_zero: Optional[bool] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[PortalSupplyEntry]:
        """Who is in the transfer portal at each program, as counts per position
        group with no one named. Counts are taken once a day; keep a copy current
        with `changes`. Developer Ultra and up."""

        async def fetch(c: Optional[str]) -> AsyncPage[PortalSupplyEntry]:
            raw = await self._client.request(
                "GET",
                "/v1/portal/supply",
                params={
                    "sport_path": sport_path,
                    "sport": sport,
                    "gender": gender,
                    "division": division,
                    "conference": conference,
                    "conference_not": conference_not,
                    "team_id": team_id,
                    "lane": lane,
                    "include_zero": include_zero,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = PortalSupplyPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)

    async def changes(
        self,
        *,
        since: Union[str, datetime, None] = None,
        sport_path: Optional[str] = None,
        sport: Optional[str] = None,
        gender: Optional[str] = None,
        division: Optional[str] = None,
        team_id: Optional[str] = None,
        lane: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[PortalSupplyChange]:
        """The change log of the portal supply feed, oldest change first. Pass the
        last entry's `changed_at` as `since` on the next poll (inclusive) and apply
        each entry by `supply.id`. Developer Ultra and up."""
        since_value = _since_str(since)

        async def fetch(c: Optional[str]) -> AsyncPage[PortalSupplyChange]:
            raw = await self._client.request(
                "GET",
                "/v1/portal/supply/changes",
                params={
                    "since": since_value,
                    "sport_path": sport_path,
                    "sport": sport,
                    "gender": gender,
                    "division": division,
                    "team_id": team_id,
                    "lane": lane,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = PortalSupplyChangePage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)
