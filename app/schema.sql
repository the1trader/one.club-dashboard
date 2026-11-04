-- ==============================================================================
-- one.club-dashboard Database Schema
-- Compatible with Neon PostgreSQL (schema: one_club) & SQLite (local fallback)
-- ==============================================================================

-- 1. Real-Time Live Tape Executions
CREATE TABLE IF NOT EXISTS live_trades (
    id VARCHAR(50) PRIMARY KEY,
    date DATE NOT NULL,
    entry_time VARCHAR(50) NOT NULL,
    exit_time VARCHAR(50),
    setup VARCHAR(255) NOT NULL,
    side VARCHAR(10) NOT NULL,
    contracts INT NOT NULL,
    entry_price NUMERIC(10, 2) NOT NULL,
    exit_price NUMERIC(10, 2),
    stop_loss NUMERIC(10, 2),
    take_profit NUMERIC(10, 2),
    sl_points NUMERIC(10, 2),
    tp_points NUMERIC(10, 2),
    rr_ratio NUMERIC(10, 2),
    dollar_risk NUMERIC(10, 2),
    risk_pct NUMERIC(5, 2),
    points NUMERIC(10, 2),
    pnl NUMERIC(10, 2),
    status VARCHAR(20) NOT NULL,
    reason VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Quarantined Historical Chart Studies & Backtests (Non-Executed)
CREATE TABLE IF NOT EXISTS historical_studies (
    study_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    session_window VARCHAR(100) NOT NULL,
    side VARCHAR(10) NOT NULL,
    entry_time VARCHAR(50) NOT NULL,
    exit_time VARCHAR(50) NOT NULL,
    entry_price NUMERIC(10, 2) NOT NULL,
    exit_price NUMERIC(10, 2) NOT NULL,
    points NUMERIC(10, 2) NOT NULL,
    theoretical_rr VARCHAR(20),
    dollar_risk NUMERIC(10, 2),
    hypothetical_pnl NUMERIC(10, 2),
    execution_type VARCHAR(100) DEFAULT 'HISTORICAL_CHART_STUDY (NON-EXECUTED)',
    account_impact VARCHAR(100) DEFAULT '$0.00 (Zero live account impact)',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Professional 3-Phase Trade Journal & Retrospectives
CREATE TABLE IF NOT EXISTS journal_entries (
    trade_id VARCHAR(50) PRIMARY KEY,
    date DATE NOT NULL,
    entry_time VARCHAR(50) NOT NULL,
    exit_time VARCHAR(50),
    setup VARCHAR(255) NOT NULL,
    instrument VARCHAR(50) DEFAULT 'US100 (NQ)',
    side VARCHAR(10) NOT NULL,
    contracts INT NOT NULL,
    entry_price NUMERIC(10, 2) NOT NULL,
    stop_loss NUMERIC(10, 2) NOT NULL,
    take_profit NUMERIC(10, 2) NOT NULL,
    dollar_risk NUMERIC(10, 2) NOT NULL,
    risk_pct NUMERIC(5, 2) NOT NULL,
    pre_trade_thesis TEXT,      -- Stored as JSON or JSONB
    in_trade_logs TEXT,         -- Stored as JSON or JSONB
    exit_review TEXT,           -- Stored as JSON or JSONB
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Account Balance & Verified Performance Metrics
CREATE TABLE IF NOT EXISTS account_metrics (
    account_id VARCHAR(50) PRIMARY KEY,
    initial_balance NUMERIC(12, 2) NOT NULL DEFAULT 50000.00,
    balance NUMERIC(12, 2) NOT NULL,
    equity NUMERIC(12, 2) NOT NULL,
    total_trades INT NOT NULL,
    wins INT NOT NULL,
    losses INT NOT NULL,
    win_rate NUMERIC(5, 2) NOT NULL,
    net_pnl NUMERIC(12, 2) NOT NULL,
    profit_factor NUMERIC(10, 2) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Autonomous Agent Chain-of-Thought Decision Stream
CREATE TABLE IF NOT EXISTS agent_decisions (
    id SERIAL PRIMARY KEY,
    ny_time VARCHAR(50) NOT NULL,
    phase VARCHAR(100) NOT NULL,
    us100_price NUMERIC(10, 2),
    us500_price NUMERIC(10, 2),
    observation TEXT NOT NULL,
    decision TEXT NOT NULL,
    bias VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
