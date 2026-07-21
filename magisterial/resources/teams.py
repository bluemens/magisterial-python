# Teams: list, profile, roster.

from __future__ import annotations

from typing import Optional

from .._pagination import AsyncPage, SyncPage
from ..types import RosterEntry, RosterPage, TeamDetail, TeamPage, TeamSummary


class Teams:
    def __init__(self, client) -> None:
        self._client = client

    def list(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        conference: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[TeamSummary]:
        """Teams in a sport/division scope, alphabetical."""

        def fetch(c: Optional[str]) -> SyncPage[TeamSummary]:
            raw = self._client.request(
                "GET",
                "/v1/teams",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "conference": conference,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = TeamPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)

    def get(
        self,
        team_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
    ) -> TeamDetail:
        """One team plus its per-season records."""
        return self._client.get_model(
            f"/v1/teams/{team_id}",
            TeamDetail,
            sport=sport,
            division=division,
            gender=gender,
        )

    def roster(
        self,
        team_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[RosterEntry]:
        """A team's roster (identity fields only)."""

        def fetch(c: Optional[str]) -> SyncPage[RosterEntry]:
            raw = self._client.request(
                "GET",
                f"/v1/teams/{team_id}/roster",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = RosterPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)


class AsyncTeams:
    def __init__(self, client) -> None:
        self._client = client

    async def list(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        conference: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[TeamSummary]:
        """Teams in a sport/division scope, alphabetical."""

        async def fetch(c: Optional[str]) -> AsyncPage[TeamSummary]:
            raw = await self._client.request(
                "GET",
                "/v1/teams",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "conference": conference,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = TeamPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)

    async def get(
        self,
        team_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
    ) -> TeamDetail:
        """One team plus its per-season records."""
        return await self._client.get_model(
            f"/v1/teams/{team_id}",
            TeamDetail,
            sport=sport,
            division=division,
            gender=gender,
        )

    async def roster(
        self,
        team_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[RosterEntry]:
        """A team's roster (identity fields only)."""

        async def fetch(c: Optional[str]) -> AsyncPage[RosterEntry]:
            raw = await self._client.request(
                "GET",
                f"/v1/teams/{team_id}/roster",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = RosterPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)
