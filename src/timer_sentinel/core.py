import time
from collections.abc import Callable
from functools import wraps
from logging import WARNING, Logger, getLogger
from typing import Any, Self
from uuid import uuid4

default_logger = getLogger("TimerSentinel")


class TimerSentinel:
    def __init__(
        self,
        threshold: float,
        name: str | None = None,
        logger_class: Logger | None = None,
        on_exceed_logging_keyword: str = "OVERTIME",
        on_exceed_log_level: int = WARNING,
        on_exceed_callback: Callable[[], None] | None = None,
        on_exceed_callback_arguments: dict[str, Any] | None = None,
    ) -> None:
        # Input params
        self.threshold = threshold
        self.name = name
        self.logger_class = logger_class if logger_class is not None else default_logger
        self.on_exceed_logging_keyword = on_exceed_logging_keyword
        self.on_exceed_log_level = on_exceed_log_level
        self.on_exceed_callback = on_exceed_callback
        self.on_exceed_callback_arguments = (
            on_exceed_callback_arguments
            if on_exceed_callback_arguments is not None
            else {}
        )

        # Internal params
        self._execution_id: str = uuid4().hex[:8]

        # Defaults
        self._timer: float | None = None
        self._total_time: float | None = None

    def __call__(self, func: Callable) -> Callable:
        """Enable TimerSentinel to be used as a decorator."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.name is None:
                self.name = func.__name__

            self.start()
            try:
                result = func(*args, **kwargs)
                return result
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
            raise Exception("TimerSentinel was not started using self.start() method")
        self._total_time = time.perf_counter() - self._timer

    def report(self) -> None:
        if self._total_time is None:
            raise Exception("TimerSentinel was not ended using self.end() method")
        msg = f"{self.on_exceed_logging_keyword} | Timer {self.name}.{self._execution_id} | Execution time exceeded {self._total_time}s"
        if self._total_time > self.threshold:
            self.logger_class.log(level=self.on_exceed_log_level, msg=msg)
            if self.on_exceed_callback is not None:
                self.on_exceed_callback(**self.on_exceed_callback_arguments)
