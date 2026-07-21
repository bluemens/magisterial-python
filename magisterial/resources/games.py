# Games: box scores and play-by-play where covered.

from __future__ import annotations

from typing import Optional

from ..types import GameSummary


class Games:
    def __init__(self, client) -> None:
        self._client = client

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
