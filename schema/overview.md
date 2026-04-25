# Data Model Overview

## Storage System Decision Guide

| Storage | Use When |
|---|---|
| **RDS (PostgreSQL)** | Structured, relational, query-heavy (joins, aggregations, filters) |
| **DynamoDB** | High-throughput writes, append-only event streams, real-time state |
| **S3** | Raw API response archival, large batch files, audit trail |

## Entity Map

```
Season
  └── Game (many per season)
        ├── PlayByPlayEvent (many per game)  → DynamoDB
        │     └── Pitch (many per event)    → DynamoDB
        ├── BattingStats (per player)        → RDS
        └── PitchingStats (per player)       → RDS

Team
  ├── Roster → Player (many-to-many via season)
  ├── TeamStats (per season)                 → RDS
  └── Standings (daily snapshot)             → RDS

Player
  ├── BattingStats (game-level + season agg) → RDS
  ├── PitchingStats (game-level + season agg)→ RDS
  └── FieldingStats (game-level + season agg)→ RDS

LiveGameState (singleton per active game)    → DynamoDB
```

## Key Design Decisions

- **Stat aggregates are stored, not always computed**: Season-level aggregates (AVG, ERA, OPS, etc.) are stored as columns rather than computed on every query. They are refreshed on a schedule. This makes leaderboard queries fast.
- **Game-level and season-level stats share the same tables**: A `game_id` FK distinguishes game-level rows from season aggregates (`game_id IS NULL`).
- **Live game state is ephemeral**: DynamoDB holds the current state of an in-progress game. Once final, the structured result is written to RDS and the DynamoDB entry can expire.
- **Play-by-play is write-once, retained indefinitely**: Events are appended in real time and never mutated.
- **Raw API responses are always archived to S3** before being processed, so any schema changes can trigger a reprocess from source.
- **No player deduplication strategy yet**: Player IDs from the MLB Stats API are used as the canonical identifier. `pybaseball` / Statcast data will be joined via the same MLB player ID where available.

## Refresh Cadence Summary

| Data | System | Cadence |
|---|---|---|
| Live game state | DynamoDB | Every ~15s during games |
| Play-by-play events | DynamoDB | On each event (~real-time) |
| Pitch data | DynamoDB | On each pitch |
| Game results (final) | RDS | End of game |
| Player game stats | RDS | End of game |
| Player season stats | RDS | Every 4–6 hours |
| Team stats / standings | RDS | Every 4–6 hours |
| Schedule | RDS | Daily |
