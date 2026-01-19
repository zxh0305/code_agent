-- Database initialization script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    avatar_url TEXT,
    github_id INTEGER UNIQUE,
    github_username VARCHAR(255),
    github_access_token TEXT,
    github_refresh_token TEXT,
    github_token_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

-- Create repositories table
CREATE TABLE IF NOT EXISTS repositories (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    github_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    full_name VARCHAR(512) NOT NULL,
    description TEXT,
    html_url TEXT NOT NULL,
    clone_url TEXT NOT NULL,
    ssh_url TEXT,
    default_branch VARCHAR(255) DEFAULT 'main',
    is_private BOOLEAN DEFAULT FALSE,
    is_fork BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    local_path TEXT,
    last_synced_at TIMESTAMP,
    stars_count INTEGER DEFAULT 0,
    forks_count INTEGER DEFAULT 0,
    watchers_count INTEGER DEFAULT 0,
    open_issues_count INTEGER DEFAULT 0,
    language VARCHAR(100),
    languages JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    github_created_at TIMESTAMP,
    github_updated_at TIMESTAMP
);

-- Create branches table
CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY,
    repository_id INTEGER REFERENCES repositories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    sha VARCHAR(40) NOT NULL,
    is_protected BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create pull_requests table
CREATE TABLE IF NOT EXISTS pull_requests (
    id SERIAL PRIMARY KEY,
    repository_id INTEGER REFERENCES repositories(id) ON DELETE CASCADE,
    creator_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    github_id INTEGER UNIQUE NOT NULL,
    number INTEGER NOT NULL,
    title VARCHAR(512) NOT NULL,
    body TEXT,
    html_url TEXT NOT NULL,
    head_branch VARCHAR(255) NOT NULL,
    head_sha VARCHAR(40),
    base_branch VARCHAR(255) NOT NULL,
    base_sha VARCHAR(40),
    status VARCHAR(20) DEFAULT 'open',
    review_status VARCHAR(30) DEFAULT 'pending',
    is_draft BOOLEAN DEFAULT FALSE,
    is_mergeable BOOLEAN,
    mergeable_state VARCHAR(50),
    commits_count INTEGER DEFAULT 0,
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    changed_files INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    review_comments_count INTEGER DEFAULT 0,
    ai_generated BOOLEAN DEFAULT FALSE,
    ai_model_used VARCHAR(100),
    ai_prompt TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    github_created_at TIMESTAMP,
    github_updated_at TIMESTAMP,
    merged_at TIMESTAMP,
    closed_at TIMESTAMP
);

-- Create pr_comments table
CREATE TABLE IF NOT EXISTS pr_comments (
    id SERIAL PRIMARY KEY,
    pull_request_id INTEGER REFERENCES pull_requests(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    github_id INTEGER UNIQUE NOT NULL,
    body TEXT NOT NULL,
    path TEXT,
    position INTEGER,
    line INTEGER,
    is_ai_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create code_analyses table
CREATE TABLE IF NOT EXISTS code_analyses (
    id SERIAL PRIMARY KEY,
    repository_id INTEGER REFERENCES repositories(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    language VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    ast_structure JSONB,
    code_structure JSONB,
    dependencies JSONB,
    metrics JSONB,
    issues JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create ai_interactions table
CREATE TABLE IF NOT EXISTS ai_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    repository_id INTEGER REFERENCES repositories(id) ON DELETE SET NULL,
    model_name VARCHAR(100) NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    context_type VARCHAR(50),
    context_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_github_id ON users(github_id);
CREATE INDEX IF NOT EXISTS idx_repositories_owner_id ON repositories(owner_id);
CREATE INDEX IF NOT EXISTS idx_repositories_github_id ON repositories(github_id);
CREATE INDEX IF NOT EXISTS idx_pull_requests_repository_id ON pull_requests(repository_id);
CREATE INDEX IF NOT EXISTS idx_pull_requests_github_id ON pull_requests(github_id);
CREATE INDEX IF NOT EXISTS idx_code_analyses_repository_id ON code_analyses(repository_id);
CREATE INDEX IF NOT EXISTS idx_ai_interactions_user_id ON ai_interactions(user_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN
        SELECT table_name
        FROM information_schema.columns
        WHERE column_name = 'updated_at'
        AND table_schema = 'public'
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS update_%s_updated_at ON %s', t, t);
        EXECUTE format('CREATE TRIGGER update_%s_updated_at BEFORE UPDATE ON %s FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()', t, t);
    END LOOP;
END;
$$ LANGUAGE plpgsql;
