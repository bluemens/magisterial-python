# Swimming & diving: meets, results by event.

from __future__ import annotations

from typing import Optional

from .._pagination import AsyncPage, SyncPage
from ..types import (
    SwimEventResults,
    SwimMeetDetail,
    SwimMeetPage,
    SwimMeetResultsPage,
    SwimMeetSummary,
)


class Swim:
    def __init__(self, client) -> None:
        self._client = client

    def list_meets(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        season: Optional[str] = None,
        meet_type: Optional[str] = None,
        course: Optional[str] = None,
        team_id: Optional[str] = None,
        start_date_min: Optional[str] = None,
        start_date_max: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[SwimMeetSummary]:
        """Swimming & diving meets holding results in the scope, newest first."""

        def fetch(c: Optional[str]) -> SyncPage[SwimMeetSummary]:
            raw = self._client.request(
                "GET",
                "/v1/swim/meets",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "season": season,
                    "meet_type": meet_type,
                    "course": course,
                    "team_id": team_id,
                    "start_date_min": start_date_min,
                    "start_date_max": start_date_max,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = SwimMeetPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)

    def get_meet(
        self,
        meet_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
    ) -> SwimMeetDetail:
        """One meet: details, final team scores, and the events it holds results
        for (read the results with `list_meet_results`)."""
        return self._client.get_model(
            f"/v1/swim/meets/{meet_id}",
            SwimMeetDetail,
            sport=sport,
            division=division,
            gender=gender,
        )

    def list_meet_results(
        self,
        meet_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        event: Optional[str] = None,
        round: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[SwimEventResults]:
        """One meet's results in the scope, grouped by event in catalog order.
        `limit` counts results, not events."""

        def fetch(c: Optional[str]) -> SyncPage[SwimEventResults]:
            raw = self._client.request(
                "GET",
                f"/v1/swim/meets/{meet_id}/results",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "event": event,
                    "round": round,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = SwimMeetResultsPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)


class AsyncSwim:
    def __init__(self, client) -> None:
        self._client = client

    async def list_meets(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        season: Optional[str] = None,
        meet_type: Optional[str] = None,
        course: Optional[str] = None,
        team_id: Optional[str] = None,
        start_date_min: Optional[str] = None,
        start_date_max: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[SwimMeetSummary]:
        """Swimming & diving meets holding results in the scope, newest first."""

        async def fetch(c: Optional[str]) -> AsyncPage[SwimMeetSummary]:
            raw = await self._client.request(
                "GET",
                "/v1/swim/meets",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "season": season,
                    "meet_type": meet_type,
                    "course": course,
                    "team_id": team_id,
                    "start_date_min": start_date_min,
                    "start_date_max": start_date_max,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = SwimMeetPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)

    async def get_meet(
        self,
        meet_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
    ) -> SwimMeetDetail:
        """One meet: details, final team scores, and the events it holds results
        for (read the results with `list_meet_results`)."""
        return await self._client.get_model(
            f"/v1/swim/meets/{meet_id}",
            SwimMeetDetail,
            sport=sport,
            division=division,
            gender=gender,
        )

    async def list_meet_results(
        self,
        meet_id: int,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        event: Optional[str] = None,
        round: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[SwimEventResults]:
        """One meet's results in the scope, grouped by event in catalog order.
        `limit` counts results, not events."""

        async def fetch(c: Optional[str]) -> AsyncPage[SwimEventResults]:
            raw = await self._client.request(
                "GET",
                f"/v1/swim/meets/{meet_id}/results",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "event": event,
                    "round": round,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = SwimMeetResultsPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)
