-- Add missing fields to campaigns.deliverables table
-- These fields are defined in the SQLAlchemy model but missing from the database schema

ALTER TABLE campaigns.deliverables 
ADD COLUMN IF NOT EXISTS title VARCHAR(255),
ADD COLUMN IF NOT EXISTS description TEXT,
ADD COLUMN IF NOT EXISTS content_url TEXT,
ADD COLUMN IF NOT EXISTS content_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS feedback TEXT,
ADD COLUMN IF NOT EXISTS views INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS likes INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS comments INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS shares INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS gmv_generated DECIMAL(12, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS published_at TIMESTAMP WITH TIME ZONE;

-- Update existing rows to have default values for new columns
UPDATE campaigns.deliverables 
SET 
    views = COALESCE(views_count, 0),
    likes = COALESCE(likes_count, 0),
    comments = COALESCE(comments_count, 0),
    shares = COALESCE(shares_count, 0)
WHERE views IS NULL OR likes IS NULL OR comments IS NULL OR shares IS NULL;

-- Drop the old column names if they exist (they were renamed in the model)
ALTER TABLE campaigns.deliverables 
DROP COLUMN IF EXISTS views_count,
DROP COLUMN IF EXISTS likes_count,
DROP COLUMN IF EXISTS comments_count,
DROP COLUMN IF EXISTS shares_count; 