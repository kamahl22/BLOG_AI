-- Creates the team_stats table for team-level statistics (MLB focus, extensible to other sports)
CREATE TABLE team_stats (
    id SERIAL PRIMARY KEY,
    sport VARCHAR(50),
    team_name VARCHAR(100),
    stat_type VARCHAR(50),
    season INTEGER, -- Added for yearly context
    games INTEGER,
    at_bats INTEGER,
    runs INTEGER,
    hits INTEGER,
    doubles INTEGER,
    triples INTEGER,
    home_runs INTEGER,
    rbi INTEGER,
    walks INTEGER,
    strikeouts INTEGER,
    batting_avg FLOAT,
    on_base_pct FLOAT,
    slugging_pct FLOAT,
    ops FLOAT,
    run_line_wins INTEGER,
    run_line_losses INTEGER,
    run_line_cover_pct FLOAT,
    source VARCHAR(50),
    stat_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);