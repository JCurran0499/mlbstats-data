# RDS (PostgreSQL) Schema

All IDs sourced from the MLB Stats API unless noted. Timestamps are UTC.

---

## `teams`

| Column | Type | Notes |
|---|---|---|
| `team_id` | INTEGER PK | MLB Stats API team ID |
| `name` | VARCHAR(100) | Full team name |
| `abbreviation` | CHAR(3) | e.g. NYY, BOS |
| `city` | VARCHAR(100) | |
| `league` | CHAR(2) | AL or NL |
| `division` | VARCHAR(20) | East, Central, West |
| `venue_name` | VARCHAR(100) | Home ballpark |
| `active` | BOOLEAN | |

---

## `players`

| Column | Type | Notes |
|---|---|---|
| `player_id` | INTEGER PK | MLB Stats API player ID |
| `first_name` | VARCHAR(100) | |
| `last_name` | VARCHAR(100) | |
| `birth_date` | DATE | |
| `birth_country` | VARCHAR(100) | |
| `primary_position` | CHAR(2) | P, C, 1B, 2B, SS, 3B, LF, CF, RF, DH |
| `bats` | CHAR(1) | L, R, S |
| `throws` | CHAR(1) | L, R |
| `height_inches` | SMALLINT | |
| `weight_lbs` | SMALLINT | |
| `debut_date` | DATE | |
| `active` | BOOLEAN | |

---

## `seasons`

| Column | Type | Notes |
|---|---|---|
| `season_year` | SMALLINT PK | e.g. 2026 |
| `regular_season_start` | DATE | |
| `regular_season_end` | DATE | |
| `postseason_start` | DATE | Nullable |

---

## `rosters`

Tracks which team a player belongs to, including mid-season trades.

| Column | Type | Notes |
|---|---|---|
| `roster_id` | SERIAL PK | |
| `player_id` | INTEGER FK → players | |
| `team_id` | INTEGER FK → teams | |
| `season_year` | SMALLINT FK → seasons | |
| `roster_status` | VARCHAR(30) | active, IL_10, IL_60, minors, etc. |
| `start_date` | DATE | Date this assignment began |
| `end_date` | DATE | NULL = current assignment |

Index: `(player_id, season_year)`, `(team_id, season_year)`

---

## `games`

| Column | Type | Notes |
|---|---|---|
| `game_id` | INTEGER PK | MLB Stats API game (gamePk) |
| `season_year` | SMALLINT FK → seasons | |
| `game_date` | DATE | |
| `game_type` | CHAR(1) | R=regular, P=postseason, S=spring, A=all-star |
| `series_description` | VARCHAR(50) | e.g. "World Series", NULL for regular season |
| `home_team_id` | INTEGER FK → teams | |
| `away_team_id` | INTEGER FK → teams | |
| `venue_name` | VARCHAR(100) | |
| `status` | VARCHAR(20) | scheduled, live, final, postponed, cancelled |
| `home_score` | SMALLINT | NULL until game starts |
| `away_score` | SMALLINT | NULL until game starts |
| `innings_played` | SMALLINT | Final inning count |
| `winning_team_id` | INTEGER FK → teams | NULL until final |
| `losing_team_id` | INTEGER FK → teams | NULL until final |
| `game_duration_minutes` | SMALLINT | NULL until final |
| `attendance` | INTEGER | |
| `updated_at` | TIMESTAMPTZ | |

Index: `(game_date)`, `(home_team_id, season_year)`, `(away_team_id, season_year)`, `(status)`

---

## `batting_stats`

Covers both game-level stats and season aggregates. `game_id IS NULL` → season aggregate.

| Column | Type | Notes |
|---|---|---|
| `stat_id` | SERIAL PK | |
| `player_id` | INTEGER FK → players | |
| `team_id` | INTEGER FK → teams | |
| `season_year` | SMALLINT FK → seasons | |
| `game_id` | INTEGER FK → games | NULL = season aggregate |
| `games_played` | SMALLINT | |
| `plate_appearances` | SMALLINT | |
| `at_bats` | SMALLINT | |
| `runs` | SMALLINT | |
| `hits` | SMALLINT | |
| `doubles` | SMALLINT | |
| `triples` | SMALLINT | |
| `home_runs` | SMALLINT | |
| `rbi` | SMALLINT | |
| `stolen_bases` | SMALLINT | |
| `caught_stealing` | SMALLINT | |
| `walks` | SMALLINT | |
| `intentional_walks` | SMALLINT | |
| `strikeouts` | SMALLINT | |
| `hit_by_pitch` | SMALLINT | |
| `sac_flies` | SMALLINT | |
| `batting_avg` | NUMERIC(5,3) | |
| `on_base_pct` | NUMERIC(5,3) | |
| `slugging_pct` | NUMERIC(5,3) | |
| `ops` | NUMERIC(5,3) | |
| `woba` | NUMERIC(5,3) | From pybaseball/Statcast |
| `wrc_plus` | SMALLINT | From pybaseball/FanGraphs |
| `babip` | NUMERIC(5,3) | |
| `iso` | NUMERIC(5,3) | Isolated power |
| `updated_at` | TIMESTAMPTZ | |

