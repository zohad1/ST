-- Insert sample data for testing payment service endpoints
-- Run this script in your PostgreSQL database

-- Test creator ID (from your test user)
DO $$
DECLARE
    creator_id UUID := '4923df90-0ecb-40e4-8114-0b2a97a280a3';
    campaign_id UUID := '550e8400-e29b-41d4-a716-446655440000';
    application_id UUID := '660e8400-e29b-41d4-a716-446655440000';
    earnings_count INTEGER;
    payments_count INTEGER;
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
        );
        
        RAISE NOTICE '✅ Inserted sample earnings for creator %', creator_id;
        RAISE NOTICE '   📊 Base Earnings: $500.00';
        RAISE NOTICE '   💰 GMV Commission: $250.00';
        RAISE NOTICE '   🎁 Bonus Earnings: $100.00';
        RAISE NOTICE '   🔗 Referral Earnings: $50.00';
        RAISE NOTICE '   💵 Total Paid: $300.00';
        RAISE NOTICE '   ⏳ Pending Payment: $600.00';
    ELSE
        RAISE NOTICE '✅ Earnings already exist for creator %', creator_id;
    END IF;
    
    -- Check if payments record already exists
    SELECT COUNT(*) INTO payments_count 
    FROM payments.payments 
    WHERE creator_id = creator_id;
    
    IF payments_count = 0 THEN
        -- Insert sample payments data
        INSERT INTO payments.payments (
            id, creator_id, campaign_id, amount, currency, status, method,
            description, created_at
        ) VALUES 
        (
            gen_random_uuid(), creator_id, campaign_id, 300.00, 'USD', 'completed', 'bank_transfer',
            'Monthly payout for TikTok Shop campaign', NOW() - INTERVAL '30 days'
        ),
        (
            gen_random_uuid(), creator_id, campaign_id, 250.00, 'USD', 'pending', 'paypal',
            'Pending payout for recent campaign', NOW()
        ),
        (
            gen_random_uuid(), creator_id, campaign_id, 150.00, 'USD', 'processing', 'stripe',
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
    
END $$; 