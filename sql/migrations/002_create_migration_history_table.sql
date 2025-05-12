CREATE TABLE migration_history (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(100) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);