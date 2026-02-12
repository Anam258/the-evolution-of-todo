# The Evolution of Todo - Project Constitution

<!--
SYNC IMPACT REPORT
==================
Version Change: Initial → 1.0.0
Rationale: First complete constitution for Todo Product evolution project

Modified Principles:
- None (initial creation)

Added Sections:
- Product Vision (Section 1)
- Core Development Principles (9 principles)
- Technology & Platform Constraints (Section 2)
- Spec-Driven Development Workflow (Section 3)
- Code Quality & Evaluation Standards (Section 4)
- Documentation Requirements (Section 5)
- Governance (Section 6)

Removed Sections:
- None (initial creation)

Templates Requiring Updates:
✅ spec-template.md - Reviewed, aligns with constitution principles
✅ plan-template.md - Reviewed, contains Constitution Check section that will reference this file
✅ tasks-template.md - Reviewed, aligns with phased execution and user story independence
⚠️ Follow-up: Command files may reference agent-specific names (verified AGENTS.md is generic)

Follow-up TODOs:
- None
==================
-->

## Product Vision

**The Evolution of Todo** is a multi-phase product evolution from a simple todo application (Phase I) into a cloud-native, AI-powered task management system (Phases II-V). This is not a throwaway prototype—it is a single, continuously evolving product built for hackathon evaluation and long-term maintainability.

**Key Characteristics**:
- **Product Mindset**: Every phase builds on the previous, maintaining backward compatibility and architectural integrity
- **Evaluation Awareness**: Designed to demonstrate technical excellence, architectural foresight, and spec-driven discipline to hackathon judges
- **AI-First Development**: All code is generated via Claude Code; manual coding is forbidden
- **Incremental Complexity**: Start simple (Phase I local CLI), evolve systematically (Phase II-V: cloud, AI, scale)
- **Long-term Sustainability**: Decisions made in Phase I must support Phase V requirements

## Core Development Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

**All development follows the rigid workflow**: `Specify → Plan → Tasks → Implement`

**Rules**:
- **MUST** complete and approve specification before planning
- **MUST** complete and approve plan before generating tasks
- **MUST** complete and approve tasks before implementation
- **MUST** reference Task IDs in all code commits
- **MUST** update specs if requirements change—never invent requirements during implementation
- **MUST** update plan if architecture changes—never freestyle architectural decisions

**Rationale**: Spec-driven development ensures traceability, prevents scope creep, enables parallel work, and demonstrates disciplined engineering to evaluators. It also ensures Phase I decisions align with Phase II-V evolution.

### II. Agent-Generated Code Only (NON-NEGOTIABLE)

**All production and test code MUST be generated via Claude Code**

**Rules**:
- **ZERO** manual coding allowed
- Agents execute tasks via `/sp.implement` or equivalent commands
- Humans review, approve, and guide—never directly edit code
- Configuration files, scripts, and documentation may be human-edited only if necessary

**Rationale**: Ensures consistency, leverages AI capabilities, demonstrates innovation for hackathon judges, and maintains reproducibility across phases.

### III. Windows Development via WSL 2 (NON-NEGOTIABLE)

**All development on Windows MUST occur within WSL 2 (Windows Subsystem for Linux)**

**Rules**:
- **MUST** use WSL 2 Ubuntu or compatible Linux distribution
- **MUST** run all build, test, and execution commands in WSL environment
- **MAY** use Windows tools (IDE, browser) pointing to WSL filesystem
- **MUST** document WSL setup in quickstart guides

**Rationale**: Ensures cross-platform compatibility, avoids Windows-specific path/command issues, and prepares for cloud deployment (Phases II-V).

### IV. Phase-Based Evolution (NON-NEGOTIABLE)

**The product evolves through five discrete phases, each building on the previous**

**Phases**:
- **Phase I**: Local CLI todo app (SQLite, TypeScript/Python)
- **Phase II**: Cloud deployment (serverless, managed DB)
- **Phase III**: AI integration (task suggestions, natural language)
- **Phase IV**: Multi-user, real-time sync
- **Phase V**: Advanced AI (predictive scheduling, analytics)

**Rules**:
- **MUST** design Phase I architecture to support Phase II-V evolution
- **MUST** document architectural decisions (ADRs) for cross-phase impact
- **MUST** maintain backward compatibility when evolving phases
- **MUST** validate each phase independently before progressing

**Rationale**: Hackathon judging values foresight and scalability. Demonstrating Phase I→V evolution shows architectural maturity.

