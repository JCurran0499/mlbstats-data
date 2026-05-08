-- MLB Stats RDS schema (PostgreSQL / public schema)
-- Source of truth for Atlas versioned migrations.
-- Never edit applied migrations — add a new migration instead.

CREATE TABLE teams (
    team_id      INTEGER PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    abbreviation CHAR(3)    NOT NULL,
    city          VARCHAR(100) NOT NULL,
    league        CHAR(2)     NOT NULL,
    division      VARCHAR(20) NOT NULL,
    venue_name    VARCHAR(100),
    debut_year    CHAR(4),
    active        BOOLEAN     NOT NULL DEFAULT TRUE
);

CREATE TABLE players (
    player_id               INTEGER PRIMARY KEY,
    first_name              VARCHAR(100) NOT NULL,
    last_name               VARCHAR(100) NOT NULL,
    full_name               VARCHAR(200),
    nickname                VARCHAR(100),
    team_id                 INTEGER REFERENCES teams(team_id),
    primary_number          CHAR(2),
    birth_date              DATE,
    birth_country           VARCHAR(100),
    birth_city              VARCHAR(100),
    birth_state_province    VARCHAR(100),
    primary_position        VARCHAR(5),
    bats                    CHAR(1),
    throws                  CHAR(1),
    height_inches           SMALLINT,
    weight_lbs              SMALLINT,
    debut_date              DATE,
    active                  BOOLEAN NOT NULL DEFAULT TRUE,
    status_code             VARCHAR(20)
);

