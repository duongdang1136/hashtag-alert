-- TikTok Hashtag Alert Bot - Database Schema
-- Run this in Supabase SQL Editor

-- Table: tracked_creators
-- Stores TikTok creators being monitored
CREATE TABLE IF NOT EXISTS tracked_creators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tiktok_username TEXT NOT NULL UNIQUE,
    tiktok_user_id TEXT,
    added_by_telegram_user BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_tracked_creators_username ON tracked_creators(tiktok_username);
CREATE INDEX IF NOT EXISTS idx_tracked_creators_active ON tracked_creators(is_active) WHERE is_active = TRUE;

-- Table: posts
-- Stores historical posts to prevent duplicate alerts
CREATE TABLE IF NOT EXISTS posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creator_id UUID REFERENCES tracked_creators(id) ON DELETE CASCADE,
    tiktok_post_id TEXT NOT NULL UNIQUE,
    post_url TEXT NOT NULL,
    description TEXT,
    hashtags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_posts_creator_id ON posts(creator_id);
CREATE INDEX IF NOT EXISTS idx_posts_tiktok_post_id ON posts(tiktok_post_id);
CREATE INDEX IF NOT EXISTS idx_posts_scraped_at ON posts(scraped_at DESC);

-- Table: bot_users
-- Stores Telegram users subscribed to alerts
CREATE TABLE IF NOT EXISTS bot_users (
    telegram_user_id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Index for active users
CREATE INDEX IF NOT EXISTS idx_bot_users_active ON bot_users(is_active) WHERE is_active = TRUE;

-- View: creator_stats
-- Helpful view for monitoring
CREATE OR REPLACE VIEW creator_stats AS
SELECT 
    tc.tiktok_username,
    tc.added_by_telegram_user,
    tc.created_at,
    COUNT(p.id) as total_posts,
    MAX(p.created_at) as latest_post_date
FROM tracked_creators tc
LEFT JOIN posts p ON tc.id = p.creator_id
WHERE tc.is_active = TRUE
GROUP BY tc.id, tc.tiktok_username, tc.added_by_telegram_user, tc.created_at
ORDER BY latest_post_date DESC NULLS LAST;
