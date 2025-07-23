--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

-- Started on 2025-07-19 12:21:56

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 12 (class 2615 OID 20554)
-- Name: analytics; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA analytics;


ALTER SCHEMA analytics OWNER TO postgres;

--
-- TOC entry 9 (class 2615 OID 20551)
-- Name: campaigns; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA campaigns;


ALTER SCHEMA campaigns OWNER TO postgres;

--
-- TOC entry 11 (class 2615 OID 20553)
-- Name: integrations; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA integrations;


ALTER SCHEMA integrations OWNER TO postgres;

--
-- TOC entry 10 (class 2615 OID 20552)
-- Name: payments; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA payments;


ALTER SCHEMA payments OWNER TO postgres;

--
-- TOC entry 8 (class 2615 OID 20550)
-- Name: users; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA users;


ALTER SCHEMA users OWNER TO postgres;

--
-- TOC entry 2 (class 3079 OID 21129)
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- TOC entry 5499 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- TOC entry 3 (class 3079 OID 21436)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 5500 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 1096 (class 1247 OID 22594)
-- Name: application_status; Type: TYPE; Schema: campaigns; Owner: postgres
--

CREATE TYPE campaigns.application_status AS ENUM (
    'pending',
    'approved',
    'rejected',
    'waitlisted'
);


ALTER TYPE campaigns.application_status OWNER TO postgres;

--
-- TOC entry 1093 (class 1247 OID 22582)
-- Name: campaign_status; Type: TYPE; Schema: campaigns; Owner: postgres
--

CREATE TYPE campaigns.campaign_status AS ENUM (
    'draft',
    'active',
    'paused',
    'completed',
    'cancelled'
);


ALTER TYPE campaigns.campaign_status OWNER TO postgres;

--
-- TOC entry 1081 (class 1247 OID 22527)
-- Name: campaign_type; Type: TYPE; Schema: campaigns; Owner: postgres
--

CREATE TYPE campaigns.campaign_type AS ENUM (
    'product',
    'brand_awareness',
    'performance',
    'content_creation'
);


ALTER TYPE campaigns.campaign_type OWNER TO postgres;

--
-- TOC entry 1099 (class 1247 OID 22604)
-- Name: deliverable_status; Type: TYPE; Schema: campaigns; Owner: postgres
--

CREATE TYPE campaigns.deliverable_status AS ENUM (
    'pending',
    'submitted',
    'approved',
    'rejected',
    'overdue'
);


ALTER TYPE campaigns.deliverable_status OWNER TO postgres;

--
-- TOC entry 1084 (class 1247 OID 22536)
-- Name: payout_model; Type: TYPE; Schema: campaigns; Owner: postgres
--

CREATE TYPE campaigns.payout_model AS ENUM (
    'fixed_per_post',
    'gmv_commission',
    'hybrid',
    'retainer_gmv'
);


ALTER TYPE campaigns.payout_model OWNER TO postgres;

--
-- TOC entry 1087 (class 1247 OID 22546)
-- Name: tracking_method; Type: TYPE; Schema: campaigns; Owner: postgres
--

CREATE TYPE campaigns.tracking_method AS ENUM (
    'hashtag',
    'product_link',
    'spark_code'
);


ALTER TYPE campaigns.tracking_method OWNER TO postgres;

--
-- TOC entry 1057 (class 1247 OID 22270)
-- Name: integration_status; Type: TYPE; Schema: integrations; Owner: postgres
--

CREATE TYPE integrations.integration_status AS ENUM (
    'active',
    'inactive',
    'error',
    'pending_setup'
);


ALTER TYPE integrations.integration_status OWNER TO postgres;

--
-- TOC entry 1054 (class 1247 OID 22259)
-- Name: integration_type; Type: TYPE; Schema: integrations; Owner: postgres
--

CREATE TYPE integrations.integration_type AS ENUM (
    'tiktok_shop',
    'discord',
    'sendblue',
    'stripe',
    'fanbasis'
);


ALTER TYPE integrations.integration_type OWNER TO postgres;

--
-- TOC entry 1033 (class 1247 OID 22123)
-- Name: payment_status; Type: TYPE; Schema: payments; Owner: postgres
--

CREATE TYPE payments.payment_status AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed',
    'cancelled',
    'refunded'
);


ALTER TYPE payments.payment_status OWNER TO postgres;

--
-- TOC entry 1036 (class 1247 OID 22136)
-- Name: payment_type; Type: TYPE; Schema: payments; Owner: postgres
--

CREATE TYPE payments.payment_type AS ENUM (
    'base_payout',
    'gmv_commission',
    'bonus',
    'leaderboard_bonus',
    'referral_bonus',
    'manual_adjustment'
);


ALTER TYPE payments.payment_type OWNER TO postgres;

--
-- TOC entry 1039 (class 1247 OID 22150)
-- Name: payout_method; Type: TYPE; Schema: payments; Owner: postgres
--

CREATE TYPE payments.payout_method AS ENUM (
    'stripe',
    'fanbasis',
    'manual',
    'bank_transfer'
);


ALTER TYPE payments.payout_method OWNER TO postgres;

--
-- TOC entry 967 (class 1247 OID 20666)
-- Name: applicationstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.applicationstatus AS ENUM (
    'pending',
    'approved',
    'rejected',
    'waitlisted'
);


ALTER TYPE public.applicationstatus OWNER TO postgres;

--
-- TOC entry 940 (class 1247 OID 20565)
-- Name: campaignstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.campaignstatus AS ENUM (
    'draft',
    'active',
    'paused',
    'completed',
    'cancelled'
);


ALTER TYPE public.campaignstatus OWNER TO postgres;

--
-- TOC entry 1090 (class 1247 OID 22572)
-- Name: campaigntype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.campaigntype AS ENUM (
    'PRODUCT',
    'BRAND_AWARENESS',
    'PERFORMANCE',
    'CONTENT_CREATION'
);


ALTER TYPE public.campaigntype OWNER TO postgres;

--
-- TOC entry 973 (class 1247 OID 20703)
-- Name: deliverablestatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.deliverablestatus AS ENUM (
    'pending',
    'submitted',
    'approved',
    'rejected',
    'overdue'
);


ALTER TYPE public.deliverablestatus OWNER TO postgres;

--
-- TOC entry 955 (class 1247 OID 20623)
-- Name: gendertype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.gendertype AS ENUM (
    'male',
    'female',
    'non_binary',
    'prefer_not_to_say'
);


ALTER TYPE public.gendertype OWNER TO postgres;

--
-- TOC entry 1000 (class 1247 OID 23499)
-- Name: payment_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.payment_status AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed',
    'cancelled',
    'refunded'
);


ALTER TYPE public.payment_status OWNER TO postgres;

--
-- TOC entry 1003 (class 1247 OID 23512)
-- Name: payment_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.payment_type AS ENUM (
    'base_payout',
    'gmv_commission',
    'bonus',
    'leaderboard_bonus',
    'referral_bonus',
    'manual_adjustment'
);


ALTER TYPE public.payment_type OWNER TO postgres;

--
-- TOC entry 1006 (class 1247 OID 23526)
-- Name: payout_method; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.payout_method AS ENUM (
    'stripe',
    'fanbasis',
    'manual',
    'bank_transfer'
);


ALTER TYPE public.payout_method OWNER TO postgres;

--
-- TOC entry 943 (class 1247 OID 20576)
-- Name: payoutmodel; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.payoutmodel AS ENUM (
    'fixed_per_post',
    'gmv_commission',
    'hybrid',
    'retainer_gmv'
);


ALTER TYPE public.payoutmodel OWNER TO postgres;

--
-- TOC entry 946 (class 1247 OID 20586)
-- Name: trackingmethod; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.trackingmethod AS ENUM (
    'hashtag',
    'product_link',
    'spark_code'
);


ALTER TYPE public.trackingmethod OWNER TO postgres;

--
-- TOC entry 1105 (class 1247 OID 22804)
-- Name: badge_type; Type: TYPE; Schema: users; Owner: postgres
--

CREATE TYPE users.badge_type AS ENUM (
    'gmv_1k',
    'gmv_10k',
    'gmv_50k',
    'gmv_100k',
    'gmv_500k',
    'gmv_1m',
    'top_creator',
    'verified',
    'rising_star'
);


ALTER TYPE users.badge_type OWNER TO postgres;

--
-- TOC entry 1030 (class 1247 OID 23149)
-- Name: gender_type; Type: TYPE; Schema: users; Owner: postgres
--

CREATE TYPE users.gender_type AS ENUM (
    'MALE',
    'FEMALE',
    'OTHER',
    'PREFER_NOT_TO_SAY'
);


ALTER TYPE users.gender_type OWNER TO postgres;

--
-- TOC entry 1102 (class 1247 OID 22790)
-- Name: token_type; Type: TYPE; Schema: users; Owner: postgres
--

CREATE TYPE users.token_type AS ENUM (
    'email_verification',
    'password_reset',
    'oauth',
    'refresh',
    'api_key',
    'access'
);


ALTER TYPE users.token_type OWNER TO postgres;

--
-- TOC entry 1027 (class 1247 OID 23115)
-- Name: user_role; Type: TYPE; Schema: users; Owner: postgres
--

CREATE TYPE users.user_role AS ENUM (
    'agency',
    'creator',
    'brand',
    'admin'
);


ALTER TYPE users.user_role OWNER TO postgres;

--
-- TOC entry 318 (class 1255 OID 22568)
-- Name: update_campaign_updated_at(); Type: FUNCTION; Schema: campaigns; Owner: postgres
--

CREATE FUNCTION campaigns.update_campaign_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION campaigns.update_campaign_updated_at() OWNER TO postgres;

--
-- TOC entry 319 (class 1255 OID 23597)
-- Name: update_last_updated_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_last_updated_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_last_updated_column() OWNER TO postgres;

--
-- TOC entry 307 (class 1255 OID 21262)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 241 (class 1259 OID 22391)
-- Name: campaign_performance_daily; Type: TABLE; Schema: analytics; Owner: postgres
--

CREATE TABLE analytics.campaign_performance_daily (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    campaign_id uuid NOT NULL,
    date_snapshot date NOT NULL,
    total_creators integer DEFAULT 0,
    active_creators integer DEFAULT 0,
    new_applications integer DEFAULT 0,
    approved_applications integer DEFAULT 0,
    posts_submitted integer DEFAULT 0,
    posts_approved integer DEFAULT 0,
    total_views bigint DEFAULT 0,
    total_likes integer DEFAULT 0,
    total_comments integer DEFAULT 0,
    total_shares integer DEFAULT 0,
    total_gmv numeric(12,2) DEFAULT 0.00,
    total_commissions numeric(10,2) DEFAULT 0.00,
    total_payouts numeric(10,2) DEFAULT 0.00,
    avg_engagement_rate numeric(5,2) DEFAULT 0.00,
    conversion_rate numeric(5,2) DEFAULT 0.00,
    cost_per_acquisition numeric(10,2) DEFAULT 0.00,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE analytics.campaign_performance_daily OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 22421)
-- Name: creator_performance; Type: TABLE; Schema: analytics; Owner: postgres
--

CREATE TABLE analytics.creator_performance (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    creator_id uuid NOT NULL,
    campaign_id uuid,
    total_posts integer DEFAULT 0,
    completed_deliverables integer DEFAULT 0,
    on_time_deliverables integer DEFAULT 0,
    total_gmv numeric(12,2) DEFAULT 0.00,
    avg_views_per_post numeric(12,2) DEFAULT 0.00,
    avg_engagement_rate numeric(5,2) DEFAULT 0.00,
    consistency_score numeric(3,2) DEFAULT 0.00,
    reliability_rating numeric(2,1) DEFAULT 0.0,
    last_calculated timestamp with time zone DEFAULT now()
);


ALTER TABLE analytics.creator_performance OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 20610)
-- Name: campaign_products; Type: TABLE; Schema: campaigns; Owner: postgres
--

CREATE TABLE campaigns.campaign_products (
    id uuid NOT NULL,
    campaign_id uuid NOT NULL,
    tiktok_product_id character varying(100) NOT NULL,
    product_name character varying(255),
    product_url text NOT NULL,
    product_price numeric(10,2),
    is_primary boolean,
    created_at timestamp with time zone
);


ALTER TABLE campaigns.campaign_products OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 20631)
-- Name: campaign_segments; Type: TABLE; Schema: campaigns; Owner: postgres
--

CREATE TABLE campaigns.campaign_segments (
    id uuid NOT NULL,
    campaign_id uuid NOT NULL,
    segment_name character varying(100) NOT NULL,
    segment_description text,
    gender_filter public.gendertype[],
    age_min integer,
    age_max integer,
    min_followers integer,
    max_followers integer,
    required_niches character varying(100)[],
    location_filter character varying(100)[],
    max_creators_in_segment integer,
    custom_payout_per_post numeric(10,2),
    custom_deliverable_count integer,
    created_at timestamp with time zone
);


ALTER TABLE campaigns.campaign_segments OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 20593)
-- Name: campaigns; Type: TABLE; Schema: campaigns; Owner: postgres
--

CREATE TABLE campaigns.campaigns (
    id uuid NOT NULL,
    agency_id uuid NOT NULL,
    brand_id uuid,
    name character varying(255) NOT NULL,
    description text,
    thumbnail_url text,
    status campaigns.campaign_status,
    payout_model campaigns.payout_model NOT NULL,
    tracking_method campaigns.tracking_method NOT NULL,
    start_date timestamp with time zone,
    end_date timestamp with time zone,
    grace_period_days integer,
    is_rolling_30_day boolean DEFAULT false NOT NULL,
    max_creators integer,
    min_deliverables_per_creator integer,
    require_approval boolean,
    require_discord_join boolean DEFAULT false NOT NULL,
    discord_server_id character varying(100),
    discord_role_name character varying(100),
    base_payout_per_post numeric(10,2),
    gmv_commission_rate numeric(5,2),
    retainer_amount numeric(10,2),
    total_budget numeric(12,2) DEFAULT 0.00,
    spent_amount numeric(12,2) DEFAULT 0.00 NOT NULL,
    hashtag character varying(100),
    target_gmv numeric(12,2),
    target_posts integer,
    target_views integer,
    referral_bonus_enabled boolean DEFAULT false NOT NULL,
    referral_bonus_amount numeric(10,2),
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    current_gmv numeric(12,2) DEFAULT 0.00,
    current_creators integer DEFAULT 0,
    current_posts integer DEFAULT 0,
    total_views bigint DEFAULT 0,
    total_engagement bigint DEFAULT 0,
    type campaigns.campaign_type DEFAULT 'performance'::campaigns.campaign_type NOT NULL,
    budget numeric(12,2) DEFAULT 0.00,
    target_creators integer,
    tiktok_product_links jsonb
);


