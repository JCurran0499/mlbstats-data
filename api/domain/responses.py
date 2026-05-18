from pydantic import BaseModel, Field

class Team(BaseModel):
    id: int = Field(alias="team_id")
    name: str
    abbreviation: str
    league: str
    division: str
    logo: str = Field(alias="logo_url")

class Teams(BaseModel):
    teams: list[Team]
