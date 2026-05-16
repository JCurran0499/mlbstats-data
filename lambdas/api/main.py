from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from adapter import db
import psycopg2

logger = Logger()
app = APIGatewayHttpResolver()

db_string = db.get_connection_string()
conn = psycopg2.connect(db_string)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/teams")
def get_teams():
    return {"teams": db.get_teams(conn)}


@app.get("/players/{player_id}/info")
def get_player_info(player_id: int):
    return {"player_id": player_id}


@logger.inject_lambda_context
def handler(event, context) -> dict:
    return app.resolve(event, context)
