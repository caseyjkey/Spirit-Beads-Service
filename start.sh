#!/bin/bash
# 1. Navigate to project
cd /home/trill/Development/spirit-beads-service

# 2. Activate the environment (Adjust path if using Conda or Venv)
source venv/bin/activate  # or: conda activate base

# 3. Start the server
python manage.py runserver 0.0.0.0:8000
