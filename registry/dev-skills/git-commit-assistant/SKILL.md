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
```

Summarize branch, ahead/behind remote, staged vs unstaged, and untracked files. If there is nothing to commit, stop and say so.

### Step 2 — Review the diff

Run (unstaged + staged):

```bash
git diff
git diff --staged
```

If output is large, use `git diff --stat` first, then narrow with paths. Call out risky edits (auth, crypto, permissions, deletions of important files).

### Step 3 — Sensitive files and secrets

Before staging, check that the change set does **not** include secrets or local-only files.

**Block or flag** if any path or diff hunk matches common leak patterns, for example:

- Environment and secrets: `.env`, `.env.*`, `*.pem`, `*.p12`, `*.key`, `id_rsa`, `id_ed25519`, `credentials`, `secrets.yml`, `serviceAccount.json`, `.npmrc` with `_auth`, AWS/Google/Azure key files
- High-risk content in diff: long random tokens, `BEGIN PRIVATE KEY`, `password=`, `api_key`, `secret`, `Authorization:` with bearer tokens

If something looks sensitive:

1. Do **not** `git add` / commit until the user removes or replaces it (e.g. env vars + `.gitignore`, secret manager, placeholder).
2. If the user insists on committing anyway, require an explicit written confirmation and still refuse if it is clearly a private key or live credential.

### Step 4 — Commit message format

Prefer **Conventional Commits**:

```text
<type>(<optional scope>): <short description in imperative>

[optional body explaining why, not only what]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`.

**Rules:**

- Subject line ~72 characters or less, no trailing period, imperative mood ("add" not "added").
- One logical change per commit when possible; if the diff mixes unrelated concerns, suggest splitting.

Propose 1–2 subject lines (and optional body) in a code block for the user to approve or edit.

### Step 5 — Stage

After safety check and approved message:

```bash
git add -p
```

Use `git add <path>` for intentional partial staging when `-p` is too heavy. Avoid `git add .` unless the user confirms the entire tree is intended.

### Step 6 — Commit

```bash
git commit -m "<subject>" -m "<optional body>"
```

Or open the editor if the user prefers multi-paragraph bodies (`git commit` with no `-m`).

### Step 7 — Push

```bash
git push -u origin HEAD
```

If the branch has no upstream yet, `-u origin HEAD` sets tracking. If push is rejected (non-fast-forward), explain: `git pull --rebase` (or merge) then push again—never force-push to shared default branches unless the user explicitly requests it and understands the impact.

---

## Quick checklist

Copy for the agent when executing end-to-end:

```text
- [ ] Step 1: git status — changes exist and are understood
- [ ] Step 2: git diff / git diff --staged — reviewed
- [ ] Step 3: no secrets or wrong files staged
- [ ] Step 4: commit message agreed (conventional commits)
- [ ] Step 5: git add (scoped or patch)
- [ ] Step 6: git commit
- [ ] Step 7: git push (handle rejections safely)
```
