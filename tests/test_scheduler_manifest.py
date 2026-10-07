import json

from config.scheduler.manifest import build_manifest


def test_scheduler_manifest_contains_enabled_users():
    manifest = build_manifest()

    assert manifest["version"] == "1.0"

    users = {user["user_id"]: user for user in manifest["users"]}

    assert set(users) == {
        "employee-001",
        "employee-002",
        "employee-003",
    }

    assert users["employee-001"]["schedule"]["time"] == "16:00"
    assert users["employee-002"]["schedule"]["time"] == "16:20"
    assert users["employee-003"]["schedule"]["time"] == "16:22"

    assert all(user["enabled"] for user in users.values())


def test_scheduler_manifest_contains_only_scheduler_fields():
    manifest = build_manifest()
    user = manifest["users"][0]

    assert set(user.keys()) == {
        "user_id",
        "user_config",
        "enabled",
        "schedule",
    }
