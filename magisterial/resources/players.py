# Players: search, profile, season history.

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from .._pagination import AsyncPage, SyncPage
from ..types import (
    PlayerDetail,
    PlayerSearchPage,
    PlayerSeasonsResponse,
    PlayerSummary,
    SwimTime,
    SwimTimesPage,
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
    **identity_filters: Any,
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
    body.update({k: v for k, v in identity_filters.items() if v is not None})
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
        team_name: Optional[Union[str, List[str]]] = None,
        school: Optional[Union[str, List[str]]] = None,
        school_id: Optional[List[int]] = None,
        team_id: Optional[List[int]] = None,
        high_school_id: Optional[List[int]] = None,
        high_school_nces_id: Optional[Union[str, List[str]]] = None,
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
            limit, cursor, school=school, school_id=school_id, team_id=team_id,
            high_school_id=high_school_id, high_school_nces_id=high_school_nces_id,
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
                school_resolutions=parsed.school_resolutions,
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


    def times(
        self,
        player_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        event: Optional[str] = None,
        course: Optional[str] = None,
        season: Optional[str] = None,
        best_only: Optional[bool] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[SwimTime]:
        """A swimmer's or diver's legal swims and dives, newest first, with meet,
        event, round, place, time or points, and splits."""

        def fetch(c: Optional[str]) -> SyncPage[SwimTime]:
            raw = self._client.request(
                "GET",
                f"/v1/players/{player_id}/times",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "event": event,
                    "course": course,
                    "season": season,
                    "best_only": best_only,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = SwimTimesPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)


class AsyncPlayers:
    def __init__(self, client) -> None:
        self._client = client

    async def search(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        team_name: Optional[Union[str, List[str]]] = None,
        school: Optional[Union[str, List[str]]] = None,
        school_id: Optional[List[int]] = None,
        team_id: Optional[List[int]] = None,
        high_school_id: Optional[List[int]] = None,
        high_school_nces_id: Optional[Union[str, List[str]]] = None,
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
            limit, cursor, school=school, school_id=school_id, team_id=team_id,
            high_school_id=high_school_id, high_school_nces_id=high_school_nces_id,
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
                school_resolutions=parsed.school_resolutions,
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

    async def times(
        self,
        player_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        event: Optional[str] = None,
        course: Optional[str] = None,
        season: Optional[str] = None,
        best_only: Optional[bool] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[SwimTime]:
        """A swimmer's or diver's legal swims and dives, newest first, with meet,
        event, round, place, time or points, and splits."""

        async def fetch(c: Optional[str]) -> AsyncPage[SwimTime]:
            raw = await self._client.request(
                "GET",
                f"/v1/players/{player_id}/times",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "event": event,
                    "course": course,
                    "season": season,
                    "best_only": best_only,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = SwimTimesPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)
