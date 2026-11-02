"""v0.7.0 surface: commitments, golf, swimming & diving, tennis, sandbox
events, movement, commitment and portal supply change logs, regions, eligibility rules,
team postseason and rankings, and the new list filters. Each method is
checked for the request it sends and the model it returns, against an
httpx.MockTransport (no network)."""

from __future__ import annotations

import asyncio
import datetime as dt
import enum
import json
import typing
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from pydantic import BaseModel

from magisterial import APIStatusError, AsyncMagisterial, Magisterial, types

API_KEY = "mag_test_abc123"


def minimal(model: typing.Type[BaseModel]) -> dict:
    """A JSON body carrying only `model`'s required fields, enough for the
    SDK's model_validate to accept it."""
    body = {}
    for name, field in model.model_fields.items():
        if not field.is_required():
            continue
        body[field.alias or name] = _value(field.annotation)
    return body


def _value(annotation):
    origin = typing.get_origin(annotation)
    args = [a for a in typing.get_args(annotation) if a is not type(None)]
    if origin is typing.Union or str(origin) == "types.UnionType":
        return _value(args[0])
    if origin is typing.Literal:
        return args[0]
    if origin in (list, typing.List):
        return []
    if origin in (dict, typing.Dict):
        return {}
    if isinstance(annotation, type):
        if issubclass(annotation, BaseModel):
            return minimal(annotation)
        if issubclass(annotation, enum.Enum):
            return next(iter(annotation)).value
        if issubclass(annotation, bool):
            return True
        if issubclass(annotation, int):
            return 1
        if issubclass(annotation, float):
            return 1.0
        if issubclass(annotation, dt.datetime):
            return "2026-11-02T00:00:00Z"
        if issubclass(annotation, dt.date):
            return "2026-11-02"
    if "Datetime" in getattr(annotation, "__name__", ""):  # pydantic AwareDatetime / NaiveDatetime
        return "2026-11-02T00:00:00Z"
    return "x"


class Recorder:
    def __init__(self, body):
        self.body = body
        self.requests = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(200, json=self.body)

    @property
    def last(self):
        req = self.requests[-1]
        parts = urlsplit(str(req.url))
        query = {k: v[0] for k, v in parse_qs(parts.query).items()}
        return req.method, parts.path, query


def sync_client(handler) -> Magisterial:
    return Magisterial(api_key=API_KEY, http_client=httpx.Client(transport=httpx.MockTransport(handler)))


def async_client(handler) -> AsyncMagisterial:
    return AsyncMagisterial(api_key=API_KEY, http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))


GOLF = dict(sport="golf", division="D1")
SWIM = dict(sport="swimming-and-diving", division="D1", gender="women")
TENNIS = dict(sport="tennis", division="D1")