### V. User Story Independence (NON-NEGOTIABLE)

**Every user story MUST be independently implementable and testable**

**Rules**:
- **MUST** prioritize user stories (P1, P2, P3, etc.)
- **MUST** ensure each story delivers standalone value (MVP slicing)
- **MUST** allow stories to be developed in parallel when possible
- **MUST** test each story independently before integration

**Rationale**: Enables incremental delivery, parallel development, and early demo capability—critical for hackathon timelines.

### VI. Test-Driven Development (CONDITIONAL)

**Tests are OPTIONAL but if required, TDD MUST be strictly followed**

**Rules**:
- **IF** tests are requested in spec, **THEN**:
  - **MUST** write tests first
  - **MUST** ensure tests fail before implementation (Red)
  - **MUST** implement minimal code to pass tests (Green)
  - **MUST** refactor while keeping tests green (Refactor)
- **IF** tests are NOT requested, skip test tasks entirely

**Rationale**: TDD ensures correctness when testing is required, but Phase I may prioritize speed over test coverage for hackathon deadlines.

### VII. Simplicity and YAGNI (NON-NEGOTIABLE)

**Start simple. Add complexity only when explicitly required.**

**Rules**:
- **MUST** implement only specified requirements—no gold-plating
- **MUST** avoid premature abstraction (wait for 3+ similar cases)
- **MUST** reject patterns/frameworks not justified by current needs
- **MUST** document complexity justifications in plan.md

**Rationale**: Hackathon timelines reward focused execution. Over-engineering wastes time and obscures core innovation. Judges value clarity over cleverness.

### VIII. Observability and Debuggability (NON-NEGOTIABLE)

**All components MUST be debuggable via standard I/O and structured logging**

**Rules**:
- **MUST** use stdin/stdout for CLI I/O (no side-channel inputs)
- **MUST** write errors to stderr with actionable messages
- **MUST** support JSON output mode for machine parsing
- **MUST** log significant operations (create, update, delete) with context

**Rationale**: Simplifies debugging, enables CI/CD integration, and supports Phase II+ cloud monitoring.

### IX. Version Control and Traceability (NON-NEGOTIABLE)

**Every code change MUST be traceable to a spec, plan, or task**

**Rules**:
- **MUST** reference Task IDs in commit messages (e.g., `[T042] Implement task creation`)
- **MUST** create feature branches per spec (e.g., `001-add-task-crud`)
- **MUST** link commits to user stories in commit body
- **MUST** never commit without a corresponding approved task

**Rationale**: Demonstrates disciplined process to judges, enables audit trail, and supports multi-phase evolution.

## Technology & Platform Constraints

### Language & Runtime
- **Phase I**: TypeScript (Node.js) OR Python 3.11+
  - **Decision criteria**: Choose based on team familiarity; both support Phase II-V evolution
  - **MUST** use async/await for I/O operations (prepares for cloud scale)

### Data Storage
- **Phase I**: SQLite (local file-based)
- **Phase II+**: PostgreSQL (managed cloud DB)
- **MUST** use ORM/query builder to ease Phase I→II migration

### CLI Framework
- **MUST** use established CLI library (e.g., `commander.js`, `click`, `typer`)
- **MUST** support `--json` flag for machine-readable output
- **MUST** provide `--help` for all commands

### Testing (if required)
- **Unit tests**: Jest (TS) / pytest (Python)
- **Integration tests**: Same framework, test end-to-end CLI workflows
- **Contract tests**: Validate data models against schema

### Development Environment
- **MUST** use WSL 2 on Windows
- **MUST** provide `package.json` / `pyproject.toml` with all dependencies
- **MUST** include setup script (e.g., `setup.sh`) for one-command initialization

## Spec-Driven Development Workflow

### Phase 0: Specification (`/sp.specify`)
**Input**: User natural-language feature description
**Output**: `specs/[###-feature]/spec.md`
**Content**: User stories (prioritized, independently testable), functional requirements, success criteria, edge cases
**Gate**: User approval required before planning

### Phase 1: Planning (`/sp.plan`)
**Input**: Approved specification
**Output**: `specs/[###-feature]/plan.md`, `research.md`, `data-model.md`, `quickstart.md`, `contracts/`
**Content**: Architecture, technical context, constitution check, project structure, complexity justifications
**Gate**: User approval + constitution compliance required before task generation

