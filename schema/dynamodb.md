# DynamoDB Schema

DynamoDB is used for high-throughput real-time data: live game state, play-by-play events, and pitch data. These access patterns favor key-based lookups over ad-hoc querying.

All items include a `ttl` attribute (epoch seconds) where appropriate for automatic expiry.

---

## Table: `mlb-live-game-state`

Holds the current state of each in-progress game. One item per active game, updated every ~15 seconds.

**Key schema**
| Attribute | Role | Type |
|---|---|---|
| `game_id` | Partition Key | Number |

**Item attributes**
| Attribute | Type | Notes |
|---|---|---|
| `game_id` | N | MLB Stats API gamePk |
| `status` | S | live, final, suspended |
| `inning` | N | Current inning number |
| `inning_half` | S | top, bottom |
| `outs` | N | 0–3 |
| `balls` | N | 0–3 |
| `strikes` | N | 0–2 |
| `home_team_id` | N | |
| `away_team_id` | N | |
| `home_score` | N | |
| `away_score` | N | |
| `current_batter_id` | N | |
| `current_pitcher_id` | N | |
| `runner_first` | N | Player ID or absent if empty |
| `runner_second` | N | Player ID or absent if empty |
| `runner_third` | N | Player ID or absent if empty |
| `last_play` | S | Plain text description of last play |
| `updated_at` | S | ISO 8601 UTC timestamp |
| `ttl` | N | Epoch seconds — expires 24h after game ends |

**Access pattern**: `GetItem(game_id)` — single game state lookup for the live tracker UI.

---

## Table: `mlb-play-by-play`

Append-only log of every play event in every game. Written in real time, retained indefinitely for post-game review and future anomaly detection.

**Key schema**
| Attribute | Role | Type |
|---|---|---|
| `game_id` | Partition Key | Number |
| `event_id` | Sort Key | String |

`event_id` format: `{inning}_{half}_{sequence_number}` (e.g., `09_B_003`) — lexicographically sortable, human-readable.

**Item attributes**
| Attribute | Type | Notes |
|---|---|---|
| `game_id` | N | |
| `event_id` | S | Sort key |
| `season_year` | N | For GSI queries by season |
| `game_date` | S | YYYY-MM-DD, for GSI |
| `inning` | N | |
| `inning_half` | S | top, bottom |
| `sequence_number` | N | Order within game |
| `play_type` | S | single, double, triple, home_run, strikeout, walk, stolen_base, caught_stealing, error, sac_fly, fielders_choice, etc. |
| `batter_id` | N | |
| `pitcher_id` | N | |
| `outs_before` | N | 0–2 |
| `balls_before` | N | 0–3 |
| `strikes_before` | N | 0–2 |
| `runners_before` | M | Map: `{first: N|null, second: N|null, third: N|null}` |
| `result_description` | S | Human-readable play description |
| `rbi` | N | RBI credited on this play |
| `home_score_after` | N | |
| `away_score_after` | N | |
| `is_scoring_play` | BOOL | |
| `is_out` | BOOL | |
| `exit_velocity` | N | mph, from Statcast if available |
| `launch_angle` | N | degrees, from Statcast if available |
| `hit_distance` | N | feet, from Statcast if available |
| `event_timestamp` | S | ISO 8601 UTC |

**GSI: `game_date-index`**
- PK: `game_date`, SK: `game_id`
- Enables: "give me all play events for games on a given date"

**Access patterns**:
- `Query(game_id)` — full play-by-play for one game (live feed or post-game review)
- `Query(game_id, ScanIndexForward=True)` — chronological event stream
- `Query(game_id, event_id BEGINS_WITH "09")` — only 9th inning events (anomaly detection)

---

## Table: `mlb-pitch-data`

Every individual pitch thrown, written in real time. High write volume during games.

**Key schema**
| Attribute | Role | Type |
|---|---|---|
| `game_id` | Partition Key | Number |
| `pitch_id` | Sort Key | String |

`pitch_id` format: `{at_bat_sequence}_{pitch_sequence}` (e.g., `0042_006`) — zero-padded for lexicographic sort.

**Item attributes**
| Attribute | Type | Notes |
|---|---|---|
| `game_id` | N | |
| `pitch_id` | S | Sort key |
| `at_bat_sequence` | N | Which at-bat in the game |
| `pitch_sequence` | N | Which pitch in the at-bat |
| `pitcher_id` | N | |
| `batter_id` | N | |
| `inning` | N | |
| `inning_half` | S | |
| `pitch_type` | S | FF, SL, CH, CU, SI, FC, KC, FS, etc. (Statcast codes) |
| `pitch_type_name` | S | Four-Seam Fastball, Slider, etc. |
| `start_speed` | N | mph out of hand |
| `end_speed` | N | mph at plate |
| `spin_rate` | N | RPM |
| `spin_direction` | N | degrees |
| `plate_x` | N | Horizontal position at plate (ft from center, catcher's view) |
| `plate_z` | N | Vertical position at plate (ft from ground) |
| `zone` | N | 1–9 in zone, 11–14 outside |
| `call` | S | B=ball, S=strike, X=in play |
| `description` | S | called_strike, swinging_strike, ball, foul, hit_into_play, blocked_ball, etc. |
| `balls_before` | N | Count before this pitch |
| `strikes_before` | N | Count before this pitch |
| `event_timestamp` | S | ISO 8601 UTC |

**GSI: `pitcher-index`**
- PK: `pitcher_id`, SK: `event_timestamp`
- Enables: "give me all pitches thrown by a pitcher today/this game"

**Access patterns**:
- `Query(game_id)` — all pitches in a game
- `Query(game_id, pitch_id BEGINS_WITH "0042")` — all pitches in a specific at-bat
- `Query(pitcher_id)` via GSI — pitcher's recent pitch log
