# 🤖 Autonomous Multi-Agent Content Pipeline

> **Turn a Product Requirements Document (PRD) into a research-backed, fact-checked, and publication-ready blog post using a multi-agent AI workflow.**

An end-to-end AI content generation system built with **Python, LangGraph, LangChain, Groq, SerpAPI, FastAPI, Next.js, React, TypeScript, and Supabase**.

The system takes a Product Requirements Document (PRD), researches the topic using live web search, generates a structured article, fact-checks the generated claims, automatically sends the draft back for revision when necessary, and finally polishes the article for publication.

---

## 📌 What is this project?

Creating a high-quality technical blog post usually requires several separate tasks:

1. Understanding the requirements
2. Researching the topic
3. Writing the article
4. Verifying facts
5. Editing and formatting the final content

Instead of performing all these tasks with one large AI prompt, this project divides the workflow into **four specialized AI agents**.

Each agent has one responsibility and passes its output to the next agent through a shared workflow state.

The workflow is orchestrated using **LangGraph**, which allows the agents to communicate through a stateful graph and supports conditional routing and iteration.

### In simple terms:

```text
PRD
 │
 ▼
Research the topic
 │
 ▼
Write the first draft
 │
 ▼
Check the facts
 │
 ├── ❌ Problems found
 │       │
 │       ▼
 │    Rewrite draft
 │       │
 │       └──────► Fact Check again
 │
 └── ✅ Passed
         │
         ▼
    Polish the article
         │
         ▼
   Final Blog Post

   🏗️ System Architecture

The application consists of a Next.js frontend, a Python AI backend, external AI/search services, and a Supabase PostgreSQL database.
 
                          ┌──────────────────────┐
                         │      Next.js UI      │
                         │ React + TypeScript   │
                         │    Tailwind CSS      │
                         └──────────┬───────────┘
                                    │
                                    │ HTTP
                                    ▼
                         ┌──────────────────────┐
                         │     FastAPI API      │
                         │     Python Backend   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      LangGraph       │
                         │ Workflow Orchestrator│
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌─────────────┐       ┌─────────────┐      ┌─────────────┐
       │  Researcher │       │    Writer   │      │Fact Checker │
       │    Agent    │──────►│    Agent    │─────►│    Agent    │
       └──────┬──────┘       └─────────────┘      └──────┬──────┘
              │                                           │
              ▼                                      ┌────┴────┐
       ┌─────────────┐                               │         │
       │   SerpAPI   │                               ▼         ▼
       │ Live Search │                           ❌ Rewrite   ✅ Continue
       └─────────────┘                               │
                                                     │
                                                     ▼
                                              ┌─────────────┐
                                              │   Polisher  │
                                              │    Agent    │
                                              └──────┬──────┘
                                                     │
                                                     ▼
                                              ┌─────────────┐
                                              │ Final Blog  │
                                              │    Post     │
                                              └──────┬──────┘
                                                     │
                                                     ▼
                                              ┌─────────────┐
                                              │  Supabase   │
                                              │ PostgreSQL  │
                                              └─────────────┘

   
 🤖 Multi-Agent Workflow

The core of the project is a four-agent pipeline orchestrated using LangGraph.

1. 🔎 Research Agent

File: researcher.py

The Research Agent is responsible for gathering information before the article is written.

It:

Receives the topic and PRD requirements.
Uses SerpAPI to perform live web searches.
Collects relevant search results.
Extracts useful facts, data points, and background information.
Provides the research context to the Writer Agent.
Technologies
Python
SerpAPI
LangChain
Structured workflow state

PRD / Topic
     │
     ▼
Research Agent
     │
     ▼
SerpAPI
     │
     ▼
Search Results
     │
     ▼
Research Context

✍️ 2. Writer Agent

File: writer.py

The Writer Agent combines the original PRD with the research gathered by the Research Agent.

It generates a structured Markdown article based on:

Topic
PRD requirements
Research findings
Target word count
Requested writing style

The agent uses the Groq API for fast LLM inference.
Current LLM
openai/gpt-oss-120b

The Writer Agent is designed to produce a complete first draft rather than a short summary.

PRD
 │
 ├──────────────┐
 │              │
 ▼              ▼
Requirements   Research
 │              │
 └──────┬───────┘
        ▼
   Writer Agent
        │
        ▼
 Markdown Draft

 🔍 3. Fact-Checker Agent

File: fact_checker.py

The Fact-Checker Agent validates the generated article against the research gathered earlier in the workflow.

It checks whether the claims made in the article are supported by the available research.

The agent produces a structured result containing:

Pass / Fail status
Identified discrepancies
Verification information
Conditional workflow

This is one of the important parts of the project.

If the article passes fact-checking:
Fact Check
    │
    └── ✅ PASS
           │
           ▼
       Polisher

If problems are found:

Fact Check
    │
    └── ❌ FAIL
           │
           ▼
       Writer Agent
           │
           ▼
      New Draft
           │
           ▼
      Fact Checker


The workflow supports multiple fact-checking iterations before continuing to the polishing stage.

This conditional routing is handled using LangGraph.

✨ 4. Style Polisher Agent

File: polisher.py

After the content passes validation, the Style Polisher prepares the article for final publication.

It improves:

Writing style
Sentence structure
Readability
Flow
Markdown formatting
Overall presentation

The result is the final publication-ready blog post.

Fact-Checked Draft
        │
        ▼
   Polisher Agent
        │
        ▼
Final Markdown Article
🧠 Why LangGraph?

Instead of simply calling an LLM four times sequentially, this project uses LangGraph to represent the entire content pipeline as a stateful graph.

The workflow maintains shared state containing information such as:

PRD
Topic
Target Length
Writing Style
Research Data
Draft Content
Fact Check Status
Fact Check Iterations
Final Content
Metadata

This allows each agent to access the information produced by previous stages.

More importantly, LangGraph enables conditional routing.

For example:

              ┌──────────────┐
              │ Fact Checker │
              └───────┬──────┘
                      │
              ┌───────┴────────┐
              │                │
            PASS              FAIL
              │                │
              ▼                ▼
          Polisher           Writer
                               │
                               ▼
                         Fact Checker

This makes the system more than a simple linear LLM pipeline.

🛠️ Technology Stack
Backend & AI

  | Technology       | Purpose                             |
| ---------------- | ----------------------------------- |
| **Python**       | Core backend and agent development  |
| **FastAPI**      | Backend API layer                   |
| **Uvicorn**      | ASGI server                         |
| **LangGraph**    | Multi-agent workflow orchestration  |
| **LangChain**    | LLM integration and agent utilities |
| **Groq API**     | Fast LLM inference                  |
| **GPT-OSS 120B** | Primary language model              |
| **SerpAPI**      | Live web research and search        |
| **Pydantic**     | Data validation and structured data |


   Frontend

   | Technology       | Purpose                        |
| ---------------- | ------------------------------ |
| **Next.js**      | Frontend framework             |
| **React**        | UI development                 |
| **TypeScript**   | Type-safe frontend development |
| **Tailwind CSS** | Styling and responsive UI      |
| **Lucide React** | UI icons                       |
 
   
   Database & Observability

   | Technology                  | Purpose                          |
| --------------------------- | -------------------------------- |
| **Supabase**                | Backend database and persistence |
| **PostgreSQL**              | Relational database              |
| **Custom Agent Logs**       | Pipeline execution tracking      |
| **Supabase SQL Migrations** | Database schema management       |


  📊 Application Features
📝 PRD Input Engine

Users can provide:

Product requirements
Topic
Target word count
Writing style

The information becomes the initial input to the multi-agent workflow.

🔎 Live Web Research

The Research Agent uses SerpAPI to search the web for relevant information.

This provides the Writer and Fact Checker with research context rather than relying entirely on the model's internal knowledge.

🤖 Multi-Agent Generation

Instead of one large prompt, the system separates responsibilities between:

Researcher
    ↓
Writer
    ↓
Fact Checker
    ↓
Polisher

Each agent has a focused role.

🔄 Automated Fact-Checking Loop

The Fact Checker can send the content back to the Writer when issues are detected.

Writer
  ↓
Fact Checker
  ↓
  ├── PASS → Polisher
  │
  └── FAIL → Writer → Fact Checker

The workflow limits the number of iterations to prevent endless loops.

📈 Real-Time Agent Timeline

The frontend provides a timeline showing the progress of the pipeline.

Example:

✓ PRD Received
│
✓ Research Completed
│
✓ Writer Draft Generated
│
✓ Fact Check Completed
│
✓ Style Polished
│
✓ Final Blog Generated

This makes the normally hidden AI workflow visible to the user.

📚 Persistent Post Library

Generated articles are stored in Supabase PostgreSQL.

Users can:

Browse generated posts
Open previous articles
Review generated content
Copy content
Export content
📊 Agent Observability

Each pipeline execution can be logged and tracked.

The system records information such as:

Agent Name
Execution Status
Execution Duration
Token Usage
Generated Output
Fact Check Result
Post ID
Timestamp

This makes it easier to understand and debug individual agent executions.

📂 Project Structure
multi-agent-content-pipeline/
│
├── python-agents/
│   │
│   ├── agents/
│   │   ├── researcher.py
│   │   ├── writer.py
│   │   ├── fact_checker.py
│   │   └── polisher.py
│   │
│   ├── migrations/
│   │   ├── 001_create_agent_logs.sql
│   │   ├── 002_create_posts.sql
│   │   └── 003_add_post_id_to_agent_logs.sql
│   │
│   ├── graph.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── nextjs-app/
│   │
│   ├── app/
│   │   ├── generate/
│   │   ├── posts/
│   │   ├── timeline/
│   │   └── api/
│   │
│   ├── package.json
│   └── ...
│
├── .env.example
├── .gitignore
└── README.md


  🔄 End-to-End Example

Suppose the user provides a PRD for:

"Write a technical blog explaining how AI agents can automate software development workflows."

The pipeline works like this:

Step 1 — PRD

The user submits:

Topic:
AI Agents in Software Development

Target Length:
1500 words

Style:
Technical but beginner-friendly
Step 2 — Research Agent

The Research Agent searches the web using SerpAPI.

It collects:

Search Results
      ↓
Relevant Sources
      ↓
Facts
      ↓
Research Context
Step 3 — Writer Agent

The Writer receives:

PRD
+
Research
+
Target Word Count
+
Writing Style

and generates:

Markdown Blog Draft
Step 4 — Fact Checker

The Fact Checker examines the draft.

If everything is supported:

PASS
 ↓
Polisher

If unsupported claims are found:

FAIL
 ↓
Writer
 ↓
New Draft
 ↓
Fact Checker
Step 5 — Style Polisher

The verified article is sent to the Polisher.

It improves:

Structure
Readability
Tone
Grammar
Markdown
Formatting
Step 6 — Final Output

The final article is saved and displayed through the frontend.

PRD
 ↓
Research
 ↓
Draft
 ↓
Fact Check
 ↓
Polish
 ↓
🚀 Publication-Ready Blog Post
🚀 Getting Started
Prerequisites

Make sure you have:

Python 3.10+
Node.js 18+
npm
A Groq API key
A SerpAPI API key
A Supabase project
1. Clone the Repository
git clone https://github.com/justMridul/multi-agent-content-pipeline.git

cd multi-agent-content-pipeline
2. Configure Environment Variables

Create a .env file according to .env.example.

Example:

# =========================
# Supabase
# =========================

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key

NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_KEY=your_supabase_anon_key


# =========================
# External APIs
# =========================

SERPAPI_API_KEY=your_serpapi_api_key

GROQ_API_KEY=your_groq_api_key


# =========================
# LLM Configuration
# =========================

LLM_MODEL=openai/gpt-oss-120b
LLM_TEMPERATURE=0.7


# =========================
# Backend
# =========================

FASTAPI_URL=http://localhost:8000

Important: Never commit your .env file or API keys to GitHub.

3. Configure Supabase

Open your Supabase project and run the SQL migrations located in:

python-agents/migrations/

Run them in the following order:

001_create_agent_logs.sql
002_create_posts.sql
003_add_post_id_to_agent_logs.sql

These migrations create the database tables required for:

Posts
Agent execution logs
Post-agent relationships
4. Start the Python Backend

Navigate to the backend:

cd python-agents

Create a virtual environment:

Windows
python -m venv venv
venv\Scripts\activate
macOS / Linux
python3 -m venv venv
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Start the backend:

python main.py

The FastAPI backend will run on:

http://localhost:8000
5. Start the Next.js Frontend

Open another terminal.

Navigate to:

cd nextjs-app

Install dependencies:

npm install

Start the development server:

npm run dev

The frontend will be available at:

http://localhost:3000