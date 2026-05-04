import logging
from datetime import date

import statsapi
import psycopg2
from shared import secrets, db
from util import entry, sql

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# --- API fetch layer ---------------------------------------------------------

def fetch_season_dates(season: int):
    logger.info("Fetching MLB schedule for season %s from Stats API", season)
    schedule = statsapi.get("seasons", {"sportId": 1, "season": season})
    return schedule["seasons"]


def fetch_teams(season: int):
    logger.info("Fetching MLB teams from Stats API")
    teams = statsapi.get("teams", {"sportId": 1, "hydrate": "venue", "season": season})
    return teams["teams"]


def fetch_team_roster(team_id, team_name):
    logger.info("Fetching roster for team %s (%s)", team_id, team_name)
    roster = statsapi.get("team_roster", {"teamId": team_id, "rosterType": "40Man", "hydrate": "person"})
    return roster["roster"]

# --- DB sync layer -----------------------------------------------------------

def sync_team_roster(cur: psycopg2.extensions.cursor, team_id: int, season_year: int, players: list[dict]):
    db_open = sql.fetch_active_roster(cur, team_id, season_year)
    api_set = {p["player_id"]: p["status_code"] for p in players}
    added = dropped = updated = unchanged = 0

    for pid in set(db_open) - set(api_set):
        sql.close_roster_entry(cur, pid, team_id, season_year)
        logger.info("Dropped player %s from team %s", pid, team_id)
        dropped += 1

    for pid, status in api_set.items():
        if pid not in db_open:
            sql.insert_roster_entry(cur, pid, team_id, season_year, status)
            logger.info("Added player %s to team %s (status=%s)", pid, team_id, status)
            added += 1
        elif db_open[pid] != status:
            sql.update_roster_entry(cur, pid, team_id, season_year, status)
            logger.info(
                "Updated player %s on team %s: %s → %s",
                pid, team_id, db_open[pid], status,
            )
            updated += 1
        else:
            unchanged += 1

    return {"added": added, "dropped": dropped, "updated": updated, "unchanged": unchanged}

# --- Orchestration -----------------------------------------------------------

def lambda_handler(event, context):
    today = date.today()
    season = today.year

    season_schedule = fetch_season_dates(season)

    if not season_schedule:
        logger.info("Skipping roster_sync: no season data returned for season %s", season)
        return {"skipped": True, "reason": "no_season_data"}

    season_info = season_schedule[0]
    season_start = date.fromisoformat(season_info["seasonStartDate"])
    season_end = date.fromisoformat(season_info["seasonEndDate"])

    if today < season_start or today > season_end:
        logger.info(
            "Skipping roster_sync: today (%s) is outside season window (%s – %s)",
            today, season_start, season_end,
        )
        return {"skipped": True, "reason": "outside_season_window"}

    db_connection_string = secrets.get_connection_string()
    conn = db.start_connection(db_connection_string)
    try:
        logger.info("Starting roster_sync for season %s (date=%s)", season, today)

        teams = fetch_teams(season)
        totals = {
            "teams_ok": 0, "teams_failed": 0,
            "added": 0, "dropped": 0, "updated": 0, "unchanged": 0
        }

        for team in teams:
            team_id = team["id"]
            team_name = team["name"]

            try:
                roster = fetch_team_roster(team_id, team_name)
                players = [entry.parse_roster_entry(e, team_id) for e in roster]

                with conn:
                    with conn.cursor() as cur:
                        sql.upsert_team(cur, entry.parse_team(team))
                        for p in players:
                            sql.upsert_player(cur, p)
                        summary = sync_team_roster(cur, team_id, season, players)

                logger.info(
                    "Team %s (%s) committed: +%d -%d ~%d =%d",
                    team_id, team_name,
                    summary["added"], summary["dropped"],
                    summary["updated"], summary["unchanged"],
                )
                totals["teams_ok"] += 1
                for k in ("added", "dropped", "updated", "unchanged"):
                    totals[k] += summary[k]

            except Exception:
                logger.exception(
                    "DB error for team %s (%s) — rolled back, continuing",
                    team_id, team_name,
                )
                totals["teams_failed"] += 1

        logger.info(
            "roster_sync complete: %d teams ok, %d failed | "
            "+%d added, -%d dropped, ~%d updated, =%d unchanged",
            totals["teams_ok"], totals["teams_failed"],
            totals["added"], totals["dropped"],
            totals["updated"], totals["unchanged"],
        )
        return totals

    finally:
        conn.close()
