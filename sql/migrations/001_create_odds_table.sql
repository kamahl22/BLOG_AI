-- Creates the odds_data table for all sports (NFL, NBA, MLB, NCAAF, NCAAMB, NCAAWB, NHL, Soccer, etc.)
CREATE TABLE IF NOT EXISTS odds_data (
    id SERIAL PRIMARY KEY,
    sport VARCHAR(50) NOT NULL,
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    moneyline_odds DECIMAL(10,2),
    game_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Creates the roster_data table for all sports
CREATE TABLE IF NOT EXISTS roster_data (
    id SERIAL PRIMARY KEY,
    sport VARCHAR(50) NOT NULL,
    team_id VARCHAR(50) NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    position VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
