import re
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

_league_abbreviations = {
    "American League": "AL",
    "National League": "NL",
}

_division_abbreviations = {
    "American League East": "AL East",
    "American League Central": "AL Central",
    "American League West": "AL West",
    "National League East": "NL East",
    "National League Central": "NL Central",
    "National League West": "NL West",
}


def parse_height(height_str: str):
    if not height_str:
        return None
    m = re.match(r"(\d+)'\s*(\d+)\"", height_str.strip())
    if not m:
        logger.warning("Unrecognized height format: %r", height_str)
        return None
    return int(m.group(1)) * 12 + int(m.group(2))


def parse_roster_entry(entry: dict, team_id: int):
    person: dict = entry.get("person", {})
    pos: dict    = entry.get("position", {})
    status: dict = entry.get("status", {})

    if "code" not in status:
        logger.error("Missing status code for player_id=%s", person.get("id"))

    return {
        "player_id":            person["id"],
        "first_name":           person.get("firstName", ""),
        "last_name":            person.get("lastName", ""),
        "full_name":            person.get("fullName", ""),
        "nickname":             person.get("nickName") or None,
        "team_id":              team_id,
        "primary_number":       person.get("primaryNumber") or None,
        "birth_date":           person.get("birthDate") or None,
        "birth_country":        person.get("birthCountry") or None,
        "birth_city":           person.get("birthCity") or None,
        "birth_state_province": person.get("birthStateProvince") or None,
        "primary_position":     pos.get("abbreviation") or None,
        "bats":                 person.get("batSide", {}).get("code") or None,
        "throws":               person.get("pitchHand", {}).get("code") or None,
        "height_inches":        parse_height(person.get("height")),
        "weight_lbs":           person.get("weight") or None,
        "debut_date":           person.get("mlbDebutDate") or None,
        "active":               person.get("active", False),
        "status_code":          status["code"]
    }

def parse_team(team: dict):
    league_name   = team.get("league", {}).get("name", "")
    division_name = team.get("division", {}).get("name", "")

    if league_name not in _league_abbreviations:
        logger.error("Unrecognized league name %r for team_id=%s", league_name, team.get("id"))
    if division_name not in _division_abbreviations:
        logger.error("Unrecognized division name %r for team_id=%s", division_name, team.get("id"))
    if "abbreviation" not in team:
        logger.error("Missing abbreviation for team_id=%s", team.get("id"))

    return {
        "team_id":      team["id"],
        "name":         team["name"],
        "abbreviation": team["abbreviation"],
        "city":         team.get("locationName", ""),
        "league":       _league_abbreviations[league_name],
        "division":     _division_abbreviations[division_name],
        "venue_name":   team.get("venue", {}).get("name"),
        "debut_year":   team.get("firstYearOfPlay"),
        "active":       team.get("active", False)
    }