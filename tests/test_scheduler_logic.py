from datetime import datetime
from zoneinfo import ZoneInfo

from services.config_service.scheduler_logic import get_scheduled_occurrence


IST = ZoneInfo("Asia/Kolkata")


def test_briefing_is_not_due_before_configured_time():
    now = datetime(2026, 10, 9, 10, 47, tzinfo=IST)

    assert get_scheduled_occurrence(now, "10:48") is None


def test_briefing_is_due_at_configured_time():
    now = datetime(2026, 10, 9, 10, 48, tzinfo=IST)

    result = get_scheduled_occurrence(now, "10:48")

    assert result == datetime(2026, 10, 9, 10, 48, tzinfo=IST)


def test_late_poll_returns_original_scheduled_occurrence():
    # n8n polls at 10:56, eight minutes after the configured time.
    now = datetime(2026, 10, 9, 10, 56, tzinfo=IST)

    result = get_scheduled_occurrence(now, "10:48")

    assert result == datetime(2026, 10, 9, 10, 48, tzinfo=IST)
    assert result.strftime("%Y-%m-%dT%H:%M:%S%z") == (
        "2026-10-09T10:48:00+0530"
    )


def test_next_day_uses_next_days_scheduled_occurrence():
    now = datetime(2026, 10, 10, 10, 56, tzinfo=IST)

    result = get_scheduled_occurrence(now, "10:48")

    assert result == datetime(2026, 10, 10, 10, 48, tzinfo=IST)


def test_invalid_configured_time_is_not_due():
    now = datetime(2026, 10, 9, 11, 0, tzinfo=IST)

    assert get_scheduled_occurrence(now, "25:00") is None
    assert get_scheduled_occurrence(now, "invalid") is None
    assert get_scheduled_occurrence(now, "9:05") is None
