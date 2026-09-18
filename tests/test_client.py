"""SDK behavior tests against an httpx.MockTransport — no network.

Covers the contract the runtime owes callers: auth headers, error mapping
from the {"error": {...}} envelope, Retry-After-honoring retries, cursor
auto-pagination, and create_and_poll's lifecycle.
"""

from __future__ import annotations

import json

import httpx
import pytest

import magisterial
from magisterial import (
    AuthenticationError,
    BillingError,
    Magisterial,
    NotFoundError,
    QueryPollTimeout,
    RateLimitError,
)

API_KEY = "mag_test_abc123"


def make_client(handler, **kwargs) -> Magisterial:
    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    return Magisterial(api_key=API_KEY, http_client=http_client, **kwargs)


def json_response(status: int, body, headers=None) -> httpx.Response:
    return httpx.Response(status, json=body, headers=headers or {})


# -- construction ------------------------------------------------------------


def test_requires_api_key(monkeypatch):
    monkeypatch.delenv("MAGISTERIAL_API_KEY", raising=False)
    with pytest.raises(magisterial.MagisterialError, match="MAGISTERIAL_API_KEY"):
        Magisterial()


def test_reads_key_and_base_url_from_env(monkeypatch):
    monkeypatch.setenv("MAGISTERIAL_API_KEY", API_KEY)
    monkeypatch.setenv("MAGISTERIAL_BASE_URL", "https://staging.example.com/")
    client = Magisterial()
    assert client._config.api_key == API_KEY
    assert client._config.base_url == "https://staging.example.com"


# -- headers -----------------------------------------------------------------


def test_sends_bearer_and_user_agent():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers["Authorization"]
        seen["ua"] = request.headers["User-Agent"]
        return json_response(200, {"data": []})

    client = make_client(handler)
    client.reference.divisions()
    assert seen["auth"] == f"Bearer {API_KEY}"
    assert seen["ua"] == f"magisterial-python/{magisterial.__version__}"


# -- error mapping -----------------------------------------------------------


def _error_body(type_, code, message):
    return {"error": {"type": type_, "code": code, "message": message}}


def test_401_maps_to_authentication_error():
    client = make_client(
        lambda req: json_response(
            401, _error_body("unauthorized", "invalid_api_key", "Invalid or revoked API key.")
        )
    )
    with pytest.raises(AuthenticationError) as exc_info:
        client.reference.sports()
    assert exc_info.value.error_code == "invalid_api_key"
    assert "revoked" in str(exc_info.value)


def test_402_maps_to_billing_error():
    client = make_client(
        lambda req: json_response(
            402, _error_body("billing", "budget_exceeded", "Monthly budget exhausted.")
        )
    )
    with pytest.raises(BillingError):
        client.portal.list(sport="soccer", division="D1")


def test_404_maps_to_not_found():
    client = make_client(
        lambda req: json_response(
            404, _error_body("not_found", "player_not_found", "No player with that id in scope.")
        )
    )
    with pytest.raises(NotFoundError):
        client.players.get(999, sport="soccer", division="D1")


# -- retries -----------------------------------------------------------------


def test_retries_429_honoring_retry_after(monkeypatch):
    sleeps = []
    monkeypatch.setattr("time.sleep", lambda s: sleeps.append(s))
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return json_response(
                429,
                _error_body("rate_limited", "rate_limit_exceeded", "Slow down."),
                headers={"Retry-After": "3"},
            )
        return json_response(200, {"data": ["D1"]})

    client = make_client(handler)
    result = client.reference.divisions()
    assert result.data == ["D1"]
    assert calls["n"] == 2
    assert sleeps == [3.0]


def test_non_retryable_post_fails_immediately():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return json_response(
            429, _error_body("rate_limited", "rate_limit_exceeded", "Slow down.")
        )

    client = make_client(handler)
    with pytest.raises(RateLimitError) as exc_info:
        client.query.create(prompt="who leads in goals?", sport="soccer")
    assert calls["n"] == 1  # billable create: no auto-retry
    assert exc_info.value.status_code == 429


