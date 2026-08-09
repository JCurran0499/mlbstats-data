import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from util import dynamo, ecs
from shared import schedule

logger = logging.getLogger()
logger.setLevel(logging.INFO)

_ET = ZoneInfo("America/New_York")

# How far ahead of first pitch we spin a tracker up.
_LEAD_TIME = timedelta(minutes=5)

# Statuses for games that are over (or never happening) — never dispatch these.
_TERMINAL_STATUSES = {
    "Final", "Postponed", "Suspended"
}


# --- Sync layer --------------------------------------------------------------

def _parse_start(game_datetime: str) -> datetime:
    # statsapi returns e.g. "2026-06-14T17:05:00Z"; fromisoformat handles the Z.
    return datetime.fromisoformat(game_datetime).astimezone(_ET)


def is_dispatchable(game: dict, now: datetime) -> bool:
    status = game.get("status", "")
    if status in _TERMINAL_STATUSES:
        return False

    game_datetime = game.get("game_datetime")
    if not game_datetime:
        logger.warning("Game %s has no game_datetime; skipping", game.get("game_id"))
        return False

    try:
        starts_at = _parse_start(game_datetime)
    except ValueError:
        logger.warning(
            "Game %s has unparseable game_datetime %r; skipping",
            game.get("game_id"), game_datetime,
        )
        return False

    # Already underway, or starting within the lead window.
    return starts_at <= now + _LEAD_TIME


# --- Orchestration -----------------------------------------------------------

def lambda_handler(event, context):
    if not schedule.validate_in_season():
        logger.info("Skipping game_dispatcher: not in season")
        return {"skipped": True, "reason": "outside_season_window"}

    now = datetime.now(_ET)
    games = dynamo.get_todays_games(now)
    candidates = [g for g in games if is_dispatchable(g, now)]
    logger.info("%s of %s games are dispatchable", len(candidates), len(games))

    if not candidates:
        return {"dispatched": 0, "skipped_existing": 0}

    tracked = ecs.get_tracked_game_ids()
    logger.info("%s games already have a running tracker", len(tracked))

    dispatched = 0
    skipped_existing = 0
    for game in candidates:
        game_id = int(game["game_id"])
        if game_id in tracked:
            skipped_existing += 1
            continue

        try:
            ecs.start_tracker(game_id)
            dispatched += 1
        except Exception:
            logger.exception("Failed to start tracker for game %s", game_id)

    logger.info(
        "Dispatch complete: %s started, %s already tracked",
        dispatched, skipped_existing,
    )
    return {"dispatched": dispatched, "skipped_existing": skipped_existing}
