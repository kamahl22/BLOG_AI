-- Drops and recreates the odds_data table to fix schema issues
DROP TABLE IF EXISTS odds_data;
CREATE TABLE odds_data (
    id SERIAL PRIMARY KEY,
    sport VARCHAR(50),
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    home_odds INTEGER, -- Added to store home team moneyline odds
    away_odds INTEGER, -- Added to store away team moneyline odds
    game_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);