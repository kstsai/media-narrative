---
name: git-workflow
description: "Git workflows for multi-remote repos, sync strategies, branching patterns, and commit conventions."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Git, Workflow, Multi-Remote, Sync, Branching]
    related_skills: [github-auth, github-repo-management]
  user:
    kstsai:
      multi_remote_workflow: true
      default_order: "pull origin → push gitea → commit → push gitea → push origin"
      gitea_remote: gitea
      github_remote: origin
---

# Git Workflows

Standardized git workflows for common patterns: multi-remote sync, branch management, and commit hygiene.

## Multi-Remote Sync Workflow (Gitea + GitHub)

Use when a repo has two remotes — a private gitea instance (primary push target) and GitHub (upstream).

### The Core Pattern

```
① git pull origin main         # Pull latest from GitHub FIRST
② git push gitea main          # Sync gitea to match GitHub
③ ... modify files ...
   git add -A
   git commit -m "message"
④ git push gitea main          # Push to primary remote first
⑤ git push origin main         # Then push to upstream
```

### Why This Order

| Step | Why |
|------|-----|
| Pull origin first | Ensures local branch is based on GitHub's latest — gitea may be stale |
| Push gitea → then origin | Primary target gets the commit first; GitHub is the mirror |
| Never skip gitea | gitea is the canonical local source; always push there first |

### Pitfalls

- **Never pull from gitea** — only pull from `origin` (GitHub). Gitea is a downstream, not upstream.
- **Rebase + gitea force-push**: After `git pull --rebase origin main`, local commits are rewritten. `git push gitea main` will fail as non-fast-forward. Since gitea is single-user/private, use `git push --force-with-lease gitea main` — but **never** force-push to GitHub without explicit user confirmation.
- **Always check remotes first**: Run `git remote -v` at the start to confirm which remote is which.

### Detecting When to Use This Pattern

Trigger when:
- The repo has more than one remote (check with `git remote -v`)
- One remote points to a non-GitHub host or IP address (private gitea/gitlab)
- The user mentions "gitea", "mini-PC", "local gitea", or "sync both"
- A `git push` fails because the user pushed to GitHub but not gitea, or vice versa

### Unified Credential Store (Recommended)

Use one credential file for all remotes:

```bash
# Configure the helper ONCE
git config --global credential.helper "store --file ~/.git-credentials"

# Write credentials directly (one line per remote)
echo "https://<user>:<pat>@github.com" >> ~/.git-credentials
echo "http://<user>:<pass>@<gitea-host>:<port>" >> ~/.git-credentials
chmod 600 ~/.git-credentials
```

Or use the approve command:
```bash
echo -e "protocol=https\nhost=github.com\nusername=<user>\npassword=<pat>" \
  | git credential-store --file ~/.git-credentials approve
```

### Credential Validation (Before Debugging Git)

When `git push/pull` gives auth errors, test credentials FIRST with curl
to isolate whether it's the credential format or the server:

```bash
# GitHub
curl -s -u "<user>:<pat>" -o /dev/null -w "%{http_code}" \
  https://api.github.com/repos/<owner>/<repo>
# 200 = OK, 401 = bad token

# Gitea
curl -s -u "<user>:<pass>" -o /dev/null -w "%{http_code}" \
  http://<host>:<port>/api/v1/user
# 200 = OK, 401 = bad credentials
```

This instantly separates "credentials are wrong" from "git is misconfigured".

**Pitfall — special chars in passwords:** A `!` in a password passed via
`git remote set-url` shell interpolation may be interpreted by the shell
before git sees it. Validate with `curl` first (above), then use the
credential-store file approach rather than embedding passwords in remote URLs.

### Verification

```bash
git remote -v
# gitea   http://<host>:<port>/<user>/<repo>.git
# origin  https://github.com/<user>/<repo>.git

git log --oneline --all     # Verify same latest commit on both
```

## 2. Branch Workflow (Standard)

For feature development with PRs:

```bash
# Start from main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feat/my-feature

# Work, commit, push
git add -A && git commit -m "feat: add my feature"
git push origin feat/my-feature

# Open PR (see github-pr-workflow skill)
```

## Commit Message Conventions

| Prefix | Use Case |
|--------|----------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `refactor:` | Code restructuring |
| `docs:` | Documentation |
| `chore:` | Maintenance, tooling |
| `revert:` | Revert a change |

## Quick Reference

```bash
# Sync multi-remote (full cycle)
git pull origin main && \
git push gitea main && \
echo "Synced — ready to work"

# Push cycle after commit
git push gitea main && \
git push origin main && \
echo "Both remotes updated"
```