ALTER TABLE campaigns.campaigns OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 23032)
-- Name: campaigns_backup; Type: TABLE; Schema: campaigns; Owner: postgres
--

CREATE TABLE campaigns.campaigns_backup (
    id uuid,
    agency_id uuid,
    brand_id uuid,
    name character varying(255),
    description text,
    thumbnail_url text,
    status campaigns.campaign_status,
    payout_model campaigns.payout_model,
    tracking_method campaigns.tracking_method,
    start_date timestamp with time zone,
    end_date timestamp with time zone,
    grace_period_days integer,
    is_rolling_30_day boolean,
    max_creators integer,
    min_deliverables_per_creator integer,
    require_approval boolean,
    require_discord_join boolean,
    discord_server_id character varying(100),
    discord_role_name character varying(100),
    base_payout_per_post numeric(10,2),
    gmv_commission_rate numeric(5,2),
    retainer_amount numeric(10,2),
    total_budget numeric(12,2),
    spent_amount numeric(12,2),
    hashtag character varying(100),
    target_gmv numeric(12,2),
    target_posts integer,
    target_views integer,
    referral_bonus_enabled boolean,
    referral_bonus_amount numeric(10,2),
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    current_gmv numeric(12,2),
    current_creators integer,
    current_posts integer,
    total_views bigint,
    total_engagement bigint,
    type campaigns.campaign_type,
    budget numeric(12,2),
    target_creators integer,
    tiktok_product_links jsonb
);


ALTER TABLE campaigns.campaigns_backup OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 20675)
-- Name: creator_applications; Type: TABLE; Schema: campaigns; Owner: postgres
--

CREATE TABLE campaigns.creator_applications (
    id uuid NOT NULL,
    campaign_id uuid NOT NULL,
    creator_id uuid NOT NULL,
    segment_id uuid,
    status campaigns.application_status,
    applied_at timestamp with time zone,
    reviewed_at timestamp with time zone,
    reviewed_by uuid,
    application_data jsonb,
    application_message text,
    response_message text,
    follower_count integer DEFAULT 0,
    engagement_rate numeric(5,2) DEFAULT 0.00,
    previous_gmv numeric(12,2) DEFAULT 0.00,
    rejection_reason text,
    review_notes text
);


ALTER TABLE campaigns.creator_applications OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 20713)
-- Name: deliverables; Type: TABLE; Schema: campaigns; Owner: postgres
--

CREATE TABLE campaigns.deliverables (
    id uuid NOT NULL,
    application_id uuid NOT NULL,
    deliverable_number integer NOT NULL,
    due_date timestamp with time zone,
    status campaigns.deliverable_status,
    tiktok_post_url text,
    post_caption text,
    hashtags_used character varying(255)[],
    submitted_at timestamp with time zone,
    approved_at timestamp with time zone,
    approved_by uuid,
    agency_feedback text,
    revision_requested boolean,
    revision_notes text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    title character varying(255) DEFAULT 'Deliverable'::character varying,
    description text,
    content_url character varying(500),
    content_type character varying(50),
    content_duration integer,
    views integer DEFAULT 0,
    likes integer DEFAULT 0,
    comments integer DEFAULT 0,
    shares integer DEFAULT 0,
    gmv_generated numeric(12,2) DEFAULT 0.00,
    published_at timestamp with time zone,
    feedback text,
    campaign_id uuid,
    creator_id uuid
);


ALTER TABLE campaigns.deliverables OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 20643)
-- Name: gmv_bonus_tiers; Type: TABLE; Schema: campaigns; Owner: postgres
--

CREATE TABLE campaigns.gmv_bonus_tiers (
    id uuid NOT NULL,
    campaign_id uuid NOT NULL,
    tier_name character varying(100) NOT NULL,
    min_gmv numeric(12,2) NOT NULL,
    max_gmv numeric(12,2),
    bonus_type character varying(20) NOT NULL,
    bonus_value numeric(10,2) NOT NULL,
    created_at timestamp with time zone
);


ALTER TABLE campaigns.gmv_bonus_tiers OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 20653)
-- Name: leaderboard_bonuses; Type: TABLE; Schema: campaigns; Owner: postgres
--

CREATE TABLE campaigns.leaderboard_bonuses (
    id uuid NOT NULL,
    campaign_id uuid NOT NULL,
    position_start integer NOT NULL,
    position_end integer NOT NULL,
    bonus_amount numeric(10,2) NOT NULL,
    metric_type character varying(20) NOT NULL,
    description text,
    created_at timestamp with time zone
);


ALTER TABLE campaigns.leaderboard_bonuses OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 22366)
-- Name: communication_logs; Type: TABLE; Schema: integrations; Owner: postgres
--

CREATE TABLE integrations.communication_logs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    sender_id uuid NOT NULL,
    recipient_id uuid,
    campaign_id uuid,
    communication_type character varying(20) NOT NULL,
    subject character varying(255),
    message_content text NOT NULL,
    sent_at timestamp with time zone DEFAULT now(),
    delivered_at timestamp with time zone,
    read_at timestamp with time zone,
    external_message_id character varying(255),
    delivery_status character varying(20) DEFAULT 'sent'::character varying,
    failure_reason text
);


ALTER TABLE integrations.communication_logs OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 22341)
-- Name: creator_discord_roles; Type: TABLE; Schema: integrations; Owner: postgres
--

CREATE TABLE integrations.creator_discord_roles (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    creator_id uuid NOT NULL,
    campaign_id uuid NOT NULL,
    discord_role_id uuid NOT NULL,
    assigned_at timestamp with time zone DEFAULT now(),
    removed_at timestamp with time zone,
    is_active boolean DEFAULT true
);


ALTER TABLE integrations.creator_discord_roles OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 22327)
-- Name: discord_roles; Type: TABLE; Schema: integrations; Owner: postgres
--

CREATE TABLE integrations.discord_roles (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    campaign_id uuid NOT NULL,
    discord_server_id character varying(100) NOT NULL,
    discord_role_id character varying(100) NOT NULL,
    role_name character varying(100) NOT NULL,
    auto_assign_on_approval boolean DEFAULT true,
    auto_remove_on_completion boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE integrations.discord_roles OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 22279)
-- Name: external_integrations; Type: TABLE; Schema: integrations; Owner: postgres
--

CREATE TABLE integrations.external_integrations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    integration_type integrations.integration_type NOT NULL,
    status integrations.integration_status DEFAULT 'pending_setup'::integrations.integration_status,
    api_key_encrypted text,
    api_secret_encrypted text,
    access_token_encrypted text,
    refresh_token_encrypted text,
    settings jsonb DEFAULT '{}'::jsonb,
    last_sync_at timestamp with time zone,
    last_error text,
    error_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE integrations.external_integrations OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 22299)
-- Name: tiktok_shop_sales; Type: TABLE; Schema: integrations; Owner: postgres
--

CREATE TABLE integrations.tiktok_shop_sales (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    campaign_id uuid NOT NULL,
    creator_id uuid NOT NULL,
    deliverable_id uuid,
    tiktok_order_id character varying(255) NOT NULL,
    tiktok_product_id character varying(255) NOT NULL,
    sale_amount numeric(10,2) NOT NULL,
    commission_amount numeric(10,2) NOT NULL,
    currency character varying(3) DEFAULT 'USD'::character varying,
    attributed_post_url text,
    attribution_method character varying(50),
    attribution_confidence numeric(3,2) DEFAULT 1.00,
    sale_date timestamp with time zone NOT NULL,
    imported_at timestamp with time zone DEFAULT now()
);


ALTER TABLE integrations.tiktok_shop_sales OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 22159)
-- Name: creator_earnings; Type: TABLE; Schema: payments; Owner: postgres
--

CREATE TABLE payments.creator_earnings (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    creator_id uuid NOT NULL,
    campaign_id uuid NOT NULL,
    application_id uuid NOT NULL,
    base_earnings numeric(10,2) DEFAULT 0.00,
    gmv_commission numeric(10,2) DEFAULT 0.00,
    bonus_earnings numeric(10,2) DEFAULT 0.00,
    referral_earnings numeric(10,2) DEFAULT 0.00,
    total_earnings numeric(10,2) GENERATED ALWAYS AS ((((base_earnings + gmv_commission) + bonus_earnings) + referral_earnings)) STORED,
    total_paid numeric(10,2) DEFAULT 0.00,
    pending_payment numeric(10,2) GENERATED ALWAYS AS (((((base_earnings + gmv_commission) + bonus_earnings) + referral_earnings) - total_paid)) STORED,
    first_earned_at timestamp with time zone DEFAULT now(),
    last_updated timestamp with time zone DEFAULT now()
);


ALTER TABLE payments.creator_earnings OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 22214)
-- Name: payment_schedules; Type: TABLE; Schema: payments; Owner: postgres
--

CREATE TABLE payments.payment_schedules (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    campaign_id uuid NOT NULL,
    schedule_name character varying(100) NOT NULL,
    is_automated boolean DEFAULT true,
    trigger_on_deliverable_completion boolean DEFAULT false,
    trigger_on_gmv_milestone boolean DEFAULT false,
    gmv_milestone_amount numeric(12,2),
    trigger_on_campaign_completion boolean DEFAULT false,
    payment_delay_days integer DEFAULT 0,
    minimum_payout_amount numeric(10,2) DEFAULT 0.00,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE payments.payment_schedules OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 22189)
-- Name: payments; Type: TABLE; Schema: payments; Owner: postgres
--

CREATE TABLE payments.payments (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    creator_id uuid NOT NULL,
    campaign_id uuid,
    earning_id uuid,
    amount numeric(10,2) NOT NULL,
    payment_type payments.payment_type NOT NULL,
    payment_method payments.payout_method NOT NULL,
    status payments.payment_status DEFAULT 'pending'::payments.payment_status,
    stripe_payment_intent_id character varying(255),
    fanbasis_transaction_id character varying(255),
    external_transaction_id character varying(255),
    description text,
    failure_reason text,
    initiated_at timestamp with time zone DEFAULT now(),
    processed_at timestamp with time zone,
    completed_at timestamp with time zone,
    failed_at timestamp with time zone
);


ALTER TABLE payments.payments OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 22232)
-- Name: referrals; Type: TABLE; Schema: payments; Owner: postgres
--

CREATE TABLE payments.referrals (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    referrer_id uuid NOT NULL,
    referred_id uuid NOT NULL,
    campaign_id uuid,
    referral_code character varying(50),
    referred_at timestamp with time zone DEFAULT now(),
    first_campaign_joined_at timestamp with time zone,
    bonus_earned numeric(10,2) DEFAULT 0.00,
    bonus_paid numeric(10,2) DEFAULT 0.00
);


ALTER TABLE payments.referrals OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 20545)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- TOC entry 249 (class 1259 OID 23433)
-- Name: auth_code_usage; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_code_usage (
    id character varying NOT NULL,
    auth_code character varying,
    used_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.auth_code_usage OWNER TO postgres;

--
-- TOC entry 254 (class 1259 OID 23535)
-- Name: creator_earnings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.creator_earnings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    creator_id character varying(36) NOT NULL,
    campaign_id character varying(36) NOT NULL,
    application_id character varying(36) NOT NULL,
    base_earnings numeric(10,2) DEFAULT 0.00,
    gmv_commission numeric(10,2) DEFAULT 0.00,
    bonus_earnings numeric(10,2) DEFAULT 0.00,
    referral_earnings numeric(10,2) DEFAULT 0.00,
    total_paid numeric(10,2) DEFAULT 0.00,
    first_earned_at timestamp with time zone DEFAULT now(),
    last_updated timestamp with time zone DEFAULT now()
);


ALTER TABLE public.creator_earnings OWNER TO postgres;

--
-- TOC entry 258 (class 1259 OID 23599)
-- Name: creator_earnings_summary; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.creator_earnings_summary AS
 SELECT creator_id,
    count(DISTINCT campaign_id) AS total_campaigns,
    sum((((base_earnings + gmv_commission) + bonus_earnings) + referral_earnings)) AS total_earnings,
    sum(total_paid) AS total_paid,
    sum(((((base_earnings + gmv_commission) + bonus_earnings) + referral_earnings) - total_paid)) AS pending_payment,
    max(last_updated) AS last_updated
   FROM public.creator_earnings
  GROUP BY creator_id;


ALTER VIEW public.creator_earnings_summary OWNER TO postgres;

