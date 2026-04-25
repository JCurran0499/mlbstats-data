import logging
import statsapi

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def fetch_rosters():
    teams = statsapi.get("teams", {"sportId": 1})["teams"]

    result = []
    for team in teams:
        team_id = team["id"]
        team_name = team["name"]
        try:
            roster = statsapi.get("team_roster", {"teamId": team_id, "rosterType": "active"})["roster"]
            players = [
                {
                    "player_id": entry["person"]["id"],
                    "name": entry["person"]["fullName"],
                    "position": entry["position"]["abbreviation"],
                }
                for entry in roster
            ]
        except Exception:
            logger.exception("Failed to fetch roster for team %s (%s)", team_id, team_name)
            players = []

        result.append({"team_id": team_id, "team_name": team_name, "roster": players})

    return result


def lambda_handler(event, context):
    rosters = fetch_rosters()
    return rosters

if __name__ == "__main__":
    print(lambda_handler(None, None))