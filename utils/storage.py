"""
utils/storage.py
 
Handles all file I/O for the project tracker: saving and loading
users, projects, and tasks as JSON. Centralizing this here keeps
main.py focused on CLI wiring instead of file-handling details.
"""
 
import json
import os
 
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
 
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
 
 
def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
 
 
def load_json(path):
    """
    Load a JSON file and return its contents as a list.
    Returns an empty list if the file doesn't exist yet or is malformed,
    so a fresh install or a corrupted file never crashes the CLI.
    """
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Warning: could not read {path} ({exc}). Starting with empty data.")
        return []
 
 
def save_json(path, records):
    """Write a list of dicts to disk as pretty-printed JSON."""
    _ensure_data_dir()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
    except OSError as exc:
        print(f"Error: could not save to {path} ({exc}).")
 
 
def load_all():
    """Load raw dict records for users, projects, and tasks."""
    return {
        "users": load_json(USERS_FILE),
        "projects": load_json(PROJECTS_FILE),
        "tasks": load_json(TASKS_FILE),
    }
 
 
def save_all(users, projects, tasks):
    """Persist current User/Project/Task objects to their JSON files."""
    save_json(USERS_FILE, [u.to_dict() for u in users])
    save_json(PROJECTS_FILE, [p.to_dict() for p in projects])
    save_json(TASKS_FILE, [t.to_dict() for t in tasks])
