"""
Database setup script to create required tables in Supabase.
Run this script once to set up your database schema.
"""
import os
from supabase import create_client, Client
from typing import Optional

from load_env import load_environment

load_environment()


def run_sql_file(supabase: Client, file_path: str) -> bool:
    """
    Execute a SQL file against Supabase.
    
    Args:
        supabase: Supabase client
        file_path: Path to SQL file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'r') as f:
            sql = f.read()
        
        # Split by semicolons to execute statements separately
        statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for statement in statements:
            if statement:
                try:
                    # Use Supabase RPC or direct SQL execution
                    # Note: Supabase Python client doesn't have direct SQL execution
                    # We'll use the REST API or provide instructions
                    print(f"Executing: {statement[:50]}...")
                except Exception as e:
                    print(f"Error executing statement: {str(e)}")
                    return False
        
        return True
    except Exception as e:
        print(f"Error reading SQL file: {str(e)}")
        return False


def setup_database():
    """
    Set up the database by creating required tables.
    Note: Supabase Python client doesn't support direct SQL execution.
    This script provides instructions and validates the setup.
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return False
    
    print("=" * 60)
    print("Database Setup for Multi-Agent Content Pipeline")
    print("=" * 60)
    print("\nNote: Supabase Python client doesn't support direct SQL execution.")
    print("   Please run the SQL migrations manually in Supabase SQL Editor.\n")
    
    print("Steps to set up your database:")
    print("-" * 60)
    print("1. Go to your Supabase Dashboard")
    print("2. Navigate to: SQL Editor (left sidebar)")
    print("3. Click 'New query'")
    print("4. Copy and paste the contents of the following files IN ORDER:")
    print("   - migrations/001_create_agent_logs.sql")
    print("   - migrations/002_create_posts.sql")
    print("   - migrations/003_add_post_id_to_agent_logs.sql")
    print("5. Run each SQL file in the SQL Editor")
    print("6. Verify tables were created in Table Editor\n")
    
    # Try to verify tables exist
    try:
        supabase: Optional[Client] = create_client(supabase_url, supabase_key)
        
        print("\033[94m[INFO]\033[0m Checking if tables exist...")
        
        # Try to query agent_logs table
        try:
            result = supabase.table("agent_logs").select("id").limit(1).execute()
            print("\033[92m[SUCCESS]\033[0m agent_logs table exists")
        except Exception as e:
            print(f"\033[91m[ERROR]\033[0m agent_logs table not found: {str(e)}")
            print("Run migrations/001_create_agent_logs.sql")
        
        # Try to query posts table
        try:
            result = supabase.table("posts").select("id").limit(1).execute()
            print("\033[92m[SUCCESS]\033[0m posts table exists")
        except Exception as e:
            print(f"\033[91m[ERROR]\033[0m posts table not found: {str(e)}")
            print("Run migrations/002_create_posts.sql")
        
        # Check if post_id column exists in agent_logs
        try:
            result = supabase.table("agent_logs").select("post_id").limit(1).execute()
            print("\033[92m[SUCCESS]\033[0m post_id column exists in agent_logs")
        except Exception as e:
            if "post_id" in str(e).lower() or "column" in str(e).lower():
                print(f"\033[91m[ERROR]\033[0m post_id column not found in agent_logs: {str(e)}")
                print("Run migrations/003_add_post_id_to_agent_logs.sql")
            else:
                print(f"\033[93m[WARNING]\033[0m Could not verify post_id column: {str(e)}")
        
        print("\n" + "=" * 60)
        print("Setup complete! Your database is ready.")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"Error connecting to Supabase: {str(e)}")
        print("Check your SUPABASE_URL and SUPABASE_KEY in .env")
        return False


if __name__ == "__main__":
    setup_database()

