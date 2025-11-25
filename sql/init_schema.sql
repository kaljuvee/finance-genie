-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema for genie
CREATE SCHEMA IF NOT EXISTS genie;

-- Vector store for world model documents
CREATE TABLE IF NOT EXISTS genie.vecs (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trading runs table
CREATE TABLE IF NOT EXISTS genie.trading_runs (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(255) UNIQUE NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    youtube_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trading decisions table
CREATE TABLE IF NOT EXISTS genie.trading_decisions (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(255) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    median_return FLOAT,
    q25_return FLOAT,
    q75_return FLOAT,
    action VARCHAR(10),
    raw_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES genie.trading_runs(run_id)
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS genie.performance_metrics (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(255) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    predicted_action VARCHAR(10),
    actual_return FLOAT,
    predicted_median FLOAT,
    predicted_q25 FLOAT,
    predicted_q75 FLOAT,
    accuracy_flag BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES genie.trading_runs(run_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_vecs_created ON genie.vecs(created_at);
CREATE INDEX IF NOT EXISTS idx_trading_runs_symbol ON genie.trading_runs(symbol);
CREATE INDEX IF NOT EXISTS idx_trading_decisions_run_id ON genie.trading_decisions(run_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_run_id ON genie.performance_metrics(run_id);
