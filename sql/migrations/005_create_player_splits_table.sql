-- Creates the player_splits table for player-level splits (e.g., vs. Left, Home)
CREATE TABLE IF NOT EXISTS player_splits (
    id SERIAL PRIMARY KEY,
    sport VARCHAR(50) NOT NULL, -- e.g., 'MLB'
    player_name VARCHAR(100) NOT NULL, -- e.g., 'Kyle Tucker'
    team_name VARCHAR(100), -- e.g., 'Chicago Cubs'
    split_type VARCHAR(50) NOT NULL, -- e.g., 'vs_left', 'home', 'count_0_0'
    split_value VARCHAR(50) NOT NULL, -- e.g., 'vs. Left', 'Home', 'Count 0-0'
    at_bats INTEGER, -- AB
    runs INTEGER, -- R
    hits INTEGER, -- H
    doubles INTEGER, -- 2B
    triples INTEGER, -- 3B
    home_runs INTEGER, -- HR
    rbi INTEGER, -- RBI
    walks INTEGER, -- BB
    strikeouts INTEGER, -- SO
    stolen_bases INTEGER, -- SB
    caught_stealing INTEGER, -- CS
    batting_avg DECIMAL(5,3), -- BA
    on_base_pct DECIMAL(5,3), -- OBP
    slugging_pct DECIMAL(5,3), -- SLG
    ops DECIMAL(5,3), -- OPS
    source VARCHAR(50), -- e.g., 'ESPN'
    stat_date DATE NOT NULL, -- Date of stats
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);