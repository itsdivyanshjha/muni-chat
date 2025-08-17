-- Database initialization script for Municipal AI Insights
-- Creates users, grants permissions, and adds seed data

-- Create roles
CREATE ROLE app_owner WITH LOGIN PASSWORD 'owner_pass';
CREATE ROLE app_readonly WITH LOGIN PASSWORD 'readonly_pass';

-- Grant necessary permissions to app_owner
GRANT CREATE, CONNECT ON DATABASE muni TO app_owner;
GRANT CREATE ON SCHEMA public TO app_owner;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_owner;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_owner;

-- Grant read-only permissions to app_readonly
GRANT CONNECT ON DATABASE muni TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_owner;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO app_owner;
