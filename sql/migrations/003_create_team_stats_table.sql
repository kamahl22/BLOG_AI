-- Creates the team_stats table for team-level statistics (MLB focus, extensible to other sports)
CREATE TABLE IF NOT EXISTS team_stats (
    id SERIAL PRIMARY KEY,
    sport VARCHAR(50) NOT NULL, -- e.g., 'MLB'
    team_name VARCHAR(100) NOT NULL, -- e.g., 'Chicago Cubs'
    stat_type VARCHAR(50) NOT NULL, -- e.g., 'run_line_trends', 'batting'
    games INTEGER, -- Games played
    at_bats INTEGER, -- AB
    runs INTEGER, -- R
    hits INTEGER, -- H
    doubles INTEGER, -- 2B
    triples INTEGER, -- 3B
    home_runs INTEGER, -- HR
    rbi INTEGER, -- RBI
    walks INTEGER, -- BB
    strikeouts INTEGER, -- SO
    batting_avg DECIMAL(5,3), -- BA
    on_base_pct DECIMAL(5,3), -- OBP
    slugging_pct DECIMAL(5,3), -- SLG
    ops DECIMAL(5,3), -- OPS
    run_line_wins INTEGER, -- Run line wins
    run_line_losses INTEGER, -- Run line losses
    run_line_cover_pct DECIMAL(5,3), -- ATS cover percentage
    source VARCHAR(50), -- e.g., 'TeamRankings', 'ESPN'
    stat_date DATE NOT NULL, -- Date of stats
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);