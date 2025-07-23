# Payment Service API Documentation

## Overview
This document describes the REST API endpoints for the Payment Service.

## Authentication
All endpoints require JWT token authentication.

## Endpoints

### Earnings
- `GET /earnings/` - Get earnings summary
- `GET /earnings/creator/{creator_id}` - Get creator earnings

### Payments
- `GET /payments/` - List payments
- `POST /payments/` - Create payment
- `GET /payments/{payment_id}` - Get payment details

### Referrals
- `GET /referrals/` - List referrals
- `POST /referrals/` - Create referral

### Payment Schedules
- `GET /schedules/` - List payment schedules
- `POST /schedules/` - Create payment schedule

### Webhooks
- `POST /webhooks/stripe` - Stripe webhook endpoint
- `POST /webhooks/fanbasis` - Fanbasis webhook endpoint
