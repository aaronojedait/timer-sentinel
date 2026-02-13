import logging
import time

import pytest

from timer_sentinel.core import TimerSentinel


class TestTimerSentinelBasics:
    """Test basic functionality"""

    def test_initialization_defaults(self) -> None:
        """Test TimerSentinel initializes with correct defaults"""
        timer = TimerSentinel(threshold=1.0)

        assert timer.threshold == 1.0
        assert timer.name == "TimerSentinel"
        assert timer._timer is None
        assert timer._total_time is None

    def test_initialization_custom_name(self) -> None:
        """Test TimerSentinel accepts custom name."""
        timer = TimerSentinel(threshold=1.0, name="custom_timer")

        assert timer.name == "custom_timer"

    def test_initialization_empty_name_uses_default(self) -> None:
        """Test empty name falls back to default."""
        timer = TimerSentinel(threshold=1.0, name="")

        assert timer.name == "TimerSentinel"


class TestTimerSentinelManualUsage:
    """Test manual start/end/report usage."""

    def test_start_sets_timer(self):
        """Test start() sets the internal timer."""
        timer = TimerSentinel(threshold=1.0)
        timer.start()

        assert timer._timer is not None
        assert isinstance(timer._timer, float)

    def test_end_calculates_time(self):
        """Test end() calculates total time correctly."""
        timer = TimerSentinel(threshold=1.0)
        timer.start()
        time.sleep(0.1)
        timer.end()

        assert timer._total_time is not None
        assert timer._total_time >= 0.1
        assert timer._total_time < 0.5  # Allow some margin

    def test_end_without_start_raises_error(self):
        """Test end() raises RuntimeError if start() not called."""
        timer = TimerSentinel(threshold=1.0)

        with pytest.raises(RuntimeError, match="Timer not started"):
            timer.end()

    def test_report_without_end_raises_error(self):
        """Test report() raises RuntimeError if end() not called."""
        timer = TimerSentinel(threshold=1.0)
        timer.start()

        with pytest.raises(RuntimeError, match="Timer not ended"):
            timer.report()


class TestTimerSentinelContextManager:
    """Test context manager usage."""

    def test_context_manager_basic(self):
        """Test basic context manager usage."""
        with TimerSentinel(threshold=1.0, name="test") as timer:
            time.sleep(0.1)
            assert timer._timer is not None

        # After context, timer should be stopped
        assert timer._total_time is not None
        assert timer._total_time >= 0.1

    def test_context_manager_with_exception(self):
        """Test context manager propagates exceptions."""
        timer = TimerSentinel(threshold=1.0, name="test")

        with pytest.raises(ValueError):
            with timer:
                raise ValueError("Test error")

        # Timer should still be stopped even with exception
        assert timer._total_time is not None


class TestTimerSentinelDecorator:
    """Test decorator usage."""

    def test_decorator_basic(self):
        """Test basic decorator usage."""

        @TimerSentinel(threshold=1.0)
        def slow_function():
            time.sleep(0.1)
            return "done"

        result = slow_function()
        assert result == "done"

    def test_decorator_uses_function_name(self):
        """Test decorator uses function name when no name provided."""
        timer_instance = TimerSentinel(threshold=1.0)

        @timer_instance
        def my_function():
            pass

        my_function()
        assert timer_instance.name == "my_function"

    def test_decorator_with_arguments(self):
        """Test decorator works with function arguments."""

        @TimerSentinel(threshold=1.0)
        def add(a, b):
            return a + b

        result = add(2, 3)
        assert result == 5

    def test_decorator_preserves_function_metadata(self):
        """Test decorator preserves function name and docstring."""

        @TimerSentinel(threshold=1.0)
        def documented_function():
            """This is a docstring."""
            pass

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a docstring."


class TestTimerSentinelLogging:
    """Test logging functionality."""

    def test_no_log_when_under_threshold(self, caplog):
        """Test no log when execution is under threshold."""
        with caplog.at_level(logging.WARNING):
            timer = TimerSentinel(threshold=1.0, name="test")
            timer.start()
            time.sleep(0.1)
            timer.end()
            timer.report()

        assert len(caplog.records) == 0

    def test_log_when_exceeds_threshold(self, caplog):
        """Test logs when execution exceeds threshold."""
        with caplog.at_level(logging.WARNING):
            timer = TimerSentinel(threshold=0.05, name="test")
            timer.start()
            time.sleep(0.1)
            timer.end()
            timer.report()

        assert len(caplog.records) == 1
        assert "OVERTIME" in caplog.text
        assert "test" in caplog.text

    def test_custom_log_keyword(self, caplog):
        """Test custom logging keyword is used."""
        with caplog.at_level(logging.WARNING):
            timer = TimerSentinel(threshold=0.05, name="test", on_exceed_keyword="SLOW")
            timer.start()
            time.sleep(0.1)
            timer.end()
            timer.report()

        assert "SLOW" in caplog.text

    def test_custom_log_level(self, caplog):
        """Test custom logging level is used."""
        with caplog.at_level(logging.ERROR):
            timer = TimerSentinel(
                threshold=0.05, name="test", on_exceed_level=logging.ERROR
            )
            timer.start()
            time.sleep(0.1)
            timer.end()
            timer.report()

        assert len(caplog.records) == 1
        assert caplog.records[0].levelno == logging.ERROR


class TestTimerSentinelCallback:
    """Test callback functionality."""

    def test_callback_not_called_under_threshold(self):
        """Test callback is not called when under threshold."""
        callback_called = []

        def callback():
            callback_called.append(True)

        timer = TimerSentinel(threshold=1.0, name="test", on_exceed_callback=callback)
        timer.start()
        time.sleep(0.1)
        timer.end()
        timer.report()

        assert len(callback_called) == 0

    def test_callback_called_when_exceeds_threshold(self):
        """Test callback is called when threshold exceeded."""
        callback_called = []

        def callback():
            callback_called.append(True)

        timer = TimerSentinel(threshold=0.05, name="test", on_exceed_callback=callback)
        timer.start()
        time.sleep(0.1)
        timer.end()
        timer.report()

        assert len(callback_called) == 1

    def test_callback_with_arguments(self):
        """Test callback receives correct arguments."""
        results = {}

        def callback(name, value):
            results["name"] = name
            results["value"] = value

        timer = TimerSentinel(
            threshold=0.05,
            name="test",
            on_exceed_callback=callback,
            callback_args={"name": "test_name", "value": 42},
        )
        timer.start()
        time.sleep(0.1)
        timer.end()
        timer.report()

        assert results["name"] == "test_name"
        assert results["value"] == 42


class TestTimerSentinelEdgeCases:
    """Test edge cases and special scenarios."""

    def test_multiple_executions_same_instance(self):
        """Test same instance can be reused for multiple timings."""
        timer = TimerSentinel(threshold=0.05, name="reusable")

        # First execution
        timer.start()
        time.sleep(0.1)
        timer.end()
        first_time = timer._total_time

        # Second execution
        timer.start()
        time.sleep(0.1)
        timer.end()
        second_time = timer._total_time

        assert first_time is not None
        assert second_time is not None
        assert first_time != second_time

    def test_execution_id_is_unique(self):
        """Test each instance has unique execution ID."""
        timer1 = TimerSentinel(threshold=1.0)
        timer2 = TimerSentinel(threshold=1.0)

        assert timer1._execution_id != timer2._execution_id
        assert len(timer1._execution_id) == 8
        assert len(timer2._execution_id) == 8