CREATE TABLE rosters (
    roster_id     SERIAL  PRIMARY KEY,
    player_id     INTEGER NOT NULL REFERENCES players(player_id),
    team_id       INTEGER NOT NULL REFERENCES teams(team_id),
    season_year   SMALLINT NOT NULL,
    roster_status VARCHAR(30) NOT NULL,
    active        BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE UNIQUE INDEX rosters_player_team_season ON rosters (player_id, team_id, season_year);
CREATE INDEX rosters_team_season              ON rosters (team_id, season_year);

CREATE TABLE games (
    game_id               INTEGER PRIMARY KEY,
    season_year           SMALLINT    NOT NULL,
    game_date             DATE        NOT NULL,
    game_type             CHAR(1)     NOT NULL,
    series_description    VARCHAR(50),
    home_team_id          INTEGER     NOT NULL REFERENCES teams(team_id),
    away_team_id          INTEGER     NOT NULL REFERENCES teams(team_id),
    venue_name            VARCHAR(100),
    status                VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    home_score            SMALLINT,
    away_score            SMALLINT,
    innings_played        SMALLINT,
    winning_team_id       INTEGER REFERENCES teams(team_id),
    losing_team_id        INTEGER REFERENCES teams(team_id),
    game_duration_minutes SMALLINT,
    attendance            INTEGER,
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX games_game_date        ON games (game_date);
CREATE INDEX games_home_team_season ON games (home_team_id, season_year);
CREATE INDEX games_away_team_season ON games (away_team_id, season_year);

CREATE TABLE batting_stats (
    stat_id           SERIAL  PRIMARY KEY,
    player_id         INTEGER NOT NULL REFERENCES players(player_id),
    team_id           INTEGER NOT NULL REFERENCES teams(team_id),
    season_year       SMALLINT NOT NULL,
    games_played      SMALLINT,
    plate_appearances SMALLINT,
    at_bats           SMALLINT,
    runs              SMALLINT,
    hits              SMALLINT,
    doubles           SMALLINT,
    triples           SMALLINT,
    home_runs         SMALLINT,
    rbi               SMALLINT,
    stolen_bases      SMALLINT,
    caught_stealing   SMALLINT,
    walks             SMALLINT,
    intentional_walks SMALLINT,
    strikeouts        SMALLINT,
    hit_by_pitch      SMALLINT,
    sac_flies         SMALLINT,
    batting_avg       NUMERIC(5,3),
    on_base_pct       NUMERIC(5,3),
    slugging_pct      NUMERIC(5,3),
    ops               NUMERIC(5,3),
    woba              NUMERIC(5,3),
    wrc_plus          SMALLINT,
    babip             NUMERIC(5,3),
    iso               NUMERIC(5,3),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX batting_stats_unique ON batting_stats (player_id, season_year);
CREATE INDEX batting_stats_hr_leaderboard  ON batting_stats (season_year, home_runs DESC);
CREATE INDEX batting_stats_ops_leaderboard ON batting_stats (season_year, ops DESC);

CREATE TABLE pitching_stats (
    stat_id           SERIAL  PRIMARY KEY,
    player_id         INTEGER NOT NULL REFERENCES players(player_id),
    team_id           INTEGER NOT NULL REFERENCES teams(team_id),
    season_year       SMALLINT NOT NULL,
    games_pitched     SMALLINT,
    games_started     SMALLINT,
    complete_games    SMALLINT,
    shutouts          SMALLINT,
    wins              SMALLINT,
    losses            SMALLINT,
    saves             SMALLINT,
    holds             SMALLINT,
    blown_saves       SMALLINT,
    innings_pitched   NUMERIC(6,1),
    hits_allowed      SMALLINT,
    runs_allowed      SMALLINT,
    earned_runs       SMALLINT,
    home_runs_allowed SMALLINT,
    walks             SMALLINT,
    intentional_walks SMALLINT,
    strikeouts        SMALLINT,
    hit_batters       SMALLINT,
    wild_pitches      SMALLINT,
    era               NUMERIC(5,2),
    whip              NUMERIC(5,3),
    k_per_9           NUMERIC(5,2),
    bb_per_9          NUMERIC(5,2),
    hr_per_9          NUMERIC(5,2),
    k_pct             NUMERIC(5,3),
    bb_pct            NUMERIC(5,3),
    fip               NUMERIC(5,2),
    xfip              NUMERIC(5,2),
    war               NUMERIC(5,2),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX pitching_stats_unique       ON pitching_stats (player_id, season_year);
CREATE INDEX pitching_stats_era_leaderboard ON pitching_stats (season_year, era ASC);
CREATE INDEX pitching_stats_k_leaderboard   ON pitching_stats (season_year, strikeouts DESC);

CREATE TABLE fielding_stats (
    stat_id      SERIAL  PRIMARY KEY,
    player_id    INTEGER NOT NULL REFERENCES players(player_id),
    team_id      INTEGER NOT NULL REFERENCES teams(team_id),
    season_year  SMALLINT NOT NULL,
    position     CHAR(5) NOT NULL,
    games        SMALLINT,
    innings      NUMERIC(6,1),
    putouts      SMALLINT,
    assists      SMALLINT,
    errors       SMALLINT,
    double_plays SMALLINT,
    fielding_pct NUMERIC(5,3),
    drs          SMALLINT,
    uzr          NUMERIC(5,1),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX fielding_stats_unique ON fielding_stats (player_id, season_year, position);

CREATE TABLE standings (
    standing_id              SERIAL  PRIMARY KEY,
    team_id                  INTEGER NOT NULL REFERENCES teams(team_id),
    season_year              SMALLINT NOT NULL,
    snapshot_date            DATE    NOT NULL,
    wins                     SMALLINT NOT NULL,
    losses                   SMALLINT NOT NULL,
    win_pct                  NUMERIC(5,3),
    games_behind             NUMERIC(4,1),
    wildcard_games_behind    NUMERIC(4,1),
    division_rank            SMALLINT,
    league_rank              SMALLINT,
    wildcard_rank            SMALLINT,
    streak_type              CHAR(1),
    streak_count             SMALLINT,
    home_wins                SMALLINT,
    home_losses              SMALLINT,
    away_wins                SMALLINT,
    away_losses              SMALLINT,
    runs_scored              SMALLINT,
    runs_allowed             SMALLINT,
    run_differential         SMALLINT,
    last_10_wins             SMALLINT,
    last_10_losses           SMALLINT,
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX standings_unique ON standings (team_id, season_year, snapshot_date);
