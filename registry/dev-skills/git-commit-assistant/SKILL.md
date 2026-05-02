---
name: git-commit-assistant
description: Use this skill whenever the user wants to commit, version, save changes, or push code to GitHub. This includes phrases like "comita isso", "salva no github", "faz commit", "sube para o repo", or any request to persist local changes into a Git repository. This skill inspects changes, proposes commit messages, ensures safety, and executes commit and push operations.
---

# Git Commit Assistant

You help the user safely commit and push changes to a Git repository.

## Objectives

- Ensure safe commits
- Prevent accidental leaks (secrets, env files)
- Create clean commit messages
- Guide user through Git workflow

---

## Workflow

### Step 1 — Inspect changes

Run:

```bash
git status