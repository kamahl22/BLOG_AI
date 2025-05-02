-- Creates the player_stats table for player-level season totals (MLB focus)
CREATE TABLE player_stats (
    id SERIAL PRIMARY KEY,
    sport VARCHAR(50),
    player_name VARCHAR(100),
    team_name VARCHAR(100),
    stat_type VARCHAR(50),
    season INTEGER, -- Added for yearly context
    games INTEGER, -- Renamed from games_played for consistency
    at_bats INTEGER,
    runs INTEGER,
    hits INTEGER,
    doubles INTEGER,
    triples INTEGER,
    home_runs INTEGER,
    rbi INTEGER,
    walks INTEGER,
    strikeouts INTEGER,
    stolen_bases INTEGER,
    caught_stealing INTEGER,
    batting_avg FLOAT,
    on_base_pct FLOAT,
    slugging_pct FLOAT,
    ops FLOAT,
    source VARCHAR(50),
    stat_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);