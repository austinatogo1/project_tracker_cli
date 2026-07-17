# Project Management CLI Tool

A command-line, multi-user project & task tracker built with Python.
Admins can create users, give each user one or more projects, and give
each project one or more tasks — all persisted locally as JSON.

## Features

- **Users, Projects, Tasks** modeled as classes with inheritance
  (`Person` -> `User`), encapsulation (`@property` validation), and
  class-level ID counters / in-memory registries.
- **Relationships**
  - One-to-many: `User -> Project`
  - One-to-many: `Project -> Task`
  - Many-to-many: `Task <-> contributors` (a task can have several
    assigned users via `assigned_to`)
- **CLI** built with `argparse`, subcommands, and `--help` on every command.
- **Persistence** via JSON files in `data/`, with try/except handling for
  missing or corrupted files.
- **Pretty output** via the `rich` package (falls back to plain text if
  `rich` isn't installed).
- **Logging** to `logs/app.log` (always on, DEBUG level) for tracing exactly
  what happened during a session; pass `--verbose` to also see it live in
  the terminal.
- **Unit + integration tests** with `pytest` (58 tests, ~90% coverage).

## Project Structure

```
project_tracker_cli/
├── main.py                # CLI entry point (argparse subcommands + logging)
├── models/
│   ├── __init__.py
│   ├── user.py             # Person (base) + User
│   ├── project.py          # Project
│   └── task.py             # Task
├── utils/
│   ├── __init__.py
│   ├── storage.py          # JSON load/save helpers
│   └── validators.py       # standalone input validation helpers
├── data/                    # users.json / projects.json / tasks.json (sample data included)
├── logs/                    # app.log (generated at runtime, gitignored)
├── tests/
│   ├── test_models.py       # unit tests for User/Project/Task
│   ├── test_validators.py   # unit tests for utils/validators.py
│   ├── test_storage.py      # unit tests for JSON load/save + error handling
│   └── test_cli.py          # integration tests for CLI command handlers
├── Pipfile / Pipfile.lock   # dependency management (pipenv)
├── requirements.txt         # equivalent dependency list for plain pip/venv users
└── README.md
```

## Setup

Two supported ways to install dependencies — pick one.

**Option A: pipenv (recommended, matches Pipfile/Pipfile.lock)**

```bash
pip install pipenv --break-system-packages   # if not already installed
pipenv install --dev
pipenv shell
```

**Option B: plain venv + pip**

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Sample Data

`data/users.json`, `data/projects.json`, and `data/tasks.json` ship with
sample data (2 users, 2 projects, 3 tasks) so you can try `list-users`,
`list-projects`, and `list-tasks` immediately without creating anything
first. To start fresh, just delete the contents of `data/` (or the
files themselves) — the CLI recreates them automatically on the next
`add-*` command.

## Running the CLI

```bash
# See all available commands
python main.py -h

# Create a user
python main.py add-user --name "Alex" --email "alex@example.com"

# List users
python main.py list-users

# Create a project for that user
python main.py add-project --user "Alex" --title "CLI Tool" \
  --description "Build a CLI tool" --due-date 2026-08-01

# List all projects, or just one user's
python main.py list-projects
python main.py list-projects --user "Alex"

# Search a user's projects by keyword
python main.py search-projects --user "Alex" --keyword "CLI"

# Add a task to a project (optionally with contributors)
python main.py add-task --project "CLI Tool" --title "Implement add-task" \
  --assigned-to "Alex"

# List tasks for a project
python main.py list-tasks --project "CLI Tool"

# Mark a task complete (use the ID shown by list-tasks)
python main.py complete-task --id 1

# Add another contributor to an existing task (many-to-many)
python main.py add-contributor --task-id 1 --user "Sam"
```

Every command supports `-h` for detailed help, e.g. `python main.py add-task -h`.

## Logging & Debugging

Every run writes a detailed, timestamped DEBUG-level trace to `logs/app.log`
(which command ran, what it loaded/saved, and any errors) — useful for
tracing exactly what happened without cluttering normal CLI output. Add
`--verbose` before the subcommand to also stream that trace to your terminal:

```bash
python main.py --verbose add-user --name "Alex" --email "alex@example.com"
```

## Running Tests

```bash
pytest
```

- `tests/test_models.py` covers the `User`, `Project`, and `Task` classes
  directly (validation, relationships, serialization).
- `tests/test_validators.py` covers the standalone email/date/non-empty
  validation helpers in isolation.
- `tests/test_storage.py` covers JSON load/save, including missing files,
  empty files, and malformed JSON (these should degrade gracefully, not crash).
- `tests/test_cli.py` drives the CLI command handlers end-to-end — happy
  paths plus edge cases like missing users/projects/tasks, empty lists,
  invalid email, and multi-contributor persistence — against a temporary
  data directory so your real `data/*.json` files are never touched.

58 tests in total.

## Known Issues / Limitations

- Lookups by name/title are case-insensitive but assume uniqueness —
  two projects with the same title will collide.
- No CLI command to delete users/projects/tasks yet (only add/list/complete).
- Single-user local tool: no concurrency handling for simultaneous writers.