Unique constraint: `(player_id, season_year, game_id)` — game_id nullable, use `COALESCE(game_id, -1)` in unique index.

Index: `(season_year, home_runs DESC)`, `(season_year, ops DESC)` — supports leaderboard queries.

---

## `pitching_stats`

Same game-level / season-aggregate pattern as `batting_stats`.

| Column | Type | Notes |
|---|---|---|
| `stat_id` | SERIAL PK | |
| `player_id` | INTEGER FK → players | |
| `team_id` | INTEGER FK → teams | |
| `season_year` | SMALLINT FK → seasons | |
| `game_id` | INTEGER FK → games | NULL = season aggregate |
| `games_pitched` | SMALLINT | |
| `games_started` | SMALLINT | |
| `complete_games` | SMALLINT | |
| `shutouts` | SMALLINT | |
| `wins` | SMALLINT | |
| `losses` | SMALLINT | |
| `saves` | SMALLINT | |
| `holds` | SMALLINT | |
| `blown_saves` | SMALLINT | |
| `innings_pitched` | NUMERIC(6,1) | e.g. 120.2 |
| `hits_allowed` | SMALLINT | |
| `runs_allowed` | SMALLINT | |
| `earned_runs` | SMALLINT | |
| `home_runs_allowed` | SMALLINT | |
| `walks` | SMALLINT | |
| `intentional_walks` | SMALLINT | |
| `strikeouts` | SMALLINT | |
| `hit_batters` | SMALLINT | |
| `wild_pitches` | SMALLINT | |
| `era` | NUMERIC(5,2) | |
| `whip` | NUMERIC(5,3) | |
| `k_per_9` | NUMERIC(5,2) | |
| `bb_per_9` | NUMERIC(5,2) | |
| `hr_per_9` | NUMERIC(5,2) | |
| `k_pct` | NUMERIC(5,3) | |
| `bb_pct` | NUMERIC(5,3) | |
| `fip` | NUMERIC(5,2) | From pybaseball |
| `xfip` | NUMERIC(5,2) | From pybaseball |
| `war` | NUMERIC(5,2) | Pitching WAR |
| `updated_at` | TIMESTAMPTZ | |

Index: `(season_year, era ASC)`, `(season_year, strikeouts DESC)` — supports leaderboard queries.

---

## `fielding_stats`

| Column | Type | Notes |
|---|---|---|
| `stat_id` | SERIAL PK | |
| `player_id` | INTEGER FK → players | |
| `team_id` | INTEGER FK → teams | |
| `season_year` | SMALLINT FK → seasons | |
| `game_id` | INTEGER FK → games | NULL = season aggregate |
| `position` | CHAR(2) | Position for this stat line |
| `games` | SMALLINT | |
| `innings` | NUMERIC(6,1) | |
| `putouts` | SMALLINT | |
| `assists` | SMALLINT | |
| `errors` | SMALLINT | |
| `double_plays` | SMALLINT | |
| `fielding_pct` | NUMERIC(5,3) | |
| `drs` | SMALLINT | Defensive runs saved |
| `uzr` | NUMERIC(5,1) | Ultimate zone rating |
| `updated_at` | TIMESTAMPTZ | |

---

## `standings`

Daily snapshot per team. Enables trend tracking (e.g., win% over time).

| Column | Type | Notes |
|---|---|---|
| `standing_id` | SERIAL PK | |
| `team_id` | INTEGER FK → teams | |
| `season_year` | SMALLINT FK → seasons | |
| `snapshot_date` | DATE | Date this snapshot represents |
| `wins` | SMALLINT | |
| `losses` | SMALLINT | |
| `win_pct` | NUMERIC(5,3) | |
| `games_behind` | NUMERIC(4,1) | 0.0 = division leader |
| `wildcard_games_behind` | NUMERIC(4,1) | |
| `division_rank` | SMALLINT | 1–5 |
| `league_rank` | SMALLINT | 1–15 |
| `wildcard_rank` | SMALLINT | Among non-division leaders |
| `streak_type` | CHAR(1) | W or L |
| `streak_count` | SMALLINT | |
| `home_wins` | SMALLINT | |
| `home_losses` | SMALLINT | |
| `away_wins` | SMALLINT | |
| `away_losses` | SMALLINT | |
| `runs_scored` | SMALLINT | |
| `runs_allowed` | SMALLINT | |
| `run_differential` | SMALLINT | |
| `last_10_wins` | SMALLINT | |
| `last_10_losses` | SMALLINT | |
| `updated_at` | TIMESTAMPTZ | |

Unique constraint: `(team_id, season_year, snapshot_date)`
