-- Database Initialization Script
-- This script performs the same operations as init-db.sh
-- Run with: psql -U <username> -d <database> -f init-db.sql

-- ============================================
-- Create Tables
-- ============================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(80),
    biography TEXT,
    avatar_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Campaigns members (many-to-many relationship)
CREATE TABLE IF NOT EXISTS campaign_members (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, campaign_id)
);

-- Posts table
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comments table
CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Images table
CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    description TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Campaign invites table
CREATE TABLE IF NOT EXISTS campaign_invites (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    inviter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invitee_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP
);

-- Characters table
CREATE TABLE IF NOT EXISTS characters (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    race VARCHAR(50) NOT NULL,
    character_class VARCHAR(50) NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Post viewed status (many-to-many relationship)
CREATE TABLE IF NOT EXISTS post_viewed_status (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, post_id)
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    related_post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    related_comment_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    related_invite_id INTEGER REFERENCES campaign_invites(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Conditional Column Additions
-- ============================================

-- Add related_comment_id to notifications if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'notifications' AND column_name = 'related_comment_id'
    ) THEN
        ALTER TABLE notifications ADD COLUMN related_comment_id INTEGER REFERENCES comments(id);
        RAISE NOTICE 'Added related_comment_id column to notifications table';
    ELSE
        RAISE NOTICE 'related_comment_id column already exists in notifications table';
    END IF;
END $$;

-- Add related_invite_id to notifications if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'notifications' AND column_name = 'related_invite_id'
    ) THEN
        ALTER TABLE notifications ADD COLUMN related_invite_id INTEGER REFERENCES campaign_invites(id) ON DELETE CASCADE;
        RAISE NOTICE 'Added related_invite_id column to notifications table';
    ELSE
        RAISE NOTICE 'related_invite_id column already exists in notifications table';
    END IF;
END $$;

-- Add post_order to posts if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'posts' AND column_name = 'post_order'
    ) THEN
        ALTER TABLE posts ADD COLUMN post_order INTEGER;
        CREATE INDEX ix_posts_post_order ON posts(post_order);
        RAISE NOTICE 'Added post_order column to posts table';
    ELSE
        RAISE NOTICE 'post_order column already exists in posts table';
    END IF;
END $$;

-- Add importance_level to posts if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'posts' AND column_name = 'importance_level'
    ) THEN
        ALTER TABLE posts ADD COLUMN importance_level INTEGER NOT NULL DEFAULT 0;
        RAISE NOTICE 'Added importance_level column to posts table';
    ELSE
        RAISE NOTICE 'importance_level column already exists in posts table';
    END IF;
END $$;

-- Add description to images if it doesn't exist
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'images'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'images' AND column_name = 'description'
    ) THEN
        ALTER TABLE images ADD COLUMN description TEXT;
        RAISE NOTICE 'Added description column to images table';
    ELSIF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'images'
    ) THEN
        RAISE NOTICE 'description column already exists in images table';
    ELSE
        RAISE NOTICE 'images table does not exist';
    END IF;
END $$;

-- Add order_index to images if it doesn't exist
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'images'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'images' AND column_name = 'order_index'
    ) THEN
        ALTER TABLE images ADD COLUMN order_index INTEGER DEFAULT 0;
        RAISE NOTICE 'Added order_index column to images table';
    ELSIF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'images'
    ) THEN
        RAISE NOTICE 'order_index column already exists in images table';
    ELSE
        RAISE NOTICE 'images table does not exist';
    END IF;
END $$;

-- Add character_creation_mode to campaigns if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'campaigns' AND column_name = 'character_creation_mode'
    ) THEN
        ALTER TABLE campaigns ADD COLUMN character_creation_mode VARCHAR(20) NOT NULL DEFAULT 'optional';
        RAISE NOTICE 'Added character_creation_mode column to campaigns table';
    ELSE
        RAISE NOTICE 'character_creation_mode column already exists in campaigns table';
    END IF;
END $$;

