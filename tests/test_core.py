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
