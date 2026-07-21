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
    sport="soccer", division="D1", gender="women",
    position="Forward", sort_by="goals",
)
for player in page.auto_paging_iter():
    print(player.name, player.team, player.stats.get("goals"))

# One player's full profile
player = client.players.get(184223, sport="soccer", division="D3")

# Live transfer portal (usage-billed; use `since` for incremental polling)
portal = client.portal.list(sport="basketball", division="D1", status="INC")

# Natural-language query (usage-billed): submit and wait for the answer
run = client.query.create_and_poll(
    prompt="Who led the NESCAC in assists this season?",
    sport="soccer", division="D3", gender="men",
)
print(run.answer)
```

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

## Types

All request/response models live in `magisterial.types` and are generated from
the published OpenAPI spec (`scripts/sync-types.sh`), so they cannot drift
from the live API contract.

## License

MIT
