"""
Quick script to check if agent_logs exist and if they have post_id set.
Run this to debug why logs aren't showing up in the timeline.
"""
import os
from supabase import create_client, Client
from load_env import load_environment

load_environment()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    exit(1)

supabase = create_client(supabase_url, supabase_key)

# Check posts
print("=" * 60)
print("Checking Posts")
print("=" * 60)
posts = supabase.table("posts").select("id, prd").order("id", desc=True).limit(5).execute()
if posts.data:
    print(f"Found {len(posts.data)} recent posts:")
    for post in posts.data:
        print(f"  Post ID: {post['id']}, PRD length: {len(post.get('prd', ''))}")
else:
    print("No posts found")

# Check agent_logs
print("\n" + "=" * 60)
print("Checking Agent Logs")
print("=" * 60)
all_logs = supabase.table("agent_logs").select("id, agent, post_id, timestamp").order("timestamp", desc=True).limit(10).execute()
if all_logs.data:
    print(f"Found {len(all_logs.data)} recent logs:")
    for log in all_logs.data:
        post_id = log.get('post_id')
        post_id_str = str(post_id) if post_id is not None else "NULL"
        print(f"  Log ID: {log['id']}, Agent: {log['agent']}, Post ID: {post_id_str}, Time: {log['timestamp']}")
else:
    print("No logs found")

# Check logs for specific post
print("\n" + "=" * 60)
print("Checking Logs for Post ID 5")
print("=" * 60)
post_5_logs = supabase.table("agent_logs").select("*").eq("post_id", 5).execute()
if post_5_logs.data:
    print(f"Found {len(post_5_logs.data)} logs for Post ID 5:")
    for log in post_5_logs.data:
        print(f"  - {log['agent']} (ID: {log['id']})")
else:
    print("No logs found for Post ID 5")
    print("\nChecking if any logs exist without post_id:")
    null_logs = supabase.table("agent_logs").select("id, agent, timestamp").is_("post_id", "null").limit(5).execute()
    if null_logs.data:
        print(f"Found {len(null_logs.data)} logs with NULL post_id (recent):")
        for log in null_logs.data:
            print(f"  - {log['agent']} (ID: {log['id']}, Time: {log['timestamp']})")

print("\n" + "=" * 60)

