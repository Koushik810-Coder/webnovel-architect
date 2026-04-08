---
name: update-repo
description: Use this skill to securely update the current repository from GitHub. Includes steps for stashing local changes, pulling the latest code, updating dependencies, and handling conflicts. Triggered by requests to "pull latest", "update repo", "sync from git", or similar.
---

# Update Repository Skill

Follow this standardized workflow whenever a user requests to update their repository from GitHub. This ensures no local work is lost and dependencies stay perfectly synchronized with the newly pulled code.

## Execution Steps

### 1. Check Local State
Run `git status` to see if there are any unstaged or uncommitted changes in the project directory.

### 2. Safely Stash (If Needed)
If `git status` reports modified files, you **must** stash them to prevent merge conflicts or overwritten work:
```bash
git stash push -m "Auto-stash before repo update"
```
*Note: Do not do this if the working tree is completely clean.*

### 3. Pull the Latest Code
Execute the pull command to fetch and merge the latest remote commits into the current branch (usually `main`):
```bash
git pull origin main
```
*(If the user is on a different default branch like `master` or `develop`, use that instead).*

### 4. Restore Local Changes & Handle Conflicts
If you stashed changes in step 2, pop them back into the workspace:
```bash
git stash pop
```
If a merge conflict occurs during the pop, stop immediately and ask the user how they would like to resolve the conflict.

### 5. Update Dependencies
If the `git pull` output indicated that dependency tracking files (like `requirements.txt`, `pyproject.toml`, or `package.json`) were updated, you must install the new dependencies.
For Python projects with a requirements file:
```bash
pip install -r requirements.txt
```

### 6. Advise on Re-runs
If the user currently has a web server, Streamlit UI, or background process running, politely inform them that they may need to restart the application in their terminal for the new changes to take effect.
