#!/usr/bin/env python3
"""
Create GitHub issues from tasks.md

Usage:
    export GITHUB_TOKEN="your_github_personal_access_token"
    python scripts/create_github_issues.py

Requirements:
    pip install requests python-dotenv
"""

import os
import re
import sys
import time
from typing import List, Dict, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "Anam258"
REPO_NAME = "the-evolution-of-todo"
TASKS_FILE = "specs/001-db-schema/tasks.md"

# GitHub API configuration
API_BASE_URL = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {GITHUB_TOKEN}",
}

# Phase to label mapping
PHASE_LABELS = {
    "Phase 1: Setup": ["phase-1", "setup"],
    "Phase 2: Foundational": ["phase-2", "foundational", "blocking"],
    "Phase 3: User Story 3": ["phase-3", "US3", "P1", "connection"],
    "Phase 4: User Story 1": ["phase-4", "US1", "P1", "schema"],
    "Phase 5: User Story 2": ["phase-5", "US2", "P2", "validation"],
    "Phase 6: Polish": ["phase-6", "polish", "documentation"],
}


def parse_tasks_file(file_path: str) -> List[Dict[str, any]]:
    """Parse tasks.md and extract all task information."""
    tasks = []
    current_phase = None
    current_phase_description = None

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        # Detect phase headers
        if line.startswith("## Phase"):
            current_phase = line.strip().replace("## ", "")
            # Get phase description from next few lines
            current_phase_description = ""
            for j in range(i+1, min(i+10, len(lines))):
                if lines[j].startswith("**Purpose**:"):
                    current_phase_description = lines[j].replace("**Purpose**:", "").strip()
                    break
                elif lines[j].startswith("**Goal**:"):
                    current_phase_description = lines[j].replace("**Goal**:", "").strip()
                    break
            continue

        # Parse task lines: - [ ] T001 [P] [US1] Description
        task_match = re.match(r'^- \[ \] (T\d+)\s+(\[P\])?\s*(\[US\d+\])?\s*(.+)$', line.strip())
        if task_match:
            task_id = task_match.group(1)
            is_parallel = task_match.group(2) is not None
            story_label = task_match.group(3).strip("[]") if task_match.group(3) else None
            description = task_match.group(4).strip()

            # Determine labels
            labels = ["task", "001-db-schema"]
            if current_phase:
                phase_key = current_phase.split(" -")[0]  # "Phase 1: Setup - Title" -> "Phase 1: Setup"
                if phase_key in PHASE_LABELS:
                    labels.extend(PHASE_LABELS[phase_key])

            if is_parallel:
                labels.append("parallel")

            if story_label:
                labels.append(story_label)

            # Check if it's a test task
            if "test_" in description.lower() or "integration test" in description.lower():
                labels.append("tests")

            tasks.append({
                "id": task_id,
                "title": f"{task_id}: {description[:80]}{'...' if len(description) > 80 else ''}",
                "description": description,
                "phase": current_phase,
                "phase_description": current_phase_description,
                "is_parallel": is_parallel,
                "story": story_label,
                "labels": list(set(labels)),  # Remove duplicates
            })

    return tasks


def create_github_issue(task: Dict[str, any], dry_run: bool = False) -> Optional[Dict]:
    """Create a GitHub issue for a task."""

    # Build issue body
    body_parts = [
        f"**Task ID**: {task['id']}",
        f"**Phase**: {task['phase']}",
    ]

    if task['phase_description']:
        body_parts.append(f"**Phase Goal**: {task['phase_description']}")

    if task['story']:
        body_parts.append(f"**User Story**: {task['story']}")

    if task['is_parallel']:
        body_parts.append("**Parallelizable**: ✅ Can run in parallel with other [P] tasks in this phase")

    body_parts.extend([
        "",
        "## Description",
        task['description'],
        "",
        "## Acceptance Criteria",
        "- [ ] Task implementation complete",
        "- [ ] Code follows project standards (type hints, validation)",
        "- [ ] Changes committed with clear message",
    ])

    if "test" in task['description'].lower():
        body_parts.append("- [ ] Test passes and covers acceptance scenario from spec.md")

    body_parts.extend([
        "",
        "## References",
        f"- Feature Spec: `specs/001-db-schema/spec.md`",
        f"- Implementation Plan: `specs/001-db-schema/plan.md`",
        f"- Data Model: `specs/001-db-schema/data-model.md`",
        f"- Tasks List: `specs/001-db-schema/tasks.md`",
        "",
        f"_This issue was auto-generated from tasks.md using /sp.taskstoissues_",
    ])

    issue_data = {
        "title": task['title'],
        "body": "\n".join(body_parts),
        "labels": task['labels'],
    }

    if dry_run:
        print(f"\n{'='*80}")
        print(f"DRY RUN: Would create issue:")
        print(f"Title: {issue_data['title']}")
        print(f"Labels: {', '.join(issue_data['labels'])}")
        print(f"Body preview: {issue_data['body'][:200]}...")
        return None

    url = f"{API_BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/issues"

    try:
        response = requests.post(url, json=issue_data, headers=HEADERS)
        response.raise_for_status()
        issue = response.json()
        print(f"✅ Created issue #{issue['number']}: {task['title']}")
        return issue
    except requests.exceptions.HTTPError as e:
        print(f"❌ Failed to create issue for {task['id']}: {e}")
        print(f"   Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error creating issue for {task['id']}: {e}")
        return None


