from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import psycopg
import yaml
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from psycopg.rows import dict_row
from pydantic import BaseModel, Field
from services.config_service.scheduler_logic import get_scheduled_occurrence


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

PROFILES_DIR = ROOT / "config" / "profiles"
FRONTEND_DIR = ROOT / "frontend"


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ai_intelligence:ai_intelligence_dev@localhost:5432/ai_intelligence",
)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

SCHEDULER_API_KEY = os.getenv("SCHEDULER_API_KEY")

AUTH_USER_HEADER = os.getenv(
    "AUTH_USER_HEADER",
    "X-Authenticated-User",
)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def require_authenticated_user(
    authenticated_user: str | None = Header(
        default=None,
        alias=AUTH_USER_HEADER,
    ),
) -> str:
    """
    Resolve the authenticated employee identity.

    Development:
        Allows requests without an identity header and uses local-dev.

    Production:
        Requires the trusted identity header supplied by the authentication
        layer / ingress.
    """

    if ENVIRONMENT == "development":
        return authenticated_user or "local-dev"

    if not authenticated_user:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identity is required",
        )

    return authenticated_user


def require_scheduler_auth(
    scheduler_key: str | None = Header(
        default=None,
        alias="X-Scheduler-Key",
    ),
) -> None:
    """
    Protect scheduler endpoints.

    The scheduler key must be supplied by n8n or another trusted scheduler.

    In development, authentication is still enforced when SCHEDULER_API_KEY
    is configured. The bypass only exists when running locally without a key.
    """

    if ENVIRONMENT == "development" and not SCHEDULER_API_KEY:
        return

    if not SCHEDULER_API_KEY or scheduler_key != SCHEDULER_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid scheduler credentials",
        )


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def get_connection():
    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
    )


