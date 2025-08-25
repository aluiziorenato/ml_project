-- Initialize ML Project Database
CREATE DATABASE IF NOT EXISTS ml_project;

-- Create additional databases for components
CREATE DATABASE IF NOT EXISTS mlflow_db;

-- Create user if not exists
CREATE USER ml_user WITH ENCRYPTED PASSWORD 'ml_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ml_project TO ml_user;
GRANT ALL PRIVILEGES ON DATABASE mlflow_db TO ml_user;

-- Switch to ml_project database
\c ml_project;

-- Create tables for experiment tracking
CREATE TABLE IF NOT EXISTS experiments (
    id SERIAL PRIMARY KEY,
    experiment_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS experiment_results (
    id SERIAL PRIMARY KEY,
    experiment_id VARCHAR(255) REFERENCES experiments(experiment_id),
    model_name VARCHAR(255) NOT NULL,
    score FLOAT,
    parameters JSONB,
    metrics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_experiments_experiment_id ON experiments(experiment_id);
CREATE INDEX IF NOT EXISTS idx_experiment_results_experiment_id ON experiment_results(experiment_id);
CREATE INDEX IF NOT EXISTS idx_experiment_results_score ON experiment_results(score);

-- Grant permissions to ml_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ml_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ml_user;