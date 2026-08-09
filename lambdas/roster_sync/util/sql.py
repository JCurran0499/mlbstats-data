import psycopg2
from shared.db import Team, Player

def fetch_active_roster(cur: psycopg2.extensions.cursor, team_id: int, season_year: int):
    cur.execute("""
        SELECT player_id, roster_status
        FROM rosters
        WHERE team_id = %s AND season_year = %s AND active = TRUE
    """, (team_id, season_year))
    return {row[0]: row[1] for row in cur.fetchall()}


def insert_roster_entry(cur: psycopg2.extensions.cursor, player_id: int, team_id: int, season_year: int, roster_status: str | None):
    cur.execute("""
        INSERT INTO rosters (player_id, team_id, season_year, roster_status)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (player_id, team_id, season_year)
        DO UPDATE SET roster_status = EXCLUDED.roster_status, active = TRUE
    """, (player_id, team_id, season_year, roster_status))


def close_roster_entry(cur: psycopg2.extensions.cursor, player_id: int, team_id: int, season_year: int):
    cur.execute("""
        UPDATE rosters
        SET active = FALSE
        WHERE player_id = %s AND team_id = %s AND season_year = %s AND active = TRUE
    """, (player_id, team_id, season_year))


def update_roster_entry(cur: psycopg2.extensions.cursor, player_id: int, team_id: int, season_year: int, roster_status: str | None):
    cur.execute("""
        UPDATE rosters
        SET roster_status = %s
        WHERE player_id = %s AND team_id = %s AND season_year = %s AND active = TRUE
    """, (roster_status, player_id, team_id, season_year))


def upsert_team(cur: psycopg2.extensions.cursor, team: Team):
    cols = list(Team.model_fields.keys())
    cur.execute(f"""
        INSERT INTO teams ({", ".join(cols)})
        VALUES ({", ".join(f"%({c})s" for c in cols)})
        ON CONFLICT (team_id) 
        DO UPDATE SET {", ".join(f"{c} = EXCLUDED.{c}" for c in cols if c != "team_id")}
    """, team.model_dump())


def upsert_player(cur: psycopg2.extensions.cursor, player: Player):
    cols = list(Player.model_fields.keys())
    cur.execute(f"""
        INSERT INTO players ({", ".join(cols)})
        VALUES ({", ".join(f"%({c})s" for c in cols)})
        ON CONFLICT (player_id) 
        DO UPDATE SET {", ".join(f"{c} = EXCLUDED.{c}" for c in cols if c != "player_id")}
    """, player.model_dump())
