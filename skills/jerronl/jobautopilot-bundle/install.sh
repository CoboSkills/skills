#!/usr/bin/env bash
# install.sh — install all three Job Autopilot skills from ClawHub
#
# Usage:
#   bash ~/.openclaw/workspace/skills/jobautopilot-bundle/install.sh
#
# This script only runs `clawhub install` for each skill.
# No data is collected or transmitted beyond the ClawHub install process.

set -e

echo "==> Installing Job Autopilot skills..."
clawhub install jobautopilot-search
clawhub install jobautopilot-tailor
clawhub install jobautopilot-submitter
echo ""
echo "All three skills installed."
echo "Run setup next:"
echo "  bash ~/.openclaw/workspace/skills/jobautopilot-bundle/setup.sh"
