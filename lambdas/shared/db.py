import psycopg2
import logging
from pydantic import BaseModel, Field
from typing import Optional

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def start_connection(connection_string: str) -> psycopg2.extensions.connection:
    logger.info("Starting Neon database connection...")
    return psycopg2.connect(connection_string)


class Team(BaseModel):
    team_id: int
    name: str
    abbreviation: str
    city: str
    league: str
    division: str
    venue_name: Optional[str]
    debut_year: Optional[str]
    logo_url: Optional[str]

class Player(BaseModel):
    player_id: int
    first_name: str
    last_name: str
    full_name: Optional[str]
    nickname: Optional[str]
    team_id: Optional[int]
    primary_number: Optional[str]
    birth_date: Optional[str]
    birth_country: Optional[str]
    birth_city: Optional[str]
    birth_state_province: Optional[str]
    primary_position: Optional[str]
    bats: Optional[str]
    throws: Optional[str]
    height_inches: Optional[int]
    weight_lbs: Optional[int]
    debut_date: Optional[str]
    status_code: Optional[str]
    headshot_url: Optional[str]