--
-- TOC entry 256 (class 1259 OID 23567)
-- Name: payment_schedules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payment_schedules (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    campaign_id character varying(36) NOT NULL,
    schedule_name character varying(100) NOT NULL,
    is_automated boolean DEFAULT true,
    trigger_on_deliverable_completion boolean DEFAULT false,
    trigger_on_gmv_milestone boolean DEFAULT false,
    gmv_milestone_amount numeric(12,2),
    trigger_on_campaign_completion boolean DEFAULT false,
    payment_delay_days integer DEFAULT 0,
    minimum_payout_amount numeric(10,2) DEFAULT 0.00,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.payment_schedules OWNER TO postgres;

--
-- TOC entry 255 (class 1259 OID 23550)
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    creator_id character varying(36) NOT NULL,
    campaign_id character varying(36),
    earning_id uuid,
    amount numeric(10,2) NOT NULL,
    payment_type public.payment_type NOT NULL,
    payment_method public.payout_method NOT NULL,
    status public.payment_status DEFAULT 'pending'::public.payment_status,
    stripe_payment_intent_id character varying(255),
    fanbasis_transaction_id character varying(255),
    external_transaction_id character varying(255),
    description text,
    failure_reason text,
    initiated_at timestamp with time zone DEFAULT now(),
    processed_at timestamp with time zone,
    completed_at timestamp with time zone,
    failed_at timestamp with time zone,
    new_column_example text
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- TOC entry 257 (class 1259 OID 23580)
-- Name: referrals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.referrals (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    referrer_id character varying(36) NOT NULL,
    referred_id character varying(36) NOT NULL,
    campaign_id character varying(36),
    referral_code character varying(50),
    referred_at timestamp with time zone DEFAULT now(),
    first_campaign_joined_at timestamp with time zone,
    bonus_earned numeric(10,2) DEFAULT 0.00,
    bonus_paid numeric(10,2) DEFAULT 0.00
);


ALTER TABLE public.referrals OWNER TO postgres;

--
-- TOC entry 252 (class 1259 OID 23470)
-- Name: sync_operations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sync_operations (
    id character varying NOT NULL,
    shop_id character varying,
    entity_type character varying,
    sync_mode character varying,
    status character varying,
    started_at timestamp with time zone DEFAULT now(),
    completed_at timestamp with time zone,
    estimated_completion timestamp with time zone,
    total_items integer,
    processed_items integer,
    failed_items integer,
    errors json,
    sync_metadata json
);


ALTER TABLE public.sync_operations OWNER TO postgres;

--
-- TOC entry 259 (class 1259 OID 23631)
-- Name: tiktok_accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tiktok_accounts (
    id character varying NOT NULL,
    user_id character varying,
    tiktok_user_id character varying,
    username character varying,
    display_name character varying,
    avatar_url character varying,
    follower_count integer,
    following_count integer,
    like_count integer,
    video_count integer,
    access_token character varying,
    refresh_token character varying,
    access_token_expire_in integer,
    refresh_token_expire_in integer,
    is_active boolean,
    last_sync_at timestamp with time zone,
    connected_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.tiktok_accounts OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 23456)
-- Name: tiktok_orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tiktok_orders (
    id character varying NOT NULL,
    shop_id character varying,
    order_id character varying,
    order_status integer,
    payment_status character varying,
    fulfillment_type integer,
    buyer_info json,
    recipient_address json,
    line_items json,
    payment_info json,
    shipping_info json,
    create_time integer,
    update_time integer,
    synced_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.tiktok_orders OWNER TO postgres;

--
-- TOC entry 250 (class 1259 OID 23442)
-- Name: tiktok_products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tiktok_products (
    id character varying NOT NULL,
    shop_id character varying,
    product_id character varying,
    product_name character varying,
    product_status integer,
    category_id character varying,
    brand_id character varying,
    skus json,
    images json,
    create_time integer,
    update_time integer,
    synced_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.tiktok_products OWNER TO postgres;

--
-- TOC entry 248 (class 1259 OID 23424)
-- Name: tiktok_shops; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tiktok_shops (
    id character varying NOT NULL,
    shop_id character varying,
    shop_name character varying,
    shop_code character varying,
    shop_cipher character varying,
    access_token character varying,
    refresh_token character varying,
    access_token_expire_in integer,
    refresh_token_expire_in integer,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.tiktok_shops OWNER TO postgres;

--
-- TOC entry 253 (class 1259 OID 23483)
-- Name: webhook_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.webhook_events (
    id character varying NOT NULL,
    webhook_id character varying,
    shop_id character varying,
    event_type character varying,
    payload json,
    headers json,
    received_at timestamp with time zone DEFAULT now(),
    processed_at timestamp with time zone,
    status character varying,
    retry_count integer,
    error_message character varying
);


ALTER TABLE public.webhook_events OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 22848)
-- Name: creator_audience_demographics; Type: TABLE; Schema: users; Owner: postgres
--

CREATE TABLE users.creator_audience_demographics (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    creator_id uuid NOT NULL,
    age_group character varying(20) NOT NULL,
    percentage numeric(5,2) NOT NULL,
    country character varying(100),
    updated_at timestamp with time zone,
    gender character varying(50) DEFAULT 'not_specified'::character varying NOT NULL
);


ALTER TABLE users.creator_audience_demographics OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 22858)
-- Name: creator_badges; Type: TABLE; Schema: users; Owner: postgres
--

CREATE TABLE users.creator_badges (
    id uuid NOT NULL,
    creator_id uuid NOT NULL,
    badge_type character varying(50) NOT NULL,
    badge_name character varying(100) NOT NULL,
    badge_description text,
    gmv_threshold numeric(12,2),
    earned_at timestamp with time zone,
    is_active boolean,
    badge_metadata json
);


ALTER TABLE users.creator_badges OWNER TO postgres;

--
-- TOC entry 244 (class 1259 OID 22832)
-- Name: user_tokens; Type: TABLE; Schema: users; Owner: postgres
--

CREATE TABLE users.user_tokens (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    token_type character varying(50) NOT NULL,
    token_value character varying(500) NOT NULL,
    expires_at timestamp with time zone,
    is_used boolean,
    created_at timestamp with time zone
);


ALTER TABLE users.user_tokens OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 22823)
-- Name: users; Type: TABLE; Schema: users; Owner: postgres
--

CREATE TABLE users.users (
    id uuid NOT NULL,
    email character varying(255) NOT NULL,
    username character varying(100) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    is_active boolean,
    email_verified boolean,
    phone character varying(20),
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    last_login timestamp with time zone,
    first_name character varying(100),
    last_name character varying(100),
    date_of_birth date,
    profile_image_url text,
    bio text,
    address_line1 character varying(255),
    address_line2 character varying(255),
    city character varying(100),
    state character varying(100),
    postal_code character varying(20),
    country character varying(100),
    tiktok_handle character varying(100),
    tiktok_user_id character varying(100),
    discord_handle character varying(100),
    discord_user_id character varying(100),
    instagram_handle character varying(100),
    content_niche character varying(100),
    follower_count integer,
    average_views integer,
    engagement_rate numeric(5,2),
    company_name character varying(200),
    website_url text,
    tax_id character varying(50),
    profile_completion_percentage integer,
    notification_preferences json,
    timezone character varying(50),
    role users.user_role NOT NULL,
    gender users.gender_type,
    current_gmv numeric(12,2) DEFAULT 0.00,
    tiktok_followers integer DEFAULT 0,
    instagram_followers integer DEFAULT 0,
    youtube_handle character varying(100),
    youtube_followers integer DEFAULT 0,
    audience_male_percentage numeric(5,2),
    audience_female_percentage numeric(5,2),
    primary_age_group character varying(50),
    location character varying(100),
    age integer,
    ethnicity character varying(50),
    shipping_address text
);


ALTER TABLE users.users OWNER TO postgres;

--
-- TOC entry 5476 (class 0 OID 22391)
-- Dependencies: 241
-- Data for Name: campaign_performance_daily; Type: TABLE DATA; Schema: analytics; Owner: postgres
--

INSERT INTO analytics.campaign_performance_daily (id, campaign_id, date_snapshot, total_creators, active_creators, new_applications, approved_applications, posts_submitted, posts_approved, total_views, total_likes, total_comments, total_shares, total_gmv, total_commissions, total_payouts, avg_engagement_rate, conversion_rate, cost_per_acquisition, created_at) VALUES
('99ea2470-a559-4ebd-a126-937d8534f3d8', '44444444-4444-4444-4444-444444444441', '2025-07-03', 3, 3, 0, 0, 1, 1, 87000, 5900, 290, 180, 0.00, 0.00, 0.00, 6.78, 0.00, 0.00, '2025-07-04 23:09:57.446615+05'),
('0e672c80-50c4-4dfa-8bdc-be05f40326e5', '44444444-4444-4444-4444-444444444441', '2025-07-02', 3, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, '2025-07-04 23:09:57.446615+05'),
('6c18f189-b10f-4a12-9a85-6e7e3715e325', '44444444-4444-4444-4444-444444444441', '2025-06-26', 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 199.99, 10.00, 0.00, 0.00, 0.15, 75.00, '2025-07-04 23:09:57.446615+05'),
('1a222433-ebb7-4aa9-a0eb-430429792719', '44444444-4444-4444-4444-444444444441', '2025-06-25', 3, 3, 0, 0, 1, 1, 98000, 6800, 380, 290, 259.98, 13.00, 0.00, 6.94, 0.27, 57.69, '2025-07-04 23:09:57.446615+05'),
('e290a04d-bfe0-444c-bfc8-d6e9dd2026fc', '44444444-4444-4444-4444-444444444441', '2025-06-20', 3, 3, 0, 0, 1, 1, 125000, 8200, 450, 320, 179.98, 9.00, 0.00, 6.56, 0.14, 83.33, '2025-07-04 23:09:57.446615+05'),
('976083e2-03bb-4a91-bdc9-21970e7d4bd2', '44444444-4444-4444-4444-444444444441', '2025-06-19', 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0.00, 0.00, 225.50, 0.00, 0.00, 0.00, '2025-07-04 23:09:57.446615+05'),
('b0612f5a-5dde-421c-b8c0-a13297070291', '44444444-4444-4444-4444-444444444442', '2025-07-03', 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, '2025-07-04 23:09:57.446615+05'),
('2aaf3afc-651f-410a-b6ba-ea4969ddf1a9', '44444444-4444-4444-4444-444444444442', '2025-06-29', 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 149.99, 12.00, 0.00, 0.00, 0.10, 0.00, '2025-07-04 23:09:57.446615+05'),
('e050dc96-0716-4685-bfcb-c1b77b773ba4', '44444444-4444-4444-4444-444444444442', '2025-06-28', 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 299.99, 24.00, 0.00, 0.00, 0.13, 0.00, '2025-07-04 23:09:57.446615+05'),
('14ce1978-9e5e-4884-bf3f-a325b61ec038', '44444444-4444-4444-4444-444444444442', '2025-06-27', 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 299.99, 24.00, 0.00, 0.00, 0.19, 0.00, '2025-07-04 23:09:57.446615+05'),
('5c1227c1-dcef-49b5-a64e-c4d2fa76c5eb', '44444444-4444-4444-4444-444444444442', '2025-06-26', 1, 1, 0, 0, 1, 1, 156000, 12000, 890, 450, 0.00, 0.00, 48.00, 7.69, 0.00, 0.00, '2025-07-04 23:09:57.446615+05');


--
-- TOC entry 5477 (class 0 OID 22421)
-- Dependencies: 242
-- Data for Name: creator_performance; Type: TABLE DATA; Schema: analytics; Owner: postgres
--

INSERT INTO analytics.creator_performance (id, creator_id, campaign_id, total_posts, completed_deliverables, on_time_deliverables, total_gmv, avg_views_per_post, avg_engagement_rate, consistency_score, reliability_rating, last_calculated) VALUES
('a1ec6f32-0310-4b8c-a1d5-eabf69f1434f', '33333333-3333-3333-3333-333333333331', '44444444-4444-4444-4444-444444444441', 3, 2, 2, 639.96, 103333.33, 6.65, 1.00, 5.0, '2025-07-04 23:09:57.446615+05'),
('2f82dab2-4ab0-45e8-bbcf-76bc07b0c9af', '33333333-3333-3333-3333-333333333332', '44444444-4444-4444-4444-444444444442', 1, 1, 1, 749.97, 156000.00, 7.69, 1.00, 5.0, '2025-07-04 23:09:57.446615+05'),
('2bd41e27-3122-4f85-81c4-d9334c22739f', '33333333-3333-3333-3333-333333333333', '44444444-4444-4444-4444-444444444441', 1, 1, 1, 219.97, 210000.00, 8.81, 1.00, 5.0, '2025-07-04 23:09:57.446615+05'),
('ca35739c-9b69-4f33-b927-7c25d2912347', '33333333-3333-3333-3333-333333333333', '44444444-4444-4444-4444-444444444443', 4, 4, 4, 99.98, 185000.00, 8.22, 1.00, 5.0, '2025-07-04 23:09:57.446615+05');


--
-- TOC entry 5461 (class 0 OID 20610)
-- Dependencies: 226
-- Data for Name: campaign_products; Type: TABLE DATA; Schema: campaigns; Owner: postgres
--

-- campaigns.campaign_products table is empty


--
-- TOC entry 5462 (class 0 OID 20631)
-- Dependencies: 227
-- Data for Name: campaign_segments; Type: TABLE DATA; Schema: campaigns; Owner: postgres
--

-- campaigns.campaign_segments table is empty


--
-- TOC entry 5460 (class 0 OID 20593)
-- Dependencies: 225
-- Data for Name: campaigns; Type: TABLE DATA; Schema: campaigns; Owner: postgres
--

INSERT INTO campaigns.campaigns (id, agency_id, brand_id, name, description, thumbnail_url, status, payout_model, tracking_method, start_date, end_date, grace_period_days, is_rolling_30_day, max_creators, min_deliverables_per_creator, require_approval, require_discord_join, discord_server_id, discord_role_name, base_payout_per_post, gmv_commission_rate, retainer_amount, total_budget, spent_amount, hashtag, target_gmv, target_posts, target_views, referral_bonus_enabled, referral_bonus_amount, created_at, updated_at, current_gmv, current_creators, current_posts, total_views, total_engagement, type, budget, target_creators, tiktok_product_links) VALUES
('903227b1-cdc9-42f7-9ea6-790267640fcb', '123e4567-e89b-12d3-a456-426614174000', NULL, 'SQLAlchemy Fix Test', 'Testing after fixing SQLAlchemy foreign keys', NULL, 'draft', 'fixed_per_post', 'hashtag', NULL, NULL, 0, false, 3, 1, true, false, NULL, NULL, 100.00, 0.00, 0.00, 300.00, 0.00, '#sqlalchemyfix', NULL, NULL, NULL, false, 0.00, '2025-06-28 14:20:37.975251+05', '2025-07-07 11:01:36.902297+05', 0.00, 0, 0, 0, 0, 'performance', 300.00, NULL, NULL),
('0f4eb751-291e-4f97-97ad-328cbf918a60', '123e4567-e89b-12d3-a456-426614174000', NULL, 'Test Campaign', 'My first test campaign', NULL, 'draft', 'fixed_per_post', 'hashtag', NULL, NULL, 0, false, 10, 1, true, false, NULL, NULL, 50.00, 0.00, 0.00, 1000.00, 0.00, '#testcampaign', NULL, NULL, NULL, false, 0.00, '2025-06-28 17:23:05.748443+05', '2025-07-07 11:01:36.902297+05', 0.00, 0, 0, 0, 0, 'performance', 1000.00, NULL, NULL),
('44444444-4444-4444-4444-444444444441', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222221', 'Fashion Nova Winter Collection', 'Promote our new winter collection with authentic styling content. Focus on versatile pieces that can be styled for different occasions.', NULL, 'active', 'hybrid', 'hashtag', '2025-06-19 23:09:57.446615+05', '2025-07-19 23:09:57.446615+05', 3, false, 20, 3, true, false, NULL, NULL, 75.00, 5.00, NULL, 15000.00, 0.00, '#FashionNovaWinter', 50000.00, 60, 2000000, false, NULL, '2025-06-14 23:09:57.446615+05', '2025-07-07 11:01:36.902297+05', 859.92, 2, 3, 433000, 36790, 'performance', 15000.00, NULL, NULL),
('44444444-4444-4444-4444-444444444442', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 'Tech Gadgets Review Series', 'Honest reviews of our latest smart home devices and tech accessories. Focus on practical use cases and real-world testing.', NULL, 'active', 'gmv_commission', 'product_link', '2025-06-24 23:09:57.446615+05', '2025-07-24 23:09:57.446615+05', 2, false, 10, 2, true, false, NULL, NULL, 0.00, 8.00, NULL, 25000.00, 0.00, '#TechGadgetsPro', 75000.00, 30, 1500000, false, NULL, '2025-06-22 23:09:57.446615+05', '2025-07-07 11:01:36.902297+05', 749.97, 1, 1, 156000, 13340, 'performance', 25000.00, NULL, NULL),
('44444444-4444-4444-4444-444444444443', '11111111-1111-1111-1111-111111111112', '22222222-2222-2222-2222-222222222221', 'Fitness Transformation Challenge', '30-day fitness journey showcasing workout equipment and supplements. Document real transformations and progress.', NULL, 'completed', 'fixed_per_post', 'hashtag', '2025-05-20 23:09:57.446615+05', '2025-06-29 23:09:57.446615+05', 5, false, 15, 4, false, false, NULL, NULL, 100.00, 0.00, NULL, 18000.00, 0.00, '#FitnessTransform30', 30000.00, 60, 2500000, false, NULL, '2025-05-15 23:09:57.446615+05', '2025-07-07 11:01:36.902297+05', 99.98, 2, 1, 185000, 16610, 'performance', 18000.00, NULL, NULL),
('44444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 'Holiday Gift Guide', 'Curate the perfect holiday gift guide featuring our top products. Show gift ideas for different personalities and budgets.', NULL, 'draft', 'hybrid', 'hashtag', '2025-07-09 23:09:57.446615+05', '2025-08-08 23:09:57.446615+05', 3, false, 25, 2, true, false, NULL, NULL, 50.00, 6.00, NULL, 20000.00, 0.00, '#HolidayGifts2024', 60000.00, 50, 1800000, false, NULL, '2025-07-02 23:09:57.446615+05', '2025-07-07 11:01:36.902297+05', 0.00, 0, 0, 0, 0, 'performance', 20000.00, NULL, NULL),
('a2115469-b5cf-48d3-8d1a-a14f7a8bf738', '9b2c18f5-ad98-4a87-8d5b-1b9a9650eff0', NULL, 'Direct Test Script', NULL, NULL, 'draft', 'fixed_per_post', 'hashtag', NULL, NULL, 0, false, NULL, 1, true, false, NULL, NULL, 0.00, 0.00, 0.00, 1000.00, 0.00, NULL, NULL, NULL, NULL, false, 0.00, '2025-07-06 05:05:13.269929+05', '2025-07-07 11:01:36.902297+05', 0.00, 0, 0, 0, 0, 'performance', 1000.00, NULL, NULL),
('b61f0742-2517-4fed-8c49-4813a38af805', 'fcd76c50-6cc6-4e38-bbd1-f21d1a5f9b19', NULL, 'Test Campaign', NULL, NULL, 'draft', 'fixed_per_post', 'hashtag', NULL, NULL, 0, false, NULL, 1, true, false, NULL, NULL, 0.00, 0.00, 0.00, 0.00, 0.00, NULL, NULL, NULL, NULL, false, 0.00, '2025-07-06 13:02:20.501146+05', '2025-07-07 11:01:36.902297+05', 0.00, 0, 0, 0, 0, 'performance', 0.00, NULL, NULL),
('386effb8-c306-4625-8ef7-514860f99581', '5b081783-a956-4dbb-ba05-48796dd6b98d', NULL, 'Test Campaign from Modal', NULL, NULL, 'draft', 'fixed_per_post', 'hashtag', NULL, NULL, 0, false, NULL, 1, true, false, NULL, NULL, 0.00, 0.00, 0.00, 1000.00, 0.00, NULL, NULL, NULL, NULL, false, 0.00, '2025-07-06 18:29:11.976159+05', '2025-07-07 11:01:36.902297+05', 0.00, 0, 0, 0, 0, 'performance', 1000.00, NULL, NULL),
('3598c80b-5077-4911-b853-8d832c55b773', '634c9d62-5e53-44b8-af7a-09b42b62bbbd', NULL, 'Test Campaign from Modal', NULL, NULL, 'draft', 'fixed_per_post', 'hashtag', NULL, NULL, 0, false, NULL, 1, true, false, NULL, NULL, 0.00, 0.00, 0.00, 1000.00, 0.00, NULL, NULL, NULL, NULL, false, 0.00, '2025-07-06 18:56:51.683648+05', '2025-07-07 11:01:36.902297+05', 0.00, 0, 0, 0, 0, 'performance', 1000.00, NULL, NULL),
('302c0889-4ce0-412f-9cc2-e9a0ae5e15da', '0ec3743c-2280-4cfd-be83-e05677457451', NULL, 'Launchpaid Promo', '', NULL, 'paused', 'gmv_commission', 'hashtag', '2025-07-06 05:00:00+05', '2025-07-08 05:00:00+05', 3, false, 25, 1, true, false, NULL, NULL, 10.00, 5.00, 10.00, 2500.00, 0.00, '', 2500.00, NULL, NULL, false, 0.00, '2025-07-07 22:19:03.876336+05', '2025-07-12 23:55:32.872979+05', 0.00, 0, 0, 0, 0, 'performance', 2500.00, 25, NULL),
('c1c62880-b564-46f1-8036-2569980c873c', '0ec3743c-2280-4cfd-be83-e05677457451', NULL, 'Junejo Campaign', '', NULL, 'active', 'fixed_per_post', 'hashtag', '2025-07-12 05:00:00+05', '2025-07-13 05:00:00+05', 3, false, 25, 1, true, false, NULL, NULL, 5.00, 0.00, 0.00, 1000.00, 0.00, '', 1000.00, NULL, NULL, false, 0.00, '2025-07-12 00:45:24.767745+05', '2025-07-19 03:39:58.840076+05', 0.00, 0, 0, 0, 0, 'performance', 1000.00, 25, NULL),
('3eff4dfb-1e1c-40d1-a101-ad5b7535fc19', 'af835780-924e-4d6b-82c2-6318b3d25152', NULL, 'Test Campaign from Modal', NULL, NULL, 'draft', 'fixed_per_post', 'hashtag', NULL, NULL, 0, false, NULL, 1, true, false, NULL, NULL, 0.00, 0.00, 0.00, 1000.00, 0.00, NULL, NULL, NULL, NULL, false, 0.00, '2025-07-07 07:30:35.181882+05', '2025-07-07 11:01:36.902297+05', 0.00, 0, 0, 0, 0, 'performance', 1000.00, NULL, NULL),
('7eee88b9-6e53-4a34-8749-329c74f52b7a', '0ec3743c-2280-4cfd-be83-e05677457451', NULL, 'Champs Campaign', 'Hello World this is champ campaign', NULL, 'active', 'fixed_per_post', 'hashtag', '2025-07-08 05:00:00+05', '2025-07-28 05:00:00+05', 3, false, 25, 5, true, false, NULL, NULL, 10.00, 0.00, 0.00, 1000.00, 0.00, '', 1000.00, NULL, NULL, false, 0.00, '2025-07-07 22:05:23.169433+05', '2025-07-07 22:12:08.210303+05', 0.00, 0, 0, 0, 0, 'performance', 1000.00, 25, NULL);


--
-- TOC entry 5482 (class 0 OID 23032)
-- Dependencies: 247
-- Data for Name: campaigns_backup; Type: TABLE DATA; Schema: campaigns; Owner: postgres
--

INSERT INTO campaigns.campaigns_backup (id, agency_id, brand_id, name, description, thumbnail_url, status, payout_model, tracking_method, start_date, end_date, grace_period_days, is_rolling_30_day, max_creators, min_deliverables_per_creator, require_approval, require_discord_join, discord_server_id, discord_role_name, base_payout_per_post, gmv_commission_rate, retainer_amount, total_budget, spent_amount, hashtag, target_gmv, target_posts, target_views, referral_bonus_enabled, referral_bonus_amount, created_at, updated_at, current_gmv, current_creators, current_posts, total_views, total_engagement, type, budget, target_creators, tiktok_product_links) VALUES
('903227b1-cdc9-42f7-9ea6-790267640fcb', '123e4567-e89b-12d3-a456-426614174000', NULL, 'SQLAlchemy Fix Test', 'Testing after fixing SQLAlchemy foreign keys', NULL, 'draft', 'fixed_per_post', 'hashtag', NULL, NULL, 0, false, 3, 1, true, false, NULL, NULL, 100.00, 0.00, 0.00, 300.00, 0.00, '#sqlalchemyfix', NULL, NULL, NULL, false, 0.00, '2025-06-28 14:20:37.975251+05', '2025-07-05 02:24:35.993468+05', 0.00, 0, 0, 0, 0, 'performance', 300.00, NULL, NULL),
('0f4eb751-291e-4f97-97ad-328cbf918a60', '123e4567-e89b-12d3-a456-426614174000', NULL, 'Test Campaign', 'My first test campaign', NULL, 'draft', 'fixed_per_post', 'hashtag', NULL, NULL, 0, false, 10, 1, true, false, NULL, NULL, 50.00, 0.00, 0.00, 1000.00, 0.00, '#testcampaign', NULL, NULL, NULL, false, 0.00, '2025-06-28 17:23:05.748443+05', '2025-07-05 02:24:35.993468+05', 0.00, 0, 0, 0, 0, 'performance', 1000.00, NULL, NULL),
('44444444-4444-4444-4444-444444444441', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222221', 'Fashion Nova Winter Collection', 'Promote our new winter collection with authentic styling content. Focus on versatile pieces that can be styled for different occasions.', NULL, 'active', 'hybrid', 'hashtag', '2025-06-19 23:09:57.446615+05', '2025-07-19 23:09:57.446615+05', 3, false, 20, 3, true, false, NULL, NULL, 75.00, 5.00, NULL, 15000.00, 0.00, '#FashionNovaWinter', 50000.00, 60, 2000000, false, NULL, '2025-06-14 23:09:57.446615+05', '2025-07-07 11:01:36.902297+05', 859.92, 2, 3, 433000, 36790, 'performance', 15000.00, NULL, NULL),
('44444444-4444-4444-4444-444444444442', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 'Tech Gadgets Review Series', 'Honest reviews of our latest smart home devices and tech accessories. Focus on practical use cases and real-world testing.', NULL, 'active', 'gmv_commission', 'product_link', '2025-06-24 23:09:57.446615+05', '2025-07-24 23:09:57.446615+05', 2, false, 10, 2, true, false, NULL, NULL, 0.00, 8.00, NULL, 25000.00, 0.00, '#TechGadgetsPro', 75000.00, 30, 1500000, false, NULL, '2025-06-22 23:09:57.446615+05', '2025-07-07 11:01:36.902297+05', 749.97, 1, 1, 156000, 13340, 'performance', 25000.00, NULL, NULL),
('44444444-4444-4444-4444-444444444443', '11111111-1111-1111-1111-111111111112', '22222222-2222-2222-2222-222222222221', 'Fitness Transformation Challenge', '30-day fitness journey showcasing workout equipment and supplements. Document real transformations and progress.', NULL, 'completed', 'fixed_per_post', 'hashtag', '2025-05-20 23:09:57.446615+05', '2025-06-29 23:09:57.446615+05', 5, false, 15, 4, false, false, NULL, NULL, 100.00, 0.00, NULL, 18000.00, 0.00, '#FitnessTransform30', 30000.00, 60, 2500000, false, NULL, '2025-05-15 23:09:57.446615+05', '2025-07-07 11:01:36.902297+05', 99.98, 2, 1, 185000, 16610, 'performance', 18000.00, NULL, NULL),
('44444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 'Holiday Gift Guide', 'Curate the perfect holiday gift guide featuring our top products. Show gift ideas for different personalities and budgets.', NULL, 'draft', 'hybrid', 'hashtag', '2025-07-09 23:09:57.446615+05', '2025-08-08 23:09:57.446615+05', 3, false, 25, 2, true, false, NULL, NULL, 50.00, 6.00, NULL, 20000.00, 0.00, '#HolidayGifts2024', 60000.00, 50, 1800000, false, NULL, '2025-07-02 23:09:57.446615+05', '2025-07-07 11:01:36.902297+05', 0.00, 0, 0, 0, 0, 'performance', 20000.00, NULL, NULL),
('a2115469-b5cf-48d3-8d1a-a14f7a8bf738', '9b2c18f5-ad98-4a87-8d5b-1b9a9650eff0', NULL, 'Direct Test Script', NULL, NULL, 'draft', 'fixed_per_post', 'hashtag', NULL, NULL, 0, false, NULL, 1, true, false, NULL, NULL, 0.00, 0.00, 0.00, 1000.00, 0.00, NULL, NULL, NULL, NULL, false, 0.00, '2025-07-06 05:05:13.269929+05', '2025-07-07 11:01:36.902297+05', 0.00, 0, 0, 0, 0, 'performance', 1000.00, NULL, NULL),
('b61f0742-2517-4fed-8c49-4813a38af805', 'fcd76c50-6cc6-4e38-bbd1-f21d1a5f9b19', NULL, 'Test Campaign', NULL, NULL, 'draft', 'fixed_per_post', 'hashtag', NULL, NULL, 0, false, NULL, 1, true, false, NULL, NULL, 0.00, 0.00, 0.00, 0.00, 0.00, NULL, NULL, NULL, NULL, false, 0.00, '2025-07-06 13:02:20.501146+05', '2025-07-07 11:01:36.902297+05', 0.00, 0, 0, 0, 0, 'performance', 0.00, NULL, NULL),
('386effb8-c306-4625-8ef7-514860f99581', '5b081783-a956-4dbb-ba05-48796dd6b98d', NULL, 'Test Campaign from Modal', NULL, NULL, 'draft', 'fixed_per_post', 'hashtag', NULL, NULL, 0, false, NULL, 1, true, false, NULL, NULL, 0.00, 0.00, 0.00, 1000.00, 0.00, NULL, NULL, NULL, NULL, false, 0.00, '2025-07-06 18:29:11.976159+05', '2025-07-07 11:01:36.902297+05', 0.00, 0, 0, 0, 0, 'performance', 1000.00, NULL, NULL),
('3598c80b-5077-4911-b853-8d832c55b773', '634c9d62-5e53-44b8-af7a-09b42b62bbbd', NULL, 'Test Campaign from Modal', NULL, NULL, 'draft', 'fixed_per_post', 'hashtag', NULL, NULL, 0, false, NULL, 1, true, false, NULL, NULL, 0.00, 0.00, 0.00, 1000.00, 0.00, NULL, NULL, NULL, NULL, false, 0.00, '2025-07-06 18:56:51.683648+05', '2025-07-07 11:01:36.902297+05', 0.00, 0, 0, 0, 0, 'performance', 1000.00, NULL, NULL),
('302c0889-4ce0-412f-9cc2-e9a0ae5e15da', '0ec3743c-2280-4cfd-be83-e05677457451', NULL, 'Launchpaid Promo', '', NULL, 'paused', 'gmv_commission', 'hashtag', '2025-07-06 05:00:00+05', '2025-07-08 05:00:00+05', 3, false, 25, 1, true, false, NULL, NULL, 10.00, 5.00, 10.00, 2500.00, 0.00, '', 2500.00, NULL, NULL, false, 0.00, '2025-07-07 22:19:03.876336+05', '2025-07-12 23:55:32.872979+05', 0.00, 0, 0, 0, 0, 'performance', 2500.00, 25, NULL),
('c1c62880-b564-46f1-8036-2569980c873c', '0ec3743c-2280-4cfd-be83-e05677457451', NULL, 'Junejo Campaign', '', NULL, 'active', 'fixed_per_post', 'hashtag', '2025-07-12 05:00:00+05', '2025-07-13 05:00:00+05', 3, false, 25, 1, true, false, NULL, NULL, 5.00, 0.00, 0.00, 1000.00, 0.00, '', 1000.00, NULL, NULL, false, 0.00, '2025-07-12 00:45:24.767745+05', '2025-07-19 03:39:58.840076+05', 0.00, 0, 0, 0, 0, 'performance', 1000.00, 25, NULL),
('3eff4dfb-1e1c-40d1-a101-ad5b7535fc19', 'af835780-924e-4d6b-82c2-6318b3d25152', NULL, 'Test Campaign from Modal', NULL, NULL, 'draft', 'fixed_per_post', 'hashtag', NULL, NULL, 0, false, NULL, 1, true, false, NULL, NULL, 0.00, 0.00, 0.00, 1000.00, 0.00, NULL, NULL, NULL, NULL, false, 0.00, '2025-07-07 07:30:35.181882+05', '2025-07-07 11:01:36.902297+05', 0.00, 0, 0, 0, 0, 'performance', 1000.00, NULL, NULL),
('7eee88b9-6e53-4a34-8749-329c74f52b7a', '0ec3743c-2280-4cfd-be83-e05677457451', NULL, 'Champs Campaign', 'Hello World this is champ campaign', NULL, 'active', 'fixed_per_post', 'hashtag', '2025-07-08 05:00:00+05', '2025-07-28 05:00:00+05', 3, false, 25, 5, true, false, NULL, NULL, 10.00, 0.00, 0.00, 1000.00, 0.00, '', 1000.00, NULL, NULL, false, 0.00, '2025-07-07 22:05:23.169433+05', '2025-07-07 22:12:08.210303+05', 0.00, 0, 0, 0, 0, 'performance', 1000.00, 25, NULL);


--
-- TOC entry 5465 (class 0 OID 20675)
-- Dependencies: 230
-- Data for Name: creator_applications; Type: TABLE DATA; Schema: campaigns; Owner: postgres
--

INSERT INTO campaigns.creator_applications (id, campaign_id, creator_id, segment_id, status, applied_at, reviewed_at, reviewed_by, application_data, application_message, response_message, follower_count, engagement_rate, previous_gmv, rejection_reason, review_notes) VALUES
('dcf0e134-365e-4a2d-8189-bd5b0c305ec2', '7eee88b9-6e53-4a34-8749-329c74f52b7a', '4923df90-0ecb-40e4-8114-0b2a97a280a3', NULL, 'approved', '2025-07-13 01:11:15.866501+05', '2025-07-13 01:22:54.532259+05', '0ec3743c-2280-4cfd-be83-e05677457451', '{}', NULL, NULL, 0, 0.00, 0.00, NULL, NULL),
('2e3a003d-361e-48c6-b334-047ec44e36ba', 'c1c62880-b564-46f1-8036-2569980c873c', '4923df90-0ecb-40e4-8114-0b2a97a280a3', NULL, 'approved', '2025-07-13 01:48:31.151249+05', '2025-07-13 01:48:43.337629+05', '0ec3743c-2280-4cfd-be83-e05677457451', '{}', NULL, NULL, 0, 0.00, 0.00, NULL, NULL);


--
-- TOC entry 5466 (class 0 OID 20713)
-- Dependencies: 231
-- Data for Name: deliverables; Type: TABLE DATA; Schema: campaigns; Owner: postgres
--

INSERT INTO campaigns.deliverables (id, application_id, deliverable_number, due_date, status, tiktok_post_url, post_caption, hashtags_used, submitted_at, approved_at, approved_by, agency_feedback, revision_requested, revision_notes, created_at, updated_at, title, description, content_url, content_type, content_duration, views, likes, comments, shares, gmv_generated, published_at, feedback, campaign_id, creator_id) VALUES
('ab478097-12df-4333-8765-9e535b45eeeb', '2e3a003d-361e-48c6-b334-047ec44e36ba', 1, NULL, 'pending', 'https://tiktok.com/samadjunejo/jshfo3802', NULL, '{}', '2025-07-14 00:11:49.556327+05', NULL, NULL, NULL, false, NULL, '2025-07-14 00:11:49.553101+05', '2025-07-14 00:11:49.553101+05', NULL, NULL, NULL, NULL, NULL, 0, 0, 0, 0, 0.00, NULL, NULL, 'c1c62880-b564-46f1-8036-2569980c873c', '4923df90-0ecb-40e4-8114-0b2a97a280a3'),
('9ba52350-d857-4481-8ef8-e43a1f8a3ab9', '2e3a003d-361e-48c6-b334-047ec44e36ba', 1, NULL, 'submitted', 'https://tiktok.com/samadjunejo/hello-product-promotion', NULL, '{}', '2025-07-14 01:32:58.360702+05', NULL, NULL, NULL, false, NULL, '2025-07-14 01:32:58.355651+05', '2025-07-14 01:32:58.355651+05', NULL, NULL, NULL, NULL, NULL, 0, 0, 0, 0, 0.00, NULL, NULL, 'c1c62880-b564-46f1-8036-2569980c873c', '4923df90-0ecb-40e4-8114-0b2a97a280a3'),
('6eddd4ed-73d9-4a7e-9712-ebf5a62c117c', 'dcf0e134-365e-4a2d-8189-bd5b0c305ec2', 1, NULL, 'submitted', NULL, NULL, '{}', '2025-07-18 20:22:30.14963+05', NULL, NULL, NULL, false, NULL, '2025-07-18 20:22:30.144081+05', '2025-07-18 20:22:30.144081+05', NULL, NULL, NULL, NULL, NULL, 0, 0, 0, 0, 0.00, NULL, NULL, '7eee88b9-6e53-4a34-8749-329c74f52b7a', '4923df90-0ecb-40e4-8114-0b2a97a280a3');


--
-- TOC entry 5463 (class 0 OID 20643)
-- Dependencies: 228
-- Data for Name: gmv_bonus_tiers; Type: TABLE DATA; Schema: campaigns; Owner: postgres
--

-- campaigns.gmv_bonus_tiers table is empty


--
-- TOC entry 5464 (class 0 OID 20653)
-- Dependencies: 229
-- Data for Name: leaderboard_bonuses; Type: TABLE DATA; Schema: campaigns; Owner: postgres
--

-- campaigns.leaderboard_bonuses table is empty


--
-- TOC entry 5475 (class 0 OID 22366)
-- Dependencies: 240
-- Data for Name: communication_logs; Type: TABLE DATA; Schema: integrations; Owner: postgres
--

-- integrations.communication_logs table is empty


--
-- TOC entry 5474 (class 0 OID 22341)
-- Dependencies: 239
-- Data for Name: creator_discord_roles; Type: TABLE DATA; Schema: integrations; Owner: postgres
--

-- integrations.creator_discord_roles table is empty


--
-- TOC entry 5473 (class 0 OID 22327)
-- Dependencies: 238
-- Data for Name: discord_roles; Type: TABLE DATA; Schema: integrations; Owner: postgres
--

-- integrations.discord_roles table is empty


--
-- TOC entry 5471 (class 0 OID 22279)
-- Dependencies: 236
-- Data for Name: external_integrations; Type: TABLE DATA; Schema: integrations; Owner: postgres
--

-- integrations.external_integrations table is empty


--
-- TOC entry 5472 (class 0 OID 22299)
-- Dependencies: 237
-- Data for Name: tiktok_shop_sales; Type: TABLE DATA; Schema: integrations; Owner: postgres
--

-- integrations.tiktok_shop_sales table is empty


--
-- TOC entry 5467 (class 0 OID 22159)
-- Dependencies: 232
-- Data for Name: creator_earnings; Type: TABLE DATA; Schema: payments; Owner: postgres
--

-- payments.creator_earnings table is empty


--
-- TOC entry 5469 (class 0 OID 22214)
-- Dependencies: 234
-- Data for Name: payment_schedules; Type: TABLE DATA; Schema: payments; Owner: postgres
--

-- payments.payment_schedules table is empty


--
-- TOC entry 5468 (class 0 OID 22189)
-- Dependencies: 233
-- Data for Name: payments; Type: TABLE DATA; Schema: payments; Owner: postgres
--

-- payments.payments table is empty


--
-- TOC entry 5470 (class 0 OID 22232)
-- Dependencies: 235
-- Data for Name: referrals; Type: TABLE DATA; Schema: payments; Owner: postgres
--

-- payments.referrals table is empty


--
-- TOC entry 5459 (class 0 OID 20545)
-- Dependencies: 224
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.alembic_version (version_num) VALUES
('d535d91823da'),
('add_missing_columns_001');


--
-- TOC entry 5484 (class 0 OID 23433)
-- Dependencies: 249
-- Data for Name: auth_code_usage; Type: TABLE DATA; Schema: public; Owner: postgres
--

-- public.auth_code_usage table is empty


--
-- TOC entry 5489 (class 0 OID 23535)
-- Dependencies: 254
-- Data for Name: creator_earnings; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.creator_earnings (id, creator_id, campaign_id, application_id, base_earnings, gmv_commission, bonus_earnings, referral_earnings, total_paid, first_earned_at, last_updated) VALUES
('2739e1d1-e5da-4ad6-a3cf-f48879197578', '4923df90-0ecb-40e4-8114-0b2a97a280a3', '550e8400-e29b-41d4-a716-446655440000', '660e8400-e29b-41d4-a716-446655440001', 1000.00, 500.00, 200.00, 50.00, 1200.00, '2025-07-17 21:59:27.019982+05', '2025-07-17 21:59:27.019982+05'),
('ca454bbf-0ab4-4967-ac7b-785cd0ea9517', '4923df90-0ecb-40e4-8114-0b2a97a280a3', '550e8400-e29b-41d4-a716-446655440002', '660e8400-e29b-41d4-a716-446655440003', 800.00, 400.00, 150.00, 25.00, 800.00, '2025-07-17 21:59:27.019982+05', '2025-07-17 21:59:27.019982+05');


--
-- TOC entry 5491 (class 0 OID 23567)
-- Dependencies: 256
-- Data for Name: payment_schedules; Type: TABLE DATA; Schema: public; Owner: postgres
--

-- public.payment_schedules table is empty


--
-- TOC entry 5490 (class 0 OID 23550)
-- Dependencies: 255
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.payments (id, creator_id, campaign_id, earning_id, amount, payment_type, payment_method, status, stripe_payment_intent_id, fanbasis_transaction_id, external_transaction_id, description, failure_reason, initiated_at, processed_at, completed_at, failed_at, new_column_example) VALUES
('2879db31-0076-4198-8b93-ae6bc4df94b3', '4923df90-0ecb-40e4-8114-0b2a97a280a3', '550e8400-e29b-41d4-a716-446655440000', NULL, 1200.00, 'base_payout', 'stripe', 'completed', NULL, NULL, NULL, 'Payment for Summer Fashion Collection campaign', NULL, '2025-07-17 21:59:27.019982+05', NULL, NULL, NULL, NULL),
('ebabf167-6022-48ed-8eaf-c4dbda37975d', '4923df90-0ecb-40e4-8114-0b2a97a280a3', '550e8400-e29b-41d4-a716-446655440002', NULL, 800.00, 'base_payout', 'stripe', 'completed', NULL, NULL, NULL, 'Payment for Tech Gadget Pro Launch campaign', NULL, '2025-07-17 21:59:27.019982+05', NULL, NULL, NULL, NULL),
('6ea20041-1872-4646-aef8-682bdf838520', '4923df90-0ecb-40e4-8114-0b2a97a280a3', '550e8400-e29b-41d4-a716-446655440004', NULL, 450.00, 'bonus', 'stripe', 'pending', NULL, NULL, NULL, 'Bonus payment for Beauty Essentials Kit campaign', NULL, '2025-07-17 21:59:27.019982+05', NULL, NULL, NULL, NULL);


--
-- TOC entry 5492 (class 0 OID 23580)
-- Dependencies: 257
-- Data for Name: referrals; Type: TABLE DATA; Schema: public; Owner: postgres
--

-- public.referrals table is empty


--
-- TOC entry 5487 (class 0 OID 23470)
-- Dependencies: 252
-- Data for Name: sync_operations; Type: TABLE DATA; Schema: public; Owner: postgres
--

-- public.sync_operations table is empty


--
-- TOC entry 5493 (class 0 OID 23631)
-- Dependencies: 259
-- Data for Name: tiktok_accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

-- public.tiktok_accounts table is empty


--
-- TOC entry 5486 (class 0 OID 23456)
-- Dependencies: 251
-- Data for Name: tiktok_orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

-- public.tiktok_orders table is empty


--
-- TOC entry 5485 (class 0 OID 23442)
-- Dependencies: 250
-- Data for Name: tiktok_products; Type: TABLE DATA; Schema: public; Owner: postgres
--

-- public.tiktok_products table is empty


--
-- TOC entry 5483 (class 0 OID 23424)
-- Dependencies: 248
-- Data for Name: tiktok_shops; Type: TABLE DATA; Schema: public; Owner: postgres
--

-- public.tiktok_shops table is empty


--
-- TOC entry 5488 (class 0 OID 23483)
-- Dependencies: 253
-- Data for Name: webhook_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

-- public.webhook_events table is empty


--
-- TOC entry 5480 (class 0 OID 22848)
-- Dependencies: 245
-- Data for Name: creator_audience_demographics; Type: TABLE DATA; Schema: users; Owner: postgres
--

INSERT INTO users.creator_audience_demographics (id, creator_id, age_group, percentage, country, updated_at, gender) VALUES
('0d5144f3-8653-4767-840c-ef59441b844b', '4923df90-0ecb-40e4-8114-0b2a97a280a3', '18-24', 25.50, 'US', '2025-07-11 12:48:05.699122+05', 'male'),
('c664f38b-6721-410b-b5db-fc9662e547eb', '4923df90-0ecb-40e4-8114-0b2a97a280a3', '18-24', 45.00, NULL, NULL, 'not_specified');


--
-- TOC entry 5481 (class 0 OID 22858)
-- Dependencies: 246
-- Data for Name: creator_badges; Type: TABLE DATA; Schema: users; Owner: postgres
--

-- users.creator_badges table is empty


--
-- TOC entry 5479 (class 0 OID 22832)
-- Dependencies: 244
-- Data for Name: user_tokens; Type: TABLE DATA; Schema: users; Owner: postgres
--

INSERT INTO users.user_tokens (id, user_id, token_type, token_value, expires_at, is_used, created_at) VALUES
('dc09137c-3834-4dac-b80c-7a1c8f6818d0', '4923df90-0ecb-40e4-8114-0b2a97a280a3', 'email_verification', '3e8916ce-c2e5-47f4-88b0-c2c292b91520', '2025-07-06 17:32:59.546266+05', false, '2025-07-05 22:32:59.552611+05');


--
-- TOC entry 5478 (class 0 OID 22823)
-- Dependencies: 243
-- Data for Name: users; Type: TABLE DATA; Schema: users; Owner: postgres
--

INSERT INTO users.users (id, email, username, hashed_password, is_active, email_verified, phone, created_at, updated_at, last_login, first_name, last_name, date_of_birth, profile_image_url, bio, address_line1, address_line2, city, state, postal_code, country, tiktok_handle, tiktok_user_id, discord_handle, discord_user_id, instagram_handle, content_niche, follower_count, average_views, engagement_rate, company_name, website_url, tax_id, profile_completion_percentage, notification_preferences, timezone, role, gender, current_gmv, tiktok_followers, instagram_followers, youtube_handle, youtube_followers, audience_male_percentage, audience_female_percentage, primary_age_group, location, age, ethnicity, shipping_address) VALUES
('529e9146-f994-4966-af20-d5019ea2ad81', 'testcreator@example.com', 'testcreator', '$2b$12$nN5onyUoEqaUM9XN.sNpEuABLyMm93d8ZAd1dDJBhl0IpvgjGcCAu', true, false, NULL, '2025-07-10 13:33:17.922052+05', NULL, NULL, 'Test', 'Creator', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'US', NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0.00, NULL, NULL, NULL, 0, '{}', 'UTC', 'creator', NULL, 0.00, 0, 0, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('9e763208-ba14-46a7-9924-4bfdac6c51f6', 'newcreator@example.com', 'newcreator', '$2b$12$qfVSzojdBx4TAegrKCEmwuXDBnck1hHEjjKR5MIR3sEAEI.bS0VkO', true, false, NULL, '2025-07-10 13:48:43.832254+05', '2025-07-10 13:48:59.942224+05', '2025-07-10 13:49:00.200803+05', 'New', 'Creator', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'US', NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0.00, NULL, NULL, NULL, 0, '{}', 'UTC', 'creator', NULL, 0.00, 0, 0, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('4923df90-0ecb-40e4-8114-0b2a97a280a3', 'asamad.ls.asj@gmail.com', 'samad', 'hashed_@12Asamad', true, false, '+923410394853', '2025-07-05 17:32:59.517155+05', '2025-07-18 21:22:19.963211+05', '2025-07-18 21:22:19.961887+05', 'AbdulSamad', 'Samad', '2025-07-10', '', 'This is abdul Samad', 'Blessing Tower, St: 01, Khayam town, H -13 Islamabad', 'string', 'Islamabad', 'Islamabad', 45200, 'United States', 'samadjunejo', NULL, 'samad', NULL, 'samad_the_great_', 'Entertainment', 0, 0, 0.00, 'string', 'string', 'string', 0, '{"email_notifications": false, "sms_notifications": false, "push_notifications": false, "campaign_updates": false, "payment_alerts": false, "weekly_digest": false}', 'string', 'creator', 'MALE', 5000.00, 0, 0, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
('0ec3743c-2280-4cfd-be83-e05677457451', 'abdulsamadjunejo0@gmail.com', 'abdulsamadjunejo0', '$2b$12$MzLYncx725Nj.If.fcoHW.TkKtWbemH8rolCd9MARxEvDvx5VdFPy', true, true, NULL, '2025-07-06 13:10:22.242794+05', '2025-07-18 22:06:02.787181+05', '2025-07-18 22:06:02.786347+05', 'Abdul', 'Samad', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'US', NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0.00, 'ByteCraftSoft', 'https://bytecraftsoft.com', NULL, 0, '{}', 'UTC', 'agency', NULL, 0.00, 0, 0, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL);


--
-- TOC entry 5211 (class 2606 OID 22415)
-- Name: campaign_performance_daily campaign_performance_daily_campaign_id_date_snapshot_key; Type: CONSTRAINT; Schema: analytics; Owner: postgres
--

ALTER TABLE ONLY analytics.campaign_performance_daily
    ADD CONSTRAINT campaign_performance_daily_campaign_id_date_snapshot_key UNIQUE (campaign_id, date_snapshot);


--
-- TOC entry 5213 (class 2606 OID 22413)
-- Name: campaign_performance_daily campaign_performance_daily_pkey; Type: CONSTRAINT; Schema: analytics; Owner: postgres
--

ALTER TABLE ONLY analytics.campaign_performance_daily
    ADD CONSTRAINT campaign_performance_daily_pkey PRIMARY KEY (id);


--
-- TOC entry 5216 (class 2606 OID 22437)
-- Name: creator_performance creator_performance_creator_id_campaign_id_key; Type: CONSTRAINT; Schema: analytics; Owner: postgres
--

ALTER TABLE ONLY analytics.creator_performance
    ADD CONSTRAINT creator_performance_creator_id_campaign_id_key UNIQUE (creator_id, campaign_id);


--
-- TOC entry 5218 (class 2606 OID 22435)
-- Name: creator_performance creator_performance_pkey; Type: CONSTRAINT; Schema: analytics; Owner: postgres
--

ALTER TABLE ONLY analytics.creator_performance
    ADD CONSTRAINT creator_performance_pkey PRIMARY KEY (id);


--
-- TOC entry 5157 (class 2606 OID 20616)
-- Name: campaign_products campaign_products_pkey; Type: CONSTRAINT; Schema: campaigns; Owner: postgres
--

ALTER TABLE ONLY campaigns.campaign_products
    ADD CONSTRAINT campaign_products_pkey PRIMARY KEY (id);


--
-- TOC entry 5159 (class 2606 OID 20637)
-- Name: campaign_segments campaign_segments_pkey; Type: CONSTRAINT; Schema: campaigns; Owner: postgres
--

ALTER TABLE ONLY campaigns.campaign_segments
    ADD CONSTRAINT campaign_segments_pkey PRIMARY KEY (id);


--
-- TOC entry 5145 (class 2606 OID 20599)
-- Name: campaigns campaigns_pkey; Type: CONSTRAINT; Schema: campaigns; Owner: postgres
--

ALTER TABLE ONLY campaigns.campaigns
    ADD CONSTRAINT campaigns_pkey PRIMARY KEY (id);


--
-- TOC entry 5165 (class 2606 OID 20681)
-- Name: creator_applications creator_applications_pkey; Type: CONSTRAINT; Schema: campaigns; Owner: postgres
--

ALTER TABLE ONLY campaigns.creator_applications
    ADD CONSTRAINT creator_applications_pkey PRIMARY KEY (id);


--
-- TOC entry 5170 (class 2606 OID 20719)
-- Name: deliverables deliverables_pkey; Type: CONSTRAINT; Schema: campaigns; Owner: postgres
--

ALTER TABLE ONLY campaigns.deliverables
    ADD CONSTRAINT deliverables_pkey PRIMARY KEY (id);


--
-- TOC entry 5161 (class 2606 OID 20647)
-- Name: gmv_bonus_tiers gmv_bonus_tiers_pkey; Type: CONSTRAINT; Schema: campaigns; Owner: postgres
--

ALTER TABLE ONLY campaigns.gmv_bonus_tiers
    ADD CONSTRAINT gmv_bonus_tiers_pkey PRIMARY KEY (id);


--
-- TOC entry 5163 (class 2606 OID 20659)
-- Name: leaderboard_bonuses leaderboard_bonuses_pkey; Type: CONSTRAINT; Schema: campaigns; Owner: postgres
--

ALTER TABLE ONLY campaigns.leaderboard_bonuses
    ADD CONSTRAINT leaderboard_bonuses_pkey PRIMARY KEY (id);


--
-- TOC entry 5207 (class 2606 OID 22375)
-- Name: communication_logs communication_logs_pkey; Type: CONSTRAINT; Schema: integrations; Owner: postgres
--

ALTER TABLE ONLY integrations.communication_logs
    ADD CONSTRAINT communication_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 5203 (class 2606 OID 22350)
-- Name: creator_discord_roles creator_discord_roles_creator_id_campaign_id_discord_role_i_key; Type: CONSTRAINT; Schema: integrations; Owner: postgres
--

ALTER TABLE ONLY integrations.creator_discord_roles
    ADD CONSTRAINT creator_discord_roles_creator_id_campaign_id_discord_role_i_key UNIQUE (creator_id, campaign_id, discord_role_id);


--
-- TOC entry 5205 (class 2606 OID 22348)
-- Name: creator_discord_roles creator_discord_roles_pkey; Type: CONSTRAINT; Schema: integrations; Owner: postgres
--

ALTER TABLE ONLY integrations.creator_discord_roles
    ADD CONSTRAINT creator_discord_roles_pkey PRIMARY KEY (id);


--
-- TOC entry 5201 (class 2606 OID 22335)
-- Name: discord_roles discord_roles_pkey; Type: CONSTRAINT; Schema: integrations; Owner: postgres
--

ALTER TABLE ONLY integrations.discord_roles
    ADD CONSTRAINT discord_roles_pkey PRIMARY KEY (id);


--
-- TOC entry 5190 (class 2606 OID 22291)
-- Name: external_integrations external_integrations_pkey; Type: CONSTRAINT; Schema: integrations; Owner: postgres
--

ALTER TABLE ONLY integrations.external_integrations
    ADD CONSTRAINT external_integrations_pkey PRIMARY KEY (id);


--
-- TOC entry 5192 (class 2606 OID 22293)
-- Name: external_integrations external_integrations_user_id_integration_type_key; Type: CONSTRAINT; Schema: integrations; Owner: postgres
--

ALTER TABLE ONLY integrations.external_integrations
    ADD CONSTRAINT external_integrations_user_id_integration_type_key UNIQUE (user_id, integration_type);


--
-- TOC entry 5197 (class 2606 OID 22309)
-- Name: tiktok_shop_sales tiktok_shop_sales_pkey; Type: CONSTRAINT; Schema: integrations; Owner: postgres
--

ALTER TABLE ONLY integrations.tiktok_shop_sales
    ADD CONSTRAINT tiktok_shop_sales_pkey PRIMARY KEY (id);


--
-- TOC entry 5199 (class 2606 OID 22311)
-- Name: tiktok_shop_sales tiktok_shop_sales_tiktok_order_id_tiktok_product_id_key; Type: CONSTRAINT; Schema: integrations; Owner: postgres
--

ALTER TABLE ONLY integrations.tiktok_shop_sales
    ADD CONSTRAINT tiktok_shop_sales_tiktok_order_id_tiktok_product_id_key UNIQUE (tiktok_order_id, tiktok_product_id);


--
-- TOC entry 5175 (class 2606 OID 22173)
-- Name: creator_earnings creator_earnings_pkey; Type: CONSTRAINT; Schema: payments; Owner: postgres
--

ALTER TABLE ONLY payments.creator_earnings
    ADD CONSTRAINT creator_earnings_pkey PRIMARY KEY (id);


--
-- TOC entry 5184 (class 2606 OID 22226)
-- Name: payment_schedules payment_schedules_pkey; Type: CONSTRAINT; Schema: payments; Owner: postgres
--

ALTER TABLE ONLY payments.payment_schedules
    ADD CONSTRAINT payment_schedules_pkey PRIMARY KEY (id);


--
-- TOC entry 5182 (class 2606 OID 22198)
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: payments; Owner: postgres
--

ALTER TABLE ONLY payments.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- TOC entry 5186 (class 2606 OID 22240)
-- Name: referrals referrals_pkey; Type: CONSTRAINT; Schema: payments; Owner: postgres
--

ALTER TABLE ONLY payments.referrals
    ADD CONSTRAINT referrals_pkey PRIMARY KEY (id);


--
-- TOC entry 5188 (class 2606 OID 22242)
-- Name: referrals referrals_referrer_id_referred_id_campaign_id_key; Type: CONSTRAINT; Schema: payments; Owner: postgres
--

ALTER TABLE ONLY payments.referrals
    ADD CONSTRAINT referrals_referrer_id_referred_id_campaign_id_key UNIQUE (referrer_id, referred_id, campaign_id);


--
-- TOC entry 5143 (class 2606 OID 20549)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 5242 (class 2606 OID 23440)
-- Name: auth_code_usage auth_code_usage_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_code_usage
    ADD CONSTRAINT auth_code_usage_pkey PRIMARY KEY (id);


--
-- TOC entry 5257 (class 2606 OID 23547)
-- Name: creator_earnings creator_earnings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.creator_earnings
    ADD CONSTRAINT creator_earnings_pkey PRIMARY KEY (id);


--
-- TOC entry 5260 (class 2606 OID 23549)
-- Name: creator_earnings idx_creator_earnings_creator_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.creator_earnings
    ADD CONSTRAINT idx_creator_earnings_creator_id UNIQUE (creator_id, campaign_id, application_id);


--
-- TOC entry 5263 (class 2606 OID 23561)
-- Name: payments idx_payments_creator_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT idx_payments_creator_id UNIQUE (creator_id, campaign_id, earning_id);


--
-- TOC entry 5273 (class 2606 OID 23590)
-- Name: referrals idx_referrals_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referrals
    ADD CONSTRAINT idx_referrals_unique UNIQUE (referrer_id, referred_id);


--
-- TOC entry 5269 (class 2606 OID 23579)
-- Name: payment_schedules payment_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_schedules
    ADD CONSTRAINT payment_schedules_pkey PRIMARY KEY (id);


--
-- TOC entry 5266 (class 2606 OID 23559)
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- TOC entry 5275 (class 2606 OID 23588)
-- Name: referrals referrals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referrals
    ADD CONSTRAINT referrals_pkey PRIMARY KEY (id);


--
-- TOC entry 5251 (class 2606 OID 23477)
-- Name: sync_operations sync_operations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sync_operations
    ADD CONSTRAINT sync_operations_pkey PRIMARY KEY (id);


--
-- TOC entry 5279 (class 2606 OID 23638)
-- Name: tiktok_accounts tiktok_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tiktok_accounts
    ADD CONSTRAINT tiktok_accounts_pkey PRIMARY KEY (id);


--
-- TOC entry 5249 (class 2606 OID 23463)
-- Name: tiktok_orders tiktok_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tiktok_orders
    ADD CONSTRAINT tiktok_orders_pkey PRIMARY KEY (id);


--
-- TOC entry 5246 (class 2606 OID 23449)
-- Name: tiktok_products tiktok_products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tiktok_products
    ADD CONSTRAINT tiktok_products_pkey PRIMARY KEY (id);


--
-- TOC entry 5240 (class 2606 OID 23431)
-- Name: tiktok_shops tiktok_shops_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tiktok_shops
    ADD CONSTRAINT tiktok_shops_pkey PRIMARY KEY (id);


--
-- TOC entry 5255 (class 2606 OID 23490)
-- Name: webhook_events webhook_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webhook_events
    ADD CONSTRAINT webhook_events_pkey PRIMARY KEY (id);


--
-- TOC entry 5235 (class 2606 OID 22852)
-- Name: creator_audience_demographics creator_audience_demographics_pkey; Type: CONSTRAINT; Schema: users; Owner: postgres
--

ALTER TABLE ONLY users.creator_audience_demographics
    ADD CONSTRAINT creator_audience_demographics_pkey PRIMARY KEY (id);


--
-- TOC entry 5237 (class 2606 OID 22864)
-- Name: creator_badges creator_badges_pkey; Type: CONSTRAINT; Schema: users; Owner: postgres
--

ALTER TABLE ONLY users.creator_badges
    ADD CONSTRAINT creator_badges_pkey PRIMARY KEY (id);


--
-- TOC entry 5233 (class 2606 OID 22838)
-- Name: user_tokens user_tokens_pkey; Type: CONSTRAINT; Schema: users; Owner: postgres
--

ALTER TABLE ONLY users.user_tokens
    ADD CONSTRAINT user_tokens_pkey PRIMARY KEY (id);


--
-- TOC entry 5227 (class 2606 OID 22829)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: users; Owner: postgres
--

ALTER TABLE ONLY users.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 5214 (class 1259 OID 22468)
-- Name: idx_campaign_performance_campaign_date; Type: INDEX; Schema: analytics; Owner: postgres
--

CREATE INDEX idx_campaign_performance_campaign_date ON analytics.campaign_performance_daily USING btree (campaign_id, date_snapshot);


--
-- TOC entry 5219 (class 1259 OID 22469)
-- Name: idx_creator_performance_creator_id; Type: INDEX; Schema: analytics; Owner: postgres
--

CREATE INDEX idx_creator_performance_creator_id ON analytics.creator_performance USING btree (creator_id);


--
-- TOC entry 5146 (class 1259 OID 22448)
-- Name: idx_campaigns_agency_id; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_campaigns_agency_id ON campaigns.campaigns USING btree (agency_id);


--
-- TOC entry 5147 (class 1259 OID 22449)
-- Name: idx_campaigns_brand_id; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_campaigns_brand_id ON campaigns.campaigns USING btree (brand_id);


--
-- TOC entry 5148 (class 1259 OID 22564)
-- Name: idx_campaigns_current_creators; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_campaigns_current_creators ON campaigns.campaigns USING btree (current_creators);


--
-- TOC entry 5149 (class 1259 OID 22563)
-- Name: idx_campaigns_current_gmv; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_campaigns_current_gmv ON campaigns.campaigns USING btree (current_gmv);


--
-- TOC entry 5150 (class 1259 OID 22451)
-- Name: idx_campaigns_dates; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_campaigns_dates ON campaigns.campaigns USING btree (start_date, end_date);


--
-- TOC entry 5151 (class 1259 OID 22631)
-- Name: idx_campaigns_payout_model; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_campaigns_payout_model ON campaigns.campaigns USING btree (payout_model);


--
-- TOC entry 5152 (class 1259 OID 22615)
-- Name: idx_campaigns_status; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_campaigns_status ON campaigns.campaigns USING btree (status);


--
-- TOC entry 5153 (class 1259 OID 23052)
-- Name: idx_campaigns_tiktok_product_links; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_campaigns_tiktok_product_links ON campaigns.campaigns USING gin (tiktok_product_links) WHERE (tiktok_product_links IS NOT NULL);


--
-- TOC entry 5154 (class 1259 OID 22647)
-- Name: idx_campaigns_tracking_method; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_campaigns_tracking_method ON campaigns.campaigns USING btree (tracking_method);


--
-- TOC entry 5155 (class 1259 OID 22565)
-- Name: idx_campaigns_type; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_campaigns_type ON campaigns.campaigns USING btree (type);


--
-- TOC entry 5166 (class 1259 OID 22452)
-- Name: idx_creator_applications_campaign_id; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_creator_applications_campaign_id ON campaigns.creator_applications USING btree (campaign_id);


--
-- TOC entry 5167 (class 1259 OID 22453)
-- Name: idx_creator_applications_creator_id; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_creator_applications_creator_id ON campaigns.creator_applications USING btree (creator_id);


--
-- TOC entry 5168 (class 1259 OID 22663)
-- Name: idx_creator_applications_status; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_creator_applications_status ON campaigns.creator_applications USING btree (status);


--
-- TOC entry 5171 (class 1259 OID 22455)
-- Name: idx_deliverables_application_id; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_deliverables_application_id ON campaigns.deliverables USING btree (application_id);


--
-- TOC entry 5172 (class 1259 OID 22457)
-- Name: idx_deliverables_due_date; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_deliverables_due_date ON campaigns.deliverables USING btree (due_date);


--
-- TOC entry 5173 (class 1259 OID 22673)
-- Name: idx_deliverables_status; Type: INDEX; Schema: campaigns; Owner: postgres
--

CREATE INDEX idx_deliverables_status ON campaigns.deliverables USING btree (status);


--
-- TOC entry 5208 (class 1259 OID 22467)
-- Name: idx_communication_logs_campaign; Type: INDEX; Schema: integrations; Owner: postgres
--

CREATE INDEX idx_communication_logs_campaign ON integrations.communication_logs USING btree (campaign_id);


--
-- TOC entry 5209 (class 1259 OID 22466)
-- Name: idx_communication_logs_recipient; Type: INDEX; Schema: integrations; Owner: postgres
--

CREATE INDEX idx_communication_logs_recipient ON integrations.communication_logs USING btree (recipient_id);


--
-- TOC entry 5193 (class 1259 OID 22463)
-- Name: idx_tiktok_sales_campaign_id; Type: INDEX; Schema: integrations; Owner: postgres
--

CREATE INDEX idx_tiktok_sales_campaign_id ON integrations.tiktok_shop_sales USING btree (campaign_id);


--
-- TOC entry 5194 (class 1259 OID 22464)
-- Name: idx_tiktok_sales_creator_id; Type: INDEX; Schema: integrations; Owner: postgres
--

CREATE INDEX idx_tiktok_sales_creator_id ON integrations.tiktok_shop_sales USING btree (creator_id);


--
-- TOC entry 5195 (class 1259 OID 22465)
-- Name: idx_tiktok_sales_date; Type: INDEX; Schema: integrations; Owner: postgres
--

CREATE INDEX idx_tiktok_sales_date ON integrations.tiktok_shop_sales USING btree (sale_date);


--
-- TOC entry 5176 (class 1259 OID 22459)
-- Name: idx_creator_earnings_campaign_id; Type: INDEX; Schema: payments; Owner: postgres
--

CREATE INDEX idx_creator_earnings_campaign_id ON payments.creator_earnings USING btree (campaign_id);


--
-- TOC entry 5177 (class 1259 OID 22458)
-- Name: idx_creator_earnings_creator_id; Type: INDEX; Schema: payments; Owner: postgres
--

CREATE INDEX idx_creator_earnings_creator_id ON payments.creator_earnings USING btree (creator_id);


--
-- TOC entry 5178 (class 1259 OID 22460)
-- Name: idx_payments_creator_id; Type: INDEX; Schema: payments; Owner: postgres
--

CREATE INDEX idx_payments_creator_id ON payments.payments USING btree (creator_id);


--
-- TOC entry 5179 (class 1259 OID 22462)
-- Name: idx_payments_dates; Type: INDEX; Schema: payments; Owner: postgres
--

CREATE INDEX idx_payments_dates ON payments.payments USING btree (initiated_at, completed_at);


--
-- TOC entry 5180 (class 1259 OID 22461)
-- Name: idx_payments_status; Type: INDEX; Schema: payments; Owner: postgres
--

CREATE INDEX idx_payments_status ON payments.payments USING btree (status);


--
-- TOC entry 5258 (class 1259 OID 23591)
-- Name: idx_creator_earnings_campaign_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_creator_earnings_campaign_id ON public.creator_earnings USING btree (campaign_id);


--
-- TOC entry 5267 (class 1259 OID 23594)
-- Name: idx_payment_schedules_campaign_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_payment_schedules_campaign_id ON public.payment_schedules USING btree (campaign_id);


--
-- TOC entry 5261 (class 1259 OID 23592)
-- Name: idx_payments_campaign_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_payments_campaign_id ON public.payments USING btree (campaign_id);


--
-- TOC entry 5264 (class 1259 OID 23593)
-- Name: idx_payments_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_payments_status ON public.payments USING btree (status);


--
-- TOC entry 5270 (class 1259 OID 23596)
-- Name: idx_referrals_referred_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_referrals_referred_id ON public.referrals USING btree (referred_id);


--
-- TOC entry 5271 (class 1259 OID 23595)
-- Name: idx_referrals_referrer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_referrals_referrer_id ON public.referrals USING btree (referrer_id);


--
-- TOC entry 5243 (class 1259 OID 23441)
-- Name: ix_auth_code_usage_auth_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_auth_code_usage_auth_code ON public.auth_code_usage USING btree (auth_code);


--
-- TOC entry 5276 (class 1259 OID 23640)
-- Name: ix_tiktok_accounts_tiktok_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_tiktok_accounts_tiktok_user_id ON public.tiktok_accounts USING btree (tiktok_user_id);


--
-- TOC entry 5277 (class 1259 OID 23639)
-- Name: ix_tiktok_accounts_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tiktok_accounts_user_id ON public.tiktok_accounts USING btree (user_id);


--
-- TOC entry 5247 (class 1259 OID 23469)
-- Name: ix_tiktok_orders_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_tiktok_orders_order_id ON public.tiktok_orders USING btree (order_id);


--
-- TOC entry 5244 (class 1259 OID 23455)
-- Name: ix_tiktok_products_product_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_tiktok_products_product_id ON public.tiktok_products USING btree (product_id);


--
-- TOC entry 5238 (class 1259 OID 23432)
-- Name: ix_tiktok_shops_shop_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_tiktok_shops_shop_id ON public.tiktok_shops USING btree (shop_id);


--
-- TOC entry 5252 (class 1259 OID 23497)
-- Name: ix_webhook_events_event_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_webhook_events_event_type ON public.webhook_events USING btree (event_type);


--
-- TOC entry 5253 (class 1259 OID 23496)
-- Name: ix_webhook_events_webhook_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_webhook_events_webhook_id ON public.webhook_events USING btree (webhook_id);


--
-- TOC entry 5220 (class 1259 OID 23010)
-- Name: idx_users_company_name; Type: INDEX; Schema: users; Owner: postgres
--

CREATE INDEX idx_users_company_name ON users.users USING btree (company_name);


--
-- TOC entry 5221 (class 1259 OID 23013)
-- Name: idx_users_email_verified; Type: INDEX; Schema: users; Owner: postgres
--

CREATE INDEX idx_users_email_verified ON users.users USING btree (email_verified);


--
-- TOC entry 5222 (class 1259 OID 23123)
-- Name: idx_users_role; Type: INDEX; Schema: users; Owner: postgres
--

CREATE INDEX idx_users_role ON users.users USING btree (role);


--
-- TOC entry 5223 (class 1259 OID 23011)
-- Name: idx_users_tiktok_handle; Type: INDEX; Schema: users; Owner: postgres
--

CREATE INDEX idx_users_tiktok_handle ON users.users USING btree (tiktok_handle);


--
-- TOC entry 5228 (class 1259 OID 22846)
-- Name: ix_user_tokens_expires_at; Type: INDEX; Schema: users; Owner: postgres
--

CREATE INDEX ix_user_tokens_expires_at ON users.user_tokens USING btree (expires_at);


--
-- TOC entry 5229 (class 1259 OID 22844)
-- Name: ix_user_tokens_user_id_type; Type: INDEX; Schema: users; Owner: postgres
--

CREATE INDEX ix_user_tokens_user_id_type ON users.user_tokens USING btree (user_id, token_type);


--
-- TOC entry 5230 (class 1259 OID 22845)
-- Name: ix_users_user_tokens_is_used; Type: INDEX; Schema: users; Owner: postgres
--

CREATE INDEX ix_users_user_tokens_is_used ON users.user_tokens USING btree (is_used);


--
-- TOC entry 5231 (class 1259 OID 22847)
-- Name: ix_users_user_tokens_token_value; Type: INDEX; Schema: users; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_user_tokens_token_value ON users.user_tokens USING btree (token_value);


--
-- TOC entry 5224 (class 1259 OID 22830)
-- Name: ix_users_users_email; Type: INDEX; Schema: users; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_users_email ON users.users USING btree (email);


--
-- TOC entry 5225 (class 1259 OID 22831)
-- Name: ix_users_users_username; Type: INDEX; Schema: users; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_users_username ON users.users USING btree (username);


--
-- TOC entry 5310 (class 2620 OID 22569)
-- Name: campaigns update_campaigns_updated_at; Type: TRIGGER; Schema: campaigns; Owner: postgres
--

CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns.campaigns FOR EACH ROW EXECUTE FUNCTION campaigns.update_campaign_updated_at();


--
-- TOC entry 5311 (class 2620 OID 22471)
-- Name: deliverables update_deliverables_updated_at; Type: TRIGGER; Schema: campaigns; Owner: postgres
--

CREATE TRIGGER update_deliverables_updated_at BEFORE UPDATE ON campaigns.deliverables FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5312 (class 2620 OID 23598)
-- Name: creator_earnings update_creator_earnings_last_updated; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_creator_earnings_last_updated BEFORE UPDATE ON public.creator_earnings FOR EACH ROW EXECUTE FUNCTION public.update_last_updated_column();


--
-- TOC entry 5300 (class 2606 OID 22416)
-- Name: campaign_performance_daily campaign_performance_daily_campaign_id_fkey; Type: FK CONSTRAINT; Schema: analytics; Owner: postgres
--

ALTER TABLE ONLY analytics.campaign_performance_daily
    ADD CONSTRAINT campaign_performance_daily_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id);


--
-- TOC entry 5301 (class 2606 OID 22443)
-- Name: creator_performance creator_performance_campaign_id_fkey; Type: FK CONSTRAINT; Schema: analytics; Owner: postgres
--

ALTER TABLE ONLY analytics.creator_performance
    ADD CONSTRAINT creator_performance_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id);


--
-- TOC entry 5280 (class 2606 OID 20617)
-- Name: campaign_products campaign_products_campaign_id_fkey; Type: FK CONSTRAINT; Schema: campaigns; Owner: postgres
--

ALTER TABLE ONLY campaigns.campaign_products
    ADD CONSTRAINT campaign_products_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id) ON DELETE CASCADE;


--
-- TOC entry 5281 (class 2606 OID 20638)
-- Name: campaign_segments campaign_segments_campaign_id_fkey; Type: FK CONSTRAINT; Schema: campaigns; Owner: postgres
--

ALTER TABLE ONLY campaigns.campaign_segments
    ADD CONSTRAINT campaign_segments_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id) ON DELETE CASCADE;


--
-- TOC entry 5284 (class 2606 OID 20682)
-- Name: creator_applications creator_applications_campaign_id_fkey; Type: FK CONSTRAINT; Schema: campaigns; Owner: postgres
--

ALTER TABLE ONLY campaigns.creator_applications
    ADD CONSTRAINT creator_applications_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id) ON DELETE CASCADE;


--
-- TOC entry 5285 (class 2606 OID 20697)
-- Name: creator_applications creator_applications_segment_id_fkey; Type: FK CONSTRAINT; Schema: campaigns; Owner: postgres
--

ALTER TABLE ONLY campaigns.creator_applications
    ADD CONSTRAINT creator_applications_segment_id_fkey FOREIGN KEY (segment_id) REFERENCES campaigns.campaign_segments(id);


--
-- TOC entry 5286 (class 2606 OID 20720)
-- Name: deliverables deliverables_application_id_fkey; Type: FK CONSTRAINT; Schema: campaigns; Owner: postgres
--

ALTER TABLE ONLY campaigns.deliverables
    ADD CONSTRAINT deliverables_application_id_fkey FOREIGN KEY (application_id) REFERENCES campaigns.creator_applications(id) ON DELETE CASCADE;


--
-- TOC entry 5287 (class 2606 OID 22700)
-- Name: deliverables fk_deliverables_campaign_id; Type: FK CONSTRAINT; Schema: campaigns; Owner: postgres
--

ALTER TABLE ONLY campaigns.deliverables
    ADD CONSTRAINT fk_deliverables_campaign_id FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id);


--
-- TOC entry 5282 (class 2606 OID 20648)
-- Name: gmv_bonus_tiers gmv_bonus_tiers_campaign_id_fkey; Type: FK CONSTRAINT; Schema: campaigns; Owner: postgres
--

ALTER TABLE ONLY campaigns.gmv_bonus_tiers
    ADD CONSTRAINT gmv_bonus_tiers_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id) ON DELETE CASCADE;


--
-- TOC entry 5283 (class 2606 OID 20660)
-- Name: leaderboard_bonuses leaderboard_bonuses_campaign_id_fkey; Type: FK CONSTRAINT; Schema: campaigns; Owner: postgres
--

ALTER TABLE ONLY campaigns.leaderboard_bonuses
    ADD CONSTRAINT leaderboard_bonuses_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id) ON DELETE CASCADE;


