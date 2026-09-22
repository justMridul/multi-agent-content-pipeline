# Database Migrations

This directory contains SQL migration files to set up the required database tables.

## Quick Setup

### Option 1: Using Supabase SQL Editor (Recommended)

1. Go to your Supabase Dashboard: https://app.supabase.com
2. Select your project
3. Navigate to **SQL Editor** (left sidebar)
4. Click **New query**
5. Copy and paste the contents of each migration file in order:
   - `001_create_agent_logs.sql`
   - `002_create_posts.sql`
6. Click **Run** (or press Cmd/Ctrl + Enter)
7. Verify tables were created in **Table Editor**

### Option 2: Using the Setup Script

Run the setup script to get instructions and verify your setup:

```bash
cd python-agents
python setup_database.py
```

## Migration Files

### 001_create_agent_logs.sql
Creates the `agent_logs` table for logging agent outputs and metrics.

**Schema:**
- `id` (BIGSERIAL, PRIMARY KEY)
- `agent` (TEXT) - Agent name (researcher, writer, fact_checker, polisher)
- `input` (TEXT) - Agent input
- `output` (TEXT) - Agent output
- `timestamp` (TIMESTAMPTZ) - When the log was created
- `metadata` (JSONB) - Additional metrics and data

### 002_create_posts.sql
Creates the `posts` table for storing final blog posts.

**Schema:**
- `id` (BIGSERIAL, PRIMARY KEY)
- `prd` (TEXT) - Product Requirements Document
- `final_post` (TEXT) - Final polished blog post

### 003_add_post_id_to_agent_logs.sql
Adds `post_id` column to `agent_logs` table to link logs to posts.

**What it does:**
- Adds nullable `post_id` (BIGINT) column to `agent_logs`
- Creates index on `post_id` for faster queries
- Allows proper tracking of which logs belong to which post

**Important:** Run this migration after `001_create_agent_logs.sql` and `002_create_posts.sql`.

## Row Level Security (RLS)

Both tables have RLS enabled with policies that allow:
- **INSERT**: All inserts (adjust for production)
- **SELECT**: All selects (adjust for production)

For production, you may want to:
- Restrict INSERT to authenticated users
- Restrict SELECT to specific users or roles
- Add UPDATE/DELETE policies if needed

## Troubleshooting

If you get permission errors:
1. Check that RLS policies are created correctly
2. Verify you're using the correct Supabase key (service role key for backend)
3. Check the Supabase Dashboard → Table Editor → Policies tab