def test_retries_exhaust_then_raise(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return json_response(500, {"error": {"type": "internal", "code": "boom", "message": "x"}})

    client = make_client(handler, max_retries=2)
    with pytest.raises(magisterial.InternalServerError):
        client.reference.sports()
    assert calls["n"] == 3  # initial + 2 retries


# -- pagination ----------------------------------------------------------------


def _player(i):
    return {"id": i, "name": f"Player {i}", "stats": {}}


def test_search_auto_pagination_follows_cursor():
    bodies = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        bodies.append(body)
        if body.get("cursor") is None:
            return json_response(
                200,
                {"data": [_player(1), _player(2)], "next_cursor": "c2", "has_more": True},
            )
        assert body["cursor"] == "c2"
        return json_response(
            200, {"data": [_player(3)], "next_cursor": None, "has_more": False}
        )

    client = make_client(handler)
    mixed_scope = "D1,NAIA,NJCAA-D1"
    page = client.players.search(sport="soccer", division=mixed_scope, limit=2)
    names = [p.name for p in page.auto_paging_iter()]
    assert names == ["Player 1", "Player 2", "Player 3"]
    # Original filters survive into the cursor-following request.
    assert bodies[1]["sport"] == "soccer" and bodies[1]["limit"] == 2
    assert bodies[1]["division"] == mixed_scope


def test_page_iteration_without_following():
    client = make_client(
        lambda req: json_response(
            200, {"data": [_player(1)], "next_cursor": "c2", "has_more": True}
        )
    )
    page = client.teams.list(sport="soccer", division="D1")
    assert len(page) == 1
    assert page.has_more and page.next_cursor == "c2"


def test_team_roster_season_survives_pagination():
    queries = []

    def handler(request: httpx.Request) -> httpx.Response:
        query = dict(request.url.params)
        queries.append(query)
        assert request.url.path == "/v1/teams/1873/roster"
        if query.get("cursor") is None:
            return json_response(
                200,
                {
                    "season": "2026",
                    "data": [{"id": 1, "name": "Player 1"}],
                    "next_cursor": "c2",
                    "has_more": True,
                },
            )
        return json_response(
            200,
            {
                "season": "2026",
                "data": [{"id": 2, "name": "Player 2"}],
                "next_cursor": None,
                "has_more": False,
            },
        )

    client = make_client(handler)
    page = client.teams.roster(
        1873,
        sport="soccer",
        division="D3",
        season="2026",
        limit=1,
    )
    assert page.season == "2026"

    next_page = page.next_page()
    assert next_page is not None
    assert next_page.season == "2026"
    assert [entry.name for entry in next_page.data] == ["Player 2"]
    assert queries == [
        {"sport": "soccer", "division": "D3", "season": "2026", "limit": "1"},
        {
            "sport": "soccer",
            "division": "D3",
            "season": "2026",
            "limit": "1",
            "cursor": "c2",
        },
    ]


# -- 0.2.0 endpoints -----------------------------------------------------------


def test_games_list_paginates():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["sport"] == "soccer"
        return json_response(
            200,
            {
                "data": [{"id": 9001, "home_team_name": "Amherst", "away_team_name": "Tufts", "status": "final"}],
                "next_cursor": None,
                "has_more": False,
            },
        )

    client = make_client(handler)
    page = client.games.list(sport="soccer", division="D3", status="final")
    assert page.data[0].home_team_name == "Amherst"


def test_movements_list_paginates():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/movements"
        assert request.url.params["kind"] == "coach"
        assert request.url.params["sport_path"] == "womens-soccer"
        return json_response(
            200,
            {
                "data": [{
                    "id": 59, "kind": "coach", "event_type": "title_changed",
                    "sport_path": "womens-soccer", "season": "2027",
                    "school_name": "Macalester College",
                    "subject": {"name": "Marissa Olson-Guillou",
                                "to_title": "Head Coach", "is_head": True},
                    "resolution_kind": "head_coach_change_confirmed",
                }],
                "next_cursor": None,
                "has_more": False,
            },
        )

    client = make_client(handler)
    page = client.movements.list(kind="coach", sport_path="womens-soccer")
    entry = page.data[0]
    assert entry.subject.name == "Marissa Olson-Guillou"
    assert entry.resolution_kind == "head_coach_change_confirmed"
    assert not page.has_more


def test_team_coaches():
    client = make_client(
        lambda req: json_response(
            200, {"season": "2025-26", "data": [{"name": "Sam Blake", "role": "Head Coach"}]}
        )
    )
    staff = client.teams.coaches(1873, sport="soccer", division="D3")
    assert staff.season == "2025-26"
    assert staff.data[0].name == "Sam Blake"


def test_export_create_and_poll(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    statuses = iter(["queued", "running", "succeeded"])

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return json_response(202, {"export_id": "e1", "status": "queued"})
        return json_response(
            200,
            {
                "export_id": "e1",
                "status": next(statuses),
                "dataset": "players",
                "format": "csv",
                "download_url": "https://example.com/f.csv.gz",
            },
        )

    client = make_client(handler)
    job = client.exports.create_and_poll(dataset="players", sport="soccer", division="D3")
    assert job.status == "succeeded"
    assert job.download_url is not None


def test_export_create_not_retried():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return json_response(429, _error_body("rate_limited", "rate_limit_exceeded", "Slow down."))

    client = make_client(handler)
    with pytest.raises(RateLimitError):
        client.exports.create(dataset="players", sport="soccer", division="D3")
    assert calls["n"] == 1  # billable create: no auto-retry


# -- query polling -------------------------------------------------------------


def test_create_and_poll_reaches_done(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    statuses = iter(["queued", "running", "done"])

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return json_response(202, {"run_id": "r1", "status": "queued"})
        return json_response(
            200, {"run_id": "r1", "status": next(statuses), "answer": "42"}
        )

    client = make_client(handler)
    run = client.query.create_and_poll(prompt="answer?", sport="soccer")
    assert run.status == "done"
    assert run.answer == "42"


def test_create_and_poll_timeout(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    clock = {"t": 0.0}

    def fake_monotonic():
        clock["t"] += 100.0
        return clock["t"]

    monkeypatch.setattr("time.monotonic", fake_monotonic)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return json_response(202, {"run_id": "r1", "status": "queued"})
        return json_response(200, {"run_id": "r1", "status": "running"})

    client = make_client(handler)
    with pytest.raises(QueryPollTimeout) as exc_info:
        client.query.create_and_poll(prompt="slow", sport="soccer", timeout=150.0)
    assert exc_info.value.run_id == "r1"


# -- 0.5.0 endpoints -----------------------------------------------------------


def test_teams_list_ipeds_unitid_filter():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["ipeds_unitid"] == "166027"
        return json_response(
            200,
            {
                "data": [{
                    "id": 1873, "name": "Amherst", "sport_path": "mens-soccer",
                    "school": {"id": 42, "name": "Amherst College", "ipeds_unitid": 166027},
                }],
                "next_cursor": None,
                "has_more": False,
            },
        )

    client = make_client(handler)
    page = client.teams.list(sport="soccer", division="D3", ipeds_unitid=166027)
    assert page.data[0].school.ipeds_unitid == 166027


def test_teams_coaches_on_behalf_of():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["on_behalf_of"] == "184223"
        return json_response(
            200,
            {
                "season": "2025-26",
                "data": [{"name": "Sam Blake", "role": "Head Coach", "email": "sam@example.edu"}],
                "contacts_included": True,
            },
        )

    client = make_client(handler)
    staff = client.teams.coaches(
        1873, sport="soccer", division="D3", on_behalf_of=184223
    )
    assert staff.contacts_included is True
    assert staff.data[0].email == "sam@example.edu"


def test_movements_list_status_param():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["status"] == "resolved"
        return json_response(
            200,
            {
                "data": [{
                    "id": 60, "kind": "player", "event_type": "player_added",
                    "sport_path": "mens-soccer", "status": "resolved",
                    "resolution_status": "linked_transfer",
                    "subject": {"name": "Alex Kim"},
                }],
                "next_cursor": None,
                "has_more": False,
            },
        )

    client = make_client(handler)
    page = client.movements.list(status="resolved")
    assert page.data[0].resolution_status == "linked_transfer"


def test_schools_list_paginates():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/schools"
        assert request.url.params["state"] == "MA"
        return json_response(
            200,
            {
                "data": [{"id": 42, "name": "Amherst College", "ipeds_unitid": 166027, "state": "MA"}],
                "next_cursor": None,
                "has_more": False,
            },
        )

    client = make_client(handler)
    page = client.schools.list(state="MA")
    assert page.data[0].name == "Amherst College"
    assert page.data[0].ipeds_unitid == 166027


def test_schools_get():
    client = make_client(
        lambda req: json_response(
            200,
            {
                "id": 42,
                "name": "Amherst College",
                "ipeds_unitid": 166027,
                "teams": [{"id": 1873, "name": "Amherst", "sport_path": "mens-soccer"}],
            },
        )
    )
    school = client.schools.get(42)
    assert school.name == "Amherst College"
    assert school.teams[0].id == 1873


def test_athletes_create_not_retried():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return json_response(
            429, _error_body("rate_limited", "rate_limit_exceeded", "Slow down.")
        )

    client = make_client(handler)
    with pytest.raises(RateLimitError):
        client.athletes.create(13232, sport_path="mens-soccer")
    assert calls["n"] == 1  # write: no auto-retry


def test_athletes_create_body_and_response():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = json.loads(request.content)
        return json_response(
            201,
            {
                "id": "grant_1",
                "status": "invited",
                "player_id": 13232,
                "sport_path": "mens-soccer",
                "organization_name": "Northstar Recruiting",
            },
        )

    client = make_client(handler)
    entry = client.athletes.create(
        13232, sport_path="mens-soccer", organization_name="Northstar Recruiting"
    )
    assert seen["body"] == {
        "player_id": 13232,
        "sport_path": "mens-soccer",
        "organization_name": "Northstar Recruiting",
    }
    assert entry.id == "grant_1"
    assert entry.status == "invited"


def test_athletes_list_status_filter():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/athletes"
        assert request.url.params["status"] == "active"
        return json_response(
            200,
            {
                "data": [{"id": "grant_1", "status": "active", "player_id": 13232}],
                "next_cursor": None,
                "has_more": False,
            },
        )

    client = make_client(handler)
    page = client.athletes.list(status="active")
    assert page.data[0].id == "grant_1"


def test_athletes_get():
    client = make_client(
        lambda req: json_response(
            200, {"id": "grant_1", "status": "invited", "player_id": 13232}
        )
    )
    entry = client.athletes.get("grant_1")
    assert entry.status == "invited"


def test_athletes_resend_invite_not_retried():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return json_response(
            429, _error_body("rate_limited", "rate_limit_exceeded", "Slow down.")
        )

    client = make_client(handler)
    with pytest.raises(RateLimitError):
        client.athletes.resend_invite("grant_1")
    assert calls["n"] == 1  # write: no auto-retry


def test_athletes_resend_invite():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/v1/athletes/grant_1/resend"
        return json_response(200, {"id": "grant_1", "status": "invited"})

    client = make_client(handler)
    entry = client.athletes.resend_invite("grant_1")
    assert entry.status == "invited"


def test_athletes_revoke():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "DELETE"
        assert request.url.path == "/v1/athletes/grant_1"
        return json_response(200, {"id": "grant_1", "status": "revoked"})

    client = make_client(handler)
    result = client.athletes.revoke("grant_1")
    assert result.status == "revoked"


def test_athletes_list_access_paginates():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/athletes/grant_1/access"
        return json_response(
            200,
            {
                "data": [{
                    "id": 1, "grant_id": "grant_1", "capability": "outreach.coach.read",
                    "row_count": 3,
                }],
                "next_cursor": None,
                "has_more": False,
            },
        )

    client = make_client(handler)
    page = client.athletes.list_access("grant_1")
    assert page.data[0].capability == "outreach.coach.read"


# -- async parity ----------------------------------------------------------------


@pytest.mark.anyio
async def test_async_client_basic_flow():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == f"Bearer {API_KEY}"
        return json_response(
            200, {"data": [_player(1)], "next_cursor": None, "has_more": False}
        )

    transport = httpx.MockTransport(handler)
    client = magisterial.AsyncMagisterial(
        api_key=API_KEY, http_client=httpx.AsyncClient(transport=transport)
    )
    page = await client.players.search(sport="soccer", division="D1")
    items = [p async for p in page.auto_paging_iter()]
    assert [p.name for p in items] == ["Player 1"]
    await client.close()


@pytest.mark.anyio
async def test_async_team_roster_exposes_season():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/teams/1873/roster"
        assert request.url.params["season"] == "2026"
        return json_response(
            200,
            {
                "season": "2026",
                "data": [{"id": 1, "name": "Player 1"}],
                "next_cursor": None,
                "has_more": False,
            },
        )

    transport = httpx.MockTransport(handler)
    client = magisterial.AsyncMagisterial(
        api_key=API_KEY, http_client=httpx.AsyncClient(transport=transport)
    )
    page = await client.teams.roster(
        1873,
        sport="soccer",
        division="D3",
        season="2026",
    )
    assert page.season == "2026"
    await client.close()


@pytest.mark.anyio
async def test_async_schools_and_athletes():
    def schools_handler(request: httpx.Request) -> httpx.Response:
        return json_response(
            200, {"data": [{"id": 42, "name": "Amherst College"}], "next_cursor": None, "has_more": False}
        )

    transport = httpx.MockTransport(schools_handler)
    client = magisterial.AsyncMagisterial(
        api_key=API_KEY, http_client=httpx.AsyncClient(transport=transport)
    )
    page = await client.schools.list()
    assert page.data[0].name == "Amherst College"
    await client.close()

    def athletes_handler(request: httpx.Request) -> httpx.Response:
        return json_response(201, {"id": "grant_1", "status": "invited", "player_id": 13232})

    transport2 = httpx.MockTransport(athletes_handler)
    client2 = magisterial.AsyncMagisterial(
        api_key=API_KEY, http_client=httpx.AsyncClient(transport=transport2)
    )
    entry = await client2.athletes.create(13232)
    assert entry.status == "invited"
    await client2.close()


@pytest.fixture
def anyio_backend():
    return "asyncio"
