# Teams: list, profile, roster.

from __future__ import annotations

from typing import Optional

from .._pagination import AsyncPage, SyncPage
from ..types import (
    RosterEntry,
    RosterPage,
    TeamCoachesResponse,
    TeamDetail,
    TeamPage,
    TeamPostseasonResponse,
    TeamRankingsResponse,
    TeamSummary,
)


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
        ipeds_unitid: Optional[int] = None,
        region: Optional[str] = None,
        region_not: Optional[str] = None,
        roster_changed_since: Optional[str] = None,
        coaches_changed_since: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[TeamSummary]:
        """Teams in a sport/division scope, alphabetical. `ipeds_unitid`
        filters to the school with that federal IPEDS UNITID."""

        def fetch(c: Optional[str]) -> SyncPage[TeamSummary]:
            raw = self._client.request(
                "GET",
                "/v1/teams",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "conference": conference,
                    "ipeds_unitid": ipeds_unitid,
                    "region": region,
                    "region_not": region_not,
                    "roster_changed_since": roster_changed_since,
                    "coaches_changed_since": coaches_changed_since,
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
        season: Optional[str] = None,
        class_level: Optional[str] = None,
        class_level_not: Optional[str] = None,
        class_redshirt: Optional[bool] = None,
        seasons_remaining_min: Optional[int] = None,
        eligibility_confidence: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[RosterEntry]:
        """A team's roster for a season (identity fields only)."""

        def fetch(c: Optional[str]) -> SyncPage[RosterEntry]:
            raw = self._client.request(
                "GET",
                f"/v1/teams/{team_id}/roster",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "season": season,
                    "class_level": class_level,
                    "class_level_not": class_level_not,
                    "class_redshirt": class_redshirt,
                    "seasons_remaining_min": seasons_remaining_min,
                    "eligibility_confidence": eligibility_confidence,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = RosterPage.model_validate(raw)
            return SyncPage(
                parsed.data,
                parsed.next_cursor,
                parsed.has_more,
                fetch,
                season=parsed.season,
            )

        return fetch(cursor)

    def coaches(
        self,
        team_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        season: Optional[str] = None,
        on_behalf_of: Optional[int] = None,
    ) -> TeamCoachesResponse:
        """A team's coaching staff for a season (defaults to the most recent
        season on record).

        `on_behalf_of` (Enterprise): player id of a managed athlete who has
        authorized your account. Contact fields are then evaluated against
        that athlete's verified claim, audited, and billed at the delegated
        coach-contact rate."""
        return self._client.get_model(
            f"/v1/teams/{team_id}/coaches",
            TeamCoachesResponse,
            sport=sport,
            division=division,
            gender=gender,
            season=season,
            on_behalf_of=on_behalf_of,
        )


    def postseason(
        self,
        team_id: int,
        *,
        sport: str,
        division: Optional[str] = None,
        gender: Optional[str] = None,
        season: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> TeamPostseasonResponse:
        """What a team won and how far it went, season by season: national
        tournaments, bowl games, and conference titles."""
        return self._client.get_model(
            f"/v1/teams/{team_id}/postseason",
            TeamPostseasonResponse,
            sport=sport,
            division=division,
            gender=gender,
            season=season,
            kind=kind,
        )

    def rankings(
        self,
        team_id: int,
        *,
        sport: str,
        division: Optional[str] = None,
        gender: Optional[str] = None,
        season: Optional[str] = None,
        ranking_system: Optional[str] = None,
    ) -> TeamRankingsResponse:
        """Where a team stands, or finished, in each national ranking, season by
        season (RPI, NET, NPI, coaches polls, ITA, Clippd, USCHO)."""
        return self._client.get_model(
            f"/v1/teams/{team_id}/rankings",
            TeamRankingsResponse,
            sport=sport,
            division=division,
            gender=gender,
            season=season,
            ranking_system=ranking_system,
        )


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
        ipeds_unitid: Optional[int] = None,
        region: Optional[str] = None,
        region_not: Optional[str] = None,
        roster_changed_since: Optional[str] = None,
        coaches_changed_since: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[TeamSummary]:
        """Teams in a sport/division scope, alphabetical. `ipeds_unitid`
        filters to the school with that federal IPEDS UNITID."""

        async def fetch(c: Optional[str]) -> AsyncPage[TeamSummary]:
            raw = await self._client.request(
                "GET",
                "/v1/teams",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "conference": conference,
                    "ipeds_unitid": ipeds_unitid,
                    "region": region,
                    "region_not": region_not,
                    "roster_changed_since": roster_changed_since,
                    "coaches_changed_since": coaches_changed_since,
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
        season: Optional[str] = None,
        class_level: Optional[str] = None,
        class_level_not: Optional[str] = None,
        class_redshirt: Optional[bool] = None,
        seasons_remaining_min: Optional[int] = None,
        eligibility_confidence: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[RosterEntry]:
        """A team's roster for a season (identity fields only)."""

        async def fetch(c: Optional[str]) -> AsyncPage[RosterEntry]:
            raw = await self._client.request(
                "GET",
                f"/v1/teams/{team_id}/roster",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "season": season,
                    "class_level": class_level,
                    "class_level_not": class_level_not,
                    "class_redshirt": class_redshirt,
                    "seasons_remaining_min": seasons_remaining_min,
                    "eligibility_confidence": eligibility_confidence,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = RosterPage.model_validate(raw)
            return AsyncPage(
                parsed.data,
                parsed.next_cursor,
                parsed.has_more,
                fetch,
                season=parsed.season,
            )

        return await fetch(cursor)

    async def coaches(
        self,
        team_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        season: Optional[str] = None,
        on_behalf_of: Optional[int] = None,
    ) -> TeamCoachesResponse:
        """A team's coaching staff for a season (defaults to the most recent
        season on record).

        `on_behalf_of` (Enterprise): player id of a managed athlete who has
        authorized your account. Contact fields are then evaluated against
        that athlete's verified claim, audited, and billed at the delegated
        coach-contact rate."""
        return await self._client.get_model(
            f"/v1/teams/{team_id}/coaches",
            TeamCoachesResponse,
            sport=sport,
            division=division,
            gender=gender,
            season=season,
            on_behalf_of=on_behalf_of,
        )

    async def postseason(
        self,
        team_id: int,
        *,
        sport: str,
        division: Optional[str] = None,
        gender: Optional[str] = None,
        season: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> TeamPostseasonResponse:
        """What a team won and how far it went, season by season: national
        tournaments, bowl games, and conference titles."""
        return await self._client.get_model(
            f"/v1/teams/{team_id}/postseason",
            TeamPostseasonResponse,
            sport=sport,
            division=division,
            gender=gender,
            season=season,
            kind=kind,
        )

    async def rankings(
        self,
        team_id: int,
        *,
        sport: str,
        division: Optional[str] = None,
        gender: Optional[str] = None,
        season: Optional[str] = None,
        ranking_system: Optional[str] = None,
    ) -> TeamRankingsResponse:
        """Where a team stands, or finished, in each national ranking, season by
        season (RPI, NET, NPI, coaches polls, ITA, Clippd, USCHO)."""
        return await self._client.get_model(
            f"/v1/teams/{team_id}/rankings",
            TeamRankingsResponse,
            sport=sport,
            division=division,
            gender=gender,
            season=season,
            ranking_system=ranking_system,
        )
