#!/usr/bin/env python3
"""
main.py - CLI entry point for the Project Management Tool.
 
Usage examples:
    python main.py add-user --name "Alex" --email "alex@example.com"
    python main.py list-users
    python main.py add-project --user "Alex" --title "CLI Tool" --description "Build a CLI" --due-date 2026-08-01
    python main.py list-projects --user "Alex"
    python main.py add-task --project "CLI Tool" --title "Implement add-task" --assigned-to "Alex"
    python main.py list-tasks --project "CLI Tool"
    python main.py complete-task --id 1
    python main.py search-projects --user "Alex" --keyword "CLI"
 
Run `python main.py -h` or `python main.py <command> -h` for full help.
"""

import argparse
import sys
 
try:
    from rich.console import Console
    from rich.table import Table
    RICH_AVAILABLE = True
    console = Console()
except ImportError:  # pragma: no cover - fallback if rich isn't installed
    RICH_AVAILABLE = False
    console = None
 
from models import User, Project, Task
from utils.storage import load_all, save_all
 
 
# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------
 
def load_data():
    """Reset in-memory registries and rebuild them from the JSON files."""
    User.reset()
    Project.reset()
    Task.reset()
 
    raw = load_all()
    for u in raw["users"]:
        User.from_dict(u)
    for p in raw["projects"]:
        Project.from_dict(p)
    for t in raw["tasks"]:
        Task.from_dict(t)
 
 
def persist():
    """Save the current in-memory state back to disk."""
    save_all(User.all(), Project.all(), Task.all())
 
 
# ---------------------------------------------------------------------------
# Output helpers (use rich if available, otherwise plain print)
# ---------------------------------------------------------------------------
 
def print_table(title, columns, rows):
    if not rows:
        print(f"No {title.lower()} found.")
        return
 
    if RICH_AVAILABLE:
        table = Table(title=title)
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*[str(cell) for cell in row])
        console.print(table)
    else:
        print(f"== {title} ==")
        print(" | ".join(columns))
        for row in rows:
            print(" | ".join(str(cell) for cell in row))
 
 
# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------
 
def cmd_add_user(args):
    try:
        user = User(name=args.name, email=args.email)
        persist()
        print(f"Created user: {user}")
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
 
 
def cmd_list_users(args):
    rows = [(u.id, u.name, u.email, len(u.project_ids)) for u in User.all()]
    print_table("Users", ["ID", "Name", "Email", "# Projects"], rows)
 
 
def cmd_add_project(args):
    user = User.find_by_name(args.user)
    if user is None:
        print(f"Error: no user named {args.user!r}. Create them first with add-user.")
        sys.exit(1)
    try:
        project = Project(
            title=args.title,
            description=args.description or "",
            due_date=args.due_date,
            user_id=user.id,
        )
        user.add_project(project)
        persist()
        print(f"Created project: {project} for user {user.name}")
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
 
 
def cmd_list_projects(args):
    if args.user:
        user = User.find_by_name(args.user)
        if user is None:
            print(f"Error: no user named {args.user!r}.")
            sys.exit(1)
        projects = Project.for_user(user.id)
        title = f"Projects for {user.name}"
    else:
        projects = Project.all()
        title = "All Projects"
 
    rows = [(p.id, p.title, p.due_date or "-", len(p.task_ids)) for p in projects]
    print_table(title, ["ID", "Title", "Due Date", "# Tasks"], rows)
 
 
def cmd_search_projects(args):
    user = User.find_by_name(args.user)
    if user is None:
        print(f"Error: no user named {args.user!r}.")
        sys.exit(1)
    keyword = args.keyword.lower()
    matches = [p for p in Project.for_user(user.id) if keyword in p.title.lower()
               or keyword in (p.description or "").lower()]
    rows = [(p.id, p.title, p.due_date or "-") for p in matches]
    print_table(f"Search results for '{args.keyword}' ({user.name})", ["ID", "Title", "Due Date"], rows)
 
 
