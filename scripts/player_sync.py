import sys
import statsapi
import psycopg2
import util

# Columns in `players` that can be filled/updated via this script.
# Explicitly listed to guard against SQL injection when building dynamic UPDATE queries.
STATS = {
    "full_name": "fullName",
    "nickname": "nickName",
    "team_id": "currentTeam.id",
    "primary_number": "primaryNumber",
    "birth_date": "birthDate",
    "birth_country": "birthCountry",
    "birth_city": "birthCity",
    "birth_state_province": "birthStateProvince",
    "primary_position": "primaryPosition.abbreviation",
    "bats": "batSide.code",
    "throws": "pitchHand.code"
}

db_string = util.get_secret("database_string")
conn = psycopg2.connect(db_string)


def fill_player_stat(cur: psycopg2.extensions.cursor, player_id: int, stat: str):
    if stat not in STATS:
        raise ValueError(f"Unknown or non-fillable column: {stat!r}")

    stat_location = STATS[stat]
    response = statsapi.get("people", {"personIds": player_id})["people"][0]
    value = util.get_stat(response, stat_location)

    if isinstance(value, str) and value.startswith("Error"):
        print(f"player {player_id}: could not extract {stat_location!r} — {value}")
        return False

    cur.execute(
        f"UPDATE players SET {stat} = %s WHERE player_id = %s",
        (value, player_id),
    )
    return True


def fill_missing(stat: str):
    """Query every player where stat_name IS NULL and fill it from the MLB Stats API."""
    if stat not in STATS:
        raise ValueError(f"Unknown or non-fillable column: {stat!r}")

    with conn.cursor() as cur:
        cur.execute(
            f"SELECT player_id FROM players WHERE {stat} IS NULL"
        )
        rows = cur.fetchall()

    if not rows:
        print(f"No players missing {stat!r}.")
        return

    player_ids = [r[0] for r in rows]
    print(f"Found {len(player_ids)} player(s) missing {stat!r}. Filling...")

    updated = skipped = 0
    for idx, player_id in enumerate(player_ids):
        try:
            with conn:
                with conn.cursor() as cur:
                    ok = fill_player_stat(cur, player_id, stat)
            if ok:
                updated += 1
                print(f"{idx+1}/{len(player_ids)} player {player_id}: updated {stat!r}")
            else:
                skipped += 1
        except Exception as e:
            print(f"  player {player_id}: error — {e}")
            skipped += 1

    print(f"Done. updated={updated}, skipped={skipped}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python player_sync.py <stat_name> <stat_location>")
        print("  stat_name     — players table column (e.g. birth_country)")
        print("  stat_location — dot-path into the API response (e.g. people.0.birthCountry)")
        sys.exit(1)

    fill_missing(sys.argv[1])
    conn.close()