# (call, response model, expected path, expected query)
CASES = [
    (lambda c: c.commitments.list(sport="volleyball", gender="women", grad_year="2027", region="NJCAA Region IV", limit=5),
     types.CommitmentPage, "/v1/commitments",
     {"sport": "volleyball", "gender": "women", "grad_year": "2027", "region": "NJCAA Region IV", "limit": "5"}),
    (lambda c: c.commitments.get(42), types.CommitmentEntry, "/v1/commitments/42", {}),
    (lambda c: c.commitments.changes(since="2026-11-01T00:00:00Z", division="D2"),
     types.CommitmentChangePage, "/v1/commitments/changes", {"since": "2026-11-01T00:00:00Z", "division": "D2"}),
    (lambda c: c.commitments.sources(), types.CommitmentSourceList, "/v1/commitments/sources", {}),
    (lambda c: c.golf.list_tournaments(**GOLF, season="2026", status="final"),
     types.GolfTournamentPage, "/v1/golf/tournaments", {**GOLF, "season": "2026", "status": "final"}),
    (lambda c: c.golf.get_tournament(7, **GOLF, gender="women"),
     types.GolfTournamentDetail, "/v1/golf/tournaments/7", {**GOLF, "gender": "women"}),
    (lambda c: c.golf.list_ratings(**GOLF, entity="team", as_of="2026-10-01"),
     types.GolfRatingPage, "/v1/golf/ratings", {**GOLF, "entity": "team", "as_of": "2026-10-01"}),
    (lambda c: c.swim.list_meets(**SWIM, meet_type="ncaa", course="SCY"),
     types.SwimMeetPage, "/v1/swim/meets", {**SWIM, "meet_type": "ncaa", "course": "SCY"}),
    (lambda c: c.swim.get_meet(9, **SWIM), types.SwimMeetDetail, "/v1/swim/meets/9", SWIM),
    (lambda c: c.swim.list_meet_results(9, **SWIM, event="SCY-100-FR", round="final"),
     types.SwimMeetResultsPage, "/v1/swim/meets/9/results", {**SWIM, "event": "SCY-100-FR", "round": "final"}),
    (lambda c: c.players.times(5, **SWIM, best_only=True, course="SCY"),
     types.SwimTimesPage, "/v1/players/5/times", {**SWIM, "best_only": "true", "course": "SCY"}),
    (lambda c: c.tennis.list_matches(**TENNIS, player_id="11,12", match_type="singles"),
     types.TennisMatchPage, "/v1/tennis/matches", {**TENNIS, "player_id": "11,12", "match_type": "singles"}),
    (lambda c: c.tennis.list_ita_rankings(**TENNIS, type="doubles", season="2026"),
     types.TennisRankingPage, "/v1/rankings/ita", {**TENNIS, "type": "doubles", "season": "2026"}),
    (lambda c: c.movements.changes(since="2026-11-01T00:00:00Z", kind="coach"),
     types.MovementChangePage, "/v1/movements/changes", {"since": "2026-11-01T00:00:00Z", "kind": "coach"}),
    (lambda c: c.reference.regions(sport="soccer", division="NJCAA-D1"),
     types.StringListResponse, "/v1/regions", {"sport": "soccer", "division": "NJCAA-D1"}),
    (lambda c: c.reference.eligibility_rules(), types.EligibilityRulesResponse, "/v1/eligibility/rules", {}),
    (lambda c: c.teams.postseason(3, sport="soccer", gender="women", kind="national_tournament"),
     types.TeamPostseasonResponse, "/v1/teams/3/postseason",
     {"sport": "soccer", "gender": "women", "kind": "national_tournament"}),
    (lambda c: c.teams.rankings(3, sport="volleyball", ranking_system="RPI"),
     types.TeamRankingsResponse, "/v1/teams/3/rankings", {"sport": "volleyball", "ranking_system": "RPI"}),
    # new filters on existing methods
    (lambda c: c.teams.list(sport="soccer", division="NJCAA-D1", region="NJCAA Region IV",
                            roster_changed_since="2026-11-01T00:00:00Z"),
     types.TeamPage, "/v1/teams",
     {"sport": "soccer", "division": "NJCAA-D1", "region": "NJCAA Region IV",
      "roster_changed_since": "2026-11-01T00:00:00Z"}),
    (lambda c: c.teams.roster(3, sport="soccer", division="D1", class_level="FR,SO", class_redshirt=False,
                              seasons_remaining_min=2, eligibility_confidence="high"),
     types.RosterPage, "/v1/teams/3/roster",
     {"sport": "soccer", "division": "D1", "class_level": "FR,SO", "class_redshirt": "false",
      "seasons_remaining_min": "2", "eligibility_confidence": "high"}),
    (lambda c: c.schools.list(state="NY", control="Private nonprofit", religious_affiliation="Roman Catholic",
                              admission_rate_max=0.2, undergrad_enrollment_min=1000),
     types.SchoolPage, "/v1/schools",
     {"state": "NY", "control": "Private nonprofit", "religious_affiliation": "Roman Catholic",
      "admission_rate_max": "0.2", "undergrad_enrollment_min": "1000"}),
    (lambda c: c.games.list(sport="soccer", division="NJCAA-D1", region="NJCAA Region IV"),
     types.GamePage, "/v1/games", {"sport": "soccer", "division": "NJCAA-D1", "region": "NJCAA Region IV"}),
    (lambda c: c.movements.list(region_not="NJCAA Region IV"),
     types.MovementPage, "/v1/movements", {"region_not": "NJCAA Region IV"}),
    (lambda c: c.portal_supply.list(sport="soccer", gender="women", division="D1", lane="GK,none", include_zero=True),
     types.PortalSupplyPage, "/v1/portal/supply",
     {"sport": "soccer", "gender": "women", "division": "D1", "lane": "GK,none", "include_zero": "true"}),
    (lambda c: c.portal_supply.changes(since=dt.datetime(2026, 11, 2, tzinfo=dt.timezone.utc), team_id="3,4"),
     types.PortalSupplyChangePage, "/v1/portal/supply/changes",
     {"since": "2026-11-02T00:00:00+00:00", "team_id": "3,4"}),
]