def create_labels_if_needed():
    """Create custom labels in the repository if they don't exist."""

    labels_to_create = [
        {"name": "task", "color": "0075ca", "description": "Implementation task from tasks.md"},
        {"name": "001-db-schema", "color": "d4c5f9", "description": "Database Schema feature"},
        {"name": "phase-1", "color": "fbca04", "description": "Phase 1: Setup"},
        {"name": "phase-2", "color": "fbca04", "description": "Phase 2: Foundational"},
        {"name": "phase-3", "color": "fbca04", "description": "Phase 3: User Story 3"},
        {"name": "phase-4", "color": "fbca04", "description": "Phase 4: User Story 1"},
        {"name": "phase-5", "color": "fbca04", "description": "Phase 5: User Story 2"},
        {"name": "phase-6", "color": "fbca04", "description": "Phase 6: Polish"},
        {"name": "setup", "color": "c5def5", "description": "Project setup and configuration"},
        {"name": "foundational", "color": "d93f0b", "description": "Foundational infrastructure (blocks other work)"},
        {"name": "blocking", "color": "d93f0b", "description": "Blocks other tasks"},
        {"name": "US1", "color": "0e8a16", "description": "User Story 1: Provision Schema"},
        {"name": "US2", "color": "0e8a16", "description": "User Story 2: SQLModel Integration"},
        {"name": "US3", "color": "0e8a16", "description": "User Story 3: Database Connection"},
        {"name": "P1", "color": "b60205", "description": "Priority 1 (High)"},
        {"name": "P2", "color": "ff9800", "description": "Priority 2 (Medium)"},
        {"name": "parallel", "color": "c2e0c6", "description": "Can run in parallel"},
        {"name": "tests", "color": "1d76db", "description": "Test implementation"},
        {"name": "documentation", "color": "0075ca", "description": "Documentation"},
        {"name": "schema", "color": "5319e7", "description": "Database schema"},
        {"name": "connection", "color": "5319e7", "description": "Database connection"},
        {"name": "validation", "color": "5319e7", "description": "Data validation"},
        {"name": "polish", "color": "ededed", "description": "Polish and refinement"},
    ]

    url = f"{API_BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/labels"

    print("Creating labels...")
    for label_data in labels_to_create:
        try:
            response = requests.post(url, json=label_data, headers=HEADERS)
            if response.status_code == 201:
                print(f"✅ Created label: {label_data['name']}")
            elif response.status_code == 422:
                # Label already exists
                print(f"⏭️  Label already exists: {label_data['name']}")
            else:
                response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"⚠️  Warning: Could not create label {label_data['name']}: {e}")
        except Exception as e:
            print(f"⚠️  Unexpected error creating label {label_data['name']}: {e}")


def main():
    """Main execution function."""

    # Check for GitHub token
    if not GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        print("   Please set your GitHub Personal Access Token:")
        print("   export GITHUB_TOKEN='your_token_here'")
        print("\n   Create a token at: https://github.com/settings/tokens")
        print("   Required scopes: 'repo' (full control of private repositories)")
        sys.exit(1)

    # Check if tasks file exists
    if not os.path.exists(TASKS_FILE):
        print(f"❌ Error: Tasks file not found: {TASKS_FILE}")
        sys.exit(1)

    print(f"📋 Parsing tasks from {TASKS_FILE}...")
    tasks = parse_tasks_file(TASKS_FILE)
    print(f"   Found {len(tasks)} tasks")

    # Ask for confirmation
    print(f"\n⚠️  This will create {len(tasks)} issues in {REPO_OWNER}/{REPO_NAME}")

    dry_run = input("   Run in DRY RUN mode first? (y/n): ").lower().strip() == 'y'

    if dry_run:
        print("\n🔍 DRY RUN MODE - No issues will be created")
        for task in tasks[:5]:  # Show first 5 as preview
            create_github_issue(task, dry_run=True)
        print(f"\n   (Showing 5 of {len(tasks)} tasks)")

        proceed = input("\n   Proceed with actual creation? (y/n): ").lower().strip() == 'y'
        if not proceed:
            print("   Cancelled.")
            sys.exit(0)
    else:
        proceed = input("   Proceed? (y/n): ").lower().strip() == 'y'
        if not proceed:
            print("   Cancelled.")
            sys.exit(0)

    # Create labels first
    print("\n📌 Setting up labels...")
    create_labels_if_needed()

    # Create issues
    print(f"\n🚀 Creating {len(tasks)} GitHub issues...")
    created_issues = []

    for i, task in enumerate(tasks, 1):
        print(f"\n[{i}/{len(tasks)}] Creating {task['id']}...")
        issue = create_github_issue(task, dry_run=False)
        if issue:
            created_issues.append(issue)

        # Rate limiting: GitHub allows 5000 requests/hour for authenticated users
        # Add small delay to be respectful
        if i < len(tasks):
            time.sleep(0.5)

    # Summary
    print(f"\n{'='*80}")
    print(f"✅ Successfully created {len(created_issues)} of {len(tasks)} issues")
    print(f"\n   View issues at: https://github.com/{REPO_OWNER}/{REPO_NAME}/issues")
    print(f"   Filter by label: https://github.com/{REPO_OWNER}/{REPO_NAME}/issues?q=is%3Aissue+is%3Aopen+label%3A001-db-schema")

    if len(created_issues) < len(tasks):
        print(f"\n⚠️  Warning: {len(tasks) - len(created_issues)} issues failed to create")
        print("   Check the error messages above for details")


if __name__ == "__main__":
    main()
