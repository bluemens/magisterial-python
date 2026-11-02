# Tennis: individual tournament matches and ITA rankings.

from __future__ import annotations

from typing import Optional

from .._pagination import AsyncPage, SyncPage
from ..types import (
    TennisMatch,
    TennisMatchPage,
    TennisRankingEntry,
    TennisRankingPage,
)


class Tennis:
    def __init__(self, client) -> None:
        self._client = client

    def list_matches(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        player_id: Optional[str] = None,
        team_id: Optional[str] = None,
        season: Optional[str] = None,
        match_type: Optional[str] = None,
        status: Optional[str] = None,
        date_min: Optional[str] = None,
        date_max: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[TennisMatch]:
        """Individual singles and doubles tournament matches, newest first, with
        each set's games and tiebreaks. Team duals are games (`games.list`)."""

        def fetch(c: Optional[str]) -> SyncPage[TennisMatch]:
            raw = self._client.request(
                "GET",
                "/v1/tennis/matches",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "player_id": player_id,
                    "team_id": team_id,
                    "season": season,
                    "match_type": match_type,
                    "status": status,
                    "date_min": date_min,
                    "date_max": date_max,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = TennisMatchPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)

    def list_ita_rankings(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        type: Optional[str] = None,
        season: Optional[str] = None,
        release_date: Optional[str] = None,
        team_id: Optional[str] = None,
        player_id: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[TennisRankingEntry]:
        """The ITA's individual rankings (singles players or doubles pairs) from
        the latest release of the season, by division then rank."""

        def fetch(c: Optional[str]) -> SyncPage[TennisRankingEntry]:
            raw = self._client.request(
                "GET",
                "/v1/rankings/ita",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "type": type,
                    "season": season,
                    "release_date": release_date,
                    "team_id": team_id,
                    "player_id": player_id,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = TennisRankingPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)


class AsyncTennis:
    def __init__(self, client) -> None:
        self._client = client

    async def list_matches(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        player_id: Optional[str] = None,
        team_id: Optional[str] = None,
        season: Optional[str] = None,
        match_type: Optional[str] = None,
        status: Optional[str] = None,
        date_min: Optional[str] = None,
        date_max: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[TennisMatch]:
        """Individual singles and doubles tournament matches, newest first, with
        each set's games and tiebreaks. Team duals are games (`games.list`)."""

        async def fetch(c: Optional[str]) -> AsyncPage[TennisMatch]:
            raw = await self._client.request(
                "GET",
                "/v1/tennis/matches",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "player_id": player_id,
                    "team_id": team_id,
                    "season": season,
                    "match_type": match_type,
                    "status": status,
                    "date_min": date_min,
                    "date_max": date_max,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = TennisMatchPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)

    async def list_ita_rankings(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        type: Optional[str] = None,
        season: Optional[str] = None,
        release_date: Optional[str] = None,
        team_id: Optional[str] = None,
        player_id: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[TennisRankingEntry]:
        """The ITA's individual rankings (singles players or doubles pairs) from
        the latest release of the season, by division then rank."""

        async def fetch(c: Optional[str]) -> AsyncPage[TennisRankingEntry]:
            raw = await self._client.request(
                "GET",
                "/v1/rankings/ita",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "type": type,
                    "season": season,
                    "release_date": release_date,
                    "team_id": team_id,
                    "player_id": player_id,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = TennisRankingPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)