@pytest.mark.parametrize("call,model,path,query", CASES, ids=[c[2] + "?" + ",".join(c[3]) for c in CASES])
def test_each_method_sends_its_request_and_parses_its_model(call, model, path, query):
    rec = Recorder(minimal(model))
    result = call(sync_client(rec))
    method, sent_path, sent_query = rec.last
    assert (method, sent_path, sent_query) == ("GET", path, query)
    if "data" in model.model_fields and "next_cursor" in model.model_fields:
        assert result.data == [] and result.has_more is False
    else:
        assert isinstance(result, model)


@pytest.mark.parametrize("call,model,path,query", CASES, ids=[c[2] + "?" + ",".join(c[3]) for c in CASES])
def test_the_async_client_sends_the_same_request(call, model, path, query):
    rec = Recorder(minimal(model))

    async def run():
        result = call(async_client(rec))
        return await result

    asyncio.run(run())
    assert rec.last == ("GET", path, query)


def test_a_new_cursor_list_follows_next_cursor():
    pages = [
        {"data": [minimal(types.TennisMatch)], "next_cursor": "Mg==", "has_more": True},
        {"data": [minimal(types.TennisMatch)], "next_cursor": None, "has_more": False},
    ]
    seen = []

    def handler(request):
        seen.append(request.url.params.get("cursor"))
        return httpx.Response(200, json=pages[len(seen) - 1])

    items = list(sync_client(handler).tennis.list_matches(**TENNIS).auto_paging_iter())
    assert len(items) == 2 and seen == [None, "Mg=="]
    assert all(isinstance(m, types.TennisMatch) for m in items)


def test_a_school_carries_its_scorecard_profile():
    school = {
        "id": 524, "name": "Cornell University", "ipeds_unitid": 190415, "control": "Private nonprofit",
        "profile": {
            "admission_rate": 0.0876, "sat_math_25": 770, "sat_math_75": 800,
            "top_majors": [{"field": "Engineering", "share": 0.1476}],
            "data_year": 2024, "source": "college_scorecard",
        },
    }
    rec = Recorder({"data": [school, {"id": 9, "name": "No Profile", "profile": None}],
                    "next_cursor": None, "has_more": False})
    page = sync_client(rec).schools.list(admission_rate_max=0.2)
    cornell, other = page.data
    assert isinstance(cornell, types.SchoolSummary)
    assert cornell.profile.admission_rate == 0.0876
    assert cornell.profile.top_majors[0].field == "Engineering"
    assert cornell.profile.top_majors[0].share == 0.1476
    assert other.profile is None


def test_create_sandbox_event_posts_its_body_and_is_never_retried():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(503, json={"error": {"type": "unavailable", "code": "busy", "message": "busy"}})

    client = sync_client(handler)
    with pytest.raises(APIStatusError):
        client.sandbox.create_event(type="portal_entry", sport="soccer", division="D1", team_id=90001)
    assert len(calls) == 1
    req = calls[0]
    assert (req.method, req.url.path) == ("POST", "/v1/sandbox/events")
    assert json.loads(req.content) == {"type": "portal_entry", "sport": "soccer", "division": "D1", "team_id": 90001}


def test_create_sandbox_event_returns_its_model():
    rec = Recorder(minimal(types.SandboxEventResponse))
    result = sync_client(rec).sandbox.create_event(type="coach_movement", sport="basketball", division="D3")
    assert isinstance(result, types.SandboxEventResponse)
    assert rec.requests[0].method == "POST"
