-- TradeMate Database Performance Optimization
-- Tier-specific optimizations for <50ms premium, <100ms shared targets

-- =====================================================
-- SHARED TIER OPTIMIZATIONS (LITE + PRO)
-- =====================================================

-- Create optimized indexes for common queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trades_user_created 
ON trades(user_id, created_at DESC) 
WHERE status = 'completed';

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_portfolio_user_symbol 
ON portfolio_positions(user_id, symbol, last_updated DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_user_status 
ON orders(user_id, status, created_at DESC)
WHERE status IN ('pending', 'active');

-- Partial indexes for WhatsApp webhook queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_whatsapp_messages_pending
ON whatsapp_messages(user_phone, created_at DESC)
WHERE processed = false;

-- Materialized view for portfolio summary (shared tier)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_portfolio_summary_shared AS
SELECT 
    p.user_id,
    COUNT(DISTINCT p.symbol) as total_positions,
    SUM(p.quantity * s.current_price) as portfolio_value,
    SUM(p.quantity * s.current_price) - SUM(p.quantity * p.average_price) as total_pnl,
    CASE 
        WHEN SUM(p.quantity * p.average_price) > 0 
        THEN ((SUM(p.quantity * s.current_price) - SUM(p.quantity * p.average_price)) / SUM(p.quantity * p.average_price) * 100)
        ELSE 0 
    END as pnl_percentage,
    MAX(p.last_updated) as last_updated
FROM portfolio_positions p
JOIN stock_prices s ON p.symbol = s.symbol
WHERE p.quantity > 0
GROUP BY p.user_id;

-- Index on materialized view
CREATE UNIQUE INDEX ON mv_portfolio_summary_shared(user_id);

-- Refresh materialized view every 5 minutes for shared tier
CREATE OR REPLACE FUNCTION refresh_shared_portfolio_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_portfolio_summary_shared;
END;
$$ LANGUAGE plpgsql;

-- Table partitioning for trades (monthly partitions)
CREATE TABLE IF NOT EXISTS trades_shared (
    LIKE trades INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- Create partitions for next 12 months
DO $$
DECLARE
    start_date date := date_trunc('month', CURRENT_DATE);
    end_date date;
    partition_name text;
BEGIN
    FOR i IN 0..11 LOOP
        end_date := start_date + interval '1 month';
        partition_name := 'trades_shared_' || to_char(start_date, 'YYYY_MM');
        
        EXECUTE format('
            CREATE TABLE IF NOT EXISTS %I PARTITION OF trades_shared
            FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date
        );
        
        start_date := end_date;
    END LOOP;
END$$;

-- =====================================================
-- PREMIUM TIER OPTIMIZATIONS (ELITE + BLACK)
-- =====================================================

-- High-performance indexes for premium tier
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trades_premium_composite
ON trades(user_id, symbol, created_at DESC, trade_type)
INCLUDE (quantity, price, total_amount)
WHERE tier IN ('ELITE', 'BLACK');

-- Covering index for instant portfolio queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_portfolio_premium_covering
ON portfolio_positions(user_id, symbol)
INCLUDE (quantity, average_price, realized_pnl, unrealized_pnl)
WHERE tier IN ('ELITE', 'BLACK');

-- Index for algorithmic trading queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_algo_orders_premium
ON algorithmic_orders(user_id, strategy_id, status, created_at DESC)
WHERE tier IN ('ELITE', 'BLACK');

-- Materialized view for real-time positions (premium tier)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_realtime_positions_premium AS
WITH latest_prices AS (
    SELECT DISTINCT ON (symbol) 
        symbol, 
        current_price, 
        day_change_percent,
        volume,
        last_updated
    FROM stock_prices
    ORDER BY symbol, last_updated DESC
)
SELECT 
    p.user_id,
    p.symbol,
    p.quantity,
    p.average_price,
    lp.current_price,
    p.quantity * lp.current_price as current_value,
    p.quantity * (lp.current_price - p.average_price) as unrealized_pnl,
    CASE 
        WHEN p.average_price > 0 
        THEN ((lp.current_price - p.average_price) / p.average_price * 100)
        ELSE 0 
    END as pnl_percentage,
    lp.day_change_percent,
    lp.volume,
    p.last_updated
FROM portfolio_positions p
JOIN latest_prices lp ON p.symbol = lp.symbol
WHERE p.quantity > 0 AND p.tier IN ('ELITE', 'BLACK');

-- Unique index for fast lookups
CREATE UNIQUE INDEX ON mv_realtime_positions_premium(user_id, symbol);

-- Refresh materialized view every minute for premium tier
CREATE OR REPLACE FUNCTION refresh_premium_positions()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_realtime_positions_premium;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- QUERY OPTIMIZATION SETTINGS
-- =====================================================

-- Shared tier connection settings
ALTER DATABASE trademate_shared SET work_mem = '4MB';
ALTER DATABASE trademate_shared SET effective_cache_size = '4GB';
ALTER DATABASE trademate_shared SET random_page_cost = 1.1;
ALTER DATABASE trademate_shared SET effective_io_concurrency = 200;

-- Premium tier connection settings (more aggressive)
ALTER DATABASE trademate_premium SET work_mem = '16MB';
ALTER DATABASE trademate_premium SET effective_cache_size = '8GB';
ALTER DATABASE trademate_premium SET random_page_cost = 1.0;
ALTER DATABASE trademate_premium SET effective_io_concurrency = 300;
ALTER DATABASE trademate_premium SET jit = off; -- Disable JIT for consistent latency

-- =====================================================
-- PERFORMANCE MONITORING VIEWS
-- =====================================================

-- View to monitor slow queries
CREATE OR REPLACE VIEW v_slow_queries AS
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    stddev_exec_time,
    max_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > CASE 
    WHEN current_database() LIKE '%premium%' THEN 20  -- 20ms threshold for premium
    ELSE 50  -- 50ms threshold for shared
END
ORDER BY mean_exec_time DESC
LIMIT 20;

-- View to monitor index usage
CREATE OR REPLACE VIEW v_index_usage AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    CASE 
        WHEN idx_scan = 0 THEN 'UNUSED'
        WHEN idx_scan < 100 THEN 'RARELY USED'
        ELSE 'ACTIVE'
    END as usage_status
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- =====================================================
-- VACUUM AND ANALYZE OPTIMIZATION
-- =====================================================

-- Aggressive autovacuum for premium tables
ALTER TABLE trades SET (autovacuum_vacuum_scale_factor = 0.05) WHERE tier IN ('ELITE', 'BLACK');
ALTER TABLE portfolio_positions SET (autovacuum_vacuum_scale_factor = 0.05) WHERE tier IN ('ELITE', 'BLACK');
ALTER TABLE orders SET (autovacuum_vacuum_scale_factor = 0.05) WHERE tier IN ('ELITE', 'BLACK');

-- Standard autovacuum for shared tables
ALTER TABLE trades SET (autovacuum_vacuum_scale_factor = 0.1) WHERE tier IN ('LITE', 'PRO');
ALTER TABLE portfolio_positions SET (autovacuum_vacuum_scale_factor = 0.1) WHERE tier IN ('LITE', 'PRO');

-- =====================================================
-- STORED PROCEDURES FOR COMMON OPERATIONS
-- =====================================================

-- Optimized portfolio fetch for shared tier
CREATE OR REPLACE FUNCTION get_portfolio_shared(p_user_id UUID)
RETURNS TABLE (
    symbol VARCHAR,
    quantity DECIMAL,
    current_value DECIMAL,
    pnl DECIMAL,
    pnl_percentage DECIMAL
) AS $$
BEGIN
    -- Use materialized view for faster response
    RETURN QUERY
    SELECT 
        p.symbol,
        p.quantity,
        p.quantity * s.current_price as current_value,
        p.quantity * (s.current_price - p.average_price) as pnl,
        CASE 
            WHEN p.average_price > 0 
            THEN ((s.current_price - p.average_price) / p.average_price * 100)
            ELSE 0 
        END as pnl_percentage
    FROM portfolio_positions p
    JOIN stock_prices s ON p.symbol = s.symbol
    WHERE p.user_id = p_user_id AND p.quantity > 0
    ORDER BY current_value DESC;
END;
$$ LANGUAGE plpgsql STABLE PARALLEL SAFE;

-- Ultra-fast portfolio fetch for premium tier
CREATE OR REPLACE FUNCTION get_portfolio_premium(p_user_id UUID)
RETURNS TABLE (
    symbol VARCHAR,
    quantity DECIMAL,
    average_price DECIMAL,
    current_price DECIMAL,
    current_value DECIMAL,
    unrealized_pnl DECIMAL,
    pnl_percentage DECIMAL,
    day_change_percent DECIMAL
) AS $$
BEGIN
    -- Use premium materialized view
    RETURN QUERY
    SELECT 
        symbol,
        quantity,
        average_price,
        current_price,
        current_value,
        unrealized_pnl,
        pnl_percentage,
        day_change_percent
    FROM mv_realtime_positions_premium
    WHERE user_id = p_user_id
    ORDER BY current_value DESC;
END;
$$ LANGUAGE plpgsql STABLE PARALLEL SAFE;

-- =====================================================
-- CONNECTION POOLING CONFIGURATION
-- =====================================================

-- PgBouncer configuration (external file)
-- Shared tier pool: max_client_conn=200, default_pool_size=25
-- Premium tier pool: max_client_conn=500, default_pool_size=50

-- =====================================================
-- MONITORING AND ALERTING
-- =====================================================

-- Create performance monitoring table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    tier VARCHAR(10),
    operation VARCHAR(50),
    execution_time DECIMAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Function to log performance metrics
CREATE OR REPLACE FUNCTION log_performance(
    p_tier VARCHAR,
    p_operation VARCHAR,
    p_execution_time DECIMAL
) RETURNS void AS $$
BEGIN
    INSERT INTO performance_metrics (tier, operation, execution_time)
    VALUES (p_tier, p_operation, p_execution_time);
    
    -- Alert if SLA breached
    IF (p_tier = 'premium' AND p_execution_time > 0.05) OR 
       (p_tier = 'shared' AND p_execution_time > 0.1) THEN
        RAISE NOTICE 'SLA BREACH: % tier % operation took %ms', 
                     p_tier, p_operation, p_execution_time * 1000;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Regular maintenance job
CREATE OR REPLACE FUNCTION perform_tier_maintenance()
RETURNS void AS $$
BEGIN
    -- Update table statistics
    ANALYZE trades;
    ANALYZE portfolio_positions;
    ANALYZE orders;
    
    -- Refresh materialized views
    PERFORM refresh_shared_portfolio_summary();
    PERFORM refresh_premium_positions();
    
    -- Clean up old performance metrics
    DELETE FROM performance_metrics WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;
