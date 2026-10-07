from pathlib import Path
import json
import sys

from config.resolver import ConfigurationError, resolve_user_config


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "config" / "scheduler" / "registry.yaml"
OUTPUT = ROOT / "config" / "scheduler" / "manifest.json"


def load_registry():
    import yaml

    if not REGISTRY.exists():
        raise ConfigurationError(f"Scheduler registry not found: {REGISTRY}")

    with REGISTRY.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ConfigurationError("Invalid scheduler registry")

    users = data.get("users", [])

    if not isinstance(users, list):
        raise ConfigurationError("scheduler.users must be a list")

    return users


def build_manifest():
    manifest_users = []

    for entry in load_registry():
        if not isinstance(entry, dict):
            raise ConfigurationError("Each scheduler registry entry must be an object")

        if not entry.get("enabled", True):
            continue

        user_config = entry.get("user_config")

        if not user_config:
            raise ConfigurationError(
                "Enabled scheduler entry must contain user_config"
            )

        config_path = ROOT / user_config

        if not config_path.exists():
            raise ConfigurationError(
                f"User configuration not found: {user_config}"
            )

        resolved = resolve_user_config(str(config_path))

        manifest_users.append(
            {
                "user_id": resolved["user"]["id"],
                "user_config": user_config,
                "enabled": True,
                "schedule": {
                    "timezone": resolved["schedule"]["timezone"],
                    "time": resolved["schedule"]["time"],
                },
            }
        )

    return {
        "version": "1.0",
        "users": manifest_users,
    }


def main():
    manifest = build_manifest()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    try:
        main()
    except ConfigurationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
