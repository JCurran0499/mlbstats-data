import logging
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def fetch_teams(cur: psycopg2.extensions.cursor):
    cur.execute("""
        SELECT team_id, name
        FROM teams
        WHERE active = TRUE
    """)
    return [{"id": row[0], "name": row[1]} for row in cur.fetchall()]


def fetch_active_players(cur: psycopg2.extensions.cursor, team_id: int, season_year: int):
    cur.execute("""
        SELECT player_id
        FROM rosters
        WHERE team_id = %s AND season_year = %s AND active = TRUE
    """, (team_id, season_year))
    return [row[0] for row in cur.fetchall()]


def upsert_batting_stats(cur: psycopg2.extensions.cursor, stats: dict):
    cur.execute("""
        INSERT INTO batting_stats (
            player_id, team_id, season_year, games_played, plate_appearances, at_bats,
            runs, hits, doubles, triples, home_runs, rbi, stolen_bases,
            caught_stealing, walks, intentional_walks, strikeouts,
            hit_by_pitch, sac_flies, batting_avg, on_base_pct, slugging_pct,
            ops, woba, wrc_plus, babip, iso
        ) VALUES (
            %(player_id)s, %(team_id)s, %(season_year)s, %(games_played)s,
            %(plate_appearances)s, %(at_bats)s, %(runs)s, %(hits)s,
            %(doubles)s, %(triples)s, %(home_runs)s, %(rbi)s,
            %(stolen_bases)s, %(caught_stealing)s, %(walks)s,
            %(intentional_walks)s, %(strikeouts)s,
            %(hit_by_pitch)s, %(sac_flies)s, %(batting_avg)s, %(on_base_pct)s,
            %(slugging_pct)s, %(ops)s, %(woba)s, %(wrc_plus)s, %(babip)s, %(iso)s
        )
        ON CONFLICT (player_id, season_year) DO UPDATE SET
            team_id = EXCLUDED.team_id,
            games_played = EXCLUDED.games_played,
            plate_appearances = EXCLUDED.plate_appearances,
            at_bats = EXCLUDED.at_bats,
            runs = EXCLUDED.runs,
            hits = EXCLUDED.hits,
            doubles = EXCLUDED.doubles,
            triples = EXCLUDED.triples,
            home_runs = EXCLUDED.home_runs,
            rbi = EXCLUDED.rbi,
            stolen_bases = EXCLUDED.stolen_bases,
            caught_stealing = EXCLUDED.caught_stealing,
            walks = EXCLUDED.walks,
            intentional_walks = EXCLUDED.intentional_walks,
            strikeouts = EXCLUDED.strikeouts,
            hit_by_pitch = EXCLUDED.hit_by_pitch,
            sac_flies = EXCLUDED.sac_flies,
            batting_avg = EXCLUDED.batting_avg,
            on_base_pct = EXCLUDED.on_base_pct,
            slugging_pct = EXCLUDED.slugging_pct,
            ops = EXCLUDED.ops,
            woba = EXCLUDED.woba,
            wrc_plus = EXCLUDED.wrc_plus,
            babip = EXCLUDED.babip,
            iso = EXCLUDED.iso
    """, stats)


def upsert_pitching_stats(cur: psycopg2.extensions.cursor, stats: dict):
    cur.execute("""
        INSERT INTO pitching_stats (
            player_id, team_id, season_year, games_pitched, games_started,
            complete_games, shutouts, wins, losses, saves, holds, blown_saves,
            innings_pitched, hits_allowed, runs_allowed, earned_runs,
            home_runs_allowed, walks, intentional_walks, strikeouts,
            hit_batters, wild_pitches, era, whip, k_per_9, bb_per_9,
            hr_per_9, k_pct, bb_pct, fip, xfip, war
        ) VALUES (
            %(player_id)s, %(team_id)s, %(season_year)s, %(games_pitched)s, %(games_started)s,
            %(complete_games)s, %(shutouts)s, %(wins)s, %(losses)s, %(saves)s, %(holds)s, %(blown_saves)s,
            %(innings_pitched)s, %(hits_allowed)s, %(runs_allowed)s, %(earned_runs)s,
            %(home_runs_allowed)s, %(walks)s, %(intentional_walks)s, %(strikeouts)s,
            %(hit_batters)s, %(wild_pitches)s, %(era)s, %(whip)s, %(k_per_9)s, %(bb_per_9)s,
            %(hr_per_9)s, %(k_pct)s, %(bb_pct)s, %(fip)s, %(xfip)s, %(war)s
        )
        ON CONFLICT (player_id, season_year) DO UPDATE SET
            team_id = EXCLUDED.team_id,
            games_pitched = EXCLUDED.games_pitched,
            games_started = EXCLUDED.games_started,
            complete_games = EXCLUDED.complete_games,
            shutouts = EXCLUDED.shutouts,
            wins = EXCLUDED.wins,
            losses = EXCLUDED.losses,
            saves = EXCLUDED.saves,
            holds = EXCLUDED.holds,
            blown_saves = EXCLUDED.blown_saves,
            innings_pitched = EXCLUDED.innings_pitched,
            hits_allowed = EXCLUDED.hits_allowed,
            runs_allowed = EXCLUDED.runs_allowed,
            earned_runs = EXCLUDED.earned_runs,
            home_runs_allowed = EXCLUDED.home_runs_allowed,
            walks = EXCLUDED.walks,
            intentional_walks = EXCLUDED.intentional_walks,
            strikeouts = EXCLUDED.strikeouts,
            hit_batters = EXCLUDED.hit_batters,
            wild_pitches = EXCLUDED.wild_pitches,
            era = EXCLUDED.era,
            whip = EXCLUDED.whip,
            k_per_9 = EXCLUDED.k_per_9,
            bb_per_9 = EXCLUDED.bb_per_9,
            hr_per_9 = EXCLUDED.hr_per_9,
            k_pct = EXCLUDED.k_pct,
            bb_pct = EXCLUDED.bb_pct,
            fip = EXCLUDED.fip,
            xfip = EXCLUDED.xfip,
            war = EXCLUDED.war
    """, stats)


def upsert_fielding_stats(cur: psycopg2.extensions.cursor, stats: dict):
    cur.execute("""
        INSERT INTO fielding_stats (
            player_id, team_id, season_year, position, games,
            innings, putouts, assists, errors, double_plays,
            fielding_pct, drs, uzr
        ) VALUES (
            %(player_id)s, %(team_id)s, %(season_year)s, %(position)s, %(games)s,
            %(innings)s, %(putouts)s, %(assists)s, %(errors)s, %(double_plays)s,
            %(fielding_pct)s, %(drs)s, %(uzr)s
        )
        ON CONFLICT (player_id, season_year, position) DO UPDATE SET
            team_id = EXCLUDED.team_id,
            games = EXCLUDED.games,
            innings = EXCLUDED.innings,
            putouts = EXCLUDED.putouts,
            assists = EXCLUDED.assists,
            errors = EXCLUDED.errors,
            double_plays = EXCLUDED.double_plays,
            fielding_pct = EXCLUDED.fielding_pct,
            drs = EXCLUDED.drs,
            uzr = EXCLUDED.uzr
    """, stats)