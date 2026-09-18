# Managed athletes (Enterprise): invite, list, and revoke the athlete
# authorizations that back `on_behalf_of` delegated coach-contact reads.

from __future__ import annotations

from typing import Any, Dict, Optional

from .._pagination import AsyncPage, SyncPage
from ..types import (
    ManagedAthleteAccessEntry,
    ManagedAthleteAccessPage,
    ManagedAthleteEntry,
    ManagedAthletePage,
    ManagedAthleteRevokeResponse,
)


def _create_body(
    player_id: int,
    email: Optional[str],
    sport_path: Optional[str],
    organization_name: Optional[str],
) -> Dict[str, Any]:
    body: Dict[str, Any] = {"player_id": player_id}
    if email is not None:
        body["email"] = email
    if sport_path is not None:
        body["sport_path"] = sport_path
    if organization_name is not None:
        body["organization_name"] = organization_name
    return body


class Athletes:
    def __init__(self, client) -> None:
        self._client = client

    def create(
        self,
        player_id: int,
        *,
        email: Optional[str] = None,
        sport_path: Optional[str] = None,
        organization_name: Optional[str] = None,
    ) -> ManagedAthleteEntry:
        """Invite one athlete to authorize your account. `email` defaults to
        the athlete's on-file contact; a supplied address is accepted only
        when it matches that contact or the athlete's school .edu domain.
        Re-inviting a declined, revoked, or expired athlete reuses the same
        grant id. Not retried automatically."""
        raw = self._client.request(
            "POST",
            "/v1/athletes",
            json=_create_body(player_id, email, sport_path, organization_name),
        )
        return ManagedAthleteEntry.model_validate(raw)

    def list(
        self,
        *,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[ManagedAthleteEntry]:
        """Every athlete who has been invited to, or has authorized, your
        account, newest first. `status` filters to invited | active |
        declined | revoked | expired. `active` grants are the ones
        `on_behalf_of` accepts."""

        def fetch(c: Optional[str]) -> SyncPage[ManagedAthleteEntry]:
            raw = self._client.request(
                "GET",
                "/v1/athletes",
                params={"status": status, "limit": limit, "cursor": c},
            )
            parsed = ManagedAthletePage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)

    def get(self, grant_id: str) -> ManagedAthleteEntry:
        """One grant by id, including its current status and timestamps."""
        return self._client.get_model(f"/v1/athletes/{grant_id}", ManagedAthleteEntry)

    def resend_invite(self, grant_id: str) -> ManagedAthleteEntry:
        """Issue a fresh 14-day invitation link to the same address. Only
        `invited` grants can be resent; re-invite a declined, revoked, or
        expired athlete with `create` instead. Not retried automatically."""
        raw = self._client.request("POST", f"/v1/athletes/{grant_id}/resend")
        return ManagedAthleteEntry.model_validate(raw)

    def revoke(self, grant_id: str) -> ManagedAthleteRevokeResponse:
        """End the authorization (or cancel a pending invitation). Delegated
        reads for the athlete fail from the next request; the grant stays
        listed as `revoked` for your records."""
        raw = self._client.request("DELETE", f"/v1/athletes/{grant_id}")
        return ManagedAthleteRevokeResponse.model_validate(raw)

    def list_access(
        self,
        grant_id: str,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> SyncPage[ManagedAthleteAccessEntry]:
        """Every request that returned contact fields on this athlete's
        behalf, newest first. The athlete sees the same log in their
        settings."""

        def fetch(c: Optional[str]) -> SyncPage[ManagedAthleteAccessEntry]:
            raw = self._client.request(
                "GET",
                f"/v1/athletes/{grant_id}/access",
                params={"limit": limit, "cursor": c},
            )
            parsed = ManagedAthleteAccessPage.model_validate(raw)
            return SyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return fetch(cursor)


class AsyncAthletes:
    def __init__(self, client) -> None:
        self._client = client

    async def create(
        self,
        player_id: int,
        *,
        email: Optional[str] = None,
        sport_path: Optional[str] = None,
        organization_name: Optional[str] = None,
    ) -> ManagedAthleteEntry:
        """Invite one athlete to authorize your account. `email` defaults to
        the athlete's on-file contact; a supplied address is accepted only
        when it matches that contact or the athlete's school .edu domain.
        Re-inviting a declined, revoked, or expired athlete reuses the same
        grant id. Not retried automatically."""
        raw = await self._client.request(
            "POST",
            "/v1/athletes",
            json=_create_body(player_id, email, sport_path, organization_name),
        )
        return ManagedAthleteEntry.model_validate(raw)

    async def list(
        self,
        *,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[ManagedAthleteEntry]:
        """Every athlete who has been invited to, or has authorized, your
        account, newest first. `status` filters to invited | active |
        declined | revoked | expired. `active` grants are the ones
        `on_behalf_of` accepts."""

        async def fetch(c: Optional[str]) -> AsyncPage[ManagedAthleteEntry]:
            raw = await self._client.request(
                "GET",
                "/v1/athletes",
                params={"status": status, "limit": limit, "cursor": c},
            )
            parsed = ManagedAthletePage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)

    async def get(self, grant_id: str) -> ManagedAthleteEntry:
        """One grant by id, including its current status and timestamps."""
        return await self._client.get_model(
            f"/v1/athletes/{grant_id}", ManagedAthleteEntry
        )

    async def resend_invite(self, grant_id: str) -> ManagedAthleteEntry:
        """Issue a fresh 14-day invitation link to the same address. Only
        `invited` grants can be resent; re-invite a declined, revoked, or
        expired athlete with `create` instead. Not retried automatically."""
        raw = await self._client.request("POST", f"/v1/athletes/{grant_id}/resend")
        return ManagedAthleteEntry.model_validate(raw)

    async def revoke(self, grant_id: str) -> ManagedAthleteRevokeResponse:
        """End the authorization (or cancel a pending invitation). Delegated
        reads for the athlete fail from the next request; the grant stays
        listed as `revoked` for your records."""
        raw = await self._client.request("DELETE", f"/v1/athletes/{grant_id}")
        return ManagedAthleteRevokeResponse.model_validate(raw)

    async def list_access(
        self,
        grant_id: str,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> AsyncPage[ManagedAthleteAccessEntry]:
        """Every request that returned contact fields on this athlete's
        behalf, newest first. The athlete sees the same log in their
        settings."""

        async def fetch(c: Optional[str]) -> AsyncPage[ManagedAthleteAccessEntry]:
            raw = await self._client.request(
                "GET",
                f"/v1/athletes/{grant_id}/access",
                params={"limit": limit, "cursor": c},
            )
            parsed = ManagedAthleteAccessPage.model_validate(raw)
            return AsyncPage(parsed.data, parsed.next_cursor, parsed.has_more, fetch)

        return await fetch(cursor)
