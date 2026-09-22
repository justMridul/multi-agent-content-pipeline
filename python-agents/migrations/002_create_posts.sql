-- Create posts table for storing final blog posts
CREATE TABLE IF NOT EXISTS public.posts (
    id BIGSERIAL PRIMARY KEY,
    prd TEXT NOT NULL,
    final_post TEXT NOT NULL
);

-- Create index on id (already indexed as primary key, but explicit for clarity)
-- Note: Primary key already creates an index automatically

-- Enable Row Level Security (optional - can be disabled for development)
ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;

-- Create policy to allow inserts (adjust as needed for your security requirements)
CREATE POLICY "Allow all inserts to posts"
ON public.posts
FOR INSERT
TO public
WITH CHECK (true);

-- Create policy to allow selects (adjust as needed)
CREATE POLICY "Allow all selects from posts"
ON public.posts
FOR SELECT
TO public
USING (true);

