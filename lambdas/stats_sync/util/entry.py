import logging
from decimal import Decimal, InvalidOperation

logger = logging.getLogger()

HITTING = "hitting"
PITCHING = "pitching"
FIELDING = "fielding"


def _dec(val) -> Decimal | None:
    if val is None:
        return None
    try:
        return Decimal(str(val))
    except InvalidOperation:
        logger.warning("Could not parse decimal value: %r", val)
        return None


def _find_stat_groups(player_data: list, group: str) -> list[dict] | None:
    stat_groups = []
    for stat_group in player_data:
        if stat_group.get("group") == group:
            stat_groups.append(stat_group.get("stats", {}))
        
    return stat_groups


def parse_batting_stats(player_data: dict, player_id: int, team_id: int, season: int) -> dict | None:
    batting_stats = _find_stat_groups(player_data, HITTING)
    if not batting_stats:
        return None
    
    stats = batting_stats[0]

    slg = _dec(stats.get("slg"))
    avg = _dec(stats.get("avg"))

    return {
        "player_id":         player_id,
        "team_id":           team_id,
        "season_year":       season,
        "games_played":      stats.get("gamesPlayed"),
        "plate_appearances": stats.get("plateAppearances"),
        "at_bats":           stats.get("atBats"),
        "runs":              stats.get("runs"),
        "hits":              stats.get("hits"),
        "doubles":           stats.get("doubles"),
        "triples":           stats.get("triples"),
        "home_runs":         stats.get("homeRuns"),
        "rbi":               stats.get("rbi"),
        "stolen_bases":      stats.get("stolenBases"),
        "caught_stealing":   stats.get("caughtStealing"),
        "walks":             stats.get("baseOnBalls"),
        "intentional_walks": stats.get("intentionalWalks"),
        "strikeouts":        stats.get("strikeOuts"),
        "hit_by_pitch":      stats.get("hitByPitch"),
        "sac_flies":         stats.get("sacFlies"),
        "batting_avg":       avg,
        "on_base_pct":       _dec(stats.get("obp")),
        "slugging_pct":      slg,
        "ops":               _dec(stats.get("ops")),
        "woba":              None,
        "wrc_plus":          None,
        "babip":             _dec(stats.get("babip")),
        "iso":               (slg - avg) if (slg is not None and avg is not None) else None,
    }


def parse_pitching_stats(player_data: dict, player_id: int, team_id: int, season: int) -> dict | None:
    pitching_stats = _find_stat_groups(player_data, PITCHING)
    if not pitching_stats:
        return None
    
    stats = pitching_stats[0]

    return {
        "player_id":         player_id,
        "team_id":           team_id,
        "season_year":       season,
        "games_pitched":     stats.get("gamesPlayed"),
        "games_started":     stats.get("gamesStarted"),
        "complete_games":    stats.get("completeGames"),
        "shutouts":          stats.get("shutouts"),
        "wins":              stats.get("wins"),
        "losses":            stats.get("losses"),
        "saves":             stats.get("saves"),
        "holds":             stats.get("holds"),
        "blown_saves":       stats.get("blownSaves"),
        "innings_pitched":   _dec(stats.get("inningsPitched")),
        "hits_allowed":      stats.get("hits"),
        "runs_allowed":      stats.get("runs"),
        "earned_runs":       stats.get("earnedRuns"),
        "home_runs_allowed": stats.get("homeRuns"),
        "walks":             stats.get("baseOnBalls"),
        "intentional_walks": stats.get("intentionalWalks"),
        "strikeouts":        stats.get("strikeOuts"),
        "hit_batters":       stats.get("hitByPitch"),
        "wild_pitches":      stats.get("wildPitches"),
        "era":               _dec(stats.get("era")),
        "whip":              _dec(stats.get("whip")),
        "k_per_9":           _dec(stats.get("strikeoutsPer9Inn")),
        "bb_per_9":          _dec(stats.get("walksPer9Inn")),
        "hr_per_9":          _dec(stats.get("homeRunsPer9")),
        "k_pct":             None,
        "bb_pct":            None,
        "fip":               None,
        "xfip":              None,
        "war":               None,
    }


def parse_fielding_stats(player_data: dict, player_id: int, team_id: int, season: int) -> list[dict]:
    fielding_stats = _find_stat_groups(player_data, FIELDING)
    if not fielding_stats:
        return None
    
    results = []
    for stats in fielding_stats:
        position = stats.get("position", {}).get("abbreviation")
        if not position:
            logger.warning("Missing position for fielding stats of player_id=%s, team_id=%s, season=%s", player_id, team_id, season)
            continue

        results.append({
            "player_id":    player_id,
            "team_id":      team_id,
            "season_year":  season,
            "position":     position,
            "games":        stats.get("gamesPlayed"),
            "innings":      _dec(stats.get("innings")),
            "putouts":      stats.get("putOuts"),
            "assists":      stats.get("assists"),
            "errors":       stats.get("errors"),
            "double_plays": stats.get("doublePlays"),
            "fielding_pct": _dec(stats.get("fielding")),
            "drs":          None,
            "uzr":          None,
        })

    return results
