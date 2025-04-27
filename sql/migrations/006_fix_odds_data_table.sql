-- Drops and recreates the odds_data table to fix schema issues
DROP TABLE IF EXISTS odds_data;

CREATE TABLE IF NOT EXISTS odds_data (
    id SERIAL PRIMARY KEY,
    sport VARCHAR(50) NOT NULL, -- e.g., 'NFL', 'MLB'
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    moneyline_odds DECIMAL(10,2),
    game_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);