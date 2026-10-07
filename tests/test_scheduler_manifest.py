from config.scheduler.manifest import build_manifest


def test_scheduler_manifest_contains_enabled_users():
    manifest = build_manifest()

    assert manifest["version"] == "1.0"
    assert len(manifest["users"]) == 2

    users = {
        user["user_id"]: user
        for user in manifest["users"]
    }

    employee_001 = users["employee-001"]
    assert employee_001["user_config"] == "config/users/example.yaml"
    assert employee_001["enabled"] is True
    assert employee_001["schedule"]["timezone"] == "Asia/Kolkata"
    assert employee_001["schedule"]["time"] == "08:00"

    employee_002 = users["employee-002"]
    assert employee_002["user_config"] == "config/users/employee-002.yaml"
    assert employee_002["enabled"] is True
    assert employee_002["schedule"]["timezone"] == "Asia/Kolkata"
    assert employee_002["schedule"]["time"] == "08:30"


def test_scheduler_manifest_contains_only_scheduler_fields():
    manifest = build_manifest()

    for user in manifest["users"]:
        assert set(user.keys()) == {
            "user_id",
            "user_config",
            "enabled",
            "schedule",
        }
