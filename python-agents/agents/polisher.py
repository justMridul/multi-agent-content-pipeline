from typing import Dict, Any, Optional
import os
import json
import time
from datetime import datetime

from langchain_groq import ChatGroq
from supabase import create_client, Client

from load_env import load_environment

load_environment()


class PolisherAgent:
    """
    Agent responsible for polishing and refining the final content using Groq.
    Logs outputs and metrics to Supabase.
    """
    
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        
        # Initialize Groq LLM client
        if self.groq_key:
            self.llm = ChatGroq(
                groq_api_key=self.groq_key,
                model_name=self.model_name,
                temperature=self.temperature
            )
        else:
            self.llm = None
            print("Warning: GROQ_API_KEY environment variable is required")
        
        # Initialize Supabase client for logging
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if supabase_url and supabase_key:
            self.supabase: Optional[Client] = create_client(supabase_url, supabase_key)
        else:
            self.supabase = None
            print("Warning: Supabase credentials not found. Logging will be skipped.")
    
    def _clean_response(self, polished_content: str) -> str:
        """
        Remove any instruction-like text or meta-commentary that might appear at the end of output.
        """
        lines = polished_content.split('\n')
        cleaned_lines = []
        skip_rest = False
        
        instruction_markers = [
            'please:',
            'instructions:',
            'return the polished',
            'do not include',
            'improve readability',
            'enhance the',
            'fix any grammar',
            'optimize sentence',
            'ensure the content',
            'make the introduction',
            'strengthen the conclusion',
            'ensure consistent formatting',
            'maintain all factual'
        ]
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            if (line_lower.startswith('please:') or 
                (line_lower.startswith('1.') and any(marker in line_lower for marker in instruction_markers)) or
                (i > len(lines) * 0.7 and any(marker in line_lower for marker in instruction_markers[:3]))):
                if i > len(lines) * 0.7:
                    skip_rest = True
                    break
            
            if not skip_rest:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()

    def _polish_content(self, content: str, style: str, target_length: int) -> str:
        """
        Polish and refine content using LLM.
        """
        if not self.llm:
            return content
        
        prompt = f"""You are an expert editor and content polisher. Refine and polish the following blog post to make it publication-ready.

Target Style: {style}
Target Length: Approximately {target_length} words

Blog Post to Polish:
{content}

Instructions (DO NOT include these in your response):
- Improve readability and flow
- Enhance the {style} writing style and tone
- Fix any grammar, spelling, or punctuation errors
- Optimize sentence structure and paragraph flow
- Ensure the content meets the target length ({target_length} words)
- Make the introduction more engaging if needed
- Strengthen the conclusion
- Ensure consistent formatting and markdown structure
- Maintain all factual content - only improve presentation

IMPORTANT: Return ONLY the polished blog post content. Do NOT include any instructions, explanations, or meta-commentary. Keep the same markdown structure and headings."""

        try:
            response = self.llm.invoke(prompt)
            polished_content = response.content.strip()
            return self._clean_response(polished_content)
        except Exception as e:
            print(f"Error polishing content: {str(e)}")
            return content
    
    async def _polish_content_async(self, content: str, style: str, target_length: int) -> str:
        """
        Async version of content polishing.
        """
        if not self.llm:
            return content
        
        prompt = f"""You are an expert editor and content polisher. Refine and polish the following blog post to make it publication-ready.

Target Style: {style}
Target Length: Approximately {target_length} words

Blog Post to Polish:
{content}

Instructions (DO NOT include these in your response):
- Improve readability and flow
- Enhance the {style} writing style and tone
- Fix any grammar, spelling, or punctuation errors
- Optimize sentence structure and paragraph flow
- Ensure the content meets the target length ({target_length} words)
- Make the introduction more engaging if needed
- Strengthen the conclusion
- Ensure consistent formatting and markdown structure
- Maintain all factual content - only improve presentation

IMPORTANT: Return ONLY the polished blog post content. Do NOT include any instructions, explanations, or meta-commentary. Keep the same markdown structure and headings."""

        try:
            response = await self.llm.ainvoke(prompt)
            polished_content = response.content.strip()
            return self._clean_response(polished_content)
        except Exception as e:
            print(f"Error polishing content: {str(e)}")
            return content
    
    def _log_to_supabase(
        self,
        input_content: str,
        polished_content: str,
        metrics: Dict[str, Any],
        post_id: Optional[int] = None
    ) -> None:
        """
        Log polisher outputs and metrics to Supabase.
        """
        if not self.supabase:
            return
        
        try:
            log_entry = {
                "agent": "polisher",
                "input": input_content[:5000] if len(input_content) > 5000 else input_content,
                "output": polished_content[:10000] if len(polished_content) > 10000 else polished_content,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "input_length": len(input_content),
                    "output_length": len(polished_content),
                    "input_word_count": len(input_content.split()),
                    "output_word_count": len(polished_content.split()),
                    **metrics
                }
            }
            
            if post_id is not None:
                log_entry["post_id"] = post_id
            
            response = self.supabase.table("agent_logs").insert(log_entry).execute()
            
            if response.data:
                print(f"Polisher logged to Supabase: {len(response.data)} record(s)")
        except Exception as e:
            print(f"Error logging to Supabase: {str(e)}")
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous polishing execution.
        """
        start_time = time.time()
        
        fact_checked_content = state.get("fact_checked_content", "")
        draft_content = state.get("draft_content", "")
        style = state.get("style", "professional")
        target_length = state.get("target_length", 1000)
        
        print(f"Polishing final content...")
        
        content_to_polish = fact_checked_content if fact_checked_content and fact_checked_content.strip() and fact_checked_content != "N/A" else draft_content
        
        if not content_to_polish or content_to_polish.strip() == "" or content_to_polish == "N/A":
            print("Warning: No valid content to polish, using draft content")
            content_to_polish = draft_content
        
        final_content = self._polish_content(content_to_polish, style, target_length)
        
        elapsed_time = time.time() - start_time
        word_count = len(final_content.split()) if final_content else 0
        metrics = {
            "execution_time_seconds": elapsed_time,
            "word_count": word_count,
            "target_length": target_length,
            "style": style
        }
        
        post_id = state.get("post_id")
        self._log_to_supabase(content_to_polish, final_content, metrics, post_id)
        
        print(f"Polishing completed: {word_count} words, {elapsed_time:.2f}s")
        
        state["final_content"] = final_content
        state["metadata"] = {
            "word_count": word_count,
            "style": style,
            "status": "completed"
        }
        
        return state
    
    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronous polishing execution.
        """
        import asyncio
        start_time = time.time()
        
        fact_checked_content = state.get("fact_checked_content", "")
        draft_content = state.get("draft_content", "")
        style = state.get("style", "professional")
        target_length = state.get("target_length", 1000)
        
        print(f"Polishing final content...")
        
        content_to_polish = fact_checked_content if fact_checked_content and fact_checked_content.strip() and fact_checked_content != "N/A" else draft_content
        
        if not content_to_polish or content_to_polish.strip() == "" or content_to_polish == "N/A":
            print("Warning: No valid content to polish, using draft content")
            content_to_polish = draft_content
        
        final_content = await self._polish_content_async(content_to_polish, style, target_length)
        
        elapsed_time = time.time() - start_time
        word_count = len(final_content.split()) if final_content else 0
        metrics = {
            "execution_time_seconds": elapsed_time,
            "word_count": word_count,
            "target_length": target_length,
            "style": style
        }
        
        post_id = state.get("post_id")
        if post_id is None:
            print(f"\033[93m[WARNING]\033[0m Polisher (async): post_id is None in state! Logs will not be linked.")
        else:
            print(f"\033[94m[DEBUG]\033[0m Polisher (async): Logging with post_id={post_id}")
            
        if self.supabase:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._log_to_supabase,
                content_to_polish,
                final_content,
                metrics,
                post_id
            )
        
        print(f"Polishing completed: {word_count} words, {elapsed_time:.2f}s")
        
        state["final_content"] = final_content
        state["metadata"] = {
            "word_count": word_count,
            "style": style,
            "status": "completed"
        }
        
        return state