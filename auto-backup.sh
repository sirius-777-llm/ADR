#!/bin/bash
# ADR Auto-Backup: detect meaningful changes and push to the backup remote
# Run via cron or launchd every 30 minutes

cd /Users/wekoidubai/ADR || exit 1

# 默认同时推 GitHub (origin) 和 GitLab (gitlab)；任一失败不影响另一个
BACKUP_REMOTES="${ADR_BACKUP_REMOTES:-${ADR_BACKUP_REMOTE:-origin gitlab}}"
BACKUP_BRANCH="${ADR_BACKUP_BRANCH:-main}"

push_backup() {
    local rc=0
    for remote in $BACKUP_REMOTES; do
        if git push "$remote" "$BACKUP_BRANCH"; then
            echo "[$(date '+%F %T')] OK: git push $remote $BACKUP_BRANCH"
        else
            echo "[$(date '+%F %T')] WARN: git push $remote $BACKUP_BRANCH failed"
            rc=1
        fi
    done
    return $rc
}

CHANGES=$(git diff --name-only -- '*.py' '*.md' '*.skill' '*.sh' 'skill/' 'openclaw-skill/')
UNTRACKED=$(git ls-files --others --exclude-standard -- '*.py' '*.md' '*.skill' '*.sh')

if [ -z "$CHANGES" ] && [ -z "$UNTRACKED" ]; then
    push_backup
    exit $?
fi

git add -- '*.py' '*.md' '*.skill' '*.sh' 'skill/' 'openclaw-skill/' 2>/dev/null

# Safety: scan staged content for common secret patterns BEFORE commit
if git diff --cached | grep -qE "sk-[a-z0-9]{24,}|github_pat_[A-Za-z0-9_]{50,}|[0-9]{9,}:AA[A-Za-z0-9_-]{30,}|AKIA[0-9A-Z]{16}"; then
    echo "[$(date '+%F %T')] BLOCKED: staged content looks like secret, aborting auto-backup"
    git reset HEAD >/dev/null 2>&1
    exit 1
fi

MSG="auto-backup: $(echo $CHANGES $UNTRACKED | tr '\n' ' ' | sed 's/ *$//')"
git commit -m "$MSG" --no-gpg-sign 2>/dev/null || exit 0
push_backup
