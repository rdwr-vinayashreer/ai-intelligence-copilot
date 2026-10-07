from pathlib import Path
import yaml


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "config" / "default.yaml"
PROFILE_DIR = ROOT / "config" / "profiles"


class ConfigurationError(Exception):
    pass


def load_yaml(path: Path):
    if not path.exists():
        raise ConfigurationError(f"Configuration file not found: {path}")

    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ConfigurationError(f"Invalid YAML structure: {path}")

    return data


def resolve_user_config(user_config_path: str):
    user = load_yaml(Path(user_config_path))
    defaults = load_yaml(DEFAULT_CONFIG)

    user_section = user.get("user", {})
    profile_section = user.get("profile", {})
    topics = user.get("topics", [])
    schedule = user.get("schedule", {})
    delivery = user.get("delivery", {})

    user_id = user_section.get("id")
    profile_id = profile_section.get("id")

    if not user_id:
        raise ConfigurationError("user.id is required")

    if not profile_id:
        raise ConfigurationError("profile.id is required")

    if not isinstance(topics, list) or not topics:
        raise ConfigurationError("topics must contain at least one topic")

    profile_path = PROFILE_DIR / f"{profile_id}.yaml"

    if not profile_path.exists():
        raise ConfigurationError(
            f"Profile '{profile_id}' does not exist"
        )

    profile = load_yaml(profile_path)

    profile_categories = set(profile.get("categories", []))

    invalid_topics = [
        topic for topic in topics
        if topic not in profile_categories
    ]

    if invalid_topics:
        raise ConfigurationError(
            f"Topics not supported by profile '{profile_id}': "
            + ", ".join(invalid_topics)
        )

    timezone = schedule.get("timezone")
    time = schedule.get("time")

    if not timezone:
        raise ConfigurationError("schedule.timezone is required")

    if not time:
        raise ConfigurationError("schedule.time is required")

    channel = delivery.get("channel")

    if not channel:
        channel = defaults.get("delivery", {}).get("channel")

    if not channel:
        raise ConfigurationError("delivery.channel is required")

    allowed_channels = {
        "email",
        "teams",
        "slack",
        "webhook",
    }

    if channel not in allowed_channels:
        raise ConfigurationError(
            f"Unsupported delivery channel: {channel}"
        )

    destination = delivery.get("destination")

    if channel == "email" and not destination:
        raise ConfigurationError(
            "delivery.destination is required for email delivery"
        )

    return {
        "user": {
            "id": user_id,
        },
        "profile": {
            "id": profile_id,
            "name": profile.get("profile", {}).get("name"),
            "audience": profile.get("profile", {}).get("audience"),
        },
        "topics": topics,
        "schedule": {
            "timezone": timezone,
            "time": time,
        },
        "delivery": {
            "channel": channel,
            "destination": delivery.get("destination"),
        },
        "research": {
            "window_hours": profile.get(
                "research", {}
            ).get(
                "window_hours",
                defaults.get("research", {}).get("window_hours", 24),
            ),
        },
        "briefing": profile.get("briefing", {}),
    }
