# Players: search, profile, season history.

from __future__ import annotations

from typing import Any, Dict, Optional

from .._pagination import AsyncPage, SyncPage
from ..types import (
    PlayerDetail,
    PlayerSearchPage,
    PlayerSeasonsResponse,
    PlayerSummary,
)


def _search_body(
    sport: str,
    division: str,
    gender: Optional[str],
    team_name: Optional[str],
    conference: Optional[str],
    position: Optional[str],
    class_year: Optional[str],
    hometown: Optional[str],
    major: Optional[str],
    season: Optional[str],
    sort_by: Optional[str],
    sort_order: Optional[str],
    limit: Optional[int],
    cursor: Optional[str],
) -> Dict[str, Any]:
    body: Dict[str, Any] = {"sport": sport, "division": division}
    for key, value in (
        ("gender", gender),
        ("team_name", team_name),
        ("conference", conference),
        ("position", position),
        ("class_year", class_year),
        ("hometown", hometown),
        ("major", major),
        ("season", season),
        ("sort_by", sort_by),
        ("sort_order", sort_order),
        ("limit", limit),
        ("cursor", cursor),
    ):
        if value is not None:
            body[key] = value
    return body


class Players:
    def __init__(self, client) -> None:
        self._client = client

    def search(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        team_name: Optional[str] = None,
        conference: Optional[str] = None,
        position: Optional[str] = None,
        class_year: Optional[str] = None,
        hometown: Optional[str] = None,
        major: Optional[str] = None,
        season: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[PlayerSummary]:
        """Search players within a sport/division scope. Sortable stat fields
        come from ``client.reference.filter_catalog()``."""
        body = _search_body(
            sport, division, gender, team_name, conference, position,
            class_year, hometown, major, season, sort_by, sort_order,
            limit, cursor,
        )

        def fetch(page_body: Dict[str, Any]) -> SyncPage[PlayerSummary]:
            # POST, but a pure read — safe to retry.
            raw = self._client.request(
                "POST", "/v1/players/search", json=page_body, retryable=True
            )
            parsed = PlayerSearchPage.model_validate(raw)
            return SyncPage(
                parsed.data,
                parsed.next_cursor,
                parsed.has_more,
                lambda c: fetch({**page_body, "cursor": c}),
            )

        return fetch(body)

    def get(
        self,
        player_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
    ) -> PlayerDetail:
        """Full profile: identity, season stats, accolades, career."""
        return self._client.get_model(
            f"/v1/players/{player_id}",
            PlayerDetail,
            sport=sport,
            division=division,
            gender=gender,
        )

    def seasons(
        self,
        player_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
    ) -> PlayerSeasonsResponse:
        """Season-by-season stats and accolades only."""
        return self._client.get_model(
            f"/v1/players/{player_id}/seasons",
            PlayerSeasonsResponse,
            sport=sport,
            division=division,
            gender=gender,
        )


class AsyncPlayers:
    def __init__(self, client) -> None:
        self._client = client

    async def search(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        team_name: Optional[str] = None,
        conference: Optional[str] = None,
        position: Optional[str] = None,
        class_year: Optional[str] = None,
        hometown: Optional[str] = None,
        major: Optional[str] = None,
        season: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[PlayerSummary]:
        """Search players within a sport/division scope. Sortable stat fields
        come from ``client.reference.filter_catalog()``."""
        body = _search_body(
            sport, division, gender, team_name, conference, position,
            class_year, hometown, major, season, sort_by, sort_order,
            limit, cursor,
        )

        async def fetch(page_body: Dict[str, Any]) -> AsyncPage[PlayerSummary]:
            raw = await self._client.request(
                "POST", "/v1/players/search", json=page_body, retryable=True
            )
            parsed = PlayerSearchPage.model_validate(raw)
            return AsyncPage(
                parsed.data,
                parsed.next_cursor,
                parsed.has_more,
                lambda c: fetch({**page_body, "cursor": c}),
            )

        return await fetch(body)

    async def get(
        self,
        player_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
    ) -> PlayerDetail:
        """Full profile: identity, season stats, accolades, career."""
        return await self._client.get_model(
            f"/v1/players/{player_id}",
            PlayerDetail,
            sport=sport,
            division=division,
            gender=gender,
        )

    async def seasons(
        self,
        player_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
    ) -> PlayerSeasonsResponse:
        """Season-by-season stats and accolades only."""
        return await self._client.get_model(
            f"/v1/players/{player_id}/seasons",
            PlayerSeasonsResponse,
            sport=sport,
            division=division,
            gender=gender,
        )
