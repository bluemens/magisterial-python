# Commitments: college commitments, their change log, and the sources behind them.

from __future__ import annotations

from typing import Optional

from .._pagination import AsyncPage, SyncPage
from ..types import (
    CommitmentChange,
    CommitmentChangePage,
    CommitmentEntry,
    CommitmentPage,
    CommitmentSourceList,
)


class Commitments:
    def __init__(self, client) -> None:
        self._client = client

    def list(
        self,
        *,
        sport_path: Optional[str] = None,
        sport: Optional[str] = None,
        gender: Optional[str] = None,
        division: Optional[str] = None,
        grad_year: Optional[str] = None,
        entry_year: Optional[str] = None,
        status: Optional[str] = None,
        team_id: Optional[str] = None,
        school_id: Optional[str] = None,
        ipeds_unitid: Optional[int] = None,
        conference: Optional[str] = None,
        conference_not: Optional[str] = None,
        region: Optional[str] = None,
        region_not: Optional[str] = None,
        state: Optional[str] = None,
        state_not: Optional[str] = None,
        home_state: Optional[str] = None,
        source: Optional[str] = None,
        person_id: Optional[str] = None,
        q: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        committed_since: Optional[str] = None,
        committed_until: Optional[str] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[CommitmentEntry]:
        """College commitments, newest first, across every sport and division,
        reconciled across every public source that lists them. Developer Pro
        and up."""

        def fetch(c: Optional[str]) -> SyncPage[CommitmentEntry]:
            raw = self._client.request(
                "GET",
                "/v1/commitments",
                params={
                    "sport_path": sport_path,
                    "sport": sport,
                    "gender": gender,
                    "division": division,
                    "grad_year": grad_year,
                    "entry_year": entry_year,
                    "status": status,
                    "team_id": team_id,
                    "school_id": school_id,
                    "ipeds_unitid": ipeds_unitid,
                    "conference": conference,
                    "conference_not": conference_not,
                    "region": region,
                    "region_not": region_not,
                    "state": state,
                    "state_not": state_not,
                    "home_state": home_state,
                    "source": source,
                    "person_id": person_id,
                    "q": q,
                    "since": since,
                    "until": until,
                    "committed_since": committed_since,
                    "committed_until": committed_until,
                    "sort": sort,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = CommitmentPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)

    def get(self, commitment_id: int) -> CommitmentEntry:
        """One published commitment. A retracted one is a 404 here and appears in
        `changes` with its reason. Developer Pro and up."""
        return self._client.get_model(f"/v1/commitments/{commitment_id}", CommitmentEntry)

    def changes(
        self,
        *,
        since: Optional[str] = None,
        sport_path: Optional[str] = None,
        sport: Optional[str] = None,
        gender: Optional[str] = None,
        division: Optional[str] = None,
        grad_year: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[CommitmentChange]:
        """The change log of the commitment feed, oldest change first. Poll it with
        `since` to keep a copy of the feed correct. Developer Pro and up."""

        def fetch(c: Optional[str]) -> SyncPage[CommitmentChange]:
            raw = self._client.request(
                "GET",
                "/v1/commitments/changes",
                params={
                    "since": since,
                    "sport_path": sport_path,
                    "sport": sport,
                    "gender": gender,
                    "division": division,
                    "grad_year": grad_year,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = CommitmentChangePage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)

    def sources(self) -> CommitmentSourceList:
        """Every source the commitment feed reads, what its dates mean and when it
        was last read. Developer Pro and up."""
        return self._client.get_model("/v1/commitments/sources", CommitmentSourceList)


class AsyncCommitments:
    def __init__(self, client) -> None:
        self._client = client

    async def list(
        self,
        *,
        sport_path: Optional[str] = None,
        sport: Optional[str] = None,
        gender: Optional[str] = None,
        division: Optional[str] = None,
        grad_year: Optional[str] = None,
        entry_year: Optional[str] = None,
        status: Optional[str] = None,
        team_id: Optional[str] = None,
        school_id: Optional[str] = None,
        ipeds_unitid: Optional[int] = None,
        conference: Optional[str] = None,
        conference_not: Optional[str] = None,
        region: Optional[str] = None,
        region_not: Optional[str] = None,
        state: Optional[str] = None,
        state_not: Optional[str] = None,
        home_state: Optional[str] = None,
        source: Optional[str] = None,
        person_id: Optional[str] = None,
        q: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        committed_since: Optional[str] = None,
        committed_until: Optional[str] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[CommitmentEntry]:
        """College commitments, newest first, across every sport and division,
        reconciled across every public source that lists them. Developer Pro
        and up."""

        async def fetch(c: Optional[str]) -> AsyncPage[CommitmentEntry]:
            raw = await self._client.request(
                "GET",
                "/v1/commitments",
                params={
                    "sport_path": sport_path,
                    "sport": sport,
                    "gender": gender,
                    "division": division,
                    "grad_year": grad_year,
                    "entry_year": entry_year,
                    "status": status,
                    "team_id": team_id,
                    "school_id": school_id,
                    "ipeds_unitid": ipeds_unitid,
                    "conference": conference,
                    "conference_not": conference_not,
                    "region": region,
                    "region_not": region_not,
                    "state": state,
                    "state_not": state_not,
                    "home_state": home_state,
                    "source": source,
                    "person_id": person_id,
                    "q": q,
                    "since": since,
                    "until": until,
                    "committed_since": committed_since,
                    "committed_until": committed_until,
                    "sort": sort,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = CommitmentPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)

    async def get(self, commitment_id: int) -> CommitmentEntry:
        """One published commitment. A retracted one is a 404 here and appears in
        `changes` with its reason. Developer Pro and up."""
        return await self._client.get_model(f"/v1/commitments/{commitment_id}", CommitmentEntry)

    async def changes(
        self,
        *,
        since: Optional[str] = None,
        sport_path: Optional[str] = None,
        sport: Optional[str] = None,
        gender: Optional[str] = None,
        division: Optional[str] = None,
        grad_year: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[CommitmentChange]:
        """The change log of the commitment feed, oldest change first. Poll it with
        `since` to keep a copy of the feed correct. Developer Pro and up."""

        async def fetch(c: Optional[str]) -> AsyncPage[CommitmentChange]:
            raw = await self._client.request(
                "GET",
                "/v1/commitments/changes",
                params={
                    "since": since,
                    "sport_path": sport_path,
                    "sport": sport,
                    "gender": gender,
                    "division": division,
                    "grad_year": grad_year,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = CommitmentChangePage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)

    async def sources(self) -> CommitmentSourceList:
        """Every source the commitment feed reads, what its dates mean and when it
        was last read. Developer Pro and up."""
        return await self._client.get_model("/v1/commitments/sources", CommitmentSourceList)
