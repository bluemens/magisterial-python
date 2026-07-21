# Transfer portal feed (usage-billed per request).

from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

from .._pagination import AsyncPage, SyncPage
from ..types import PortalEntry, PortalPage


def _since_str(since: Union[str, datetime, None]) -> Optional[str]:
    return since.isoformat() if isinstance(since, datetime) else since


class Portal:
    def __init__(self, client) -> None:
        self._client = client

    def list(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        status: Optional[str] = None,
        since: Union[str, datetime, None] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[PortalEntry]:
        """Live portal entries, newest first. Usage-billed per request —
        prefer ``since`` for incremental polling over re-reading full pages.
        ``contacts`` is populated only on PRO/MAX plans for the sport."""
        since_value = _since_str(since)

        def fetch(c: Optional[str]) -> SyncPage[PortalEntry]:
            raw = self._client.request(
                "GET",
                "/v1/portal",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "status": status,
                    "since": since_value,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = PortalPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)


class AsyncPortal:
    def __init__(self, client) -> None:
        self._client = client

    async def list(
        self,
        *,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        status: Optional[str] = None,
        since: Union[str, datetime, None] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[PortalEntry]:
        """Live portal entries, newest first. Usage-billed per request —
        prefer ``since`` for incremental polling over re-reading full pages.
        ``contacts`` is populated only on PRO/MAX plans for the sport."""
        since_value = _since_str(since)

        async def fetch(c: Optional[str]) -> AsyncPage[PortalEntry]:
            raw = await self._client.request(
                "GET",
                "/v1/portal",
                params={
                    "sport": sport,
                    "division": division,
                    "gender": gender,
                    "status": status,
                    "since": since_value,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = PortalPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)
