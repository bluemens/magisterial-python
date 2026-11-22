# Recruit fit: score a soccer athlete against every program.

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..types import RecruitFitPage


def _body(**fields: Any) -> Dict[str, Any]:
    return {key: value for key, value in fields.items() if value is not None}


class RecruitFit:
    def __init__(self, client) -> None:
        self._client = client

    def score(
        self,
        *,
        sport_path: str,
        grad_year: int,
        position: Optional[str] = None,
        home_state: Optional[str] = None,
        club_league: Optional[str] = None,
        target_divisions: Optional[List[str]] = None,
        target_regions: Optional[List[str]] = None,
        must_haves: Optional[List[str]] = None,
        max_distance_miles: Optional[int] = None,
        max_annual_cost_usd: Optional[int] = None,
        intended_major: Optional[str] = None,
        team_ids: Optional[List[int]] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> RecruitFitPage:
        """Programs in rank order for one athlete's answers. Takes no name or
        other identity. `fit` measures how a program recruits and whether it
        has room, not how good a player is. Pass `next_cursor` as `cursor` for
        the next page. Soccer only; Developer Pro and up."""
        raw = self._client.request(
            "POST",
            "/v1/recruit/fit",
            json=_body(
                sport_path=sport_path, grad_year=grad_year, position=position, home_state=home_state,
                club_league=club_league, target_divisions=target_divisions, target_regions=target_regions,
                must_haves=must_haves, max_distance_miles=max_distance_miles,
                max_annual_cost_usd=max_annual_cost_usd, intended_major=intended_major, team_ids=team_ids,
                limit=limit, cursor=cursor,
            ),
            retryable=True,  # POST, but a pure read.
        )
        return RecruitFitPage.model_validate(raw)


class AsyncRecruitFit:
    def __init__(self, client) -> None:
        self._client = client

    async def score(
        self,
        *,
        sport_path: str,
        grad_year: int,
        position: Optional[str] = None,
        home_state: Optional[str] = None,
        club_league: Optional[str] = None,
        target_divisions: Optional[List[str]] = None,
        target_regions: Optional[List[str]] = None,
        must_haves: Optional[List[str]] = None,
        max_distance_miles: Optional[int] = None,
        max_annual_cost_usd: Optional[int] = None,
        intended_major: Optional[str] = None,
        team_ids: Optional[List[int]] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> RecruitFitPage:
        """Programs in rank order for one athlete's answers. See `RecruitFit.score`."""
        raw = await self._client.request(
            "POST",
            "/v1/recruit/fit",
            json=_body(
                sport_path=sport_path, grad_year=grad_year, position=position, home_state=home_state,
                club_league=club_league, target_divisions=target_divisions, target_regions=target_regions,
                must_haves=must_haves, max_distance_miles=max_distance_miles,
                max_annual_cost_usd=max_annual_cost_usd, intended_major=intended_major, team_ids=team_ids,
                limit=limit, cursor=cursor,
            ),
            retryable=True,
        )
        return RecruitFitPage.model_validate(raw)
