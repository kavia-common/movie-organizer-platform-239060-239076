#!/bin/bash
cd /tmp/kavia/workspace/code-generation/movie-organizer-platform-239060-239076/movie_api_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

