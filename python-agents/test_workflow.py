"""
Test script to run the LangGraph workflow directly.
This demonstrates how to use the workflow programmatically.
"""
import asyncio
import os
from supabase import create_client, Client
from typing import Optional
from graph import create_workflow_async
from load_env import load_environment

# Load environment variables
load_environment()

# Initialize Supabase client for posts table
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Optional[Client] = None
if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)
    print("Supabase client initialized for posts table")
else:
    print("\033[93m[WARNING]\033[0m Supabase credentials not found. Posts will not be saved.")


async def test_workflow():
    """Test the LangGraph workflow with sample data."""
    
    # Create the workflow
    workflow = create_workflow_async()
    
    # Sample PRD and topic
    sample_prd = """
    Product Requirements Document: AI-Powered Content Generator
    
    Overview:
    We are building an AI-powered content generation tool that helps users create
    high-quality blog posts from product requirements documents.
    
    Features:
    - Multi-agent workflow for content creation
    - Research integration via SerpAPI
    - Fact-checking capabilities
    - Style polishing
    - Supabase logging for metrics
    
    Target Audience:
    Content creators, marketers, and product teams who need to quickly generate
    well-researched, fact-checked blog content.
    
    Success Metrics:
    - Content quality score > 8/10
    - Fact-check accuracy > 95%
    - Average generation time < 5 minutes
    """
    
    # Create post entry first (with empty final_post, will be updated later)
    # This allows us to get the post_id and link all agent logs to it
    post_id = None
    if supabase:
        try:
            post_entry = {
                "prd": sample_prd,
                "final_post": ""  # Will be updated after workflow completes
            }
            print(f"Creating post entry in Supabase (PRD length: {len(sample_prd)})...")
            response = supabase.table("posts").insert(post_entry).execute()
            
            if response.data and len(response.data) > 0:
                post_id = response.data[0].get("id")
                print(f"\033[92m[SUCCESS]\033[0m Post created with ID: {post_id}")
            else:
                print("\033[93m[WARNING]\033[0m Post created but no ID returned. Logs will not be linked.")
        except Exception as e:
            error_msg = str(e)
            print(f"\033[91m[ERROR]\033[0m Error creating post in Supabase: {error_msg}")
            print("Workflow will continue, but logs will not be linked to a post.")
    
    # Initial state
    initial_state = {
        "prd": sample_prd,
        "topic": "AI-Powered Content Generation",
        "target_length": 800,
        "style": "professional",
        "post_id": post_id,  # Pass post_id through workflow
        "fact_check_iterations": 0
    }
    
    print("\033[95m[START]\033[0m Starting LangGraph workflow...")
    print(f"Topic: {initial_state['topic']}")
    print(f"Target Length: {initial_state['target_length']} words")
    print("-" * 50)
    
    # Run the workflow
    # You can also use astream() for streaming updates
    result = await workflow.ainvoke(initial_state)
    
    print("\n" + "=" * 50)
    print("Workflow completed!")
    print("=" * 50)
    
    final_content = result.get("final_content", "")
    
    # Update the post with final content
    if post_id and supabase and final_content:
        try:
            print(f"\n\033[96m[SAVE]\033[0m Updating post {post_id} with final content (length: {len(final_content)})...")
            update_response = supabase.table("posts").update({
                "final_post": final_content
            }).eq("id", post_id).execute()
            
            if update_response.data:
                print(f"\033[92m[SUCCESS]\033[0m Post {post_id} updated with final content")
            else:
                print("\033[93m[WARNING]\033[0m Post update returned no data")
        except Exception as e:
            print(f"\033[91m[ERROR]\033[0m Error updating post: {str(e)}")
            import traceback
            traceback.print_exc()
    elif not supabase:
        print("\033[93m[WARNING]\033[0m Supabase client not initialized. Check SUPABASE_URL and SUPABASE_KEY in .env")
    elif not final_content or final_content.strip() == "":
        print("\033[93m[WARNING]\033[0m Final content is empty, skipping post update")
    
    print(f"\nFinal Content ({len(final_content.split())} words):")
    print("-" * 50)
    print(final_content)
    print("\n" + "-" * 50)
    print("\nMetadata:")
    print(result.get("metadata", {}))
    print(f"\nFact Check Iterations: {result.get('fact_check_iterations', 0)}")
    print(f"Fact Check Status: {result.get('fact_check_status', 'unknown')}")


async def test_workflow_streaming():
    """Test the workflow with streaming to see progress in real-time."""
    
    workflow = create_workflow_async()
    
    sample_prd = """
    Product: New Mobile App Feature
    Description: A social sharing feature that allows users to share content
    with their network. Includes privacy controls and analytics.
    """
    
    # Create post entry first for streaming test too
    post_id = None
    if supabase:
        try:
            post_entry = {
                "prd": sample_prd,
                "final_post": ""
            }
            response = supabase.table("posts").insert(post_entry).execute()
            if response.data and len(response.data) > 0:
                post_id = response.data[0].get("id")
        except Exception as e:
            print(f"Error creating post: {str(e)}")
    
    initial_state = {
        "prd": sample_prd,
        "topic": "Social Sharing Feature Launch",
        "target_length": 600,
        "style": "casual",
        "post_id": post_id,
        "fact_check_iterations": 0
    }
    
    print("Starting LangGraph workflow with streaming...")
    print("-" * 50)
    
    # Stream the workflow execution
    async for event in workflow.astream(initial_state):
        # event is a dict with node names as keys
        for node_name, node_output in event.items():
            print(f"\nNode: {node_name}")
            if node_name == "research":
                findings = node_output.get("research_data", {}).get("findings", [])
                print(f"   Found {len(findings)} research findings")
            elif node_name == "write":
                word_count = len(node_output.get("draft_content", "").split())
                print(f"   Draft created: {word_count} words")
            elif node_name == "fact_check":
                status = node_output.get("fact_check_status", "unknown")
                iterations = node_output.get("fact_check_iterations", 0)
                print(f"   Fact-check: {status} (iteration {iterations})")
            elif node_name == "polish":
                word_count = len(node_output.get("final_content", "").split())
                print(f"   Final content: {word_count} words")
    
    print("\nStreaming complete!")


if __name__ == "__main__":
    print("=" * 50)
    print("LangGraph Workflow Test")
    print("=" * 50)
    print("\nChoose test mode:")
    print("1. Standard execution (ainvoke)")
    print("2. Streaming execution (astream)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "2":
        asyncio.run(test_workflow_streaming())
    else:
        asyncio.run(test_workflow())

