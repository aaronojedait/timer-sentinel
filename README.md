# Timer Sentinel

[![PyPI version](https://img.shields.io/pypi/v/timer-sentinel.svg?color=blue)](https://pypi.org/project/timer-sentinel/)
[![Python Support](https://img.shields.io/pypi/pyversions/timer-sentinel.svg)](https://pypi.org/project/timer-sentinel/)
[![CI Status](https://img.shields.io/github/actions/workflow/status/aaronojedait/timer-sentinel/ci.yml?branch=main&label=tests)](https://github.com/aaronojedait/timer-sentinel/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](#)
[![MyPy Checked](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy.readthedocs.io/)
[![Linting: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A dead-simple, **fast**, and **lightweight** Python timer for catching slow code. Zero dependencies, optimized performance, just pure Python doing one thing well.

### Branch Status
- **Main (Stable):** ![Main](https://img.shields.io/github/actions/workflow/status/aaronojedait/timer-sentinel/ci.yml?branch=main)
- **Develop (Dev):** ![Develop](https://img.shields.io/github/actions/workflow/status/aaronojedait/timer-sentinel/ci.yml?branch=develop)

---

## Why?

I built this after spending too much time debugging inconsistent latency in complex systems. Sometimes a function that should take 100ms randomly takes 5 seconds, and you need to know **when** and **where**.

This timer helped me catch those issues. Works great with **Grafana + Loki** for analyzing logs and creating alerts, or use the callback for whatever custom logic you need.

## What it does

- ⏱️ Times your code with high precision
- 📊 Logs when it's too slow
- 🔔 Runs callbacks when thresholds are exceeded
- 🎯 Works as decorator, context manager, or manual timer
- 🔀 Supports async functions
- 🚀 **Fast** - optimized with `__slots__`, minimal overhead
- 🪶 **Lightweight** - zero dependencies, tiny footprint
- ⚡ **Efficient** - uses `time.perf_counter()` for microsecond precision

## Install

```bash
pip install timer-sentinel
```

## Usage

```python
from timer_sentinel import TimerSentinel

# Context manager
with TimerSentinel(threshold=1.0, name="db_query"):
    slow_database_call()

# Decorator
@TimerSentinel(threshold=0.5)
def api_call():
    return requests.get(url)

# Async
@TimerSentinel(threshold=0.5)
async def async_operation():
    await some_io()
```

## Real-world Examples

### Catch slow database queries

```python
@TimerSentinel(threshold=0.1, name="db_query")
def get_user(user_id):
    return db.query(f"SELECT * FROM users WHERE id={user_id}")
```

### Integration with Grafana + Loki

Just log to your standard logger and ship logs to Loki:

```python
import logging

logger = logging.getLogger("production")

with TimerSentinel(threshold=1.0, logger=logger, name="api_call"):
    call_external_api()
```

Create alerts in Grafana based on the "OVERTIME" keyword or parse execution times. Good for catching performance regressions in production.

## API

```python
TimerSentinel(
    threshold: float,              # Max time in seconds
    name: str = "",                # Timer name (uses function name if decorator)
    logger: Logger | None = None,  # Custom logger
    on_exceed_keyword: str = "OVERTIME",     # Log keyword
    on_exceed_level: int = WARNING,          # Log level
    on_exceed_callback: Callable = None,     # Callback function (sync or async)
    callback_args: dict = None,              # Args for callback
)
```

**Callback:**

- The `on_exceed_callback` can be a synchronous or asynchronous function. If you provide an async function, it will be awaited automatically.

**Methods:**
- `start()` - Start timing
- `end()` - Stop timing
- `report()` - Log if threshold exceeded

**Use as:**
- Decorator: `@TimerSentinel(...)`
- Context manager: `with TimerSentinel(...)`
- Manual: `timer.start()` → `timer.end()` → `timer.report()`

## Requirements

- Python 3.10+
- No external dependencies

## Contributing

Found a bug? Want a feature? Open an issue or PR on [GitHub](https://github.com/aaronojedait/timer-sentinel).

## License

MIT License - do whatever you want with it.

## Author

**Aaron Ojeda** · [GitHub](https://github.com/aaronojedait)
