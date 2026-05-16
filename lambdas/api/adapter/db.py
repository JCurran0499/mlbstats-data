import os
import boto3
import psycopg2
import logging

logger = logging.getLogger()


def get_connection_string() -> str:
    client = boto3.client("ssm", region_name=os.environ["AWS_REGION"])
    response = client.get_parameter(
        Name=os.environ["DB_CONNECTION_PARAMETER"], WithDecryption=True
    )
    return response["Parameter"]["Value"]


def get_teams(conn: psycopg2.extensions.connection) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT team_id, name, abbreviation, city, league, division,"
            " venue_name, debut_year, active FROM teams ORDER BY name"
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_player_info(conn: psycopg2.extensions.connection, player_id: int) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM players WHERE player_id = %s",
            (player_id,)
        )
        row = cur.fetchone()
        if row:
            cols = [desc[0] for desc in cur.description]
            return dict(zip(cols, row))
        else:
            logger.warning(f"Player with id {player_id} not found")
            return {}