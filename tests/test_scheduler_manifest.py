import json

from config.scheduler.manifest import build_manifest


def test_scheduler_manifest_contains_enabled_user():
    manifest = build_manifest()

    assert manifest["version"] == "1.0"
    assert len(manifest["users"]) == 1

    user = manifest["users"][0]

    assert user["user_id"] == "employee-001"
    assert user["user_config"] == "config/users/example.yaml"
    assert user["enabled"] is True
    assert user["schedule"]["timezone"] == "Asia/Kolkata"
    assert user["schedule"]["time"] == "17:55"

def test_scheduler_manifest_contains_only_scheduler_fields():
    manifest = build_manifest()
    user = manifest["users"][0]

    assert set(user.keys()) == {
        "user_id",
        "user_config",
        "enabled",
        "schedule",
    }
