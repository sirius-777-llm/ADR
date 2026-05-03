#!/bin/bash
# ADR Auto-Backup: detect meaningful changes and push to GitHub
# Run via cron or launchd every 30 minutes

cd /Users/wekoidubai/ADR || exit 1

CHANGES=$(git diff --name-only -- '*.py' '*.md' '*.skill' 'skill/' 'openclaw-skill/')
UNTRACKED=$(git ls-files --others --exclude-standard -- '*.py' '*.md' '*.skill')

if [ -z "$CHANGES" ] && [ -z "$UNTRACKED" ]; then
    exit 0
fi

git add -- '*.py' '*.md' '*.skill' 'skill/' 'openclaw-skill/' 2>/dev/null

# Safety: scan staged content for common secret patterns BEFORE commit
if git diff --cached | grep -qE "sk-[a-z0-9]{24,}|github_pat_[A-Za-z0-9_]{50,}|[0-9]{9,}:AA[A-Za-z0-9_-]{30,}|AKIA[0-9A-Z]{16}"; then
    echo "[$(date '+%F %T')] BLOCKED: staged content looks like secret, aborting auto-backup"
    git reset HEAD >/dev/null 2>&1
    exit 1
fi

MSG="auto-backup: $(echo $CHANGES $UNTRACKED | tr '\n' ' ' | sed 's/ *$//')"
git commit -m "$MSG" --no-gpg-sign 2>/dev/null || exit 0
git push origin main 2>/dev/null
