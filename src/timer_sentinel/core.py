import time
from collections.abc import Callable
from functools import wraps
from logging import WARNING, Logger, getLogger
from typing import Any, Self
from uuid import uuid4

default_logger = getLogger("TimerSentinel")


class TimerSentinel:
    """Monitor execution time and log when threshold is exceeded.

    Can be used as a context manager, decorator, or called manually.

    Examples:
        # As context manager
        with TimerSentinel(threshold=1.0, name="task"):
            do_work()

        # As decorator
        @TimerSentinel(threshold=1.0, name="task")
        def do_work():
            pass

        # Manual usage
        timer = TimerSentinel(threshold=1.0, name="task")
        timer.start()
        do_work()
        timer.end()
        timer.report()
    """

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
        name: str = "",
        logger: Logger | None = None,
        on_exceed_keyword: str = "OVERTIME",
        on_exceed_level: int = WARNING,
        on_exceed_callback: Callable[[], None] | None = None,
        callback_args: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the timer sentinel.

        Args:
            threshold: Maximum allowed execution time in seconds.
            name: Name identifier for the timer. Empty string by default.
                If empty or used as decorator, will use "TimerSentinel"
                or the function name respectively.
            logger: Logger instance to use. If None, uses default
                TimerSentinel logger.
            on_exceed_keyword: Keyword to include in log message when
                threshold exceeded. Default is "OVERTIME".
            on_exceed_level: Logging level (integer) to use when threshold
                exceeded. Default is WARNING (30).
            on_exceed_callback: Optional callback function to execute when
                threshold exceeded. Must be callable without arguments.
            callback_args: Optional keyword arguments to pass to the
                callback function when invoked.
        """
        self.threshold = threshold
        self.name = name if name else "TimerSentinel"
        self._logger = logger or default_logger
        self._on_exceed_keyword = on_exceed_keyword
        self._on_exceed_level = on_exceed_level
        self._on_exceed_callback = on_exceed_callback
        self._callback_args = callback_args or {}
        self._execution_id = uuid4().hex[:8]
        self._timer = None
        self._total_time = None

    def __call__(self, func: Callable) -> Callable:
        """Enable TimerSentinel to be used as a decorator.

        Args:
            func: The function to wrap and time.

        Returns:
            Wrapped function that automatically times execution.

        Example:
            @TimerSentinel(threshold=1.0)
            def my_function():
                pass
        """

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
        """Enter the context manager and start timing.

        Returns:
            Self instance for use in with statement.
        """
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager, stop timing and report.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_val: Exception value if an exception occurred.
            exc_tb: Exception traceback if an exception occurred.

        Note:
            Exceptions are propagated (not suppressed).
        """
        self.end()
        self.report()

    def start(self) -> None:
        """Start the timer.

        Records the current time using perf_counter for high precision.
        """
        self._timer = time.perf_counter()

    def end(self) -> None:
        """Stop the timer and calculate total execution time.

        Raises:
            RuntimeError: If start() was not called before end().
        """
        if self._timer is None:
            raise RuntimeError("Timer not started. Call start() first.")
        self._total_time = time.perf_counter() - self._timer

    def report(self) -> None:
        """Log a message and execute callback if threshold was exceeded.

        Logs a message with execution time details if the threshold was
        exceeded. Executes the configured callback function if provided.

        Raises:
            RuntimeError: If end() was not called before report().
        """
        if self._total_time is None:
            raise RuntimeError("Timer not ended. Call end() first.")

        if self._total_time > self.threshold:
            msg = (
                f"{self._on_exceed_keyword} | {self.name}.{self._execution_id}"
                f" | {self._total_time:.4f}s > {self.threshold:.4f}s"
            )
            self._logger.log(self._on_exceed_level, msg)

            if self._on_exceed_callback:
                self._on_exceed_callback(**self._callback_args)
