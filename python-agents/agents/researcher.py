from typing import Dict, Any, List, Optional
import os
import json
from datetime import datetime
import serpapi
from supabase import create_client, Client

from load_env import load_environment

load_environment()


class ResearchAgent:
    """
    Agent responsible for researching the given topic using SerpAPI and gathering relevant information.
    Logs research outputs and metrics to Supabase.
    """
    
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        if not self.serpapi_key:
            raise ValueError("SERPAPI_API_KEY environment variable is required")
        
        # Initialize SerpAPI client
        self.serpapi_client = serpapi.Client(api_key=self.serpapi_key)
        
        # Initialize Supabase client for logging
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if supabase_url and supabase_key:
            self.supabase: Optional[Client] = create_client(supabase_url, supabase_key)
        else:
            self.supabase = None
            print("Warning: Supabase credentials not found. Logging will be skipped.")
    
    def _search_serpapi(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """
        Perform a web search using SerpAPI.
        
        Args:
            query: Search query
            num_results: Number of results to retrieve
            
        Returns:
            Dictionary containing search results
        """
        try:
            # Perform Google search via SerpAPI
            search_results = self.serpapi_client.search(
                q=query,
                engine="google",
                num=num_results,
                hl="en",
                gl="us"
            )
            
            return {
                "success": True,
                "results": search_results,
                "query": query
            }
        except Exception as e:
            print(f"SerpAPI search error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def _extract_research_data(self, search_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and structure research data from SerpAPI results.
        
        Args:
            search_response: Raw SerpAPI response
            
        Returns:
            Structured research data
        """
        if not search_response.get("success"):
            return {
                "findings": [],
                "sources": [],
                "key_points": [],
                "organic_results": []
            }
        
        results = search_response.get("results", {})
        organic_results = results.get("organic_results", [])
        
        # Extract findings and sources
        findings = []
        sources = []
        key_points = []
        
        for result in organic_results[:10]:  # Limit to top 10 results
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            
            if title and snippet:
                findings.append({
                    "title": title,
                    "snippet": snippet,
                    "source": link
                })
                
                sources.append({
                    "url": link,
                    "title": title,
                    "snippet": snippet
                })
                
                # Extract key points from snippet
                if snippet:
                    key_points.append(snippet[:200])  # First 200 chars as key point
        
        # Also check for answer box, knowledge graph, etc.
        answer_box = results.get("answer_box")
        if answer_box:
            answer_text = answer_box.get("answer") or answer_box.get("snippet", "")
            if answer_text:
                key_points.insert(0, answer_text)
                findings.insert(0, {
                    "title": "Direct Answer",
                    "snippet": answer_text,
                    "source": "answer_box"
                })
        
        return {
            "findings": findings,
            "sources": sources,
            "key_points": key_points,
            "organic_results": organic_results,
            "total_results": len(organic_results)
        }
    
    def _log_to_supabase(
        self,
        topic: str,
        research_data: Dict[str, Any],
        metrics: Dict[str, Any],
        post_id: Optional[int] = None
    ) -> None:
        """
        Log research outputs and metrics to Supabase.
        
        Schema: id (int8), agent (text), input (text), output (text), 
                timestamp (timestamptz), metadata (json), post_id (bigint)
        
        Args:
            topic: Research topic
            research_data: Structured research data
            metrics: Performance metrics (timing, result count, etc.)
            post_id: ID of the post this log belongs to (optional)
        """
        if not self.supabase:
            return
        
        try:
            # Prepare log entry matching the schema
            log_entry = {
                "agent": "researcher",
                "input": topic,
                "output": json.dumps(research_data),  # Convert research_data to JSON string
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "findings_count": len(research_data.get("findings", [])),
                    "sources_count": len(research_data.get("sources", [])),
                    "key_points_count": len(research_data.get("key_points", [])),
                    **metrics  # Include all metrics in metadata
                }
            }
            
            # Add post_id if provided
            if post_id is not None:
                log_entry["post_id"] = post_id
            
            # Insert into Supabase agent_logs table
            response = self.supabase.table("agent_logs").insert(log_entry).execute()
            
            if response.data:
                print(f"Research logged to Supabase: {len(response.data)} record(s)")
        except Exception as e:
            print(f"Error logging to Supabase: {str(e)}")
            # Don't fail the research if logging fails
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous research execution.
        
        Args:
            state: Current workflow state containing the topic
            
        Returns:
            Updated state with research_data
        """
        import time
        start_time = time.time()
        
        topic = state.get("topic", "")
        if not topic:
            raise ValueError("Topic is required for research")
        
        print(f"\033[94m[RESEARCH]\033[0m Researching topic: {topic}")
        
        # Perform SerpAPI search
        search_response = self._search_serpapi(topic, num_results=10)
        
        # Extract and structure research data
        research_data = self._extract_research_data(search_response)
        research_data["topic"] = topic
        research_data["search_successful"] = search_response.get("success", False)
        
        # Calculate metrics
        elapsed_time = time.time() - start_time
        metrics = {
            "execution_time_seconds": elapsed_time,
            "results_found": research_data.get("total_results", 0),
            "search_successful": search_response.get("success", False)
        }
        
        # Log to Supabase
        post_id = state.get("post_id")
        if post_id is None:
            print(f"\033[93m[WARNING]\033[0m Researcher: post_id is None in state! Logs will not be linked.")
        else:
            print(f"\033[94m[DEBUG]\033[0m Researcher: Logging with post_id={post_id}")
        self._log_to_supabase(topic, research_data, metrics, post_id)
        
        print(f"\033[92m[SUCCESS]\033[0m Research completed: {len(research_data.get('findings', []))} findings, {elapsed_time:.2f}s")
        
        state["research_data"] = research_data
        return state
    
    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronous research execution.
        
        Args:
            state: Current workflow state containing the topic
            
        Returns:
            Updated state with research_data
        """
        import asyncio
        import time
        start_time = time.time()
        
        topic = state.get("topic", "")
        if not topic:
            raise ValueError("Topic is required for research")
        
        print(f"\033[94m[RESEARCH]\033[0m Researching topic: {topic}")
        
        # Run SerpAPI search in executor to avoid blocking
        loop = asyncio.get_event_loop()
        search_response = await loop.run_in_executor(
            None,
            self._search_serpapi,
            topic,
            10
        )
        
        # Extract and structure research data
        research_data = self._extract_research_data(search_response)
        research_data["topic"] = topic
        research_data["search_successful"] = search_response.get("success", False)
        
        # Calculate metrics
        elapsed_time = time.time() - start_time
        metrics = {
            "execution_time_seconds": elapsed_time,
            "results_found": research_data.get("total_results", 0),
            "search_successful": search_response.get("success", False)
        }
        
        # Log to Supabase (run in executor to avoid blocking)
        post_id = state.get("post_id")
        if post_id is None:
            print(f"\033[93m[WARNING]\033[0m Researcher (async): post_id is None in state! Logs will not be linked.")
        else:
            print(f"\033[94m[DEBUG]\033[0m Researcher (async): Logging with post_id={post_id}")
        if self.supabase:
            await loop.run_in_executor(
                None,
                self._log_to_supabase,
                topic,
                research_data,
                metrics,
                post_id
            )
        
        print(f"Research completed: {len(research_data.get('findings', []))} findings, {elapsed_time:.2f}s")
        
        state["research_data"] = research_data
        return state

