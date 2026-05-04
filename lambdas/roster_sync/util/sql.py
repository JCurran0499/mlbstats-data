import logging
import psycopg2

logger = logging.getLogger()


def fetch_active_roster(cur: psycopg2.extensions.cursor, team_id: int, season_year: int):
    cur.execute("""
        SELECT player_id, roster_status
        FROM rosters
        WHERE team_id = %s AND season_year = %s AND active = TRUE
    """, (team_id, season_year))
    return {row[0]: row[1] for row in cur.fetchall()}


def insert_roster_entry(cur: psycopg2.extensions.cursor, player_id: int, team_id: int, season_year: int, roster_status: str):
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


def update_roster_entry(cur: psycopg2.extensions.cursor, player_id: int, team_id: int, season_year: int, roster_status: str):
    cur.execute("""
        UPDATE rosters
        SET roster_status = %s
        WHERE player_id = %s AND team_id = %s AND season_year = %s AND active = TRUE
    """, (roster_status, player_id, team_id, season_year))


def upsert_team(cur: psycopg2.extensions.cursor, team: dict):
    cur.execute("""
        INSERT INTO teams (team_id, name, abbreviation, city, league, division, venue_name, debut_year, active)
        VALUES (%(team_id)s, %(name)s, %(abbreviation)s, %(city)s, %(league)s, %(division)s, %(venue_name)s, %(debut_year)s, %(active)s)
        ON CONFLICT (team_id) DO UPDATE SET
            name         = EXCLUDED.name,
            abbreviation = EXCLUDED.abbreviation,
            city         = EXCLUDED.city,
            league       = EXCLUDED.league,
            division     = EXCLUDED.division,
            venue_name   = EXCLUDED.venue_name,
            debut_year   = EXCLUDED.debut_year,
            active       = EXCLUDED.active
    """, team)


def upsert_player(cur: psycopg2.extensions.cursor, player: dict):
    cur.execute("""
        INSERT INTO players (
            player_id, first_name, last_name, nickname, team_id,
            primary_number, birth_date, birth_country, birth_city,
            birth_state_province, primary_position, bats, throws, height_inches,
            weight_lbs, debut_date, active, status_code
        )
        VALUES (
            %(player_id)s, %(first_name)s, %(last_name)s, %(nickname)s, %(team_id)s,
            %(primary_number)s, %(birth_date)s, %(birth_country)s, %(birth_city)s,
            %(birth_state_province)s, %(primary_position)s, %(bats)s, %(throws)s, %(height_inches)s, %(weight_lbs)s,
            %(debut_date)s, %(active)s, %(status_code)s
        )
        ON CONFLICT (player_id) DO UPDATE SET
            first_name              = EXCLUDED.first_name,
            last_name               = EXCLUDED.last_name,
            nickname                = EXCLUDED.nickname,
            team_id                 = EXCLUDED.team_id,
            primary_number          = EXCLUDED.primary_number,
            birth_date              = EXCLUDED.birth_date,
            birth_country           = EXCLUDED.birth_country,
            birth_city              = EXCLUDED.birth_city,
            birth_state_province    = EXCLUDED.birth_state_province,
            primary_position        = EXCLUDED.primary_position,
            bats                    = EXCLUDED.bats,
            throws                  = EXCLUDED.throws,
            height_inches           = EXCLUDED.height_inches,
            weight_lbs              = EXCLUDED.weight_lbs,
            debut_date              = EXCLUDED.debut_date,
            active                  = EXCLUDED.active,
            status_code             = EXCLUDED.status_code
    """, player)
