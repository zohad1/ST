-- Fix enum types and insert sample data for payment service
-- Run this script in your PostgreSQL database

-- 1. Drop existing enum types if they exist (to recreate them correctly)
DO $$
BEGIN
    -- Drop payment_status enum if it exists
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_status') THEN
        DROP TYPE payments.payment_status CASCADE;
    END IF;
    
    -- Drop payment_method enum if it exists  
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_method') THEN
        DROP TYPE payments.payment_method CASCADE;
    END IF;
    
    -- Drop payment_type enum if it exists
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_type') THEN
        DROP TYPE payments.payment_type CASCADE;
    END IF;
END $$;

-- 2. Create the correct enum types that match the Python enums
CREATE TYPE payments.payment_status AS ENUM (
    'pending',
    'processing', 
    'completed',
    'failed',
    'cancelled',
    'refunded'
);

CREATE TYPE payments.payment_type AS ENUM (
    'base_payout',
    'gmv_commission',
    'bonus',
    'leaderboard_bonus', 
    'referral_bonus',
    'manual_adjustment'
);

CREATE TYPE payments.payout_method AS ENUM (
    'stripe',
    'fanbasis',
    'manual',
    'bank_transfer'
);

-- 3. Update the payments table to use the correct enum types
ALTER TABLE payments.payments 
    ALTER COLUMN status TYPE payments.payment_status USING status::text::payments.payment_status,
    ALTER COLUMN payment_type TYPE payments.payment_type USING payment_type::text::payments.payment_type,
    ALTER COLUMN payment_method TYPE payments.payout_method USING payment_method::text::payments.payout_method;

-- 4. Insert sample data with correct enum values
DO $$
DECLARE
    creator_id UUID := '4923df90-0ecb-40e4-8114-0b2a97a280a3';
    campaign_id UUID := '550e8400-e29b-41d4-a716-446655440000';
    application_id UUID := '660e8400-e29b-41d4-a716-446655440000';
    earnings_count INTEGER;
    payments_count INTEGER;
    earning_id UUID;
BEGIN
    -- Check if earnings record already exists
    SELECT COUNT(*) INTO earnings_count 
    FROM payments.creator_earnings 
    WHERE creator_id = creator_id;
    
    IF earnings_count = 0 THEN
        -- Insert sample earnings data
        INSERT INTO payments.creator_earnings (
            id, creator_id, campaign_id, application_id,
            base_earnings, gmv_commission, bonus_earnings, referral_earnings,
            total_paid, first_earned_at, last_updated
        ) VALUES (
            gen_random_uuid(), creator_id, campaign_id, application_id,
            500.00, 250.00, 100.00, 50.00,
            300.00, NOW(), NOW()
        ) RETURNING id INTO earning_id;
        
        RAISE NOTICE '✅ Inserted sample earnings for creator %', creator_id;
        RAISE NOTICE '   📊 Base Earnings: $500.00';
        RAISE NOTICE '   💰 GMV Commission: $250.00';
        RAISE NOTICE '   🎁 Bonus Earnings: $100.00';
        RAISE NOTICE '   🔗 Referral Earnings: $50.00';
        RAISE NOTICE '   💵 Total Paid: $300.00';
        RAISE NOTICE '   ⏳ Pending Payment: $600.00';
    ELSE
        -- Get existing earning ID
        SELECT id INTO earning_id FROM payments.creator_earnings WHERE creator_id = creator_id LIMIT 1;
        RAISE NOTICE '✅ Earnings already exist for creator %', creator_id;
    END IF;
    
    -- Check if payments record already exists
    SELECT COUNT(*) INTO payments_count 
    FROM payments.payments 
    WHERE creator_id = creator_id;
    
    IF payments_count = 0 THEN
        -- Insert sample payments data with correct enum values
        INSERT INTO payments.payments (
            id, creator_id, campaign_id, earning_id, amount, payment_type, payment_method, status,
            description, created_at
        ) VALUES 
        (
            gen_random_uuid(), creator_id, campaign_id, earning_id, 300.00, 
            'base_payout'::payments.payment_type, 'bank_transfer'::payments.payout_method, 'completed'::payments.payment_status,
            'Monthly payout for TikTok Shop campaign', NOW() - INTERVAL '30 days'
        ),
        (
            gen_random_uuid(), creator_id, campaign_id, earning_id, 250.00,
            'bonus'::payments.payment_type, 'stripe'::payments.payout_method, 'pending'::payments.payment_status,
            'Pending payout for recent campaign', NOW()
        ),
        (
            gen_random_uuid(), creator_id, campaign_id, earning_id, 150.00,
            'gmv_commission'::payments.payment_type, 'stripe'::payments.payout_method, 'processing'::payments.payment_status,
            'Processing payment for bonus earnings', NOW() - INTERVAL '7 days'
        );
        
        RAISE NOTICE '✅ Inserted sample payments for creator %', creator_id;
        RAISE NOTICE '   💳 Completed: $300.00';
        RAISE NOTICE '   ⏳ Pending: $250.00';
        RAISE NOTICE '   🔄 Processing: $150.00';
    ELSE
        RAISE NOTICE '✅ Payments already exist for creator %', creator_id;
    END IF;
    
    -- Show summary
    RAISE NOTICE '';
    RAISE NOTICE '📊 Data Summary:';
    RAISE NOTICE '   Creator ID: %', creator_id;
    RAISE NOTICE '   Campaign ID: %', campaign_id;
    RAISE NOTICE '   Application ID: %', application_id;
    RAISE NOTICE '   Earning ID: %', earning_id;
    
END $$; 