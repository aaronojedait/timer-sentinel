import time
from collections.abc import Callable
from functools import wraps
from logging import WARNING, Logger, getLogger
from typing import Any, Self
from uuid import uuid4

default_logger = getLogger("TimerSentinel")


class TimerSentinel:
    __slots__ = (
        "threshold",
        "name",
        "_logger",
        "_on_exceed_keyword",
        "_on_exceed_level",
        "_on_exceed_callback",
        "_callback_args",
        "_execution_id",
        "_timer",
        "_total_time",
    )

    def __init__(
        self,
        threshold: float,
        name: str | None = None,
        logger: Logger | None = None,
        on_exceed_keyword: str = "OVERTIME",
        on_exceed_level: int = WARNING,
        on_exceed_callback: Callable[[], None] | None = None,
        callback_args: dict[str, Any] | None = None,
    ) -> None:
        self.threshold = threshold
        self.name = name
        self._logger = logger or default_logger
        self._on_exceed_keyword = on_exceed_keyword
        self._on_exceed_level = on_exceed_level
        self._on_exceed_callback = on_exceed_callback
        self._callback_args = callback_args or {}
        self._execution_id = uuid4().hex[:8]
        self._timer = None
        self._total_time = None

    def __call__(self, func: Callable) -> Callable:
        """Enable TimerSentinel to be used as a decorator."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set name once if not provided
            if self.name is None:
                self.name = func.__name__

            self.start()
            try:
                return func(*args, **kwargs)
            finally:
                self.end()
                self.report()

        return wrapper

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.end()
        self.report()

    def start(self) -> None:
        self._timer = time.perf_counter()

    def end(self) -> None:
        if self._timer is None:
            raise RuntimeError("Timer not started. Call start() first.")
        self._total_time = time.perf_counter() - self._timer

    def report(self) -> None:
        if self._total_time is None:
            raise RuntimeError("Timer not ended. Call end() first.")

        if self._total_time > self.threshold:
            msg = f"{self._on_exceed_keyword} | Timer {self.name}.{self._execution_id} | {self._total_time:.4f}s (threshold: {self.threshold:.4f}s)"
            self._logger.log(self._on_exceed_level, msg)

            if self._on_exceed_callback:
                self._on_exceed_callback(**self._callback_args)