def initialize_database() -> None:
    """
    Initialize the database tables required by the configuration service.

    This is suitable for the current development/prototype deployment.
    A proper migration system such as Alembic can replace this later for
    production schema management.
    """

    with get_connection() as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                profile_id TEXT NOT NULL,
                topics_json TEXT NOT NULL,
                timezone TEXT NOT NULL,
                briefing_time TEXT NOT NULL,
                delivery_channel TEXT NOT NULL,
                delivery_destination TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_user_preferences_schedule
            ON user_preferences(timezone, briefing_time)
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS scheduler_dispatches (
                user_id TEXT NOT NULL,
                scheduled_at TEXT NOT NULL,
                correlation_id TEXT NOT NULL UNIQUE,
                dispatched_at TEXT NOT NULL,
                PRIMARY KEY (user_id, scheduled_at)
            )
            """
        )

        connection.commit()


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Intelligence Configuration Service",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Static frontend
# ---------------------------------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)


# ---------------------------------------------------------------------------
# Database initialization
# ---------------------------------------------------------------------------

initialize_database()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class PreferenceRequest(BaseModel):
    user_id: str = Field(
        min_length=1,
        max_length=100,
    )

    profile: str = Field(
        min_length=1,
        max_length=100,
    )

    topics: list[str] = Field(
        min_length=1,
    )

    timezone: str = Field(
        min_length=1,
        max_length=100,
    )

    time: str = Field(
        pattern=r"^\d{2}:\d{2}$",
    )

    delivery: dict[str, str]


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

SUPPORTED_CHANNELS = {
    "email",
    "teams",
    "slack",
    "webhook",
}


USER_ID_PATTERN = re.compile(
    r"^[a-zA-Z0-9._-]+$"
)


def load_profile(profile_id: str) -> dict[str, Any]:
    profile_path = PROFILES_DIR / f"{profile_id}.yaml"

    if not profile_path.exists():
        raise HTTPException(
            status_code=400,
            detail=f"Unknown intelligence profile: {profile_id}",
        )

    with profile_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        profile = yaml.safe_load(file) or {}

    return profile


def validate_preferences(payload: PreferenceRequest) -> None:
    """
    Validate user configuration before writing it to PostgreSQL.
    """

    # -----------------------------------------------------------------------
    # User ID
    # -----------------------------------------------------------------------

    if not USER_ID_PATTERN.fullmatch(payload.user_id):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid user ID. Use letters, numbers, '.', '_' or '-'."
            ),
        )

    # -----------------------------------------------------------------------
    # Profile
    # -----------------------------------------------------------------------

    profile = load_profile(payload.profile)

    profile_config = profile.get("profile", {})
    profile_categories = set(
        profile.get("categories", [])
    )

    if not profile_config.get("id"):
        raise HTTPException(
            status_code=500,
            detail=f"Profile {payload.profile} is missing profile.id.",
        )

    if not profile_categories:
        raise HTTPException(
            status_code=500,
            detail=f"Profile {payload.profile} has no categories.",
        )

    # -----------------------------------------------------------------------
    # Topics
    # -----------------------------------------------------------------------

    requested_topics = set(payload.topics)

    unsupported_topics = (
        requested_topics - profile_categories
    )

    if unsupported_topics:
        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    "One or more selected topics are not supported "
                    "by the selected profile."
                ),
                "unsupported_topics": sorted(
                    unsupported_topics
                ),
                "profile": payload.profile,
            },
        )

    # -----------------------------------------------------------------------
    # Time
    # -----------------------------------------------------------------------

    if len(payload.time) != 5:
        raise HTTPException(
            status_code=400,
            detail="Briefing time must use HH:MM format.",
        )

    hour, minute = map(
        int,
        payload.time.split(":"),
    )

    if not (
        0 <= hour <= 23
        and 0 <= minute <= 59
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid briefing time.",
        )

    # -----------------------------------------------------------------------
    # Timezone
    # -----------------------------------------------------------------------

    try:
        ZoneInfo(payload.timezone)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid timezone: {payload.timezone}",
        )

    # -----------------------------------------------------------------------
    # Delivery
    # -----------------------------------------------------------------------

    channel = payload.delivery.get(
        "channel",
        "",
    ).lower()

    destination = payload.delivery.get(
        "destination",
        "",
    ).strip()

    if channel not in SUPPORTED_CHANNELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported delivery channel: {channel}",
        )

    if not destination:
        raise HTTPException(
            status_code=400,
            detail="Delivery destination is required.",
        )

    if channel == "email":
        email_pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"

        if not re.fullmatch(
            email_pattern,
            destination,
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid email destination.",
            )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/healthz")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "ai-intelligence-config",
    }


@app.get("/readyz")
def readiness() -> dict[str, str]:
    """
    Readiness check.

    Unlike /healthz, this verifies that the service can reach PostgreSQL.
    """

    try:
        with get_connection() as connection:
            connection.execute("SELECT 1")
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Configuration service is not ready",
        )

    return {
        "status": "ready",
        "service": "ai-intelligence-config",
    }


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------

@app.get("/api/v1/profiles")
def profiles() -> list[dict[str, Any]]:
    result = []

    for profile_path in sorted(
        PROFILES_DIR.glob("*.yaml")
    ):
        with profile_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            profile = yaml.safe_load(file) or {}

        profile_data = profile.get(
            "profile",
            {},
        )

        result.append(
            {
                "id": profile_data.get(
                    "id",
                    profile_path.stem,
                ),
                "name": profile_data.get(
                    "name",
                    profile_path.stem,
                ),
                "audience": profile_data.get(
                    "audience",
                    "",
                ),
                "categories": profile.get(
                    "categories",
                    [],
                ),
            }
        )

    return result


# ---------------------------------------------------------------------------
# User configuration
# ---------------------------------------------------------------------------

@app.get("/api/v1/users/{user_id}")
def get_user(
    user_id: str,
    authenticated_user: str = Depends(
        require_authenticated_user
    ),
) -> dict[str, Any]:

    # Production identity enforcement.
    #
    # The authentication/ingress layer must provide the trusted employee
    # identity in AUTH_USER_HEADER.
    if (
        ENVIRONMENT != "development"
        and authenticated_user != user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Cannot access another user's configuration",
        )

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM user_preferences
            WHERE user_id = %s
            """,
            (user_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="User configuration not found.",
        )

    return {
        "user_id": row["user_id"],
        "profile": row["profile_id"],
        "topics": json.loads(
            row["topics_json"]
        ),
        "timezone": row["timezone"],
        "time": row["briefing_time"],
        "delivery": {
            "channel": row["delivery_channel"],
            "destination": row[
                "delivery_destination"
            ],
        },
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@app.put("/api/v1/users/{user_id}")
def save_user(
    user_id: str,
    payload: PreferenceRequest,
    authenticated_user: str = Depends(
        require_authenticated_user
    ),
) -> dict[str, Any]:

    # Production identity enforcement.
    if (
        ENVIRONMENT != "development"
        and authenticated_user != user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Cannot modify another user's configuration",
        )

    # Prevent changing another user's configuration through the payload.
    if user_id != payload.user_id:
        raise HTTPException(
            status_code=400,
            detail="Path user_id must match payload user_id.",
        )

    validate_preferences(payload)

    now = datetime.now(
        timezone.utc
    ).isoformat()

    channel = payload.delivery[
        "channel"
    ].lower()

    destination = payload.delivery[
        "destination"
    ].strip()

    with get_connection() as connection:

        existing = connection.execute(
            """
            SELECT user_id
            FROM user_preferences
            WHERE user_id = %s
            """,
            (payload.user_id,),
        ).fetchone()

        if existing:

            connection.execute(
                """
                UPDATE user_preferences
                SET
                    profile_id = %s,
                    topics_json = %s,
                    timezone = %s,
                    briefing_time = %s,
                    delivery_channel = %s,
                    delivery_destination = %s,
                    updated_at = %s
                WHERE user_id = %s
                """,
                (
                    payload.profile,
                    json.dumps(
                        payload.topics
                    ),
                    payload.timezone,
                    payload.time,
                    channel,
                    destination,
                    now,
                    payload.user_id,
                ),
            )

            operation = "updated"

        else:

            connection.execute(
                """
                INSERT INTO user_preferences (
                    user_id,
                    profile_id,
                    topics_json,
                    timezone,
                    briefing_time,
                    delivery_channel,
                    delivery_destination,
                    created_at,
                    updated_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    payload.user_id,
                    payload.profile,
                    json.dumps(
                        payload.topics
                    ),
                    payload.timezone,
                    payload.time,
                    channel,
                    destination,
                    now,
                    now,
                ),
            )

            operation = "created"

        connection.commit()

    return {
        "status": "success",
        "operation": operation,
        "user_id": payload.user_id,
        "updated_at": now,
    }


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

@app.get("/api/v1/scheduler/due-users")
def get_due_users(
    _: None = Depends(
        require_scheduler_auth
    ),
) -> dict[str, Any]:
    """
    Return users whose configured briefing time matches the current minute
    in their configured timezone and who have not yet been dispatched for
    that scheduled occurrence.
    """

    now_utc = datetime.now(
        timezone.utc
    )

    due_users = []

    with get_connection() as connection:

        users = connection.execute(
            """
            SELECT
                user_id,
                profile_id,
                topics_json,
                timezone,
                briefing_time,
                delivery_channel,
                delivery_destination
            FROM user_preferences
            """
        ).fetchall()

        for user in users:

            try:
                local_now = now_utc.astimezone(
                    ZoneInfo(
                        user["timezone"]
                    )
                )
            except Exception:
                # Invalid timezone should normally be prevented by
                # configuration validation. Skip defensively if encountered.
                continue

            configured_time = user["briefing_time"]

            # Keep a due briefing eligible even if n8n polls after its
            # configured minute. The occurrence remains today's configured
            # local time, not the time at which the scheduler polled.
            scheduled_occurrence = get_scheduled_occurrence(
                local_now,
                configured_time,
            )
            if scheduled_occurrence is None:
                continue

            scheduled_at = scheduled_occurrence.strftime(
                "%Y-%m-%dT%H:%M:%S%z"
            )

            correlation_id = (
                f"AIINT-{user['user_id']}-"
                f"{scheduled_occurrence.strftime('%Y%m%d-%H%M')}"
            )

            already_dispatched = connection.execute(
                """
                SELECT 1
                FROM scheduler_dispatches
                WHERE user_id = %s
                  AND scheduled_at = %s
                """,
                (
                    user["user_id"],
                    scheduled_at,
                ),
            ).fetchone()

            if already_dispatched:
                continue

            due_users.append(
                {
                    "user_id": user[
                        "user_id"
                    ],
                    "user_config": {
                        "user_id": user[
                            "user_id"
                        ],
                        "profile": user[
                            "profile_id"
                        ],
                        "topics": json.loads(
                            user["topics_json"]
                        ),
                        "schedule": {
                            "timezone": user[
                                "timezone"
                            ],
                            "time": user[
                                "briefing_time"
                            ],
                        },
                        "delivery": {
                            "channel": user[
                                "delivery_channel"
                            ],
                            "destination": user[
                                "delivery_destination"
                            ],
                        },
                    },
                    "scheduled_at": scheduled_at,
                    "correlation_id": correlation_id,
                }
            )

    return {
        "status": "success",
        "checked_at": now_utc.isoformat(),
        "users": due_users,
        "count": len(due_users),
    }


@app.post("/api/v1/scheduler/dispatches")
def record_dispatch(
    payload: dict[str, str],
    _: None = Depends(
        require_scheduler_auth
    ),
) -> dict[str, str]:
    """
    Record a successfully dispatched scheduled run.

    Idempotency key:
        user_id + scheduled_at

    correlation_id remains stable for the scheduled occurrence.
    """

    required = [
        "user_id",
        "scheduled_at",
        "correlation_id",
    ]

    missing = [
        field
        for field in required
        if not payload.get(field)
    ]

    if missing:
        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    "Missing required dispatch fields."
                ),
                "missing": missing,
            },
        )

    dispatched_at = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:

        connection.execute(
            """
            INSERT INTO scheduler_dispatches (
                user_id,
                scheduled_at,
                correlation_id,
                dispatched_at
            )
            VALUES (
                %s,
                %s,
                %s,
                %s
            )
            ON CONFLICT (
                user_id,
                scheduled_at
            )
            DO NOTHING
            """,
            (
                payload["user_id"],
                payload["scheduled_at"],
                payload["correlation_id"],
                dispatched_at,
            ),
        )

        connection.commit()

    return {
        "status": "recorded",
        "user_id": payload["user_id"],
        "correlation_id": payload[
            "correlation_id"
        ],
    }


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------

@app.get("/")
def frontend() -> FileResponse:
    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


app.mount(
    "/static",
    StaticFiles(
        directory=FRONTEND_DIR
    ),
    name="static",
)