--
-- TOC entry 5299 (class 2606 OID 22386)
-- Name: communication_logs communication_logs_campaign_id_fkey; Type: FK CONSTRAINT; Schema: integrations; Owner: postgres
--

ALTER TABLE ONLY integrations.communication_logs
    ADD CONSTRAINT communication_logs_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id);


--
-- TOC entry 5297 (class 2606 OID 22356)
-- Name: creator_discord_roles creator_discord_roles_campaign_id_fkey; Type: FK CONSTRAINT; Schema: integrations; Owner: postgres
--

ALTER TABLE ONLY integrations.creator_discord_roles
    ADD CONSTRAINT creator_discord_roles_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id);


--
-- TOC entry 5298 (class 2606 OID 22361)
-- Name: creator_discord_roles creator_discord_roles_discord_role_id_fkey; Type: FK CONSTRAINT; Schema: integrations; Owner: postgres
--

ALTER TABLE ONLY integrations.creator_discord_roles
    ADD CONSTRAINT creator_discord_roles_discord_role_id_fkey FOREIGN KEY (discord_role_id) REFERENCES integrations.discord_roles(id);


--
-- TOC entry 5296 (class 2606 OID 22336)
-- Name: discord_roles discord_roles_campaign_id_fkey; Type: FK CONSTRAINT; Schema: integrations; Owner: postgres
--

