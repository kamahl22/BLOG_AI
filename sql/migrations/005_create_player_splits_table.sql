-- Creates the player_splits table for player-level splits (e.g., vs. Left, Home)
CREATE TABLE player_splits (
    id SERIAL PRIMARY KEY,
    sport VARCHAR(50),
    player_name VARCHAR(100),
    team_name VARCHAR(100),
    split_type VARCHAR(50),
    split_value VARCHAR(100),
    season INTEGER, -- Added for yearly context
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