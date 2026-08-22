# Stage 0: Git Setup and Usage (~15 min)

## Goal

Set up a local Git repository with a real, incremental commit history —
not one bulk commit at the end. In the real assessment, your commit
history is part of what's evaluated: it shows how you actually worked.

## Steps

1. Initialize the repo (if not already done):

   ```bash
   git init
   git branch -M main
   ```

2. Create a `.gitignore` covering at least: `.venv/`, `__pycache__/`,
   `*.pyc`, `.env`, `.pytest_cache/`, `.coverage`, `*.egg-info/`.

3. Make your first commit with the scaffold as-given:

   ```bash
   git add .
   git commit -m "chore: initial scaffold for astra-triage"
   ```

4. For each stage from here on:
   - Create a branch: `git checkout -b stage2-classification-retrieval`
     (or work on `main` if you prefer trunk-based — either is fine, just
     be consistent and say which in your Stage 6 PR description).
   - Make **multiple** small commits as you complete sub-parts of the
     stage (e.g. "fix classifier ranking bug", "add config env loading",
     "implement TF-IDF retrieval", "add relevance threshold filtering").
     Aim for at least 2-4 commits per stage, not one.
   - Write commit messages that describe *why*, not just *what*
     (`fix: classifier now returns true max-scoring category instead of
     first tie` beats `update classifier.py`).
   - If you used an AI assistant heavily for a chunk of work, it's fine
     to note that in the commit body, e.g. "drafted with Claude Code,
     reviewed and adjusted threshold logic manually."

5. Before moving to the next stage, run:

   ```bash
   git status        # nothing uncommitted
   git log --oneline # review your history reads sensibly
   ```

## Acceptance criteria for this stage

- [ ] Local git repo initialized with `main` branch.
- [ ] `.gitignore` in place, `.env` is never tracked.
- [ ] At least one clean initial commit exists.
- [ ] You understand the incremental-commit expectation for every
      subsequent stage (this isn't optional polish — it's graded).

## Common mistakes to avoid

- Committing `.env` or any file containing a real API key.
- One giant "final submission" commit with no history.
- Amending/force-pushing over commits that already show your process
  (there's no remote here, but the habit matters — don't `git commit
  --amend` your way into losing the trail).