ALTER TABLE ONLY integrations.discord_roles
    ADD CONSTRAINT discord_roles_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id);


--
-- TOC entry 5294 (class 2606 OID 22312)
-- Name: tiktok_shop_sales tiktok_shop_sales_campaign_id_fkey; Type: FK CONSTRAINT; Schema: integrations; Owner: postgres
--

ALTER TABLE ONLY integrations.tiktok_shop_sales
    ADD CONSTRAINT tiktok_shop_sales_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id);


--
-- TOC entry 5295 (class 2606 OID 22322)
-- Name: tiktok_shop_sales tiktok_shop_sales_deliverable_id_fkey; Type: FK CONSTRAINT; Schema: integrations; Owner: postgres
--

ALTER TABLE ONLY integrations.tiktok_shop_sales
    ADD CONSTRAINT tiktok_shop_sales_deliverable_id_fkey FOREIGN KEY (deliverable_id) REFERENCES campaigns.deliverables(id);


--
-- TOC entry 5288 (class 2606 OID 22184)
-- Name: creator_earnings creator_earnings_application_id_fkey; Type: FK CONSTRAINT; Schema: payments; Owner: postgres
--

ALTER TABLE ONLY payments.creator_earnings
    ADD CONSTRAINT creator_earnings_application_id_fkey FOREIGN KEY (application_id) REFERENCES campaigns.creator_applications(id);


