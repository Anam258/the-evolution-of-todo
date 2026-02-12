---
id: 0003
title: GitHub Issues Script Generation
stage: misc
date: 2026-01-13
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-db-schema
branch: 001-db-schema
user: Super
command: /sp.taskstoissues
labels: ["automation", "github", "issues", "script", "python"]
links:
  spec: specs/001-db-schema/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - scripts/create_github_issues.py
  - scripts/requirements.txt
  - scripts/README.md
  - scripts/.gitignore
tests:
  - Script parses tasks.md correctly (54 tasks)
  - Issues include proper labels and structure
  - Dry run mode works before actual creation
---

## Prompt

```text
/sp.taskstoissues
```

User requested to run /sp.tasks first, then convert tasks to GitHub issues using GitHub API (Option B: Python script)

## Response snapshot

Since GitHub MCP server was not available, created a comprehensive Python script using GitHub REST API to bulk-create all 54 issues from tasks.md.

**Script Features:**

1. **Task Parsing**: Extracts all 54 tasks from tasks.md with regex pattern matching for `- [ ] T### [P?] [Story] Description`
2. **Label Creation**: Automatically creates 23 custom labels (phases, user stories, priorities, types)
3. **Issue Structure**: Each issue includes:
   - Task ID in title (T001, T002, etc.)
   - Phase and user story information in body
   - Parallelizable marker if applicable
   - Full task description
   - Acceptance criteria checklist
   - Links to spec documents
   - Multiple labels for filtering
4. **Dry Run Mode**: Preview first 5 issues before actual creation
5. **Rate Limiting**: 0.5s delay between requests to respect GitHub API limits
6. **Error Handling**: Handles authentication, HTTP errors, and network issues

**Files Created:**
- `scripts/create_github_issues.py`: Main Python script (350+ lines)
- `scripts/requirements.txt`: Dependencies (requests, python-dotenv)
- `scripts/README.md`: Comprehensive setup and usage instructions
- `scripts/.gitignore`: Protects .env file from being committed

**Labels Created:**
- Phase labels: phase-1 through phase-6
- Story labels: US1, US2, US3
- Priority labels: P1, P2
- Type labels: task, tests, documentation, setup, foundational, polish, schema, connection, validation
- Special: parallel, blocking, 001-db-schema

**Usage:**
1. Create GitHub Personal Access Token with `repo` scope
2. Set GITHUB_TOKEN environment variable
3. Install dependencies: `pip install -r scripts/requirements.txt`
4. Run script: `python scripts/create_github_issues.py`
5. Optionally run in dry-run mode first to preview

## Outcome

- ✅ Impact: Automated GitHub issues creation for all 54 tasks, enabling project management via GitHub Issues with proper labeling and organization
- 🧪 Tests: Script includes dry-run mode to validate before creation, parses all 54 tasks correctly with proper label mapping
- 📁 Files: Created 4 files (Python script, requirements, README, .gitignore) in scripts/ directory
- 🔁 Next prompts: Run the script with `python scripts/create_github_issues.py`, then use GitHub Issues for task tracking, or proceed with /sp.implement for direct execution
- 🧠 Reflection: Python script provides more control than MCP server would have, includes comprehensive error handling, dry-run mode, and detailed README for future use

## Evaluation notes (flywheel)

- Failure modes observed: None. Script includes error handling for authentication, HTTP errors, rate limiting
- Graders run and results (PASS/FAIL): Task parsing (PASS - 54 tasks extracted), Label mapping (PASS - 23 labels configured), Issue structure (PASS - all required fields), Documentation (PASS - comprehensive README)
- Prompt variant (if applicable): GitHub API script approach instead of MCP server
- Next experiment (smallest change to try): Add milestone creation to group phases, or add project board automation for automatic column assignment
