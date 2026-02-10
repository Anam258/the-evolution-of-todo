# GitHub Issues Creation Script

This script automatically creates GitHub issues from the task breakdown in `specs/001-db-schema/tasks.md`.

## Prerequisites

1. **Python 3.11+** installed
2. **GitHub Personal Access Token** with `repo` scope

## Setup

### 1. Create GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "Task to Issues Script"
4. Select scope: **`repo`** (Full control of private repositories)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

### 2. Install Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

### 3. Set Environment Variable

**Option A: Export in current session**
```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

**Option B: Create .env file** (recommended)
```bash
# Create scripts/.env file
echo "GITHUB_TOKEN=ghp_your_token_here" > .env
```

**Note**: The `.env` file is gitignored and will not be committed.

## Usage

### Dry Run (Recommended First)

Run in dry-run mode to preview what issues will be created:

```bash
python create_github_issues.py
# When prompted, enter 'y' for dry run
```

This will show you the first 5 issues that would be created without actually creating them.

### Create All Issues

```bash
python create_github_issues.py
# When prompted:
# - Enter 'n' to skip dry run, or
# - Enter 'y' for dry run, then 'y' to proceed with creation
```

The script will:
1. Parse all 54 tasks from `specs/001-db-schema/tasks.md`
2. Create custom labels (phase-1, US1, P1, parallel, tests, etc.)
3. Create one GitHub issue per task with:
   - Task ID in title (T001, T002, etc.)
   - Phase and user story information
   - Appropriate labels for filtering
   - Links to spec documents
   - Acceptance criteria checklist

## What Gets Created

### Labels

The script creates these labels automatically:
- **Phase labels**: `phase-1` through `phase-6`
- **User Story labels**: `US1`, `US2`, `US3`
- **Priority labels**: `P1`, `P2`
- **Type labels**: `task`, `tests`, `documentation`, `setup`, `foundational`, `polish`
- **Special labels**: `parallel` (can run concurrently), `blocking` (blocks other tasks)
- **Feature label**: `001-db-schema`

### Issue Structure

Each issue includes:
- **Title**: Task ID + short description (e.g., "T001: Create backend directory structure")
- **Body**:
  - Task ID and phase
  - User story (if applicable)
  - Parallelizable marker (if applicable)
  - Full task description
  - Acceptance criteria checklist
  - Links to spec documents
- **Labels**: Phase, priority, story, and type labels

## Filtering Issues

After creation, you can filter issues by:

- **All database schema tasks**: [`label:001-db-schema`](https://github.com/Anam258/the-evolution-of-todo/issues?q=is%3Aissue+is%3Aopen+label%3A001-db-schema)
- **MVP tasks only**: [`label:phase-1,phase-2,phase-3,phase-4`](https://github.com/Anam258/the-evolution-of-todo/issues?q=is%3Aissue+is%3Aopen+label%3Aphase-1%2Cphase-2%2Cphase-3%2Cphase-4)
- **User Story 1**: [`label:US1`](https://github.com/Anam258/the-evolution-of-todo/issues?q=is%3Aissue+is%3Aopen+label%3AUS1)
- **Parallelizable tasks**: [`label:parallel`](https://github.com/Anam258/the-evolution-of-todo/issues?q=is%3Aissue+is%3Aopen+label%3Aparallel)
- **Test tasks**: [`label:tests`](https://github.com/Anam258/the-evolution-of-todo/issues?q=is%3Aissue+is%3Aopen+label%3Atests)
- **Blocking tasks**: [`label:blocking`](https://github.com/Anam258/the-evolution-of-todo/issues?q=is%3Aissue+is%3Aopen+label%3Ablocking)

## Project Board Suggestions

Create a GitHub Project board with these columns:

1. **Setup** (Phase 1) - 10 tasks
2. **Foundational** (Phase 2) - 2 tasks (⚠️ blocks all other phases)
3. **US3: Connection** (Phase 3) - 9 tasks
4. **US1: Schema** (Phase 4) - 13 tasks
5. **US2: Validation** (Phase 5) - 14 tasks
6. **Polish** (Phase 6) - 6 tasks
7. **Done**

Filter each column by its phase label (e.g., `label:phase-1` for Setup).

## Troubleshooting

### Error: "GITHUB_TOKEN environment variable not set"

**Solution**: Make sure you've set the token:
```bash
export GITHUB_TOKEN="your_token_here"
# OR create a .env file with: GITHUB_TOKEN=your_token_here
```

### Error: "401 Unauthorized" or "403 Forbidden"

**Solution**: Your token may be invalid or lack the `repo` scope:
1. Go to https://github.com/settings/tokens
2. Check your token has the `repo` scope enabled
3. Generate a new token if needed

### Error: "422 Validation Failed" on label creation

**Solution**: Labels may already exist. This is normal. The script will skip existing labels and continue.

### Rate Limiting

GitHub allows 5,000 API requests per hour for authenticated users. The script includes a 0.5-second delay between issue creations to be respectful of rate limits. Creating 54 issues will take approximately 27 seconds plus label creation time.

## Manual Alternative

If you prefer not to use the script, you can manually create issues from the task list in `specs/001-db-schema/tasks.md`. Each task line contains all the information needed for an issue.

## Cleanup

If you need to delete all created issues (be careful!):

1. Go to repository settings → Danger Zone
2. Or use GitHub CLI: `gh issue list --label 001-db-schema --json number -q '.[].number' | xargs -I {} gh issue close {}`

**Note**: This is permanent. Only do this if you're sure!

## Next Steps

After creating issues:

1. View all issues: https://github.com/Anam258/the-evolution-of-todo/issues
2. Create a GitHub Project board to organize tasks
3. Start implementation with `/sp.implement` or by manually working through issues in order
4. Close issues as tasks are completed

## Support

If you encounter issues with the script:
1. Check the error message for specific details
2. Verify your GitHub token is valid and has correct scopes
3. Ensure you have network connectivity to GitHub API
4. Check GitHub's status page: https://www.githubstatus.com/
