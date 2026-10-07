from pathlib import Path

import pytest

from config.resolver import (
    ConfigurationError,
    resolve_user_config,
)


ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG = ROOT / "config" / "users" / "example.yaml"


def test_example_configuration_resolves():
    result = resolve_user_config(str(EXAMPLE_CONFIG))

    assert result["user"]["id"] == "employee-001"
    assert result["profile"]["id"] == "ai-engineering"
    assert "agentic_ai" in result["topics"]
    assert result["schedule"]["timezone"] == "Asia/Kolkata"
    assert result["schedule"]["time"] == "17:55"
    assert result["delivery"]["channel"] == "email"


def test_invalid_profile_is_rejected(tmp_path):
    config = tmp_path / "invalid.yaml"

    config.write_text(
        """
user:
  id: employee-001

profile:
  id: does-not-exist

topics:
  - agentic_ai

schedule:
  timezone: Asia/Kolkata
  time: "08:00"

delivery:
  channel: email
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError):
        resolve_user_config(str(config))


def test_topic_not_supported_by_profile_is_rejected(tmp_path):
    config = tmp_path / "invalid-topic.yaml"

    config.write_text(
        """
user:
  id: employee-001

profile:
  id: ai-engineering

topics:
  - robotics_multimodal

schedule:
  timezone: Asia/Kolkata
  time: "08:00"

delivery:
  channel: email
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError):
        resolve_user_config(str(config))
