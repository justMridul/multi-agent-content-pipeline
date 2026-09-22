from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from supabase import create_client, Client

from graph import create_workflow_async
from load_env import load_environment

# Load environment variables (from root .env or local .env)
load_environment()

app = FastAPI(title="Multi-Agent Content Pipeline API")

# Initialize Supabase client for posts table
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Optional[Client] = None
if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)
else:
    print("Warning: Supabase credentials not found. Posts will not be saved.")

# Configure CORS
# Allow localhost for development, specific origins for production
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

# Add Vercel URL from environment variable if set
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    # Vercel provides URL without protocol, add https
    if not vercel_url.startswith("http"):
        vercel_url = f"https://{vercel_url}"
    allowed_origins.append(vercel_url)

# Also check for explicit NEXT_PUBLIC_VERCEL_URL
nextjs_url = os.getenv("NEXT_PUBLIC_VERCEL_URL")
if nextjs_url:
    if not nextjs_url.startswith("http"):
        nextjs_url = f"https://{nextjs_url}"
    allowed_origins.append(nextjs_url)

# In production, use specific origins; in development, allow all
environment = os.getenv("ENVIRONMENT", os.getenv("FLY_APP_NAME", "development"))
if environment == "production" or os.getenv("FLY_APP_NAME"):
    # Production: restrict to allowed origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Development: allow all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Initialize the async workflow
workflow = create_workflow_async()


class ContentRequest(BaseModel):
    prd: str  # Product Requirements Document
    topic: str
    target_length: Optional[int] = None
    style: Optional[str] = None


class ContentResponse(BaseModel):
    content: str
    status: str
    metadata: Optional[dict] = None


@app.get("/")
async def root():
    return {"message": "Multi-Agent Content Pipeline API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest):
    """
    Generate content using the multi-agent pipeline.
    """
    try:
        # Create post entry first (with empty final_post, will be updated later)
        # This allows us to get the post_id and link all agent logs to it
        post_id = None
        if supabase:
            try:
                post_entry = {
                    "prd": request.prd,
                    "final_post": ""  # Will be updated after workflow completes
                }
                print(f"Creating post entry in Supabase (PRD length: {len(request.prd)})...")
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
                if "permission" in error_msg.lower() or "policy" in error_msg.lower() or "rls" in error_msg.lower():
                    print("\n\033[93m[WARNING]\033[0m This looks like a Row Level Security (RLS) issue.")
                    print("   Check your Supabase table policies for the posts table.")
        
        # Run the workflow with PRD, topic, and post_id
        print(f"\033[94m[DEBUG]\033[0m Starting workflow with post_id: {post_id}")
        workflow_state = {
            "prd": request.prd,
            "topic": request.topic,
            "target_length": request.target_length or 1000,
            "style": request.style or "professional",
            "post_id": post_id,  # Pass post_id through workflow
            "fact_check_iterations": 0  # Initialize iteration counter
        }
        print(f"\033[94m[DEBUG]\033[0m Workflow state post_id: {workflow_state.get('post_id')}")
        result = await workflow.ainvoke(workflow_state)
        
        final_content = result.get("final_content", "")
        
        # Update the post with final content
        if post_id and supabase and final_content:
            try:
                print(f"Updating post {post_id} with final content (length: {len(final_content)})...")
                update_response = supabase.table("posts").update({
                    "final_post": final_content
                }).eq("id", post_id).execute()
                
                if update_response.data:
                    print(f"\033[92m[SUCCESS]\033[0m Post {post_id} updated with final content")
                else:
                    print("\033[93m[WARNING]\033[0m Post update returned no data")
            except Exception as e:
                print(f"\033[91m[ERROR]\033[0m Error updating post: {str(e)}")
                # Don't fail the request if update fails
        
        return ContentResponse(
            content=final_content,
            status="success",
            metadata={
                **result.get("metadata", {}),
                "post_id": post_id  # Include post_id in metadata so frontend can redirect
            }
        )
    except Exception as e:
        return ContentResponse(
            content="",
            status=f"error: {str(e)}",
            metadata=None
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