### Phase 2: Task Generation (`/sp.tasks`)
**Input**: Approved plan + supporting docs
**Output**: `specs/[###-feature]/tasks.md`
**Content**: Ordered, parallelizable tasks with IDs, file paths, user story mapping, dependency tracking
**Gate**: User approval required before implementation

### Phase 3: Implementation (`/sp.implement`)
**Input**: Approved tasks
**Output**: Working code, passing tests (if required), updated documentation
**Process**: Agent executes tasks sequentially or in parallel (where marked `[P]`), references Task IDs in commits
**Gate**: All tests pass, quickstart validated, user acceptance

### Phase 4: Review & Refinement
**Input**: Implemented feature
**Output**: ADRs (if architectural decisions made), updated constitution (if principles change), PRs merged
**Process**: Code review (human), cross-artifact consistency check (`/sp.analyze`), GitHub issue creation (`/sp.taskstoissues`)

## Code Quality & Evaluation Standards

### For Hackathon Judges
- **Clarity**: Code should be self-documenting; prefer explicit over clever
- **Traceability**: Every file/function should map to a task/spec
- **Evolution**: Phase I code should show signs of Phase II-V readiness (e.g., config files, modular architecture)
- **Innovation**: Demonstrate AI-first development; include AI usage notes in README

### Code Standards
- **MUST** pass linter (ESLint/Pylint) with zero warnings
- **MUST** use consistent formatting (Prettier/Black, auto-formatted)
- **MUST** include inline comments ONLY where logic is non-obvious
- **MUST** avoid commented-out code (delete unused code)

### Performance Targets
- **Phase I**: Local CLI should respond <100ms for CRUD operations
- **Phase II+**: API p95 latency <200ms, support 1000+ concurrent users

### Security
- **MUST** sanitize user input (prevent injection attacks)
- **MUST** validate file paths (prevent directory traversal)
- **Phase II+**: MUST use environment variables for secrets (never hardcode)

## Documentation Requirements

### Required Artifacts
1. **README.md**: Product overview, setup (WSL 2), quickstart, phase roadmap
2. **specs/[###-feature]/spec.md**: User stories, requirements (per feature)
3. **specs/[###-feature]/plan.md**: Architecture, constitution check (per feature)
4. **specs/[###-feature]/tasks.md**: Task list (per feature)
5. **specs/[###-feature]/quickstart.md**: Feature-specific usage guide
6. **ADRs** (`specs/[###-feature]/adrs/`): Architectural decisions (when significant)

### Documentation Standards
- **MUST** write for future developers (including judges who may review code)
- **MUST** use Markdown with proper heading hierarchy
- **MUST** include code examples in quickstart guides
- **MUST** update docs in same commit as code changes

### Hackathon-Specific
- **MUST** include `HACKATHON.md` highlighting:
  - Phase I achievements vs. Phase II-V roadmap
  - AI-first development approach
  - Spec-driven discipline
  - Architectural decisions enabling evolution

## Governance

### Amendment Process
1. Identify constitutional violation or new principle needed
2. Propose amendment via `/sp.constitution` command with justification
3. Update constitution with incremented version (semantic versioning)
4. Propagate changes to all dependent templates (spec, plan, tasks)
5. Document in Sync Impact Report (HTML comment at top of constitution)

### Version Semantics
- **MAJOR** (X.0.0): Backward-incompatible governance changes (e.g., removing TDD requirement)
- **MINOR** (0.X.0): New principle added or section materially expanded
- **PATCH** (0.0.X): Clarifications, wording fixes, non-semantic changes

### Compliance Review
- **Constitution Check** in `plan.md` MUST verify adherence before implementation
- **Cross-artifact analysis** (`/sp.analyze`) MUST validate spec/plan/tasks alignment
- **Gate reviews** (user approval at Specify, Plan, Tasks) enforce compliance

### Source of Truth Order
1. **constitution.md** (this file)
2. **spec.md** (feature requirements)
3. **plan.md** (architecture & design)
4. **tasks.md** (implementation breakdown)

If conflict arises, higher-ranked artifact prevails. Update lower-ranked artifacts to resolve.

### Complexity Justification
Any violation of Simplicity (Principle VII) MUST be documented in `plan.md` Complexity Tracking table with:
- What constraint is violated
- Why added complexity is necessary
- Why simpler alternative was rejected

**Version**: 1.0.0 | **Ratified**: 2025-12-30 | **Last Amended**: 2025-12-30
