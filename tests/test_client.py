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
    page = client.players.search(sport="soccer", division="D1", limit=2)
    names = [p.name for p in page.auto_paging_iter()]
    assert names == ["Player 1", "Player 2", "Player 3"]
    # Original filters survive into the cursor-following request.
    assert bodies[1]["sport"] == "soccer" and bodies[1]["limit"] == 2


def test_page_iteration_without_following():
    client = make_client(
        lambda req: json_response(
            200, {"data": [_player(1)], "next_cursor": "c2", "has_more": True}
        )
    )
    page = client.teams.list(sport="soccer", division="D1")
    assert len(page) == 1
    assert page.has_more and page.next_cursor == "c2"


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


@pytest.fixture
def anyio_backend():
    return "asyncio"
