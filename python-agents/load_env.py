"""
Utility to load environment variables from either:
1. python-agents/.env (local override)
2. ../.env (root shared file)
"""
import os
from pathlib import Path
from dotenv import load_dotenv


def load_environment():
    """
    Load environment variables, checking both local and root .env files.
    Local .env takes precedence if it exists.
    """
    # Get the directory of this file (python-agents/)
    current_dir = Path(__file__).parent
    root_dir = current_dir.parent
    
    # Try to load from root .env first (shared)
    root_env = root_dir / '.env'
    if root_env.exists():
        load_dotenv(root_env, override=False)  # Don't override if already set
    
    # Then load from local .env (takes precedence)
    local_env = current_dir / '.env'
    if local_env.exists():
        load_dotenv(local_env, override=True)  # Override with local values
    
    # Also check for .env.local in root (for local overrides)
    root_env_local = root_dir / '.env.local'
    if root_env_local.exists():
        load_dotenv(root_env_local, override=True)

