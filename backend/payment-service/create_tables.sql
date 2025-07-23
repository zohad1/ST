-- Create necessary tables for payment service
-- Run this script in your PostgreSQL database

-- Create payments schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS payments;

-- Create payment_status enum if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_status') THEN
        CREATE TYPE payments.payment_status AS ENUM (
            'pending',
            'processing',
            'completed',
            'failed',
            'cancelled',
            'refunded'
        );
    END IF;
END $$;

-- Create payment_type enum if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_type') THEN
        CREATE TYPE payments.payment_type AS ENUM (
            'base_payout',
            'gmv_commission',
            'bonus',
            'leaderboard_bonus',
            'referral_bonus',
            'manual_adjustment'
        );
    END IF;
END $$;

-- Create payout_method enum if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payout_method') THEN
        CREATE TYPE payments.payout_method AS ENUM (
            'stripe',
            'fanbasis',
            'manual',
            'bank_transfer'
        );
    END IF;
END $$;

-- Create payments table
CREATE TABLE IF NOT EXISTS payments.payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creator_id UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns.campaigns(id) ON DELETE SET NULL,
    earning_id UUID REFERENCES payments.creator_earnings(id) ON DELETE SET NULL,
    
    -- Payment details
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    payment_type payments.payment_type NOT NULL,
    payment_method payments.payout_method NOT NULL,
    status payments.payment_status DEFAULT 'pending',
    
    -- Processing details
    transaction_id VARCHAR(255),
    external_reference VARCHAR(255),
    processing_fee DECIMAL(10,2) DEFAULT 0.00,
    
    -- Metadata
    description TEXT,
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    scheduled_for TIMESTAMP WITH TIME ZONE
);

-- Create creator_earnings table
CREATE TABLE IF NOT EXISTS payments.creator_earnings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creator_id UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    campaign_id UUID NOT NULL REFERENCES campaigns.campaigns(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES campaigns.creator_applications(id) ON DELETE CASCADE,
    
    -- Earnings breakdown
    base_earnings DECIMAL(10,2) DEFAULT 0.00,
    gmv_commission DECIMAL(10,2) DEFAULT 0.00,
    bonus_earnings DECIMAL(10,2) DEFAULT 0.00,
    referral_earnings DECIMAL(10,2) DEFAULT 0.00,
    
    -- Computed columns
    total_earnings DECIMAL(10,2) GENERATED ALWAYS AS (
        base_earnings + gmv_commission + bonus_earnings + referral_earnings
    ) STORED,
    total_paid DECIMAL(10,2) DEFAULT 0.00,
    pending_payment DECIMAL(10,2) GENERATED ALWAYS AS (
        (base_earnings + gmv_commission + bonus_earnings + referral_earnings) - total_paid
    ) STORED,
    
    -- Timestamps
    first_earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create payment_schedules table
CREATE TABLE IF NOT EXISTS payments.payment_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creator_id UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    
    -- Schedule details
    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('weekly', 'biweekly', 'monthly')),
    day_of_week INTEGER CHECK (day_of_week >= 0 AND day_of_week <= 6), -- 0=Sunday, 6=Saturday
    day_of_month INTEGER CHECK (day_of_month >= 1 AND day_of_month <= 31),
    minimum_amount DECIMAL(10,2) DEFAULT 0.00,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    next_payout_date TIMESTAMP WITH TIME ZONE
);

-- Create referrals table
CREATE TABLE IF NOT EXISTS payments.referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_id UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    referred_id UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    
    -- Referral details
    commission_rate DECIMAL(5,4) DEFAULT 0.0500, -- 5% default
    total_earned DECIMAL(10,2) DEFAULT 0.00,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(referrer_id, referred_id)
);

-- Add foreign key relationship from payments to creator_earnings
ALTER TABLE payments.payments 
ADD CONSTRAINT fk_payments_earning 
FOREIGN KEY (earning_id) REFERENCES payments.creator_earnings(id) ON DELETE SET NULL;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_payments_creator_id ON payments.payments(creator_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments.payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments.payments(created_at);

CREATE INDEX IF NOT EXISTS idx_creator_earnings_creator_id ON payments.creator_earnings(creator_id);
CREATE INDEX IF NOT EXISTS idx_creator_earnings_campaign_id ON payments.creator_earnings(campaign_id);

CREATE INDEX IF NOT EXISTS idx_payment_schedules_creator_id ON payments.payment_schedules(creator_id);
CREATE INDEX IF NOT EXISTS idx_payment_schedules_active ON payments.payment_schedules(is_active);

CREATE INDEX IF NOT EXISTS idx_referrals_referrer_id ON payments.referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referred_id ON payments.referrals(referred_id);

-- Insert sample data for testing
DO $$
DECLARE
    creator_id UUID := '4923df90-0ecb-40e4-8114-0b2a97a280a3';
    campaign_id UUID := '550e8400-e29b-41d4-a716-446655440000';
    application_id UUID := '660e8400-e29b-41d4-a716-446655440000';
    earnings_count INTEGER;
    payments_count INTEGER;
BEGIN
    -- Check if sample data already exists
    SELECT COUNT(*) INTO earnings_count FROM payments.creator_earnings WHERE creator_id = creator_id;
    SELECT COUNT(*) INTO payments_count FROM payments.payments WHERE creator_id = creator_id;
    
    IF earnings_count = 0 THEN
        -- Insert sample earnings
        INSERT INTO payments.creator_earnings (
            id, creator_id, campaign_id, application_id,
            base_earnings, gmv_commission, bonus_earnings, referral_earnings,
            total_paid, first_earned_at, last_updated
        ) VALUES (
            gen_random_uuid(), creator_id, campaign_id, application_id,
            500.00, 250.00, 100.00, 50.00,
            300.00, NOW(), NOW()
        );
        
        RAISE NOTICE '✅ Inserted sample earnings for creator %', creator_id;
    ELSE
        RAISE NOTICE '✅ Earnings already exist for creator %', creator_id;
    END IF;
    
    IF payments_count = 0 THEN
        -- Insert sample payments
        INSERT INTO payments.payments (
            id, creator_id, campaign_id, amount, payment_type, payment_method, status,
            description, created_at
        ) VALUES 
        (
            gen_random_uuid(), creator_id, campaign_id, 300.00, 'base_payout'::payments.payment_type, 'bank_transfer'::payments.payout_method, 'completed'::payments.payment_status,
            'Monthly payout for TikTok Shop campaign', NOW() - INTERVAL '30 days'
        ),
        (
            gen_random_uuid(), creator_id, campaign_id, 250.00, 'bonus'::payments.payment_type, 'stripe'::payments.payout_method, 'pending'::payments.payment_status,
            'Pending payout for recent campaign', NOW()
        );
        
        RAISE NOTICE '✅ Inserted sample payments for creator %', creator_id;
    ELSE
        RAISE NOTICE '✅ Payments already exist for creator %', creator_id;
    END IF;
END $$; 