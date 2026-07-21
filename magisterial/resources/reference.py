# Reference data: sports, divisions, conferences, filter catalog, coverage.

from __future__ import annotations

from typing import Any, Dict, Optional

from ..types import SportListResponse, StringListResponse


class Reference:
    def __init__(self, client) -> None:
        self._client = client

    def sports(self) -> SportListResponse:
        """Supported sports and the genders each carries."""
        return self._client.get_model("/v1/sports", SportListResponse)

    def divisions(self) -> StringListResponse:
        """Every public division value, e.g. D1, D1-FBS, NAIA, NJCAA-D1."""
        return self._client.get_model("/v1/divisions", StringListResponse)

    def conferences(
        self, *, sport: str, division: str, gender: Optional[str] = None
    ) -> StringListResponse:
        """Conferences present in one sport/division scope."""
        return self._client.get_model(
            "/v1/conferences",
            StringListResponse,
            sport=sport,
            division=division,
            gender=gender,
        )

    def coverage(self) -> Dict[str, Any]:
        """Data-coverage matrix: per sport/division/season counts."""
        return self._client.request("GET", "/v1/coverage")

    def filter_catalog(self, *, sport: Optional[str] = None) -> Dict[str, Any]:
        """Queryable/sortable fields per sport (feeds players.search sort_by
        and alert filter DSLs)."""
        return self._client.request(
            "GET", "/v1/filters/catalog", params={"sport": sport}
        )


class AsyncReference:
    def __init__(self, client) -> None:
        self._client = client

    async def sports(self) -> SportListResponse:
        """Supported sports and the genders each carries."""
        return await self._client.get_model("/v1/sports", SportListResponse)

    async def divisions(self) -> StringListResponse:
        """Every public division value, e.g. D1, D1-FBS, NAIA, NJCAA-D1."""
        return await self._client.get_model("/v1/divisions", StringListResponse)

    async def conferences(
        self, *, sport: str, division: str, gender: Optional[str] = None
    ) -> StringListResponse:
        """Conferences present in one sport/division scope."""
        return await self._client.get_model(
            "/v1/conferences",
            StringListResponse,
            sport=sport,
            division=division,
            gender=gender,
        )

    async def coverage(self) -> Dict[str, Any]:
        """Data-coverage matrix: per sport/division/season counts."""
        return await self._client.request("GET", "/v1/coverage")

    async def filter_catalog(self, *, sport: Optional[str] = None) -> Dict[str, Any]:
        """Queryable/sortable fields per sport (feeds players.search sort_by
        and alert filter DSLs)."""
        return await self._client.request(
            "GET", "/v1/filters/catalog", params={"sport": sport}
        )
