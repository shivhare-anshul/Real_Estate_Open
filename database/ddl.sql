-- PostgreSQL DDL for Real Estate Data Pipeline
-- Schema 1: Structured Data

-- Project Tasks Table (from Project Schedule Document)
CREATE TABLE IF NOT EXISTS project_tasks (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL UNIQUE,
    task_name VARCHAR(500) NOT NULL,
    duration_days INTEGER NOT NULL CHECK (duration_days >= 0),
    start_date DATE NOT NULL,
    finish_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_finish_after_start CHECK (finish_date >= start_date)
);

-- Cost Items Table (from Construction Planning and Costing Document)
CREATE TABLE IF NOT EXISTS cost_items (
    id SERIAL PRIMARY KEY,
    item_name VARCHAR(500) NOT NULL,
    quantity NUMERIC(15, 2) NOT NULL CHECK (quantity >= 0),
    unit_price_yen NUMERIC(15, 2) NOT NULL CHECK (unit_price_yen >= 0),
    total_cost_yen NUMERIC(20, 2) NOT NULL CHECK (total_cost_yen >= 0),
    cost_type VARCHAR(50) NOT NULL CHECK (cost_type IN ('Foreign cost', 'Local cost', 'foreign cost', 'local cost')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Regulatory Rules Table (from URA Circular)
CREATE TABLE IF NOT EXISTS regulatory_rules (
    id SERIAL PRIMARY KEY,
    rule_id VARCHAR(50) NOT NULL UNIQUE,
    rule_summary TEXT NOT NULL,
    measurement_basis VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_project_tasks_task_id ON project_tasks(task_id);
CREATE INDEX IF NOT EXISTS idx_project_tasks_start_date ON project_tasks(start_date);
CREATE INDEX IF NOT EXISTS idx_cost_items_cost_type ON cost_items(cost_type);
CREATE INDEX IF NOT EXISTS idx_regulatory_rules_rule_id ON regulatory_rules(rule_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_project_tasks_updated_at BEFORE UPDATE ON project_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cost_items_updated_at BEFORE UPDATE ON cost_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_regulatory_rules_updated_at BEFORE UPDATE ON regulatory_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