-- Add is_predefined to characters if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'characters' AND column_name = 'is_predefined'
    ) THEN
        ALTER TABLE characters ADD COLUMN is_predefined BOOLEAN NOT NULL DEFAULT FALSE;
        RAISE NOTICE 'Added is_predefined column to characters table';
    ELSE
        RAISE NOTICE 'is_predefined column already exists in characters table';
    END IF;
END $$;

-- Add assigned_to_user_id to characters if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'characters' AND column_name = 'assigned_to_user_id'
    ) THEN
        ALTER TABLE characters ADD COLUMN assigned_to_user_id INTEGER REFERENCES users(id);
        RAISE NOTICE 'Added assigned_to_user_id column to characters table';
    ELSE
        RAISE NOTICE 'assigned_to_user_id column already exists in characters table';
    END IF;
END $$;

-- Add is_hidden to posts if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'posts' AND column_name = 'is_hidden'
    ) THEN
        ALTER TABLE posts ADD COLUMN is_hidden BOOLEAN NOT NULL DEFAULT FALSE;
        RAISE NOTICE 'Added is_hidden column to posts table';
    ELSE
        RAISE NOTICE 'is_hidden column already exists in posts table';
    END IF;
END $$;

-- Add nickname to users if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'nickname'
    ) THEN
        ALTER TABLE users ADD COLUMN nickname VARCHAR(80);
        RAISE NOTICE 'Added nickname column to users table';
    ELSE
        RAISE NOTICE 'nickname column already exists in users table';
    END IF;
END $$;

-- Add biography to users if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'biography'
    ) THEN
        ALTER TABLE users ADD COLUMN biography TEXT;
        RAISE NOTICE 'Added biography column to users table';
    ELSE
        RAISE NOTICE 'biography column already exists in users table';
    END IF;
END $$;

-- Add avatar_url to users if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'avatar_url'
    ) THEN
        ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500);
        RAISE NOTICE 'Added avatar_url column to users table';
    ELSE
        RAISE NOTICE 'avatar_url column already exists in users table';
    END IF;
END $$;

-- ============================================
-- Backfill post_order values for existing posts
-- ============================================
DO $$
DECLARE
    campaign_record RECORD;
    post_record RECORD;
    post_order_val INTEGER;
BEGIN
    -- Check if there are posts without post_order
    IF EXISTS (SELECT 1 FROM posts WHERE post_order IS NULL) THEN
        RAISE NOTICE 'Backfilling post_order values for existing posts...';
        
        FOR campaign_record IN SELECT id FROM campaigns ORDER BY id LOOP
            post_order_val := 0;
            FOR post_record IN 
                SELECT id FROM posts 
                WHERE campaign_id = campaign_record.id 
                ORDER BY created_at
            LOOP
                post_order_val := post_order_val + 1;
                UPDATE posts SET post_order = post_order_val WHERE id = post_record.id;
            END LOOP;
        END LOOP;
        
        RAISE NOTICE 'post_order values backfilled for existing posts';
    ELSE
        RAISE NOTICE 'All posts already have post_order values';
    END IF;
END $$;

-- ============================================
-- Create Admin User
-- ============================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin') THEN
        -- Note: Replace 'admin123' with your actual admin password
        -- The password hash below is for 'admin123' using werkzeug's default pbkdf2:sha256
        INSERT INTO users (username, email, password_hash, created_at)
        VALUES (
            'admin',
            'admin@dndbook.local',
            'scrypt:32768:8:1$Wu94BDi5qO9CMVj7$2fb491da1b839649e108ac6ed977a073a31a6fe10273acd0971f652c4bde1e6662092355af9f7e4bcf2d2411069ea9bce70dced27759827359c4874db83af56f',
            CURRENT_TIMESTAMP
        );
        RAISE NOTICE 'Admin user created (username: admin, password: admin123)';
        RAISE NOTICE 'IMPORTANT: Change the default password after first login!';
    ELSE
        RAISE NOTICE 'Admin user already exists';
    END IF;
END $$;

-- ============================================
-- Completion Message
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '====================================';
    RAISE NOTICE 'Database initialization complete!';
    RAISE NOTICE '====================================';
END $$;