def cmd_add_task(args):
    project = Project.find_by_title(args.project)
    if project is None:
        print(f"Error: no project titled {args.project!r}. Create it first with add-project.")
        sys.exit(1)
    try:
        contributors = args.assigned_to or []
        task = Task(title=args.title, project_id=project.id, assigned_to=contributors)
        project.add_task(task)
        persist()
        print(f"Created task: {task} in project {project.title}")
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
 
 
def cmd_list_tasks(args):
    project = Project.find_by_title(args.project)
    if project is None:
        print(f"Error: no project titled {args.project!r}.")
        sys.exit(1)
    tasks = Task.for_project(project.id)
    rows = [(t.id, t.title, t.status, ", ".join(t.assigned_to) or "-") for t in tasks]
    print_table(f"Tasks for {project.title}", ["ID", "Title", "Status", "Assigned To"], rows)
 
 
def cmd_complete_task(args):
    task = Task.find_by_id(args.id)
    if task is None:
        print(f"Error: no task with id {args.id}.")
        sys.exit(1)
    task.mark_complete()
    persist()
    print(f"Marked complete: {task}")
 
 
def cmd_add_contributor(args):
    task = Task.find_by_id(args.task_id)
    if task is None:
        print(f"Error: no task with id {args.task_id}.")
        sys.exit(1)
    task.add_contributor(args.user)
    persist()
    print(f"Added {args.user} as contributor on: {task}")
 
 
# ---------------------------------------------------------------------------
# Argument parser setup
# ---------------------------------------------------------------------------
 
def build_parser():
    parser = argparse.ArgumentParser(
        prog="project-tracker",
        description="A simple multi-user project & task tracker CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
 
    p = subparsers.add_parser("add-user", help="Create a new user")
    p.add_argument("--name", required=True, help="Full name of the user")
    p.add_argument("--email", required=True, help="Email address of the user")
    p.set_defaults(func=cmd_add_user)
 
    p = subparsers.add_parser("list-users", help="List all users")
    p.set_defaults(func=cmd_list_users)
 
    p = subparsers.add_parser("add-project", help="Create a project for a user")
    p.add_argument("--user", required=True, help="Name of the owning user")
    p.add_argument("--title", required=True, help="Project title")
    p.add_argument("--description", default="", help="Project description")
    p.add_argument("--due-date", dest="due_date", default=None, help="Due date, YYYY-MM-DD")
    p.set_defaults(func=cmd_add_project)
 
    p = subparsers.add_parser("list-projects", help="List projects (optionally for one user)")
    p.add_argument("--user", default=None, help="Only show projects owned by this user")
    p.set_defaults(func=cmd_list_projects)
 
    p = subparsers.add_parser("search-projects", help="Search a user's projects by keyword")
    p.add_argument("--user", required=True, help="Name of the user")
    p.add_argument("--keyword", required=True, help="Keyword to search title/description")
    p.set_defaults(func=cmd_search_projects)
 
    p = subparsers.add_parser("add-task", help="Add a task to a project")
    p.add_argument("--project", required=True, help="Title of the project")
    p.add_argument("--title", required=True, help="Task title")
    p.add_argument("--assigned-to", dest="assigned_to", nargs="*", default=None,
                   help="One or more contributor names")
    p.set_defaults(func=cmd_add_task)
 
    p = subparsers.add_parser("list-tasks", help="List tasks for a project")
    p.add_argument("--project", required=True, help="Title of the project")
    p.set_defaults(func=cmd_list_tasks)
 
    p = subparsers.add_parser("complete-task", help="Mark a task as done")
    p.add_argument("--id", required=True, type=int, help="Task ID")
    p.set_defaults(func=cmd_complete_task)
 
    p = subparsers.add_parser("add-contributor", help="Add a contributor to an existing task")
    p.add_argument("--task-id", dest="task_id", required=True, type=int, help="Task ID")
    p.add_argument("--user", required=True, help="Contributor name to add")
    p.set_defaults(func=cmd_add_contributor)
 
    return parser
 
 
def main():
    load_data()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
 
 
if __name__ == "__main__":
    main()
