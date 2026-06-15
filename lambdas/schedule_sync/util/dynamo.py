import boto3
import logging
import os

from datetime import datetime
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ddb = boto3.client("dynamodb", region_name=os.environ["AWS_REGION"])
serializer = TypeSerializer()
deserializer = TypeDeserializer()


def get_games_map(date: datetime) -> dict[int, dict]:
    resp = ddb.query(
        TableName=os.environ["DDB_TABLE"],
        KeyConditionExpression="game_date = :date",
        ExpressionAttributeValues={
            ":date": {"S": date.strftime("%Y-%m-%d")},
        },
    )
    games_list = [_deserialize(game) for game in resp.get("Items", [])]
    return {
        int(game["game_id"]):game
        for game in games_list
    }

def insert_game(game: dict):
    game_item = {
        "game_date": game["game_date"],
        "game_datetime_id": "#".join((game["game_datetime"], str(game["game_id"]))),
        "game_datetime": game["game_datetime"],
        "game_id": game["game_id"],
        "game_type": game["game_type"],
        "status": game["status"],
        "away_name": game["away_name"],
        "home_name": game["home_name"], 
        "away_id": game["away_id"],
        "home_id": game["home_id"],
        "home_probable_pitcher": game["home_probable_pitcher"],
        "away_probable_pitcher": game["away_probable_pitcher"],
        "home_pitcher_note": game["home_pitcher_note"],
        "away_pitcher_note": game["away_pitcher_note"],
        "venue_name": game["venue_name"]
    }

    game_item_serialized = {
        k:serializer.serialize(v)
        for k,v in game_item.items()
    }

    ddb.put_item(
        TableName=os.environ["DDB_TABLE"],
        Item=game_item_serialized
    )

def update_game(game: dict):
    game_key = {
        "game_date": serializer.serialize(game["game_date"]),
        "game_datetime_id": serializer.serialize(
            "#".join((game["game_datetime"], str(game["game_id"])))
        )
    }
    game_item = {
        "game_datetime": game["game_datetime"],
        "status": game["status"],
        "home_probable_pitcher": game["home_probable_pitcher"],
        "away_probable_pitcher": game["away_probable_pitcher"],
        "home_pitcher_note": game["home_pitcher_note"],
        "away_pitcher_note": game["away_pitcher_note"]
    }

    game_item_serialized = {
        k: serializer.serialize(v)
        for k, v in game_item.items()
    }

    ddb.update_item(
        TableName=os.environ["DDB_TABLE"],
        Key=game_key,
        UpdateExpression="SET " + ", ".join(f"#n_{k} = :v_{k}" for k in game_item_serialized),
        ExpressionAttributeNames={f"#n_{k}": k for k in game_item_serialized},
        ExpressionAttributeValues={f":v_{k}": v for k, v in game_item_serialized.items()},
    )


def _deserialize(item: dict):
    return {
        k:deserializer.deserialize(v)
        for k,v in item.items()
    }