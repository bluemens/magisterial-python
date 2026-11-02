# Golf: tournaments, round scores, and magisterial's golf ratings.

from __future__ import annotations

from typing import Optional

from .._pagination import AsyncPage, SyncPage
from ..types import (
    GolfRatingEntry,
    GolfRatingPage,
    GolfTournamentDetail,
    GolfTournamentPage,
    GolfTournamentSummary,
)


class Golf:
    def __init__(self, client) -> None:
        self._client = client

    def list_tournaments(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        season: Optional[str] = None,
        team_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date_min: Optional[str] = None,
        start_date_max: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[GolfTournamentSummary]:
        """College golf tournaments in a division scope, newest first."""

        def fetch(c: Optional[str]) -> SyncPage[GolfTournamentSummary]:
            raw = self._client.request(
                "GET",
                "/v1/golf/tournaments",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "season": season,
                    "team_id": team_id,
                    "status": status,
                    "start_date_min": start_date_min,
                    "start_date_max": start_date_max,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = GolfTournamentPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)

    def get_tournament(
        self,
        tournament_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
    ) -> GolfTournamentDetail:
        """One tournament with its team standings and every player's round scores."""
        return self._client.get_model(
            f"/v1/golf/tournaments/{tournament_id}",
            GolfTournamentDetail,
            sport=sport,
            division=division,
            gender=gender,
        )

    def list_ratings(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        entity: Optional[str] = None,
        team_id: Optional[str] = None,
        as_of: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[GolfRatingEntry]:
        """magisterial's golf rating for players or teams, ranked within each
        division in scope (strokes per round better than the division average)."""

        def fetch(c: Optional[str]) -> SyncPage[GolfRatingEntry]:
            raw = self._client.request(
                "GET",
                "/v1/golf/ratings",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "entity": entity,
                    "team_id": team_id,
                    "as_of": as_of,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = GolfRatingPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)


class AsyncGolf:
    def __init__(self, client) -> None:
        self._client = client

    async def list_tournaments(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        season: Optional[str] = None,
        team_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date_min: Optional[str] = None,
        start_date_max: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[GolfTournamentSummary]:
        """College golf tournaments in a division scope, newest first."""

        async def fetch(c: Optional[str]) -> AsyncPage[GolfTournamentSummary]:
            raw = await self._client.request(
                "GET",
                "/v1/golf/tournaments",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "season": season,
                    "team_id": team_id,
                    "status": status,
                    "start_date_min": start_date_min,
                    "start_date_max": start_date_max,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = GolfTournamentPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)

    async def get_tournament(
        self,
        tournament_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
    ) -> GolfTournamentDetail:
        """One tournament with its team standings and every player's round scores."""
        return await self._client.get_model(
            f"/v1/golf/tournaments/{tournament_id}",
            GolfTournamentDetail,
            sport=sport,
            division=division,
            gender=gender,
        )

    async def list_ratings(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        entity: Optional[str] = None,
        team_id: Optional[str] = None,
        as_of: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[GolfRatingEntry]:
        """magisterial's golf rating for players or teams, ranked within each
        division in scope (strokes per round better than the division average)."""

        async def fetch(c: Optional[str]) -> AsyncPage[GolfRatingEntry]:
            raw = await self._client.request(
                "GET",
                "/v1/golf/ratings",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "entity": entity,
                    "team_id": team_id,
                    "as_of": as_of,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = GolfRatingPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)
