# Schools: institution identity, cross-sport and cross-division.

from __future__ import annotations

from typing import Literal, Optional

from .._pagination import AsyncPage, SyncPage
from ..types import SchoolDetail, SchoolPage, SchoolSummary, SchoolDiscoveryResponse


class Schools:
    def __init__(self, client) -> None:
        self._client = client

    def list(
        self,
        *,
        q: Optional[str] = None,
        state: Optional[str] = None,
        ipeds_unitid: Optional[int] = None,
        control: Optional[str] = None,
        religious_affiliation: Optional[str] = None,
        admission_rate_min: Optional[float] = None,
        admission_rate_max: Optional[float] = None,
        undergrad_enrollment_min: Optional[int] = None,
        undergrad_enrollment_max: Optional[int] = None,
        region: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[SchoolSummary]:
        """Institutions, alphabetical, with the federal IPEDS UNITID where
        matched, and each school's College Scorecard `profile` (admissions,
        SAT/ACT ranges, enrollment, tuition, net price, outcomes; null where no
        federal profile is held). Cross-division and cross-sport; no scope
        parameters. Look a school up by `ipeds_unitid` to map your own records
        onto ours, then fetch its programs with `get`."""

        def fetch(c: Optional[str]) -> SyncPage[SchoolSummary]:
            raw = self._client.request(
                "GET",
                "/v1/schools",
                params={
                    "q": q,
                    "state": state,
                    "ipeds_unitid": ipeds_unitid,
                    "control": control,
                    "religious_affiliation": religious_affiliation,
                    "admission_rate_min": admission_rate_min,
                    "admission_rate_max": admission_rate_max,
                    "undergrad_enrollment_min": undergrad_enrollment_min,
                    "undergrad_enrollment_max": undergrad_enrollment_max,
                    "region": region,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = SchoolPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)

    def resolve(
        self, *, kind: Literal["college", "high_school"] = "college",
        query: Optional[str] = None, school_id: Optional[int] = None,
        ipeds_unitid: Optional[int] = None, high_school_id: Optional[int] = None,
        nces_id: Optional[str] = None, sport: Optional[str] = None,
        gender: Optional[str] = None, division: Optional[str] = None,
        city: Optional[str] = None, state: Optional[str] = None, country: Optional[str] = None,
    ) -> SchoolDiscoveryResponse:
        """Discover identities, choose candidates from context, then retain IDs.

        College names/aliases identify automatically; partial/typo candidates
        include location and programs. High schools use their own IDs/NCES.
        """
        body = {k: v for k, v in dict(kind=kind, query=query, school_id=school_id,
            ipeds_unitid=ipeds_unitid, high_school_id=high_school_id, nces_id=nces_id,
            sport=sport, gender=gender, division=division, city=city, state=state,
            country=country).items() if v is not None}
        raw = self._client.request("POST", "/v1/schools/resolve", json=body, retryable=True)
        return SchoolDiscoveryResponse.model_validate(raw)

    def get(self, school_id: int) -> SchoolDetail:
        """One institution, its College Scorecard `profile`, and every program
        it fields across sports and divisions (team ids for the scoped team
        endpoints). Athletics stats stay behind the sport/division-scoped
        endpoints."""
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
        control: Optional[str] = None,
        religious_affiliation: Optional[str] = None,
        admission_rate_min: Optional[float] = None,
        admission_rate_max: Optional[float] = None,
        undergrad_enrollment_min: Optional[int] = None,
        undergrad_enrollment_max: Optional[int] = None,
        region: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[SchoolSummary]:
        """Institutions, alphabetical, with the federal IPEDS UNITID where
        matched, and each school's College Scorecard `profile` (admissions,
        SAT/ACT ranges, enrollment, tuition, net price, outcomes; null where no
        federal profile is held). Cross-division and cross-sport; no scope
        parameters. Look a school up by `ipeds_unitid` to map your own records
        onto ours, then fetch its programs with `get`."""

        async def fetch(c: Optional[str]) -> AsyncPage[SchoolSummary]:
            raw = await self._client.request(
                "GET",
                "/v1/schools",
                params={
                    "q": q,
                    "state": state,
                    "ipeds_unitid": ipeds_unitid,
                    "control": control,
                    "religious_affiliation": religious_affiliation,
                    "admission_rate_min": admission_rate_min,
                    "admission_rate_max": admission_rate_max,
                    "undergrad_enrollment_min": undergrad_enrollment_min,
                    "undergrad_enrollment_max": undergrad_enrollment_max,
                    "region": region,
                    "limit": limit,
                    "cursor": c,
                },
            )
            parsed = SchoolPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)

    async def resolve(
        self, *, kind: Literal["college", "high_school"] = "college",
        query: Optional[str] = None, school_id: Optional[int] = None,
        ipeds_unitid: Optional[int] = None, high_school_id: Optional[int] = None,
        nces_id: Optional[str] = None, sport: Optional[str] = None,
        gender: Optional[str] = None, division: Optional[str] = None,
        city: Optional[str] = None, state: Optional[str] = None, country: Optional[str] = None,
    ) -> SchoolDiscoveryResponse:
        """Discover identities, choose candidates from context, then retain IDs.

        College names/aliases identify automatically; partial/typo candidates
        include location and programs. High schools use their own IDs/NCES.
        """
        body = {k: v for k, v in dict(kind=kind, query=query, school_id=school_id,
            ipeds_unitid=ipeds_unitid, high_school_id=high_school_id, nces_id=nces_id,
            sport=sport, gender=gender, division=division, city=city, state=state,
            country=country).items() if v is not None}
        raw = await self._client.request("POST", "/v1/schools/resolve", json=body, retryable=True)
        return SchoolDiscoveryResponse.model_validate(raw)

    async def get(self, school_id: int) -> SchoolDetail:
        """One institution, its College Scorecard `profile`, and every program
        it fields across sports and divisions (team ids for the scoped team
        endpoints). Athletics stats stay behind the sport/division-scoped
        endpoints."""
        return await self._client.get_model(f"/v1/schools/{school_id}", SchoolDetail)
