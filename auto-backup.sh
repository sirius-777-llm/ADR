#!/bin/bash
# ADR Auto-Backup: detect meaningful changes and push to GitHub
# Run via cron or launchd every 30 minutes

cd /Users/wekoidubai/ADR || exit 1

# Only care about .py and .md files (skip logs, temp, media)
CHANGES=$(git diff --name-only -- '*.py' '*.md' '*.skill' 'skill/' 'openclaw-skill/')
UNTRACKED=$(git ls-files --others --exclude-standard -- '*.py' '*.md' '*.skill')

if [ -z "$CHANGES" ] && [ -z "$UNTRACKED" ]; then
    exit 0  # nothing to backup
fi

# Build commit message from changed files
MSG="auto-backup: $(echo $CHANGES $UNTRACKED | tr '\n' ' ' | sed 's/ *$//')"

git add -- '*.py' '*.md' '*.skill' 'skill/' 'openclaw-skill/' 2>/dev/null
git commit -m "$MSG" --no-gpg-sign 2>/dev/null || exit 0
git push origin main 2>/dev/null
