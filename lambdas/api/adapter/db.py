import os
import boto3
import psycopg2
import logging

logger = logging.getLogger()


def _get_connection_string() -> str:
    client = boto3.client("ssm", region_name=os.environ["AWS_REGION"])
    response = client.get_parameter(
        Name=os.environ["DB_CONNECTION_PARAMETER"], WithDecryption=True
    )
    return response["Parameter"]["Value"]


_conn = psycopg2.connect(_get_connection_string())


def get_teams() -> list[dict]:
    with _conn.cursor() as cur:
        cur.execute(
            "SELECT team_id, name, abbreviation, city, league, division,"
            " venue_name, debut_year, active FROM teams ORDER BY name"
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
