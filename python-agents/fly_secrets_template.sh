#!/bin/bash
# Fly.io Secrets Setup Template
# Copy this file, fill in your values, and run: bash fly_secrets.sh

# Replace the placeholder values below with your actual API keys and configuration

flyctl secrets set \
  SUPABASE_URL="https://your-project-id.supabase.co" \
  SUPABASE_KEY="your_supabase_service_role_key_here" \
  OPENAI_API_KEY="your_openai_api_key_here" \
  SERPAPI_API_KEY="your_serpapi_api_key_here" \
  LLM_MODEL="gpt-4o-mini" \
  LLM_TEMPERATURE="0.7" \
  ENVIRONMENT="production"

# Alternative: Set secrets one at a time (useful if some values contain special characters)
# flyctl secrets set SUPABASE_URL="https://your-project-id.supabase.co"
# flyctl secrets set SUPABASE_KEY="your_supabase_service_role_key_here"
# flyctl secrets set OPENAI_API_KEY="your_openai_api_key_here"
# flyctl secrets set SERPAPI_API_KEY="your_serpapi_api_key_here"
# flyctl secrets set LLM_MODEL="gpt-4o-mini"
# flyctl secrets set LLM_TEMPERATURE="0.7"
# flyctl secrets set ENVIRONMENT="production"

# Verify secrets are set (they won't show values, just confirm they exist)
echo "Verifying secrets..."
flyctl secrets list

