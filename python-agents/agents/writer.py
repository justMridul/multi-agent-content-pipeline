from typing import Dict, Any, Optional
import os
import json
import time
from datetime import datetime

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from supabase import create_client, Client

from load_env import load_environment


# Load environment variables
load_environment()


class WriterAgent:
    """
    Agent responsible for writing blog post drafts based on PRD
    and research data using Groq.

    Logs outputs and metrics to Supabase.
    """

    def __init__(self):
        # ---------------------------------------------------------
        # Environment configuration
        # ---------------------------------------------------------
        self.groq_key = os.getenv("GROQ_API_KEY")

        self.model_name = os.getenv(
            "LLM_MODEL",
            "openai/gpt-oss-120b"
        )

        self.temperature = float(
            os.getenv("LLM_TEMPERATURE", "0.7")
        )

        print("\n========== WRITER CONFIG ==========")
        print(f"LLM Model: {self.model_name}")
        print(f"Temperature: {self.temperature}")
        print(f"Groq API Key loaded: {bool(self.groq_key)}")
        print("===================================\n")

        # ---------------------------------------------------------
        # Initialize Groq LLM client
        # ---------------------------------------------------------
        if self.groq_key:
            self.llm = ChatGroq(
                groq_api_key=self.groq_key,
                model_name=self.model_name,
                temperature=self.temperature,
                model_kwargs={
                    "include_reasoning": False
                }
            )
        else:
            self.llm = None
            print(
                "WARNING: GROQ_API_KEY environment variable "
                "is required"
            )

        # ---------------------------------------------------------
        # Initialize Supabase client
        # ---------------------------------------------------------
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if supabase_url and supabase_key:
            self.supabase: Optional[Client] = create_client(
                supabase_url,
                supabase_key
            )
        else:
            self.supabase = None
            print(
                "WARNING: Supabase credentials not found. "
                "Logging will be skipped."
            )

    # ============================================================
    # PRD EXTRACTION
    # ============================================================

    def _extract_prd(self, state: Dict[str, Any]) -> str:
        """
        Extract PRD from state.

        PRD can be:
        1. Directly in state["prd"]
        2. Inside research_data["prd"]
        3. Reconstructed from research findings
        """

        # ---------------------------------------------------------
        # Check direct PRD
        # ---------------------------------------------------------
        prd = state.get("prd", "")

        if prd:
            return str(prd)

        # ---------------------------------------------------------
        # Check PRD inside research_data
        # ---------------------------------------------------------
        research_data = state.get("research_data", {})

        if isinstance(research_data, dict):

            prd = research_data.get("prd", "")

            if prd:
                return str(prd)

        # ---------------------------------------------------------
        # Use research findings as fallback context
        # ---------------------------------------------------------
        if isinstance(research_data, dict):

            findings = research_data.get("findings", [])
            key_points = research_data.get("key_points", [])

            prd_context = ""

            if key_points:
                prd_context = "\n".join(
                    str(point)
                    for point in key_points[:5]
                )

            elif findings:
                snippets = []

                for finding in findings[:3]:

                    if isinstance(finding, dict):
                        snippet = finding.get("snippet", "")

                        if snippet:
                            snippets.append(str(snippet))

                prd_context = "\n".join(snippets)

            if prd_context:
                return prd_context

        return "No PRD or research data provided"

    # ============================================================
    # CONTENT EXTRACTION
    # ============================================================

    def _extract_content(self, response: Any) -> str:
        """
        Robustly extract text from a LangChain AIMessage.

        Handles:
        - Normal string content
        - List-based content blocks
        - Dictionary content blocks
        - Other response formats
        """

        if response is None:
            return ""

        # ---------------------------------------------------------
        # Get response.content
        # ---------------------------------------------------------
        if hasattr(response, "content"):
            content = response.content
        else:
            content = response

        # ---------------------------------------------------------
        # Normal string response
        # ---------------------------------------------------------
        if isinstance(content, str):
            return content.strip()

        # ---------------------------------------------------------
        # List-based content
        # ---------------------------------------------------------
        if isinstance(content, list):

            text_parts = []

            for block in content:

                if isinstance(block, str):
                    text_parts.append(block)

                elif isinstance(block, dict):

                    # Common LangChain/Groq content format
                    text = block.get("text")

                    if text:
                        text_parts.append(str(text))
                        continue

                    # Alternative content keys
                    text = block.get("content")

                    if text:
                        text_parts.append(str(text))
                        continue

                else:
                    text_parts.append(str(block))

            return "\n".join(text_parts).strip()

        # ---------------------------------------------------------
        # Dictionary response
        # ---------------------------------------------------------
        if isinstance(content, dict):

            text = content.get("text")

            if text:
                return str(text).strip()

            text = content.get("content")

            if text:
                return str(text).strip()

            return json.dumps(content)

        # ---------------------------------------------------------
        # Fallback
        # ---------------------------------------------------------
        return str(content).strip()

    # ============================================================
    # RESEARCH CONTEXT
    # ============================================================

    def _build_research_context(
        self,
        research_data: Dict[str, Any]
    ) -> str:

        if not research_data:
            return ""

        findings = research_data.get("findings", [])

        if not findings:
            return ""

        research_context = "\n\nResearch Findings:\n"

        for i, finding in enumerate(findings[:8], 1):

            if not isinstance(finding, dict):
                continue

            title = finding.get("title", "")
            snippet = finding.get("snippet", "")

            research_context += (
                f"{i}. {title}: {snippet}\n"
            )

        return research_context

    # ============================================================
    # SYNCHRONOUS BLOG GENERATION
    # ============================================================

    def _generate_blog_post(
        self,
        prd: str,
        topic: str,
        target_length: int,
        style: str,
        research_data: Dict[str, Any]
    ) -> str:

        if not self.llm:

            return (
                f"# {topic}\n\n"
                "[Blog post draft based on PRD]\n\n"
                f"PRD Content:\n{prd[:500]}..."
            )

        # ---------------------------------------------------------
        # Build research context
        # ---------------------------------------------------------
        research_context = self._build_research_context(
            research_data
        )

        # ---------------------------------------------------------
        # System prompt
        # ---------------------------------------------------------
        system_prompt = """
You are an expert content writer.

Your task is to write a complete, useful, engaging blog post.

Rules:
- Return ONLY the blog post.
- Do not explain what you are doing.
- Do not discuss the prompt.
- Do not mention being an AI.
- Do not ask the user for additional information.
- Use Markdown headings.
- Use paragraphs and lists where appropriate.
- Use the provided research as supporting information.
- Do not invent facts that contradict the research.
"""

        # ---------------------------------------------------------
        # User prompt
        # ---------------------------------------------------------
        user_prompt = f"""
Create a complete blog post using the information below.

TOPIC:
{topic}

TARGET LENGTH:
Approximately {target_length} words

WRITING STYLE:
{style}

PRODUCT REQUIREMENTS DOCUMENT:
{prd}

{research_context}

REQUIREMENTS:

1. Start with an engaging introduction.
2. Clearly explain the topic.
3. Include the important information requested in the PRD.
4. Incorporate relevant information from the research.
5. Organize the article using Markdown headings.
6. Use clear paragraphs and lists where useful.
7. End with a meaningful conclusion.
8. Stay close to the requested target length.
9. Return the FULL article.
10. Do NOT return a summary or outline.

Write the complete blog post now.
"""

        try:

            messages = [
                SystemMessage(
                    content=system_prompt
                ),
                HumanMessage(
                    content=user_prompt
                )
            ]

            print("\n========== WRITER REQUEST ==========")
            print(f"Model: {self.model_name}")
            print(f"Topic: {topic}")
            print(f"Target length: {target_length}")
            print(f"Style: {style}")
            print("====================================\n")

            response = self.llm.invoke(messages)

            # -----------------------------------------------------
            # Debug information
            # -----------------------------------------------------
            print("\n========== WRITER RESPONSE ==========")
            print(f"Response type: {type(response)}")

            if hasattr(response, "content"):
                print(
                    f"Raw content type: "
                    f"{type(response.content)}"
                )

                print(
                    f"Raw content length: "
                    f"{len(str(response.content))}"
                )

            print(f"Response: {response}")
            print("====================================\n")

            # -----------------------------------------------------
            # Extract final text
            # -----------------------------------------------------
            content = self._extract_content(response)

            if not content:

                print(
                    "\nWARNING: Writer returned EMPTY CONTENT."
                )

                print(
                    "Response additional kwargs:",
                    getattr(
                        response,
                        "additional_kwargs",
                        {}
                    )
                )

                print(
                    "Response response_metadata:",
                    getattr(
                        response,
                        "response_metadata",
                        {}
                    )
                )

                return (
                    f"# {topic}\n\n"
                    "The writer model returned an empty response."
                )

            return content

        except Exception as e:

            print(
                f"Error generating blog post: {str(e)}"
            )

            return (
                f"# {topic}\n\n"
                f"[Error generating content: {str(e)}]\n\n"
                f"PRD:\n{prd[:500]}"
            )

    # ============================================================
    # ASYNCHRONOUS BLOG GENERATION
    # ============================================================

    async def _generate_blog_post_async(
        self,
        prd: str,
        topic: str,
        target_length: int,
        style: str,
        research_data: Dict[str, Any]
    ) -> str:

        if not self.llm:

            return (
                f"# {topic}\n\n"
                "[Blog post draft based on PRD]\n\n"
                f"PRD Content:\n{prd[:500]}..."
            )

        # ---------------------------------------------------------
        # Build research context
        # ---------------------------------------------------------
        research_context = self._build_research_context(
            research_data
        )

        # ---------------------------------------------------------
        # System prompt
        # ---------------------------------------------------------
        system_prompt = """
You are an expert content writer.

Your task is to write a complete, useful, engaging blog post.

Rules:
- Return ONLY the blog post.
- Do not explain what you are doing.
- Do not discuss the prompt.
- Do not mention being an AI.
- Do not ask the user for additional information.
- Use Markdown headings.
- Use paragraphs and lists where appropriate.
- Use the provided research as supporting information.
- Do not invent facts that contradict the research.
"""

        # ---------------------------------------------------------
        # User prompt
        # ---------------------------------------------------------
        user_prompt = f"""
Create a complete blog post using the information below.

TOPIC:
{topic}

TARGET LENGTH:
Approximately {target_length} words

WRITING STYLE:
{style}

PRODUCT REQUIREMENTS DOCUMENT:
{prd}

{research_context if research_context else
 "Limited research data is available. Focus primarily on the PRD."}

REQUIREMENTS:

1. Start with an engaging introduction.
2. Clearly explain the topic.
3. Include the important information requested in the PRD.
4. Incorporate relevant information from the research.
5. Organize the article using Markdown headings.
6. Use clear paragraphs and lists where useful.
7. End with a meaningful conclusion.
8. Stay close to the requested target length.
9. Return the FULL article.
10. Do NOT return a summary or outline.
11. Do NOT ask for more information.

Write the complete blog post now.
"""

        try:

            messages = [
                SystemMessage(
                    content=system_prompt
                ),
                HumanMessage(
                    content=user_prompt
                )
            ]

            print("\n========== WRITER REQUEST ==========")
            print(f"Model: {self.model_name}")
            print(f"Topic: {topic}")
            print(f"Target length: {target_length}")
            print(f"Style: {style}")
            print("====================================\n")

            response = await self.llm.ainvoke(messages)

            # -----------------------------------------------------
            # Debug information
            # -----------------------------------------------------
            print("\n========== WRITER RESPONSE ==========")
            print(f"Response type: {type(response)}")

            if hasattr(response, "content"):

                print(
                    f"Raw content type: "
                    f"{type(response.content)}"
                )

                print(
                    f"Raw content length: "
                    f"{len(str(response.content))}"
                )

            print(f"Response: {response}")
            print("====================================\n")

            # -----------------------------------------------------
            # Extract final text
            # -----------------------------------------------------
            content = self._extract_content(response)

            if not content:

                print(
                    "\nWARNING: Writer returned EMPTY CONTENT."
                )

                print(
                    "Response additional kwargs:",
                    getattr(
                        response,
                        "additional_kwargs",
                        {}
                    )
                )

                print(
                    "Response response_metadata:",
                    getattr(
                        response,
                        "response_metadata",
                        {}
                    )
                )

                return (
                    f"# {topic}\n\n"
                    "The writer model returned an empty response."
                )

            return content

        except Exception as e:

            print(
                f"Error generating blog post: {str(e)}"
            )

            return (
                f"# {topic}\n\n"
                f"[Error generating content: {str(e)}]\n\n"
                f"PRD:\n{prd[:500]}"
            )

    # ============================================================
    # SUPABASE LOGGING
    # ============================================================

    def _log_to_supabase(
        self,
        prd: str,
        draft_content: str,
        metrics: Dict[str, Any],
        post_id: Optional[int] = None
    ) -> None:

        if not self.supabase:
            return

        try:

            log_entry = {
                "agent": "writer",

                "input": (
                    prd[:5000]
                    if len(prd) > 5000
                    else prd
                ),

                "output": (
                    draft_content[:10000]
                    if len(draft_content) > 10000
                    else draft_content
                ),

                "timestamp": datetime.utcnow().isoformat(),

                "metadata": {
                    "word_count": len(
                        draft_content.split()
                    ),

                    "prd_length": len(prd),

                    "draft_length": len(
                        draft_content
                    ),

                    **metrics
                }
            }

            if post_id is not None:
                log_entry["post_id"] = post_id

            response = (
                self.supabase
                .table("agent_logs")
                .insert(log_entry)
                .execute()
            )

            if response.data:

                print(
                    "Writer logged to Supabase: "
                    f"{len(response.data)} record(s)"
                )

        except Exception as e:

            print(
                f"Error logging to Supabase: {str(e)}"
            )

    # ============================================================
    # SYNCHRONOUS RUN
    # ============================================================

    def run(
        self,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:

        start_time = time.time()

        research_data = state.get(
            "research_data",
            {}
        )

        topic = state.get(
            "topic",
            ""
        )

        target_length = state.get(
            "target_length",
            1000
        )

        style = state.get(
            "style",
            "professional"
        )

        print(
            f"Writing blog post draft for topic: {topic}"
        )

        # ---------------------------------------------------------
        # Extract PRD
        # ---------------------------------------------------------
        prd = self._extract_prd(state)

        # ---------------------------------------------------------
        # Generate draft
        # ---------------------------------------------------------
        draft_content = self._generate_blog_post(
            prd,
            topic,
            target_length,
            style,
            research_data
        )

        # ---------------------------------------------------------
        # Metrics
        # ---------------------------------------------------------
        elapsed_time = (
            time.time() - start_time
        )

        word_count = len(
            draft_content.split()
        )

        metrics = {
            "execution_time_seconds":
                elapsed_time,

            "word_count":
                word_count,

            "target_length":
                target_length,

            "style":
                style,

            "prd_provided":
                bool(
                    prd
                    and
                    prd !=
                    "No PRD or research data provided"
                )
        }

        # ---------------------------------------------------------
        # Log to Supabase
        # ---------------------------------------------------------
        post_id = state.get(
            "post_id"
        )

        self._log_to_supabase(
            prd,
            draft_content,
            metrics,
            post_id
        )

        print(
            f"Blog post draft completed: "
            f"{word_count} words, "
            f"{elapsed_time:.2f}s"
        )

        # ---------------------------------------------------------
        # Update state
        # ---------------------------------------------------------
        state["draft_content"] = draft_content

        return state

    # ============================================================
    # ASYNCHRONOUS RUN
    # ============================================================

    async def run_async(
        self,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:

        import asyncio

        start_time = time.time()

        research_data = state.get(
            "research_data",
            {}
        )

        topic = state.get(
            "topic",
            ""
        )

        target_length = state.get(
            "target_length",
            1000
        )

        style = state.get(
            "style",
            "professional"
        )

        print(
            f"Writing blog post draft for topic: {topic}"
        )

        # ---------------------------------------------------------
        # Extract PRD
        # ---------------------------------------------------------
        prd = self._extract_prd(state)

        # ---------------------------------------------------------
        # Generate draft
        # ---------------------------------------------------------
        draft_content = (
            await self._generate_blog_post_async(
                prd,
                topic,
                target_length,
                style,
                research_data
            )
        )

        # ---------------------------------------------------------
        # Metrics
        # ---------------------------------------------------------
        elapsed_time = (
            time.time() - start_time
        )

        word_count = len(
            draft_content.split()
        )

        metrics = {
            "execution_time_seconds":
                elapsed_time,

            "word_count":
                word_count,

            "target_length":
                target_length,

            "style":
                style,

            "prd_provided":
                bool(
                    prd
                    and
                    prd !=
                    "No PRD or research data provided"
                )
        }

        # ---------------------------------------------------------
        # Log to Supabase
        # ---------------------------------------------------------
        post_id = state.get(
            "post_id"
        )

        if post_id is None:

            print(
                "\033[93m[WARNING]\033[0m "
                "Writer (async): post_id is None "
                "in state! Logs will not be linked."
            )

        else:

            print(
                "\033[94m[DEBUG]\033[0m "
                f"Writer (async): "
                f"Logging with post_id={post_id}"
            )

        if self.supabase:

            loop = asyncio.get_event_loop()

            await loop.run_in_executor(
                None,
                self._log_to_supabase,
                prd,
                draft_content,
                metrics,
                post_id
            )

        # ---------------------------------------------------------
        # Final logging
        # ---------------------------------------------------------
        print(
            f"Blog post draft completed: "
            f"{word_count} words, "
            f"{elapsed_time:.2f}s"
        )

        # ---------------------------------------------------------
        # Update state
        # ---------------------------------------------------------
        state["draft_content"] = draft_content

        return state