# Schools: institution identity, cross-sport and cross-division.

from __future__ import annotations

from typing import Optional

from .._pagination import AsyncPage, SyncPage
from ..types import SchoolDetail, SchoolPage, SchoolRef


class Schools:
    def __init__(self, client) -> None:
        self._client = client

    def list(
        self,
        *,
        q: Optional[str] = None,
        state: Optional[str] = None,
        ipeds_unitid: Optional[int] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[SchoolRef]:
        """Institutions, alphabetical, with the federal IPEDS UNITID where
        matched. Cross-division and cross-sport; no scope parameters. Look a
        school up by `ipeds_unitid` to map your own records onto ours, then
        fetch its programs with `get`."""

        def fetch(c: Optional[str]) -> SyncPage[SchoolRef]:
            raw = self._client.request(
                "GET",
                "/v1/schools",
                params={
                    "q": q,
                    "state": state,
                    "ipeds_unitid": ipeds_unitid,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = SchoolPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)

    def get(self, school_id: int) -> SchoolDetail:
        """One institution plus every program it fields across sports and
        divisions (team ids for the scoped team endpoints). Identity only;
        stats stay behind the sport/division-scoped endpoints."""
        return self._client.get_model(f"/v1/schools/{school_id}", SchoolDetail)


class AsyncSchools:
    def __init__(self, client) -> None:
        self._client = client

    async def list(
        self,
        *,
        q: Optional[str] = None,
        state: Optional[str] = None,
        ipeds_unitid: Optional[int] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[SchoolRef]:
        """Institutions, alphabetical, with the federal IPEDS UNITID where
        matched. Cross-division and cross-sport; no scope parameters. Look a
        school up by `ipeds_unitid` to map your own records onto ours, then
        fetch its programs with `get`."""

        async def fetch(c: Optional[str]) -> AsyncPage[SchoolRef]:
            raw = await self._client.request(
                "GET",
                "/v1/schools",
                params={
                    "q": q,
                    "state": state,
                    "ipeds_unitid": ipeds_unitid,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = SchoolPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)

    async def get(self, school_id: int) -> SchoolDetail:
        """One institution plus every program it fields across sports and
        divisions (team ids for the scoped team endpoints). Identity only;
        stats stay behind the sport/division-scoped endpoints."""
        return await self._client.get_model(f"/v1/schools/{school_id}", SchoolDetail)