--
-- TOC entry 5289 (class 2606 OID 22179)
-- Name: creator_earnings creator_earnings_campaign_id_fkey; Type: FK CONSTRAINT; Schema: payments; Owner: postgres
--

ALTER TABLE ONLY payments.creator_earnings
    ADD CONSTRAINT creator_earnings_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id);


--
-- TOC entry 5292 (class 2606 OID 22227)
-- Name: payment_schedules payment_schedules_campaign_id_fkey; Type: FK CONSTRAINT; Schema: payments; Owner: postgres
--

ALTER TABLE ONLY payments.payment_schedules
    ADD CONSTRAINT payment_schedules_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id);


--
-- TOC entry 5290 (class 2606 OID 22204)
-- Name: payments payments_campaign_id_fkey; Type: FK CONSTRAINT; Schema: payments; Owner: postgres
--

ALTER TABLE ONLY payments.payments
    ADD CONSTRAINT payments_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id);


--
-- TOC entry 5291 (class 2606 OID 22209)
-- Name: payments payments_earning_id_fkey; Type: FK CONSTRAINT; Schema: payments; Owner: postgres
--

ALTER TABLE ONLY payments.payments
    ADD CONSTRAINT payments_earning_id_fkey FOREIGN KEY (earning_id) REFERENCES payments.creator_earnings(id);


