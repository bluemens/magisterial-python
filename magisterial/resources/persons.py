# Persons: cross-program careers and transfer histories.

from __future__ import annotations

from typing import Optional

from ..types import PlayerDetail, TransferListResponse


class Persons:
    def __init__(self, client) -> None:
        self._client = client

    def get(
        self, person_id: int, *, sport: str, gender: Optional[str] = None
    ) -> PlayerDetail:
        """A person's career across every program/division in one sport."""
        return self._client.get_model(
            f"/v1/persons/{person_id}", PlayerDetail, sport=sport, gender=gender
        )

    def transfers(self, person_id: int) -> TransferListResponse:
        """Every school-change edge for a person, across divisions."""
        return self._client.get_model(
            f"/v1/persons/{person_id}/transfers", TransferListResponse
        )


class AsyncPersons:
    def __init__(self, client) -> None:
        self._client = client

    async def get(
        self, person_id: int, *, sport: str, gender: Optional[str] = None
    ) -> PlayerDetail:
        """A person's career across every program/division in one sport."""
        return await self._client.get_model(
            f"/v1/persons/{person_id}", PlayerDetail, sport=sport, gender=gender
        )

    async def transfers(self, person_id: int) -> TransferListResponse:
        """Every school-change edge for a person, across divisions."""
        return await self._client.get_model(
            f"/v1/persons/{person_id}/transfers", TransferListResponse
        )
