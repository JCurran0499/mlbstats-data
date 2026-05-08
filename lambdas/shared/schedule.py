import logging
import statsapi
from datetime import datetime, date
from zoneinfo import ZoneInfo

logger = logging.getLogger()

_ET = ZoneInfo("America/New_York")

def validate_in_season() -> bool:
    today = datetime.now(_ET).date()
    season = today.year

    logger.info("Fetching MLB schedule for season %s from Stats API", season)
    schedule = statsapi.get("seasons", {"sportId": 1, "season": season})
    season_schedule = schedule["seasons"]

    if not season_schedule:
        logger.warning("No season data returned for season %s", season)
        return False
    
    season_info = season_schedule[0]
    season_start = date.fromisoformat(season_info["seasonStartDate"])
    season_end = date.fromisoformat(season_info["seasonEndDate"])
    
    if today < season_start or today > season_end:
        logger.warning(
            "Skipping roster_sync: today (%s) is outside season window (%s – %s)",
            today, season_start, season_end,
        )
        return False
    
    return True
