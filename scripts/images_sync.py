import boto3
import requests
import sys
import psycopg2
import util

IMAGES_BUCKET = "mlbstats-images"

db_string = util.get_secret("database_string")
cloudfront_url = util.get_secret("cloudfront_url")

conn = psycopg2.connect(db_string)
s3 = boto3.client("s3")

def get_teams():
    with conn.cursor() as cur:
        cur.execute("SELECT team_id FROM teams")
        return [r[0] for r in cur.fetchall()]
    
def get_players(team_id: int):
    with conn.cursor() as cur:
        cur.execute("SELECT player_id FROM rosters WHERE team_id = %s AND active = True", (team_id,))
        return [r[0] for r in cur.fetchall()]
    
# endpoint: https://midfield.mlbstatic.com/v1/team/{TEAM_ID}/spots/500
def sync_team_logo(cur: psycopg2.extensions.cursor, team_id: int):
    url = f"https://midfield.mlbstatic.com/v1/team/{team_id}/spots/500"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    key = f"teams/{team_id}.png"
    s3.put_object(Bucket=IMAGES_BUCKET, Key=key, Body=response.content, ContentType="image/png")
    print(f"team {team_id}: uploaded logo to s3://{IMAGES_BUCKET}/{key}")

    cur.execute("UPDATE teams SET logo_url = %s WHERE team_id = %s", (f"https://{cloudfront_url}/{key}", team_id))
    print(f"team {team_id}: updated logo_url in database")

# endpoint: https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/{PLAYER_ID}/headshot/67/current
def sync_player_headshot(cur: psycopg2.extensions.cursor, player_id: int):
    url = f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/{player_id}/headshot/67/current"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    key = f"players/{player_id}.jpg"
    s3.put_object(Bucket=IMAGES_BUCKET, Key=key, Body=response.content, ContentType="image/jpeg")
    print(f"player {player_id}: uploaded headshot to s3://{IMAGES_BUCKET}/{key}")

    cur.execute("UPDATE players SET headshot_url = %s WHERE player_id = %s", (f"https://{cloudfront_url}/{key}", player_id))
    print(f"player {player_id}: updated headshot_url in database")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python images_sync.py [teams|players]")
        sys.exit(1)

    teams = get_teams()
    for team_id in teams:
        with conn:
            with conn.cursor() as cur:
                if sys.argv[1] == "teams":
                    try:
                        sync_team_logo(cur, team_id)
                    except Exception as e:
                        print(f"team {team_id}: error syncing logo — {e}")
                
                if sys.argv[1] == "players":
                    player_ids = get_players(team_id)
                    for player_id in player_ids:
                        try:
                            sync_player_headshot(cur, player_id)
                        except Exception as e:
                            print(f"player {player_id}: error syncing headshot — {e}")