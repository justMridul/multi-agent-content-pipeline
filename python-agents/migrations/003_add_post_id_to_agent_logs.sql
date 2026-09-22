-- Add post_id column to agent_logs table to link logs to posts
-- This allows proper tracking of which logs belong to which post

-- Add post_id column (nullable for backward compatibility with existing logs)
ALTER TABLE public.agent_logs 
ADD COLUMN IF NOT EXISTS post_id BIGINT;

-- Create index on post_id for faster queries
CREATE INDEX IF NOT EXISTS idx_agent_logs_post_id ON public.agent_logs(post_id);

-- Add foreign key constraint (optional, but recommended for data integrity)
-- Note: This will fail if there are existing logs with invalid post_ids
-- You may want to clean up existing data first, or make this nullable and add it later
-- ALTER TABLE public.agent_logs
-- ADD CONSTRAINT fk_agent_logs_post_id 
-- FOREIGN KEY (post_id) REFERENCES public.posts(id) ON DELETE CASCADE;

-- Add comment to document the column
COMMENT ON COLUMN public.agent_logs.post_id IS 'Foreign key to posts table. Links agent logs to their corresponding post.';