--
-- TOC entry 5293 (class 2606 OID 22253)
-- Name: referrals referrals_campaign_id_fkey; Type: FK CONSTRAINT; Schema: payments; Owner: postgres
--

ALTER TABLE ONLY payments.referrals
    ADD CONSTRAINT referrals_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES campaigns.campaigns(id);


--
-- TOC entry 5309 (class 2606 OID 23562)
-- Name: payments payments_earning_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_earning_id_fkey FOREIGN KEY (earning_id) REFERENCES public.creator_earnings(id) ON DELETE SET NULL;


--
-- TOC entry 5307 (class 2606 OID 23478)
-- Name: sync_operations sync_operations_shop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sync_operations
    ADD CONSTRAINT sync_operations_shop_id_fkey FOREIGN KEY (shop_id) REFERENCES public.tiktok_shops(shop_id);


--
-- TOC entry 5306 (class 2606 OID 23464)
-- Name: tiktok_orders tiktok_orders_shop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tiktok_orders
    ADD CONSTRAINT tiktok_orders_shop_id_fkey FOREIGN KEY (shop_id) REFERENCES public.tiktok_shops(shop_id);


--
-- TOC entry 5305 (class 2606 OID 23450)
-- Name: tiktok_products tiktok_products_shop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tiktok_products
    ADD CONSTRAINT tiktok_products_shop_id_fkey FOREIGN KEY (shop_id) REFERENCES public.tiktok_shops(shop_id);


