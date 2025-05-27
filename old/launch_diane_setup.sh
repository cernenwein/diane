#!/bin/bash
set -e

LOGFILE="$HOME/diane_setup.log"
REPEATABLE_SCRIPT="$HOME/setup_llm_repeatable.sh"
ONETIME_SCRIPT="$HOME/setup_llm_onetime.sh"

echo "=== Running Diane LLM setup ===" | tee -a "$LOGFILE"
echo "Started at $(date)" | tee -a "$LOGFILE"

# Make sure both scripts are executable
chmod +x "$REPEATABLE_SCRIPT" "$ONETIME_SCRIPT"

# Run repeatable setup
echo "--- Running repeatable setup ---" | tee -a "$LOGFILE"
"$REPEATABLE_SCRIPT" 2>&1 | tee -a "$LOGFILE"

# Run one-time setup
echo "--- Running one-time setup ---" | tee -a "$LOGFILE"
"$ONETIME_SCRIPT" 2>&1 | tee -a "$LOGFILE"

echo "Setup completed at $(date)" | tee -a "$LOGFILE"
