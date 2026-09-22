# 🤖 Autonomous Multi-Agent Content Pipeline

> **Transform Product Requirements Documents (PRDs) into research-backed, fact-checked, and publication-ready blog posts using an orchestrated multi-agent AI system.**

---

## 📌 Overview

Writing technical blog posts from Product Requirements Documents (PRDs) typically requires manual research, writing, fact-checking, and editing. 

This project automates that end-to-end pipeline using an autonomous **Multi-Agent Architecture** orchestrated via **LangGraph**. Instead of relying on a single monolithic prompt, the system breaks down generation into four specialized, stateful AI agents—each responsible for a single stage in the content publishing workflow.

---

## 🏗️ System Architecture & Workflow

The system is structured as a stateful graph where data flows sequentially through four specialized agents, with automated validation loops:

```text
[ PRD Input ]
      │
      ▼
┌─────────────────────────┐
│  01. Research Agent     │ ──► Searches live web via SerpAPI for real-time sources & facts
└─────────────────────────┘
      │
      ▼
┌─────────────────────────┐
│  02. Writer Agent       │ ──► Drafts structured Markdown article via Groq (Llama-3.1-8b)
└─────────────────────────┘
      │
      ▼
┌─────────────────────────┐
│  03. Fact-Checker Agent │ ──► Cross-checks claims against research; loops back if errors exist
└─────────────────────────┘
      │
      ▼
┌─────────────────────────┐
│  04. Polisher Agent     │ ──► Refines tone, style, readability, and final formatting
└─────────────────────────┘
      │
      ▼
[ Published Post + Live Supabase Logs + Next.js Timeline UI ]

🧠 Agent Breakdown
Research Agent (researcher.py): Accepts topic inputs and queries the live web using SerpAPI to gather real-time citations, data points, and background context.

Writer Agent (writer.py): Evaluates the PRD alongside the retrieved web findings to generate an initial structured Markdown draft using Groq (llama-3.1-8b-instant).

Fact-Checker Agent (fact_checker.py): Performs structured validation by cross-referencing draft claims against the research findings. Returns a JSON payload containing pass/fail status and identified discrepancies.

Style-Polisher Agent (polisher.py): Receives verified drafts to optimize tone, sentence structure, flow, and visual Markdown layout before saving the final deliverable.

🛠️ Tech Stack
Backend & AI Architecture
Language/Framework: Python 3.10+, FastAPI, Uvicorn

Agent Orchestration: LangGraph & LangChain (Stateful state graph & conditional routing)

LLM Provider: Groq API (llama-3.1-8b-instant for low-latency inference)

Live Search Integration: SerpAPI (Google Search API)

Frontend & User Interface
Framework: Next.js 14+ (App Router), React, TypeScript

Styling: Tailwind CSS (Modern dark-mode design system)

Icons: Lucide React

Database & Observability
Database: Supabase (PostgreSQL)

Logging & Telemetry: Custom execution logging tracking token count, step durations, and post histories across every pipeline run.

📂 Project Structure - 

  multi-agent-content-pipeline/
├── python-agents/          # Backend Microservice (FastAPI + LangGraph)
│   ├── agents/             # Modular agent logic
│   │   ├── researcher.py   # Web search agent (SerpAPI)
│   │   ├── writer.py       # Drafting agent (Groq Llama-3.1)
│   │   ├── fact_checker.py # Claim verification & evaluation
│   │   └── polisher.py     # Style and formatting agent
│   ├── graph.py            # LangGraph workflow orchestration & state definition
│   ├── main.py             # FastAPI entry point (/generate endpoint)
│   ├── migrations/         # Supabase SQL schema definitions
│   └── requirements.txt    # Python dependencies
│
├── nextjs-app/             # Frontend Application (Next.js)
│   ├── app/
│   │   ├── generate/       # PRD submission & post creation form
│   │   ├── posts/          # Library of generated articles
│   │   ├── timeline/       # Real-time visual timeline of agent steps
│   │   └── api/            # Internal Next.js API routes
│   └── package.json
│
├── .env.example            # Environment variable template
└── README.md               # Project documentation

🚀 Getting Started (Local Setup)
Prerequisites
Node.js (v18+) & npm

Python (v3.10+)

API Keys for Groq, SerpAPI, and Supabase

1. Environment Configuration
Create a .env file in the root directory:

# Supabase Configuration
SUPABASE_URL=[https://your-supabase-project.supabase.co](https://your-supabase-project.supabase.co)
SUPABASE_KEY=your_supabase_service_role_key
NEXT_PUBLIC_SUPABASE_URL=[https://your-supabase-project.supabase.co](https://your-supabase-project.supabase.co)
NEXT_PUBLIC_SUPABASE_KEY=your_supabase_anon_key

# External APIs
SERPAPI_API_KEY=your_serpapi_key
GROQ_API_KEY=your_groq_api_key

# Model Configuration
LLM_MODEL=llama-3.1-8b-instant
LLM_TEMPERATURE=0.7

# Server Endpoints
FASTAPI_URL=http://localhost:8000

2. Database Migration
Run the provided SQL scripts in your Supabase Dashboard → SQL Editor to create the required tables:

python-agents/migrations/001_create_agent_logs.sql

python-agents/migrations/002_create_posts.sql

python-agents/migrations/003_add_post_id_to_agent_logs.sql

3. Backend Setup (FastAPI)

# Navigate to backend directory
cd python-agents

# Create & activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
python main.py

he web interface will be accessible at http://localhost:3000.

📊 Application Features
PRD Input Engine: Submit detailed product requirements along with custom target word counts and tone styles.

Step-by-Step Agent Timeline: View real-time agent output logs (/timeline/[postId]), showcasing raw search context, writer drafts, fact-check results, and final polisher outputs.

Persistent Post Library: Browse, review, copy, and export generated blog posts stored in PostgreSQL.

📄 License
This project is licensed under the MIT License.