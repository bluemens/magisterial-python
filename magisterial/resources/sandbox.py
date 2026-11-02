# Sandbox: trigger events in the test-key world.

from __future__ import annotations

from typing import Any, Dict, Optional

from ..types import SandboxEventResponse


class Sandbox:
    def __init__(self, client) -> None:
        self._client = client

    def create_event(
        self,
        *,
        type: str,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        name: Optional[str] = None,
        team_id: Optional[int] = None,
    ) -> SandboxEventResponse:
        """Make something happen in the sandbox world (test keys only): a portal
        entry, or a player or coach joining a program. Never auto-retried."""
        body: Dict[str, Any] = {
            "type": type,
            "sport": sport,
            "division": division,
        }
        if gender is not None:
            body["gender"] = gender
        if name is not None:
            body["name"] = name
        if team_id is not None:
            body["team_id"] = team_id
        raw = self._client.request("POST", "/v1/sandbox/events", json=body)
        return SandboxEventResponse.model_validate(raw)


class AsyncSandbox:
    def __init__(self, client) -> None:
        self._client = client

    async def create_event(
        self,
        *,
        type: str,
        sport: str,
        division: str,
        gender: Optional[str] = None,
        name: Optional[str] = None,
        team_id: Optional[int] = None,
    ) -> SandboxEventResponse:
        """Make something happen in the sandbox world (test keys only): a portal
        entry, or a player or coach joining a program. Never auto-retried."""
        body: Dict[str, Any] = {
            "type": type,
            "sport": sport,
            "division": division,
        }
        if gender is not None:
            body["gender"] = gender
        if name is not None:
            body["name"] = name
        if team_id is not None:
            body["team_id"] = team_id
        raw = await self._client.request("POST", "/v1/sandbox/events", json=body)
        return SandboxEventResponse.model_validate(raw)
