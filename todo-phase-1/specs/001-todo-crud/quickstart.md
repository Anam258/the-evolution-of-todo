# Quickstart Guide: Phase I Todo CRUD

**Feature**: 001-todo-crud
**Last Updated**: 2025-12-30

## Prerequisites

### Windows Users (WSL 2 Required)

This application **must** run in WSL 2 (Windows Subsystem for Linux) per project constitution.

**Check if WSL 2 is installed**:
```bash
wsl --status
```

**If not installed**, follow Microsoft's official guide:
1. Open PowerShell as Administrator
2. Run: `wsl --install`
3. Restart computer
4. Set default to WSL 2: `wsl --set-default-version 2`

**Install Ubuntu** (if not already installed):
```bash
wsl --install -d Ubuntu
```

**Open WSL terminal**:
- Press `Win + R`, type `wsl`, press Enter
- Or search for "Ubuntu" in Start menu

### Verify Python Version

**Check Python version** (must be 3.11 or higher):
```bash
python3 --version
```

**If Python 3.11+ not installed**:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv

# Verify
python3.11 --version
```

## Installation

### 1. Clone Repository

```bash
cd ~
git clone <repository-url>
cd The-Evolution-of-Todo/todo-phase-1
```

### 2. Checkout Feature Branch

```bash
git checkout 001-todo-crud
```

### 3. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

**What setup.sh does**:
- Verifies Python 3.11+ is installed
- Creates virtual environment (optional, but recommended)
- Confirms no external dependencies required
- Displays ready message

### 4. Run Application

```bash
python3 src/main.py
```

**Expected Output**:
```
=== Todo App (Phase I - In-Memory Mode) ===
WARNING: All tasks will be lost when you exit.
Phase II will add persistent storage.

=== Main Menu ===
1. Create Task
2. View All Tasks
3. Update Task
4. Delete Task
5. Mark Task Complete
6. Mark Task Incomplete
7. Exit

Enter choice (1-7):
```

## Usage Examples

### Example 1: Create and View Tasks (User Story P1)

**Scenario**: Create multiple tasks and view them in a list

```
Enter choice (1-7): 1
Enter task title: Buy groceries
Enter description (optional): Milk, eggs, bread
Task 1 created successfully.

Enter choice (1-7): 1
Enter task title: Write quarterly report
Enter description (optional): Due Friday, include Q4 financials
Task 2 created successfully.

Enter choice (1-7): 2
=== All Tasks ===
[ ] 1. Buy groceries - Milk, eggs, bread
[ ] 2. Write quarterly report - Due Friday, include Q4 financials

Total: 2 tasks
```

**Key Points**:
- Task IDs auto-assigned sequentially (1, 2, 3, ...)
- Description is optional (press Enter to skip)
- `[ ]` indicates incomplete status
- All tasks displayed with ID, title, and description preview

### Example 2: Mark Tasks Complete (User Story P2)

**Scenario**: Complete a task and toggle completion status

```
Enter choice (1-7): 5
Enter task ID: 1
Task 1 marked as complete.

Enter choice (1-7): 2
=== All Tasks ===
[X] 1. Buy groceries - Milk, eggs, bread
[ ] 2. Write quarterly report - Due Friday, include Q4 financials

Total: 2 tasks

Enter choice (1-7): 6
Enter task ID: 1
Task 1 marked as incomplete.

Enter choice (1-7): 2
=== All Tasks ===
[ ] 1. Buy groceries - Milk, eggs, bread
[ ] 2. Write quarterly report - Due Friday, include Q4 financials

Total: 2 tasks
```

**Key Points**:
- `[X]` indicates completed status
- Option 5 marks complete, option 6 marks incomplete
- Completion status toggles independently of other fields

### Example 3: Update Task Details (User Story P3)

**Scenario**: Edit a task's title or description

```
Enter choice (1-7): 3
Enter task ID: 2
Enter new title (press Enter to keep current): Finalize quarterly report
Enter new description (press Enter to keep current): Due Friday EOD, include Q4 financials and projections
Task 2 updated successfully.

Enter choice (1-7): 2
=== All Tasks ===
[ ] 1. Buy groceries - Milk, eggs, bread
[ ] 2. Finalize quarterly report - Due Friday EOD, include Q4 financials a...

Total: 2 tasks
```

**Key Points**:
- Press Enter to skip updating a field (keeps current value)
- Can update title only, description only, or both
- Long descriptions truncated in list view (full text preserved in storage)

### Example 4: Delete Tasks (User Story P3)

**Scenario**: Remove a completed task from the list

```
Enter choice (1-7): 4
Enter task ID: 1
Task 1 deleted successfully.

Enter choice (1-7): 2
=== All Tasks ===
[ ] 2. Finalize quarterly report - Due Friday EOD, include Q4 financials a...

Total: 1 task

Enter choice (1-7): 5
Enter task ID: 1
Error: Task ID 1 does not exist.
```

**Key Points**:
- Deleted tasks removed from list immediately
- Task IDs are **not reused** (ID 1 is gone forever this session)
- Remaining tasks keep their original IDs (no renumbering)
- Attempts to access deleted task ID show error message

### Example 5: Error Handling

**Scenario**: Invalid inputs and edge cases

```
# Empty title
Enter choice (1-7): 1
Enter task title:
Error: Title cannot be empty.

# Invalid task ID (non-existent)
Enter choice (1-7): 5
Enter task ID: 999
Error: Task ID 999 does not exist.

