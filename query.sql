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


