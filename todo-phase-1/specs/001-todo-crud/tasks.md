# Tasks: Phase I Todo CRUD

**Input**: Design documents from `specs/001-todo-crud/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, quickstart.md

**Tests**: Tests are NOT requested in the specification. Manual validation via quickstart.md sufficient for Phase I.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below use single project structure per plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure (src/models, src/services, src/cli)
- [X] T002 [P] Create Python .gitignore file for venv, __pycache__, *.pyc
- [X] T003 [P] Create empty requirements.txt (no dependencies for Phase I)
- [X] T004 [P] Create setup.sh script to verify Python 3.11+ installation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Implement Task dataclass in src/models/task.py with id, title, description, is_complete attributes
- [X] T006 [P] Add __str__ method to Task class for console display formatting ([X]/[ ] status indicator)
- [X] T007 Initialize TaskManager class in src/services/task_manager.py with empty dict and next_id counter
- [X] T008 [P] Create display utility module src/cli/display.py with print_menu function
- [X] T009 [P] Create main application entry point src/main.py with startup warning message

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks with titles/descriptions and view all tasks in a list

**Independent Test**: User launches app, creates 3 tasks (one with title only, two with title+description), views complete list showing all tasks with IDs and completion status, then exits. All tasks display with unique sequential IDs starting from 1.

### Implementation for User Story 1

- [X] T010 [US1] Implement TaskManager.create() method in src/services/task_manager.py to create task with auto-assigned ID
- [X] T011 [US1] Add title validation to TaskManager.create() (reject empty titles, return error tuple)
- [X] T012 [US1] Implement TaskManager.get_all() method to return list of all Task objects
- [X] T013 [P] [US1] Create handle_create_task() function in src/cli/handlers.py to prompt for title and description
- [X] T014 [P] [US1] Create handle_view_tasks() function in src/cli/handlers.py to display task list
- [X] T015 [US1] Add CLI input validation for empty title in handle_create_task() (prompt user to retry)
- [X] T016 [P] [US1] Implement print_tasks() function in src/cli/display.py to format task list output
- [X] T017 [P] [US1] Add empty list message handling to print_tasks() ("No tasks found. Create one with option 1!")
- [X] T018 [US1] Add menu options 1 (Create Task) and 2 (View All Tasks) to src/main.py main loop
- [X] T019 [US1] Implement menu display with options 1-2 and 7 (Exit) in src/main.py
- [X] T020 [US1] Add menu choice validation (numeric 1-2 or 7) with error message for invalid input
- [X] T021 [US1] Test User Story 1: Create 3 tasks, view list, verify IDs are sequential 1-3, exit app

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (MVP delivered)

---

## Phase 4: User Story 2 - Mark Tasks Complete (Priority: P2)

**Goal**: Enable users to toggle task completion status (complete ↔ incomplete)

**Independent Test**: User creates task, marks it complete (status shows [X]), views list to confirm, toggles back to incomplete (status shows [ ]), views list again. Status changes persist within session.

### Implementation for User Story 2

- [X] T022 [US2] Implement TaskManager.toggle_complete() method in src/services/task_manager.py to flip is_complete boolean
- [X] T023 [US2] Add task existence validation to toggle_complete() (return error if task ID not found)
- [X] T024 [P] [US2] Create handle_complete_task() function in src/cli/handlers.py for option 5 (mark complete)
- [X] T025 [P] [US2] Create handle_incomplete_task() function in src/cli/handlers.py for option 6 (mark incomplete)
- [X] T026 [US2] Add numeric ID validation to complete/incomplete handlers (catch non-numeric input)
- [X] T027 [US2] Update print_tasks() in src/cli/display.py to show [X] for complete, [ ] for incomplete
- [X] T028 [US2] Add menu options 5 (Mark Task Complete) and 6 (Mark Task Incomplete) to src/main.py
- [X] T029 [US2] Update menu display to show options 1-2, 5-6, 7 in src/main.py
- [X] T030 [US2] Update menu choice validation to accept 1-2, 5-6, 7 in src/main.py
- [X] T031 [US2] Test User Story 2: Create task, mark complete, verify [X] status, mark incomplete, verify [ ] status

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Update Task Details (Priority: P3)

**Goal**: Enable users to edit task title and/or description by task ID

**Independent Test**: User creates task with title "Draft email" and description "Send to client", updates title to "Draft proposal" and description to "Send to client by Friday", views task to confirm both fields updated correctly.

### Implementation for User Story 3

- [X] T032 [US3] Implement TaskManager.update() method in src/services/task_manager.py with optional title and description params
- [X] T033 [US3] Add task existence validation to update() (return error if task ID not found)
- [X] T034 [US3] Add title validation to update() (reject empty title if title param provided)
- [X] T035 [US3] Create handle_update_task() function in src/cli/handlers.py to prompt for task ID and new values
- [X] T036 [US3] Implement "press Enter to keep current" logic in handle_update_task() for both title and description
- [X] T037 [US3] Add numeric ID validation to update handler (catch non-numeric input)
- [X] T038 [US3] Add menu option 3 (Update Task) to src/main.py main loop
- [X] T039 [US3] Update menu display to show options 1-3, 5-6, 7 in src/main.py
- [X] T040 [US3] Update menu choice validation to accept 1-3, 5-6, 7 in src/main.py
- [X] T041 [US3] Test User Story 3: Create task, update title only, verify change; update description only, verify change; update both, verify both changes

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P3)

**Goal**: Enable users to remove tasks from the list by task ID

**Independent Test**: User creates 3 tasks (IDs 1, 2, 3), deletes task ID 2, views list to confirm only tasks 1 and 3 remain with original IDs, attempts to delete task ID 2 again and receives error message.

### Implementation for User Story 4

- [X] T042 [US4] Implement TaskManager.delete() method in src/services/task_manager.py to remove task from dict
- [X] T043 [US4] Add task existence validation to delete() (return error if task ID not found)
- [X] T044 [US4] Create handle_delete_task() function in src/cli/handlers.py to prompt for task ID
- [X] T045 [US4] Add numeric ID validation to delete handler (catch non-numeric input)
- [X] T046 [US4] Add confirmation message after successful deletion in handle_delete_task()
- [X] T047 [US4] Add menu option 4 (Delete Task) to src/main.py main loop
- [X] T048 [US4] Update menu display to show all options 1-7 in src/main.py
- [X] T049 [US4] Update menu choice validation to accept full range 1-7 in src/main.py
- [X] T050 [US4] Test User Story 4: Create 3 tasks, delete middle task, verify IDs unchanged for remaining tasks, verify error on accessing deleted ID

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final quality checks

- [X] T051 [P] Add startup warning message to src/main.py about data loss (in-memory only)
- [X] T052 [P] Add exit confirmation message to src/main.py ("Goodbye! All tasks cleared from memory.")
- [ ] T053 [P] Implement print_message() helper in src/cli/display.py for consistent success/error formatting
- [X] T054 Standardize all error messages to use stderr (print(..., file=sys.stderr)) in CLI handlers
- [X] T055 [P] Add docstrings to all public methods in src/models/task.py
- [X] T056 [P] Add docstrings to all public methods in src/services/task_manager.py
- [X] T057 [P] Add docstrings to all handler functions in src/cli/handlers.py
- [ ] T058 Test edge case: Empty title creation (should reject with error)
- [ ] T059 Test edge case: Invalid menu choice (e.g., 10, abc) - should show error and re-prompt
- [ ] T060 Test edge case: Non-numeric task ID input - should show "Invalid task ID format" error
- [ ] T061 Test edge case: Very long title (1000+ chars) - should accept and display (may truncate)
- [ ] T062 Test edge case: 50 tasks in memory - verify <1 second response per NFR-002
- [ ] T063 Run quickstart.md validation scenarios (all 7 examples must work as documented)
- [X] T064 [P] Create README.md with project overview, WSL 2 setup instructions, link to quickstart.md
- [ ] T065 Final integration test: Full workflow (create, view, complete, update, delete, exit) without crashes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories CAN proceed in parallel (if staffed) after Phase 2 complete
  - OR sequentially in priority order (US1 → US2 → US3 → US4)
- **Polish (Phase 7)**: Depends on all user stories (Phase 3-6) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Independently testable

### Within Each User Story

- Setup phase tasks can run in parallel (T001-T004 all marked [P] or independent)
- Foundational phase tasks T005, T006, T008, T009 can run in parallel (different files)
- T007 depends on T005 (Task model needed for TaskManager)
- Within each user story:
  - TaskManager methods before CLI handlers (handlers depend on service methods)
  - Display utilities can run in parallel with handlers (different files)
  - Menu integration tasks depend on handler completion
  - Test task is last per story (validates story completion)

### Parallel Opportunities

- All Setup tasks (T001-T004) can run in parallel
- Foundational tasks T005, T006, T008, T009 can run in parallel
- Within US1: T013, T014, T016, T017 can run in parallel (different functions/files)
- Within US2: T024, T025 can run in parallel (different handlers)
- Within each user story: Tasks marked [P] are parallelizable
- Polish phase: T051-T053, T055-T057 can run in parallel (different files)

---

## Parallel Example: User Story 1

```bash
# After Foundational Phase completes, launch US1 implementation in parallel:

