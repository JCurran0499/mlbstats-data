import logging
import random
import time
from datetime import date, datetime
from zoneinfo import ZoneInfo
import statsapi
from shared import secrets, db, schedule
from util import sql, entry

logger = logging.getLogger()

PLAYER_STATS_MAX_ATTEMPTS = 4
PLAYER_STATS_BASE_BACKOFF_SECONDS = 1.0

# --- API fetch layer ---------------------------------------------------------

def fetch_player_stats(player_id: int, season: int):
    logger.info("Fetching stats for player %s in season %s", player_id, season)
    for attempt in range(1, PLAYER_STATS_MAX_ATTEMPTS + 1):
        try:
            stats = statsapi.player_stat_data(player_id, group="[hitting,pitching,fielding]", type="season", season=season)
            return stats["stats"]
        except Exception as exc:
            if attempt == PLAYER_STATS_MAX_ATTEMPTS:
                logger.warning("statsapi exhausted retries for player %s after %s attempts", player_id, attempt)
                raise
            delay = PLAYER_STATS_BASE_BACKOFF_SECONDS * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
            logger.warning(
                "statsapi call failed for player %s (attempt %s/%s): %s — retrying in %.2fs",
                player_id, attempt, PLAYER_STATS_MAX_ATTEMPTS, exc, delay,
            )
            time.sleep(delay)

# --- DB sync layer -----------------------------------------------------------

def sync_player_stats(cur, player_id: int, team_id: int, season: int):
    stats = fetch_player_stats(player_id, season)
    batting_stats = entry.parse_batting_stats(stats, player_id, team_id, season)
    pitching_stats = entry.parse_pitching_stats(stats, player_id, team_id, season)
    all_fielding_stats = entry.parse_fielding_stats(stats, player_id, team_id, season)

    if batting_stats:
        sql.upsert_batting_stats(cur, batting_stats)
        logger.info("Upserted batting stats for player %s in season %s", player_id, season)

    if pitching_stats:
        sql.upsert_pitching_stats(cur, pitching_stats)
        logger.info("Upserted pitching stats for player %s in season %s", player_id, season)

    if all_fielding_stats:
        for fielding_stats in all_fielding_stats:
            sql.upsert_fielding_stats(cur, fielding_stats)
            logger.info("Upserted fielding stats for player %s in position %s in season %s", player_id, fielding_stats["position"], season)

# --- Orchestration -----------------------------------------------------------

_ET = ZoneInfo("America/New_York")
_EARLIEST_HOUR_ET = 9

def lambda_handler(event, context):
    now_et = datetime.now(_ET)
    if now_et.hour < _EARLIEST_HOUR_ET:
        logger.info("Skipping stats_sync: before %sam ET", _EARLIEST_HOUR_ET)
        return {"skipped": True, "reason": "before_earliest_hour"}

    today = now_et.date()
    season = today.year

    if not schedule.validate_in_season():
        logger.info("Skipping stats_sync: not in season")
        return {"skipped": True, "reason": "outside_season_window"}
    
    db_connection_string = secrets.get_connection_string()
    conn = db.start_connection(db_connection_string)
    try:
        logger.info("Starting stats_sync")

        try:
            with conn.cursor() as cur:
                teams = sql.fetch_teams(cur)
        except Exception:
            logger.exception(
                "DB error retrieving teams"
            )
            return {"synced": False, "reason": "db_error_retrieving_teams"}

        for team in teams:
            team_id = team["id"]
            team_name = team["name"]

            try:
                with conn:
                    with conn.cursor() as cur:
                        players = sql.fetch_active_players(cur, team_id, season)
            except Exception:
                logger.exception(
                    "DB error fetching active players for team %s (%s) — skipping team",
                    team_id, team_name,
                )
                continue

            logger.info("Syncing stats for team %s (%s) with %s active players", team_id, team_name, len(players))

            for player_id in players:
                try:
                    with conn:
                        with conn.cursor() as cur:
                            sync_player_stats(cur, player_id, team_id, season)
                except Exception:
                    logger.exception(
                        "Error syncing player %s on team %s (%s) — rolled back, continuing",
                        player_id, team_id, team_name,
                    )

        logger.info("Finished stats_sync")
    finally:
        conn.close()

    return {"synced": True}