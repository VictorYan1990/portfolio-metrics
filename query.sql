-- Alter securities table to drop ISIN column and make symbol the primary key
-- This script will fail if there are any nulls in the symbol column
BEGIN;

-- 1) Ensure symbol is NOT NULL (fails if nulls exist)
ALTER TABLE securities
  ALTER COLUMN symbol SET NOT NULL;

-- 2) Drop existing primary key (if any)
DO $$
DECLARE pk_name text;
BEGIN
  SELECT conname INTO pk_name
  FROM pg_constraint
  WHERE conrelid = 'securities'::regclass AND contype = 'p';
  IF pk_name IS NOT NULL THEN
    EXECUTE format('ALTER TABLE securities DROP CONSTRAINT %I', pk_name);
  END IF;
END $$;

-- 3) Make symbol the primary key
ALTER TABLE securities
  ADD CONSTRAINT securities_pkey PRIMARY KEY (symbol);

-- 4) Drop ISIN column
ALTER TABLE securities
  DROP COLUMN IF EXISTS isin;

COMMIT;


-- Create optimized market_price table
CREATE TABLE market_price (
    date DATE NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    close_price DECIMAL(15,4) NOT NULL,
    -- Optional fields (can be NULL for your 90% use case)
    open_price DECIMAL(15,4),
    high_price DECIMAL(15,4),
    low_price DECIMAL(15,4),
    volume BIGINT,
    adjusted_close DECIMAL(15,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (date, symbol),
    FOREIGN KEY (symbol) REFERENCES securities(symbol) ON DELETE CASCADE
);

-- Create optimized indexes for performance
CREATE INDEX idx_market_price_symbol_date ON market_price(symbol, date);
CREATE INDEX idx_market_price_date ON market_price(date);
CREATE INDEX idx_market_price_symbol ON market_price(symbol);

-- Add sample data for testing
INSERT INTO market_price (date, symbol, close_price, volume) VALUES
('2024-01-17', 'GOOGL', 141.90, 21000000);