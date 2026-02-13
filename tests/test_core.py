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
