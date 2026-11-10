# Magisterial Python SDK

The official Python library for the [Magisterial](https://magisterial.ai) developer API —
college sports data across NCAA D1/D2/D3, NAIA, and NJCAA: players, teams, rosters,
cross-program careers, games, the live transfer portal, and an agent-backed
natural-language query endpoint.

- Interactive API reference: https://api.magisterial.ai/v1/docs
- OpenAPI spec: https://api.magisterial.ai/v1/openapi.json
- Agent-ready one-file reference: https://api.magisterial.ai/v1/llms.txt

## Installation

```bash
pip install magisterial
```

Requires Python 3.10+.

## Usage

Create an API key at [magisterial.ai/console/api-keys](https://magisterial.ai/console/api-keys)
and set `MAGISTERIAL_API_KEY` (or pass `api_key=` to the client).

```python
from magisterial import Magisterial

client = Magisterial()

# Search players (auto-pagination follows the cursor for you)
page = client.players.search(
    sport="soccer", division="D1,NAIA,NJCAA-D1", gender="women",
    position="Forward", sort_by="g",
)
for player in page.auto_paging_iter():
    print(player.name, player.team, player.stats["g"])

# One player's full profile
player = client.players.get(184223, sport="soccer", division="D3")

# Live transfer portal (usage-billed; use `since` for incremental polling)
portal = client.portal.list(sport="basketball", division="D1", status="INC")

# Schools (cross-sport, cross-division institution identity), each with its
# College Scorecard profile: admissions, SAT/ACT ranges, enrollment, cost
schools = client.schools.list(state="MA", admission_rate_max=0.3)
school = client.schools.get(schools.data[0].id)
print(school.profile.admission_rate if school.profile else "no federal profile")

# College commitments and their change log (Developer Pro and up)
commits = client.commitments.list(sport="volleyball", gender="women", grad_year="2027")
changes = client.commitments.changes(since="2026-11-01T00:00:00Z")

# Portal supply: counts per program and position group, no one named
# (Developer Ultra and up); keep a copy current with the change log
supply = client.portal_supply.list(sport="soccer", gender="women", division="D1")
supply_changes = client.portal_supply.changes(since="2026-11-01T00:00:00Z")

# Natural-language query (usage-billed): submit and wait for the answer
run = client.query.create_and_poll(
    prompt="Who led the NESCAC in assists this season?",
    sport="soccer", division="D3", gender="men",
)
print(run.answer)
```

### Sport-specific events

Golf, swimming & diving and tennis have their own event shapes:
`client.golf.list_tournaments()` / `.get_tournament()` / `.list_ratings()`,
`client.swim.list_meets()` / `.get_meet()` / `.list_meet_results()` and
`client.players.times()`, and `client.tennis.list_matches()` /
`.list_ita_rankings()`. A team's postseason history and national rankings are
`client.teams.postseason()` and `client.teams.rankings()`;
`client.reference.regions()` lists the values `region` filters take, and
`client.reference.eligibility_rules()` the rules behind every `eligibility`
reading. `client.movements.changes()` is the movement feed's change log, and
with a test key `client.sandbox.create_event()` makes a sandbox event happen.

### Stats

A stat has one name everywhere: the field names `client.reference.filter_catalog()`
lists for a sport (`stats_by_sport`) are what you sort by and what every
`stats` object holds. Every stat field of the sport is present on every row;
`None` means the source did not publish it.

```python
from magisterial.types import SoccerStats

player = page.data[0]
player.stats["g"], player.stats["sh_pct"], player.stats["yc"]   # plain dict
SoccerStats.model_validate(player.stats).pk_made                # or typed

detail = client.players.get(player.id, sport="soccer", division="D1", gender="women")
for season in detail.stats_by_season:        # newest first
    print(season.season, season.team_id, season.stats["g"])
print(detail.stats_totals["g"])
```

There is one stat model per sport: `SoccerStats`, `BasketballStats`,
`BaseballSoftballStats`, `VolleyballStats`, `FootballStats`, `LacrosseStats`.
Track and field has no season stats: a search row reports the athlete's best
mark in `player.track`, and `detail.track_bests` lists the best per event.

A player row carries its profile at the top level (`team_id`, `person_id`,
`sport`, `gender`, `jersey_number`, `home_state`, `height_inches`, ...).
Until 2027-01-12 the API also returns the keys it returned before 2026-10-09
(copies of those fields and the soccer keys `sh%`, `sog%`, `sv%`, `yc-rc`,
`pg-pa` inside `stats`, and `season_stats` on a player); read the fields
above instead.

### Async

Every method is mirrored on `AsyncMagisterial`:

```python
import asyncio
from magisterial import AsyncMagisterial

async def main():
    async with AsyncMagisterial() as client:
        page = await client.players.search(sport="soccer", division="D1")
        async for player in page.auto_paging_iter():
            print(player.name)

asyncio.run(main())
```

### Errors

Non-2xx responses raise typed exceptions carrying the API's error envelope:

```python
from magisterial import Magisterial, NotFoundError, RateLimitError

client = Magisterial()
try:
    client.players.get(1, sport="soccer", division="D1")
except NotFoundError as e:
    print(e.error_code)   # "player_not_found"
except RateLimitError as e:
    print(e.retry_after)  # seconds, from the Retry-After header
```

`BillingError` (402) means API billing is not enabled or the monthly budget is
exhausted — manage both in the [developer console](https://magisterial.ai/console).

### Retries

Idempotent requests (and `players.search`) are retried automatically on 429s,
5xx and connection failures — up to `max_retries` (default 2), honoring the
server's `Retry-After`. Billable creates (`query.create`, `alerts.create`)
are never retried automatically.

### Managed athletes (Enterprise)

Invite an athlete to authorize your platform, then pass their player id as
`on_behalf_of` to `teams.coaches` for delegated coach-contact reads:

```python
grant = client.athletes.create(184223, sport_path="mens-soccer")
# ... athlete accepts the invitation ...
staff = client.teams.coaches(
    1873, sport="soccer", division="D3", on_behalf_of=184223,
)
```

`client.athletes.list()`, `.get()`, `.resend_invite()`, `.revoke()`, and
`.list_access()` manage the grant lifecycle and its audit log.

## School discovery

```python
scope = dict(sport="soccer", gender="women", division="D2")
found = client.schools.resolve(query="Lock Haven University", **scope)
if found.selected and found.selected.in_scope_team_ids:
    players = client.players.search(team_id=found.selected.in_scope_team_ids, **scope)
else:
    print(found.candidates)
```

Use candidate location and program details to choose an identity. For secondary
schools, use `kind="high_school"` and an optional state or city, then pass the
returned `high_school_id` or NCES ID to player search. Name-based player and team
searches return evidence on `page.school_resolutions`.

## Types

All request/response models live in `magisterial.types` and are generated from
the published OpenAPI spec (`scripts/sync-types.sh`), so they cannot drift
from the live API contract.

## License

MIT
