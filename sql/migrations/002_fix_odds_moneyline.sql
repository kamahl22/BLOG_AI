-- Fixes the moneyline_odds column to support decimal values for all sports
ALTER TABLE odds_data
ALTER COLUMN moneyline_odds TYPE DECIMAL(10,2);
