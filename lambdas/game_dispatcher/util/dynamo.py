import boto3
import logging
import os

from datetime import datetime
from boto3.dynamodb.types import TypeDeserializer

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ddb = boto3.client("dynamodb", region_name=os.environ["AWS_REGION"])
deserializer = TypeDeserializer()


def get_todays_games(date: datetime) -> list[dict]:
    """Return every game stored for `date` in the mlb-schedule table."""
    resp = ddb.query(
        TableName=os.environ["DDB_TABLE"],
        KeyConditionExpression="game_date = :date",
        ExpressionAttributeValues={
            ":date": {"S": date.strftime("%Y-%m-%d")},
        },
    )
    return [_deserialize(game) for game in resp.get("Items", [])]


def _deserialize(item: dict) -> dict:
    return {
        k: deserializer.deserialize(v)
        for k, v in item.items()
    }
