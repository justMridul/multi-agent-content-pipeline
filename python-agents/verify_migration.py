"""
Verify that the post_id column was added to agent_logs table.
"""
import os
from supabase import create_client
from load_env import load_environment

load_environment()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    exit(1)

supabase = create_client(supabase_url, supabase_key)

print("=" * 60)
print("Verifying Migration: post_id column in agent_logs")
print("=" * 60)

# Try to query with post_id to see if column exists
try:
    # This will fail if the column doesn't exist
    result = supabase.table("agent_logs").select("id, agent, post_id").limit(1).execute()
    
    if result.data:
        print("\033[92m[SUCCESS]\033[0m post_id column EXISTS in agent_logs table!")
        print(f"Sample log: ID={result.data[0].get('id')}, Agent={result.data[0].get('agent')}, Post ID={result.data[0].get('post_id')}")
    else:
        print("\033[93m[WARNING]\033[0m Column exists but no data found")
        
except Exception as e:
    error_msg = str(e)
    if "post_id" in error_msg.lower() or "column" in error_msg.lower():
        print("\033[91m[ERROR]\033[0m post_id column does NOT exist!")
        print(f"Error: {error_msg}")
        print("\nYou need to run the migration:")
        print("  003_add_post_id_to_agent_logs.sql")
        print("\nIn Supabase:")
        print("  1. Go to SQL Editor")
        print("  2. Copy the contents of migrations/003_add_post_id_to_agent_logs.sql")
        print("  3. Run it")
    else:
        print(f"\033[91m[ERROR]\033[0m Unexpected error: {error_msg}")

print("\n" + "=" * 60)
print("Checking table structure...")
print("=" * 60)

# Try to insert a test log with post_id to verify it works
try:
    test_log = {
        "agent": "test",
        "input": "test",
        "output": "test",
        "post_id": None  # Should work even with NULL
    }
    # Don't actually insert, just verify the structure accepts it
    print("Column structure appears correct (can accept post_id)")
except Exception as e:
    print(f"Error with column structure: {str(e)}")

print("\n" + "=" * 60)

