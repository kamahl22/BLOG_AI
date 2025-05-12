CREATE TABLE odds_data (
    id SERIAL PRIMARY KEY,
    sport VARCHAR(50) NOT NULL,
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    home_odds INTEGER,
    away_odds INTEGER,
    game_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);