# Invalid task ID (non-numeric)
Enter choice (1-7): 3
Enter task ID: abc
Error: Invalid task ID format. Please enter a number.

# Invalid menu choice
Enter choice (1-7): 10
Invalid choice. Please enter a number between 1 and 7.
```

**Key Points**:
- All errors return to main menu (application never crashes)
- Error messages are specific and actionable
- Input validation at both CLI and service layers

### Example 6: Empty Task List

**Scenario**: View tasks when none exist

```
Enter choice (1-7): 2
=== All Tasks ===
No tasks found. Create one with option 1!

Total: 0 tasks
```

**Key Points**:
- Clear message when list is empty
- Helpful hint to guide user to create task

### Example 7: Exit Application

**Scenario**: Exit and lose all data (in-memory only)

```
Enter choice (1-7): 7
Goodbye! All tasks have been cleared from memory.
(Phase II will add persistent storage)
```

**Key Points**:
- Exit reminder that data is lost
- Prepares user for Phase II enhancement

## Common Workflows

### Daily Task Management

**Morning Setup**:
```
1. Launch app: python3 src/main.py
2. Create tasks for the day (option 1)
3. View task list (option 2)
```

**Throughout Day**:
```
1. Mark tasks complete as you finish them (option 5)
2. Update task details if priorities change (option 3)
3. Check progress with View All Tasks (option 2)
```

**End of Day**:
```
1. View completed tasks (option 2, look for [X])
2. Delete obsolete tasks (option 4)
3. Exit app (option 7) - tasks lost, fresh start tomorrow
```

**Note**: Phase II will add persistence so tasks survive restarts.

### Quick Task Capture

**Use Case**: Capture idea quickly without description

```
Enter choice (1-7): 1
Enter task title: Call Dr. Smith
Enter description (optional): [press Enter]
Task 3 created successfully.
```

**Tip**: Description is optional - skip it for quick capture, add details later with option 3 (Update Task).

## Troubleshooting

### "python3: command not found"

**Solution**: Install Python 3.11+
```bash
sudo apt update
sudo apt install python3.11
python3.11 --version
```

### "No such file or directory: src/main.py"

**Solution**: Ensure you're in project root directory
```bash
pwd  # Should end with .../todo-phase-1
ls src/main.py  # Should show file exists
```

If not in correct directory:
```bash
cd ~/The-Evolution-of-Todo/todo-phase-1
git checkout 001-todo-crud
```

### Application Crashes on Invalid Input

**Expected Behavior**: Application should **never** crash, always return to menu

**If crash occurs**:
1. Note the exact input that caused crash
2. File bug report with reproduction steps
3. Restart application: `python3 src/main.py`

**Constitution Requirement**: NFR-003 mandates graceful error handling. Crashes indicate bug.

### WSL 2 Not Running

**Check WSL status**:
```bash
# In PowerShell (Windows)
wsl --status
```

**Restart WSL**:
```bash
# In PowerShell (Windows)
wsl --shutdown
wsl
```

### Performance Degradation with Many Tasks

**Expected Behavior**: <1 second response for up to 100 tasks (NFR-002)

**If slow performance**:
1. Check task count: How many tasks in list? (View All Tasks)
2. Expected: Up to 100 tasks should be fast
3. If <100 tasks and slow, file performance bug report
4. If >100 tasks, acceptable per spec assumption #9

**Workaround**: Delete old completed tasks to reduce count

## Performance Benchmarks

**Expected Response Times** (per NFR-001, NFR-002):

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Application Startup | <2 seconds | From command to menu display |
| Create Task | <1 second | Including user input time |
| View All Tasks (50 tasks) | <1 second | Display list of 50 tasks |
| View All Tasks (100 tasks) | <1 second | Display list of 100 tasks |
| Update Task | <1 second | Lookup and modify |
| Delete Task | <1 second | Lookup and remove |
| Toggle Complete | <1 second | Lookup and toggle |

**Note**: Timings exclude user typing time, measure only system response after input submitted.

## Limitations (Phase I)

**Known Limitations** (by design, not bugs):

1. **No Persistence**: All data lost on exit (deferred to Phase II)
2. **No Search**: Cannot search by title/description (out of scope)
3. **No Filtering**: Cannot filter by completion status (out of scope)
4. **No Sorting**: Tasks displayed in creation order only (out of scope)
5. **No Priority Levels**: All tasks equal priority (out of scope)
6. **No Due Dates**: No time tracking (out of scope)
7. **No Undo**: Cannot reverse delete/update operations (out of scope)
8. **Single User**: No multi-user support or user accounts (Phase IV feature)
9. **Console Only**: No GUI or web interface (out of scope)
10. **Display Limit**: Long lists (>100 tasks) may be unwieldy but functional (acceptable per spec)

**Future Enhancements**: See [spec.md](spec.md) "Out of Scope" section for Phase II-V roadmap.

## Next Steps

**After mastering Phase I**:
1. **Phase II**: SQLite persistence (tasks survive restarts)
2. **Phase III**: AI-powered task suggestions and natural language input
3. **Phase IV**: Multi-user support with real-time sync
4. **Phase V**: Advanced AI features (predictive scheduling, analytics)

**Provide Feedback**:
- Report bugs via GitHub issues
- Suggest features for future phases
- Contribute to spec-driven development process

**Learn More**:
- [Specification](spec.md) - Detailed requirements and user stories
- [Implementation Plan](plan.md) - Architecture and design decisions
- [Data Model](data-model.md) - Task entity and storage structure
- [Constitution](../../.specify/memory/constitution.md) - Project principles and governance
