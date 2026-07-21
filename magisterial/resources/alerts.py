# Standing transfer-portal watch alerts (usage-billed monthly per alert).

from __future__ import annotations

from typing import Any, Dict, Optional

from ..types import (
    AlertDeleteResponse,
    AlertListResponse,
    AlertMatchListResponse,
    AlertSummary,
)


class Alerts:
    def __init__(self, client) -> None:
        self._client = client

    def create(
        self,
        *,
        name: str,
        sport: str,
        division: str,
        filters: Dict[str, Any],
        gender: Optional[str] = None,
        webhook_url: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> AlertSummary:
        """Create a portal watch. Billed per active alert per calendar month,
        charged at creation; deleting within the month does not refund."""
        body: Dict[str, Any] = {
            "name": name,
            "sport": sport,
            "division": division,
            "filters": filters,
        }
        if gender is not None:
            body["gender"] = gender
        if webhook_url is not None:
            body["webhook_url"] = webhook_url
        if enabled is not None:
            body["enabled"] = enabled
        raw = self._client.request("POST", "/v1/alerts", json=body)
        return AlertSummary.model_validate(raw)

    def list(self) -> AlertListResponse:
        """Every alert created through the API for this account."""
        return self._client.get_model("/v1/alerts", AlertListResponse)

    def delete(self, alert_id: str) -> AlertDeleteResponse:
        """Delete an alert (no refund for the current month)."""
        raw = self._client.request("DELETE", f"/v1/alerts/{alert_id}")
        return AlertDeleteResponse.model_validate(raw)

    def matches(
        self, alert_id: str, *, limit: Optional[int] = None
    ) -> AlertMatchListResponse:
        """Recent portal entries that matched an alert (poll this until
        webhook delivery ships)."""
        return self._client.get_model(
            f"/v1/alerts/{alert_id}/matches", AlertMatchListResponse, limit=limit
        )


class AsyncAlerts:
    def __init__(self, client) -> None:
        self._client = client

    async def create(
        self,
        *,
        name: str,
        sport: str,
        division: str,
        filters: Dict[str, Any],
        gender: Optional[str] = None,
        webhook_url: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> AlertSummary:
        """Create a portal watch. Billed per active alert per calendar month,
        charged at creation; deleting within the month does not refund."""
        body: Dict[str, Any] = {
            "name": name,
            "sport": sport,
            "division": division,
            "filters": filters,
        }
        if gender is not None:
            body["gender"] = gender
        if webhook_url is not None:
            body["webhook_url"] = webhook_url
        if enabled is not None:
            body["enabled"] = enabled
        raw = await self._client.request("POST", "/v1/alerts", json=body)
        return AlertSummary.model_validate(raw)

    async def list(self) -> AlertListResponse:
        """Every alert created through the API for this account."""
        return await self._client.get_model("/v1/alerts", AlertListResponse)

    async def delete(self, alert_id: str) -> AlertDeleteResponse:
        """Delete an alert (no refund for the current month)."""
        raw = await self._client.request("DELETE", f"/v1/alerts/{alert_id}")
        return AlertDeleteResponse.model_validate(raw)

    async def matches(
        self, alert_id: str, *, limit: Optional[int] = None
    ) -> AlertMatchListResponse:
        """Recent portal entries that matched an alert (poll this until
        webhook delivery ships)."""
        return await self._client.get_model(
            f"/v1/alerts/{alert_id}/matches", AlertMatchListResponse, limit=limit
        )