# Parallel batch 1: Core logic
Task T010: "Implement TaskManager.create() in src/services/task_manager.py"
Task T012: "Implement TaskManager.get_all() in src/services/task_manager.py"

# Parallel batch 2: CLI handlers (depends on batch 1 completion)
Task T013: "Create handle_create_task() in src/cli/handlers.py"
Task T014: "Create handle_view_tasks() in src/cli/handlers.py"
Task T016: "Implement print_tasks() in src/cli/display.py"

# Sequential: Menu integration (depends on handlers)
Task T018: "Add menu options 1 and 2 to src/main.py"
Task T019: "Implement menu display in src/main.py"
Task T020: "Add menu choice validation in src/main.py"

# Final: Testing (depends on all above)
Task T021: "Test User Story 1 independently"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T009) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T010-T021)
4. **STOP and VALIDATE**: Test User Story 1 independently (T021)
5. Deploy/demo if ready (MVP with Create + View tasks)

**Outcome**: Functional MVP that delivers standalone value (users can create and view tasks)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (T010-T021) → Test independently (T021) → **Deploy/Demo MVP!**
3. Add User Story 2 (T022-T031) → Test independently (T031) → Deploy/Demo (now with completion tracking)
4. Add User Story 3 (T032-T041) → Test independently (T041) → Deploy/Demo (now with editing)
5. Add User Story 4 (T042-T050) → Test independently (T050) → Deploy/Demo (full CRUD)
6. Add Polish (T051-T065) → Final integration test (T065) → **Deploy Production**

