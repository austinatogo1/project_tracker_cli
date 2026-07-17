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
- **Unit + integration tests** with `pytest`.
 
## Project Structure
 
```
project_tracker_cli/
├── main.py                # CLI entry point (argparse subcommands)
├── models/
│   ├── __init__.py
│   ├── user.py             # Person (base) + User
│   ├── project.py          # Project
│   └── task.py             # Task
├── utils/
│   ├── __init__.py
│   ├── storage.py          # JSON load/save helpers
│   └── validators.py       # standalone input validation helpers
├── data/                    # users.json / projects.json / tasks.json (generated)
├── tests/
│   ├── test_models.py       # unit tests for User/Project/Task
│   └── test_cli.py          # integration tests for CLI command handlers
├── requirements.txt
└── README.md
```
 
## Setup
 
```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
 
# 2. Install dependencies
pip install -r requirements.txt
```
 
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
 
## Running Tests
 
```bash
pytest
```
 
`tests/test_models.py` covers the `User`, `Project`, and `Task` classes
directly (validation, relationships, serialization). `tests/test_cli.py`
drives the CLI command handlers end-to-end against a temporary data
directory so your real `data/*.json` files are never touched by tests.
 
## Known Issues / Limitations
 
- Lookups by name/title are case-insensitive but assume uniqueness —
  two projects with the same title will collide.
- No CLI command to delete users/projects/tasks yet (only add/list/complete).
- Single-user local tool: no concurrency handling for simultaneous writers.
