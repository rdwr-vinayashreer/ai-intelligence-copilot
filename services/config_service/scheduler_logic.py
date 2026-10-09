from datetime import datetime


def get_scheduled_occurrence(
    local_now: datetime,
    configured_time: str,
) -> datetime | None:
    """
    Return today's configured briefing occurrence if it is due.

    A briefing remains eligible after its configured time until it is
    dispatched. The caller is responsible for checking dispatch records.

    The returned datetime retains the timezone of local_now.
    """
    try:
        hour_text, minute_text = configured_time.split(":")
        hour = int(hour_text)
        minute = int(minute_text)

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return None

        if len(hour_text) != 2 or len(minute_text) != 2:
            return None
    except (AttributeError, TypeError, ValueError):
        return None

    scheduled = local_now.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0,
    )

    if local_now < scheduled:
        return None

    return scheduled
