from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from adapter import db

logger = Logger()
app = APIGatewayHttpResolver()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/teams")
def get_teams():
    return {"teams": db.get_teams()}


@logger.inject_lambda_context
def handler(event, context) -> dict:
    return app.resolve(event, context)
