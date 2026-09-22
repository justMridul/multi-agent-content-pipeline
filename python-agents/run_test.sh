#!/bin/bash
# Helper script to run test_workflow.py with the virtual environment activated

cd "$(dirname "$0")"
source venv/bin/activate
python test_workflow.py

