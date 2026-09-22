-- Create agent_logs table for logging agent outputs and metrics
CREATE TABLE IF NOT EXISTS public.agent_logs (
    id BIGSERIAL PRIMARY KEY,
    agent TEXT NOT NULL,
    input TEXT NOT NULL,
    output TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB
);

-- Create index on agent for faster queries
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent ON public.agent_logs(agent);

-- Create index on timestamp for time-based queries
CREATE INDEX IF NOT EXISTS idx_agent_logs_timestamp ON public.agent_logs(timestamp);

-- Enable Row Level Security (optional - can be disabled for development)
ALTER TABLE public.agent_logs ENABLE ROW LEVEL SECURITY;

-- Create policy to allow inserts (adjust as needed for your security requirements)
CREATE POLICY "Allow all inserts to agent_logs"
ON public.agent_logs
FOR INSERT
TO public
WITH CHECK (true);

-- Create policy to allow selects (adjust as needed)
CREATE POLICY "Allow all selects from agent_logs"
ON public.agent_logs
FOR SELECT
TO public
USING (true);