--
-- TOC entry 5308 (class 2606 OID 23491)
-- Name: webhook_events webhook_events_shop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webhook_events
    ADD CONSTRAINT webhook_events_shop_id_fkey FOREIGN KEY (shop_id) REFERENCES public.tiktok_shops(shop_id);


--
-- TOC entry 5303 (class 2606 OID 22853)
-- Name: creator_audience_demographics creator_audience_demographics_creator_id_fkey; Type: FK CONSTRAINT; Schema: users; Owner: postgres
--

ALTER TABLE ONLY users.creator_audience_demographics
    ADD CONSTRAINT creator_audience_demographics_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES users.users(id) ON DELETE CASCADE;


--
-- TOC entry 5304 (class 2606 OID 22865)
-- Name: creator_badges creator_badges_creator_id_fkey; Type: FK CONSTRAINT; Schema: users; Owner: postgres
--

ALTER TABLE ONLY users.creator_badges
    ADD CONSTRAINT creator_badges_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES users.users(id) ON DELETE CASCADE;


--
-- TOC entry 5302 (class 2606 OID 22839)
-- Name: user_tokens user_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: users; Owner: postgres
--

ALTER TABLE ONLY users.user_tokens
    ADD CONSTRAINT user_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES users.users(id) ON DELETE CASCADE;


-- Completed on 2025-07-19 12:21:56

--
-- PostgreSQL database dump complete
--

