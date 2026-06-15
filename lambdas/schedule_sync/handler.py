import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import statsapi
from util import dynamo
from shared import schedule

logger = logging.getLogger()
logger.setLevel(logging.INFO)

_ET = ZoneInfo("America/New_York")


# --- API fetch layer ---------------------------------------------------------

def fetch_games(now: datetime) -> list[dict]:
    today = now.strftime("%Y-%m-%d")
    logger.info("Fetching today's schedule (%s) from Stats API", today)
    return statsapi.schedule(date=today, sportId=1)

# --- Sync layer --------------------------------------------------------------

def compare_schedules(sched1: dict, sched2: dict):
    comparison_keys = [
        "game_datetime", "status", "home_probable_pitcher", "away_probable_pitcher",
        "home_pitcher_note", "away_pitcher_note"
    ]

    for key in comparison_keys:
        if sched1.get(key) != sched2.get(key):
            logger.info("Out of date field \"%s\" for game %s", key, sched1["game_id"])
            return False
    
    return True

# --- Orchestration -----------------------------------------------------------

def lambda_handler(event, context):
    if not schedule.validate_in_season():
        logger.info("Skipping game_dispatcher: not in season")
        return {"skipped": True, "reason": "outside_season_window"}

    now = datetime.now(_ET)
    games = fetch_games(now)
    schedule_map = dynamo.get_games_map(now)

    for game in games:
        game_id = game["game_id"]
        if game_id not in schedule_map:
            dynamo.insert_game(game)

        else:
            in_sync = compare_schedules(game, schedule_map[game_id])
            if not in_sync:
                dynamo.update_game(game)

    return {}
