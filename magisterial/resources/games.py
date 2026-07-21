# Games: schedules/results list plus per-game box scores and play-by-play.

from __future__ import annotations

from typing import Optional

from .._pagination import AsyncPage, SyncPage
from ..types import GameFixture, GamePage, GameSummary


class Games:
    def __init__(self, client) -> None:
        self._client = client

    def list(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        team_id: Optional[int] = None,
        season: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[GameFixture]:
        """Games in a sport/division scope, filterable by team, season, date
        range, and status ('scheduled' | 'final' | 'postponed' | 'cancelled'
        | 'forfeit')."""

        def fetch(c: Optional[str]) -> SyncPage[GameFixture]:
            raw = self._client.request(
                "GET",
                "/v1/games",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "team_id": team_id,
                    "season": season,
                    "date_from": date_from,
                    "date_to": date_to,
                    "status": status,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = GamePage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)

    def get(
        self,
        game_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
    ) -> GameSummary:
        """One game with box score / play-by-play where covered."""
        return self._client.get_model(
            f"/v1/games/{game_id}",
            GameSummary,
            sport=sport,
            division=division,
            gender=gender,
        )


class AsyncGames:
    def __init__(self, client) -> None:
        self._client = client

    async def list(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        team_id: Optional[int] = None,
        season: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[GameFixture]:
        """Games in a sport/division scope, filterable by team, season, date
        range, and status ('scheduled' | 'final' | 'postponed' | 'cancelled'
        | 'forfeit')."""

        async def fetch(c: Optional[str]) -> AsyncPage[GameFixture]:
            raw = await self._client.request(
                "GET",
                "/v1/games",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "team_id": team_id,
                    "season": season,
                    "date_from": date_from,
                    "date_to": date_to,
                    "status": status,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = GamePage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)

    async def get(
        self,
        game_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
    ) -> GameSummary:
        """One game with box score / play-by-play where covered."""
        return await self._client.get_model(
            f"/v1/games/{game_id}",
            GameSummary,
            sport=sport,
            division=division,
            gender=gender,
        )