**Benefit**: Each story adds value without breaking previous stories; can stop at any checkpoint

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (T001-T009)
2. Once Foundational is done (after T009):
   - **Developer A**: User Story 1 (T010-T021) - MVP priority
   - **Developer B**: User Story 2 (T022-T031) - Can start in parallel
   - **Developer C**: User Story 3 (T032-T041) - Can start in parallel
   - **Developer D**: User Story 4 (T042-T050) - Can start in parallel
3. Stories complete and integrate independently
4. **Team reconvenes for Polish** (T051-T065) after all stories done

**Benefit**: Maximizes parallel work while maintaining story independence

---

## Task Execution Checklist

Before starting implementation (`/sp.implement`):

- [ ] All planning documents approved (spec.md, plan.md, data-model.md, quickstart.md)
- [ ] This tasks.md file reviewed and approved by user
- [ ] Python 3.11+ verified in WSL 2 environment
- [ ] Git feature branch 001-todo-crud checked out
- [ ] All team members understand user story priorities (P1 > P2 > P3)

During implementation:

- [ ] Reference Task IDs in all commit messages (e.g., `[T010] Implement TaskManager.create()`)
- [ ] Complete tasks in order within each phase (unless marked [P] for parallel)
- [ ] Test each user story independently after completing its phase
- [ ] No freestyle coding - all code generated via Claude Code per constitution
- [ ] Validate against quickstart.md examples as you complete features

After implementation:

- [ ] Run final integration test (T065) - all features work together
- [ ] Validate all quickstart.md scenarios (T063) work as documented
- [ ] Verify constitution compliance (9/9 principles)
- [ ] Create pull request with Task ID references in commit history

---

## Notes

- **Total tasks**: 65 tasks
  - Setup: 4 tasks
  - Foundational: 5 tasks
  - User Story 1 (P1): 12 tasks
  - User Story 2 (P2): 10 tasks
  - User Story 3 (P3): 10 tasks
  - User Story 4 (P3): 9 tasks
  - Polish: 15 tasks

- **Parallel opportunities**: 18 tasks marked [P] can run concurrently
  - Phase 1: 3 parallel tasks (T002, T003, T004)
  - Phase 2: 3 parallel tasks (T005, T006, T008, T009 partially)
  - User stories: 12 parallel tasks across US1-US4
  - Polish: 7 parallel tasks

- **User story task distribution**:
  - US1 (MVP): 12 tasks (18% of total)
  - US2: 10 tasks (15% of total)
  - US3: 10 tasks (15% of total)
  - US4: 9 tasks (14% of total)
  - Infrastructure + Polish: 24 tasks (37% of total)

- **MVP scope**: Phases 1-3 only (T001-T021) = 21 tasks for standalone MVP
- **Full feature set**: All 65 tasks for production-ready Phase I application
- **Estimated parallel efficiency**: With 4 developers, can reduce sequential execution by ~30%

- **Tests are NOT included** per specification (manual validation sufficient for Phase I)
- **Each task includes exact file path** for LLM execution clarity
- **Story labels ([US1], [US2], etc.)** enable traceability to spec.md user stories
- **Checkpoint comments** indicate when stories are independently testable
- **No implementation details in task descriptions** - focus on what, not how (LLM determines implementation)
